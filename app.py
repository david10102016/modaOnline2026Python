from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import json
import uuid
from datetime import datetime
import urllib.parse
from database import get_db_connection, init_database, hash_password, check_password
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura_2024'

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/images/productos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Crear carpetas de imágenes si no existen
def create_upload_folders():
    folders = [
        'static/images/productos',
        'static/images/productos/hombres',
        'static/images/productos/mujeres', 
        'static/images/productos/ninos',
        'static/images/productos/ofertas'
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

# Crear carpetas al iniciar
create_upload_folders()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializar base de datos al iniciar
def initialize():
    init_database()
    try:
        from init_db import populate_database
        populate_database()
    except Exception as e:
        pass  # Si ya está poblada

# Registrar la función de inicialización para que se ejecute antes de la primera petición
with app.app_context():
    initialize()

# Funciones de validación
def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

import re

import re

def validar_telefono_bolivia(telefono):
    if not telefono:
        return False
    # Eliminar el código de país (+591) si está presente
    if telefono.startswith('+591'):
        telefono = telefono[4:]
    # Patrón para 7 u 8 dígitos, comenzando con 6, 7 u 8
    patron = r'^[678]\d{6,7}$'
    if re.match(patron, telefono) is None:
        return False
    return True

def validar_contraseña(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def validar_nombre(nombre):
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    return re.match(patron, nombre) is not None

# ========== RUTAS ORIGINALES (SIN CAMBIOS) ==========

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Consulta de productos (código existente)
    query = '''
        SELECT p.*, c.nombre as categoria_nombre, c.tipo as categoria_tipo
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
        ORDER BY c.tipo, c.nombre, p.nombre
    '''
    productos = conn.execute(query).fetchall()
    
    # Organizar productos (código existente)
    productos_organizados = {
        'hombres': [],
        'mujeres': [],
        'ninos': [],
        'ofertas': []
    }
    for producto in productos:
        productos_organizados[producto['categoria_tipo']].append(producto)
    
    # Obtener categorías (código existente)
    categorias = conn.execute('SELECT * FROM categorias ORDER BY tipo, nombre').fetchall()
    
    # ✅ Obtener comentarios aprobados con nombres de columna CORRECTOS
    comentarios_rows = conn.execute('''
    SELECT c.*, u.nombre as usuario_nombre
    FROM comentarios c
    JOIN usuarios u ON c.usuario_id = u.id
    WHERE c.aprobado = 1 AND c.producto_id IS NULL
    ORDER BY c.fecha DESC
    LIMIT 5
''').fetchall()
    
    # ✅ Convertir Row objects a diccionarios - usando "calificacion" no "puntuacion"
    comentarios_aprobados = []
    for row in comentarios_rows:
        comentarios_aprobados.append({
            'id': row['id'],
            'usuario_id': row['usuario_id'],
            'producto_id': row['producto_id'],
            'puntuacion': row['calificacion'],  # ✅ AQUÍ ESTÁ EL CAMBIO: calificacion -> puntuacion para el frontend
            'comentario': row['comentario'],
            'fecha': row['fecha'],
            'aprobado': row['aprobado'],
            'usuario_nombre': row['usuario_nombre'],
        })
    
    conn.close()
    
    return render_template('index.html', 
                         productos_organizados=productos_organizados,
                         categorias=categorias,
                         comentarios_aprobados=comentarios_aprobados)

@app.route('/agregar_comentario_tienda', methods=['POST'])
def agregar_comentario_tienda():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'})
    
    calificacion = request.form.get('calificacion')
    comentario = request.form.get('comentario')
    
    if not calificacion or not comentario:
        return jsonify({'success': False, 'message': 'Faltan datos'})
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO comentarios (usuario_id, producto_id, calificacion, comentario, aprobado)
        VALUES (?, NULL, ?, ?, ?)
    ''', (session['user_id'], calificacion, comentario, 1 if int(calificacion) >= 4 else 0))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Comentario sobre la tienda enviado'})  

@app.route('/producto/<int:producto_id>')
def detalle_producto(producto_id):
    conn = get_db_connection()
    producto = conn.execute('''
        SELECT p.*, c.nombre as categoria_nombre, c.tipo as categoria_tipo
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ? AND p.activo = 1
    ''', (producto_id,)).fetchone()
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('index'))
    
    # Mostrar comentarios aprobados y, si el usuario está logueado, también mostrar
    # los comentarios propios del usuario aunque estén pendientes de aprobación.
    usuario_id = session.get('user_id')
    if usuario_id:
        comentarios = conn.execute('''
            SELECT c.*, u.nombre as usuario_nombre
            FROM comentarios c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.producto_id = ? AND (c.aprobado = 1 OR c.usuario_id = ?)
            ORDER BY c.fecha DESC
        ''', (producto_id, usuario_id)).fetchall()
    else:
        comentarios = conn.execute('''
            SELECT c.*, u.nombre as usuario_nombre
            FROM comentarios c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.producto_id = ? AND c.aprobado = 1
            ORDER BY c.fecha DESC
        ''', (producto_id,)).fetchall()
    
    relacionados = conn.execute('''
        SELECT * FROM productos
        WHERE categoria_id = ? AND id != ? AND activo = 1
        LIMIT 4
    ''', (producto['categoria_id'], producto_id)).fetchall()
    
    conn.close()
    
    return render_template('producto.html', 
                         producto=producto,
                         comentarios=comentarios,
                         relacionados=relacionados)

@app.route('/buscar')
def buscar():
    query = request.args.get('q', '')
    categoria = request.args.get('categoria', '')
    
    conn = get_db_connection()
    sql = '''
        SELECT p.*, c.nombre as categoria_nombre, c.tipo as categoria_tipo
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
    '''
    params = []
    
    if query:
        sql += ' AND (p.nombre LIKE ? OR p.descripcion LIKE ?)'
        params.extend([f'%{query}%', f'%{query}%'])
    
    if categoria:
        sql += ' AND c.tipo = ?'
        params.append(categoria)
    
    sql += ' ORDER BY p.nombre'
    resultados = conn.execute(sql, params).fetchall()
    categorias = conn.execute('SELECT DISTINCT tipo FROM categorias').fetchall()
    conn.close()
    
    return render_template('buscar.html',
                         resultados=resultados,
                         categorias=categorias,
                         query=query,
                         categoria_seleccionada=categoria)

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ? AND activo = 1', 
                           (producto_id,)).fetchone()
    
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'})
    
    usuario_id = session.get('user_id')
    session_id = get_session_id()
    
    if usuario_id:
        existente = conn.execute(
            'SELECT * FROM carrito WHERE usuario_id = ? AND producto_id = ?',
            (usuario_id, producto_id)
        ).fetchone()
    else:
        existente = conn.execute(
            'SELECT * FROM carrito WHERE session_id = ? AND producto_id = ?',
            (session_id, producto_id)
        ).fetchone()
    
    if existente:
        nueva_cantidad = existente['cantidad'] + cantidad
        conn.execute(
            'UPDATE carrito SET cantidad = ? WHERE id = ?',
            (nueva_cantidad, existente['id'])
        )
    else:
        conn.execute('''
            INSERT INTO carrito (usuario_id, producto_id, cantidad, precio_unitario, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, producto_id, cantidad, producto['precio'], session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Producto agregado al carrito'})

@app.route('/carrito')
def carrito():
    conn = get_db_connection()
    
    usuario_id = session.get('user_id')
    session_id = get_session_id()
    
    if usuario_id:
        items = conn.execute('''
            SELECT c.*, p.nombre, p.imagen, p.precio as precio_actual
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = ?
            ORDER BY c.fecha DESC
        ''', (usuario_id,)).fetchall()
    else:
        items = conn.execute('''
            SELECT c.*, p.nombre, p.imagen, p.precio as precio_actual
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.session_id = ?
            ORDER BY c.fecha DESC
        ''', (session_id,)).fetchall()
    
    total = sum(item['precio_unitario'] * item['cantidad'] for item in items)
    
    conn.close()
    
    return render_template('carrito.html', items=items, total=total)

@app.route('/api/carrito/count')
def get_carrito_count():
    conn = get_db_connection()
    usuario_id = session.get('user_id')
    session_id = get_session_id()
    
    if usuario_id:
        count = conn.execute('''
            SELECT SUM(cantidad) FROM carrito WHERE usuario_id = ?
        ''', (usuario_id,)).fetchone()[0]
    else:
        count = conn.execute('''
            SELECT SUM(cantidad) FROM carrito WHERE session_id = ?
        ''', (session_id,)).fetchone()[0]
    
    conn.close()
    return jsonify({'count': count or 0})

@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    item_id = request.form.get('item_id')
    cantidad = int(request.form.get('cantidad'))
    
    if cantidad <= 0:
        return redirect(url_for('eliminar_carrito', item_id=item_id))
    
    conn = get_db_connection()
    conn.execute('UPDATE carrito SET cantidad = ? WHERE id = ?', (cantidad, item_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('carrito'))

@app.route('/eliminar_carrito/<int:item_id>')
def eliminar_carrito(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM carrito WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('carrito'))

@app.route('/checkout')
def checkout():
    conn = get_db_connection()
    
    usuario_id = session.get('user_id')
    session_id = get_session_id()
    
    if usuario_id:
        items = conn.execute('''
            SELECT c.*, p.nombre
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = ?
        ''', (usuario_id,)).fetchall()
    else:
        items = conn.execute('''
            SELECT c.*, p.nombre
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.session_id = ?
        ''', (session_id,)).fetchall()
    
    if not items:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))

    total = sum(item['precio_unitario'] * item['cantidad'] for item in items)
    
    usuario = None
    if usuario_id:
        usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
    
    conn.close()
    
    return render_template('checkout.html', items=items, total=total, usuario=usuario)

@app.route('/procesar_pedido', methods=['POST'])
def procesar_pedido():
    # Obtener datos del formulario
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    metodo_entrega = request.form.get('metodo_entrega')
    direccion = request.form.get('direccion', '').strip() if metodo_entrega == 'envio' else None
    ciudad = request.form.get('ciudad', '').strip() if metodo_entrega == 'envio' else None
    metodo_pago = request.form.get('metodo_pago')
    facturar = request.form.get('facturar') == 'on'
    nit = request.form.get('nit', '').strip() if facturar else None
    ci = request.form.get('ci', '').strip() if facturar else None

    # Validaciones
    if not validar_nombre(nombre):
        flash('Nombre inválido. Solo se permiten letras y espacios.', 'error')
        return redirect(url_for('checkout'))
    if not validar_telefono_bolivia(telefono):
        flash('Teléfono inválido. Debe ser un número boliviano válido.', 'error')
        return redirect(url_for('checkout'))
    if not metodo_entrega or (metodo_entrega == 'envio' and (not direccion or not ciudad)):
        flash('Selecciona un método de entrega válido y completa los datos si es envío.', 'error')
        return redirect(url_for('checkout'))
    if metodo_pago not in ['tigo_money', 'qr_simple', 'whatsapp']:
        flash('Método de pago inválido.', 'error')
        return redirect(url_for('checkout'))

    conn = get_db_connection()
    usuario_id = session.get('user_id')
    session_id = get_session_id()

    # Depuración: Verificar los items del carrito
    if usuario_id:
        items = conn.execute('SELECT c.*, p.nombre, p.imagen FROM carrito c JOIN productos p ON c.producto_id = p.id WHERE c.usuario_id = ?', (usuario_id,)).fetchall()
    else:
        items = conn.execute('SELECT c.*, p.nombre, p.imagen FROM carrito c JOIN productos p ON c.producto_id = p.id WHERE c.session_id = ?', (session_id,)).fetchall()
    print(f"Items en carrito: {items}")  # Depuración

    # Verificar si el carrito está vacío
    if not items:
        flash('Tu carrito está vacío. Agrega productos antes de procesar el pedido.', 'error')
        conn.close()
        return redirect(url_for('carrito'))

    total = sum(item['precio_unitario'] * item['cantidad'] for item in items)
    envio_costo = 20.0 if metodo_entrega == 'envio' else 0.0
    total_con_envio = total + envio_costo

    detalles = {
        'items': [{'producto': item['nombre'], 'cantidad': item['cantidad'], 
                   'precio_unitario': float(item['precio_unitario']), 
                   'subtotal': float(item['precio_unitario'] * item['cantidad'])} 
                  for item in items],
        'entrega': {'metodo': metodo_entrega, 'direccion': direccion, 'ciudad': ciudad, 'costo': envio_costo},
        'facturacion': {'facturar': facturar, 'nit': nit, 'ci': ci} if facturar else None
    }

    cursor = conn.execute('INSERT INTO ordenes (usuario_id, nombre_cliente, telefono_cliente, total, metodo_pago, detalles, estado) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                         (usuario_id, nombre, telefono, total_con_envio, metodo_pago, json.dumps(detalles), 'pendiente'))
    orden_id = cursor.lastrowid

    if usuario_id:
        conn.execute('DELETE FROM carrito WHERE usuario_id = ?', (usuario_id,))
    else:
        conn.execute('DELETE FROM carrito WHERE session_id = ?', (session_id,))

    conn.commit()
    conn.close()

    # Simulación de pago y redirección
    if metodo_pago == 'tigo_money':
        flash('Pago procesado con Tigo Money. Redirigiendo al comprobante...', 'success')
        return render_template('factura.html', orden_id=orden_id, nombre=nombre, telefono=telefono, total=total_con_envio, metodo_pago=metodo_pago, detalles=detalles, estado='pendiente', tipo_documento='Comprobante', fecha=datetime.now())
    elif metodo_pago == 'qr_simple':
        flash('Pago simulado con QR Simple. Generando comprobante...', 'success')
        return render_template('factura.html', orden_id=orden_id, nombre=nombre, telefono=telefono, total=total_con_envio, metodo_pago=metodo_pago, detalles=detalles, estado='pendiente', tipo_documento='Comprobante', fecha=datetime.now())
    elif metodo_pago == 'whatsapp':
        mensaje = f"¡Hola! Quiero realizar este pedido:\n\n*Orden #{orden_id}*\n"
        for item in detalles['items']:
            mensaje += f"• {item['producto']} x{item['cantidad']} - Bs. {item['subtotal']:.2f}\n"
        mensaje += f"\n*Total: Bs. {total_con_envio:.2f}*\nCliente: {nombre}\nTeléfono: {telefono}"
        whatsapp_url = f"https://wa.me/59173138524?text={urllib.parse.quote_plus(mensaje)}"
        return redirect(whatsapp_url)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')
        
        if not validar_email(correo):
            flash('Correo electrónico inválido', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuarios WHERE correo = ?', (correo,)).fetchone()
        conn.close()
        
        if usuario and check_password(password, usuario['contraseña']):
            session['user_id'] = usuario['id']
            session['user_name'] = usuario['nombre']
            session['user_role'] = usuario['rol']
            
            migrar_carrito_sesion_a_usuario(usuario['id'])
            
            flash(f'¡Bienvenido, {usuario["nombre"]}!', 'success')
            
            if usuario['rol'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not validar_nombre(nombre):
            flash('Nombre inválido. Solo se permiten letras, espacios y acentos.', 'error')
            return render_template('login.html')
        
        if not validar_email(correo):
            flash('Correo electrónico inválido', 'error')
            return render_template('login.html')
        
        if not validar_telefono_bolivia(telefono):
            flash('Teléfono inválido. Debe ser un número boliviano válido.', 'error')
            return render_template('login.html')
        
        if not validar_contraseña(password):
            flash('Contraseña debe tener mínimo 8 caracteres, una mayúscula, minúscula, número y símbolo.', 'error')
            return render_template('login.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        
        existente = conn.execute('SELECT id FROM usuarios WHERE correo = ?', (correo,)).fetchone()
        if existente:
            flash('Ya existe una cuenta con este correo electrónico', 'error')
            conn.close()
            return render_template('login.html')
        
        hashed_password = hash_password(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contraseña, telefono, rol)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, correo, hashed_password, telefono, 'usuario'))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        session['user_id'] = user_id
        session['user_name'] = nombre
        session['user_role'] = 'usuario'
        
        migrar_carrito_sesion_a_usuario(user_id)
        
        flash('¡Cuenta creada exitosamente! Bienvenido.', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('index'))

def migrar_carrito_sesion_a_usuario(usuario_id):
    if 'session_id' not in session:
        return
    
    conn = get_db_connection()
    session_id = session['session_id']
    
    items_sesion = conn.execute(
        'SELECT * FROM carrito WHERE session_id = ? AND usuario_id IS NULL',
        (session_id,)
    ).fetchall()
    
    for item in items_sesion:
        existente = conn.execute(
            'SELECT * FROM carrito WHERE usuario_id = ? AND producto_id = ?',
            (usuario_id, item['producto_id'])
        ).fetchone()
        
        if existente:
            nueva_cantidad = existente['cantidad'] + item['cantidad']
            conn.execute(
                'UPDATE carrito SET cantidad = ? WHERE id = ?',
                (nueva_cantidad, existente['id'])
            )
        else:
            conn.execute(
                'UPDATE carrito SET usuario_id = ?, session_id = NULL WHERE id = ?',
                (usuario_id, item['id'])
            )
    
    conn.commit()
    conn.close()

@app.route('/admin')
def admin():
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Estadísticas
    total_productos = conn.execute('SELECT COUNT(*) FROM productos WHERE activo = 1').fetchone()[0]
    total_ordenes = conn.execute('SELECT COUNT(*) FROM ordenes').fetchone()[0]
    comentarios_pendientes = conn.execute('SELECT COUNT(*) FROM comentarios WHERE aprobado = 0').fetchone()[0]
    
    # Productos recientes
    rows = conn.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
        ORDER BY p.fecha_creacion DESC
        LIMIT 5
    ''').fetchall()
    productos_recientes = [dict(row) for row in rows]
    for producto in productos_recientes:
        if producto['fecha_creacion']:
            try:
                producto['fecha_creacion'] = datetime.strptime(producto['fecha_creacion'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                producto['fecha_creacion'] = None
    
    # Órdenes recientes con método de pago
    rows = conn.execute('''
        SELECT * FROM ordenes
        ORDER BY fecha DESC
        LIMIT 5
    ''').fetchall()
    ordenes_recientes = [dict(row) for row in rows]
    for orden in ordenes_recientes:
        if orden.get('fecha'):
            try:
                orden['fecha'] = datetime.strptime(orden['fecha'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                orden['fecha'] = None
    
    conn.close()
    
    return render_template('admin.html',
                          total_productos=total_productos,
                          total_ordenes=total_ordenes,
                          comentarios_pendientes=comentarios_pendientes,
                          productos_recientes=productos_recientes,
                          ordenes_recientes=ordenes_recientes)
@app.route('/productos')
def ver_productos():
    conn = get_db_connection()
    productos = conn.execute('SELECT * FROM productos WHERE activo = 1 ORDER BY fecha_creacion DESC').fetchall()
    conn.close()
    return render_template('productos.html', productos=productos)

@app.route('/ordenes')
def ver_ordenes():
    conn = get_db_connection()
    query = "SELECT * FROM ordenes"
    params = []
    
    # Aplicar filtros desde los parámetros GET
    if request.args.get('estado'):
        query += " WHERE estado = ?"
        params.append(request.args.get('estado'))
    if request.args.get('fecha_inicio'):
        query += " WHERE fecha >= ?" if not params else " AND fecha >= ?"
        params.append(request.args.get('fecha_inicio'))
    if request.args.get('fecha_fin'):
        query += " WHERE fecha <= ?" if not params else " AND fecha <= ?"
        params.append(request.args.get('fecha_fin'))
    if request.args.get('metodo_pago'):
        query += " WHERE metodo_pago = ?" if not params else " AND metodo_pago = ?"
        params.append(request.args.get('metodo_pago'))
    
    query += " ORDER BY fecha DESC"
    ordenes = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('ordenes.html', ordenes=ordenes)

@app.route('/actualizar_ordenes_masa', methods=['POST'])
def actualizar_ordenes_masa():
    if session.get('user_role') != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('admin'))
    
    conn = get_db_connection()
    ordenes_seleccionadas = request.form.getlist('ordenes_seleccionadas')
    nuevo_estado = request.form.get('nuevo_estado')
    
    # Depuración mejorada
    print(f"Request form: {dict(request.form)}")
    print(f"Ordenes seleccionadas: {ordenes_seleccionadas}")
    print(f"Nuevo estado: {nuevo_estado}")
    
    if ordenes_seleccionadas and nuevo_estado:
        try:
            conn.executemany('UPDATE ordenes SET estado = ? WHERE id = ?', [(nuevo_estado, id) for id in ordenes_seleccionadas])
            conn.commit()
            flash(f'Estado de {len(ordenes_seleccionadas)} órdenes actualizado a {nuevo_estado}.', 'success')
        except sqlite3.Error as e:
            flash(f'Error al actualizar: {str(e)}', 'error')
            conn.rollback()
    else:
        flash('Selecciona al menos una orden y un estado.', 'error')
    
    conn.close()
    return redirect(url_for('ver_ordenes'))

@app.route('/actualizar_orden/<int:orden_id>', methods=['POST'])
def actualizar_orden(orden_id):
    if session.get('user_role') != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('admin'))
    
    estado = request.form.get('estado')
    # Añadir "pagado" como estado válido
    if estado not in ['pendiente', 'procesando', 'enviado', 'completado', 'cancelado', 'pagado']:
        flash('Estado inválido', 'error')
        return redirect(url_for('ver_ordenes'))
    
    conn = get_db_connection()
    conn.execute('UPDATE ordenes SET estado = ? WHERE id = ?', (estado, orden_id))
    conn.commit()
    conn.close()
    
    flash('Estado actualizado', 'success')
    return redirect(url_for('admin'))
@app.route('/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()

    if not producto:
        flash('Producto no encontrado', 'error')
        conn.close()
        return redirect(url_for('ver_productos'))

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio')
        stock = request.form.get('stock', 100)
        categoria_id = request.form.get('categoria_id')

        # Validaciones
        if not nombre or not precio:
            flash('Nombre y precio son requeridos', 'error')
            return render_template('editar_producto.html', producto=producto)

        try:
            precio = float(precio)
            if precio <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('Precio inválido', 'error')
            return render_template('editar_producto.html', producto=producto)

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            flash('Stock inválido', 'error')
            return render_template('editar_producto.html', producto=producto)

        # Preparar campos a actualizar
        campos = {
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': precio,
            'stock': stock,
            'categoria_id': int(categoria_id) if categoria_id else None
        }

        # Manejar nueva imagen si se sube
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                categoria = conn.execute('SELECT tipo FROM categorias WHERE id = ?', (campos['categoria_id'],)).fetchone()
                subcarpeta = categoria['tipo'] if categoria else 'general'
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subcarpeta)
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                campos['imagen'] = f"/static/images/productos/{subcarpeta}/{filename}"

        # Construir y ejecutar query de actualización
        set_clauses = [f"{k} = ?" for k in campos if campos[k] is not None]
        query = f"UPDATE productos SET {', '.join(set_clauses)} WHERE id = ?"
        values = [v for v in campos.values() if v is not None] + [producto_id]
        conn.execute(query, values)
        conn.commit()

        flash('Producto actualizado exitosamente', 'success')
        conn.close()
        return redirect(url_for('editar_producto', producto_id=producto_id))

    # Obtener categorías para el formulario
    categorias = conn.execute('SELECT * FROM categorias ORDER BY tipo, nombre').fetchall()
    conn.close()
    return render_template('editar_producto.html', producto=producto, categorias=categorias)

@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto_web(producto_id):
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()

    if not producto:
        flash('Producto no encontrado', 'error')
        conn.close()
        return redirect(url_for('ver_productos'))

    conn.execute('UPDATE productos SET activo = 0 WHERE id = ?', (producto_id,))
    conn.commit()
    conn.close()

    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('ver_productos'))

@app.route('/moderar')
def moderar():
    conn = get_db_connection()
    comentarios = conn.execute('SELECT * FROM comentarios WHERE aprobado = 0 ORDER BY fecha DESC').fetchall()
    conn.close()
    return render_template('moderar.html', comentarios=comentarios)

@app.route('/agregar_comentario', methods=['POST'])
def agregar_comentario():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para comentar'})
    
    producto_id = request.form.get('producto_id')
    calificacion = int(request.form.get('calificacion'))
    comentario = request.form.get('comentario', '').strip()
    
    if calificacion < 1 or calificacion > 5:
        return jsonify({'success': False, 'message': 'Calificación inválida'})
    
    if len(comentario) > 250:
        return jsonify({'success': False, 'message': 'Comentario muy largo (máximo 250 caracteres)'})
    
    comentario = re.sub(r'<[^>]*>', '', comentario)
    
    conn = get_db_connection()
    
    producto = conn.execute('SELECT id FROM productos WHERE id = ? AND activo = 1', 
                           (producto_id,)).fetchone()
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'})
    
    aprobado = 1 if calificacion >= 4 else 0
    
    conn.execute('''
        INSERT INTO comentarios (usuario_id, producto_id, calificacion, comentario, aprobado)
        VALUES (?, ?, ?, ?, ?)
    ''', (session['user_id'], producto_id, calificacion, comentario, aprobado))
    
    conn.commit()
    conn.close()
    
    mensaje = 'Comentario agregado' if aprobado else 'Comentario enviado para moderación'
    return jsonify({'success': True, 'message': mensaje})

# ========== NUEVOS ENDPOINTS API PARA EL ADMIN ==========

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Obtener todas las categorías"""
    try:
        conn = get_db_connection()
        categorias = conn.execute('SELECT * FROM categorias ORDER BY tipo, nombre').fetchall()
        conn.close()
        
        categorias_list = []
        for categoria in categorias:
            categorias_list.append({
                'id': categoria['id'],
                'nombre': categoria['nombre'],
                'tipo': categoria['tipo']
            })
        
        return jsonify({
            'success': True,
            'categorias': categorias_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto"""
    try:
        # Verificar que el usuario es admin
        if session.get('user_role') != 'admin':
            return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
        
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        precio = request.form.get('precio')
        stock = request.form.get('stock', 100)
        categoria_id = request.form.get('categoria_id')
        
        # Validaciones
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre es requerido'}), 400
        
        if not precio:
            return jsonify({'success': False, 'error': 'El precio es requerido'}), 400
        
        try:
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'El precio debe ser un número válido mayor a 0'}), 400

        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo")
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'El stock debe ser un número válido'}), 400

        # Manejar imagen si se proporciona
        imagen_path = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Agregar timestamp para evitar conflictos
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                
                # Determinar carpeta según categoría
                conn = get_db_connection()
                if categoria_id:
                    categoria = conn.execute('SELECT tipo FROM categorias WHERE id = ?', (categoria_id,)).fetchone()
                    if categoria:
                        subcarpeta = categoria['tipo']
                    else:
                        subcarpeta = 'general'
                else:
                    subcarpeta = 'general'
                conn.close()
                
                # Crear carpeta si no existe
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subcarpeta)
                os.makedirs(upload_path, exist_ok=True)
                
                # Guardar archivo
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                imagen_path = f"/static/images/productos/{subcarpeta}/{filename}"

        # Insertar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id, imagen)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            nombre,
            descripcion,
            precio,
            stock,
            int(categoria_id) if categoria_id else None,
            imagen_path
        ))
        
        producto_id = cursor.lastrowid
        conn.commit()
        
        # Obtener el producto creado con información de categoría
        producto = conn.execute('''
            SELECT p.*, c.nombre as categoria_nombre, c.tipo as categoria_tipo
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = ?
        ''', (producto_id,)).fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Producto creado exitosamente',
            'producto': {
                'id': producto['id'],
                'nombre': producto['nombre'],
                'descripcion': producto['descripcion'],
                'precio': float(producto['precio']),
                'stock': producto['stock'],
                'categoria_id': producto['categoria_id'],
                'categoria_nombre': producto['categoria_nombre'],
                'categoria_tipo': producto['categoria_tipo'],
                'imagen': producto['imagen'],
                'fecha_creacion': producto['fecha_creacion']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al crear producto: {str(e)}'
        }), 500

@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def get_producto_details(producto_id):
    try:
        conn = get_db_connection()
        producto = conn.execute('''
            SELECT p.*, c.nombre as categoria_nombre, c.tipo as categoria_tipo
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = ?
        ''', (producto_id,)).fetchone()
        conn.close()
        
        if producto:
            return jsonify({
                'success': True,
                'producto': {
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'descripcion': producto['descripcion'],
                    'precio': float(producto['precio']),
                    'stock': producto['stock'],
                    'categoria_id': producto['categoria_id'],
                    'imagen': producto['imagen']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    try:
        if session.get('user_role') != 'admin':
            return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
        
        # Obtener datos del formulario
        data = request.form.to_dict()
        if not data.get('nombre') or not data.get('precio'):
            return jsonify({'success': False, 'error': 'Nombre y precio son requeridos'}), 400
        
        # Validar precio
        try:
            precio = float(data['precio'])
            if precio <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Precio inválido'}), 400
        
        # Validar stock
        stock = int(data.get('stock', 100)) if data.get('stock') else 100
        
        conn = get_db_connection()
        producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
        if not producto:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Preparar campos a actualizar
        campos = {
            'nombre': data.get('nombre'),
            'descripcion': data.get('descripcion'),
            'precio': precio,
            'stock': stock,
            'categoria_id': int(data.get('categoria_id')) if data.get('categoria_id') else None
        }
        
        # Manejar nueva imagen si se sube
        if 'imagen' in request.files and request.files['imagen'].filename:
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                # Determinar carpeta según categoría
                categoria = conn.execute('SELECT tipo FROM categorias WHERE id = ?', (campos['categoria_id'],)).fetchone()
                subcarpeta = categoria['tipo'] if categoria else 'general'
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subcarpeta)
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                campos['imagen'] = f"/static/images/productos/{subcarpeta}/{filename}"
        
        # Construir y ejecutar query de actualización
        set_clauses = [f"{k} = ?" for k in campos if campos[k] is not None]
        query = f"UPDATE productos SET {', '.join(set_clauses)} WHERE id = ?"
        values = [v for v in campos.values() if v is not None] + [producto_id]
        conn.execute(query, values)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Producto actualizado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Eliminar (desactivar) un producto"""
    try:
        # Verificar que el usuario es admin
        if session.get('user_role') != 'admin':
            return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
        
        conn = get_db_connection()
        
        # Verificar que el producto existe
        producto = conn.execute('SELECT * FROM productos WHERE id = ?', (producto_id,)).fetchone()
        if not producto:
            conn.close()
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Soft delete - solo desactivar
        conn.execute('UPDATE productos SET activo = 0 WHERE id = ?', (producto_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Producto eliminado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al eliminar producto: {str(e)}'
        }), 500
# ========== ENDPOINTS UAT (USER ACCEPTANCE TESTING) ==========

@app.route('/api/uat/save', methods=['POST'])
def save_uat_data():
    """Guardar datos de sesión UAT en archivo JSON"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        # Crear directorio si no existe
        uat_dir = 'data/uat_sessions'
        os.makedirs(uat_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        session_id = data.get('sessionId', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"uat_{session_id}_{timestamp}.json"
        file_path = os.path.join(uat_dir, filename)
        
        # Agregar metadatos
        data['server_timestamp'] = datetime.now().isoformat()
        data['user_session'] = session.get('user_id', 'anonymous')
        
        # Guardar archivo JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Datos UAT guardados exitosamente',
            'file': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error guardando UAT: {str(e)}'
        }), 500

@app.route('/admin/uat-results')
def admin_uat_results():
    """Dashboard administrativo para ver resultados UAT"""
    if session.get('user_role') != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect(url_for('login'))
    
    try:
        uat_dir = 'data/uat_sessions'
        
        # Verificar si existe el directorio
        if not os.path.exists(uat_dir):
            return render_template('admin_uat.html', 
                                 total_sessions=0, 
                                 sessions=[], 
                                 stats={})
        
        # Leer todos los archivos UAT
        sessions = []
        for filename in os.listdir(uat_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(uat_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        session_data['filename'] = filename
                        sessions.append(session_data)
                except Exception as e:
                    print(f"Error leyendo {filename}: {e}")
                    continue
        
        # Ordenar por timestamp
        sessions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Calcular estadísticas
        stats = calculate_uat_stats(sessions)
        
        return render_template('admin_uat.html',
                             total_sessions=len(sessions),
                             sessions=sessions,
                             stats=stats)
        
    except Exception as e:
        flash(f'Error cargando datos UAT: {str(e)}', 'error')
        return redirect(url_for('admin'))

def calculate_uat_stats(sessions):
    """Calcular estadísticas de las sesiones UAT"""
    from types import SimpleNamespace
    
    if not sessions:
        return SimpleNamespace(
            by_scenario={},
            by_success={'si': 0, 'parcial': 0, 'no': 0},
            avg_time=0,
            avg_rating=0,
            common_difficulties=[]
        )
    
    stats = {
        'by_scenario': {},
        'by_success': {'si': 0, 'parcial': 0, 'no': 0},
        'avg_time': 0,
        'avg_rating': 0,
        'common_difficulties': []
    }
    
    total_time = 0
    total_rating = 0
    difficulties = []
    
    for session in sessions:
        scenario = session.get('scenario', 'unknown')
        success = session.get('success', 'no')
        time_spent = session.get('timeSpent', 0)
        rating = session.get('rating', 0)
        difficulty = session.get('difficulties', '')
        
        # Por escenario
        if scenario not in stats['by_scenario']:
            stats['by_scenario'][scenario] = {
                'count': 0, 'success': 0, 'avg_time': 0, 'total_time': 0
            }
        
        stats['by_scenario'][scenario]['count'] += 1
        stats['by_scenario'][scenario]['total_time'] += time_spent
        stats['by_scenario'][scenario]['avg_time'] = (
            stats['by_scenario'][scenario]['total_time'] / 
            stats['by_scenario'][scenario]['count']
        )
        
        if success == 'si':
            stats['by_scenario'][scenario]['success'] += 1
        
        # Estadísticas generales
        stats['by_success'][success] += 1
        total_time += time_spent
        total_rating += rating
        
        if difficulty.strip():
            difficulties.append(difficulty.strip())
    
    # Calcular promedios
    stats['avg_time'] = total_time / len(sessions) if sessions else 0
    stats['avg_rating'] = total_rating / len(sessions) if sessions else 0
    
    # Dificultades más comunes (simplificado)
    stats['common_difficulties'] = list(set(difficulties))[:5]
    
    # Convertir diccionario a objeto
    return SimpleNamespace(**stats)

if __name__ == '__main__':
    app.run(debug=True)