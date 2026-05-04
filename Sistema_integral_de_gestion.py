from abc import ABC, abstractmethod
from datetime import datetime


# =========================
# ENTIDAD BASE
# =========================
class Entidad(ABC):
    """
    Clase base abstracta que representa una entidad general del sistema.
    Sirve como punto de herencia para otras clases como Cliente y Servicio.
    """

    def __init__(self, id, nombre):
        self._id = id
        self._nombre = nombre

    @property
    def nombre(self):
        """
        Permite acceder al nombre de la entidad de forma controlada (encapsulación).
        """
        return self._nombre


# =========================
# CLIENTE
# =========================
class Cliente(Entidad):
    """
    Representa un cliente del sistema que puede realizar y cancelar reservas.
    Hereda de Entidad.
    """

    def __init__(self, id, nombre, correo):
        super().__init__(id, nombre)
        self.correo = correo
        self.reservas = []  # Lista de reservas asociadas al cliente

    def realizar_reserva(self, reserva):
        """
        Agrega una reserva a la lista de reservas del cliente.
        """
        self.reservas.append(reserva)

    def cancelar_reserva(self, reserva):
        """
        Elimina una reserva si existe en la lista del cliente.
        """
        if reserva in self.reservas:
            self.reservas.remove(reserva)


# =========================
# SERVICIO ABSTRACTO
# =========================
class Servicio(Entidad, ABC):
    """
    Clase abstracta que define la estructura base de los servicios.
    Obliga a que las clases hijas implementen el cálculo de costo y descripción.
    """

    def __init__(self, id, nombre, precio_base):
        super().__init__(id, nombre)
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, duracion):
        """
        Método abstracto que debe calcular el costo del servicio según duración.
        """
        pass

    @abstractmethod
    def descripcion(self):
        """
        Método abstracto que devuelve una descripción del servicio.
        """
        pass


# =========================
# SERVICIO: RESERVAR SALA
# =========================
class ReservarSala(Servicio):
    """
    Servicio de reserva de salas (ej: reuniones, clases, etc.).
    """

    def __init__(self, id, nombre, tipo, precio_base):
        super().__init__(id, nombre, precio_base)
        self.tipo = tipo

    def calcular_costo(self, duracion):
        """
        Calcula el costo basado en horas de uso.
        """
        return self.precio_base * duracion

    def descripcion(self):
        """
        Retorna una descripción del servicio de sala.
        """
        return f"Servicio: {self.nombre} | Sala: {self.tipo}"


# =========================
# SERVICIO: ALQUILER EQUIPOS
# =========================
class AlquilerEquipos(Servicio):
    """
    Servicio de alquiler de equipos con posible descuento por duración.
    """

    def __init__(self, id, nombre, tipo, precio_base):
        super().__init__(id, nombre, precio_base)
        self.tipo = tipo

    def calcular_costo(self, duracion, descuento=0):
        """
        Calcula el costo del alquiler en días.
        Aplica descuento si supera 5 días.
        """
        dias = duracion / 24

        if dias > 5:
            descuento += 0.10

        precio = self.precio_base * dias
        precio_final = precio * (1 - descuento)
        return precio_final

    def descripcion(self):
        """
        Retorna descripción del equipo alquilado.
        """
        return f"Servicio: {self.nombre} | Equipo: {self.tipo}"


# =========================
# SERVICIO: ASESORÍA
# =========================
class Asesoria(Servicio):
    """
    Servicio de asesoría profesional por horas.
    """

    def __init__(self, id, nombre, tipo, precio_base):
        super().__init__(id, nombre, precio_base)
        self.tipo = tipo

    def calcular_costo(self, duracion):
        """
        Calcula costo de asesoría por horas.
        """
        return self.precio_base * duracion

    def descripcion(self):
        """
        Retorna descripción de la asesoría.
        """
        return f"Servicio: {self.nombre} | Asesoria: {self.tipo} "


# =========================
# RESERVA
# =========================
class Reserva:
    """
    Representa una reserva realizada por un cliente sobre un servicio.
    Maneja fechas, duración, estado y cálculo de costo.
    """

    def __init__(self, id_reserva, cliente, servicio, fecha_entrada, fecha_salida):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.estado = "pendiente"

        # duración automática en horas
        self.duracion = self.calcular_duracion()

    def calcular_duracion(self):
        """
        Calcula la duración de la reserva en horas usando datetime.
        """
        diferencia = self.fecha_salida - self.fecha_entrada
        return diferencia.total_seconds() / 3600

    def confirmar(self):
        """
        Cambia el estado de la reserva a confirmada.
        """
        self.estado = "confirmada"

    def cancelar(self):
        """
        Cambia el estado de la reserva a cancelada.
        """
        self.estado = "cancelada"

    def calcular_costo(self):
        """
        Calcula el costo total de la reserva usando el servicio asociado.
        """
        return self.servicio.calcular_costo(self.duracion)

    def __str__(self):
        """
        Representación en texto de la reserva para impresión.
        """
        return (
            f"Reserva #{self.id_reserva} | "
            f"{self.servicio.descripcion()} | "
            f"Estado: {self.estado} | "
            f"Duración: {self.duracion:.2f} horas | "
            f"Costo: ${self.calcular_costo():.2f}"
        )


# =========================
# PRUEBA DEL SISTEMA
# =========================

cliente1 = Cliente(1, "Damian", "correo@gmail.com")

servicio1 = AlquilerEquipos(101, "AlquilerEquipos", "computador", 1000)

entrada = datetime.strptime("2026-05-04 00:00", "%Y-%m-%d %H:%M")
salida = datetime.strptime("2026-05-05 00:00", "%Y-%m-%d %H:%M")

reserva1 = Reserva(1, cliente1, servicio1, entrada, salida)

cliente1.realizar_reserva(reserva1)

print(reserva1)
