import pandas as pd
import pytest
from Servidor.lectura_voltaje import lecturaVoltaje
from Servidor.detector_incidencias import DetectorIncidencias
from Servidor.patron_observer import (
    notificadorIncidencia,
    suscriptorAusenciaDatos,
    suscriptorSaltoVoltaje
)


# ======================================================
# 1. TESTS DE lecturaVoltaje (ETL + Requisitos)
# ======================================================

def test_requisito_presencia_tren():
    """
    Requisito funcional del PDF:
    status = 0 -> hay tren
    status = 1 -> no hay tren
    """
    lector = lecturaVoltaje()

    assert lector.detectarTren(0) is True
    assert lector.detectarTren(1) is False


def test_lectura_csv_devuelve_dataframe():
    lector = lecturaVoltaje()
    df = lector.leerCSV("Dataset-CV.csv")

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_lectura_csv_columnas_necesarias():
    lector = lecturaVoltaje()
    df = lector.leerCSV("Dataset-CV.csv")

    for col in ['voltageReceiver1', 'voltageReceiver2', 'status', 'tiempo']:
        assert col in df.columns


def test_lectura_csv_archivo_inexistente():
    lector = lecturaVoltaje()
    df = lector.leerCSV("archivo_que_no_existe.csv")

    assert df is None


# ======================================================
# 2. TESTS DE DetectorIncidencias (Lógica de negocio + ML)
# ======================================================

def test_generar_etiquetas_crea_target():
    detector = DetectorIncidencias()

    # CORRECCIÓN: Añadimos la columna 'tiempo' obligatoria
    df = pd.DataFrame({
        'tiempo': ['01/01/2025 10:00:00', '01/01/2025 10:01:00'],
        'voltageReceiver1': [1000, 1000],
        'voltageReceiver2': [1000, 1000],
        'status': [0, 0]
    })

    df_et = detector._generar_etiquetas(df)

    assert 'target' in df_et.columns
    assert len(df_et) == 2


def test_generar_etiquetas_valores_correctos():
    """
    Test actualizado a la NUEVA LÓGICA:
    - Salto si diferencia > 500mV
    - Ausencia si diferencia tiempo > 120s
    """
    detector = DetectorIncidencias()

    df = pd.DataFrame({
        # Caso 0: Inicio (Normal)
        # Caso 1: Salto brusco de voltaje (1000 -> 1600 = 600mV dif) -> SaltoVoltaje
        # Caso 2: Pasan 5 minutos (10:01 -> 10:06) -> AusenciaDatos
        'tiempo': [
            '01/01/2025 10:00:00',
            '01/01/2025 10:01:00',
            '01/01/2025 10:06:00'
        ],
        'voltageReceiver1': [1000, 1600, 1600],
        'voltageReceiver2': [1000, 1000, 1000],
        'status': [0, 0, 0]
    })

    df_et = detector._generar_etiquetas(df)

    # Verificamos las etiquetas generadas
    etiquetas = df_et['target'].values

    # El primero siempre es normal (no hay anterior con quien comparar)
    assert etiquetas[0] == 'Normal'
    # El segundo tiene un salto de 600mV (>500)
    assert etiquetas[1] == 'SaltoVoltaje'
    # El tercero ha tardado 5 minutos (>120s)
    assert etiquetas[2] == 'AusenciaDatos'


def test_entrenamiento_cambia_estado_entrenado():
    detector = DetectorIncidencias()

    df = pd.DataFrame({
        'voltageReceiver1': [10, 3000, 500, 100],
        'voltageReceiver2': [100, 100, 100, 100],
        'status': [0, 0, 0, 0],
        'tiempo': [1, 2, 3, 4]
    })

    detector.entrenar(df)

    assert detector.entrenado is True


def test_ejecutar_analisis_sin_entrenar():
    detector = DetectorIncidencias()

    # Datos de prueba (con tiempo para que no falle antes de llegar a la comprobación)
    datos_json = {
        'voltageReceiver1': 100,
        'voltageReceiver2': 100,
        'status': 0,
        'tiempo': '01/01/2025 10:00:00'
    }

    # Nota: Usamos analizar_dato_api que es el método que usa el servidor
    resultado = detector.analizar_dato_api(datos_json)

    # CORRECCIÓN: Ahora devuelve un mensaje, no None
    assert resultado == "Servidor No Entrenado"

# ======================================================
# 3. TESTS DEL PATRÓN OBSERVER
# ======================================================

def test_add_suscriber():
    notificador = notificadorIncidencia()
    sub = suscriptorAusenciaDatos()

    notificador.Addsuscriber(sub)

    assert sub in notificador.suscribers


def test_remove_suscriber():
    notificador = notificadorIncidencia()
    sub = suscriptorAusenciaDatos()

    notificador.Addsuscriber(sub)
    notificador.Removesuscriber(sub)

    assert sub not in notificador.suscribers


def test_notify_suscriber_ausencia(capsys):
    notificador = notificadorIncidencia()
    sub = suscriptorAusenciaDatos()

    notificador.Addsuscriber(sub)

    incidencia = {'tipo': 'AusenciaDatos'}
    notificador.notifySuscribers(incidencia)

    salida = capsys.readouterr().out
    assert "Ausencia de Datos" in salida


def test_notify_suscriber_salto(capsys):
    notificador = notificadorIncidencia()
    sub = suscriptorSaltoVoltaje()

    notificador.Addsuscriber(sub)

    incidencia = {'tipo': 'SaltoVoltaje', 'valor': 3000}
    notificador.notifySuscribers(incidencia)

    salida = capsys.readouterr().out
    assert "Salto de Voltaje" in salida


def test_suscriptor_no_reacciona_a_otro_tipo(capsys):
    sub = suscriptorSaltoVoltaje()

    sub.Update({'tipo': 'AusenciaDatos'})
    salida = capsys.readouterr().out

    assert salida == ""

