class Propuesta:
    def __init__(self, id, nro_antiguo, fecha_solicitud, fecha_actualizacion,
                 cliente, cliente_final, nombre_oportunidad, account_manager,
                 contacto_cliente, preventa_asignado, probabilidad_cierre,
                 status, cierre_soles, cierre_dolares, comentarios):
        self.id = id
        self.nro_antiguo = nro_antiguo
        self.fecha_solicitud = fecha_solicitud
        self.fecha_actualizacion = fecha_actualizacion
        self.cliente = cliente
        self.cliente_final = cliente_final
        self.nombre_oportunidad = nombre_oportunidad
        self.account_manager = account_manager
        self.contacto_cliente = contacto_cliente
        self.preventa_asignado = preventa_asignado
        self.probabilidad_cierre = probabilidad_cierre
        self.status = status
        self.cierre_soles = cierre_soles
        self.cierre_dolares = cierre_dolares
        self.comentarios = comentarios

    @property
    def nro_oportunidad(self):
        return self.id
