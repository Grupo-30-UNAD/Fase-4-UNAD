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
    encoding="utf-8",
)


# ============================================================
# EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ============================================================


class ErrorSistema(Exception):
    """Excepción base para controlar errores propios del sistema."""

    pass


class DatosInvalidosError(ErrorSistema):
    """Se genera cuando los datos ingresados no cumplen las validaciones."""

    pass


class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando se intenta reservar o procesar un servicio no disponible."""

    pass


class ReservaInvalidaError(ErrorSistema):
    """Se genera cuando una reserva tiene datos incorrectos."""

    pass


class OperacionNoPermitidaError(ErrorSistema):
    """Se genera cuando se intenta ejecutar una acción no permitida."""

    pass


# ============================================================
# FUNCIONES DE VALIDACIÓN GENERAL
# ============================================================


def validar_id(id_entidad):
    """Valida que el identificador sea un número entero positivo."""
    if not isinstance(id_entidad, int) or id_entidad <= 0:
        raise DatosInvalidosError("El ID debe ser un número entero positivo.")


def validar_texto(valor, nombre_campo):
    """Valida que un texto no esté vacío y tenga una longitud mínima."""
    if not isinstance(valor, str) or len(valor.strip()) < 3:
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe tener mínimo 3 caracteres."
        )


def validar_precio(precio):
    """Valida que el precio base del servicio sea numérico y mayor que cero."""
    if not isinstance(precio, (int, float)) or precio <= 0:
        raise DatosInvalidosError("El precio base debe ser un número mayor que cero.")


def validar_porcentaje(valor, nombre_campo):
    """Valida porcentajes usados para impuestos o descuentos."""
    if not isinstance(valor, (int, float)):
        raise DatosInvalidosError(f"El campo '{nombre_campo}' debe ser numérico.")
    if valor < 0 or valor >= 1:
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe estar entre 0 y 0.99."
        )


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
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @abstractmethod
    def resumen(self):
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
        logging.info(f"Cliente creado correctamente: {self.nombre} - {self._correo}")

    @property
    def correo(self):
        return self._correo

    def _validar_correo(self, correo):
        """Valida el formato básico del correo electrónico."""
        if not isinstance(correo, str):
            raise DatosInvalidosError("El correo debe ser un texto válido.")
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, correo):
            raise DatosInvalidosError(
                "El correo electrónico no tiene un formato válido."
            )
        return correo.strip()

    def realizar_reserva(self, reserva):
        if reserva is None:
            raise ReservaInvalidaError("No se puede agregar una reserva vacía.")
        self.reservas.append(reserva)
        logging.info(
            f"Reserva #{reserva.id_reserva} asociada al cliente {self.nombre}."
        )

    def cancelar_reserva(self, reserva):
        if reserva not in self.reservas:
            raise OperacionNoPermitidaError("La reserva no pertenece a este cliente.")
        reserva.cancelar()
        logging.info(
            f"El cliente {self.nombre} canceló la reserva #{reserva.id_reserva}."
        )

    def resumen(self):
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
            raise DatosInvalidosError(
                "El estado 'disponible' debe ser verdadero o falso."
            )
        self.precio_base = precio_base
        self.disponible = disponible

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Método abstracto para calcular costos.
        Los parámetros opcionales simulan sobrecarga de métodos.
        """
        pass

    @abstractmethod
    def descripcion(self):
        pass

    def resumen(self):
        estado = "disponible" if self.disponible else "no disponible"
        return (
            f"Servicio #{self.id} | {self.nombre} | "
            f"Precio base: ${self.precio_base:,.0f} | Estado: {estado}"
        )


# ============================================================
# SERVICIO ESPECIALIZADO: RESERVAR SALA
# ============================================================


