
document.addEventListener("DOMContentLoaded", function() {
  const tabla = document.getElementById("tabla-acuerdos").getElementsByTagName('tbody')[0];
  const form = document.querySelector("form");

  // Agregar / eliminar filas
  tabla.addEventListener("click", function(e) {
    if (e.target.classList.contains("agregar-fila")) {
      const fila = e.target.closest("tr").cloneNode(true);
      fila.querySelectorAll("input").forEach(input => {
        if(input.type === "text" || input.type === "number") input.value = '';
        if(input.type === "checkbox") input.checked = false;
      });
      tabla.appendChild(fila);
    }

    if (e.target.classList.contains("eliminar-fila")) {
      if(tabla.rows.length > 1){
        e.target.closest("tr").remove();
      } else {
        alert("No se puede eliminar la última fila.");
      }
    }
  });

  // Validación antes de enviar
  form.addEventListener("submit", function(e) {
    let error = false;
    tabla.querySelectorAll("tr").forEach((fila, index) => {
      const numerador = fila.querySelector("input[name='numerador']").value;
      const acuerdo = fila.querySelector("input[name='acuerdo']").value;
      const fecha = fila.querySelector("input[name='fecha_limite']").value;
      const avance = fila.querySelector("input[name='porcentaje_avance']").value;
      const responsable = fila.querySelector("select[name='responsable']").value;

      if (!numerador || !acuerdo || !fecha || !avance || !responsable) {
        alert(`Fila ${index + 1} tiene campos incompletos.`);
        error = true;
      }
      if (avance < 0 || avance > 100) {
        alert(`Fila ${index + 1}: % de avance debe estar entre 0 y 100.`);
        error = true;
      }
    });

    if (error) e.preventDefault(); // Evita enviar si hay error
  });
});
