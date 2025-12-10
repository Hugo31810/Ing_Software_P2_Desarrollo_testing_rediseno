from abc import ABC, abstractmethod

# Interfaz (Abstracta)
class Listener(ABC):
    @abstractmethod
    def update(self, incidencia):
        pass

# Sujeto (Notificador)
class NotificadorIncidencia:
    def __init__(self):
        self._suscriptores =[]

    def add_subscriber(self, subscriber: Listener):
        self._suscriptores.append(subscriber)

    def remove_subscriber(self, subscriber: Listener):
        self._suscriptores.remove(subscriber)

    def notify_subscribers(self, incidencia):
        for sub in self._suscriptores:
            sub.update(incidencia)

# Implementación Concreta: Suscriptor Ausencia
class SuscriptorAusenciaDatos(Listener):
    def update(self, incidencia):
        if incidencia['tipo'] == 'AusenciaDatos':
            print(f"   [ALERTA] 🔴 Ausencia de datos en {incidencia['hora']}. V1: {incidencia['v1']}")

# Implementación Concreta: Suscriptor Salto
class SuscriptorSaltoVoltaje(Listener):
    def update(self, incidencia):
        if incidencia['tipo'] == 'SaltoVoltaje':
            print(f"   [ALERTA] ⚡ Salto de Tensión detectado en {incidencia['hora']}. V1: {incidencia['v1']}")