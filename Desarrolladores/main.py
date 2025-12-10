import matplotlib.pyplot as plt
from lectura_voltaje import LecturaVoltaje
from patron_observer import SuscriptorAusenciaDatos, SuscriptorSaltoVoltaje
from detector_incidencias import DetectorIncidencias


def main():
    print("===INICIO DEL SISTEMA (ROL DESARROLLADOR)===")

    # 1. Instanciación y Carga
    archivo = "Dataset-CV.csv"
    lector = LecturaVoltaje(archivo)
    datos = lector.leer_csv()

    if datos is None: return

    # 2. Configuración de Arquitectura
    detector = DetectorIncidencias()

    # Suscribimos los observers
    detector.notificador.add_subscriber(SuscriptorAusenciaDatos())
    detector.notificador.add_subscriber(SuscriptorSaltoVoltaje())

    # 3. Entrenamiento (Machine Learning)
    # Obtenemos los datos de prueba (20%) para la simulación
    datos_test = detector.entrenar(datos)

    # 4. Ejecución (Simulación tiempo real)
    detector.ejecutar_analisis(datos_test)

    # 5. Visualización (Requerimiento Matplotlib)
    print("--> [Desarrollo] Generando gráfico de resultados...")

    # Tomamos una muestra para que el gráfico sea legible
    muestra = datos.head(200)

    plt.figure(figsize=(10, 5))
    plt.plot(muestra['tiempo'], muestra['voltageReceiver1'], label='Receptor 1', color='blue')
    plt.plot(muestra['tiempo'], muestra['voltageReceiver2'], label='Receptor 2', color='green')
    plt.title("Monitorización de Voltajes (Muestra)")
    plt.xlabel("Tiempo")
    plt.ylabel("Voltaje")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()