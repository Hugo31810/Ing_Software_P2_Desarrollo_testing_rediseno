import sys
import os
from flask import Flask, request, jsonify
from lectura_voltaje import lecturaVoltaje
from detector_incidencias import DetectorIncidencias

# Configuración de rutas para encontrar el CSV en la carpeta superior
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.dirname(directorio_actual)
ruta_csv = os.path.join(directorio_raiz, "Dataset-CV.csv")

app = Flask(__name__)
cerebro = DetectorIncidencias()

print(f"--> [Servidor] Iniciando carga desde: {ruta_csv}")
lector = lecturaVoltaje()
df = lector.leerCSV(ruta_csv)

if df is not None:
    cerebro.entrenar(df)
    print("--> [Servidor] ¡SISTEMA LISTO!")
else:
    print("❌ ERROR CRÍTICO: No se pudo leer el CSV.")

@app.route('/analizar', methods=['POST'])
def endpoint_analizar():
    datos = request.json
    resultado = cerebro.analizar_dato_api(datos)
    return jsonify({"diagnostico": resultado})

if __name__ == '__main__':
    # Debug=False para evitar problemas de reinicio en Windows
    app.run(port=5000, debug=False)