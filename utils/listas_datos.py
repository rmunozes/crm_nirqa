# CLIENTE = ['Airon Group', 'BVS', 'CESCORP', 'Claro', 'E&M Instalacion', 'ENTEL/TMOWS', 'EyM', 'GRPasco', 'GTD', 'Goldfields', 'INFINITEK', 'ITALTEL', 'ITAS Solutions', 'Italtel', 'Logicalis', 'NEXUS/Cisco', 'None', 'Noovus/Internexa', 'PNP', 'Pluspetrol', 'Quanta', 'RENIEC', 'SpeedCast', 'Sunarp', 'Tecnosys', 'Telefónica']

# ACCOUNT_MANAGER ahora se genera dinámicamente ['Alejandra Oyarce', 'Andrea Urcuhuaranga', 'Jhonny Avila', 'Raphael Munoz', 'Raphael Muñoz']

# PREVENTA_ASIGNADO ahora se genera dinámicamente ['Eder Huillca', 'Jhonny Avila', 'Juan Carlos Lopes', 'Juan Mendez', 'None', 'Raphael Muñoz', 'Rodrigo Machado', 'Traitor']

PROBABILIDAD_CIERRE = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]

STATUS = ['No offer', 'Upside', 'Commit', 'Booking','dismiss', 'lost']

ROLES = [
    "administrador",
    "gerente",
    "director",
    "account_manager",
    "preventa",
    "gestor"
]


from utils.db_connection import get_db_connection

def get_account_managers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios WHERE rol = 'account_manager' AND activo = 1")
    resultado = [fila["nombre"] for fila in cursor.fetchall()]
    conn.close()
    return resultado

def get_preventas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuarios WHERE rol = 'preventa' AND activo = 1")
    resultado = [fila["nombre"] for fila in cursor.fetchall()]
    conn.close()
    return resultado

def get_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM clientes ORDER BY nombre ASC")
    resultado = [fila["nombre"] for fila in cursor.fetchall()]
    conn.close()
    return resultado


