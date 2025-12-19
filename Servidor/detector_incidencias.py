import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from patron_observer import notificadorIncidencia
from datetime import datetime


class DetectorIncidencias:
    def __init__(self):
        self.modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        self.notificador = notificadorIncidencia()
        self.entrenado = False

        # MEMORIA para streaming (Dato a dato)
        self.ultimo_tiempo = None
        self.ultimo_v1 = None
        self.ultimo_v2 = None

    def _generar_etiquetas(self, df):
        try:
            df['tiempo'] = pd.to_datetime(df['tiempo'], dayfirst=True)
        except:
            # Plan B: Si falla, forzamos el formato exacto del CSV
            df['tiempo'] = pd.to_datetime(df['tiempo'], format="%d/%m/%Y %H:%M")

        df = df.sort_values('tiempo')

        # Calculamos diferencias (Deltas)
        df['delta_v1'] = df['voltageReceiver1'].diff().abs().fillna(0)
        df['delta_v2'] = df['voltageReceiver2'].diff().abs().fillna(0)
        df['delta_tiempo'] = df['tiempo'].diff().dt.total_seconds().fillna(0)

        # Reglas: Ausencia (>120s) O Salto (>500mV en cualquiera de los dos)
        cond_ausencia = df['delta_tiempo'] > 120
        cond_salto = (df['delta_v1'] > 500) | (df['delta_v2'] > 500)

        df['target'] = np.select(
            [cond_ausencia, cond_salto],
            ['AusenciaDatos', 'SaltoVoltaje'],
            default='Normal'
        )
        return df

    def entrenar(self, df_datos):
        print("--> [Detector] Generando etiquetas y entrenando...")
        df_etiquetado = self._generar_etiquetas(df_datos.copy())

        features = ['voltageReceiver1', 'voltageReceiver2', 'status',
                    'delta_v1', 'delta_v2', 'delta_tiempo']

        X = df_etiquetado[features]
        y = df_etiquetado['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        print(f"--> [Detector] Modelo entrenado. Score: {self.modelo.score(X_test, y_test):.2f}")

        return df_etiquetado.loc[X_test.index]

    def analizar_dato_api(self, datos_json):
        if not self.entrenado:
            return "Servidor No Entrenado"

        v1 = datos_json['voltageReceiver1']
        v2 = datos_json['voltageReceiver2']

        # Convertimos el texto del JSON a fecha real para hacer la resta
        try:
            # Aquí también aplicamos dayfirst por seguridad
            tiempo_actual = pd.to_datetime(datos_json['tiempo'], dayfirst=True)
        except:
            tiempo_actual = datetime.now()

        # Usamos la memoria para calcular el salto
        if self.ultimo_tiempo is None:
            d_v1, d_v2, d_tiempo = 0, 0, 0
        else:
            d_v1 = abs(v1 - self.ultimo_v1)
            d_v2 = abs(v2 - self.ultimo_v2)
            d_tiempo = (tiempo_actual - self.ultimo_tiempo).total_seconds()

        # Actualizamos la memoria
        self.ultimo_v1 = v1
        self.ultimo_v2 = v2
        self.ultimo_tiempo = tiempo_actual

        # Preparamos los datos para la IA
        input_data = pd.DataFrame([{
            'voltageReceiver1': v1,
            'voltageReceiver2': v2,
            'status': datos_json['status'],
            'delta_v1': d_v1,
            'delta_v2': d_v2,
            'delta_tiempo': d_tiempo
        }])

        prediccion = self.modelo.predict(input_data)[0]

        if prediccion != 'Normal':
            self.notificador.notifySuscribers({
                'tipo': prediccion,
                'hora': str(tiempo_actual),
                'v1': v1, 'v2': v2
            })

        return prediccion