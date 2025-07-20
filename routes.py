from ast import main
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app, g
from models import Libro, Categoria, Usuario, Pedido, PedidoDetalle
from database import get_db_connection
import datetime
import mysql.connector

# --- Definición de Blueprints ---

# Blueprint para rutas públicas/cliente
main_bp = Blueprint('main', __name__)

# Blueprint para rutas de administrador
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Blueprint para autenticación (login, registro, logout)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@main_bp.app_context_processor
def inject_alert():
    alert = None
    if 'alert' in session:
        alert = session.pop('alert')
    return dict(alert=alert)

# ---  SweetAlert2  ---
def set_alert(message, category='info'):

    alert_type_map = {
        'success': 'success',
        'error': 'error',
        'info': 'info',
        'warning': 'warning'
    }
    alert_data = {
        'message': message,
        'type': alert_type_map.get(category, 'info') 
    }
    session['alert'] = alert_data
    session.modified = True 
    print(f"DEBUG: Alerta guardada en sesión: {session['alert']}")

# --- Rutas del Blueprint 'main' ---

@main_bp.route('/')
def index():
    latest_books = Libro.get_latest_books(limit=8)
    popular_books = Libro.get_popular_books(limit=8)
    on_sale_books = Libro.get_on_sale_books(limit=8)
    return render_template('main/index.html', 
                            latest_books=latest_books, 
                            popular_books=popular_books, 
                            on_sale_books=on_sale_books)

@main_bp.route('/explore_books')
def explore_books():
    search_query = request.args.get('search', '').strip()
    selected_category_id = request.args.get('categoria', type=int)

    libros = Libro.get_all()
    categorias = Categoria.get_all()

    # Filtra los libros si hay una consulta de búsqueda.
    if search_query:
        libros = [
            libro for libro in libros 
            if search_query.lower() in libro.titulo.lower() or 
               search_query.lower() in libro.autor.lower()
        ]
    # Filtro por categoria
    if selected_category_id:
        libros = [
            libro for libro in libros 
            if libro.categoria_id == selected_category_id
        ]
    
    return render_template('main/explore_books.html', 
                            libros=libros, 
                            categorias=categorias,
                            selected_category=selected_category_id,
                            search_query=search_query)

@main_bp.route('/book/<int:libro_id>')
def book_detail(libro_id):
    libro = Libro.get_by_id(libro_id)
    if libro:
        return render_template('main/book_detail.html', libro=libro)
    set_alert('Libro no encontrado.', 'error')
    return redirect(url_for('main.explore_books'))

# --- RUTAS Y LÓGICA DEL CARRITO DE COMPRAS---

def get_user_cart():
    user_id = session.get('user_id')
    if not user_id:
        return {} 
    
    if 'user_carts' not in session:
        session['user_carts'] = {}
    
    if str(user_id) not in session['user_carts']:
        session['user_carts'][str(user_id)] = {}
        
    return session['user_carts'][str(user_id)]

def save_user_cart(cart):
    user_id = session.get('user_id')
    if user_id:
        if 'user_carts' not in session:
            session['user_carts'] = {} 
        session['user_carts'][str(user_id)] = cart
        session.modified = True 

