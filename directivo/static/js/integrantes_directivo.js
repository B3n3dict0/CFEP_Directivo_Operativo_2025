document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("integrantesSelect");
    const lista = document.getElementById("listaSeleccionados");
    const botonAgregar = document.getElementById("agregarSeleccionados");
    const mensajeVacio = document.getElementById("mensajeVacio");
    const formDescargar = document.getElementById("formDescargarPDF");

    // Almacena los seleccionados para evitar duplicados
    const seleccionadosSet = new Set();

    function actualizarMensaje() {
        const count = lista.querySelectorAll("li[data-id]").length;
        mensajeVacio.style.display = count === 0 ? "block" : "none";
        document.getElementById("contadorSeleccionados").textContent = `(${count})`;
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
                li.innerHTML = `${texto} <button class="eliminarBtn" type="button">✕</button>`;
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

    // Función para crear inputs hidden
    function agregarHiddenInputs(nombre, valores) {
        // Eliminar inputs previos
        formDescargar.querySelectorAll(`input[name="${nombre}"]`).forEach(i => i.remove());
        // Crear un input hidden por cada valor
        valores.forEach(valor => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = nombre;
            input.value = valor;
            formDescargar.appendChild(input);
        });
    }

    // Preparar inputs hidden al enviar el formulario
    formDescargar.addEventListener("submit", function () {
        // Integrantes
        const idsIntegrantes = Array.from(lista.querySelectorAll("li[data-id]"))
                                     .map(li => li.dataset.id);
        agregarHiddenInputs("integrantes", idsIntegrantes);

        // Notas seleccionadas
        const idsNotas = Array.from(document.querySelectorAll('input[name="notas_seleccionadas"]:checked'))
                              .map(n => n.value);
        agregarHiddenInputs("notas_seleccionadas", idsNotas);

        // Acuerdos seleccionados
        const idsAcuerdos = Array.from(document.querySelectorAll('input[name="acuerdos_seleccionados"]:checked'))
                                 .map(a => a.value);
        agregarHiddenInputs("acuerdos_seleccionados", idsAcuerdos);
    });
});
