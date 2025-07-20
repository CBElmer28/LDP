import mysql.connector
from database import get_db_connection
# Para hashing de contraseñas (necesitaras instalar: pip install Werkzeug o solo darle install a requirements.txt)
from werkzeug.security import generate_password_hash, check_password_hash 
import datetime 

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
                    if 'categoria_nombre' not in data or data['categoria_nombre'] is None:
                        if data.get('categoria_id') is not None: 
                            categoria = Categoria.get_by_id(data['categoria_id'])
                            data['categoria_nombre'] = categoria.nombre if categoria else 'Desconocido'
                        else:
                            data['categoria_nombre'] = None
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
            except mysql.connector.Error as e:
                print(f"Error SQL al guardar el libro: {e}")
                conn.rollback()
                return False
            except Exception as e:
                print(f"Error inesperado al guardar el libro: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        print("Error: No se pudo obtener conexión a la base de datos para guardar el libro.")
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
            except mysql.connector.Error as e:
                print(f"Error SQL al eliminar el libro: {e}")
                conn.rollback()
                return False
            except Exception as e:
                print(f"Error inesperado al eliminar el libro: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        print("Error: No se pudo obtener conexión a la base de datos para eliminar el libro.")
        return False

    def update_stock(self, quantity_change, conn=None, cursor=None):
        if conn and cursor:
            sql = "UPDATE libros SET stock = stock + %s WHERE id = %s"
            try:
                cursor.execute(sql, (quantity_change, self.id))
                self.stock += quantity_change
                return True
            except mysql.connector.Error as e:
                print(f"Error SQL al actualizar stock del libro {self.id}: {e}")
                return False
        else:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    sql = "UPDATE libros SET stock = stock + %s WHERE id = %s"
                    cursor.execute(sql, (quantity_change, self.id))
                    conn.commit()
                    self.stock += quantity_change
                    return True
                except mysql.connector.Error as e:
                    print(f"Error SQL al actualizar stock del libro {self.id}: {e}")
                    conn.rollback()
                    return False
                except Exception as e:
                    print(f"Error inesperado al actualizar stock del libro {self.id}: {e}")
                    conn.rollback()
                    return False
                finally:
                    cursor.close()
                    conn.close()
            print("Error: No se pudo obtener conexión a la base de datos para actualizar stock.")
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
            except mysql.connector.Error as e:
                print(f"Error SQL al guardar la categoría: {e}")
                conn.rollback()
                return False
            except Exception as e:
                print(f"Error inesperado al guardar la categoría: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        print("Error: No se pudo obtener conexión a la base de datos para guardar la categoría.")
        return False

class Usuario:
    def __init__(self, id, nombre, correo, password_hash, rol_id): 
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password_hash = password_hash 
        self.rol_id = rol_id
        self.is_admin = (rol_id == 1) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
                    cursor.execute(sql, (self.nombre, self.correo, self.password_hash, self.rol_id, self.id))
                else: 
                    sql = """
                    INSERT INTO usuarios (nombre, correo, contraseña, rol_id)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql, (self.nombre, self.correo, self.password_hash, self.rol_id))
                    self.id = cursor.lastrowid 
                conn.commit()
                return True
            except mysql.connector.Error as err:
                print(f"Error SQL al guardar usuario en DB: {err}")
                conn.rollback()
                return False
            except Exception as e:
                print(f"Error inesperado al guardar usuario: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        print("Error: No se pudo obtener conexión a la base de datos para guardar el usuario.")
        return False

    @staticmethod
    def get_all():
        conn = get_db_connection()
        usuarios = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.id, u.nombre, u.correo, u.contraseña, u.rol_id
                FROM usuarios u
                ORDER BY u.nombre ASC
                """
                cursor.execute(query)
                usuarios_data = cursor.fetchall()
                usuarios = [Usuario(u['id'], u['nombre'], u['correo'], u['contraseña'], u['rol_id']) for u in usuarios_data]
            except Exception as e:
                print(f"Error al obtener todos los usuarios: {e}")
            finally:
                cursor.close()
                conn.close()
        return usuarios

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.id, u.nombre, u.correo, u.contraseña, u.rol_id
                FROM usuarios u
                WHERE u.id = %s
                """
                cursor.execute(query, (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(user_data['id'], user_data['nombre'], user_data['correo'], user_data['contraseña'], user_data['rol_id'])
            except Exception as e:
                print(f"Error al obtener usuario por ID: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.id, u.nombre, u.correo, u.contraseña, u.rol_id
                FROM usuarios u
                WHERE u.nombre = %s
                """
                cursor.execute(query, (username,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(user_data['id'], user_data['nombre'], user_data['correo'], user_data['contraseña'], user_data['rol_id'])
            except Exception as e:
                print(f"Error al buscar usuario por nombre: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def find_by_email(email):
        if not email:
            return None
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                query = """
                SELECT u.id, u.nombre, u.correo, u.contraseña, u.rol_id
                FROM usuarios u
                WHERE u.correo = %s
                """
                cursor.execute(query, (email,))
                user_data = cursor.fetchone()
                if user_data:
                    return Usuario(user_data['id'], user_data['nombre'], user_data['correo'], user_data['contraseña'], user_data['rol_id'])
            except Exception as e:
                print(f"Error al buscar usuario por email: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def create_user(username, password, email=None, is_admin=False):
        hashed_password = generate_password_hash(password)
        rol_id = 1 if is_admin else 2 
        new_user = Usuario(id=None, nombre=username, correo=email, password_hash=hashed_password, rol_id=rol_id) 
        if new_user.save():
            return new_user
        return None

    @staticmethod
    def delete(user_id):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
                conn.commit()
                return True
            except mysql.connector.Error as err:
                print(f"Error SQL al eliminar usuario de DB: {err}")
                conn.rollback()
                return False
            except Exception as e:
                print(f"Error inesperado al eliminar usuario: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
                conn.close()
        print("Error: No se pudo obtener conexión a la base de datos para eliminar el usuario.")
        return False

class Pedido:
    def __init__(self, id=None, usuario_id=None, fecha=None, total=None):
        self.id = id
        self.usuario_id = usuario_id
        self.fecha = fecha if fecha else datetime.datetime.now()
        self.total = total

    def save(self, conn=None, cursor=None):
        _conn = conn if conn else get_db_connection()
        if not _conn:
            print("Error: No se pudo obtener conexión a la base de datos para guardar el pedido.")
            return None
        
        _cursor = cursor if cursor else _conn.cursor()
        try:
            sql = "INSERT INTO pedidos (usuario_id, fecha, total) VALUES (%s, %s, %s)"
            _cursor.execute(sql, (self.usuario_id, self.fecha, self.total))
            if not conn:
                _conn.commit()
            self.id = _cursor.lastrowid
            return self.id
        except mysql.connector.Error as err:
            print(f"Error SQL al guardar pedido en DB: {err}")
            if not conn: _conn.rollback()
            return None
        except Exception as e:
            print(f"Error inesperado al guardar pedido: {e}")
            if not conn: _conn.rollback()
            return None
        finally:
            if not conn:
                _cursor.close()
                _conn.close()
        return None

class PedidoDetalle:
    def __init__(self, id=None, pedido_id=None, libro_id=None, cantidad=None, precio_unitario=None):
        self.id = id
        self.pedido_id = pedido_id
        self.libro_id = libro_id
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    def save(self, conn=None, cursor=None):

        _conn = conn if conn else get_db_connection()
        if not _conn:
            print("Error: No se pudo obtener conexión a la base de datos para guardar el detalle del pedido.")
            return False
        
        _cursor = cursor if cursor else _conn.cursor()
        try:
            sql = "INSERT INTO pedido_detalles (pedido_id, libro_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
            _cursor.execute(sql, (self.pedido_id, self.libro_id, self.cantidad, self.precio_unitario))
            if not conn:
                _conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error SQL al guardar detalle de pedido en DB: {err}")
            if not conn: _conn.rollback()
            return False
        except Exception as e:
            print(f"Error inesperado al guardar detalle de pedido: {e}")
            if not conn: _conn.rollback()
            return False
        finally:
            if not conn:
                _cursor.close()
                _conn.close()
        return False
