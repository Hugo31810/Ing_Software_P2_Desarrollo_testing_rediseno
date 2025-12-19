import sys
import os
import requests
import matplotlib.pyplot as plt

# Configuración de rutas para importar librerías hermanas y encontrar el CSV
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.dirname(directorio_actual)
ruta_servidor = os.path.join(directorio_raiz, 'Servidor')
ruta_csv = os.path.join(directorio_raiz, "Dataset-CV.csv")

sys.path.append(ruta_servidor)
from lectura_voltaje import lecturaVoltaje


class VisualizacionIncidencias:
    def __init__(self):
        self.Incidencias = []
        self.Voltajes = []
        self.Tiempos = []

    def Visualizador(self):
        if not self.Voltajes:
            print("No hay datos para visualizar.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.Tiempos, self.Voltajes, label='Voltaje R1', color='blue', alpha=0.6)
        # Dibujamos incidencias
        for inc in self.Incidencias:
            plt.scatter(inc['t'], inc['v'], color='red', s=50, zorder=5)

        plt.title("Monitorización Cliente")
        plt.xlabel("Muestras")
        plt.ylabel("Milivoltios (mV)")
        plt.grid(True)
        print("--> [Cliente] Mostrando gráfico...")
        plt.show()


def main():
    print("=== CLIENTE INICIADO ===")
    url = "http://127.0.0.1:5000/analizar"

    print(f"--> Leyendo datos para simulación: {ruta_csv}")
    lector = lecturaVoltaje()
    datos_totales = lector.leerCSV(ruta_csv)

    if datos_totales is None:
        print("❌ Error: No se encuentra el CSV.")
        return

    # Ordenamos por tiempo para simular correctamente
    datos_simulacion = datos_totales.sort_values('tiempo')
    gui = VisualizacionIncidencias()

    print(f"--> Enviando {len(datos_simulacion)} lecturas...")

    for index, row in datos_simulacion.iterrows():
        payload = {
            "voltageReceiver1": row['voltageReceiver1'],
            "voltageReceiver2": row['voltageReceiver2'],
            "status": row['status'],
            #Convertimos a texto para enviarlo por JSON
            "tiempo": str(row['tiempo'])
        }

        try:
            respuesta = requests.post(url, json=payload)
            diagnostico = respuesta.json().get('diagnostico')

            print(f"Enviado: {payload['voltageReceiver1']}mV | Diagnóstico: {diagnostico}")

            # Guardamos para la gráfica (solo los primeros 100 para no saturar memoria si son muchos)
            gui.Voltajes.append(row['voltageReceiver1'])
            gui.Tiempos.append(str(index))  # Usamos índice como tiempo simple para eje X

            if diagnostico != 'Normal':
                gui.Incidencias.append({'t': str(index), 'v': row['voltageReceiver1']})

        except Exception as e:
            print(f"❌ ERROR CONEXIÓN: {e}")
            break

    gui.Visualizador()


if __name__ == "__main__":
    main()