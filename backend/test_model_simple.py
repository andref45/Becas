#!/usr/bin/env python3

import torch
import os

def check_model_simple():
    model_path = '/Users/andreflores/Documents/Becas/modelo/cedulas/entrenamiento_cedulas/weights/best.pt'
    
    print(f"📁 Verificando archivo: {model_path}")
    print(f"📊 Archivo existe: {os.path.exists(model_path)}")
    print(f"📏 Tamaño archivo: {os.path.getsize(model_path) / (1024*1024):.1f} MB")
    
    try:
        # Cargar con weights_only=False
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
        print(f"✅ Checkpoint cargado exitosamente")
        print(f"🔑 Claves principales: {list(checkpoint.keys())}")
        
        if 'model' in checkpoint:
            model_info = checkpoint['model']
            print(f"📋 Info del modelo: {type(model_info)}")
            
        # Intentar acceder a names si existe
        if hasattr(checkpoint.get('model', {}), 'names'):
            print(f"🏷️ Nombres: {checkpoint['model'].names}")
        elif 'names' in checkpoint:
            print(f"🏷️ Nombres: {checkpoint['names']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_model_simple()