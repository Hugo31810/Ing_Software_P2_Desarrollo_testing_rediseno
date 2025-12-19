import sys
import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lectura_voltaje import lecturaVoltaje

# --- BLOQUE DE RUTAS ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.dirname(directorio_actual)
ruta_csv = os.path.join(directorio_raiz, "Dataset-CV.csv")


# -----------------------

class CerebroServidor:
    def __init__(self):
        self.modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        self.entrenado = False

    def entrenar_sistema_interno(self):
        print(f"--> [Servidor] Buscando CSV en: {ruta_csv}")
        lector = lecturaVoltaje()
        df = lector.leerCSV(ruta_csv)  # Usamos la ruta dinámica

        if df is None:
            print("❌ ERROR CRÍTICO: No se encuentra el Dataset-CV.csv")
            return False

        print("--> [Servidor] Generando etiquetas...")
        df['target'] = np.select(
            [(df['voltageReceiver1'] < 50), (df['voltageReceiver1'] > 2000)],
            ['AusenciaDatos', 'SaltoVoltaje'],
            default='Normal'
        )
        X = df[['voltageReceiver1', 'voltageReceiver2', 'status']]
        y = df['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        print("--> [Servidor] IA Entrenada y Lista. ✅")
        return True

    def detectarSaltoFrecuencia(self, datos_json):
        if not self.entrenado:
            return "Servidor No Entrenado"

        input_data = pd.DataFrame([{
            'voltageReceiver1': datos_json['voltageReceiver1'],
            'voltageReceiver2': datos_json['voltageReceiver2'],
            'status': datos_json['status']
        }])
        return self.modelo.predict(input_data)[0]


app = Flask(__name__)
cerebro = CerebroServidor()
cerebro.entrenar_sistema_interno()


@app.route('/analizar', methods=['POST'])
def endpoint_analizar():
    datos = request.json
    resultado = cerebro.detectarSaltoFrecuencia(datos)
    return jsonify({"diagnostico": resultado})


if __name__ == '__main__':
    app.run(port=5000, debug=True)