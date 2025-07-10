# 🎯 Sistema de Procesamiento de Cédulas

Sistema web para extraer automáticamente información de cédulas ecuatorianas usando OCR y YOLO.

## 📋 Características

- **Modal de Discapacidad**: Flujo condicional según el tipo de usuario
- **OCR Frontal**: Extrae nombres, apellidos, número de cédula
- **OCR Reverso**: Extrae tipo y porcentaje de discapacidad
- **Exportación Excel**: Descarga automática de datos
- **Interfaz Profesional**: Diseño moderno y responsivo

## 🚀 Instalación Rápida

### 1. Instalar Tesseract OCR

**Windows:**
```bash
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en: C:\Program Files\Tesseract-OCR\
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### 2. Configurar Backend

```bash
# Navegar a la carpeta del proyecto
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Modelo YOLO

```bash
# Copiar tu modelo entrenado a la carpeta backend
cp /ruta/a/tu/modelo/best.pt backend/best.pt
```

### 4. Ejecutar el Sistema

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
# Abrir cedula_processor.html en navegador
# O usar servidor local:
python -m http.server 8000
# Ir a: http://localhost:8000/cedula_processor.html
```

## 🔧 Configuración Avanzada

### Ajustar Ruta de Tesseract (si es necesario)

Editar `backend/app.py`:
```python
# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS/Linux
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

### Configurar Modelo YOLO

Si no tienes el modelo entrenado:
1. El sistema funcionará con OCR básico
2. Para entrenar tu modelo, sigue el notebook `deteccion_cedula-4.ipynb`
3. Coloca el archivo `best.pt` en la carpeta `backend/`

## 🌐 Uso de la Aplicación

1. **Abrir**: `cedula_processor.html` en navegador
2. **Pregunta**: Responder si tiene discapacidad
3. **Subir**: Imagen frontal de cédula (obligatorio)
4. **Subir**: Imagen reversa (solo si tiene discapacidad)
5. **Procesar**: Hacer clic en "Procesar Cédula"
6. **Exportar**: Descargar datos en Excel

## 📊 API Endpoints

### `POST /api/process-front`
Procesa cédula frontal
- **Input**: Imagen (form-data)
- **Output**: JSON con nombres, apellidos, número de cédula

### `POST /api/process-back`
Procesa cédula reversa
- **Input**: Imagen (form-data)
- **Output**: JSON con tipo y porcentaje de discapacidad

### `GET /api/health`
Verificar estado del servidor
- **Output**: Estado del servidor y modelos

## 🛠️ Solución de Problemas

### Error: "Tesseract not found"
```bash
# Verificar instalación
tesseract --version

# Configurar ruta manualmente en app.py
pytesseract.pytesseract.tesseract_cmd = '/ruta/a/tesseract'
```

### Error: "CORS policy"
- Verificar que el backend esté ejecutándose en puerto 5000
- Usar navegador con CORS deshabilitado para desarrollo

### Error: "Module not found"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔄 Desarrollo

### Estructura del Proyecto
```
Becas/
├── cedula_processor.html      # Frontend
├── backend/
│   ├── app.py                # Servidor Flask
│   ├── requirements.txt      # Dependencias
│   └── best.pt              # Modelo YOLO (opcional)
├── Notebooks/               # Notebooks originales
└── README.md               # Este archivo
```


