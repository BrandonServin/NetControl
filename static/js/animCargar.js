// Espera a que todo el contenido del DOM esté completamente cargado y disponible
document.addEventListener("DOMContentLoaded", function () {
    // Selecciona todos los elementos con la clase 'animacion'
    const elements = document.querySelectorAll('.animacion');
    // Recorre cada uno de los elementos seleccionados
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
        }, index * 160); // Ajusta el tiempo entre apariciones según tus necesidades
    });
});
