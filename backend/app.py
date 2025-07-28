from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import base64
import re
import os
import tempfile

# Configuración para evitar problemas de threading
os.environ['OMP_NUM_THREADS'] = '1'

from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# Configurar pytesseract (ajustar ruta si es necesario)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/Mac

# Cargar modelo YOLO entrenado
try:
    model_path = '/Users/andreflores/Documents/Becas/modelo/cedulas/entrenamiento_cedulas/weights/best.pt'
    
    # Cargar modelo con torch.load permitiendo código inseguro (para modelos locales confiables)
    import torch
    
    # Permitir carga insegura para modelo local confiable
    torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
    
    # Cargar modelo con weights_only=False para compatibilidad
    model = YOLO(model_path, verbose=False)
    
    print(f"Modelo YOLO cargado exitosamente desde: {model_path}")
    print(f"Clases del modelo: {model.names}")
    print(f"Número de clases: {len(model.names)}")
    
except Exception as e:
    # Si falla, intentar cargar con torch directamente
    try:
        import torch
        # Cargar estado del modelo con weights_only=False
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        model = YOLO(model_path, verbose=False)
        print(f"Modelo YOLO cargado exitosamente (método alternativo)")
        print(f"Clases del modelo: {model.names}")
    except Exception as e2:
        model = None
        print(f"Advertencia: No se pudo cargar el modelo YOLO.")
        print(f"   Error 1: {e}")
        print(f"   Error 2: {e2}")
        print("Usando OCR básico como fallback.")

def process_image_with_yolo(image_path):
    """Procesa imagen con YOLO y extrae texto con OCR - Igual que en el notebook"""
    if not model:
        return process_image_basic_ocr(image_path)
    
    try:
        # Ejecutar modelo YOLO igual que en el notebook
        results = model(image_path, conf=0.25, save=False)[0]
        
        # Cargar imagen con PIL para compatibilidad
        img_pil = Image.open(image_path)
        img_np = np.array(img_pil)
        
        datos_detectados = {}
        
        # Procesar cada detección
        for box in results.boxes:
            clase_idx = int(box.cls[0])
            nombre_clase = model.names[clase_idx]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Recortar la región usando numpy array
            region = img_np[y1:y2, x1:x2]
            region_pil = Image.fromarray(region)
            
            # Aplicar OCR igual que en el notebook
            texto = pytesseract.image_to_string(region_pil, config="--psm 6").strip()
            
            # Normalización específica para cédula según clases del modelo
            if nombre_clase == "identity-number":
                texto = texto.replace("-", "").replace("–", "").strip()
                # Limpiar solo números
                texto = re.sub(r'[^0-9]', '', texto)
            elif nombre_clase in ["firstname", "lastname", "lastname_first", "lastname_second"]:
                texto = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', texto).upper().strip()
            
            datos_detectados[nombre_clase] = texto
            
        print(f"🔍 Detecciones encontradas: {list(datos_detectados.keys())}")
        print(f"📋 Datos extraídos: {datos_detectados}")
        
        return datos_detectados
        
    except Exception as e:
        print(f"Error en procesamiento YOLO: {e}")
        return process_image_basic_ocr(image_path)

def process_image_basic_ocr(image_path):
    """OCR básico para cuando no hay modelo YOLO"""
    img = cv2.imread(image_path)
    
    # Preprocesar imagen
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Aplicar OCR
    text = pytesseract.image_to_string(thresh, lang='spa', config='--psm 6')
    
    # Extraer patrones comunes
    datos = extract_patterns_from_text(text)
    return datos

def extract_patterns_from_text(text):
    """Extrae patrones comunes de texto OCR"""
    datos = {}
    
    # Buscar número de cédula (10 dígitos)
    cedula_match = re.search(r'\b\d{10}\b', text)
    if cedula_match:
        datos['numeroIdentidad'] = cedula_match.group()
    
    # Buscar nombres y apellidos (líneas con solo letras y espacios)
    lines = text.split('\n')
    potential_names = []
    
    for line in lines:
        clean_line = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', line).strip()
        if len(clean_line) > 3 and clean_line.replace(' ', '').isalpha():
            potential_names.append(clean_line.upper())
    
    if potential_names:
        if len(potential_names) >= 2:
            datos['nombres'] = potential_names[0]
            datos['apellidos'] = potential_names[1]
        else:
            datos['nombres'] = potential_names[0]
    
    # Buscar fechas (dd/mm/yyyy)
    fecha_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', text)
    if fecha_match:
        datos['fechaNacimiento'] = fecha_match.group()
    
    return datos

