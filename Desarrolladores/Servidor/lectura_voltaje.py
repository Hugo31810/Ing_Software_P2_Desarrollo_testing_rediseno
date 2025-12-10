import pandas as pd


class LecturaVoltaje:
    def __init__(self, ruta_csv):
        self.ruta_csv= ruta_csv

    def leer_csv(self):
        """
        Lee el CSV, convierte fechas y pivota la tabla para que
        cada fila sea un instante único con columnas v1, v2 y status.
        """
        try:
            # Leemos con ; porque es el separador de tu archivo
            df = pd.read_csv(self.ruta_csv, sep=';')

            # Convertimos columna tiempo a datetime
            df['tiempo'] = pd.to_datetime(df['tiempo'], format='%d/%m/%Y %H:%M')

            # PIVOTING: Transformamos filas en columnas
            # Esto es vital porque tu CSV tiene los sensores en filas separadas
            df_pivot = df.pivot_table(index=['tiempo', 'id'],
                                      columns='medida',
                                      values='valor',
                                      aggfunc='mean').reset_index()

            # Limpieza de estructura
            df_pivot.columns.name = None
            df_pivot = df_pivot.dropna()

            print(f"--> [Desarrollo] Datos cargados y transformados: {len(df_pivot)} registros.")
            return df_pivot

        except FileNotFoundError:
            print("Error: Archivo no encontrado.")
            return None