function gestionarSeguimientoTareas() {
  // Obtiene el libro de cálculo de Google Sheets que está activo actualmente
  const libro = SpreadsheetApp.getActiveSpreadsheet();
  
  // Busca la pestaña por su nombre exacto. Si no la encuentra, usa la pestaña que esté abierta en pantalla
  const hoja = libro.getSheetByName("Tareas atrasadas Turing IA") || libro.getActiveSheet();
  
  // Extrae absolutamente todos los datos escritos en la hoja y los guarda en una matriz bidimensional (filas y columnas)
  const datos = hoja.getDataRange().getValues();
  
  // Crea un objeto con la fecha y hora exacta del momento en que se corre el script
  const hoy = new Date();
  
  // Resetea las horas, minutos y segundos a 0 para que la comparación matemática de fechas sea exacta a medianoche
  hoy.setHours(0, 0, 0, 0); 

  // Inicia un bucle para recorrer las filas. Comienza en i = 1 para saltarse la fila 0 (que son los encabezados)
  for (let i = 1; i < datos.length; i++) {
    const fila = datos[i]; // Guarda la información completa de la fila actual que se está analizando
    const tarea = fila[2]; // Extrae el texto de la columna C (Nombre de la tarea)
    const responsable = fila[3]; // Extrae el texto de la columna D (Persona responsable)
    const email = fila[4]; // Extrae el correo de la columna E
    const fechaLimite = new Date(fila[5]); // Extrae la fecha de la columna F y la convierte a formato de fecha estándar
    const estadoActual = fila[6]; // Extrae el estado de la columna G (Pendiente, Completado, etc.)
    
    const filaReal = i + 1; // Guarda el número físico de la fila en el Excel (Ejemplo: el índice 1 es la fila 2 física)

    // Si la celda de tarea está vacía o si ya fue completada, entra a este bloque de descarte
    if (!tarea || estadoActual === "Completado") {
      if (estadoActual === "Completado") {
         hoja.getRange(filaReal, 8).setValue("-"); // Escribe una raya en la columna de días restantes (H)
         hoja.getRange(filaReal, 9).setValue("Finalizado ✅"); // Escribe el texto de éxito en la columna de Alerta (I)
         hoja.getRange(filaReal, 9).setBackground("#b6d7a8"); // Pinta la celda de color verde claro
      }
      continue; // Detiene el análisis de esta fila y salta automáticamente a la siguiente fila del bucle
    }

    // Resetea las horas de la fecha límite a medianoche para restarla justamente contra el día de hoy
    fechaLimite.setHours(0, 0, 0, 0);
    
    // Resta las dos fechas. El resultado de JavaScript siempre se da en milisegundos
    const diferenciaMilisegundos = fechaLimite.getTime() - hoy.getTime();
    
    // Divide los milisegundos entre los milisegundos que tiene 1 día completo y redondea hacia abajo
    const diasRestantes = Math.floor(diferenciaMilisegundos / (1000 * 60 * 60 * 24));

    // Escribe el número de días restantes calculado en la Columna H (Columna 8 del Sheets)
    hoja.getRange(filaReal, 8).setValue(diasRestantes);

    // Declara variables vacías que se llenarán dependiendo de la urgencia de la tarea
    let estadoAlerta = "";
    let colorFondo = "#ffffff";
    let enviarNotificacion = false;

    // Regla 1: Si los días restantes son menores a 0, significa que la tarea está vencida
    if (diasRestantes < 0) {
      estadoAlerta = "⚠️ ATRASADO";
      colorFondo = "#ff9999"; // Color Rojo claro
      enviarNotificacion = true; // Activa el permiso de mandar un correo
      
    // Regla 2: Si quedan entre 0 y 2 días, la tarea es urgente
    } else if (diasRestantes <= 2) {
      estadoAlerta = "⏳ URGENTE (Menos de 48h)";
      colorFondo = "#ffe599"; // Color Amarillo claro
      enviarNotificacion = true; // Activa el permiso de mandar un correo
      
    // Regla 3: Si quedan más de 2 días, la tarea va a tiempo
    } else {
      estadoAlerta = "👍 En tiempo";
      colorFondo = "#cfe2f3"; // Color Azul claro
    }

    // Selecciona la celda física de la columna I (Columna 9 de Alerta)
    const celdaAlerta = hoja.getRange(filaReal, 9);
    celdaAlerta.setValue(estadoAlerta); // Imprime el texto de alerta (Atrasado, Urgente o En tiempo)
    celdaAlerta.setBackground(colorFondo); // Pinta el fondo de la celda del color correspondiente

    // Si el semáforo marcó que amerita correo y la celda del email no está vacía, procede
    if (enviarNotificacion && email) {
      // Llama a la siguiente función de Gmail pasándole los datos de la fila analizada
      notificarResponsable(email, responsable, tarea, estadoAlerta, diasRestantes);
    }
  }
}
function notificarResponsable(email, responsable, tarea, alerta, dias) {
  // Construye el título del correo electrónico dinámicamente usando el nombre de la tarea
  const asunto = `[Recordatorio] Tarea de Proyecto: ${tarea}`;
  
  // Evalúa si el número de días es negativo para redactar el texto gramaticalmente correcto
  let mensajeDias = dias < 0 
    ? `está atrasada por ${Math.abs(dias)} día(s).` // Math.abs convierte el -3 en un 3 positivo para que se lea bien
    : `vence en ${dias} día(s). ¡Es hora de priorizarla!`;

  // Construye el cuerpo del correo saltando líneas con el símbolo "\n"
  const cuerpo = `Hola ${responsable},\n\n` +
                 `Este es un mensaje automatizado del sistema.\n` +
                 `La tarea "${tarea}" marcada como "${alerta}", ${mensajeDias}\n\n` +
                 `Por favor, actualiza el estado en la hoja de cálculo cuando finalices.\n\n` +
                 `Saludos,\nSistema de Gestión.`;

  // Usa la API de Gmail de Google para escupir el correo a la bandeja de entrada del destinatario
  GmailApp.sendEmail(email, asunto, cuerpo);
}
function sincronizarConCalendar() {
  // Vuelve a conectarse al libro activo de Google Sheets
  const libro = SpreadsheetApp.getActiveSpreadsheet();
  
  // Abre la pestaña de Tareas o la activa por defecto
  const hoja = libro.getSheetByName("Tareas atrasadas Turing IA") || libro.getActiveSheet();
  
  // Extrae la matriz completa de datos del Excel
  const datos = hoja.getDataRange().getValues();
  
  // Se conecta a la aplicación de Google Calendar principal del usuario de la cuenta
  const calendario = CalendarApp.getDefaultCalendar();
  
  // Identifica el huso horario del libro de Google Sheets (Evita desfases de horas)
  const zonaHoraria = libro.getSpreadsheetTimeZone(); 

  // Comienza a leer las filas desde la fila 2 física (índice 1 del bucle)
  for (let i = 1; i < datos.length; i++) {
    const fila = datos[i];
    const proyecto = fila[1]; // Columna B (Proyecto)
    const tarea = fila[2]; // Columna C (Tarea)
    const responsable = fila[3]; // Columna D (Responsable)
    const estado = fila[6]; // Columna G (Estado)
    const yaSincronizado = fila[9]; // Columna J (Index 9 - Validador de Calendar)

    const filaReal = i + 1; // Mapea el renglón físico de la hoja

    // Si la celda de la fecha límite (Columna F / Indice 5) está vacía, ignora la fila y pasa a la siguiente
    if (!fila[5]) continue; 
    
    // Toma la fecha escrita en el Excel
    const fechaOriginal = new Date(fila[5]);
    
    // Limpia la fecha quitándole desfases de horas de verano usando el formato Año-Mes-Día
    const fechaFormateada = Utilities.formatDate(fechaOriginal, zonaHoraria, "yyyy-MM-dd");
    
    // Fuerza a crear un objeto de fecha limpio clavado exactamente a medianoche (T00:00:00)
    const fechaFinal = new Date(fechaFormateada + "T00:00:00"); 

    // Regla de Negocio: Si hay tarea, no está completada y en la columna J NO dice "SÍ"
    if (tarea && estado !== "Completado" && yaSincronizado !== "SÍ") {
      
      // Crea los textos que se verán estéticos en el calendario del celular
      const tituloEvento = `[${proyecto}] Entregar: ${tarea}`;
      const descripcion = `Responsable: ${responsable}\nEstado actual: ${estado}`;

      // Abre un bloque Try-Catch para atrapar errores y que el código no se rompa de golpe
      try {
        // Ejecuta la API de Calendar para crear un recordatorio de día completo
        calendario.createAllDayEvent(tituloEvento, fechaFinal, {
          description: descripcion
        });

        // Escribe "SÍ" en la columna J para bloquear que el script vuelva a duplicar esta tarea mañana
        hoja.getRange(filaReal, 10).setValue("SÍ");
        
        // Imprime en la consola de programador que todo salió exitoso
        Logger.log(`✅ Evento creado en Calendar para: ${tarea}`);
      } catch (error) {
        // Si el servidor de Google falla, imprime el error en la consola sin detener el flujo de la hoja
        Logger.log(`❌ Error al crear evento para ${tarea}: ` + error.toString());
      }
    }
  }
}
