from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from models import Libro, Categoria, Usuario
from database import get_db_connection 
import datetime

# --- Definición de Blueprints ---

# Blueprint para rutas públicas/cliente
main_bp = Blueprint('main', __name__)

# Blueprint para rutas de administrador
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Blueprint para autenticación (login, registro, logout)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- Rutas del Blueprint 'main' (Públicas/Cliente) ---

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

    # Filtrar libros
    if search_query:
        libros = [
            libro for libro in libros 
            if search_query.lower() in libro.titulo.lower() or 
               search_query.lower() in libro.autor.lower()
        ]
    
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
    flash('Libro no encontrado.', 'error')
    return redirect(url_for('main.explore_books'))

# --- Rutas del Blueprint 'admin' (Administración) ---

@admin_bp.route('/manage_books')
def manage_books():
    libros = Libro.get_all() 
    return render_template('admin/manage_books.html', libros=libros)

@admin_bp.route('/add_book', methods=['GET', 'POST'])
def add_book():
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
            flash('Por favor, completa todos los campos obligatorios.', 'error')
            return render_template('admin/add_edit_book.html', title='Añadir Nuevo Libro', categorias=categorias)
        
        nuevo_libro = Libro(id=None, titulo=titulo, autor=autor, precio=precio, stock=stock, 
                             imagen_url=imagen_url, descripcion=descripcion, editorial=editorial, 
                             fecha_publicacion=fecha_publicacion, en_remate=en_remate, 
                             categoria_id=categoria_id)
        
        if nuevo_libro.save():
            flash('Libro añadido exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            flash('Error al añadir el libro. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_book.html', title='Añadir Nuevo Libro', categorias=categorias)

@admin_bp.route('/edit_book/<int:libro_id>', methods=['GET', 'POST'])
def edit_book(libro_id):
    libro = Libro.get_by_id(libro_id)
    categorias = Categoria.get_all() 
    if not libro:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('admin.manage_books')) 

    if request.method == 'POST':
        libro.titulo = request.form['titulo']
        libro.autor = request.form['autor']
        libro.precio = float(request.form['precio'])
        libro.stock = int(request.form['stock'])
        libro.imagen_url = request.form.get('imagen_url')
        libro.descripcion = request.form.get('descripcion')
        libro.editorial = request.form.get('editorial')
        fecha_publicacion_str = request.form.get('fecha_publicacion')
        libro.fecha_publicacion = None
        if fecha_publicacion_str:
            libro.fecha_publicacion = datetime.datetime.strptime(fecha_publicacion_str, '%Y-%m-%d').date()
        libro.en_remate = 'en_remate' in request.form
        libro.categoria_id = request.form.get('categoria_id', type=int)

        if libro.save():
            flash('Libro actualizado exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            flash('Error al actualizar el libro. Inténtalo de nuevo.', 'error')

    return render_template('admin/add_edit_book.html', title='Editar Libro', libro=libro, categorias=categorias)

@admin_bp.route('/delete_book/<int:libro_id>', methods=['GET', 'POST'])
def delete_book(libro_id):
    libro = Libro.get_by_id(libro_id)
    if not libro:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('admin.manage_books')) 

    if request.method == 'POST':
        if Libro.delete(libro_id):
            flash('Libro eliminado exitosamente!', 'success')
            return redirect(url_for('admin.manage_books')) 
        else:
            flash('Error al eliminar el libro.', 'error')
    
    return render_template('admin/confirm_delete.html', libro=libro)

@admin_bp.route('/add_category_ajax', methods=['POST'])
def add_category_ajax():
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


# --- Rutas del Blueprint 'auth' (Autenticación) ---

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
            flash('¡Inicio de sesión exitoso!', 'success')
            if user.is_admin:
                return redirect(url_for('admin.manage_books'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        
        if not username or not password:
            flash('Usuario y contraseña son obligatorios.', 'error')
            return render_template('auth/register.html')

        if Usuario.find_by_username(username):
            flash('El nombre de usuario ya existe.', 'error')
            return render_template('auth/register.html')
        if email and Usuario.find_by_email(email):
            flash('El correo electrónico ya está registrado.', 'error')
            return render_template('auth/register.html')


        new_user = Usuario.create_user(username, password, email=email, is_admin=False)
        
        if new_user:
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error al registrar usuario. Inténtalo de nuevo.', 'error')
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index'))