def process_back_id_card(image_path):
    """Procesa reverso de cédula para extraer datos de discapacidad - Mejorado"""
    img = cv2.imread(image_path)
    
    # Múltiples configuraciones de OCR para mejor detección
    configs = [
        '--psm 6',
        '--psm 7',
        '--psm 8',
        '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%'
    ]
    
    all_text = ""
    
    # Probar diferentes preprocesados y configuraciones
    for config in configs:
        # Preprocesar imagen con diferentes métodos
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Método 1: Umbralización OTSU
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text1 = pytesseract.image_to_string(thresh1, lang='spa', config=config).strip()
        
        # Método 2: Umbralización adaptativa
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        text2 = pytesseract.image_to_string(thresh2, lang='spa', config=config).strip()
        
        all_text += " " + text1 + " " + text2
    
    # Normalizar texto
    full_text = all_text.upper()
    
    datos = {}
    
    # Buscar tipo de discapacidad (patrones mejorados como en el notebook)
    discapacidad_patterns = [
        (r'AUDITIVA|AUDIIIVA|AUDITI\w*', 'AUDITIVA'),
        (r'VISUAL', 'VISUAL'),
        (r'FÍSICA|FISICA|FISIC\w*', 'FÍSICA'),
        (r'INTELECTUAL|INTELECT\w*', 'INTELECTUAL'),
        (r'PSICOSOCIAL|PSICO\w*', 'PSICOSOCIAL'),
        (r'MÚLTIPLE|MULTIPLE|MULTI\w*', 'MÚLTIPLE')
    ]
    
    for pattern, tipo in discapacidad_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            datos['tipoDiscapacidad'] = tipo
            break
    
    # Buscar porcentaje de discapacidad (mejorado)
    porcentaje_matches = re.findall(r'(\d{1,2})%', full_text)
    if porcentaje_matches:
        datos['porcentajeDiscapacidad'] = porcentaje_matches[0] + '%'
    
    # Buscar información adicional (variaciones como en el notebook)
    if re.search(r'DONANTE|DONANE|DONAN\w*', full_text, re.IGNORECASE):
        datos['donante'] = 'Sí'
    
    # Debug: mostrar texto detectado
    print(f"🔍 Texto completo detectado: {full_text[:200]}...")
    print(f"📋 Datos extraídos: {datos}")
    
    return datos

@app.route('/api/process-front', methods=['POST'])
def process_front_id():
    """Procesa cédula frontal"""
    try:
        # Obtener imagen del request
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró imagen'}), 400
        
        image_file = request.files['image']
        
        # Guardar imagen temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Procesar imagen
        datos = process_image_with_yolo(tmp_path)
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        # Mapear campos según las clases reales del modelo:
        # {0: 'firstname', 1: 'identity-number', 2: 'lastname', 3: 'lastname_first', 4: 'lastname_second'}
        resultado = {
            'nombres': datos.get('firstname', ''),
            'apellidos': ' '.join(filter(None, [
                datos.get('lastname', ''),
                datos.get('lastname_first', ''),
                datos.get('lastname_second', '')
            ])).strip(),
            'numeroIdentidad': datos.get('identity-number', ''),
            'fechaNacimiento': '',  # No detectado por el modelo actual
            'lugarNacimiento': ''   # No detectado por el modelo actual
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-back', methods=['POST'])
def process_back_id():
    """Procesa cédula reversa"""
    try:
        # Obtener imagen del request
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró imagen'}), 400
        
        image_file = request.files['image']
        
        # Guardar imagen temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Procesar imagen
        datos = process_back_id_card(tmp_path)
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        return jsonify(datos)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar estado del servidor"""
    return jsonify({
        'status': 'ok',
        'yolo_model': model is not None,
        'tesseract': True
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)