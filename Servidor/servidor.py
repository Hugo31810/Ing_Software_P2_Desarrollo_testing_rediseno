import sys
import os
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lectura_voltaje import lecturaVoltaje
from datetime import datetime

# --- BLOQUE DE RUTAS ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.dirname(directorio_actual)
ruta_csv = os.path.join(directorio_raiz, "Dataset-CV.csv")

# -----------------------

class CerebroServidor:
    def __init__(self):
        # Aumentamos un poco los estimadores para que aprenda mejor las nuevas reglas
        self.modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        self.entrenado = False

        # MEMORIA: Necesaria para calcular diferencias en tiempo real
        self.ultimo_tiempo = None
        self.ultimo_voltaje = None

    def entrenar_sistema_interno(self):
        print(f"--> [Servidor] Buscando CSV en: {ruta_csv}")
        lector = lecturaVoltaje()
        df = lector.leerCSV(ruta_csv)

        if df is None:
            print("❌ ERROR: No se encuentra el Dataset.")
            return False

        print("--> [Servidor] Aplicando Lógica Dinámica (Deltas)...")

        # 1. ORDENAR: Fundamental para calcular diferencias temporales
        df = df.sort_values('tiempo')

        # 2. INGENIERÍA DE CARACTERÍSTICAS (Feature Engineering)
        # Calculamos la diferencia respecto a la fila anterior
        df['delta_voltaje'] = df['voltageReceiver1'].diff().abs().fillna(0)
        df['delta_tiempo'] = df['tiempo'].diff().dt.total_seconds().fillna(0)

        # 3. APLICAR TU NUEVA LÓGICA
        # Condición 1: Ausencia de datos (> 2 minutos = 120 segundos)
        cond_ausencia = df['delta_tiempo'] > 120

        # Condición 2: Salto de voltaje (> 0.5 V)
        cond_salto = df['delta_voltaje'] > 500

        # Generamos las etiquetas basadas en TUS reglas
        df['target'] = np.select(
            [cond_ausencia, cond_salto],
            ['AusenciaDatos', 'SaltoVoltaje'],
            default='Normal'
        )

        # 4. ENTRENAMIENTO
        # IMPORTANTE: El modelo ahora debe recibir los deltas, no solo los valores brutos
        X = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'delta_voltaje', 'delta_tiempo']]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        print(f"--> [Servidor] IA Entrenada con lógica dinámica. ✅")
        print(f"    (Detectados {sum(cond_ausencia)} casos de Ausencia y {sum(cond_salto)} Saltos en histórico)")
        return True

    def detectarSaltoFrecuencia(self, datos_json):
        if not self.entrenado:
            return "Servidor No Entrenado"

        # Procesar tiempo actual (asumimos que el cliente envía o usamos hora servidor)
        tiempo_actual = datetime.now()
        voltaje_actual = datos_json['voltageReceiver1']

        # CÁLCULO DE DELTAS EN TIEMPO REAL
        if self.ultimo_tiempo is None:
            # Primer dato: no hay anterior, asumimos todo 0 (Normal)
            d_voltaje = 0
            d_tiempo = 0
        else:
            d_voltaje = abs(voltaje_actual - self.ultimo_voltaje)
            d_tiempo = (tiempo_actual - self.ultimo_tiempo).total_seconds()

        # Actualizamos la memoria para la siguiente vez
        self.ultimo_tiempo = tiempo_actual
        self.ultimo_voltaje = voltaje_actual

        # Preparamos el DataFrame con la MISMA estructura que en el entrenamiento
        input_data = pd.DataFrame([{
            'voltageReceiver1': voltaje_actual,
            'voltageReceiver2': datos_json['voltageReceiver2'],
            'status': datos_json['status'],
            'delta_voltaje': d_voltaje,  # <--- Nuevos datos
            'delta_tiempo': d_tiempo  # <--- Nuevos datos
        }])

        prediccion = self.modelo.predict(input_data)[0]
        return prediccion

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