class ReservarSala(Servicio):
    """Servicio de reserva de salas."""

    def __init__(self, id, nombre, tipo_sala, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo_sala, "tipo de sala")
        self.tipo = tipo_sala.strip()
        logging.info(f"Servicio de sala creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo de una sala por horas.
        Permite aplicar impuesto o descuento como variante del cálculo.
        """
        self.validar_disponibilidad()
        if duracion <= 0:
            raise ReservaInvalidaError(
                "La duración de la reserva debe ser mayor que cero."
            )
        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        subtotal = self.precio_base * duracion
        total = subtotal * (1 + impuesto) * (1 - descuento)
        return total

    def descripcion(self):
        return f"Servicio: {self.nombre} | Sala: {self.tipo}"


# ============================================================
# SERVICIO ESPECIALIZADO: ALQUILER DE EQUIPOS
# ============================================================


class AlquilerEquipos(Servicio):
    """Servicio de alquiler de equipos."""

    def __init__(self, id, nombre, tipo_equipo, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo_equipo, "tipo de equipo")
        self.tipo = tipo_equipo.strip()
        logging.info(f"Servicio de alquiler creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo del alquiler por días (duracion en horas).
        Si la duración supera 5 días, aplica descuento automático del 10%.
        """

        self.validar_disponibilidad()
        if duracion <= 0:
            raise ReservaInvalidaError(
                "La duración del alquiler debe ser mayor que cero."
            )
        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        dias = duracion / 24
        if dias > 5:
            descuento_final = descuento + 0.10
        else:
            descuento_final = descuento + 0

        if descuento_final >= 1:
            raise ReservaInvalidaError(
                "El descuento total (incluyendo el bono por días) no puede ser >= 100%."
            )

        subtotal = self.precio_base * dias
        total = subtotal * (1 + impuesto) * (1 - descuento_final)
        return total

    def descripcion(self):
        return f"Servicio: {self.nombre} | Equipo: {self.tipo}"


# ============================================================
# SERVICIO ESPECIALIZADO: ASESORÍA
# ============================================================


class Asesoria(Servicio):
    """Servicio de asesoría profesional por horas."""

    def __init__(self, id, nombre, tipo_asesoria, precio_base, disponible=True):
        super().__init__(id, nombre, precio_base, disponible)
        validar_texto(tipo_asesoria, "tipo de asesoría")
        self.tipo = tipo_asesoria.strip()
        logging.info(f"Servicio de asesoría creado: {self.nombre} - {self.tipo}")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """
        Calcula el costo de asesoría por horas.
        Permite impuesto y descuento como parámetros opcionales.
        """
        self.validar_disponibilidad()
        if duracion <= 0:
            raise ReservaInvalidaError(
                "La duración de la asesoría debe ser mayor que cero."
            )
        validar_porcentaje(impuesto, "impuesto")
        validar_porcentaje(descuento, "descuento")

        subtotal = self.precio_base * duracion
        total = subtotal * (1 + impuesto) * (1 - descuento)
        return total

    def descripcion(self):
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
            raise ReservaInvalidaError(
                "La reserva debe estar asociada a un cliente válido."
            )
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                "La reserva debe estar asociada a un servicio válido."
            )
        if not isinstance(fecha_entrada, datetime) or not isinstance(
            fecha_salida, datetime
        ):
            raise ReservaInvalidaError(
                "Las fechas de entrada y salida deben ser objetos datetime."
            )
        if fecha_salida <= fecha_entrada:
            raise ReservaInvalidaError(
                "La fecha de salida debe ser posterior a la fecha de entrada."
            )

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = "pendiente"
        self.duracion = self._calcular_duracion()

        logging.info(f"Reserva #{self.id_reserva} creada en estado pendiente.")

    def _calcular_duracion(self):
        """Calcula la duración de la reserva en horas."""
        diferencia = self.fecha_salida - self.fecha_entrada
        duracion = diferencia.total_seconds() / 3600
        if duracion <= 0:
            raise ReservaInvalidaError("La duración calculada no es válida.")
        return duracion

    def confirmar(self):
        if self.estado != "pendiente":
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )
        self.servicio.validar_disponibilidad()
        self.estado = "confirmada"
        self.servicio.disponible = False
        logging.info(f"Reserva #{self.id_reserva} confirmada correctamente.")

    def cancelar(self):
        if self.estado == "cancelada":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
        self.estado = "cancelada"
        self.servicio.disponible = True
        logging.info(f"Reserva #{self.id_reserva} cancelada correctamente.")

    def calcular_costo(self, impuesto=0, descuento=0):
        """
        Calcula el costo total de la reserva.
        Usa polimorfismo: cada servicio implementa su propio cálculo.
        """
        return self.servicio.calcular_costo(
            self.duracion, impuesto=impuesto, descuento=descuento
        )

    def procesar(self, impuesto=0, descuento=0):
        """
        Procesa la reserva usando try/except/else/finally.
        Registra eventos y errores en el archivo de logs.
        """
        try:
            if self.estado == "cancelada":
                raise OperacionNoPermitidaError(
                    "No se puede procesar una reserva cancelada."
                )
            if self.estado != "pendiente":
                raise OperacionNoPermitidaError(
                    "Solo se pueden procesar reservas pendientes."
                )
            costo = self.calcular_costo(impuesto=impuesto, descuento=descuento)

        except ErrorSistema as error:
            logging.exception(
                f"Error controlado al procesar la reserva #{self.id_reserva}: {error}"
            )
            raise

        except Exception as error:
            logging.exception(
                f"Error inesperado al procesar la reserva #{self.id_reserva}: {error}"
            )

            raise ErrorSistema(
                "Ocurrió un error inesperado durante el procesamiento."
            ) from error

        else:
            self.confirmar()
            logging.info(f"Reserva #{self.id_reserva} procesada exitosamente.")
            return costo

        finally:
            logging.info(
                f"Finalizó el intento de procesamiento de la reserva #{self.id_reserva}."
            )

    def __str__(self):
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
        """Registra un cliente y lo almacena en la lista interna."""
        try:
            cliente = Cliente(id, nombre, correo)
        except DatosInvalidosError as e:
            logging.error(f"Fallo al registrar cliente id={id}: {e}")
            raise DatosInvalidosError(
                f"No se pudo registrar el cliente '{nombre}': {e}"
            ) from e

        self.clientes.append(cliente)
        logging.info(f"Cliente registrado en el sistema: {cliente.nombre}")
        return cliente

    def registrar_servicio(
        self, id, nombre=None, tipo=None, precio_base=None, disponible=True
    ):
        """
        Registra un servicio en la lista interna del sistema.
        """
        try:
            if isinstance(id, Servicio):
                servicio = id
            else:
                if nombre is None or tipo is None or precio_base is None:
                    raise DatosInvalidosError(
                        "Para registrar un servicio con parámetros debes indicar "
                        "id, nombre, tipo y precio_base."
                    )

                tipo = tipo.strip().lower()

                if tipo == "sala":
                    servicio = ReservarSala(
                        id, nombre, "Sala de reuniones", precio_base, disponible
                    )
                elif tipo == "equipo":
                    servicio = AlquilerEquipos(
                        id, nombre, "Equipo general", precio_base, disponible
                    )
                elif tipo == "asesoria":
                    servicio = Asesoria(
                        id, nombre, "Consultoría general", precio_base, disponible
                    )
                else:
                    raise DatosInvalidosError(
                        f"Tipo de servicio '{tipo}' no reconocido. "
                        "Use: 'sala', 'equipo' o 'asesoria'."
                    )

        except DatosInvalidosError as e:
            logging.error(f"Fallo al registrar servicio: {e}")
            raise DatosInvalidosError(f"No se pudo registrar el servicio: {e}") from e

        self.servicios.append(servicio)
        logging.info(f"Servicio registrado en el sistema: {servicio.nombre}")
        return servicio

    def buscar_cliente(self, id):
        """
        Busca al cliente usando su ID, retorna al objeto cliente si existe.
        Si no se encuentra retorna None.
        """
        for cliente in self.clientes:
            if cliente.id == id:
                return cliente
        return None

    def buscar_servicio(self, id):
        """
        Busca un servicio mediante su ID si, si existe retorna al objeto servicio.
        Si no se encuentra retorna None
        """
        for servicio in self.servicios:
            if servicio.id == id:
                return servicio
        return None

    def crear_reserva(self, id_reserva, cliente, servicio, fecha_entrada, fecha_salida):
        """Crea una reserva, la guarda en la lista interna y la asocia al cliente."""
        try:
            reserva = Reserva(
                id_reserva, cliente, servicio, fecha_entrada, fecha_salida
            )
        except ReservaInvalidaError as e:
            logging.error(f"Fallo al crear reserva #{id_reserva}: {e}")
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva #{id_reserva}: {e}"
            ) from e

        self.reservas.append(reserva)
        cliente.realizar_reserva(reserva)
        logging.info(f"Reserva #{reserva.id_reserva} registrada en el sistema.")
        return reserva

    def listar_clientes(self):
        """
        Retorna un listado los clientes registrados en el sistema.
        Si no existen clientes retorna un aviso.
        """
        if not self.clientes:
            return "No hay clientes registrados."
        return "\n".join(cliente.resumen() for cliente in self.clientes)

    def listar_servicios(self):
        """
        Retorna un listado de los servicios registrados en el sistema.
        Si no existen servicios retorna un aviso.
        """
        if not self.servicios:
            return "No hay servicios registrados."
        return "\n".join(servicio.resumen() for servicio in self.servicios)

    def listar_reservas(self):
        """Muestra todas las reservas registradas en el sistema."""
        if not self.reservas:
            return "No hay reservas registradas."
        return "\n".join(str(reserva) for reserva in self.reservas)

    def buscar_reserva(self, id_reserva):
        """
        Busca una reserva dentro del sistema usando su ID, retorna el objeto reserva si existe
        Si no se encuentra, retorna None.
        """
        for reserva in self.reservas:
            if reserva.id_reserva == id_reserva:
                logging.info(f"Reserva #{id_reserva} encontrada.")
                return reserva
        return None


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
        print(f"  Error controlado: {error}")
        logging.exception(f"Operación {numero} fallida de forma controlada: {error}")
    except Exception as error:
        print(f"  Error inesperado: {error}")
        logging.exception(f"Operación {numero} generó un error inesperado: {error}")
    else:
        if resultado is not None:
            print(f"{resultado}")
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

    # ----------------------------------------------------------------
    # OP 1 — Cliente válido
    # ----------------------------------------------------------------
    def op1():
        nonlocal cliente1
        cliente1 = sistema.registrar_cliente(1, "Damian", "damian@gmail.com")
        return cliente1.resumen()

    # ----------------------------------------------------------------
    # OP 2 — Cliente inválido: correo mal formado
    # ----------------------------------------------------------------
    def op2():
        sistema.registrar_cliente(2, "Luis", "correo_invalido")
        return "Cliente inválido registrado."

    # ----------------------------------------------------------------
    # OP 3 — Servicio de sala válido
    # ----------------------------------------------------------------
    def op3():
        nonlocal sala1
        sala1 = ReservarSala(101, "Sala Ejecutiva", "Sala de reuniones", 50000)
        sistema.registrar_servicio(sala1)
        return sala1.resumen()

    # ----------------------------------------------------------------
    # OP 4 — Servicio con precio negativo
    # ----------------------------------------------------------------
    def op4():
        servicio_errado = ReservarSala(102, "Sala Errada", "Sala VIP", -30000)
        sistema.registrar_servicio(servicio_errado)
        return servicio_errado.resumen()

    # ----------------------------------------------------------------
    # OP 5 — Servicio de equipo válido
    # ----------------------------------------------------------------
    def op5():
        nonlocal equipo1
        equipo1 = AlquilerEquipos(103, "Alquiler Portátil", "Computador portátil", 1000)
        sistema.registrar_servicio(equipo1)
        return equipo1.resumen()

    # ----------------------------------------------------------------
    # OP 6 — Servicio de asesoría válido
    # ----------------------------------------------------------------
    def op6():
        nonlocal asesoria1
        asesoria1 = sistema.registrar_servicio(
            104, "Asesoría Python", "asesoria", 80000
        )
        return asesoria1.resumen()

    # ----------------------------------------------------------------
    # OP 7 — Reserva exitosa con impuesto y descuento
    # ----------------------------------------------------------------
    def op7():
        nonlocal reserva1
        entrada = datetime.strptime("2026-05-04 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-04 12:00", "%Y-%m-%d %H:%M")
        reserva1 = sistema.crear_reserva(1, cliente1, sala1, entrada, salida)
        costo = reserva1.procesar(impuesto=0.19, descuento=0.05)
        return f"{reserva1}\n  Costo final (IVA 19%, descuento 5%): ${costo:,.2f}"

    # ----------------------------------------------------------------
    # OP 8 — Reserva fallida por fechas invertidas
    # ----------------------------------------------------------------
    def op8():
        entrada = datetime.strptime("2026-05-05 14:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-05 10:00", "%Y-%m-%d %H:%M")
        sistema.crear_reserva(2, cliente1, equipo1, entrada, salida)

    # ----------------------------------------------------------------
    # OP 9 — Cancelación correcta de una reserva
    # ----------------------------------------------------------------
    def op9():
        nonlocal reserva2
        entrada = datetime.strptime("2026-05-06 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-08 08:00", "%Y-%m-%d %H:%M")
        reserva2 = sistema.crear_reserva(3, cliente1, equipo1, entrada, salida)
        reserva2.cancelar()
        return f"{reserva2}\n  Reserva cancelada correctamente."

    # ----------------------------------------------------------------
    # OP 10 — Intento fallido de procesar una reserva cancelada
    # ----------------------------------------------------------------
    def op10():
        costo = reserva2.procesar()
        return f"Reserva procesada con costo: ${costo:.2f}"

    # ----------------------------------------------------------------
    # OP 11 — Creación de servicio no disponible
    # ----------------------------------------------------------------
    def op11():
        nonlocal servicio_inactivo
        servicio_inactivo = Asesoria(
            105, "Asesoría No Disponible", "Soporte avanzado", 120000, disponible=False
        )
        sistema.registrar_servicio(servicio_inactivo)
        return servicio_inactivo.resumen()

    # ----------------------------------------------------------------
    # OP 12 — Intento fallido de procesar servicio no disponible
    # ----------------------------------------------------------------
    def op12():
        entrada = datetime.strptime("2026-05-09 08:00", "%Y-%m-%d %H:%M")
        salida = datetime.strptime("2026-05-09 11:00", "%Y-%m-%d %H:%M")
        reserva3 = sistema.crear_reserva(
            4, cliente1, servicio_inactivo, entrada, salida
        )
        costo = reserva3.procesar()
        return f"Reserva procesada con costo: ${costo:.2f}"

    ejecutar_operacion(1, "Registro válido de cliente", op1)
    ejecutar_operacion(2, "Registro inválido de cliente (correo mal formado)", op2)
    ejecutar_operacion(3, "Creación correcta de servicio de sala (obj directo)", op3)
    ejecutar_operacion(4, "Creación incorrecta de servicio con precio negativo", op4)
    ejecutar_operacion(5, "Creación correcta de servicio de equipo", op5)
    ejecutar_operacion(6, "Creación correcta de servicio de asesoría (params)", op6)
    ejecutar_operacion(7, "Reserva exitosa con impuesto y descuento", op7)
    ejecutar_operacion(8, "Reserva fallida por fechas incorrectas", op8)
    ejecutar_operacion(9, "Cancelación correcta de una reserva", op9)
    ejecutar_operacion(10, "Intento fallido de procesar una reserva cancelada", op10)
    ejecutar_operacion(11, "Creación de servicio no disponible", op11)
    ejecutar_operacion(12, "Intento fallido de procesar servicio no disponible", op12)

    print("\n" + "=" * 70)
    print("RESERVAS REGISTRADAS EN EL SISTEMA")
    print("=" * 70)
    print(sistema.listar_reservas())

    logging.info("Simulación completa finalizada.")


