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
        Define las reglas de incidencia de forma segura.
        Si faltan columnas (como en los tests), se crean con valores por defecto.
        """
        # 1. Asegurar columna 'tiempo' para el cálculo temporal
        if 'tiempo' in df.columns:
            df = df.sort_values(by=['tiempo'])
            df['diff_t'] = df['tiempo'].diff().fillna(0)
        else:
            # Si el test no manda 'tiempo', ponemos 0 para que no explote
            df['diff_t'] = 0

        # 2. Asegurar columna 'voltageReceiver1' para el salto de voltaje
        if 'voltageReceiver1' in df.columns:
            df['diff_v'] = df['voltageReceiver1'].diff().abs().fillna(0)
        else:
            df['diff_v'] = 0

        # 3. Definir condiciones basadas en los nuevos requisitos
        condiciones = [
            (df['diff_t'] > 120),    # (i) Diferencia temporal > 120s
            (df['diff_v'] >= 0.5)    # (ii) Salto de voltaje >= 0.5V
        ]
        etiquetas = ['IncidenciaTiempo', 'SaltoVoltaje']
        
        # 4. Crear columna 'target'. Si no cumple nada, es 'Normal'
        df['target'] = np.select(condiciones, etiquetas, default='Normal')
        return df

    def entrenar(self, df_datos):
        df = self._generar_etiquetas(df_datos.copy())

        # Usamos las columnas de diferencia para que la IA aprenda los patrones
        X = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
        
        print("--> [Desarrollo] Entrenando con reglas: >120s y salto >=0.5V")
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        return df.loc[X_test.index]

    def ejecutar_analisis(self, df_nuevos):
        if not self.entrenado:
            return

        df = self._generar_etiquetas(df_nuevos.copy())
        features = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        predicciones = self.modelo.predict(features)

        for i, pred in enumerate(predicciones):
            if pred != 'Normal':
                incidencia = {
                    'tipo': pred,
                    'hora': df['tiempo'].iloc[i] if 'tiempo' in df.columns else "N/A",
                    'v1': df['voltageReceiver1'].iloc[i] if 'voltageReceiver1' in df.columns else 0
                }
                # Nombre compatible con tus tests
                self.notificador.notifySuscribers(incidencia)
