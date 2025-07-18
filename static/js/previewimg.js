window.addCategoryUrl = "{{ url_for('admin.add_category_ajax') }}"; 

        document.addEventListener('DOMContentLoaded', function() {
            const imageUrlInput = document.getElementById('imagen_url');
            const imagePreview = document.getElementById('image-preview');

            function updateImagePreview() {
                const url = imageUrlInput.value;
                if (url) {
                    imagePreview.src = url;
                } else {
                    imagePreview.src = 'https://placehold.co/200x200/cccccc/333333?text=Sin+Imagen';
                }
            }
            updateImagePreview();
            imageUrlInput.addEventListener('input', updateImagePreview);
            imagePreview.onerror = function() {
                this.src = 'https://placehold.co/200x200/cccccc/333333?text=Error+Carga';
                console.error('Error al cargar la imagen de vista previa. URL inválida o inaccesible.');
            };
        });