# ============================================================
# MENÚ INTERACTIVO
# ============================================================


def menu():
    """
    Ejecuta el menú interactivo principal del sistema.
    Permite registrar clientes y servicios, crear y procesar
    reservas, consultar información almacenada y ejecutar
    simulaciones de prueba desde consola.
    """
    sistema = SistemaGestion()
    salir = False

    while not salir:
        print("\n========== SISTEMA SOFTWARE FJ ==========")
        print("1.  Registrar cliente")
        print("2.  Registrar servicio")
        print("3.  Listar clientes")
        print("4.  Listar servicios")
        print("5.  Listar reservas")
        print("6.  Crear reserva")
        print("7.  Confirmar reserva")
        print("8.  Cancelar reserva")
        print("9.  Procesar reserva")
        print("10. Calcular costo reserva")
        print("11. Resumen del sistema")
        print("12. Ejecutar simulación")
        print("13. cosultar estado de un servicio")
        print("0.  Salir")

        opcion = input("Elige una opción: ").strip()

        try:
            # =========================
            # REGISTRAR CLIENTE
            # =========================
            if opcion == "1":
                try:
                    id_cli = int(input("ID cliente: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                nombre = input("Nombre: ")
                correo = input("Correo: ")
                cliente = sistema.registrar_cliente(id_cli, nombre, correo)
                print(f"Cliente registrado: {cliente.resumen()}")

            # =========================
            # REGISTRAR SERVICIO
            # =========================
            elif opcion == "2":
                tipo = input("Tipo (sala/equipo/asesoria): ").strip().lower()
                try:
                    id_srv = int(input("ID servicio: "))
                    precio_base = float(input("Precio base: "))
                except ValueError:
                    print("ID y precio deben ser numéricos.")
                    continue
                nombre = input("Nombre del servicio: ")
                nombre_tipo = input(
                    "Nombre descriptivo del tipo (ej: 'Sala de juntas'): "
                )

                # Creamos el objeto directamente para poder pasar el nombre_tipo
                if tipo == "sala":
                    srv = ReservarSala(id_srv, nombre, nombre_tipo, precio_base)
                elif tipo == "equipo":
                    srv = AlquilerEquipos(id_srv, nombre, nombre_tipo, precio_base)
                elif tipo == "asesoria":
                    srv = Asesoria(id_srv, nombre, nombre_tipo, precio_base)
                else:
                    print("Tipo no reconocido. Use: sala, equipo o asesoria.")
                    continue

                sistema.registrar_servicio(srv)
                print(f"Servicio registrado: {srv.resumen()}")

            # =========================
            # LISTADOS
            # =========================
            elif opcion == "3":
                print(sistema.listar_clientes())

            elif opcion == "4":
                print(sistema.listar_servicios())

            elif opcion == "5":
                print(sistema.listar_reservas())

            # =========================
            # CREAR RESERVA
            # =========================
            elif opcion == "6":
                try:
                    id_reserva = int(input("ID reserva: "))
                    id_cliente = int(input("ID cliente: "))
                    id_servicio = int(input("ID servicio: "))
                except ValueError:
                    print("Los IDs deben ser números enteros.")
                    continue

                cliente = sistema.buscar_cliente(id_cliente)
                servicio = sistema.buscar_servicio(id_servicio)

                if cliente is None:
                    print("Cliente no encontrado.")
                    continue
                if servicio is None:
                    print("Servicio no encontrado.")
                    continue

                try:
                    entrada = datetime.strptime(
                        input("Fecha entrada (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M"
                    )
                    salida = datetime.strptime(
                        input("Fecha salida  (YYYY-MM-DD HH:MM): "), "%Y-%m-%d %H:%M"
                    )
                except ValueError:
                    print("Formato de fecha incorrecto. Use YYYY-MM-DD HH:MM")
                    continue

                reserva = sistema.crear_reserva(
                    id_reserva, cliente, servicio, entrada, salida
                )
                print(f"Reserva creada: {reserva}")

            # =========================
            # CONFIRMAR
            # =========================
            elif opcion == "7":
                try:
                    id_reserva = int(input("ID reserva: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                reserva = sistema.buscar_reserva(id_reserva)
                if reserva:
                    reserva.confirmar()
                    print("Reserva confirmada.")
                else:
                    print("Reserva no encontrada.")

            # =========================
            # CANCELAR
            # =========================
            elif opcion == "8":
                try:
                    id_reserva = int(input("ID reserva: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                reserva = sistema.buscar_reserva(id_reserva)
                if reserva:
                    reserva.cancelar()
                    print("Reserva cancelada.")
                else:
                    print("Reserva no encontrada.")

            # =========================
            # PROCESAR
            # =========================
            elif opcion == "9":
                try:
                    id_res = int(input("ID reserva: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                reserva = sistema.buscar_reserva(id_res)
                if reserva:
                    costo = reserva.procesar()
                    print(f"Reserva procesada. Costo: ${costo:,.2f}")
                else:
                    print("Reserva no encontrada.")

            # =========================
            # COSTO
            # =========================
            elif opcion == "10":
                try:
                    id_reserva = int(input("ID reserva: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                reserva = sistema.buscar_reserva(id_reserva)
                if reserva:
                    print(
                        f"Costo base (sin impuesto ni descuento): ${reserva.calcular_costo():,.2f}"
                    )
                else:
                    print("Reserva no encontrada.")

            # =========================
            # RESUMEN
            # =========================
            elif opcion == "11":
                print("\n--- Clientes ---")
                print(sistema.listar_clientes())
                print("\n--- Servicios ---")
                print(sistema.listar_servicios())
                print("\n--- Reservas ---")
                print(sistema.listar_reservas())

            # =========================
            # SIMULACIÓN
            # =========================
            elif opcion == "12":
                ejecutar_simulacion()

            elif opcion == "13":
                try:
                    id_srv = int(input("ID servicio: "))
                except ValueError:
                    print("El ID debe ser un número entero.")
                    continue
                servicio = sistema.buscar_servicio(id_srv)
                if servicio:
                    if servicio.disponible:
                        estado = "disponible"
                    else:
                        estado = "ocupado"
                    print(f"Servicio '{servicio.nombre}' está actualmente: {estado}")
                else:
                    print("Servicio no encontrado.")

            # =========================
            # SALIR
            # =========================
            elif opcion == "0":
                salir = True
                print("Saliendo del sistema. ¡Hasta pronto!")

            else:
                print("Opción inválida. Elige un número del 0 al 12.")

        except ErrorSistema as e:
            print(f"Error del sistema: {e}")
            logging.error(f"Error capturado en el menú: {e}")

        except Exception as e:
            print(f"Error inesperado: {e}")
            logging.exception(f"Error inesperado en el menú: {e}")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    menu()
