document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const uploadForm = document.getElementById('uploadForm');
    const progressBar = document.getElementById('progressBar');
    const progress = progressBar.querySelector('.progress');
    const fileContainer = document.getElementById('fileContainer');
    const copyButtons = document.querySelectorAll('.copy-link');
    let draggedItem = null;

    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        handleFiles(files);
    });

    document.body.addEventListener('dragenter', highlight, false);
    document.body.addEventListener('dragover', highlight, false);
    document.body.addEventListener('dragleave', unhighlight, false);
    document.body.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        preventDefaults(e);
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        preventDefaults(e);
        dropZone.classList.remove('highlight');
    }

    function handleDrop(e) {
        unhighlight(e);
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        [...files].forEach(uploadFile);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', uploadForm.action, true);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progress.style.width = percentComplete + '%';
            }
        };

        xhr.onload = () => {
            progressBar.style.display = 'none'; // Скрыть прогрессбар после загрузки
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        const link = `${window.location.origin}/${response.unique_link}`;
                        const originalFilename = response.original_filename; // Получаем оригинальное имя файла
                        navigator.clipboard.writeText(link).then(() => {
                            alert('Ссылка на файл скопирована в буфер обмена');
                        }).catch(err => {
                            console.error('Ошибка копирования ссылки: ', err);
                        });
                        window.location.reload(); // Обновление страницы после успешной загрузки
                    }
                } catch (err) {
                    console.error('Ошибка обработки ответа сервера: ', err);
                    window.location.reload(); // Обновление страницы даже при ошибке обработки
                }
            } else {
                alert('Ошибка при загрузке файла');
            }
        };

        xhr.onerror = () => {
            progressBar.style.display = 'none'; // Скрыть прогрессбар при ошибке
            alert('Ошибка сети');
        };

        progressBar.style.display = 'block';
        xhr.send(formData);
    }

    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const link = button.getAttribute('data-link');
            navigator.clipboard.writeText(link).then(() => {
                button.classList.add('success');
                setTimeout(() => {
                    button.classList.remove('success');
                }, 2000);
            }).catch(err => {
                console.error('Ошибка копирования ссылки: ', err);
            });
        });
    });

    fileContainer.addEventListener('dragstart', (e) => {
        if (e.target.classList.contains('file-item')) {
            draggedItem = e.target;
            e.target.classList.add('dragging');
        }
    });

    fileContainer.addEventListener('dragend', (e) => {
        if (e.target.classList.contains('file-item')) {
            e.target.classList.remove('dragging');
        }
    });

    fileContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        const afterElement = getDragAfterElement(fileContainer, e.clientY);
        if (afterElement == null) {
            fileContainer.appendChild(draggedItem);
        } else {
            fileContainer.insertBefore(draggedItem, afterElement);
        }
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.file-item:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
});

const listViewButton = document.getElementById('listView');
const gridViewButton = document.getElementById('gridView');
const fileContainer = document.getElementById('fileContainer');

if (listViewButton && gridViewButton && fileContainer) {
    // Установка начального вида
    if (fileContainer.classList.contains('file-grid')) {
        gridViewButton.classList.add('active');
        listViewButton.classList.remove('active');
    } else {
        listViewButton.classList.add('active');
        gridViewButton.classList.remove('active');
    }

    // Существующий код для обработчиков событий
    listViewButton.addEventListener('click', () => {
        fileContainer.classList.remove('file-grid');
        fileContainer.classList.add('file-list');
        listViewButton.classList.add('active');
        gridViewButton.classList.remove('active');
    });

    gridViewButton.addEventListener('click', () => {
        fileContainer.classList.remove('file-list');
        fileContainer.classList.add('file-grid');
        gridViewButton.classList.add('active');
        listViewButton.classList.remove('active');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    const modal = document.getElementById('deleteModal');
    const closeModal = modal.querySelector('.close-btn');
    const confirmDelete = document.getElementById('confirmDelete');
    const cancelDelete = document.getElementById('cancelDelete');
    let currentForm = null;

    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            currentForm = button.closest('form');
            modal.style.display = 'block';
        });
    });

    closeModal.onclick = function() {
        modal.style.display = 'none';
    }

    cancelDelete.onclick = function() {
        modal.style.display = 'none';
    }

    confirmDelete.onclick = function() {
        if (currentForm) {
            currentForm.submit();
        }
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

