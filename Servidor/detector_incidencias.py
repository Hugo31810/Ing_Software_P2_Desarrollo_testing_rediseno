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
        """Calcula diferencias temporales y de voltaje por dispositivo."""
        # Ordenar por dispositivo y tiempo para calcular diferencias reales
        sort_cols = ['dispositivo_id', 'tiempo'] if 'dispositivo_id' in df.columns else ['tiempo']
        df = df.sort_values(by=sort_cols)

        # Delta de tiempo y voltaje respecto a la fila anterior
        if 'dispositivo_id' in df.columns:
            df['diff_t'] = df.groupby('dispositivo_id')['tiempo'].diff().fillna(0)
            df['diff_v'] = df.groupby('dispositivo_id')['voltageReceiver1'].diff().abs().fillna(0)
        else:
            df['diff_t'] = df['tiempo'].diff().fillna(0)
            df['diff_v'] = df['voltageReceiver1'].diff().abs().fillna(0)
        return df

    def _generar_etiquetas(self, df):
        """Define las nuevas reglas de incidencia para el entrenamiento."""
        condiciones = [
            (df['diff_t'] > 120),    # Incidencia tipo (i): Salto temporal
            (df['diff_v'] >= 0.5)    # Salto de voltaje >= 0.5V
        ]
        etiquetas = ['IncidenciaTiempo', 'SaltoVoltaje']
        df['target'] = np.select(condiciones, etiquetas, default='Normal')
        return df

    def entrenar(self, df_datos):
        df = self._preprocesar(df_datos.copy())
        df = self._generar_etiquetas(df)

        # Entrenamos con las diferencias (deltas) para que la IA detecte los saltos
        X = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
        
        print("--> [Desarrollo] Entrenando modelo con reglas de saltos (0.5V / 120s)...")
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        return df.loc[X_test.index]

    def ejecutar_analisis(self, df_nuevos):
        if not self.entrenado:
            print("Error: Modelo no entrenado.")
            return

        df = self._preprocesar(df_nuevos.copy())
        features = df[['voltageReceiver1', 'voltageReceiver2', 'status', 'diff_t', 'diff_v']]
        predicciones = self.modelo.predict(features)

        print(f"--> [Desarrollo] Analizando {len(df)} registros...")

        incidentes_count = 0
        for i, pred in enumerate(predicciones):
            if pred != 'Normal':
                incidentes_count += 1
                incidencia = {
                    'tipo': pred,
                    'hora': df['tiempo'].iloc[i],
                    'v1': df['voltageReceiver1'].iloc[i]
                }
                # Mantenemos el nombre sin guion bajo para tus tests
                self.notificador.notifySuscribers(incidencia)

        print(f"--> [Desarrollo] Análisis finalizado. Incidentes detectados: {incidentes_count}")
