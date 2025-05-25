from utils.db_connection import create_connection

# Función para modificar una propuesta existente
def modificar_entrada():
    # Solicitar el id de la propuesta que se desea modificar
    id_propuesta = input("Ingrese el ID de la propuesta que desea modificar: ")

    # Conectar a la base de datos y verificar si la propuesta existe
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM propuestas WHERE id=?", (id_propuesta,))
    propuesta = cursor.fetchone()

    if propuesta:
        print(f"\nPropuesta encontrada con ID {id_propuesta}:")
        print(f"Cliente: {propuesta[4]}")
        print(f"Cliente Final: {propuesta[5]}")
        print(f"Nombre de oportunidad: {propuesta[6]}")
        print(f"Account Manager: {propuesta[7]}")
        print(f"Contacto Cliente: {propuesta[8]}")
        print(f"Preventa Asignado: {propuesta[9]}")
        print(f"Estado: {propuesta[11]}")
        print(f"Probabilidad de cierre: {propuesta[10]}")
        print(f"Cierre en Soles: {propuesta[12]}")
        print(f"Cierre en Dólares: {propuesta[13]}")

        while True:
            # Preguntar qué campo se desea modificar
            print("\n¿Qué deseas modificar?")
            print("1. Cliente")
            print("2. Cliente Final")
            print("3. Nombre de oportunidad")
            print("4. Account Manager")
            print("5. Contacto Cliente")
            print("6. Preventa Asignado")
            print("7. Estado")
            print("8. Probabilidad de cierre")
            print("9. Cierre en Soles")
            print("10. Cierre en Dólares")
            print("11. Salir y guardar cambios")

            opcion = input("Seleccione el número del campo a modificar (1-11): ")

            if opcion == "1":
                modificar = input("¿Estás seguro de que deseas modificar el CLIENTE? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_cliente = input("Ingrese el nuevo nombre del cliente: ")
                    cursor.execute("UPDATE propuestas SET cliente=? WHERE id=?", (nuevo_cliente, id_propuesta))
                else:
                    print("No se modificó el CLIENTE.")
            elif opcion == "2":
                modificar = input("¿Estás seguro de que deseas modificar el CLIENTE FINAL? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_cliente_final = input("Ingrese el nuevo nombre del cliente final: ")
                    cursor.execute("UPDATE propuestas SET cliente_final=? WHERE id=?", (nuevo_cliente_final, id_propuesta))
                else:
                    print("No se modificó el CLIENTE FINAL.")
            elif opcion == "3":
                modificar = input("¿Estás seguro de que deseas modificar el NOMBRE DE OPORTUNIDAD? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_nombre_oportunidad = input("Ingrese el nuevo nombre de la oportunidad: ")
                    cursor.execute("UPDATE propuestas SET nombre_oportunidad=? WHERE id=?", (nuevo_nombre_oportunidad, id_propuesta))
                else:
                    print("No se modificó el NOMBRE DE OPORTUNIDAD.")
            elif opcion == "4":
                modificar = input("¿Estás seguro de que deseas modificar el ACCOUNT MANAGER? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_account_manager = input("Ingrese el nuevo nombre del account manager: ")
                    cursor.execute("UPDATE propuestas SET account_manager=? WHERE id=?", (nuevo_account_manager, id_propuesta))
                else:
                    print("No se modificó el ACCOUNT MANAGER.")
            elif opcion == "5":
                modificar = input("¿Estás seguro de que deseas modificar el CONTACTO CLIENTE? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_contacto_cliente = input("Ingrese el nuevo nombre del contacto cliente: ")
                    cursor.execute("UPDATE propuestas SET contacto_cliente=? WHERE id=?", (nuevo_contacto_cliente, id_propuesta))
                else:
                    print("No se modificó el CONTACTO CLIENTE.")
            elif opcion == "6":
                modificar = input("¿Estás seguro de que deseas modificar el PREVENTA ASIGNADO? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_preventa_asignado = input("Ingrese el nuevo nombre del preventa asignado: ")
                    cursor.execute("UPDATE propuestas SET preventa_asignado=? WHERE id=?", (nuevo_preventa_asignado, id_propuesta))
                else:
                    print("No se modificó el PREVENTA ASIGNADO.")
            elif opcion == "7":
                modificar = input("¿Estás seguro de que deseas modificar el ESTADO? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_estado = input("Ingrese el nuevo estado de la propuesta (UPSIDE, COMMIT, BOOKING, LOST, DESCARTADA): ")
                    cursor.execute("UPDATE propuestas SET status=? WHERE id=?", (nuevo_estado, id_propuesta))
                else:
                    print("No se modificó el ESTADO.")
            elif opcion == "8":
                modificar = input("¿Estás seguro de que deseas modificar la PROBABILIDAD DE CIERRE? (S/N): ").strip().upper()
                if modificar == "S":
                    nueva_probabilidad = input("Ingrese la nueva probabilidad de cierre (0%, 50%, 75%, 90%, 100%): ")
                    cursor.execute("UPDATE propuestas SET probabilidad_cierre=? WHERE id=?", (nueva_probabilidad, id_propuesta))
                else:
                    print("No se modificó la PROBABILIDAD DE CIERRE.")
            elif opcion == "9":
                modificar = input("¿Estás seguro de que deseas modificar el CIERRE EN SOLES? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_cierre_soles = float(input("Ingrese el nuevo monto de cierre en soles: "))
                    cursor.execute("UPDATE propuestas SET cierre_soles=? WHERE id=?", (nuevo_cierre_soles, id_propuesta))
                else:
                    print("No se modificó el CIERRE EN SOLES.")
            elif opcion == "10":
                modificar = input("¿Estás seguro de que deseas modificar el CIERRE EN DÓLARES? (S/N): ").strip().upper()
                if modificar == "S":
                    nuevo_cierre_dolares = float(input("Ingrese el nuevo monto de cierre en dólares: "))
                    cursor.execute("UPDATE propuestas SET cierre_dolares=? WHERE id=?", (nuevo_cierre_dolares, id_propuesta))
                else:
                    print("No se modificó el CIERRE EN DÓLARES.")
            elif opcion == "11":
                # Confirmar los cambios y guardar
                conn.commit()
                print("Los cambios han sido guardados correctamente.")
                break  # Salir después de guardar
            else:
                print("Opción no válida, por favor seleccione una opción válida.")

        # Cerrar la conexión
        conn.close()
    else:
        print(f"No se encontró ninguna propuesta con el ID {id_propuesta}.")
        conn.close()

# Ejecutar la función para modificar una propuesta
if __name__ == "__main__":
    modificar_entrada()

