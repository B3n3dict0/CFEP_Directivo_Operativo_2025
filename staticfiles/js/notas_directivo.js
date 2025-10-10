document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById('directivo-formulario-nota');
    const textarea = document.getElementById('directivo-texto-nota');
    const inputApartado = document.getElementById('directivo-id-apartado');

    const notasTemporales = {
        produccion: [],
        mantenimiento: [],
        gestion: [],
        seguridad: [],
        superintendencia: []
    };

    let editando = { apartado: null, index: null };
    formulario.style.display = 'none';

    window.directivoMostrarFormulario = function(apartado, index = null) {
        formulario.style.display = 'block';
        inputApartado.value = apartado;

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

    window.directivoCerrarFormulario = function() {
        formulario.style.display = 'none';
        textarea.value = '';
        editando = { apartado: null, index: null };
    }

    window.directivoAgregarNotaTemporal = function() {
        const apartado = inputApartado.value;
        const texto = textarea.value.trim();
        if(texto === '') return false;

        const contenedor = document.getElementById(`notas-temporales-${apartado}`);

        if(editando.index !== null) {
            notasTemporales[apartado][editando.index] = texto;
            const div = contenedor.children[editando.index];
            div.querySelector('span').textContent = texto + ' (Temporal)';
            directivoCerrarFormulario();
            return false;
        }

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

    const formGuardarTodo = document.getElementById('directivo-guardar-todo-form');
    formGuardarTodo.addEventListener('submit', function(e) {
        e.preventDefault();

        const csrfTokenElem = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfToken = csrfTokenElem ? csrfTokenElem.value : '';
        const url = formGuardarTodo.dataset.url;

        const payload = [];
        for(let key in notasTemporales){
            notasTemporales[key].forEach(texto => {
                payload.push({apartado: key, texto: texto});
            });
        }

        if(payload.length === 0) return;

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
                location.reload();
            } else {
                alert("Error al guardar las notas.");
            }
        })
        .catch(err => console.error("Error al enviar notas:", err));
    });
});
