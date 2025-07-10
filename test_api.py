#!/usr/bin/env python3

import requests
import json

def test_api():
    """Prueba la API del backend"""
    
    # URL base de la API
    API_BASE_URL = 'http://localhost:5001/api'
    
    # Probar health check
    try:
        print("🔍 Probando health check...")
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check exitoso")
            print(f"   Status: {data['status']}")
            print(f"   YOLO Model: {'Cargado' if data['yolo_model'] else 'No cargado'}")
            print(f"   Tesseract: {'Disponible' if data['tesseract'] else 'No disponible'}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("Asegúrate de que el servidor esté ejecutándose en puerto 5001")
        return
    
    print("\n" + "="*50)
    print("🎯 SERVIDOR LISTO PARA PROCESAR CÉDULAS")
    print("="*50)
    print("\n📋 Clases que detecta el modelo:")
    print("   • firstname (nombres)")
    print("   • lastname, lastname_first, lastname_second (apellidos)")
    print("   • identity-number (número de cédula)")
    print("\n🌐 Para usar la aplicación web:")
    print("   1. Mantén este servidor ejecutándose")
    print("   2. Abre cedula_processor.html en tu navegador")
    print("   3. Sube las imágenes de las cédulas")
    print("   4. ¡El modelo procesará automáticamente!")

if __name__ == "__main__":
    test_api()