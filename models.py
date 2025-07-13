class Libro:
    def __init__(self, id, titulo, autor, genero, precio, stock, imagen_url=None):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.precio = precio
        self.stock = stock
        self.imagen_url = imagen_url

    @staticmethod
    def get_all():
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM libros ORDER BY titulo ASC')
            libros_data = cursor.fetchall()
            cursor.close()
            conn.close()
            return [Libro(**data) for data in libros_data]
        return []

    @staticmethod
    def get_by_id(libro_id):
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM libros WHERE id = %s', (libro_id,))
            libro_data = cursor.fetchone()
            cursor.close()
            conn.close()
            if libro_data:
                return Libro(**libro_data)
        return None

    def save(self):
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if self.id:
                sql = """
                UPDATE libros SET titulo = %s, autor = %s, genero = %s, precio = %s, stock = %s, imagen_url = %s
                WHERE id = %s
                """
                cursor.execute(sql, (self.titulo, self.autor, self.genero, self.precio, self.stock, self.imagen_url, self.id))
            else:
                sql = """
                INSERT INTO libros (titulo, autor, genero, precio, stock, imagen_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (self.titulo, self.autor, self.genero, self.precio, self.stock, self.imagen_url))
                self.id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False

    @staticmethod
    def delete(libro_id):
        from database import get_db_connection
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM libros WHERE id = %s', (libro_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False