@main_bp.route('/add_to_cart/<int:libro_id>', methods=['POST'])
def add_to_cart(libro_id):
    if not session.get('user_id'):
        set_alert('Para añadir productos al carrito, por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))
    
    if session.get('is_admin'):
        set_alert('Los administradores no pueden usar el carrito de compras.', 'warning')
        return redirect(request.referrer or url_for('main.index'))

    libro = Libro.get_by_id(libro_id)
    if not libro:
        set_alert('El libro no existe.', 'error')
        return redirect(request.referrer or url_for('main.explore_books'))

    try:
        cantidad = int(request.form.get('cantidad', 1))
        if cantidad <= 0:
            set_alert('La cantidad debe ser al menos 1.', 'error')
            return redirect(request.referrer or url_for('main.book_detail', libro_id=libro_id))
    except ValueError:
        set_alert('Cantidad inválida.', 'error')
        return redirect(request.referrer or url_for('main.book_detail', libro_id=libro_id))

    cart = get_user_cart()

    if str(libro_id) in cart:
        cart[str(libro_id)]['cantidad'] += cantidad
    else:
        cart[str(libro_id)] = {
            'id': libro.id,
            'titulo': libro.titulo,
            'autor': libro.autor,
            'precio': float(libro.precio),
            'imagen_url': libro.imagen_url,
            'stock': libro.stock,
            'cantidad': cantidad
        }
    
    if cart[str(libro_id)]['cantidad'] > libro.stock:
        added_over_stock = cart[str(libro_id)]['cantidad'] - libro.stock
        if added_over_stock > 0:             
            cart[str(libro_id)]['cantidad'] = libro.stock 
        
        if cart[str(libro_id)]['cantidad'] <= 0: 
            if str(libro_id) in cart: 
                del cart[str(libro_id)]
    else:
        set_alert(f'{libro.titulo} añadido al carrito.', 'success')

    save_user_cart(cart)
    return redirect(request.referrer or url_for('main.explore_books')) 

@main_bp.route('/cart')
def cart_detail():
    if not session.get('user_id'):
        set_alert('Para ver tu carrito, por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))
    
    if session.get('is_admin'):
        set_alert('Los administradores no tienen acceso al carrito de compras.', 'warning')
        return redirect(url_for('main.index'))

    cart = get_user_cart()
    cart_items_data = []
    total_price = 0

    for item_id in list(cart.keys()): 
        item_data = cart[item_id]
        libro = Libro.get_by_id(int(item_id))
        if libro:
            if item_data['cantidad'] > libro.stock:
                item_data['cantidad'] = libro.stock
                set_alert(f'La cantidad de "{libro.titulo}" se ajustó a {libro.stock} debido a stock limitado.', 'info')
            
            if libro.stock <= 0: 
                set_alert(f'"{libro.titulo}" ha sido eliminado de tu carrito porque no hay stock disponible.', 'warning')
                del cart[item_id]
                continue 
            
            item_data['titulo'] = libro.titulo
            item_data['autor'] = libro.autor
            item_data['precio'] = float(libro.precio)
            item_data['imagen_url'] = libro.imagen_url
            item_data['stock'] = libro.stock 
            
            cart_items_data.append(item_data)
            total_price += item_data['precio'] * item_data['cantidad']
        else:
            del cart[item_id]
            set_alert(f'Un artículo fue removido de tu carrito porque ya no está disponible.', 'warning')

    save_user_cart(cart)
    
    return render_template('main/cart.html', cart_items=cart_items_data, total_price=total_price)

@main_bp.route('/update_cart/<int:libro_id>', methods=['POST'])
def update_cart(libro_id):
    if not session.get('user_id'):
        set_alert('Para actualizar tu carrito, por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))
    
    if session.get('is_admin'):
        set_alert('Los administradores no pueden modificar el carrito de compras.', 'warning')
        return redirect(request.referrer or url_for('main.index'))

    cart = get_user_cart()
    str_libro_id = str(libro_id)

    if str_libro_id not in cart:
        set_alert('El libro no está en tu carrito.', 'error')
        return redirect(url_for('main.cart_detail'))

    try:
        new_cantidad = int(request.form.get('cantidad'))
        libro = Libro.get_by_id(libro_id)

        if not libro:
            del cart[str_libro_id]
            set_alert('El libro fue eliminado de tu carrito porque ya no existe.', 'warning')
            save_user_cart(cart)
            return redirect(url_for('main.cart_detail'))

        if new_cantidad <= 0:
            del cart[str_libro_id]
            set_alert(f'"{libro.titulo}" eliminado del carrito.', 'success')
        elif new_cantidad > libro.stock:
            set_alert(f'No puedes añadir más de {libro.stock} unidades de "{libro.titulo}".', 'error')
            cart[str_libro_id]['cantidad'] = libro.stock 
        else:
            cart[str_libro_id]['cantidad'] = new_cantidad
            set_alert(f'Cantidad de "{libro.titulo}" actualizada a {new_cantidad}.', 'success')
        
        save_user_cart(cart)
        return redirect(url_for('main.cart_detail'))

    except ValueError:
        set_alert('Cantidad inválida.', 'error')
        return redirect(url_for('main.cart_detail'))

@main_bp.route('/remove_from_cart/<int:libro_id>', methods=['POST'])
def remove_from_cart(libro_id):
    if not session.get('user_id'):
        set_alert('Para eliminar productos del carrito, por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))

    if session.get('is_admin'):
        set_alert('Los administradores no pueden modificar el carrito de compras.', 'warning')
        return redirect(request.referrer or url_for('main.index'))

    cart = get_user_cart()
    str_libro_id = str(libro_id)

    if str_libro_id in cart:
        del cart[str_libro_id]
        save_user_cart(cart)
        set_alert('Artículo eliminado del carrito.', 'success')
    else:
        set_alert('El artículo no se encontró en el carrito.', 'error')
    
    return redirect(url_for('main.cart_detail'))

@main_bp.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('user_id'):
        set_alert('Debes iniciar sesión para completar tu compra.', 'info')
        return redirect(url_for('auth.login'))
    
    if session.get('is_admin'):
        set_alert('Los administradores no pueden realizar compras.', 'warning')
        return redirect(url_for('main.index'))

    user_id = session.get('user_id')
    cart = get_user_cart()

    if not cart:
        set_alert('Tu carrito está vacío. Añade productos antes de proceder al pago.', 'error')
        return redirect(url_for('main.explore_books'))

    total_compra = 0
    items_para_pedido = []
    
    conn = None 
    try:
        conn = get_db_connection()
        if not conn:
            set_alert('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('main.cart_detail'))
        
        cursor = conn.cursor()
        conn.start_transaction() 

        for item_id_str, item_data in cart.items():
            libro_id = int(item_id_str)
            libro = Libro.get_by_id(libro_id) 

            if not libro or libro.stock < item_data['cantidad']:
                conn.rollback() 
                set_alert(f'No hay suficiente stock para "{item_data["titulo"]}". Stock disponible: {libro.stock if libro else 0}.', 'error')
                return redirect(url_for('main.cart_detail'))
            
            total_compra += item_data['precio'] * item_data['cantidad']
            items_para_pedido.append({
                'libro_obj': libro, 
                'cantidad': item_data['cantidad'],
                'precio_unitario': item_data['precio']
            })

        nuevo_pedido = Pedido(usuario_id=user_id, total=total_compra, fecha=datetime.datetime.now())
        pedido_id = nuevo_pedido.save(conn=conn, cursor=cursor) 
        
        if not pedido_id:
            conn.rollback()
            set_alert('Error al crear el pedido. Inténtalo de nuevo.', 'error')
            return redirect(url_for('main.cart_detail'))

        for item in items_para_pedido:
            detalle = PedidoDetalle(
                pedido_id=pedido_id,
                libro_id=item['libro_obj'].id,
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )
            if not detalle.save(conn=conn, cursor=cursor): 
                conn.rollback()
                set_alert(f'Error al guardar detalles para "{item["libro_obj"].titulo}". La compra ha sido cancelada.', 'error')
                return redirect(url_for('main.cart_detail'))
            
            if not item['libro_obj'].update_stock(-item['cantidad'], conn=conn, cursor=cursor): 
                conn.rollback()
                set_alert(f'Error al actualizar el stock de "{item["libro_obj"].titulo}". La compra ha sido cancelada.', 'error')
                return redirect(url_for('main.cart_detail'))

        conn.commit() 
        
        user_cart = get_user_cart()
        user_cart.clear() 
        save_user_cart(user_cart) 

        set_alert('¡Tu compra se ha realizado con éxito! Gracias por tu pedido.', 'success')
        return redirect(url_for('main.index')) 

    except mysql.connector.Error as err:
        print(f"Error de base de datos durante el checkout: {err}")
        if conn: conn.rollback()
        set_alert('Ocurrió un error en la base de datos durante tu compra. Inténtalo de nuevo.', 'error')
        return redirect(url_for('main.cart_detail'))
    except Exception as e:
        print(f"Error inesperado durante el checkout: {e}")
        if conn: conn.rollback()
        set_alert('Ocurrió un error inesperado durante tu compra. Inténtalo de nuevo.', 'error')
        return redirect(url_for('main.cart_detail'))
    finally:
        if conn:
            cursor.close()
            conn.close()

@main_bp.route('/checkout/confirm', methods=['POST'])
def checkout_confirm():
    cart = get_user_cart()
    if not cart:
        set_alert('Tu carrito está vacío.', 'error')
        return redirect(url_for('main.cart_detail'))

    total = sum(item['precio'] * item['cantidad'] for item in cart.values())
    return render_template('main/checkout_confirm.html', cart_items=cart.values(), total_price=total)





# --- Rutas del Blueprint (Administrador) ---

@admin_bp.route('/manage_books')
def manage_books():
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    libros = Libro.get_all() 
    return render_template('admin/manage_books.html', libros=libros)

@admin_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    categorias = Categoria.get_all() 
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        imagen_url = request.form.get('imagen_url')
        descripcion = request.form.get('descripcion')
        editorial = request.form.get('editorial')
        fecha_publicacion_str = request.form.get('fecha_publicacion')
        fecha_publicacion = None
        if fecha_publicacion_str:
            fecha_publicacion = datetime.datetime.strptime(fecha_publicacion_str, '%Y-%m-%d').date()
        en_remate = 'en_remate' in request.form
        categoria_id = request.form.get('categoria_id', type=int)

        if not all([titulo, autor, precio, stock, categoria_id]):
            set_alert('Por favor, completa todos los campos obligatorios.', 'error')
            return render_template('admin/add_edit_book.html', title='Añadir Nuevo Libro', categorias=categorias)
        
        nuevo_libro = Libro(id=None, titulo=titulo, autor=autor, precio=precio, stock=stock, 
                                imagen_url=imagen_url, descripcion=descripcion, editorial=editorial, 
                                fecha_publicacion=fecha_publicacion, en_remate=en_remate, 
                                categoria_id=categoria_id)
        
        if nuevo_libro.save():
            set_alert('Libro añadido exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            set_alert('Error al añadir el libro. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_book.html', title='Añadir Nuevo Libro', categorias=categorias)

@admin_bp.route('/edit_book/<int:libro_id>', methods=['GET', 'POST'])
def edit_book(libro_id):
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    libro = Libro.get_by_id(libro_id)
    categorias = Categoria.get_all() 
    if not libro:
        set_alert('Libro no encontrado.', 'error')
        return redirect(url_for('admin.manage_books')) 

    if request.method == 'POST':
        libro.titulo = request.form['titulo']
        libro.autor = request.form['autor']
        libro.precio = float(request.form['precio'])
        libro.stock = int(request.form['stock'])
        libro.imagen_url = request.form.get('imagen_url')
        descripcion = request.form.get('descripcion')
        editorial = request.form.get('editorial')
        fecha_publicacion_str = request.form.get('fecha_publicacion')
        libro.fecha_publicacion = None
        if fecha_publicacion_str:
            libro.fecha_publicacion = datetime.datetime.strptime(fecha_publicacion_str, '%Y-%m-%d').date()
        libro.en_remate = 'en_remate' in request.form
        libro.categoria_id = request.form.get('categoria_id', type=int)

        if libro.save():
            set_alert('Libro actualizado exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            set_alert('Error al actualizar el libro. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_book.html', title='Editar Libro', libro=libro, categorias=categorias)

@admin_bp.route('/delete_book/<int:libro_id>', methods=['GET', 'POST'])
def delete_book(libro_id):
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    libro = Libro.get_by_id(libro_id)
    if not libro:
        set_alert('Libro no encontrado.', 'error')
        return redirect(url_for('admin.manage_books')) 

    if request.method == 'POST':
        if Libro.delete(libro_id):
            set_alert('Libro eliminado exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            set_alert('Error al eliminar el libro.', 'error')
    
    return render_template('admin/confirm_delete.html', libro=libro)

@admin_bp.route('/add_category_ajax', methods=['POST'])
def add_category_ajax():
    if not session.get('is_admin'):
        return jsonify({'error': 'Acceso denegado. Se requiere ser administrador.'}), 403

    data = request.get_json()
    category_name = data.get('name')

    if not category_name or len(category_name.strip()) < 2:
        return jsonify({'error': 'El nombre de la categoría es demasiado corto o está vacío.'}), 400

    existing_categories = Categoria.get_all()
    for cat in existing_categories:
        if cat.nombre.lower() == category_name.strip().lower():
            return jsonify({'error': 'La categoría ya existe.'}), 409 

    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            sql = "INSERT INTO categorias (nombre) VALUES (%s)"
            cursor.execute(sql, (category_name.strip(),))
            conn.commit()
            new_category_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            return jsonify({'id': new_category_id, 'nombre': category_name.strip()}), 201 
        else:
            return jsonify({'error': 'No se pudo conectar a la base de datos.'}), 500
    except Exception as e:
        print(f"Error al añadir categoría AJAX: {e}")
        return jsonify({'error': 'Error interno del servidor al añadir categoría.'}), 500


# --- GESTIÓN DE USUARIOS  ---

@admin_bp.route('/manage_users')
def manage_users():    
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    usuarios = Usuario.get_all() 
    return render_template('admin/manage_users.html', usuarios=usuarios)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nombre = request.form['nombre'] 
        correo = request.form.get('correo') 
        password = request.form['password']
        confirm_password = request.form.get('confirm_password') 

        if not nombre or not password or not correo:
            set_alert('Nombre de usuario, correo y contraseña son obligatorios.', 'error')
            return render_template('admin/add_edit_user.html', title='Añadir Nuevo Usuario', 
                                   usuario={'nombre': nombre, 'correo': correo})

        if password != confirm_password:
            set_alert('Las contraseñas no coinciden.', 'error')
            return render_template('admin/add_edit_user.html', title='Añadir Nuevo Usuario', 
                                   usuario={'nombre': nombre, 'correo': correo})

        if Usuario.find_by_username(nombre): 
            set_alert('El nombre de usuario ya existe.', 'error')
            return render_template('admin/add_edit_user.html', title='Añadir Nuevo Usuario', 
                                   usuario={'nombre': nombre, 'correo': correo})
        
        if correo and Usuario.find_by_email(correo): 
            set_alert('El correo electrónico ya está registrado.', 'error')
            return render_template('admin/add_edit_user.html', title='Añadir Nuevo Usuario', 
                                   usuario={'nombre': nombre, 'correo': correo})

        is_admin = 'is_admin' in request.form
        
        new_user = Usuario.create_user(nombre, password, email=correo, is_admin=is_admin) 

        if new_user:
            set_alert('Usuario añadido exitosamente!', 'success')
            return redirect(url_for('admin.manage_users'))
        else:
            set_alert('Error al añadir el usuario. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_user.html', title='Añadir Nuevo Usuario')

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    usuario = Usuario.get_by_id(user_id)
    if not usuario:
        set_alert('Usuario no encontrado.', 'error')
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.correo = request.form.get('correo') 
        
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password') 

        if new_password:
            if new_password != confirm_password:
                set_alert('Las contraseñas no coinciden.', 'error')
                return render_template('admin/add_edit_user.html', title='Editar Usuario', usuario=usuario)
            usuario.set_password(new_password)

        usuario.rol_id = 1 if 'is_admin' in request.form else 2 
        
        existing_user_by_name = Usuario.find_by_username(usuario.nombre)
        if existing_user_by_name and existing_user_by_name.id != user_id:
            set_alert('El nombre de usuario ya existe.', 'error')
            return render_template('admin/add_edit_user.html', title='Editar Usuario', usuario=usuario)

        existing_user_by_email = Usuario.find_by_email(usuario.correo) 
        if usuario.correo and existing_user_by_email and existing_user_by_email.id != user_id:
            set_alert('El correo electrónico ya está registrado por otro usuario.', 'error')
            return render_template('admin/add_edit_user.html', title='Editar Usuario', usuario=usuario)

        if usuario.save():
            if session.get('user_id') == usuario.id:
                session['is_admin'] = usuario.is_admin 
                
            set_alert('Usuario actualizado exitosamente!', 'success')
            return redirect(url_for('admin.manage_users'))
        else:
            set_alert('Error al actualizar el usuario. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_user.html', title='Editar Usuario', usuario=usuario)

@admin_bp.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        set_alert('Acceso denegado. Se requiere ser administrador.', 'error')
        return redirect(url_for('auth.login'))

    usuario = Usuario.get_by_id(user_id)
    if not usuario:
        set_alert('Usuario no encontrado.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if usuario.id == session.get('user_id'):
        set_alert('No puedes eliminar tu propia cuenta de administrador.', 'error')
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        if Usuario.delete(user_id):
            set_alert('Usuario eliminado exitosamente!', 'success')
            return redirect(url_for('admin.manage_users'))
        else:
            set_alert('Error al eliminar el usuario.', 'error')

    return render_template('admin/confirm_delete_user.html', usuario=usuario)


# --- Rutas del Blueprint (Autenticación) ---

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.find_by_username(username) 
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.nombre
            session['is_admin'] = user.is_admin
            get_user_cart() 
            set_alert('¡Inicio de sesión exitoso!', 'success')
            if user.is_admin:
                return redirect(url_for('admin.manage_books'))
            else:
                return redirect(url_for('main.index'))
        else:
            set_alert('Usuario o contraseña incorrectos.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        
        if not username or not password:
            set_alert('Usuario y contraseña son obligatorios.', 'error')
            return render_template('auth/register.html')

        if Usuario.find_by_username(username):
            set_alert('El nombre de usuario ya existe.', 'error')
            return render_template('auth/register.html')
        if email and Usuario.find_by_email(email):
            set_alert('El correo electrónico ya está registrado.', 'error')
            return render_template('auth/register.html')

        new_user = Usuario.create_user(username, password, email=email, is_admin=False)
        
        if new_user:
            set_alert('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            set_alert('Error al registrar usuario. Inténtalo de nuevo.', 'error')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    set_alert('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index'))



@main_bp.route('/checkout_pass')
def checkout_pass():
    if not session.get('user_id'):
        set_alert('Para continuar al checkout, por favor inicia sesión.', 'info')
        return redirect(url_for('auth.login'))

    if session.get('is_admin'):
        set_alert('Los administradores no pueden hacer compras.', 'warning')
        return redirect(url_for('main.index'))

    cart = get_user_cart()
    cart_items_data = []
    total_price = 0

    for item_id in list(cart.keys()):
        item_data = cart[item_id]
        libro = Libro.get_by_id(int(item_id))
        if libro:
            item_data['titulo'] = libro.titulo
            item_data['precio'] = float(libro.precio)
            item_data['cantidad'] = int(item_data['cantidad'])
            cart_items_data.append(item_data)
            total_price += item_data['precio'] * item_data['cantidad']
        else:
            del cart[item_id]

    save_user_cart(cart)

    return render_template('main/checkout_pass.html', cart_items=cart_items_data, total_price=total_price)