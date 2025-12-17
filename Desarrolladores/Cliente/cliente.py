import requests
import time
import matplotlib.pyplot as plt
from lectura_voltaje import lecturaVoltaje


# --- CLASE UML: VisualizacionIncidencias ---
class VisualizacionIncidencias:
    def __init__(self):
        self.Incidencias=[]
        self.Voltajes = []
        self.Tiempos = []

    def Visualizador(self):
        """ Operación UML: Pinta los resultados acumulados """
        if not self.Voltajes:
            print("No hay datos para visualizar.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.Tiempos, self.Voltajes, label='Voltaje R1', color='blue', alpha=0.6)

        # Pintar incidencias detectadas como puntos rojos
        for inc in self.Incidencias:
            plt.scatter(inc['t'], inc['v'], color='red', s=50, label='Incidencia', zorder=5)

        # Truco para evitar duplicar labels en la leyenda
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())

        plt.title("Cliente: Monitorización de Vía (Respuesta del Servidor)")
        plt.xlabel("Muestras")
        plt.ylabel("Voltaje (V)")
        plt.grid(True)
        print("--> [Cliente] Abriendo gráfico...")
        plt.show()


# --- SIMULACIÓN DEL CLIENTE ---
def main():
    print("=== CLIENTE INICIADO ===")
    url = "http://127.0.0.1:5000/analizar"

    # 1. Cargar datos para simular los sensores del tren
    lector = lecturaVoltaje()
    datos_totales = lector.leerCSV(r".\Dataset-CV.csv")

    # Tomamos una muestra de 100 datos para la demo
    datos_simulacion = datos_totales.sort_values('tiempo').head(100)
    gui = VisualizacionIncidencias()

    print(f"--> Enviando {len(datos_simulacion)} lecturas al servidor...")


    for index, row in datos_simulacion.iterrows():
        """ BUCLE PARA PROBAR SI DETECTA ERRORES (ROJO)
        # 1. Definimos el voltaje a usar (Normal o Trucado)
        voltaje_final = row['voltageReceiver1']

        # --- SABOTAJE PARA TESTING ---
        # En el registro 10, forzamos un valor de 3000V para probar la alerta
        if index == 10:
            print("!!! TESTER: Forzando salto de voltaje (3000V) para probar alertas !!!")
            voltaje_final = 3000
        # -----------------------------

        # 2. Preparamos el paquete con el voltaje final
        payload = {
            "voltageReceiver1": voltaje_final,  # <--- Usamos la variable, no la fila directa
            "voltageReceiver2": row['voltageReceiver2'],
            "status": row['status']
        }

        try:
            # ENVIAR POR HTTP (REST)
            respuesta = requests.post(url, json=payload)
            diagnostico = respuesta.json().get('diagnostico')

            print(f"Enviado: {voltaje_final}V | Diagnóstico Servidor: {diagnostico}")

            # 3. Guardar para el gráfico (¡Importante guardar el valor trucado!)
            gui.Voltajes.append(voltaje_final)
            gui.Tiempos.append(str(row['tiempo']))

            # Si el servidor detecta fallo, guardamos la incidencia para el punto rojo
            if diagnostico != 'Normal':
                gui.Incidencias.append({'t': str(row['tiempo']), 'v': voltaje_final})

        except Exception as e:
            print(f"Error: El servidor no responde. Detalle: {e}")
            break
        """

        # Paquete de datos (simula lectura de sensor)
        payload = {
            "voltageReceiver1": row['voltageReceiver1'],
            "voltageReceiver2": row['voltageReceiver2'],
            "status": row['status']
        }

        try:
            # ENVIAR POR HTTP (REST)
            respuesta = requests.post(url, json=payload)
            diagnostico = respuesta.json().get('diagnostico')

            print(f"Enviado: {payload['voltageReceiver1']}V | Diagnóstico Servidor: {diagnostico}")

            # Guardar para el gráfico
            gui.Voltajes.append(row['voltageReceiver1'])
            gui.Tiempos.append(str(row['tiempo']))

            if diagnostico != 'Normal':
                gui.Incidencias.append({'t': str(row['tiempo']), 'v': row['voltageReceiver1']})

        except:
            print("Error: El servidor no responde. ¿Ejecutaste servidor.py?")
            break


    # 2. Visualizar al terminar
    gui.Visualizador()


if __name__ == "__main__":
    main()
