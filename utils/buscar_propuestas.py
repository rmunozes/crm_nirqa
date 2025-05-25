from utils.db_connection import create_connection

# Funcion busqueda propuesta
def buscar_propuestas():
    print("Seleccione el campo por el cual desea realizar la búsqueda:")
    print("1. Cliente")
    print("2. Account Manager")
    print("3. Estado (status)")
    print("4. Probabilidad de Cierre")
    print("5. Nombre de Oportunidad")

    opcion = input("Ingrese el número de la opción (1-5): ")

    # Opciones
    if opcion == '1':
        campo = 'cliente'
        campo_nombre = 'Cliente'
    elif opcion == '2':
        campo = 'account_manager'
        campo_nombre = 'Account Manager'
    elif opcion == '3':
        campo = 'status'
        campo_nombre = 'Estado'
    elif opcion == '4':
        campo = 'probabilidad_cierre'
        campo_nombre = 'Probabilidad de Cierre'
    elif opcion == '5':
        campo = 'nombre_oportunidad'
        campo_nombre = 'Nombre de Oportunidad'
    else:
        print("Opción no válida.")
        return

    valor_busqueda = input(f"Ingrese el valor para buscar en el campo '{campo_nombre}': ")

    # Conectar a la base de datos y realizar la busqueda
    conn = create_connection()
    cursor = conn.cursor()

    # Realizar la consulta SQL para buscar las propuestas que coincidan
    query = f"SELECT * FROM propuestas WHERE {campo} LIKE ?"
    cursor.execute(query, ('%' + valor_busqueda + '%',))
    resultados = cursor.fetchall()

    # Mostrar resultados
    if resultados:
        print(f"\nPropuestas que coinciden con '{campo_nombre}' = '{valor_busqueda}':")
        for propuesta in resultados:
            print(f"ID: {propuesta[0]}, Cliente: {propuesta[4]}, Account Manager: {propuesta[7]}, "
                  f"Estado: {propuesta[11]}, Probabilidad de Cierre: {propuesta[10]}, Monto Cierre Soles: {propuesta[12]}, Monto Cierre Dólares: {propuesta[13]}")
    else:
        print(f"No se encontraron propuestas que coincidan con '{valor_busqueda}' en el campo '{campo_nombre}'.")

    conn.close()

if __name__ == "__main__":
    buscar_propuestas()
