
import json
from datetime import datetime, timedelta
from typing import List, Optional

DATA_FILE = "hotel_data.json"

class Habitacion:
    def __init__(self, numero: int, tipo: str, precio: float, foto: Optional[str] = None, extra: dict = None):
        self.numero = numero
        self.tipo = tipo  
        self.precio = precio
        self.foto = foto or ""
        self.extra = extra or {}  

    def to_dict(self):
        return {
            "numero": self.numero,
            "tipo": self.tipo,
            "precio": self.precio,
            "foto": self.foto,
            "extra": self.extra
        }

class Cliente:
    def __init__(self, id_cliente:int, nombre: str, direccion: str, telefono: str, habitual: bool=False, descuento: float = 0.0, suscrito_ofertas: bool=False):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.habitual = habitual
        self.descuento = descuento  
        self.suscrito_ofertas = suscrito_ofertas

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "habitual": self.habitual,
            "descuento": self.descuento,
            "suscrito_ofertas": self.suscrito_ofertas
        }

class Reserva:
    def __init__(self, id_reserva:int, cliente_id: int, habitacion_num: int, fecha_entrada: str, dias: int):
        self.id_reserva = id_reserva
        self.cliente_id = cliente_id
        self.habitacion_num = habitacion_num
        self.fecha_entrada = fecha_entrada  
        self.dias = dias

    def to_dict(self):
        return {
            "id_reserva": self.id_reserva,
            "cliente_id": self.cliente_id,
            "habitacion_num": self.habitacion_num,
            "fecha_entrada": self.fecha_entrada,
            "dias": self.dias
        }

