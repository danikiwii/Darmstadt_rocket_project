// Asegúrate de tener <canvas id="chart1"></canvas> en tu HTML
// No importes Chart, ya está disponible como global por el script en el HTML



/**
 * Clase para crear y animar un gráfico de líneas en un canvas específico.
 * Permite graficar una o varias variables y animar la aparición de los datos.
 */
export class AnimatedLineChart {
  /**
   * @param {string} canvasId - id del canvas donde se dibuja el gráfico
   * @param {Array} fields - array de strings con los nombres de los campos a graficar
   * @param {Array} labels - array de strings con las etiquetas para cada línea
   * @param {Array} colors - array de strings con los colores de cada línea
   */
  constructor(canvasId, fields, labels, colors) {
    this.ctx = document.getElementById(canvasId).getContext('2d');
    this.fields = fields;
    this.labels = labels;
    this.colors = colors;
    this.chart = new Chart(this.ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: fields.map((field, idx) => ({
          label: labels[idx] || field,
          data: [],
          borderColor: colors[idx % colors.length],
          tension: 0.5,
          fill: false,
          pointRadius: 0
        }))
      },
      options: {
        animation: false,
        elements: { point: { radius: 0 } },
        scales: {
          x: {
            title: { display: false }, // Oculta la leyenda del eje X
            ticks: { display: false }  // Oculta los números del eje X
          },
          y: { title: { display: true } }
        }
      }
    });
  }

  animateChart(dataPoint) {
    // dataPoint es un objeto con los datos del frame actual
    // Agrega la etiqueta de tiempo al eje X
    this.chart.data.labels.push(dataPoint.timestamp);

    // Para cada campo configurado, agrega su valor correspondiente
    this.fields.forEach((field, idx) => {
      this.chart.data.datasets[idx].data.push(dataPoint[field]);
    });

    this.chart.update();
  }
}
