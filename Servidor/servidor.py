from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from lectura_voltaje import lecturaVoltaje
from patron_observer import notificadorIncidencia, suscriptorAusenciaDatos, suscriptorSaltoVoltaje


# --- CLASE UML: DetectroIncidencias (Cerebro del sistema) ---
class DetectorIncidencias:
    def __init__(self):
        # Atributos UML
        self.ultimahora = None
        self.frecuencia=0

        # Componentes internos
        self.modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        self.entrenado = False
        self.notificador = notificadorIncidencia()

        # Suscribimos los listeners aquí mismo para que el servidor escuche
        self.notificador.Addsuscriber(suscriptorAusenciaDatos())
        self.notificador.Addsuscriber(suscriptorSaltoVoltaje())

    def detectarAusenciaDatos(self, datos):
        """ Operación UML: Implementada con lógica ML """
        return datos['voltageReceiver1'] < 10  # Umbral de ejemplo

    def detectarSaltoFrecuencia(self, datos_json):
        """
        Operación UML principal adaptada a ML.
        Recibe datos, predice y si hay fallo, notifica.
        """
        if not self.entrenado:
            return "SistemaNoListo"

        # Preparamos el dato para la IA (DataFrame de 1 fila)
        df_input = pd.DataFrame([datos_json])

        # PREDICCIÓN ML
        prediccion = self.modelo.predict(df_input[['voltageReceiver1', 'voltageReceiver2', 'status']])[0]

        # Si la predicción no es Normal, usamos el Patrón Observer
        if prediccion != 'Normal':
            incidencia = {
                'tipo': prediccion,
                'valor': datos_json['voltageReceiver1']
            }
            self.notificador.notifySuscribers(incidencia)

        return prediccion

    def entrenar_sistema_interno(self):
        """ Método auxiliar para cumplir el requisito de P2 (Training) """
        lector = lecturaVoltaje()
        df = lector.leerCSV(r".\Dataset-CV.csv")

        if df is None: return False

        print("--> [Servidor] Generando etiquetas de entrenamiento...")
        # Generar etiquetas artificiales (Training Labeling)
        df['target'] = np.select(
            [(df['voltageReceiver1'] < 50), (df['voltageReceiver1'] > 2000)],
            ['AusenciaDatos', 'SaltoVoltaje'],
            default='Normal'
        )

        X = df[['voltageReceiver1', 'voltageReceiver2', 'status']]
        y = df['target']

        # Split 80/20 Requerido
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        print("--> [Servidor] Entrenando Random Forest...")
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        print("--> [Servidor] IA Entrenada y Lista.")
        return True


# --- FLASK (Infraestructura HTTP) ---
app = Flask(__name__)
cerebro = DetectorIncidencias()

# Entrenar al arrancar
cerebro.entrenar_sistema_interno()


@app.route('/analizar', methods=['POST'])
def endpoint_analizar():
    datos = request.json
    resultado = cerebro.detectarSaltoFrecuencia(datos)
    return jsonify({"diagnostico": resultado})


if __name__ == '__main__':
    # Ejecuta el servidor en puerto 5000
    app.run(port=5000, debug=True)
