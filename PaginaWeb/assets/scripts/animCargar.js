// Espera a que todo el contenido del DOM esté completamente cargado y disponible
document.addEventListener("DOMContentLoaded", function () {
    // Selecciona todos los elementos con la clase 'animacion'
    const elements = document.querySelectorAll('.animacion');
    // Recorre cada uno de los elementos seleccionados
    elements.forEach((element, index) => {
        // Establece un temporizador para añadir la clase 'visible' después de un retraso
        setTimeout(() => {
            // Añade la clase 'visible' al elemento actual
            element.classList.add('visible');
        // Establece el retraso en milisegundos para cada elemento basado en su índice
        }, index * 230); // Ajusta el tiempo entre apariciones según tus necesidades
    });
});
