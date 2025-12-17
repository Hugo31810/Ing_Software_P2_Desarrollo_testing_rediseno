import pytest
import pandas as pd
from lectura_voltaje import lecturaVoltaje
from detector_incidencias import DetectorIncidencias

# 1. Test de Lógica Inversa (Requisito PDF P2)
def test_requisito_presencia_tren():
    lector = lecturaVoltaje()
    # PDF: 0 es SI hay tren. Por tanto, detectarTren(0) debe ser True.
    assert lector.detectarTren(0) is True, "FALLO: El sistema no detecta el tren con status 0"
    # PDF: 1 es NO hay tren.
    assert lector.detectarTren(1) is False, "FALLO: El sistema detecta tren fantasma con status 1"

# 2. Test de Reglas de Incidencia (Requisito P1/Negocio)
def test_clasificacion_voltajes():
    cerebro = DetectorIncidencias()
    df_test = pd.DataFrame({
        'voltageReceiver1': [10, 1700, 3000], # Bajo, Normal, Alto
        'voltageReceiver2': [100, 100, 100],
        'status': [0, 0, 0]
    })
    resultado = cerebro._generar_etiquetas(df_test)

    assert resultado.iloc[0]['target'] == 'AusenciaDatos', "FALLO: <50 debería ser AusenciaDatos"
    assert resultado.iloc[1]['target'] == 'Normal', "FALLO: 1700 debería ser Normal"
    assert resultado.iloc[2]['target'] == 'SaltoVoltaje', "FALLO: >2000 debería ser SaltoVoltaje"

# 3. Test de Integridad de Datos (Lectura CSV)
def test_lectura_csv():
    lector = lecturaVoltaje()
    # Asegúrate de que el CSV existe para este test
    try:
        df = lector.leerCSV("Dataset-CV.csv")
        assert not df.empty, "FALLO: El DataFrame está vacío"
        assert 'voltageReceiver1' in df.columns, "FALLO: No se leen las columnas correctas"
    except FileNotFoundError:
        pytest.fail("FALLO CRÍTICO: No se encuentra Dataset-CV.csv")
