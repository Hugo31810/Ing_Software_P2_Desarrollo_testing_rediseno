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

    df = pd.DataFrame({
        'voltageReceiver1': [10, 1700, 3000],
        'voltageReceiver2': [100, 100, 100],
        'status': [0, 0, 0]
    })

    df_et = detector._generar_etiquetas(df)

    assert 'target' in df_et.columns


def test_generar_etiquetas_valores_correctos():
    detector = DetectorIncidencias()

    df = pd.DataFrame({
        'voltageReceiver1': [10, 1700, 3000],
        'voltageReceiver2': [100, 100, 100],
        'status': [0, 0, 0]
    })

    df_et = detector._generar_etiquetas(df)

    assert df_et.iloc[0]['target'] == 'AusenciaDatos'
    assert df_et.iloc[1]['target'] == 'Normal'
    assert df_et.iloc[2]['target'] == 'SaltoVoltaje'


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

    df = pd.DataFrame({
        'voltageReceiver1': [100],
        'voltageReceiver2': [100],
        'status': [0],
        'tiempo': [1]
    })

    resultado = detector.ejecutar_analisis(df)

    assert resultado is None


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

