
from database import get_db_connection
# Para hashing de contraseñas (necesitaras instalar: pip install Werkzeug o solo darle install a requirements.txt)
from werkzeug.security import generate_password_hash, check_password_hash 

class Libro:
    def __init__(self, id, titulo, autor, precio, stock, imagen_url=None,
                 descripcion=None, editorial=None, fecha_publicacion=None,
                 en_remate=False, categoria_id=None, categoria_nombre=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.precio = precio
        self.stock = stock
        self.imagen_url = imagen_url
        self.descripcion = descripcion
        self.editorial = editorial
        self.fecha_publicacion = fecha_publicacion
        self.en_remate = en_remate
        self.categoria_id = categoria_id
        self.categoria_nombre = categoria_nombre

    @staticmethod
    def _fetch_libros_from_db(query, params=None):
        conn = get_db_connection()
        libros = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                libros_data = cursor.fetchall()
                for data in libros_data:
                    if 'categoria_nombre' not in data and data.get('categoria_id'):
                        categoria = Categoria.get_by_id(data['categoria_id'])
                        data['categoria_nombre'] = categoria.nombre if categoria else 'Desconocido'
                    libros.append(Libro(**data))
            except Exception as e:
                print(f"Error al ejecutar la consulta de libros: {e}")
            finally:
                cursor.close()
                conn.close()
        return libros

    @staticmethod
    def get_all():
        query = """
        SELECT l.*, c.nombre AS categoria_nombre
        FROM libros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        ORDER BY l.titulo ASC
        """
        return Libro._fetch_libros_from_db(query)

    @staticmethod
    def get_by_id(libro_id):
        query = """
        SELECT l.*, c.nombre AS categoria_nombre
        FROM libros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        WHERE l.id = %s
        """
        libros = Libro._fetch_libros_from_db(query, (libro_id,))
        return libros[0] if libros else None

    @staticmethod
    def get_latest_books(limit=8):
        query = """
        SELECT l.*, c.nombre AS categoria_nombre
        FROM libros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        ORDER BY l.fecha_publicacion DESC, l.id DESC
        LIMIT %s
        """
        return Libro._fetch_libros_from_db(query, (limit,))

    @staticmethod
    def get_popular_books(limit=8):
        query = """
        SELECT l.*, c.nombre AS categoria_nombre
        FROM libros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        ORDER BY l.stock ASC, l.id DESC
        LIMIT %s
        """
        return Libro._fetch_libros_from_db(query, (limit,))

    @staticmethod
    def get_on_sale_books(limit=8):
        query = """
        SELECT l.*, c.nombre AS categoria_nombre
        FROM libros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        WHERE l.en_remate = TRUE
        ORDER BY l.titulo ASC
        LIMIT %s
        """
        return Libro._fetch_libros_from_db(query, (limit,))

    def save(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if self.id: 
                    sql = """
                    UPDATE libros SET titulo = %s, autor = %s, precio = %s, stock = %s,
                    imagen_url = %s, descripcion = %s, editorial = %s, fecha_publicacion = %s,
                    en_remate = %s, categoria_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(sql, (self.titulo, self.autor, self.precio, self.stock,
                                         self.imagen_url, self.descripcion, self.editorial,
                                         self.fecha_publicacion, self.en_remate, self.categoria_id,
                                         self.id))
                else: 
                    sql = """
                    INSERT INTO libros (titulo, autor, precio, stock, imagen_url,
                                        descripcion, editorial, fecha_publicacion, en_remate, categoria_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (self.titulo, self.autor, self.precio, self.stock,
                                         self.imagen_url, self.descripcion, self.editorial,
                                         self.fecha_publicacion, self.en_remate, self.categoria_id))
                    self.id = cursor.lastrowid 
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al guardar el libro: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        return False

    @staticmethod
    def delete(libro_id):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM libros WHERE id = %s', (libro_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al eliminar el libro: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        return False

class Categoria:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    @staticmethod
    def get_all():
        conn = get_db_connection()
        categorias = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute('SELECT * FROM categorias ORDER BY nombre ASC')
                categorias_data = cursor.fetchall()
                categorias = [Categoria(**data) for data in categorias_data]
            except Exception as e:
                print(f"Error al obtener categorías: {e}")
            finally:
                cursor.close()
                conn.close()
        return categorias

    @staticmethod
    def get_by_id(categoria_id):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute('SELECT * FROM categorias WHERE id = %s', (categoria_id,))
                categoria_data = cursor.fetchone()
                if categoria_data:
                    return Categoria(**categoria_data)
            except Exception as e:
                print(f"Error al obtener categoría por ID: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    def save(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if self.id: 
                    sql = "UPDATE categorias SET nombre = %s WHERE id = %s"
                    cursor.execute(sql, (self.nombre, self.id))
                else: 
                    sql = "INSERT INTO categorias (nombre) VALUES (%s)"
                    cursor.execute(sql, (self.nombre,))
                    self.id = cursor.lastrowid 
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al guardar la categoría: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        return False

class Usuario:
    def __init__(self, id, nombre, correo, contraseña, rol_id, rol_nombre=None):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña
        self.rol_id = rol_id
        self.rol_nombre = rol_nombre
        self.is_admin = (rol_id == 1) 

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.*, r.nombre AS rol_nombre
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.nombre = %s
                """
                cursor.execute(query, (username,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(**user_data)
            except Exception as e:
                print(f"Error al buscar usuario por nombre: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def find_by_email(email):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.*, r.nombre AS rol_nombre
                FROM usuarios u
                LEFT JOIN roles r ON u.rol_id = r.id
                WHERE u.correo = %s
                """
                cursor.execute(query, (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(**user_data)
            except Exception as e:
                print(f"Error al buscar usuario por email: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    def check_password(self, password):

        return check_password_hash(self.contraseña, password)

    def save(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if self.id:
                    sql = """
                    UPDATE usuarios SET nombre = %s, correo = %s, contraseña = %s, rol_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(sql, (self.nombre, self.correo, self.contraseña, self.rol_id, self.id))
                else:
                    sql = """
                    INSERT INTO usuarios (nombre, correo, contraseña, rol_id)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (self.nombre, self.correo, self.contraseña, self.rol_id))
                    self.id = cursor.lastrowid
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al guardar el usuario: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        return False

    @staticmethod
    def create_user(username, password, email=None, is_admin=False):
        hashed_password = generate_password_hash(password)
        rol_id = 1 if is_admin else 2 

        new_user = Usuario(id=None, nombre=username, correo=email, contraseña=hashed_password, rol_id=rol_id)
        if new_user.save():
            return new_user
        return None