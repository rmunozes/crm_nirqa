from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import date, datetime, timedelta
from urllib.parse import urlencode


from services.propuesta_service import leer_logs_propuesta
import bcrypt
import sqlite3
import io
import xlsxwriter
import re
import secrets
import string
import xml.etree.ElementTree as ET



def tiene_permiso(accion):
    rol = session.get("rol")
    permisos = {
        "ver_propuestas": ["preventa", "account_manager", "gerente", "director", "administrador"],
        "editar_propias": ["preventa", "account_manager"],
        "nueva_propuesta": ["account_manager", "gerente", "director", "administrador"],
        "admin_usuarios": ["administrador"],
        "admin_clientes": ["administrador"],
        "facturacion": ["gestor", "director", "administrador"]
    }
    return rol in permisos.get(accion, [])


def es_password_segura(password):
    return (
            len(password) >= 8 and
            re.search(r"[A-Z]", password) and
            re.search(r"[a-z]", password) and
            re.search(r"[0-9]", password) and
            re.search(r"[\W_]", password)
    )


from services import facturacion_service
# 🔐 Conexión a base de datos
from utils.db_connection import get_db_connection

# 📋 Constantes y listas dinámicas
from utils.listas_datos import get_clientes, get_account_managers, get_preventas, STATUS, PROBABILIDAD_CIERRE, ROLES

# 🧱 Módulo de propuestas
from services.propuesta_service import (
    leer_propuestas,
    guardar_propuesta,
    actualizar_propuesta,
    actualizar_comentario,
    contar_propuestas,
    leer_logs_propuesta,
    guardar_log,
    Propuesta,
    generar_nuevo_id
)

# 💳 Módulo de facturación
from services.facturacion_service import (
    obtener_propuestas_booking,
    obtener_todo_facturacion,
    obtener_resumen_facturacion,
    obtener_status_propuesta,
    obtener_moneda_oc_existentes,
    crear_orden_compra,
    leer_ordenes_compra,       # ✅ AÑADIR
    leer_facturas              # ✅ AÑADIR
)

from services.facturacion_service import obtener_logs_por_propuesta



# 🛠️ Inicialización de tablas si es necesario
# from utils.crear_tablas_facturacion import crear_tablas_facturacion

app = Flask(__name__)
app.secret_key = "clave_super_secreta"  # cámbiala por una segura en producción
app.permanent_session_lifetime = timedelta(minutes=20)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND activo = 1", (email,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            hashed_password = usuario["password"]
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                session.permanent = True
                session["usuario_id"] = usuario["id"]
                session["nombre"] = usuario["nombre"]
                session["rol"] = usuario["rol"]

                # 🔒 Validar si han pasado más de 180 días desde el último cambio
                ultima_fecha_str = usuario["ultima_actualizacion_password"]

                # Forzar cambio si nunca la ha actualizado
                if not ultima_fecha_str:
                    flash("Debes cambiar tu contraseña antes de continuar.", "error")
                    return redirect(url_for("cambiar_password", id=usuario["id"]))

                # Forzar cambio si han pasado más de 6 meses
                try:
                    ultima_fecha = datetime.strptime(ultima_fecha_str, "%Y-%m-%d").date()
                    if (date.today() - ultima_fecha).days > 180:
                        flash("Por seguridad, debes actualizar tu contraseña.", "error")
                        return redirect(url_for("cambiar_password", id=usuario["id"]))
                except Exception:
                    pass  # Si hay error con la fecha, se omite la validación

                return redirect(url_for("index"))

        flash("Credenciales incorrectas", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    filtros = request.args.to_dict()
    pagina = int(filtros.pop("pagina", 1))  # Por defecto, página 1
    filas_por_pagina = 50

    # ✅ NUEVO: parámetros de ordenamiento
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")

    # -------------------------
    # Restricciones por perfil
    # -------------------------
    rol = session.get("rol")
    usuario = session.get("nombre")

    if rol == "account_manager":
        filtros["account_manager"] = usuario
    elif rol == "preventa":
        filtros["preventa_asignado"] = usuario
    elif rol == "gestor":
        flash("Acceso denegado: no tienes permisos para ver propuestas", "error")
        return redirect(url_for("facturacion_index"))

    # ✅ Ahora incluye ordenamiento dinámico
    propuestas = leer_propuestas(filtros, pagina, filas_por_pagina, sort=sort, order=order)
    total = contar_propuestas(filtros)
    total_paginas = (total + filas_por_pagina - 1) // filas_por_pagina

    args_sin_pagina = dict(request.args)
    args_sin_pagina.pop('pagina', None)

    return render_template(
        "index.html",
        propuestas=propuestas,
        pagina=pagina,
        total_paginas=total_paginas,
        request=request,
        args_sin_pagina=args_sin_pagina,
        mostrar_volver=False,
        sort=sort,
        order=order
    )



@app.route("/propuestas/editar/<string:id>", methods=["GET", "POST"])
def editar_propuesta(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    filtros = {"id": id}
    propuestas = leer_propuestas(filtros=filtros, pagina=1, filas_por_pagina=1)
    propuesta = propuestas[0] if propuestas else None

    if not propuesta:
        flash("Propuesta no encontrada.", "error")
        return redirect(url_for("index"))

    # 🔒 Validación de permisos
    if not puede_editar_propuesta(propuesta):
        flash("No tienes permiso para editar esta propuesta.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        campos = [
            "nro_antiguo", "fecha_solicitud", "cliente", "cliente_final",
            "nombre_oportunidad", "account_manager", "contacto_cliente",
            "preventa_asignado", "probabilidad_cierre", "status",
            "cierre_soles", "cierre_dolares"
        ]

        for campo in campos:
            valor_anterior = getattr(propuesta, campo)
            nuevo_valor = request.form.get(campo)

            # Normalizar comparaciones numéricas
            if campo in ["cierre_soles", "cierre_dolares", "probabilidad_cierre"]:
                try:
                    valor_anterior = float(valor_anterior) if valor_anterior is not None else 0.0
                    nuevo_valor = float(nuevo_valor) if nuevo_valor else 0.0
                except ValueError:
                    valor_anterior = str(valor_anterior).strip()
                    nuevo_valor = nuevo_valor.strip()
            else:
                valor_anterior = "" if valor_anterior is None else str(valor_anterior).strip()
                nuevo_valor = "" if nuevo_valor is None else nuevo_valor.strip()

            if valor_anterior != nuevo_valor:
                guardar_log(
                    id_propuesta=propuesta.id,
                    campo=campo,
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    usuario_id=session.get("nombre", "Desconocido")
                )
                setattr(propuesta, campo, nuevo_valor)

        propuesta.fecha_actualizacion = datetime.now().date().isoformat()
        actualizar_propuesta(propuesta)
        flash("Propuesta actualizada correctamente.", "success")
        return redirect(url_for("index"))

    # Cargar listas desplegables necesarias para GET
    clientes = get_clientes()
    account_managers = get_account_managers()
    preventas = get_preventas()
    probabilidades = PROBABILIDAD_CIERRE
    estados = STATUS

    # Cargar logs de la propuesta
    logs = sorted(leer_logs_propuesta(id), key=lambda l: l["fecha"], reverse=True)

    return render_template(
        "editar_propuesta.html",
        propuesta=propuesta,
        clientes=clientes,
        account_managers=account_managers,
        preventas=preventas,
        probabilidades=probabilidades,
        estados=estados,
        logs=logs
    )


@app.route("/propuestas/nueva", methods=["GET", "POST"])
def agregar_propuesta():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        propuestas = leer_propuestas()
        nuevo_id = generar_nuevo_id(propuestas)

        propuesta = Propuesta(
            id=nuevo_id,
            nro_antiguo=request.form.get("nro_antiguo"),
            fecha_solicitud=request.form.get("fecha_solicitud"),
            fecha_actualizacion=request.form.get("fecha_actualizacion"),
            cliente=request.form.get("cliente"),
            cliente_final=request.form.get("cliente_final"),
            nombre_oportunidad=request.form.get("nombre_oportunidad"),
            account_manager=request.form.get("account_manager"),
            contacto_cliente=request.form.get("contacto_cliente"),
            preventa_asignado=request.form.get("preventa_asignado"),
            probabilidad_cierre=request.form.get("probabilidad_cierre"),
            status=request.form.get("status"),
            cierre_soles=request.form.get("cierre_soles"),
            cierre_dolares=request.form.get("cierre_dolares"),
            comentarios=""
        )
        guardar_propuesta(propuesta)
        return redirect(url_for("index"))

    return render_template(
        "agregar_propuesta.html",
        fecha_hoy=date.today().isoformat(),
        clientes=get_clientes(),
        account_managers=get_account_managers(),
        preventas=get_preventas(),
        estados=STATUS,
        probabilidades=PROBABILIDAD_CIERRE
    )


def generar_password_segura():
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(caracteres) for _ in range(12))

@app.route("/usuarios/nuevo", methods=["GET", "POST"])
def crear_usuario():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    if session.get("rol") != "administrador":
        flash("Acceso denegado: solo administradores pueden crear usuarios", "error")
        return redirect(url_for("index"))

    mostrar_password = False
    password = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        rol = request.form.get("rol")
        password_form = request.form.get("password", "").strip()

        if not (nombre and email and rol):
            flash("Todos los campos excepto la contraseña son obligatorios", "error")
            return redirect(request.url)

        if not password_form:
            password = generar_password_segura()
            mostrar_password = True
        else:
            password = password_form
            mostrar_password = False

        if not es_password_segura(password):
            flash("La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y símbolos.", "error")
            return redirect(request.url)

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        fecha_actualizacion = None  # Forzar cambio al primer login

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            if usuario_existente["activo"] == 1:
                flash("Ya existe un usuario activo con ese email", "error")
            else:
                # Reactivar usuario inactivo
                cursor.execute("""
                    UPDATE usuarios
                    SET nombre = ?, password = ?, rol = ?, activo = 1, ultima_actualizacion_password = ?
                    WHERE id = ?
                """, (nombre, password_hash, rol, fecha_actualizacion, usuario_existente["id"]))
                conn.commit()
                flash("Usuario reactivado exitosamente", "ok")
                if mostrar_password:
                    flash(f"Contraseña temporal generada para {email}: {password}", "info")
        else:
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol, activo, ultima_actualizacion_password)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (nombre, email, password_hash, rol, fecha_actualizacion))
            conn.commit()
            flash("Usuario creado exitosamente", "ok")
            if mostrar_password:
                flash(f"Contraseña temporal generada para {email}: {password}", "info")

        conn.close()

    return render_template("nuevo_usuario.html", roles=ROLES, password_generada=password if mostrar_password else "")



