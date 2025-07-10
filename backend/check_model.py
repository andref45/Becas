#!/usr/bin/env python3

from ultralytics import YOLO
import sys

def check_model_info():
    """Verifica información del modelo entrenado"""
    try:
        model_path = '/Users/andreflores/Documents/Becas/modelo/cedulas/entrenamiento_cedulas/weights/best.pt'
        model = YOLO(model_path)
        
        print("=" * 50)
        print("🔍 INFORMACIÓN DEL MODELO ENTRENADO")
        print("=" * 50)
        
        print(f"📁 Ruta del modelo: {model_path}")
        print(f"📊 Número de clases: {len(model.names)}")
        print(f"🏷️ Nombres de clases: {model.names}")
        print(f"📝 Clases por índice:")
        
        for idx, name in model.names.items():
            print(f"   {idx}: {name}")
        
        print("\n" + "=" * 50)
        print("✅ Modelo cargado exitosamente")
        print("=" * 50)
        
        return model.names
        
    except Exception as e:
        print(f"❌ Error al cargar modelo: {e}")
        return None

if __name__ == "__main__":
    class_names = check_model_info()
    if class_names:
        print(f"\n🔧 Para usar en el backend, las clases son: {list(class_names.values())}")