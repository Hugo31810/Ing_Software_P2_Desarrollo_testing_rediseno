from abc import ABC, abstractmethod
import datetime

# --- INTERFAZ LISTENER ---
class Listener(ABC):
    @abstractmethod
    def Update(self, incidencia):
        pass

# --- SUJETO (NOTIFICADOR) ---
class notificadorIncidencia:
    def __init__(self):
        self.suscribers =[] # Atributo UML

    def Addsuscriber(self, suscriber: Listener):
        self.suscribers.append(suscriber)

    def Removesuscriber(self, suscriber: Listener):
        self.suscribers.remove(suscriber)

    def notifySuscribers(self, incidencia):
        # En el diagrama se pasa la incidencia a los suscriptores
        for sub in self.suscribers:
            sub.Update(incidencia)

# --- SUSCRIPTORES CONCRETOS ---
class suscriptorAusenciaDatos(Listener):
    def Update(self, incidencia):
        if incidencia['tipo'] == 'AusenciaDatos':
            print(f"   [SERVIDOR LOG] 🔴 ALERTA CRÍTICA: Ausencia de Datos detectada.")

class suscriptorSaltoVoltaje(Listener):
    def Update(self, incidencia):
        if incidencia['tipo'] == 'SaltoVoltaje':
            val = incidencia.get('valor', 0)
            print(f"   [SERVIDOR LOG] ⚡ ALERTA: Salto de Voltaje ({val}V).")