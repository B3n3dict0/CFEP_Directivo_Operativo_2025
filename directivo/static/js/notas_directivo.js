document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById('directivo-formulario-nota');
    const textarea = document.getElementById('directivo-texto-nota');
    const inputApartado = document.getElementById('directivo-id-apartado');

    // Objeto para almacenar notas temporales
    const notasTemporales = {
        produccion: [],
        mantenimiento: [],
        gestion: [],
        seguridad: [],
        superintendencia: []
    };

    // Variable para saber si estamos editando
    let editando = { apartado: null, index: null };

    formulario.style.display = 'none';

    // Mostrar formulario
    window.directivoMostrarFormulario = function(apartado, index = null) {
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
    window.directivoCerrarFormulario = function() {
        formulario.style.display = 'none';
        textarea.value = '';
        editando = { apartado: null, index: null };
    }

    // Guardar o modificar nota temporal
    window.directivoAgregarNotaTemporal = function() {
        const apartado = inputApartado.value;
        const texto = textarea.value.trim();
        if(texto === '') return false;

        const contenedor = document.getElementById(`notas-temporales-${apartado}`);
        if(!contenedor) return false;

        // Si estamos editando
        if(editando.index !== null) {
            // Actualizar array
            notasTemporales[apartado][editando.index] = texto;
            // Actualizar HTML
            const div = contenedor.children[editando.index];
            div.querySelector('span').textContent = texto + ' (Temporal)';
            directivoCerrarFormulario();
            return false;
        }

        // Si es nueva nota
        const index = notasTemporales[apartado].push(texto) - 1;

        const div = document.createElement('div');
        div.classList.add('nota-item');

        const span = document.createElement('span');
        span.textContent = texto + ' (Temporal)';

        const btnModificar = document.createElement('button');
        btnModificar.textContent = 'Modificar';
        btnModificar.classList.add('btn-editar');
        btnModificar.style.marginLeft = '10px';

        btnModificar.addEventListener('click', function() {
            directivoMostrarFormulario(apartado, index);
        });

        div.appendChild(span);
        div.appendChild(btnModificar);
        contenedor.appendChild(div);

        directivoCerrarFormulario();
        return false;
    }

    // Asociar submit del modal al guardar temporal
    const formTemporal = document.getElementById('directivo-form-temporal');
    formTemporal.addEventListener('submit', function(e){
        e.preventDefault();
        directivoAgregarNotaTemporal();
    });

    // Enviar todas las notas al servidor
    const formGuardarTodo = document.getElementById('directivo-guardar-todo-form');
    formGuardarTodo.addEventListener('submit', function(e){
        e.preventDefault();

        const csrfTokenElem = document.querySelector('#directivo-guardar-todo-form [name=csrfmiddlewaretoken]');
        const csrfToken = csrfTokenElem ? csrfTokenElem.value : '';
        const url = formGuardarTodo.dataset.url;

        const payload = JSON.stringify(notasTemporales);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: payload
        })
        .then(response => response.json())
        .then(data => {
            alert('Notas guardadas correctamente!');
            window.location.reload();
        })
        .catch(err => console.error(err));
    });
});