@app.route("/admin/usuarios")
def admin_usuarios():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso denegado", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, rol, activo FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    return render_template("admin_usuarios.html", usuarios=usuarios)


@app.route("/admin/usuarios/<int:id>/cambiar_password", methods=["GET", "POST"])
def cambiar_password(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin_usuarios"))

    if request.method == "POST":
        nueva_password = request.form.get("nueva_password", "").strip()
        confirmar_password = request.form.get("confirmar_password", "").strip()

        if not nueva_password or not confirmar_password or nueva_password != confirmar_password:
            flash("Las contraseñas no coinciden o están vacías", "error")
            return redirect(request.url)

        if not es_password_segura(nueva_password):
            flash("La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y símbolos.", "error")
            return redirect(request.url)

        # Verificar que la nueva no sea igual a la actual
        hashed_actual = usuario["password"]
        if bcrypt.checkpw(nueva_password.encode("utf-8"), hashed_actual):
            flash("La nueva contraseña no puede ser igual a la actual.", "error")
            return redirect(request.url)

        # Verificar que la nueva no sea igual a la anterior (si existe)
        hashed_anterior = usuario["password_anterior"]
        if hashed_anterior and bcrypt.checkpw(nueva_password.encode("utf-8"), hashed_anterior.encode("utf-8")):
            flash("No puedes reutilizar tu contraseña anterior.", "error")
            return redirect(request.url)

        # Generar y guardar la nueva contraseña
        nuevo_hash = bcrypt.hashpw(nueva_password.encode("utf-8"), bcrypt.gensalt())
        hoy = date.today().isoformat()

        cursor.execute("""
            UPDATE usuarios
            SET password_anterior = password,
                password = ?,
                ultima_actualizacion_password = ?
            WHERE id = ?
        """, (nuevo_hash, hoy, id))

        conn.commit()
        conn.close()

        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for("admin_usuarios"))

    conn.close()
    return render_template("cambiar_password.html", usuario=usuario)


