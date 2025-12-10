import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from patron_observer import NotificadorIncidencia


class DetectorIncidencias:
    def __init__(self):
        self.modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        self.notificador = NotificadorIncidencia()
        self.entrenado = False

    def _generar_etiquetas(self, df):
        """
        Método auxiliar para crear el 'Target' del entrenamiento.
        Define reglas heurísticas para enseñar a la IA qué es un fallo.
        """
        condiciones = [
            (df['voltageReceiver1'] < 50),  # Regla: Voltaje muy bajo = Ausencia
            (df['voltageReceiver1'] > 2000)  # Regla: Voltaje muy alto = Salto
        ]
        etiquetas = ['AusenciaDatos', 'SaltoVoltaje']

        # Crea columna 'target'. Si no es fallo, es 'Normal'
        df['target'] = np.select(condiciones, etiquetas, default='Normal')
        return df

    def entrenar(self, df_datos):
        # 1. Preparamos los datos
        df_etiquetado = self._generar_etiquetas(df_datos.copy())

        X = df_etiquetado[['voltageReceiver1', 'voltageReceiver2', 'status']]
        y = df_etiquetado['target']

        # 2. Split 80% Train / 20% Test (Requerimiento estricto)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        # 3. Entrenamiento
        print("--> [Desarrollo] Entrenando modelo Random Forest...")
        self.modelo.fit(X_train, y_train)
        self.entrenado = True

        # Devolvemos el set de prueba (con índices originales) para simular la ejecución
        return df_etiquetado.loc[X_test.index]

    def ejecutar_analisis(self, df_nuevos):
        """
        Recibe nuevos datos, predice y notifica si hay incidencia.
        """
        if not self.entrenado:
            print("Error:Modelo no entrenado.")
            return

        features = df_nuevos[['voltageReceiver1', 'voltageReceiver2', 'status']]
        predicciones = self.modelo.predict(features)

        # Convertimos a arrays para acceso rápido
        tiempos = df_nuevos['tiempo'].values
        v1 = df_nuevos['voltageReceiver1'].values

        print(f"--> [Desarrollo] Analizando {len(df_nuevos)} registros en tiempo real...")

        incidentes_count = 0
        for i, pred in enumerate(predicciones):
            if pred != 'Normal':
                incidentes_count += 1
                incidencia = {
                    'tipo': pred,
                    'hora': tiempos[i],
                    'v1': v1[i]
                }
                self.notificador.notify_subscribers(incidencia)

        print(f"--> [Desarrollo] Análisis finalizado. Incidentes detectados: {incidentes_count}")