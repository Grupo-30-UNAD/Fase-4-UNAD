from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re


# ============================================================
# CONFIGURACIÓN DE LOGS
# ============================================================

logging.basicConfig(
    filename="sistema_gestion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ============================================================
# EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ============================================================

class ErrorSistema(Exception):
    """
    Excepción base para controlar errores propios del sistema.
    """
    pass


class DatosInvalidosError(ErrorSistema):
    """
    Se genera cuando los datos ingresados no cumplen las validaciones.
    """
    pass


class ServicioNoDisponibleError(ErrorSistema):
    """
    Se genera cuando se intenta reservar o procesar un servicio no disponible.
    """
    pass


class ReservaInvalidaError(ErrorSistema):
    """
    Se genera cuando una reserva tiene datos incorrectos.
    """
    pass


class OperacionNoPermitidaError(ErrorSistema):
    """
    Se genera cuando se intenta ejecutar una acción no permitida.
    """
    pass


# ============================================================
# FUNCIONES DE VALIDACIÓN GENERAL
# ============================================================

def validar_id(id_entidad):
    """
    Valida que el identificador sea un número entero positivo.
    """
    if not isinstance(id_entidad, int) or id_entidad <= 0:
        raise DatosInvalidosError("El ID debe ser un número entero positivo.")


def validar_texto(valor, nombre_campo):
    """
    Valida que un texto no esté vacío y tenga una longitud mínima.
    """
    if not isinstance(valor, str) or len(valor.strip()) < 3:
        raise DatosInvalidosError(f"El campo {nombre_campo} debe tener mínimo 3 caracteres.")


def validar_precio(precio):
    """
    Valida que el precio base del servicio sea numérico y mayor que cero.
    """
    if not isinstance(precio, (int, float)) or precio <= 0:
        raise DatosInvalidosError("El precio base debe ser un número mayor que cero.")


def validar_porcentaje(valor, nombre_campo):
    """
    Valida porcentajes usados para impuestos o descuentos.
    """
    if not isinstance(valor, (int, float)):
        raise DatosInvalidosError(f"El campo {nombre_campo} debe ser numérico.")

    if valor < 0 or valor >= 1:
        raise DatosInvalidosError(f"El campo {nombre_campo} debe estar entre 0 y 0.99.")


# ============================================================
# ENTIDAD BASE ABSTRACTA
# ============================================================

class Entidad(ABC):
    """
    Clase abstracta que representa una entidad general del sistema.
    Sirve como base para Cliente y Servicio.
    """

    def __init__(self, id, nombre):
        validar_id(id)
        validar_texto(nombre, "nombre")

        self._id = id
        self._nombre = nombre.strip()

    @property
    def id(self):
        """
        Retorna el identificador de la entidad.
        """
        return self._id

    @property
    def nombre(self):
        """
        Retorna el nombre de la entidad.
        """
        return self._nombre

    @abstractmethod
    def resumen(self):
        """
        Método abstracto que obliga a las clases hijas a mostrar un resumen.
        """
        pass


# ============================================================
# CLASE CLIENTE
# ============================================================

class Cliente(Entidad):
    """
    Representa un cliente del sistema.
    Maneja validaciones, encapsulación y lista interna de reservas.
    """

    def __init__(self, id, nombre, correo):
        super().__init__(id, nombre)
        self._correo = self._validar_correo(correo)
        self.reservas = []

        logging.info(f"Cliente creado correctamente: {self.nombre} - {self.correo}")

    @property
    def correo(self):
        """
        Retorna el correo del cliente de forma controlada.
        """
        return self._correo

    def _validar_correo(self, correo):
        """
        Valida el formato básico del correo electrónico.
        """
        if not isinstance(correo, str):
            raise DatosInvalidosError("El correo debe ser un texto válido.")

        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(patron, correo):
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")

        return correo.strip()

    def realizar_reserva(self, reserva):
        """
        Agrega una reserva a la lista interna del cliente.
        """
        if reserva is None:
            raise ReservaInvalidaError("No se puede agregar una reserva vacía.")

        self.reservas.append(reserva)
        logging.info(f"Reserva #{reserva.id_reserva} asociada al cliente {self.nombre}.")

    def cancelar_reserva(self, reserva):
        """
        Cancela una reserva asociada al cliente.
        """
        if reserva not in self.reservas:
            raise OperacionNoPermitidaError("La reserva no pertenece a este cliente.")

        reserva.cancelar()
        logging.info(f"El cliente {self.nombre} canceló la reserva #{reserva.id_reserva}.")

    def resumen(self):
        """
        Retorna un resumen del cliente.
        """
        return f"Cliente #{self.id} | Nombre: {self.nombre} | Correo: {self.correo}"


# ============================================================
# CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(Entidad, ABC):
    """
    Clase abstracta que representa un servicio general.
    Define estructura común para servicios especializados.
    """

    def __init__(self, id, nombre, precio_base, disponible=True):
        super().__init__(id, nombre)
        validar_precio(precio_base)

        if not isinstance(disponible, bool):
            raise DatosInvalidosError("El estado disponible debe ser verdadero o falso.")

        self.precio_base = precio_base
        self.disponible = disponible

    def validar_disponibilidad(self):
        """
        Verifica si el servicio está disponible.
        """
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio {self.nombre} no está disponible.")

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Método abstracto para calcular costos.
        Los parámetros opcionales simulan sobrecarga de métodos.
        """
        pass

    @abstractmethod
    def descripcion(self):
        """
        Método abstracto para describir cada servicio.
        """
        pass

    def resumen(self):
        """
        Retorna un resumen general del servicio.
        """
        estado = "disponible" if self.disponible else "no disponible"
        return f"Servicio #{self.id} | {self.nombre} | Precio base: ${self.precio_base} | Estado: {estado}"


# ============================================================
# SERVICIO ESPECIALIZADO: RESERVAR SALA
# ============================================================

class ReservarSala(Servicio):
    """
    Servicio de reserva de salas.
    """

    def __init__(self, id, nombre, tipo, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo, "tipo de sala")
        self.tipo = tipo.strip()

        logging.info(f"Servicio de sala creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo de una sala por horas.
        Permite aplicar impuesto o descuento como variante del cálculo.
        """
        self.validar_disponibilidad()

        if duracion <= 0:
            raise ReservaInvalidaError("La duración de la reserva debe ser mayor que cero.")

        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        subtotal = self.precio_base * duracion
        total = subtotal + (subtotal * impuesto)
        total = total - (total * descuento)

        return total

    def descripcion(self):
        """
        Retorna la descripción del servicio de sala.
        """
        return f"Servicio: {self.nombre} | Sala: {self.tipo}"


# ============================================================
# SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ============================================================

class AlquilerEquipos(Servicio):
    """
    Servicio de alquiler de equipos.
    """

    def __init__(self, id, nombre, tipo, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo, "tipo de equipo")
        self.tipo = tipo.strip()

        logging.info(f"Servicio de alquiler creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo del alquiler por días.
        Si la duración supera 5 días, aplica descuento automático del 10%.
        """
        self.validar_disponibilidad()

        if duracion <= 0:
            raise ReservaInvalidaError("La duración del alquiler debe ser mayor que cero.")

        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        dias = duracion / 24

        if dias > 5:
            descuento += 0.10

        if descuento >= 1:
            raise DatosInvalidosError("El descuento total no puede ser igual o superior al 100%.")

        subtotal = self.precio_base * dias
        total = subtotal + (subtotal * impuesto)
        total = total - (total * descuento)

        return total

    def descripcion(self):
        """
        Retorna la descripción del equipo alquilado.
        """
        return f"Servicio: {self.nombre} | Equipo: {self.tipo}"


# ============================================================
# SERVICIO ESPECIALIZADO: ASESORÍA
# ============================================================

class Asesoria(Servicio):
    """
    Servicio de asesoría profesional por horas.
    """

    def __init__(self, id, nombre, tipo, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo, "tipo de asesoría")
        self.tipo = tipo.strip()

        logging.info(f"Servicio de asesoría creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo de asesoría por horas.
        Permite impuesto y descuento como parámetros opcionales.
        """
        self.validar_disponibilidad()

        if duracion <= 0:
            raise ReservaInvalidaError("La duración de la asesoría debe ser mayor que cero.")

        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        subtotal = self.precio_base * duracion
        total = subtotal + (subtotal * impuesto)
        total = total - (total * descuento)

        return total

    def descripcion(self):
        """
        Retorna la descripción de la asesoría.
        """
        return f"Servicio: {self.nombre} | Asesoría: {self.tipo}"


# ============================================================
# CLASE RESERVA
# ============================================================

class Reserva:
    """
    Representa una reserva realizada por un cliente sobre un servicio.
    Maneja duración, estado, confirmación, cancelación y procesamiento.
    """

    def __init__(self, id_reserva, cliente, servicio, fecha_entrada, fecha_salida):
        validar_id(id_reserva)

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva debe estar asociada a un cliente válido.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva debe estar asociada a un servicio válido.")

        if not isinstance(fecha_entrada, datetime) or not isinstance(fecha_salida, datetime):
            raise ReservaInvalidaError("Las fechas de entrada y salida deben ser objetos datetime.")

        if fecha_salida <= fecha_entrada:
            raise ReservaInvalidaError("La fecha de salida debe ser posterior a la fecha de entrada.")

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = "pendiente"
        self.duracion = self.calcular_duracion()

        logging.info(f"Reserva #{self.id_reserva} creada en estado pendiente.")

    def calcular_duracion(self):
        """
        Calcula la duración de la reserva en horas.
        """
        diferencia = self.fecha_salida - self.fecha_entrada
        duracion = diferencia.total_seconds() / 3600

        if duracion <= 0:
            raise ReservaInvalidaError("La duración calculada no es válida.")

        return duracion

    def confirmar(self):
        """
        Confirma una reserva pendiente.
        """
        if self.estado != "pendiente":
            raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")

        self.servicio.validar_disponibilidad()
        self.estado = "confirmada"

        logging.info(f"Reserva #{self.id_reserva} confirmada correctamente.")

    def cancelar(self):
        """
        Cancela una reserva si no ha sido cancelada previamente.
        """
        if self.estado == "cancelada":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")

        self.estado = "cancelada"

        logging.info(f"Reserva #{self.id_reserva} cancelada correctamente.")

    def calcular_costo(self, impuesto=0, descuento=0):
        """
        Calcula el costo total de la reserva.
        Usa polimorfismo porque cada servicio calcula el costo de forma diferente.
        """
        return self.servicio.calcular_costo(
            self.duracion,
            impuesto=impuesto,
            descuento=descuento
        )

    def procesar(self, impuesto=0, descuento=0):
        """
        Procesa la reserva usando try/except/else/finally.
        Registra eventos y errores en el archivo de logs.
        """
        try:
            if self.estado == "cancelada":
                raise OperacionNoPermitidaError("No se puede procesar una reserva cancelada.")

            if self.estado != "pendiente":
                raise OperacionNoPermitidaError("Solo se pueden procesar reservas pendientes.")

            costo = self.calcular_costo(impuesto=impuesto, descuento=descuento)

        except ErrorSistema as error:
            logging.exception(f"Error controlado al procesar la reserva #{self.id_reserva}: {error}")
            raise

        except Exception as error:
            logging.exception(f"Error inesperado al procesar la reserva #{self.id_reserva}: {error}")
            raise ErrorSistema("Ocurrió un error inesperado durante el procesamiento.") from error

        else:
            self.confirmar()
            logging.info(f"Reserva #{self.id_reserva} procesada exitosamente.")
            return costo

        finally:
            logging.info(f"Finalizó el intento de procesamiento de la reserva #{self.id_reserva}.")

    def __str__(self):
        """
        Retorna una representación textual de la reserva.
        """
        return (
            f"Reserva #{self.id_reserva} | "
            f"Cliente: {self.cliente.nombre} | "
            f"{self.servicio.descripcion()} | "
            f"Estado: {self.estado} | "
            f"Duración: {self.duracion:.2f} horas"
        )


# ============================================================
# SISTEMA INTEGRAL DE GESTIÓN
# ============================================================

class SistemaGestion:
    """
    Clase principal que administra clientes, servicios y reservas mediante listas internas.
    No utiliza bases de datos.
    """

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

        logging.info("Sistema Integral de Gestión iniciado correctamente.")

    def registrar_cliente(self, id, nombre, correo):
        """
        Registra un cliente y lo almacena en la lista interna.
        """
        cliente = Cliente(id, nombre, correo)
        self.clientes.append(cliente)

        logging.info(f"Cliente registrado en el sistema: {cliente.nombre}")
        return cliente

    def registrar_servicio(self, servicio):
        """
        Registra un servicio en la lista interna del sistema.
        """
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Solo se pueden registrar objetos de tipo Servicio.")

        self.servicios.append(servicio)

        logging.info(f"Servicio registrado en el sistema: {servicio.nombre}")
        return servicio

    def crear_reserva(self, id_reserva, cliente, servicio, fecha_entrada, fecha_salida):
        """
        Crea una reserva, la guarda en la lista interna y la asocia al cliente.
        """
        reserva = Reserva(id_reserva, cliente, servicio, fecha_entrada, fecha_salida)
        self.reservas.append(reserva)
        cliente.realizar_reserva(reserva)

        logging.info(f"Reserva #{reserva.id_reserva} registrada en el sistema.")
        return reserva

    def listar_reservas(self):
        """
        Muestra todas las reservas registradas en el sistema.
        """
        if not self.reservas:
            return "No hay reservas registradas."

        resultado = "\n".join(str(reserva) for reserva in self.reservas)
        return resultado


# ============================================================
# FUNCIÓN PARA EJECUTAR OPERACIONES CONTROLADAS
# ============================================================

def ejecutar_operacion(numero, descripcion, accion):
    """
    Ejecuta una operación del sistema y mantiene activa la aplicación aunque ocurran errores.
    """
    print(f"\nOperación {numero}: {descripcion}")

    try:
        resultado = accion()

    except ErrorSistema as error:
        print(f"Error controlado: {error}")
        logging.exception(f"Operación {numero} fallida de forma controlada: {error}")

    except Exception as error:
        print(f"Error inesperado: {error}")
        logging.exception(f"Operación {numero} generó un error inesperado: {error}")

    else:
        if resultado is not None:
            print(resultado)

        logging.info(f"Operación {numero} ejecutada correctamente.")

    finally:
        print("-" * 70)
        logging.info(f"Finalizó la operación {numero}: {descripcion}")


# ============================================================
# SIMULACIÓN DE OPERACIONES DEL SISTEMA
# ============================================================

def ejecutar_simulacion():
    """
    Simula operaciones válidas e inválidas para demostrar robustez,
    manejo de excepciones, logs y continuidad del sistema.
    """

    sistema = SistemaGestion()

    cliente1 = None
    sala1 = None
    equipo1 = None
    asesoria1 = None
    servicio_inactivo = None
    reserva1 = None
    reserva2 = None
    reserva3 = None

    def op1():
        nonlocal cliente1
        cliente1 = sistema.registrar_cliente(1, "Damian", "correo@gmail.com")
        return cliente1.resumen()

    def op2():
        sistema.registrar_cliente(2, "Lu", "correo_invalido")
        return "Cliente inválido registrado."

    def op3():
        nonlocal sala1
        sala1 = ReservarSala(101, "Reserva de Sala", "Sala de reuniones", 50000)
        sistema.registrar_servicio(sala1)
        return sala1.resumen()

    def op4():
        servicio_errado = ReservarSala(102, "Sala Errada", "Sala VIP", -30000)
        sistema.registrar_servicio(servicio_errado)
        return servicio_errado.resumen()

    def op5():
        nonlocal equipo1
        equipo1 = AlquilerEquipos(103, "Alquiler Equipos", "Computador", 1000)
        sistema.registrar_servicio(equipo1)
        return equipo1.resumen()

    def op6():
        nonlocal asesoria1
        asesoria1 = Asesoria(104, "Asesoría Especializada", "Consultoría Python", 80000)
        sistema.registrar_servicio(asesoria1)
        return asesoria1.resumen()

    def op7():
        nonlocal reserva1
        entrada = datetime.strptime("2026-05-04 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-04 12:00", "%Y-%m-%d %H:%M")

        reserva1 = sistema.crear_reserva(1, cliente1, sala1, entrada, salida)
        costo = reserva1.procesar(impuesto=0.19, descuento=0.05)

        return f"{reserva1}\nCosto final con impuesto y descuento: ${costo:.2f}"

    def op8():
        entrada = datetime.strptime("2026-05-05 14:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-05 10:00", "%Y-%m-%d %H:%M")

        reserva_errada = sistema.crear_reserva(2, cliente1, equipo1, entrada, salida)
        return reserva_errada

    def op9():
        nonlocal reserva2
        entrada = datetime.strptime("2026-05-06 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-08 08:00", "%Y-%m-%d %H:%M")

        reserva2 = sistema.crear_reserva(3, cliente1, equipo1, entrada, salida)
        reserva2.cancelar()

        return f"{reserva2}\nReserva cancelada correctamente."

    def op10():
        costo = reserva2.procesar()
        return f"Reserva procesada con costo: ${costo:.2f}"

    def op11():
        nonlocal servicio_inactivo
        servicio_inactivo = Asesoria(
            105,
            "Asesoría No Disponible",
            "Soporte avanzado",
            120000,
            disponible=False
        )
        sistema.registrar_servicio(servicio_inactivo)
        return servicio_inactivo.resumen()

    def op12():
        nonlocal reserva3
        entrada = datetime.strptime("2026-05-09 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-09 11:00", "%Y-%m-%d %H:%M")

        reserva3 = sistema.crear_reserva(4, cliente1, servicio_inactivo, entrada, salida)
        costo = reserva3.procesar()

        return f"Reserva procesada con costo: ${costo:.2f}"

    ejecutar_operacion(1, "Registro válido de cliente", op1)
    ejecutar_operacion(2, "Registro inválido de cliente por nombre y correo incorrectos", op2)
    ejecutar_operacion(3, "Creación correcta de servicio de reserva de sala", op3)
    ejecutar_operacion(4, "Creación incorrecta de servicio con precio negativo", op4)
    ejecutar_operacion(5, "Creación correcta de servicio de alquiler de equipos", op5)
    ejecutar_operacion(6, "Creación correcta de servicio de asesoría", op6)
    ejecutar_operacion(7, "Reserva exitosa con impuesto y descuento", op7)
    ejecutar_operacion(8, "Reserva fallida por fechas incorrectas", op8)
    ejecutar_operacion(9, "Cancelación correcta de una reserva", op9)
    ejecutar_operacion(10, "Intento fallido de procesar una reserva cancelada", op10)
    ejecutar_operacion(11, "Creación de servicio no disponible", op11)
    ejecutar_operacion(12, "Intento fallido de procesar servicio no disponible", op12)

    print("\nRESERVAS REGISTRADAS EN EL SISTEMA")
    print("=" * 70)
    print(sistema.listar_reservas())

    logging.info("Simulación completa finalizada.")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    ejecutar_simulacion()