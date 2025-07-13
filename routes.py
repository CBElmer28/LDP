from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Libro

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    libros = Libro.get_all()
    return render_template('index.html', libros=libros)

@main_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        genero = request.form['genero']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        imagen_url = request.form.get('imagen_url')

        nuevo_libro = Libro(id=None, titulo=titulo, autor=autor, genero=genero, precio=precio, stock=stock, imagen_url=imagen_url)
        if nuevo_libro.save():
            flash('Libro añadido exitosamente!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Error al añadir el libro.', 'error')
            return render_template('add_edit_book.html', title='Añadir Libro', libro=None)
    
    return render_template('add_edit_book.html', title='Añadir Libro', libro=None)

@main_bp.route('/edit/<int:libro_id>', methods=['GET', 'POST'])
def edit_book(libro_id):
    libro = Libro.get_by_id(libro_id)
    if not libro:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        libro.titulo = request.form['titulo']
        libro.autor = request.form['autor']
        libro.genero = request.form['genero']
        libro.precio = float(request.form['precio'])
        libro.stock = int(request.form['stock'])
        libro.imagen_url = request.form.get('imagen_url')

        if libro.save():
            flash('Libro actualizado exitosamente!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Error al actualizar el libro.', 'error')
    
    return render_template('add_edit_book.html', title='Editar Libro', libro=libro)

@main_bp.route('/delete/<int:libro_id>', methods=['GET', 'POST'])
def delete_book(libro_id):
    libro = Libro.get_by_id(libro_id)
    if not libro:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if Libro.delete(libro_id):
            flash('Libro eliminado exitosamente!', 'success')
        else:
            flash('Error al eliminar el libro.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('confirm_delete.html', libro=libro)