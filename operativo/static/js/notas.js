document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById('formulario-nota');
    const textarea = document.getElementById('texto_nota');
    const inputApartado = document.getElementById('id_apartado');

    // Objeto para almacenar notas temporales
    const notasTemporales = {
        produccion: [],
        mantenimiento: [],
        seguridad: [],
        superintendencia: []
    };

    // Variable para saber si estamos editando
    let editando = { apartado: null, index: null };

    // Inicialmente ocultar el formulario
    formulario.style.display = 'none';

    // Mostrar formulario
    window.mostrarFormulario = function(apartado, index = null) {
        formulario.style.display = 'block';
        inputApartado.value = apartado;

        // Si estamos editando, cargar el texto
        if(index !== null) {
            textarea.value = notasTemporales[apartado][index];
            editando = { apartado, index };
        } else {
            textarea.value = '';
            editando = { apartado: null, index: null };
        }

        formulario.style.position = 'fixed';
        formulario.style.top = '50%';
        formulario.style.left = '50%';
        formulario.style.transform = 'translate(-50%, -50%)';
        formulario.style.backgroundColor = '#fff';
        formulario.style.padding = '20px';
        formulario.style.border = '2px solid #8B0000';
        formulario.style.borderRadius = '8px';
        formulario.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        formulario.style.zIndex = '1000';
    }

    // Cerrar formulario
    window.cerrarFormulario = function() {
        formulario.style.display = 'none';
        textarea.value = '';
        editando = { apartado: null, index: null };
    }

    // Guardar nota temporal o actualizar
    window.agregarNotaTemporal = function() {
        const apartado = inputApartado.value;
        const texto = textarea.value.trim();
        if(texto === '') return false;

        const contenedor = document.getElementById(`notas-temporales-${apartado}`);

        // Si estamos editando
        if(editando.index !== null) {
            // Actualizar array
            notasTemporales[apartado][editando.index] = texto;
            // Actualizar HTML
            const div = contenedor.children[editando.index];
            div.querySelector('span').textContent = texto + ' (Temporal)';
            cerrarFormulario();
            return false;
        }

        // Si es una nueva nota
        const index = notasTemporales[apartado].push(texto) - 1;

        const div = document.createElement('div');
        div.classList.add('nota-item');

        const span = document.createElement('span');
        span.textContent = texto + ' (Temporal)';

        // Botón modificar
        const btnModificar = document.createElement('button');
        btnModificar.textContent = 'Modificar';
        btnModificar.classList.add('btn-editar');
        btnModificar.style.marginLeft = '10px';

        btnModificar.addEventListener('click', function() {
            mostrarFormulario(apartado, index);
        });

        div.appendChild(span);
        div.appendChild(btnModificar);
        contenedor.appendChild(div);

        cerrarFormulario();
        return false; // Evitar submit real
    }

    // Enviar todas las notas temporales al servidor
    const formGuardarTodo = document.getElementById('guardar-todo-form');
    formGuardarTodo.addEventListener('submit', function(e) {
        e.preventDefault();

        const csrfTokenElem = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfTokenElem ? csrfTokenElem.value : '';
        const url = formGuardarTodo.dataset.url;

        // Preparar payload
        const payload = [];
        for(let key in notasTemporales){
            notasTemporales[key].forEach(texto => {
                payload.push({apartado: key, texto: texto});
            });
        }

        if(payload.length === 0) return; // nada que guardar

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({notas: payload})
        })
        .then(res => {
            if(res.ok){
                location.reload(); // recargar la página con las notas guardadas
            } else {
                alert("Error al guardar las notas.");
            }
        })
        .catch(err => console.error("Error al enviar notas:", err));
    });
});
