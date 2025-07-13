
document.addEventListener('DOMContentLoaded', function () {
    const categoriaSelect = document.getElementById('categoria_id');
    const addCategoryModal = document.getElementById('addCategoryModal');
    const newCategoryNameInput = document.getElementById('newCategoryName');
    const saveNewCategoryBtn = document.getElementById('saveNewCategory');
    const cancelAddCategoryBtn = document.getElementById('cancelAddCategory');
    const openAddCategoryModalBtn = document.getElementById('openAddCategoryModal');
    const categoryError = document.getElementById('categoryError');

    function toggleAddCategoryButtonVisibility() {
        if (categoriaSelect.value === 'new_category') {
            openAddCategoryModalBtn.classList.remove('hidden');
        } else {
            openAddCategoryModalBtn.classList.add('hidden');
        }
    }

    toggleAddCategoryButtonVisibility();

    categoriaSelect.addEventListener('change', function () {
        toggleAddCategoryButtonVisibility();
        if (this.value === 'new_category') {
            addCategoryModal.classList.remove('hidden');
            newCategoryNameInput.focus();
        }
    });
    
    openAddCategoryModalBtn.addEventListener('click', function () {
        addCategoryModal.classList.remove('hidden');
        newCategoryNameInput.focus();
    });

    cancelAddCategoryBtn.addEventListener('click', function () {
        addCategoryModal.classList.add('hidden');
        newCategoryNameInput.value = '';
        categoryError.classList.add('hidden');
        categoryError.textContent = '';

        const newCategoryOption = categoriaSelect.querySelector('option[value="new_category"]');
        if (newCategoryOption && categoriaSelect.value === 'new_category') {
            categoriaSelect.value = '';
        }
        toggleAddCategoryButtonVisibility();
    });
    
    saveNewCategoryBtn.addEventListener('click', async function () {
        const categoryName = newCategoryNameInput.value.trim();
        categoryError.classList.add('hidden');
        categoryError.textContent = '';

        if (!categoryName) {
            categoryError.textContent = 'El nombre de la categoría no puede estar vacío.';
            categoryError.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch(window.addCategoryUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: categoryName })
            });

            const data = await response.json();

            if (response.ok) {
                const newOption = document.createElement('option');
                newOption.value = data.id;
                newOption.textContent = data.nombre;

                const addNewCategoryOption = categoriaSelect.querySelector('option[value="new_category"]');
                if (addNewCategoryOption) {
                    categoriaSelect.insertBefore(newOption, addNewCategoryOption);
                } else {
                    categoriaSelect.appendChild(newOption);
                }

                categoriaSelect.value = data.id;

                addCategoryModal.classList.add('hidden');
                newCategoryNameInput.value = '';
                openAddCategoryModalBtn.classList.add('hidden');
            } else {
                categoryError.textContent = data.error || 'Error al agregar la categoría.';
                categoryError.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error al enviar la solicitud:', error);
            categoryError.textContent = 'Error de conexión. Inténtalo de nuevo.';
            categoryError.classList.remove('hidden');
        }
    });
});