class Hotel:
    def __init__(self, nombre: str, estrellas: int):
        self.nombre = nombre
        self.estrellas = estrellas
        self.habitaciones: List[Habitacion] = []
        self.clientes: List[Cliente] = []
        self.reservas: List[Reserva] = []
        self._next_cliente_id = 1
        self._next_reserva_id = 1

   
    def add_habitacion(self, hab: Habitacion):
        self.habitaciones.append(hab)

    def add_cliente(self, cliente: Cliente):
        self.clientes.append(cliente)
        self._next_cliente_id = max(self._next_cliente_id, cliente.id_cliente + 1)

    def add_reserva(self, reserva: Reserva):
        self.reservas.append(reserva)
        self._next_reserva_id = max(self._next_reserva_id, reserva.id_reserva + 1)

    
    def habitaciones_disponibles_por_tipo(self, tipo: str, desde_fecha: Optional[str]=None, dias:int=1):
        
        ocupadas = set()
        if desde_fecha:
            fecha = datetime.strptime(desde_fecha, "%Y-%m-%d")
            rango_inicio = fecha
            rango_fin = fecha + timedelta(days=dias)
            for r in self.reservas:
                r_start = datetime.strptime(r.fecha_entrada, "%Y-%m-%d")
                r_end = r_start + timedelta(days=r.dias)
               
                if (r_start < rango_fin and r_end > rango_inicio):
                    ocupadas.add(r.habitacion_num)
      
        return [h for h in self.habitaciones if h.tipo == tipo and h.numero not in ocupadas]

    def precio_por_tipo(self, tipo: str):
     
        return [h.precio for h in self.habitaciones if h.tipo == tipo]

    def descuento_habitual(self):
       
        return sorted({c.descuento for c in self.clientes if c.habitual})

    def reservar_habitacion(self, cliente_id: int, numero_hab: int, fecha_entrada: str, dias: int):
      
        hab = next((h for h in self.habitaciones if h.numero == numero_hab), None)
        if not hab:
            return False, "Habitación no existe."
       
        fecha = datetime.strptime(fecha_entrada, "%Y-%m-%d")
        rango_inicio = fecha
        rango_fin = fecha + timedelta(days=dias)
        for r in self.reservas:
            if r.habitacion_num != numero_hab:
                continue
            r_start = datetime.strptime(r.fecha_entrada, "%Y-%m-%d")
            r_end = r_start + timedelta(days=r.dias)
            if (r_start < rango_fin and r_end > rango_inicio):
                return False, "Habitación ocupada en esas fechas."
        reserva = Reserva(self._next_reserva_id, cliente_id, numero_hab, fecha_entrada, dias)
        self.add_reserva(reserva)
        return True, f"Reserva creada (id {reserva.id_reserva})."

    def cambiar_precio_por_tipo(self, tipo: str, nuevo_precio: float):
        cont = 0
        for h in self.habitaciones:
            if h.tipo == tipo:
                h.precio = nuevo_precio
                cont += 1
        return cont

  
    def save(self, filename=DATA_FILE):
        data = {
            "hotel": {"nombre": self.nombre, "estrellas": self.estrellas},
            "habitaciones": [h.to_dict() for h in self.habitaciones],
            "clientes": [c.to_dict() for c in self.clientes],
            "reservas": [r.to_dict() for r in self.reservas]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(filename=DATA_FILE):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return None
        h = Hotel(data["hotel"]["nombre"], data["hotel"]["estrellas"])
        for hh in data.get("habitaciones", []):
            h.add_habitacion(Habitacion(hh["numero"], hh["tipo"], hh["precio"], hh.get("foto"), hh.get("extra")))
        for cc in data.get("clientes", []):
            h.add_cliente(Cliente(cc["id_cliente"], cc["nombre"], cc["direccion"], cc["telefono"], cc["habitual"], cc["descuento"], cc.get("suscrito_ofertas", False)))
        for rr in data.get("reservas", []):
            h.add_reserva(Reserva(rr["id_reserva"], rr["cliente_id"], rr["habitacion_num"], rr["fecha_entrada"], rr["dias"]))
        return h


def crear_hotel_demo():
    hotel = Hotel("Hotel ejemplo", 3)
   
    hotel.add_habitacion(Habitacion(101, "sencilla", 50.0, foto="img101.jpg", extra={"exterior": True}))
    hotel.add_habitacion(Habitacion(102, "sencilla", 45.0, foto="img102.jpg", extra={"exterior": False}))
    hotel.add_habitacion(Habitacion(201, "doble", 80.0, foto="img201.jpg", extra={"cama_matrimonial": True}))
    hotel.add_habitacion(Habitacion(202, "doble", 75.0, foto="img202.jpg", extra={"cama_matrimonial": False}))
    hotel.add_habitacion(Habitacion(301, "suite", 150.0, foto="img301.jpg", extra={"banera": True, "sauna": False, "mirador": True}))
    
    hotel.add_cliente(Cliente(1, "Ana Perez", "Calle 1", "123456", habitual=True, descuento=10.0))
    hotel.add_cliente(Cliente(2, "Luis Gomez", "Calle 2", "234567", habitual=False, suscrito_ofertas=True))
    return hotel

def main():
    hotel = Hotel.load() or crear_hotel_demo()
    while True:
        print("\n--- MENU ---")
        print("1) Listar habitaciones disponibles por tipo")
        print("2) Consultar precio por tipo")
        print("3) Consultar descuento clientes habituales")
        print("4) Reservar habitación por número")
        print("5) Cambiar precio por tipo")
        print("6) Guardar y salir")
        opt = input("Elige opción: ").strip()
        if opt == "1":
            tipo = input("Tipo (sencilla/doble/suite): ").strip().lower()
            fecha = input("Fecha inicio (YYYY-MM-DD) o ENTER para hoy: ").strip()
            dias = input("Días (default 1): ").strip()
            if not fecha:
                fecha = datetime.now().strftime("%Y-%m-%d")
            dias = int(dias) if dias else 1
            libres = hotel.habitaciones_disponibles_por_tipo(tipo, fecha, dias)
            if not libres:
                print("No hay habitaciones disponibles de ese tipo en ese rango.")
            else:
                print("Habitaciones disponibles:")
                for h in libres:
                    print(f"  Nº {h.numero} - Precio: {h.precio} - Extra: {h.extra}")
        elif opt == "2":
            tipo = input("Tipo (sencilla/doble/suite): ").strip().lower()
            precios = hotel.precio_por_tipo(tipo)
            if precios:
                print("Precios (por habitación):", precios)
                print("Precio promedio:", sum(precios)/len(precios))
            else:
                print("No hay habitaciones de ese tipo.")
        elif opt == "3":
            descuentos = hotel.descuento_habitual()
            if descuentos:
                print("Descuentos para clientes habituales (porcentajes):", descuentos)
            else:
                print("No hay clientes habituales registrados.")
        elif opt == "4":
            cliente_id = int(input("ID cliente (si no existe, crea nuevo con 0): ").strip())
            if cliente_id == 0:
                nombre = input("Nombre: "); direccion = input("Dirección: "); telefono = input("Teléfono: ")
                habitual = input("Es habitual? (s/n): ").strip().lower() == "s"
                descuento = float(input("Descuento si habitual (ej 10 para 10%): ").strip() or 0.0)
                nuevo_id = hotel._next_cliente_id
                hotel.add_cliente(Cliente(nuevo_id, nombre, direccion, telefono, habitual, descuento, suscrito_ofertas=False))
                cliente_id = nuevo_id
                print("Cliente creado con ID", cliente_id)
            numero_hab = int(input("Número de habitación a reservar: ").strip())
            fecha = input("Fecha entrada (YYYY-MM-DD): ").strip()
            dias = int(input("Número de días: ").strip())
            ok, msg = hotel.reservar_habitacion(cliente_id, numero_hab, fecha, dias)
            print(msg)
        elif opt == "5":
            tipo = input("Tipo (sencilla/doble/suite): ").strip().lower()
            nuevo = float(input("Nuevo precio (ej 80.0): ").strip())
            cont = hotel.cambiar_precio_por_tipo(tipo, nuevo)
            print(f"Cambiado precio en {cont} habitaciones.")
        elif opt == "6":
            hotel.save()
            print("Datos guardados en", DATA_FILE)
            break
        else:
            print("Opción no reconocida.")

if __name__ == "__main__":
    main()
