from utils.db_connection import create_connection
from models.propuesta import Propuesta

# Función para agregar una nueva propuesta a la base de datos
def agregar_entrada():
    # Datos pre-rellenados como ejemplo
    nro_oportunidad = input("Ingrese el número de oportunidad: ")  # Ejemplo: NQ000123
    fecha_solicitud = input("Ingrese la fecha de solicitud: ")  # Ejemplo: 2024-12-02
    fecha_actualizacion = input("Ingrese la fecha de actualización: ")  # Ejemplo: 2024-12-06
    cliente = input("Ingrese el nombre del cliente: ")  # Ejemplo: TELEFÓNICA
    cliente_final = input("Ingrese el nombre del cliente final: ")  # Ejemplo: PODER JUDICIAL
    nombre_oportunidad = input("Ingrese el nombre de la oportunidad: ")  # Ejemplo: Implementación de Sistema de Telefonía
    account_manager = input("Ingrese el nombre del account manager: ")  # Ejemplo: JUAN PÉREZ
    contacto_cliente = input("Ingrese el nombre del contacto del cliente: ")  # Ejemplo: María López
    preventa_asignado = input("Ingrese el nombre del preventa asignado: ")  # Ejemplo: JUAN MÉNDEZ
    probabilidad_cierre = input("Ingrese la probabilidad de cierre: ")  # Ejemplo: 75%
    status = input("Ingrese el estado de la oportunidad: ")  # Ejemplo: UPSIDE
    cierre_soles = float(input("Ingrese el cierre en soles: "))  # Ejemplo: 15000.00
    cierre_dolares = float(input("Ingrese el cierre en dólares: "))  # Ejemplo: 3000.00


    # Crear el objeto Propuesta
    propuesta = Propuesta(
        nro_oportunidad=nro_oportunidad,
        fecha_solicitud=fecha_solicitud,
        fecha_actualizacion=fecha_actualizacion,
        cliente=cliente,
        cliente_final=cliente_final,
        nombre_oportunidad=nombre_oportunidad,
        account_manager=account_manager,
        contacto_cliente=contacto_cliente,
        preventa_asignado=preventa_asignado,
        probabilidad_cierre=probabilidad_cierre,
        status=status,
        cierre_soles=cierre_soles,
        cierre_dolares=cierre_dolares,
    )

    # Validar los datos antes de insertarlos en la base de datos
    try:
        # Aquí deberías agregar todas las validaciones necesarias (validar_nro_oportunidad, etc.)
        # Si las validaciones son correctas, insertamos los datos

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(""" 
            INSERT INTO propuestas (nro_oportunidad, fecha_solicitud, fecha_actualizacion, cliente, 
            cliente_final, nombre_oportunidad, account_manager, contacto_cliente, preventa_asignado, 
            probabilidad_cierre, status, cierre_soles, cierre_dolares, nro_antiguo)  # Agregamos nro_antiguo a la consulta
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """, (propuesta.nro_oportunidad, propuesta.fecha_solicitud, propuesta.fecha_actualizacion,
              propuesta.cliente, propuesta.cliente_final, propuesta.nombre_oportunidad, propuesta.account_manager,
              propuesta.contacto_cliente, propuesta.preventa_asignado, propuesta.probabilidad_cierre,
              propuesta.status, propuesta.cierre_soles, propuesta.cierre_dolares, propuesta.nro_antiguo))

        # Resetear el contador de ID después de insertar la nueva propuesta
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='propuestas';")

        conn.commit()
        conn.close()

        print("¡Propuesta agregada exitosamente!")
    except ValueError as e:
        print(f"Error de validación: {e}")

# Ejecutar la función para agregar una nueva propuesta
if __name__ == "__main__":
    agregar_entrada()
