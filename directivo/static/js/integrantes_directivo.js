document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("integrantesSelectDirectivo");
    const lista = document.getElementById("listaSeleccionadosDirectivo");
    const botonAgregar = document.getElementById("agregarSeleccionadosDirectivo");
    const mensajeVacio = document.getElementById("mensajeVacioDirectivo");

    // Almacena los seleccionados para evitar duplicados
    const seleccionadosSet = new Set();
    lista.querySelectorAll("li").forEach(li => {
        if (li.dataset.id) seleccionadosSet.add(li.dataset.id);
    });

    // Mostrar/ocultar mensaje vacío
    function actualizarMensaje() {
        if (lista.querySelectorAll("li[data-id]").length === 0) {
            mensajeVacio.style.display = "block";
        } else {
            mensajeVacio.style.display = "none";
        }
    }

    actualizarMensaje();

    // Agregar seleccionados
    botonAgregar.addEventListener("click", function () {
        Array.from(select.selectedOptions).forEach(option => {
            const id = option.value;
            const texto = option.text;

            if (!seleccionadosSet.has(id)) {
                seleccionadosSet.add(id);
                const li = document.createElement("li");
                li.dataset.id = id;
                li.innerHTML = `${texto} <button class="eliminarBtn" type="button">Eliminar</button>`;
                lista.appendChild(li);
            }
        });
        actualizarMensaje();
    });

    // Delegación de eventos para eliminar
    lista.addEventListener("click", function (e) {
        if (e.target.classList.contains("eliminarBtn")) {
            const li = e.target.parentElement;
            seleccionadosSet.delete(li.dataset.id);
            li.remove();
            actualizarMensaje();
        }
    });
});
