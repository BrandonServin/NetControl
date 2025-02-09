// Función para abrir la ventana modal específica
function abrirModal(idModal) {
    // Obtiene el elemento modal con el ID proporcionado
    var modal = document.getElementById(idModal);
    // Cambia el estilo para mostrar el modal
    modal.style.display = "block";
}

// Función para cerrar la ventana modal específica
function cerrarModal(idModal) {
    // Obtiene el elemento modal con el ID proporcionado
    var modal = document.getElementById(idModal);
    // Cambia el estilo para ocultar el modal
    modal.style.display = "none";
}

// Cerrar la ventana modal si el usuario hace clic fuera de ella
window.onclick = function (event) {
    // Obtiene todos los elementos con la clase 'modal'
    var modals = document.getElementsByClassName('modal');
    // Recorre cada modal
    for (var i = 0; i < modals.length; i++) {
        // Verifica si el clic ocurrió en el fondo del modal (es decir, fuera del contenido del modal)
        if (event.target === modals[i]) {
            // Oculta el modal si el clic fue fuera del contenido
            modals[i].style.display = "none";
        }
    }
}
