import pandas as pd


class lecturaVoltaje:
    """
    Clase del UML encargada de la persistencia y lectura de datos.
    """

    def __init__(self):
        self.estadoVoltaje= 0
        self.hora = None
        self.idDispositivo = 0

    def leerCSV(self, ruta_archivo):
        try:
            # 1. Leemos el CSV (tiempo, medida, valor)
            df = pd.read_csv(ruta_archivo, sep=';')

            # 2. Pivotamos usando SOLO 'tiempo' como índice
            df_pivot = df.pivot_table(index='tiempo',
                                      columns='medida',
                                      values='valor').reset_index()

            # 3. Limpiamos el nombre de las columnas (quita el nombre 'medida')
            df_pivot.columns.name = None

            # 4. Aseguramos que existan todas las columnas necesarias
            columnas_necesarias = ['voltageReceiver1', 'voltageReceiver2', 'status']

            for col in columnas_necesarias:
                if col not in df_pivot.columns:
                    df_pivot[col] = 0  # Rellenar con 0 si falta

            # Convertimos 'status' a enteros
            df_pivot['status'] = df_pivot['status'].fillna(0).astype(int)

            return df_pivot.dropna()

        except FileNotFoundError:
            print(f"Error: No se encuentra el archivo en: {ruta_archivo}")
            return None
        except KeyError as e:
            # Este es el error que te salía antes, ahora debería arreglarse
            print(f"Error de estructura en CSV: Falta la columna {e}")
            return None
        except Exception as e:
            print(f"Error leyendo CSV: {e}")
            return None

    def detectarTren(self, estadoVoltaje):
        """ Operación UML """
        return estadoVoltaje == 0