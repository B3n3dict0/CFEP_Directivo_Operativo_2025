document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("integrantesSelect");
    const lista = document.getElementById("listaSeleccionados");
    const botonAgregar = document.getElementById("agregarSeleccionados");
    const mensajeVacio = document.getElementById("mensajeVacio");
    const formWord = document.getElementById("formDescargarWord");

    const seleccionadosSet = new Set();

    function actualizarMensaje() {
        const count = lista.querySelectorAll("li[data-id]").length;
        mensajeVacio.style.display = count === 0 ? "block" : "none";
        document.getElementById("contadorSeleccionados").textContent = `(${count})`;
    }

    actualizarMensaje();

    // --- Agregar integrantes seleccionados ---
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

    // --- Eliminar integrantes seleccionados ---
    lista.addEventListener("click", function (e) {
        if (e.target.classList.contains("eliminarBtn")) {
            const li = e.target.parentElement;
            seleccionadosSet.delete(li.dataset.id);
            li.remove();
            actualizarMensaje();
        }
    });

    // --- Función para agregar hidden inputs ---
    function agregarHiddenInputs(form, nombre, valores) {
        // Limpiar solo inputs generados con el mismo name
        form.querySelectorAll(`input.generated[name="${nombre}"]`).forEach(i => i.remove());

        valores.forEach(valor => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = nombre;
            input.value = valor;
            input.classList.add("generated"); // marca como generado por JS
            form.appendChild(input);
        });
    }

    // --- Word: agregar hidden inputs al enviar ---
    formWord.addEventListener("submit", function () {
        const idsIntegrantes = Array.from(lista.querySelectorAll("li[data-id]"))
                                     .map(li => li.dataset.id);
        const idsNotas = Array.from(document.querySelectorAll('input[name="notas_seleccionadas"]:checked'))
                              .map(n => n.value);
        const idsAcuerdos = Array.from(document.querySelectorAll('input[name="acuerdos_seleccionados"]:checked'))
                                 .map(a => a.value);

        agregarHiddenInputs(formWord, "integrantes", idsIntegrantes);
        agregarHiddenInputs(formWord, "notas_seleccionadas", idsNotas);
        agregarHiddenInputs(formWord, "acuerdos_seleccionados", idsAcuerdos);
    });
});
