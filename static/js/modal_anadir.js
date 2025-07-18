document.addEventListener('DOMContentLoaded', () => {
    const $ = id => document.getElementById(id);
    const [categoriaSelect, addCategoryModal, newCategoryNameInput, saveNewCategoryBtn, cancelAddCategoryBtn, openAddCategoryModalBtn, categoryError] = 
        ['categoria_id', 'addCategoryModal', 'newCategoryName', 'saveNewCategory', 'cancelAddCategory', 'openAddCategoryModal', 'categoryError'].map($);

    const toggleModal = show => addCategoryModal.classList.toggle('hidden', !show);
    const toggleError = (show, text = '') => {
        categoryError.classList.toggle('hidden', !show);
        categoryError.textContent = text;
    };
    const toggleAddBtn = () => openAddCategoryModalBtn.classList.toggle('hidden', categoriaSelect.value !== 'new_category');
    const resetForm = () => {
        newCategoryNameInput.value = '';
        toggleError(false);
    };

    const openModal = () => {
        toggleModal(true);
        newCategoryNameInput.focus();
    };

    const closeModal = () => {
        toggleModal(false);
        resetForm();
        if (categoriaSelect.value === 'new_category') categoriaSelect.value = '';
        toggleAddBtn();
    };

    toggleAddBtn();

    categoriaSelect.addEventListener('change', () => {
        toggleAddBtn();
        if (categoriaSelect.value === 'new_category') openModal();
    });

    openAddCategoryModalBtn.addEventListener('click', openModal);
    cancelAddCategoryBtn.addEventListener('click', closeModal);

    saveNewCategoryBtn.addEventListener('click', async () => {
        const categoryName = newCategoryNameInput.value.trim();
        toggleError(false);

        if (!categoryName) return toggleError(true, 'El nombre de la categoría no puede estar vacío.');

        try {
            const response = await fetch(window.addCategoryUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: categoryName })
            });

            const data = await response.json();

            if (response.ok) {
                const newOption = Object.assign(document.createElement('option'), {
                    value: data.id,
                    textContent: data.nombre
                });

                const addNewCategoryOption = categoriaSelect.querySelector('option[value="new_category"]');
                categoriaSelect.insertBefore(newOption, addNewCategoryOption || null);
                categoriaSelect.value = data.id;

                toggleModal(false);
                resetForm();
                toggleAddBtn();
            } else {
                toggleError(true, data.error || 'Error al agregar la categoría.');
            }
        } catch (error) {
            console.error('Error al enviar la solicitud:', error);
            toggleError(true, 'Error de conexión. Inténtalo de nuevo.');
        }
    });
});