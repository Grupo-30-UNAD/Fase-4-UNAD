# Fase-4-UNAD
Tarea Fase 4  Programación - Sistema de gestión en Python con POO y manejo de excepciones.
# 🗂️ Sistema Integral de Gestión de Clientes, Servicios y Reservas

## 📌 Software FJ — Programación Orientada a Objetos en Python

Sistema desarrollado en Python bajo el paradigma de Programación Orientada a Objetos (POO) para gestionar clientes, servicios y reservas de la empresa ficticia *Software FJ*.

El proyecto implementa conceptos avanzados de:

- Abstracción
- Herencia
- Polimorfismo
- Encapsulación
- Manejo avanzado de excepciones
- Registro de eventos y errores mediante logs

El sistema funciona completamente *sin base de datos*, utilizando únicamente:

- Objetos
- Listas internas
- Manejo de archivos para logs

---

# 🎯 Objetivo del proyecto

Desarrollar una aplicación robusta y estable capaz de:

- Registrar clientes
- Gestionar servicios especializados
- Crear y procesar reservas
- Manejar errores sin detener la ejecución del sistema
- Registrar eventos y excepciones en archivos de logs

---

# 🏗️ Estructura general del sistema

Actualmente el sistema se encuentra implementado en un único archivo principal:

bash
software_fj/
│
├── main.py
└── sistema_gestion.log


---

# 🧱 Arquitectura Orientada a Objetos

## 🔷 Clase abstracta Entidad

Clase base abstracta utilizada para representar entidades generales del sistema.

### Características:

- ID único
- Nombre
- Método abstracto resumen()

python
class Entidad(ABC):


---

## 🔷 Clase Cliente

Representa a los clientes registrados en el sistema.

### Funcionalidades:

- Validación de correo electrónico
- Validación de nombre
- Asociación de reservas
- Cancelación de reservas
- Encapsulación mediante propiedades (@property)

### Atributos principales:

- id
- nombre
- correo
- reservas

---

## 🔷 Clase abstracta Servicio

Clase base para todos los servicios del sistema.

### Características:

- Precio base
- Disponibilidad
- Métodos abstractos
- Validaciones generales

### Métodos abstractos:

python
calcular_costo()
descripcion()


---

# 🔧 Servicios especializados

El sistema implementa tres tipos de servicios especializados mediante herencia.

---

## 🏢 ReservarSala

Servicio para reservas de salas.

### Características:

- Cálculo de costo por horas
- Validación de disponibilidad
- Aplicación de impuestos y descuentos

---

## 💻 AlquilerEquipos

Servicio de alquiler de equipos tecnológicos.

### Características:

- Cálculo por días
- Descuento automático por alquileres largos
- Validaciones de duración

---

## 🧠 Asesoria

Servicio de asesoría especializada.

### Características:

- Cobro por horas
- Impuestos opcionales
- Descuentos opcionales

---

# 📅 Clase Reserva

Integra:

- Cliente
- Servicio
- Fechas
- Estado
- Procesamiento de reservas

### Estados posibles:

- pendiente
- confirmada
- cancelada

### Funcionalidades:

- Confirmar reservas
- Cancelar reservas
- Procesar reservas
- Calcular duración automáticamente
- Calcular costos usando polimorfismo

---

# ⚠️ Manejo de excepciones

El sistema implementa manejo avanzado de excepciones personalizadas.

## Excepciones implementadas

python
class ErrorSistema(Exception)
class DatosInvalidosError(ErrorSistema)
class ServicioNoDisponibleError(ErrorSistema)
class ReservaInvalidaError(ErrorSistema)
class OperacionNoPermitidaError(ErrorSistema)


---

# 🔄 Patrones de excepciones utilizados

## ✅ try / except

Captura errores específicos.

python
try:
    ...
except ErrorSistema:
    ...


---

## ✅ try / except / else

Ejecuta lógica adicional si no ocurre ningún error.

python
try:
    ...
except:
    ...
else:
    ...


---

## ✅ try / except / finally

Garantiza la ejecución de procesos finales como logs.

python
finally:
    logging.info(...)


---

## ✅ Encadenamiento de excepciones

Permite conservar el error original.

python
raise ErrorSistema(...) from error


---

# 📝 Sistema de logs

Todos los eventos importantes y errores del sistema son registrados automáticamente mediante el módulo logging.

## Archivo generado

bash
sistema_gestion.log


## Información registrada

- Registro de clientes
- Creación de servicios
- Confirmación de reservas
- Cancelaciones
- Errores controlados
- Errores inesperados

---

# 🧪 Simulación automática de operaciones

El sistema incluye una simulación automática de operaciones válidas e inválidas para demostrar:

- Robustez
- Continuidad del sistema
- Manejo profesional de errores

## Operaciones simuladas

| # | Operación | Resultado |
|---|---|---|
| 1 | Registro válido de cliente | ✅ |
| 2 | Cliente con correo inválido | ❌ |
| 3 | Creación válida de sala | ✅ |
| 4 | Servicio con precio negativo | ❌ |
| 5 | Servicio de equipos válido | ✅ |
| 6 | Servicio de asesoría válido | ✅ |
| 7 | Reserva exitosa | ✅ |
| 8 | Reserva con fechas inválidas | ❌ |
| 9 | Cancelación correcta | ✅ |
| 10 | Procesar reserva cancelada | ❌ |
| 11 | Servicio no disponible | ✅ |
| 12 | Procesar servicio no disponible | ❌ |

---

# 🖥️ Menú interactivo

El sistema incorpora un menú interactivo en consola.

## Funcionalidades disponibles

- Registrar clientes
- Registrar servicios
- Crear reservas
- Confirmar reservas
- Cancelar reservas
- Procesar reservas
- Calcular costos
- Consultar servicios
- Ejecutar simulaciones
- Visualizar información del sistema

---

# 📚 Conceptos de Programación Orientada a Objetos aplicados

## 🔷 Abstracción

Uso de clases abstractas:

- Entidad
- Servicio

---

## 🔷 Herencia

Las clases:

- ReservarSala
- AlquilerEquipos
- Asesoria

heredan de Servicio.

---

## 🔷 Polimorfismo

Cada servicio implementa su propia versión de:

python
calcular_costo()


---

## 🔷 Encapsulación

Uso de propiedades (@property) y validaciones internas para proteger atributos.

---

# ▶️ Ejecución del sistema

## Requisitos

- Python 3.10 o superior

---

## Ejecutar el programa

bash
python main.py


---

# 👥 Equipo de trabajo

> Agregar nombres y roles de los integrantes del equipo.

---

# 🎓 Información académica

*Universidad:* UNAD  
*Escuela:* ECBTI  
*Curso:* Programación  
*Actividad:* Sistema Integral de Gestión de Clientes, Servicios y Reservas

---

# 📄 Licencia

Proyecto académico con fines educativos.tengo esta nueva