@app.route("/usuarios/editar/<int:usuario_id>", methods=["GET", "POST"])
def editar_usuario(usuario_id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    if session.get("rol") != "administrador":
        flash("Acceso denegado: solo administradores pueden editar usuarios", "error")
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        conn.close()
        flash("Usuario no encontrado", "error")
        return redirect(url_for("admin_usuarios"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")
        activo = 1 if request.form.get("activo") == "1" else 0

        # Verificar si el email está siendo usado por otro usuario
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND id != ?", (email, usuario_id))
        otro = cursor.fetchone()
        if otro:
            conn.close()
            flash("Ya existe otro usuario con ese correo", "error")
            return redirect(request.url)

        # Actualizar contraseña si fue ingresada
        if password:
            if not es_password_segura(password):
                conn.close()
                flash("La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y símbolos.", "error")
                return redirect(request.url)
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute("""
                UPDATE usuarios
                SET nombre = ?, email = ?, password = ?, rol = ?, activo = ?, ultima_actualizacion_password = ?
                WHERE id = ?
            """, (nombre, email, password_hash, rol, activo, datetime.now().date(), usuario_id))
        else:
            # Sin cambio de contraseña
            cursor.execute("""
                UPDATE usuarios
                SET nombre = ?, email = ?, rol = ?, activo = ?
                WHERE id = ?
            """, (nombre, email, rol, activo, usuario_id))

        conn.commit()
        conn.close()
        flash("Usuario actualizado exitosamente", "ok")
        return redirect(url_for("admin_usuarios"))

    conn.close()
    return render_template("editar_usuario.html", usuario=usuario, roles=ROLES)



@app.route("/clientes")
def admin_clientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return render_template("admin_clientes.html", clientes=clientes)


@app.route("/admin/usuarios/<int:id>/eliminar", methods=["POST"])
def eliminar_usuario(id):
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso denegado", "error")
        return redirect(url_for("index"))

    if session["usuario_id"] == id:
        flash("No puedes eliminar tu propio usuario", "error")
        return redirect(url_for("admin_usuarios"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Usuario eliminado exitosamente", "ok")
    return redirect(url_for("admin_usuarios"))


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        email = request.form.get("email")
        contacto_principal = request.form.get("contacto")  # ← este es el fix
        notas = request.form.get("notas")

        if not nombre:
            flash("El campo 'Cliente' es obligatorio.", "error")
            return render_template("nuevo_cliente.html")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre, direccion, telefono, email, contacto_principal, notas)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, direccion, telefono, email, contacto_principal, notas))
            conn.commit()
            flash("Cliente creado exitosamente.", "success")
            return redirect(url_for("admin_clientes"))
        except Exception as e:
            flash(f"Ocurrió un error: {e}", "error")
        finally:
            conn.close()

    return render_template("nuevo_cliente.html")


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        email = request.form.get("email")
        contacto_principal = request.form.get("contacto")

        if not nombre:
            flash("El campo 'Cliente' es obligatorio.", "error")
        else:
            cursor.execute("""
                UPDATE clientes
                SET nombre = ?, direccion = ?, telefono = ?, email = ?, contacto_principal = ?
                WHERE id = ?
            """, (nombre, direccion, telefono, email, contacto_principal, id))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_clientes"))

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (id,))
    cliente = cursor.fetchone()
    conn.close()

    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/propuestas/comentarios/<string:id>", methods=["GET", "POST"])
def editar_comentario(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    propuesta = next((p for p in leer_propuestas({"id": id}) if p.id == id), None)
    if not propuesta:
        flash("Propuesta no encontrada.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        nuevo = request.form.get("nuevo_comentario")
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        entrada = f"[{timestamp}] {nuevo}"

        comentario_actual = propuesta.comentarios or ""
        comentario_actualizado = f"{entrada}\n{comentario_actual}".strip()

        actualizar_comentario(id, comentario_actualizado)
        flash("Comentario añadido exitosamente.", "success")
        return redirect(url_for("index"))

    return render_template("editar_comentario.html", propuesta=propuesta)


@app.template_filter('datetimeformat')
def datetimeformat(value):
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d")
        except:
            return value
    return value.strftime("%d/%m/%Y")


@app.before_request
def verificar_acceso():
    rutas_publicas = ["/login", "/static", "/favicon.ico"]
    if not session.get("usuario_id"):
        if not any(request.path.startswith(r) for r in rutas_publicas):
            return redirect(url_for('login'))


@app.template_filter("datetime")
def datetime_filter(value, format="%d-%m-%Y %H:%M"):
    dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    return dt.strftime(format)


# Aca inicia facturacion
@app.route("/facturacion/nueva_oc", methods=["GET", "POST"])
def nueva_orden_compra():
    if request.method == "POST":
        id_propuesta = request.form.get("id_propuesta")
        nro_oc = request.form.get("nro_oc")
        fecha_oc = request.form.get("fecha_oc")
        monto_oc = float(request.form.get("monto_oc", 0))
        moneda = request.form.get("moneda")
        pm_asignado = request.form.get("pm_asignado")
        print("📌 ID propuesta recibido en POST:", id_propuesta)  # 👈 AGREGA ESTO
        # Validaciones
        status = obtener_status_propuesta(id_propuesta)
        if status != "Booking":
            return "Error: Propuesta no está en estado 'Booking'.", 400

        monedas_existentes = obtener_moneda_oc_existentes(id_propuesta)
        if monedas_existentes and moneda not in monedas_existentes:
            return "Error: Moneda no coincide con órdenes anteriores.", 400

        if monto_oc <= 0:
            return "Error: El monto debe ser mayor que cero.", 400

        # Validar que la suma total de OCs no exceda cierre_soles o cierre_dolares
        propuesta = leer_propuestas({"id": id_propuesta})[0] if id_propuesta else None
        if not propuesta:
            return "Error: Propuesta no encontrada", 400

        # 🔒 Validar que solo se pueda usar la moneda correspondiente al cierre definido
        if moneda == "S/" and not propuesta.cierre_soles:
            return "Error: No se puede registrar OC en soles si no se ha definido 'cierre_soles'.", 400
        if moneda == "US$" and not propuesta.cierre_dolares:
            return "Error: No se puede registrar OC en dólares si no se ha definido 'cierre_dolares'.", 400

        ordenes = facturacion_service.obtener_todas_oc()
        ordenes_filtradas = [oc for oc in ordenes if oc["id_propuesta"] == id_propuesta and oc["moneda"] == moneda]
        total_actual = sum(float(oc["monto_oc"]) for oc in ordenes_filtradas)

        if moneda == "S/":
            maximo = float(propuesta.cierre_soles or 0)
        elif moneda == "US$":
            maximo = float(propuesta.cierre_dolares or 0)
        else:
            return "Error: Moneda no válida.", 400

        if total_actual + monto_oc > maximo:
            return f"Error: El monto total de órdenes de compra ({moneda} {total_actual + monto_oc:,.2f}) excede el cierre permitido ({moneda} {maximo:,.2f}).", 400

        datos_oc = {
            "id_propuesta": id_propuesta,
            "nro_oc": nro_oc,
            "fecha_oc": fecha_oc,
            "monto_oc": monto_oc,
            "moneda": moneda,
            "pm_asignado": pm_asignado
        }
        crear_orden_compra(datos_oc)


        if request.args.get("ajax") == "1":
            ordenes = facturacion_service.obtener_todas_oc()
            facturas = facturacion_service.obtener_todo_facturacion()[1]
            ordenes_filtradas = [oc for oc in ordenes if oc["id_propuesta"] == id_propuesta]
            ids_oc = [oc["id_oc"] for oc in ordenes_filtradas]
            facturas_filtradas = [f for f in facturas if f["id_oc"] in ids_oc]
            propuesta = leer_propuestas({"id": id_propuesta})[0]


            return render_template("facturacion/facturacion_detalles_parcial.html",
                                   ordenes=ordenes_filtradas,
                                   facturas=facturas_filtradas,
                                   id_propuesta=id_propuesta,
                                   propuesta=propuesta
                                   )

        else:
            return redirect(url_for("facturacion_index", id_abierta=id_propuesta))

    # ←←← Esto es para manejar GET con id_propuesta
    id_propuesta = request.args.get("id_propuesta", "")
    propuesta = leer_propuestas({"id": id_propuesta})[0] if id_propuesta else None
    return render_template("facturacion/oc_nueva.html", id_propuesta=id_propuesta, propuesta=propuesta)

    print(">>> POST recibido: id_propuesta =", id_propuesta)

@app.route('/facturacion')
def facturacion_index():
    filtros = request.args.to_dict()
    pagina = int(request.args.get("pagina", 1))
    filas_por_pagina = 50
    offset = (pagina - 1) * filas_por_pagina

    ordenes, facturas = facturacion_service.obtener_todo_facturacion()

    print("🔍 Total ordenes de compra recibidas:", len(ordenes))
    for oc in ordenes[:5]:
        print(f"🧾 OC ID: {oc['id_oc']} | Propuesta: {oc['id_propuesta']} | Monto: {oc['monto_oc']} {oc['moneda']}")

    propuestas_completas = leer_propuestas(
        filtros={"status": "Booking"},
        pagina=1,
        filas_por_pagina=10000  # trae todas
    )

    from services.propuesta_service import leer_logs_propuesta
    from datetime import datetime

    # Cargar logs una sola vez
    logs_por_propuesta = {p.id: leer_logs_propuesta(p.id) for p in propuestas_completas}

    # Agregar campos calculados a cada propuesta
    for p in propuestas_completas:
        # Fecha de booking en formato YYYY-MM-DD (para filtros)
        fecha_booking = ""
        for log in logs_por_propuesta.get(p.id, []):
            if log["campo"] == "status" and log["valor_nuevo"].strip().lower() == "booking":
                fecha_booking = log["fecha"][:10]  # YYYY-MM-DD
                break
        #p.fecha_booking = fecha_booking
        p.fecha_booking = fecha_booking if fecha_booking else None

        # Totales por moneda
        ocs = [oc for oc in ordenes if oc["id_propuesta"] == p.id]
        p.total_soles = sum(float(oc["monto_oc"]) for oc in ocs if oc["moneda"] == "S/")
        p.total_dolares = sum(float(oc["monto_oc"]) for oc in ocs if oc["moneda"] == "US$")

    propuestas_filtradas = propuestas_completas

    # 🔍 Filtros de OC y factura
    if filtros.get("nro_oc"):
        nro_oc = filtros["nro_oc"].lower()
        oc_encontradas = [oc for oc in ordenes if nro_oc in oc["nro_oc"].lower()]
        ids_propuesta_oc = set(oc["id_propuesta"] for oc in oc_encontradas)
        propuestas_filtradas = [p for p in propuestas_filtradas if p.id in ids_propuesta_oc]
        ordenes = oc_encontradas

    if filtros.get("nro_factura"):
        nro_factura = filtros["nro_factura"].lower()
        facturas_encontradas = [f for f in facturas if nro_factura in f["nro_factura"].lower()]
        ids_oc_facturas = set(f["id_oc"] for f in facturas_encontradas)
        oc_asociadas = [oc for oc in ordenes if oc["id_oc"] in ids_oc_facturas]
        ids_propuesta_facturas = set(oc["id_propuesta"] for oc in oc_asociadas)
        propuestas_filtradas = [p for p in propuestas_filtradas if p.id in ids_propuesta_facturas]
        facturas = facturas_encontradas
        ordenes = oc_asociadas

    # 🔍 Filtros por campos de propuesta
    if filtros.get("id_propuesta"):
        propuestas_filtradas = [p for p in propuestas_filtradas if filtros["id_propuesta"].lower() in p.id.lower()]
    if filtros.get("cliente"):
        propuestas_filtradas = [p for p in propuestas_filtradas if filtros["cliente"].lower() in p.cliente.lower()]
    if filtros.get("cliente_final"):
        propuestas_filtradas = [p for p in propuestas_filtradas if filtros["cliente_final"].lower() in p.cliente_final.lower()]
    if filtros.get("nombre_oportunidad"):
        propuestas_filtradas = [p for p in propuestas_filtradas if filtros["nombre_oportunidad"].lower() in p.nombre_oportunidad.lower()]

    # 🔍 Filtros por rangos de fecha y montos
    if filtros.get("fecha_booking_desde"):
        propuestas_filtradas = [
            p for p in propuestas_filtradas
            if p.fecha_booking and p.fecha_booking >= filtros["fecha_booking_desde"]
        ]
    if filtros.get("fecha_booking_hasta"):
        propuestas_filtradas = [
            p for p in propuestas_filtradas
            if p.fecha_booking and p.fecha_booking <= filtros["fecha_booking_hasta"]
        ]
    if filtros.get("min_soles"):
        propuestas_filtradas = [p for p in propuestas_filtradas if (p.total_soles or 0) >= float(filtros["min_soles"])]
    if filtros.get("max_soles"):
        propuestas_filtradas = [p for p in propuestas_filtradas if (p.total_soles or 0) <= float(filtros["max_soles"])]
    if filtros.get("min_dolares"):
        propuestas_filtradas = [p for p in propuestas_filtradas if (p.total_dolares or 0) >= float(filtros["min_dolares"])]
    if filtros.get("max_dolares"):
        propuestas_filtradas = [p for p in propuestas_filtradas if (p.total_dolares or 0) <= float(filtros["max_dolares"])]

    # 🔃 Aplicar ordenamiento si se solicita
    sort_key = filtros.get("sort")
    sort_order = filtros.get("order", "asc")

    if sort_key:
        reverse = sort_order == "desc"
        def sort_val(p):
            val = getattr(p, sort_key, "")
            if sort_key in ["total_soles", "total_dolares"]:
                return float(val or 0)
            return str(val or "").lower()
        try:
            propuestas_filtradas.sort(key=sort_val, reverse=reverse)
        except Exception as e:
            print("Error al ordenar:", e)

    total_propuestas = len(propuestas_filtradas)
    propuestas_paginadas = propuestas_filtradas[offset:offset + filas_por_pagina]

    # Construir el query string sin el parámetro de paginación
    filtros_sin_pagina = {k: v for k, v in filtros.items() if k != "pagina"}
    query_string_base = urlencode(filtros_sin_pagina)

    return render_template(
        'facturacion/facturacion_index.html',
        ordenes=ordenes,
        facturas=facturas,
        propuestas=propuestas_paginadas,
        pagina_actual=pagina,
        total_paginas=(total_propuestas + filas_por_pagina - 1) // filas_por_pagina,
        mostrar_volver=True,
        query_string_base=query_string_base
    )
    print(">> FILTROS ACTIVOS:", filtros)
    print(">> Ejemplo propuesta:",
          propuestas_filtradas[0].__dict__ if propuestas_filtradas else "ninguna propuesta pasa")


@app.route('/facturacion/factura/nueva', methods=['GET', 'POST'])
def nueva_factura():
    if request.method == 'POST':
        datos = {
            'id_oc': request.form['id_oc'],
            'nro_factura': request.form['nro_factura'],
            'fecha_factura': request.form['fecha_factura'],
            'monto_factura': request.form['monto_factura']
        }

        # 🔒 Validar que el número de factura no se repita
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM facturas WHERE nro_factura = ?", (datos['nro_factura'],))
        existe = cursor.fetchone()['total']
        conn.close()

        if existe > 0:
            return f"Error: Ya existe una factura con el número {datos['nro_factura']}", 400

        # Leer id_propuesta y monto_oc de esa OC
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_propuesta, monto_oc FROM ordenes_compra WHERE id_oc = ?", (datos["id_oc"],))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return "Error: OC no válida", 400

        id_propuesta = row["id_propuesta"]
        monto_oc = float(row["monto_oc"])
        nuevo_monto = float(datos["monto_factura"])

        # Obtener total facturado actual para esa OC
        cursor.execute("SELECT SUM(monto_factura) AS total FROM facturas WHERE id_oc = ?", (datos["id_oc"],))
        total_facturado = cursor.fetchone()["total"] or 0

        if total_facturado + nuevo_monto > monto_oc:
            conn.close()
            return f"❌ Error: El total facturado ({total_facturado + nuevo_monto:,.2f}) excede el monto de la OC ({monto_oc:,.2f})", 400

        conn.close()

        if not row:
            return "Error: OC no válida", 400
        id_propuesta = row["id_propuesta"]

        resultado = facturacion_service.crear_factura(datos)

        if request.args.get("ajax") == "1":
            ordenes = facturacion_service.obtener_todas_oc()
            facturas = facturacion_service.obtener_todo_facturacion()[1]
            ordenes_filtradas = [oc for oc in ordenes if oc["id_propuesta"] == id_propuesta]
            ids_oc = [oc["id_oc"] for oc in ordenes_filtradas]
            facturas_filtradas = [f for f in facturas if f["id_oc"] in ids_oc]


            propuesta = leer_propuestas({"id": id_propuesta})[0]  # ✅ Añadir esta línea
            return render_template("facturacion/facturacion_detalles_parcial.html",
                                   ordenes=ordenes_filtradas,
                                   facturas=facturas_filtradas,
                                   id_propuesta=id_propuesta,
                                   propuesta=propuesta)  # ✅ Añadir propuesta

        if resultado['ok']:
            return redirect(url_for('facturacion_index', id_abierta=id_propuesta))
        else:
            ordenes = facturacion_service.obtener_todas_oc()
            return render_template('facturacion/factura_nueva.html', error=resultado['error'], datos=datos,
                                   ordenes=ordenes)

    #ordenes = facturacion_service.obtener_todas_oc()
    #id_propuesta = request.args.get("id_propuesta", "")
    #return render_template('facturacion/factura_nueva.html', ordenes=ordenes, id_propuesta=id_propuesta)

    id_propuesta = request.args.get("id_propuesta", "")
    todas_las_oc = facturacion_service.obtener_todas_oc()
    ordenes_filtradas = [oc for oc in todas_las_oc if oc["id_propuesta"] == id_propuesta]

    return render_template('facturacion/factura_nueva.html',
                           ordenes=ordenes_filtradas,
                           id_propuesta=id_propuesta)


@app.route("/facturacion")
def vista_facturacion():
    propuestas = obtener_propuestas_booking()
    ordenes, facturas = obtener_todo_facturacion()
    resumen = obtener_resumen_facturacion()

    return render_template("facturacion_index.html", propuestas=propuestas, ordenes=ordenes, facturas=facturas,
                           resumen=resumen)


@app.route("/facturacion/propuesta/<string:id_propuesta>")
def facturacion_por_propuesta(id_propuesta):
    ordenes = facturacion_service.obtener_todas_oc()
    facturas = facturacion_service.obtener_todo_facturacion()[1]

    ordenes_filtradas = [oc for oc in ordenes if oc["id_propuesta"] == id_propuesta]
    ids_oc = [oc["id_oc"] for oc in ordenes_filtradas]
    facturas_filtradas = [f for f in facturas if f["id_oc"] in ids_oc]
    propuesta = leer_propuestas({"id": id_propuesta})[0]

    # 🔍 Cálculo de montos facturados por OC
    mapa_facturas_por_oc = {}
    for f in facturas_filtradas:
        id_oc = f["id_oc"]
        monto = float(f["monto_factura"] or 0)
        mapa_facturas_por_oc[id_oc] = mapa_facturas_por_oc.get(id_oc, 0) + monto


    ordenes_con_montos = []
    for oc in ordenes_filtradas:
        oc_dict = dict(oc)  # ✅ Convierte Row a dict
        monto_oc = float(oc_dict["monto_oc"] or 0)
        facturado = mapa_facturas_por_oc.get(oc_dict["id_oc"], 0)
        pendiente = max(0, monto_oc - facturado)
        oc_dict["monto_facturado"] = facturado
        oc_dict["monto_pendiente"] = pendiente
        ordenes_con_montos.append(oc_dict)

    if request.args.get("ajax") == "1":

        return render_template(
            "facturacion/facturacion_detalles_parcial.html",
            ordenes=ordenes_con_montos,  # ✅ usa los dicts
            facturas=facturas_filtradas,
            id_propuesta=id_propuesta,
            propuesta=propuesta
        )

    return render_template("facturacion/facturacion_por_propuesta.html",
                           id_propuesta=id_propuesta,
                           ordenes=ordenes_filtradas,
                           facturas=facturas_filtradas,
                           propuesta=propuesta)




@app.route("/facturacion/oc/editar/<int:id_oc>", methods=["GET", "POST"])
def editar_oc(id_oc):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ordenes_compra WHERE id_oc = ?", (id_oc,))
    oc = cursor.fetchone()
    if not oc:
        conn.close()
        return "Orden de compra no encontrada", 404

    if request.method == "POST":
        cursor.execute("""
            UPDATE ordenes_compra
            SET nro_oc = ?, fecha_oc = ?, monto_oc = ?, moneda = ?, pm_asignado = ?
            WHERE id_oc = ?
        """, (
            request.form["nro_oc"],
            request.form["fecha_oc"],
            request.form["monto_oc"],
            request.form["moneda"],
            request.form["pm_asignado"],
            id_oc
        ))
        conn.commit()
        conn.close()
        id_propuesta = request.form["id_propuesta"]

        ordenes = facturacion_service.obtener_todas_oc()
        facturas = facturacion_service.obtener_todo_facturacion()[1]
        ordenes_filtradas = [oc for oc in ordenes if oc["id_propuesta"] == id_propuesta]
        ids_oc = [oc["id_oc"] for oc in ordenes_filtradas]
        facturas_filtradas = [f for f in facturas if f["id_oc"] in ids_oc]
        propuesta = leer_propuestas({"id": id_propuesta})[0]


        # 🔍 Cálculo de montos facturados por OC
        mapa_facturas_por_oc = {}
        for f in facturas_filtradas:
            id_oc = f["id_oc"]
            monto = float(f["monto_factura"] or 0)
            mapa_facturas_por_oc[id_oc] = mapa_facturas_por_oc.get(id_oc, 0) + monto

        ordenes_con_montos = []
        for oc in ordenes_filtradas:
            oc_dict = dict(oc)  # ✅ convertir de sqlite3.Row a dict
            monto_oc = float(oc_dict["monto_oc"] or 0)
            facturado = mapa_facturas_por_oc.get(oc_dict["id_oc"], 0)
            pendiente = max(0, monto_oc - facturado)
            oc_dict["monto_facturado"] = facturado
            oc_dict["monto_pendiente"] = pendiente
            ordenes_con_montos.append(oc_dict)

        return render_template("facturacion/facturacion_detalles_parcial.html",
                               ordenes=ordenes_con_montos,
                               facturas=facturas_filtradas,
                               id_propuesta=id_propuesta,
                               propuesta=propuesta)

    conn.close()
    return render_template("facturacion/oc_editar.html", oc=oc)


@app.route('/facturacion/factura/editar/<int:id_factura>', methods=['GET', 'POST'])
def editar_factura(id_factura):
    if request.method == 'POST':
        id_propuesta = request.form["id_propuesta"]
        monto = request.form["monto_factura"]
        fecha = request.form["fecha_factura"]
        nro_factura = request.form["nro_factura"]

        actualizar_factura(id_factura, fecha, monto, nro_factura)

        # Obtener datos actualizados


        ordenes_filtradas = leer_ordenes_compra(id_propuesta)
        facturas_filtradas = leer_facturas(id_propuesta)
        propuesta = leer_propuestas({"id": id_propuesta})[0]

        # 🔍 Cálculo de montos facturados por OC
        mapa_facturas_por_oc = {}
        for f in facturas_filtradas:
            id_oc = f["id_oc"]
            monto = float(f["monto_factura"] or 0)
            mapa_facturas_por_oc[id_oc] = mapa_facturas_por_oc.get(id_oc, 0) + monto


        ordenes_con_montos = []
        for oc in ordenes_filtradas:
            oc_dict = dict(oc)  # ✅ convertir de sqlite3.Row a dict
            monto_oc = float(oc_dict["monto_oc"] or 0)
            facturado = mapa_facturas_por_oc.get(oc_dict["id_oc"], 0)
            pendiente = max(0, monto_oc - facturado)
            oc_dict["monto_facturado"] = facturado
            oc_dict["monto_pendiente"] = pendiente
            ordenes_con_montos.append(oc_dict)

        return render_template("facturacion/facturacion_detalles_parcial.html",
                               ordenes=ordenes_con_montos,
                               facturas=facturas_filtradas,
                               id_propuesta=id_propuesta,
                               propuesta=propuesta)


    # GET
    factura = obtener_factura(id_factura)
    id_propuesta = request.args.get("id_propuesta")
    # Obtener nro_oc de la OC asociada
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nro_oc FROM ordenes_compra WHERE id_oc = ?", (factura["id_oc"],))
    row_oc = cursor.fetchone()
    conn.close()

    nro_oc = row_oc["nro_oc"] if row_oc else "?"


    return render_template("facturacion/factura_editar.html",
                           factura=factura,
                           id_propuesta=id_propuesta,
                           nro_oc=nro_oc)


def actualizar_factura(id_factura, fecha, monto, nro_factura):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE facturas
        SET fecha_factura = ?, monto_factura = ?, nro_factura = ?
        WHERE id_factura = ?
    """, (fecha, monto, nro_factura, id_factura))
    conn.commit()
    conn.close()


def obtener_factura(id_factura):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facturas WHERE id_factura = ?", (id_factura,))
    factura = cursor.fetchone()
    conn.close()
    return factura


@app.route("/facturacion/reporte_facturas/excel")
def descargar_reporte_facturas_excel():
    import io
    import xlsxwriter
    from flask import send_file, request

    # 1. Leer filtros y orden
    filtros = request.args.to_dict()
    sort = filtros.get("sort")
    order = filtros.get("order", "asc")
    reverse = order == "desc"

    # 2. Obtener datos y convertir
    ordenes, facturas = facturacion_service.obtener_todo_facturacion()
    ordenes_dict = {str(oc["id_oc"]): dict(oc) for oc in ordenes}
    propuestas = {p.id: p for p in leer_propuestas(pagina=1, filas_por_pagina=10000)}

    # 3. Construir el reporte (igual que en facturacion_reporte_facturas)
    reporte = []
    for f in facturas:
        f = dict(f)
        id_oc = str(f.get("id_oc", ""))
        nro_factura = f.get("nro_factura", "")
        fecha_factura = f.get("fecha_factura", "")
        monto = float(f.get("monto_factura") or f.get("monto") or f.get("monto_sin_igv") or 0)

        oc = ordenes_dict.get(id_oc)
        if not oc:
            continue

        moneda = (oc.get("moneda") or "S/").strip()
        propuesta = propuestas.get(oc["id_propuesta"])
        if not propuesta:
            continue

        reporte.append({
            "nro_factura": nro_factura,
            "fecha_factura": fecha_factura,
            "nro_oc": oc.get("nro_oc", ""),
            "id_propuesta": propuesta.id,
            "cliente": propuesta.cliente,
            "cliente_final": propuesta.cliente_final,
            "nombre_oportunidad": propuesta.nombre_oportunidad,
            "monto_soles": monto if moneda == "S/" else 0.0,
            "monto_dolares": monto if moneda == "US$" else 0.0
        })

    # 4. Filtros
    def coincide(fila, campo, valor):
        return valor.lower() in fila.get(campo, "").lower()

    def rango_fecha_ok(fila):
        desde = filtros.get("fecha_desde")
        hasta = filtros.get("fecha_hasta")
        fecha = fila.get("fecha_factura", "")
        return (not desde or fecha >= desde) and (not hasta or fecha <= hasta)

    for campo in ["nro_factura", "nro_oc", "id_propuesta", "cliente", "cliente_final", "nombre_oportunidad"]:
        if filtros.get(campo):
            reporte = [r for r in reporte if coincide(r, campo, filtros[campo])]

    reporte = [r for r in reporte if rango_fecha_ok(r)]

    # 5. Ordenamiento
    if sort:
        try:
            if sort in ["monto_soles", "monto_dolares"]:
                reporte.sort(key=lambda x: float(x.get(sort, 0)), reverse=reverse)
            else:
                reporte.sort(key=lambda x: (x.get(sort) or "").lower(), reverse=reverse)
        except Exception:
            pass

    # 6. Exportar a Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Reporte de Facturas")

    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '#,##0.00'})
    string_bold = workbook.add_format({'bold': True})

    headers = [
        "Número de Factura", "Fecha de Factura", "Número de OC", "ID Oportunidad",
        "Cliente", "Cliente Final", "Nombre de la Oportunidad", "Monto S/", "Monto US$"
    ]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, bold)

    total_soles = total_dolares = 0
    for row_num, r in enumerate(reporte, start=1):
        row = [
            r["nro_factura"],
            r["fecha_factura"],
            r["nro_oc"],
            r["id_propuesta"],
            r["cliente"],
            r["cliente_final"],
            r["nombre_oportunidad"],
            r["monto_soles"],
            r["monto_dolares"]
        ]
        total_soles += r["monto_soles"]
        total_dolares += r["monto_dolares"]

        for col_num, value in enumerate(row):
            if col_num in (7, 8):  # Montos
                worksheet.write_number(row_num, col_num, value, money)
            else:
                worksheet.write(row_num, col_num, value)

    # Fila total
    total_row = len(reporte) + 1
    worksheet.write(total_row, 6, "TOTAL GENERAL:", bold)
    worksheet.write(total_row, 7, f"S/. {total_soles:,.2f}", string_bold)
    worksheet.write(total_row, 8, f"US$ {total_dolares:,.2f}", string_bold)

    workbook.close()
    output.seek(0)

    return send_file(output,
                     download_name="reporte_facturas.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')




@app.route("/facturacion/reporte_proyectos")
def facturacion_reporte_proyectos():
    from services.propuesta_service import leer_logs_propuesta

    sort = request.args.get("sort")
    order = request.args.get("order", "asc")

    ordenes, facturas = facturacion_service.obtener_todo_facturacion()
    propuestas = leer_propuestas(filtros={}, pagina=1, filas_por_pagina=10000)

    # Agrupar OCs por propuesta
    mapa_oc_por_propuesta = {}
    for oc in ordenes:
        mapa_oc_por_propuesta.setdefault(oc["id_propuesta"], []).append(oc)

    # Agrupar facturas por OC (no usado por ahora)
    reporte = []
    for propuesta in propuestas:
        ocs = mapa_oc_por_propuesta.get(propuesta.id, [])

        total_soles = 0
        total_dolares = 0
        for oc in ocs:
            monto = oc["monto_oc"] or 0
            moneda = (oc["moneda"] if "moneda" in oc.keys() and oc["moneda"] else "").strip()
            if moneda == "S/":
                total_soles += monto
            elif moneda == "US$":
                total_dolares += monto

        # Buscar fecha de Booking desde logs
        logs = leer_logs_propuesta(propuesta.id)
        fecha_booking = ""
        for log in logs:
            if log["campo"] == "status" and log["valor_nuevo"].strip().lower() == "booking":
                fecha_booking = log["fecha"][:10]  # yyyy-mm-dd
                break

        reporte.append({
            "id_propuesta": propuesta.id,
            "cliente": propuesta.cliente,
            "cliente_final": propuesta.cliente_final,
            "nombre_oportunidad": propuesta.nombre_oportunidad,
            "fecha_booking": fecha_booking,
            "total_soles": total_soles,
            "total_dolares": total_dolares
        })

    # Ordenamiento
    if sort:
        reverse = (order == "desc")
        reporte.sort(key=lambda r: (str(r.get(sort) or "")).lower(), reverse=reverse)

    # Totales generales
    total_general_soles = sum(r["total_soles"] for r in reporte)
    total_general_dolares = sum(r["total_dolares"] for r in reporte)

    return render_template("facturacion/reporte_proyectos.html",
                           reporte=reporte,
                           mostrar_volver=True,
                           sort=sort,
                           order=order,
                           total_general_soles=total_general_soles,
                           total_general_dolares=total_general_dolares)


@app.route('/reporte/facturas')
def facturacion_reporte_facturas():
    filtros = request.args.to_dict()
    pagina = int(request.args.get("pagina", 1))
    por_pagina = 50
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")
    reverse = order == "desc"

    # 🔁 Obtener datos y convertir a dict para evitar errores con sqlite3.Row
    ordenes, facturas = facturacion_service.obtener_todo_facturacion()
    ordenes_dict = {str(oc["id_oc"]): dict(oc) for oc in ordenes}
    propuestas = {p.id: p for p in leer_propuestas(pagina=1, filas_por_pagina=10000)}

    # 🔄 Construir reporte sin aplicar filtros todavía
    reporte = []
    for f in facturas:
        f = dict(f)
        id_oc = str(f.get("id_oc", ""))
        nro_factura = f.get("nro_factura", "")
        fecha_factura = f.get("fecha_factura", "")
        monto = float(f.get("monto_factura") or f.get("monto") or f.get("monto_sin_igv") or 0)

        oc = ordenes_dict.get(id_oc)
        if not oc:
            continue

        moneda = (oc.get("moneda") or "S/").strip()

        propuesta = propuestas.get(oc["id_propuesta"])
        if not propuesta:
            continue

        reporte.append({
            "nro_factura": nro_factura,
            "fecha_factura": fecha_factura,
            "nro_oc": oc.get("nro_oc", ""),
            "id_propuesta": propuesta.id,
            "cliente": propuesta.cliente,
            "cliente_final": propuesta.cliente_final,
            "nombre_oportunidad": propuesta.nombre_oportunidad,
            "monto_soles": monto if moneda == "S/" else 0.0,
            "monto_dolares": monto if moneda == "US$" else 0.0
        })

    # 🔍 Filtros después de construir el reporte
    def coincide(fila, campo, valor):
        return valor.lower() in fila.get(campo, "").lower()

    def rango_fecha_ok(fila):
        desde = filtros.get("fecha_desde")
        hasta = filtros.get("fecha_hasta")
        fecha = fila.get("fecha_factura", "")
        return (not desde or fecha >= desde) and (not hasta or fecha <= hasta)

    for campo in ["nro_factura", "nro_oc", "id_propuesta", "cliente", "cliente_final", "nombre_oportunidad"]:
        if filtros.get(campo):
            reporte = [r for r in reporte if coincide(r, campo, filtros[campo])]

    reporte = [r for r in reporte if rango_fecha_ok(r)]

    # Ordenamiento
    if sort:
        try:
            if sort in ["monto_soles", "monto_dolares"]:
                reporte.sort(key=lambda x: float(x.get(sort, 0)), reverse=reverse)
            else:
                reporte.sort(key=lambda x: (x.get(sort) or "").lower(), reverse=reverse)
        except Exception:
            pass

    # Totales y paginación
    total_general_soles = sum(r["monto_soles"] for r in reporte)
    total_general_dolares = sum(r["monto_dolares"] for r in reporte)

    total_paginas = (len(reporte) + por_pagina - 1) // por_pagina
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    reporte_paginado = reporte[inicio:fin]

    return render_template("facturacion/reporte_facturas.html",
                           reporte=reporte_paginado,
                           pagina=pagina,
                           por_pagina=por_pagina,
                           total_paginas=total_paginas,
                           sort=sort,
                           order=order,
                           total_general_soles=total_general_soles,
                           total_general_dolares=total_general_dolares)




@app.route("/facturacion/reporte_proyectos/excel")
def descargar_reporte_proyectos_excel():
    import io
    import xlsxwriter
    from flask import send_file, request
    from datetime import datetime

    ordenes, facturas = facturacion_service.obtener_todo_facturacion()
    propuestas = leer_propuestas(filtros={}, pagina=1, filas_por_pagina=10000)
    logs_por_id = facturacion_service.obtener_logs_por_propuesta()  # Debes implementar esta función si aún no existe

    mapa_oc_por_propuesta = {}
    for oc in ordenes:
        mapa_oc_por_propuesta.setdefault(oc["id_propuesta"], []).append(oc)

    # Preparar datos
    data = []
    total_soles = 0
    total_dolares = 0

    for propuesta in propuestas:
        ocs = mapa_oc_por_propuesta.get(propuesta.id, [])

        soles = 0
        dolares = 0
        for oc in ocs:
            monto = oc["monto_oc"] or 0
            moneda = oc["moneda"] if isinstance(oc, dict) else oc["moneda"]
            if moneda == "S/":
                soles += monto
            elif moneda == "US$":
                dolares += monto

        fecha_booking = ""
        for log in logs_por_id.get(propuesta.id, []):
            if log["campo"] == "status" and log["valor_nuevo"] == "Booking":
                fecha_booking = datetime.strptime(log["fecha"][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
                break

        data.append([
            propuesta.id,
            propuesta.cliente,
            propuesta.cliente_final,
            propuesta.nombre_oportunidad,
            fecha_booking,
            soles,
            dolares
        ])
        total_soles += soles
        total_dolares += dolares

    # 🔃 Ordenamiento si corresponde
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")
    reverse = (order == "desc")

    if sort:
        if sort == "fecha_booking":
            def parse_fecha(f):
                try:
                    return datetime.strptime(f[4], "%d/%m/%Y")
                except:
                    return datetime.min
            data.sort(key=parse_fecha, reverse=reverse)
        elif sort in ["total_soles", "total_dolares"]:
            col_index = 5 if sort == "total_soles" else 6
            data.sort(key=lambda r: r[col_index], reverse=reverse)
        else:
            # Orden alfabético
            headers = ["id_propuesta", "cliente", "cliente_final", "nombre_oportunidad"]
            if sort in headers:
                col_index = headers.index(sort)
                data.sort(key=lambda r: r[col_index].lower(), reverse=reverse)

    # Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Reporte de Proyectos")

    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '#,##0.00'})
    money_bold = workbook.add_format({'num_format': '#,##0.00', 'bold': True})

    headers = [
        "ID Oportunidad", "Cliente", "Cliente Final", "Nombre de la Oportunidad",
        "Fecha Booking", "Total S/", "Total US$"
    ]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, bold)

    for row_num, row_data in enumerate(data, start=1):
        for col_num, value in enumerate(row_data):
            if col_num in (5, 6):
                worksheet.write(row_num, col_num, value, money)
            else:
                worksheet.write(row_num, col_num, value)

    # Total general
    total_row = len(data) + 1
    worksheet.write(total_row, 4, "TOTAL GENERAL:", bold)
    worksheet.write(total_row, 5, total_soles, money_bold)
    worksheet.write(total_row, 6, total_dolares, money_bold)

    workbook.close()
    output.seek(0)
    return send_file(output,
                     download_name="reporte_proyectos.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route("/facturacion/importar_xml", methods=["GET", "POST"])
def importar_factura_xml():
    if request.method == "POST":
        archivo = request.files.get("archivo_xml")
        if not archivo:
            return render_template("facturacion/importar_factura_xml.html", error="No se subió ningún archivo", datos=None)



        try:
            tree = ET.parse(archivo)
            root = tree.getroot()

            ns = {
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            }

            nro_factura = root.findtext("cbc:ID", default="", namespaces=ns)
            fecha = root.findtext("cbc:IssueDate", default="", namespaces=ns)
            nro_oc = root.find("cac:OrderReference/cbc:ID", ns)
            monto_sin_igv = root.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", ns)

            data = {
                "nro_factura": nro_factura,
                "fecha_factura": fecha,
                "nro_oc": nro_oc.text if nro_oc is not None else "",
                "monto_factura": monto_sin_igv.text if monto_sin_igv is not None else "",
                "id_propuesta": ""
            }

            return render_template("facturacion/importar_factura_xml.html", datos=data)

        except Exception as e:
            return render_template("facturacion/importar_factura_xml.html", error=f"Error al procesar el XML: {e}", datos=None)

    return render_template("facturacion/importar_factura_xml.html", datos=None)




@app.route("/facturacion/registrar_factura_xml", methods=["POST"])
def registrar_factura_desde_xml():
    id_propuesta = request.form.get("id_propuesta")
    nro_oc = request.form.get("nro_oc")
    nro_factura = request.form.get("nro_factura")
    fecha_factura = request.form.get("fecha_factura")
    monto_factura = request.form.get("monto_factura")

    # Verificar si ya existe una factura con ese número
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM facturas WHERE nro_factura = ?", (nro_factura,))
    existe = cursor.fetchone()["total"]

    if existe > 0:
        conn.close()
        return render_template("facturacion/error_factura_xml.html",
                               mensaje=f"Ya existe una factura con el número {nro_factura}")

    # Validar que el número de OC pertenezca a la oportunidad indicada
    cursor.execute("SELECT id_oc FROM ordenes_compra WHERE nro_oc = ? AND id_propuesta = ?", (nro_oc, id_propuesta))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return render_template("facturacion/error_factura_xml.html",
                               mensaje=f"❌ La OC {nro_oc} no pertenece a la oportunidad {id_propuesta}")

    id_oc = row["id_oc"]

    datos = {
        "id_oc": id_oc,
        "nro_factura": nro_factura,
        "fecha_factura": fecha_factura,
        "monto_factura": monto_factura
    }

    resultado = facturacion_service.crear_factura(datos)

    if resultado['ok']:
        return redirect(url_for('facturacion_index', id_abierta=id_propuesta))
    else:
        return render_template("facturacion/error_factura_xml.html", mensaje=resultado['error'])


def puede_editar_propuesta(propuesta):
    rol = session.get("rol")
    usuario = session.get("nombre")

    # Siempre puede editar si es administrador
    if rol == "administrador":
        return True

    # Si está en Booking, nadie más puede editarla
    if propuesta.status.strip().lower() == "booking":
        return False

    if rol in ["gerente", "director"]:
        return True
    if rol == "preventa" and propuesta.preventa_asignado == usuario:
        return True
    if rol == "account_manager" and propuesta.account_manager == usuario:
        return True

    return False


@app.route("/facturacion/importar_nc_xml", methods=["GET", "POST"])
def importar_nc_xml():
    if request.method == "POST":
        archivo = request.files.get("archivo_xml")
        if not archivo:
            return render_template("facturacion/importar_nc_xml.html", error="No se subió ningún archivo", datos=None)

        try:
            tree = ET.parse(archivo)
            root = tree.getroot()

            ns = {
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            }

            nro_nc = root.findtext("cbc:ID", default="", namespaces=ns)
            fecha_nc = root.findtext("cbc:IssueDate", default="", namespaces=ns)
            monto = root.findtext("cac:LegalMonetaryTotal/cbc:PayableAmount", default="", namespaces=ns)
            factura_afectada_raw = root.findtext("cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", default="", namespaces=ns)

            factura_afectada = factura_afectada_raw.replace(" ", "").strip()  # Normaliza

            # Buscar en BD
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_oc FROM facturas WHERE nro_factura = ?", (factura_afectada,))
            row = cursor.fetchone()
            conn.close()

            if row:
                id_oc = row["id_oc"]
                cursor = get_db_connection().cursor()
                cursor.execute("SELECT id_propuesta FROM ordenes_compra WHERE id_oc = ?", (id_oc,))
                p_row = cursor.fetchone()
                id_propuesta = p_row["id_propuesta"] if p_row else ""
            else:
                id_propuesta = ""

            datos = {
                "nro_nc": nro_nc,
                "factura_afectada": factura_afectada,
                "fecha_nc": fecha_nc,
                "monto_nc": monto,
                "id_propuesta": id_propuesta
            }

            return render_template("facturacion/importar_nc_xml.html", datos=datos)

        except Exception as e:
            return render_template("facturacion/importar_nc_xml.html", error=f"Error al procesar el XML: {e}", datos=None)

    return render_template("facturacion/importar_nc_xml.html", datos=None)


@app.route("/facturacion/registrar_nc_desde_xml", methods=["POST"])
def registrar_nc_desde_xml():
    nro_nc = request.form.get("nro_nc")
    factura_afectada = request.form.get("factura_afectada").replace(" ", "").strip()
    fecha_nc = request.form.get("fecha_nc")
    monto_nc = request.form.get("monto_nc")
    id_propuesta = request.form.get("id_propuesta")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Validar duplicado
    cursor.execute("SELECT COUNT(*) as total FROM facturas WHERE nro_factura = ?", (nro_nc,))
    if cursor.fetchone()["total"] > 0:
        conn.close()
        return render_template("facturacion/error_factura_xml.html",
                               mensaje=f"❌ Ya existe una nota de crédito con el número {nro_nc}")

    # Buscar factura afectada
    cursor.execute("SELECT id_oc FROM facturas WHERE nro_factura = ?", (factura_afectada,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template("facturacion/error_factura_xml.html",
                               mensaje=f"❌ No se encontró la factura afectada {factura_afectada}")

    id_oc = row["id_oc"]

    # Insertar nota de crédito como factura negativa
    datos = {
        "id_oc": id_oc,
        "nro_factura": nro_nc,
        "fecha_factura": fecha_nc,
        "monto_factura": -abs(float(monto_nc or 0))  # ⚠️ negativo
    }

    resultado = facturacion_service.crear_nota_credito(datos)

    if resultado["ok"]:
        return redirect(url_for("facturacion_index", id_abierta=id_propuesta))
    else:
        return render_template("facturacion/error_factura_xml.html", mensaje=resultado["error"])

from functools import wraps
from flask import redirect, url_for, session



@app.route("/admin/recargar_oc", methods=["GET"])
def recargar_ordenes_compra():
    if session.get("rol") != "administrador":
        return "Acceso denegado", 403

    try:
        print("📦 Ejecutando carga de OC desde Excel...")
        from cargar_ordenes_compra_excel import cargar_ordenes_compra_desde_excel
        total = cargar_ordenes_compra_desde_excel(confirmar=False)
        flash(f"✅ Se cargaron {total} órdenes de compra desde Excel.", "success")
    except Exception as e:
        flash(f"❌ Error al recargar órdenes de compra: {e}", "error")

    return redirect(url_for("index"))



app.jinja_env.globals.update(tiene_permiso=tiene_permiso)
app.jinja_env.globals.update(puede_editar_propuesta=puede_editar_propuesta)
app.jinja_env.filters['datetimeformat'] = lambda value, format='%d/%m/%Y': datetime.strptime(value, "%Y-%m-%d").strftime(format) if value else ''


if __name__ == "__main__":
    app.run(debug=True)
