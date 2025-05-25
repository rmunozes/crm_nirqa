from services.propuesta_validations import (
    validar_nro_oportunidad,
    validar_nro_antiguo,
    validar_fecha,
    validar_cliente,
    validar_cliente_final,
    validar_account_manager,
    validar_preventa_asignado,
    validar_probabilidad,
    validar_status,
    validar_monto_cierre
)
from models.propuesta import Propuesta

# Datos de prueba
propuesta = Propuesta(
    nro_oportunidad="NQ000123",
    fecha_solicitud="2024-12-21",
    fecha_actualizacion="2024-12-22",
    cliente="ITALTEL",
    cliente_final="BANCO DE LA NACIÓN",
    nombre_oportunidad="Implementación de Sistema de Telefonía IP",
    account_manager="RODRIGO MACHADO",
    contacto_cliente="María López",
    preventa_asignado="JUAN MÉNDEZ",
    probabilidad_cierre="75%",
    status="UPSIDE",
    cierre_soles=15000.00,
    cierre_dolares=3000.00
)

# Validación de los datos
try:
    # Realizamos las validaciones
    validar_nro_oportunidad(propuesta.nro_oportunidad)
    validar_fecha(propuesta.fecha_solicitud)
    validar_fecha(propuesta.fecha_actualizacion)
    validar_cliente(propuesta.cliente)
    validar_cliente_final(propuesta.cliente_final)
    validar_account_manager(propuesta.account_manager)
    validar_preventa_asignado(propuesta.preventa_asignado)
    validar_probabilidad(propuesta.probabilidad_cierre)
    propuesta.status = validar_status(propuesta.status, propuesta.probabilidad_cierre)
    propuesta.cierre_soles = validar_monto_cierre(propuesta.cierre_soles, 'soles')
    propuesta.cierre_dolares = validar_monto_cierre(propuesta.cierre_dolares, 'dólares')

    print("Las validaciones han pasado correctamente. Los datos son válidos.")
except ValueError as e:
    print(f"Error de validación: {e}")
