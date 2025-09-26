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

    // Inicialmente ocultar el formulario
    formulario.style.display = 'none';

    // Mostrar formulario
    window.mostrarFormulario = function(apartado) {
        formulario.style.display = 'block';
        inputApartado.value = apartado;

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
    }

    // Guardar nota temporal
    window.agregarNotaTemporal = function() {
        const apartado = inputApartado.value;
        const texto = textarea.value.trim();
        if(texto === '') return false;

        // Guardar en array temporal
        notasTemporales[apartado].push(texto);

        // Mostrar en el contenedor correspondiente
        const contenedor = document.getElementById(`notas-temporales-${apartado}`);
        const div = document.createElement('div');
        div.classList.add('nota-item');
        div.textContent = texto + ' (Temporal)';
        contenedor.appendChild(div);

        cerrarFormulario();
        return false; // Evitar submit real
    }

    // Enviar todas las notas temporales al servidor
    const formGuardarTodo = document.getElementById('guardar-todo-form');
    formGuardarTodo.addEventListener('submit', function(e) {
        e.preventDefault();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Preparar payload
        const payload = [];
        for(let key in notasTemporales){
            notasTemporales[key].forEach(texto => {
                payload.push({apartado: key, texto: texto});
            });
        }

        if(payload.length === 0) return; // nada que guardar

        // Enviar fetch POST a una nueva view
        fetch("{% url 'guardar_todo' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({notas: payload})
        }).then(res => {
            if(res.ok){
                location.reload(); // recargar la página con las notas guardadas
            } else {
                alert("Error al guardar las notas.");
            }
        });
    });
});
