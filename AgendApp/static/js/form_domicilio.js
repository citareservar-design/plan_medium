document.addEventListener('DOMContentLoaded', () => {
  // 1. Elementos del DOM (Asegúrate de que estos IDs existen en tu HTML)
  const domicilioSelect = document.getElementById('domicilio');
  const direccionRow = document.getElementById('direccionRow');
  const costoAdicional = document.getElementById('costoadicional');
  const direccionInput = document.getElementById('direccion');
  const dateInput = document.getElementById('date');
  const form = document.querySelector('form');
  
  // Captura todos los inputs necesarios para preservar los datos
  const nombreInput = document.getElementById('nombre');
  const emailInput = document.getElementById('email');
  const telefonoInput = document.getElementById('telefono');
  const tipoUnaInput = document.getElementById('tipo_una');
  const notasInput = document.getElementById('notas');
  const horaInput = document.getElementById('hora'); // Usado para guardar la hora seleccionada
  
  // Lista de horas libres exportada desde Flask (templates/form.html)
  // Se mantiene, pero la usaremos solo para referencia, no para validación estricta de envío.
  const availableHours = window.HORAS_LIBRES_CLIENTE || []; 

  
  // =========================================================
  // --- Lógica de Domicilio (tu código) ---
  // =========================================================
  function toggleDomicilioFields() {
    if (domicilioSelect && domicilioSelect.value === 'Si') {
      direccionRow.classList.remove('oculto');
      costoAdicional.classList.remove('oculto');
      direccionInput.setAttribute("required", "required");
    } else if (domicilioSelect) {
      direccionRow.classList.add('oculto');
      costoAdicional.classList.add('oculto');
      direccionInput.removeAttribute("required");
      // Nota: No limpiamos el valor aquí para que se capture si el campo estaba oculto al cambiar la fecha.
    }
  }

  // Inicializar y escuchar cambios en el selector de Domicilio
  if (domicilioSelect) {
    toggleDomicilioFields();
    domicilioSelect.addEventListener('change', toggleDomicilioFields);
  }


  // =========================================================
  // --- Lógica CRÍTICA de Recarga de Página al Cambiar la Fecha ---
  // =========================================================
  /**
  * Al cambiar la fecha, recarga la página, guardando todos los datos del formulario 
  * como parámetros de consulta en la URL.
  */
  if (dateInput) {
    dateInput.addEventListener('change', () => {
      const selectedDate = dateInput.value;
      if (!selectedDate) return;

      // 1. Capturar todos los valores del formulario
      const data = {
        // Fecha de recarga (CRÍTICO)
        date: selectedDate, 
        // Resto de campos
        nombre: nombreInput ? nombreInput.value : '',
        email: emailInput ? emailInput.value : '',
        domicilio: domicilioSelect ? domicilioSelect.value : 'No',
        // Aseguramos que la dirección se envíe incluso si el campo está oculto
        direccion: direccionInput ? direccionInput.value : '', 
        notas: notasInput ? notasInput.value : '',
        tipo_una: tipoUnaInput ? tipoUnaInput.value : '',
        telefono: telefonoInput ? telefonoInput.value : '',
        // Enviamos el valor de la hora actual. Flask lo recupera como 'hora_previa'
        hora_previa: horaInput ? horaInput.value : '' 
      };

      // 2. Construir los parámetros de consulta
      const params = new URLSearchParams(data);
      
      // 3. Recarga la página con todos los parámetros
      window.location.href = window.location.pathname + '?' + params.toString();
    });
  }
  
  
  // =========================================================
  // --- Lógica de Validación de Hora antes del Envío (MODIFICADA) ---
  // La validación estricta de superposición se elimina aquí. 
  // Ahora confiamos completamente en la lógica de Flask.
  // Solo se mantiene la validación de "required".
  // =========================================================
  if (form && horaInput) {
    form.addEventListener('submit', (event) => {
      const selectedHour = horaInput.value.trim();
      
      // Si no hay una hora seleccionada, el navegador debe encargarse de la validación 'required'.
      if (!selectedHour) {
        return; 
      }
      
      // Limpiamos la validez personalizada para evitar que se quede pegado el mensaje anterior.
      horaInput.setCustomValidity('');
      
      // Nota: El servidor (Flask) tiene la validación más robusta y es quien debe 
      // confirmar o rechazar la reserva, ya que conoce la duración del servicio.
      // Si la validación de Flask falla, el servidor regresa a /form y muestra el mensaje Flash.
    });
  }


  // =========================================================
  // --- Inicialización del calendario Flatpickr ---
  // =========================================================
  if (dateInput) {
    // flatpickr se inicializará con el valor ya cargado desde Flask (form_data)
    flatpickr(dateInput, {
      dateFormat: "Y-m-d",
      minDate: "today",
      defaultDate: dateInput.value || "today" 
    });
  }
});
