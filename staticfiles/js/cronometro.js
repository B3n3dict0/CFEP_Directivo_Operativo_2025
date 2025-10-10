document.addEventListener("DOMContentLoaded", function () {
    const cronometro = document.getElementById("cronometro");
    const btnIniciar = document.getElementById("btnIniciar");
    const btnPausar = document.getElementById("btnPausar");
    const btnReiniciar = document.getElementById("btnReiniciar");
    const btnCancelar = document.getElementById("btnCancelar");

    let tiempoInicial = 15 * 60; // 32 minutos en segundos
    let tiempoRestante = tiempoInicial;
    let intervalo = null;

    // Función para actualizar el cronómetro en el HTML
    function actualizarCronometro() {
        const minutos = Math.floor(tiempoRestante / 60);
        const segundos = tiempoRestante % 60;
        cronometro.textContent = `${minutos.toString().padStart(2,'0')}:${segundos.toString().padStart(2,'0')}`;
    }

    // Iniciar o reanudar el cronómetro
    function iniciarCronometro() {
        if (intervalo) return; // Evita múltiples intervalos
        intervalo = setInterval(() => {
            if (tiempoRestante > 0) {
                tiempoRestante--;
                actualizarCronometro();
            } else {
                clearInterval(intervalo);
                intervalo = null;
                alert("¡Tiempo de la reunión terminado!");
            }
        }, 1000);
    }

    // Pausar el cronómetro
    function pausarCronometro() {
        if (intervalo) {
            clearInterval(intervalo);
            intervalo = null;
        }
    }

    // Reiniciar el cronómetro y empezar a contar automáticamente
    function reiniciarCronometro() {
        pausarCronometro();
        tiempoRestante = tiempoInicial;
        actualizarCronometro();
        iniciarCronometro();
    }

    // Cancelar el cronómetro y ponerlo en 0
    function cancelarCronometro() {
        pausarCronometro();
        tiempoRestante = 0;
        actualizarCronometro();
    }

    // Enlazar botones con las funciones
    btnIniciar.addEventListener("click", iniciarCronometro);
    btnPausar.addEventListener("click", pausarCronometro);
    btnReiniciar.addEventListener("click", reiniciarCronometro);
    btnCancelar.addEventListener("click", cancelarCronometro);

    // Mostrar tiempo inicial
    actualizarCronometro();
});
