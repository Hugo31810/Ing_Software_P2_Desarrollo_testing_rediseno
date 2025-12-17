import pandas as pd
from Servidor.lectura_voltaje import lecturaVoltaje
from Servidor.detector_incidencias import DetectorIncidencias


# 1. Test de requisito funcional
def test_requisito_presencia_tren():
    lector = lecturaVoltaje()

    # 0 = hay tren
    assert lector.detectarTren(0) is True

    # 1 = no hay tren
    assert lector.detectarTren(1) is False


# 2. Test de reglas de negocio (clasificación)
def test_clasificacion_voltajes():
    cerebro = DetectorIncidencias()

    df_test = pd.DataFrame({
        'voltageReceiver1': [10, 1700, 3000],
        'voltageReceiver2': [100, 100, 100],
        'status': [0, 0, 0]
    })

    resultado = cerebro._generar_etiquetas(df_test)

    assert resultado.iloc[0]['target'] == 'AusenciaDatos'
    assert resultado.iloc[1]['target'] == 'Normal'
    assert resultado.iloc[2]['target'] == 'SaltoVoltaje'


# 3. Test de integridad del dataset
def test_lectura_csv():
    lector = lecturaVoltaje()
    df = lector.leerCSV("Dataset-CV.csv")

    assert df is not None, "No se pudo leer el CSV"
    assert not df.empty, "El DataFrame está vacío"
    assert 'voltageReceiver1' in df.columns
    assert 'voltageReceiver2' in df.columns
    assert 'status' in df.columns
