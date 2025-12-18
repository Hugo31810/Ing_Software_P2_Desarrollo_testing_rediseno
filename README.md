# Railway Incidence Management System – Development, Testing & Redesign

Este repositorio contiene la **fase de desarrollo, testing y rediseño** del *Railway Incidence Management System*, una aplicación software orientada a la **detección y predicción de incidencias en infraestructuras ferroviarias**.

El proyecto parte de los **requisitos y el diseño UML definidos en la fase previa** y se centra en su **implementación en Python**, la validación mediante **testing sistemático** y la **evolución del diseño** cuando ha sido necesario.

---

## 🎯 Objetivo del proyecto

Los objetivos principales de esta fase son:

- Implementar el sistema diseñado en la fase de requisitos y diseño
- Desarrollar una solución funcional en **Python**
- Aplicar **técnicas de testing** para garantizar la calidad del código
- Utilizar **Machine Learning** para la predicción de incidencias
- Realizar un **rediseño parcial** del sistema si el desarrollo lo requiere
- Justificar técnica y arquitectónicamente los cambios realizados

Este repositorio corresponde a la **fase de implementación y validación** del sistema.

---

## 🧩 Contexto del sistema

El sistema procesa datos eléctricos procedentes de **dispositivos situados en vías ferroviarias**, almacenados en ficheros CSV.

Cada registro contiene:
- Estado de la vía (`status`):
  - `1`: vía libre
  - `0`: vía ocupada por un tren
- Valores de voltaje de dos receptores:
  - `voltageReceiver1` (canal A)
  - `voltageReceiver2` (canal B)
- Marca temporal asociada a la medición

A partir de estos datos, el sistema detecta y predice incidencias relevantes para la operación ferroviaria.

---

## 👥 Equipo y roles

Los roles del equipo se han asignado conforme a la definición de esta fase del proyecto:

### 🧑‍💻 Developers
- **Pablo Sastre Noriega**
- **Héctor Santiago Martínez**
- **Raúl Vicente Sánchez**
- **Tomás Cano Santa Catalina**

### 🧪 Tester
- **Hugo Salvador Aizpún**

### 🏗️ Software Architect
- **Iván De Rada López**

Cada rol ha contribuido al desarrollo, validación y evolución del sistema para asegurar su calidad y coherencia arquitectónica.

---

## 🧠 Predicción de incidencias (Machine Learning)

El sistema incorpora un módulo de **Machine Learning** para la predicción de incidencias, basado en:

- Selección del algoritmo más adecuado al problema
- División del dataset:
  - 80% entrenamiento
  - 20% predicción
- Evaluación del rendimiento durante la fase de testing

El modelo se integra como parte del flujo principal del sistema.

---

## 🧪 Testing

Se ha llevado a cabo un proceso de **testing estructurado**, que incluye:

- Tests unitarios de los principales módulos
- Validación de la lectura y adaptación del dataset
- Comprobación del correcto funcionamiento del sistema de predicción
- Detección y corrección de errores lógicos y estructurales

Los problemas detectados y sus soluciones se documentan tanto en el código como en la presentación final del proyecto.

---

## 🔄 Rediseño

Durante el desarrollo se ha evaluado de forma continua la adecuación del diseño original.

Cuando ha sido necesario, se ha realizado un **rediseño parcial**, documentando:

- Limitaciones del diseño inicial
- Cambios aplicados
- Justificación técnica y arquitectónica
- Impacto del rediseño en el sistema final


---

## 📄 Entregables

El proyecto incluye:

- Código fuente completo en Python
- Tests automatizados
- Dataset adaptado al problema
- Presentación con:
  - Arquitectura final
  - Fallos detectados durante el testing
  - Soluciones aplicadas
  - Rediseño realizado
  - Librerías y decisiones técnicas

---

## 📌 Relación con otros repositorios

- **Fase de análisis y diseño:**  
  `railway-incidence-management-system-requirements-and-design`

Este repositorio constituye la **continuación natural** del proyecto.

---

## ✍️ Autoría

Proyecto desarrollado en el marco de la asignatura **Ingeniería del Software**  
Universidad Rey Juan Carlos – Curso 2025–2026
