from datetime import datetime

def validar_fecha(fecha_str):
    """
    Valida que la fecha esté en formato YYYY-MM-DD.
    """
    if not fecha_str:
        raise ValueError("La fecha no puede estar vacía")
    try:
        datetime.strptime(str(fecha_str), "%Y-%m-%d")
    except ValueError:
        raise ValueError("Formato de fecha inválido. Usa YYYY-MM-DD")

def validar_probabilidad_cierre(valor):
    """
    Valida que el valor de probabilidad esté entre 0.0 y 1.0.
    """
    if valor is None:
        raise ValueError("La probabilidad de cierre no puede ser nula")
    if not (0.0 <= float(valor) <= 1.0):
        raise ValueError("La probabilidad de cierre debe estar entre 0.0 y 1.0")

def validar_valor_numerico_opcional(valor):
    """
    Convierte el valor a float si es posible, o retorna None si está vacío o inválido.
    """
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValueError("El valor debe ser un número o estar vacío")
