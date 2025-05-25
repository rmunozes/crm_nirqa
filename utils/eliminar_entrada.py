from utils.db_connection import create_connection

# Función para eliminar una propuesta de la base de datos
def eliminar_entrada():
    # Solicitar el id de la propuesta a eliminar
    id_propuesta = input("Ingrese el ID de la propuesta que desea eliminar: ")

    # Validar que el id ingresado sea un número
    try:
        id_propuesta = int(id_propuesta)
    except ValueError:
        print("El ID debe ser un número entero.")
        return

    # Conectar a la base de datos y verificar si la propuesta existe
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM propuestas WHERE id=?", (id_propuesta,))
    propuesta = cursor.fetchone()

    if propuesta:
        # Si la propuesta existe, eliminarla
        cursor.execute("DELETE FROM propuestas WHERE id=?", (id_propuesta,))
        
        # Reiniciar el contador de ID después de eliminar la propuesta
        # Esto asegura que la siguiente propuesta creada obtendrá el ID correcto.
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='propuestas';")
        
        conn.commit()
        print(f"Propuesta con ID {id_propuesta} eliminada correctamente.")
    else:
        print(f"No se encontró ninguna propuesta con el ID {id_propuesta}.")
    
    conn.close()

# Ejecutar la función para eliminar la propuesta
if __name__ == "__main__":
    eliminar_entrada()
