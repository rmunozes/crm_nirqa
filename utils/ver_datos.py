import sqlite3
import os

def ver_datos():
    # Ruta de la base de datos
    db_path = os.path.abspath("/Users/rominavaleria/PycharmProjects/PROYECTO_CRM/database/crm_database.db")

    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta SQL para obtener todos los datos de la tabla 'propuestas'
    cursor.execute("SELECT * FROM propuestas")

    # Obtener todos los registros
    rows = cursor.fetchall()

    # Si hay datos, imprímelos en la consola
    if rows:
        print("Datos de la tabla 'propuestas':")
        for row in rows:
            print(row)

        # Preguntar si se desea guardar los resultados en un archivo de texto
        guardar = input("\n¿Deseas guardar los datos en un archivo de texto? (s/n): ")
        if guardar.lower() == 's':
            with open("datos_propuestas.txt", "w") as file:
                for row in rows:
                    file.write(str(row) + "\n")
            print("Datos guardados en 'datos_propuestas.txt'")
    else:
        print("No hay datos en la tabla 'propuestas'.")

    # Cerrar la conexión
    conn.close()

if __name__ == "__main__":
    ver_datos()
