import pandas as pd


class lecturaVoltaje:
    """
    Clase del UML encargada de la persistencia y lectura de datos.
    """

    def __init__(self):
        self.estadoVoltaje= 0
        self.hora = None
        self.idDispositivo = 0

    def leerCSV(self, ruta_csv):
        """
        Operación UML: leerCSV
        Realiza la ETL: Lee el CSV crudo, pivota la tabla y limpia nulos.
        """
        try:
            # Lectura con separador de punto y coma
            df = pd.read_csv(ruta_csv, sep=';')

            # Conversión de fecha
            df['tiempo'] = pd.to_datetime(df['tiempo'], format='%d/%m/%Y %H:%M')

            # PIVOTING: Transformación necesaria para tu dataset específico
            df_pivot = df.pivot_table(index=['tiempo', 'id'],
                                      columns='medida',
                                      values='valor',
                                      aggfunc='mean').reset_index()

            # Limpieza final
            df_pivot.columns.name = None
            return df_pivot.dropna()

        except FileNotFoundError:
            print(f"Error: No se encuentra el archivo {ruta_csv}")
            return None
        except Exception as e:
            print(f"Error procesando CSV: {e}")
            return None

    def detectarTren(self, estadoVoltaje):
        """ Operación UML """
        return estadoVoltaje == 1