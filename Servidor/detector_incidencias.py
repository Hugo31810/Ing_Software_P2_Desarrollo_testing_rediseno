import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from Servidor.patron_observer import notificadorIncidencia

class DetectorIncidencias:
    def __init__(self):
        self.modelo = RandomForestClassifier(n_estimators=50, random_state=42)
        self.notificador = notificadorIncidencia()
        self.entrenado = False

    def _generar_etiquetas(self, df):
        """
        Calcula diferencias y define reglas de incidencia. 
        Calculamos diff aquí para que los tests no fallen por KeyError.
        """
        # Asegurar que los datos están ordenados para el cálculo
        df = df.sort_values(by=['tiempo'])
        
        # Crear columnas de diferencia si no existen (necesario para los tests)
        df['diff_t'] = df['tiempo'].diff().fillna(0)
        df['diff_v'] = df['voltageReceiver1'].diff().abs().fillna(0)

        # Regla (i): Tiempo > 120s | Regla (ii): Salto Voltaje >= 0.5V
        condiciones = [
            (df['diff_t'] > 120),
            (df['diff_v'] >= 0.5)
        ]
        etiquetas = ['IncidenciaTiempo', 'SaltoVoltaje']
        
        df['target'] = np.select(condiciones, etiquetas, default='Normal')
        return df

    def entrenar(self, df_datos):
        # 1. Etiquetamos (ahora incluye el cálculo de diff_t y diff_v)
        df = self._generar_etiquetas(df_datos.copy())

        # 2. Features para la IA
        X = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        y = df['target']

        # 3. Split 80/20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
        
        print("--> [Desarrollo] Entrenando con reglas: >120s y salto >=0.5V")
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        
        return df.loc[X_test.index]

    def ejecutar_analisis(self, df_nuevos):
        if not self.entrenado:
            print("Error: Modelo no entrenado.")
            return

        # Preparamos los nuevos datos igual que en el entrenamiento
        df = self._generar_etiquetas(df_nuevos.copy())
        features = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        predicciones = self.modelo.predict(features)

        incidentes_count = 0
        for i, pred in enumerate(predicciones):
            if pred != 'Normal':
                incidentes_count += 1
                incidencia = {
                    'tipo': pred,
                    'hora': df['tiempo'].iloc[i],
                    'v1': df['voltageReceiver1'].iloc[i]
                }
                # Mantenemos el nombre que tus tests esperan
                self.notificador.notifySuscribers(incidencia)

        print(f"--> [Desarrollo] Análisis finalizado. Incidentes: {incidentes_count}")
