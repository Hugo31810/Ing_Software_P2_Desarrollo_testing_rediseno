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

    def _preprocesar(self, df):
        """Calcula diferencias temporales y de voltaje para la IA."""
        df = df.sort_values(by=['tiempo'])
        df['diff_t'] = df['tiempo'].diff().fillna(0)
        df['diff_v'] = df['voltageReceiver1'].diff().abs().fillna(0)
        return df

    def _generar_etiquetas(self, df):
        # Regla (i): Tiempo > 120s | Regla (ii): Salto Voltaje >= 0.5V
        condiciones = [
            (df['diff_t'] > 120),
            (df['diff_v'] >= 0.5)
        ]
        etiquetas = ['IncidenciaTiempo', 'SaltoVoltaje']
        df['target'] = np.select(condiciones, etiquetas, default='Normal')
        return df

    def entrenar(self, df_datos):
        df = self._preprocesar(df_datos.copy())
        df = self._generar_etiquetas(df)

        # Entrenamos con las diferencias para que la IA entienda los "saltos"
        X = df[['voltageReceiver1', 'diff_t', 'diff_v']]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        return df.loc[X_test.index]

    def ejecutar_analisis(self, df_nuevos):
        if not self.entrenado:
            return

        df = self._preprocesar(df_nuevos.copy())
        features = df[['voltageReceiver1', 'diff_t', 'diff_v']]
        predicciones = self.modelo.predict(features)

        for i, pred in enumerate(predicciones):
            if pred != 'Normal':
                incidencia = {
                    'tipo': pred,
                    'hora': df['tiempo'].iloc[i],
                    'v1': df['voltageReceiver1'].iloc[i]
                }
                # Aquí usamos el nombre corregido (con _)
                self.notificador.notify_subscribers(incidencia)
