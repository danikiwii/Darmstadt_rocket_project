// Asegúrate de tener <canvas id="chart1"></canvas> en tu HTML
// No importes Chart, ya está disponible como global por el script en el HTML



/**
 * Clase para crear y animar un gráfico de líneas en un canvas específico.
 * Permite graficar una o varias variables y animar la aparición de los datos.
 */
export class AnimatedLineChart {
  /**
   * @param {string} canvasId - id del canvas donde se dibuja el gráfico
   * @param {Array} dataList - lista de objetos con los datos
   * @param {Array} fields - array de strings con los nombres de los campos a graficar
   * @param {Array} labels - array de strings con las etiquetas para cada línea
   * @param {Array} colors - array de strings con los colores de cada línea
   */
  constructor(canvasId, dataList, fields, labels, colors) {
    this.ctx = document.getElementById(canvasId).getContext('2d');
    this.dataList = dataList;
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
          tension: 0.1,
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
          y: { title: { display: true, text: labels[0] } }
        }
      }
    });
    this.i = 0;
    this.animateChart(); // la funcion se autollama. Añade el siguiente punto cada vez
  }

  animateChart() {
    const animateSpeed =30 ; // Ajusta la velocidad de animación aquí. segundos de actualizacion
    // Si hay más datos, añade el siguiente punto al gráfico
    if (this.i < this.dataList.length) {
      this.chart.data.labels.push(this.dataList[this.i].time);
      this.fields.forEach((field, idx) => {
        this.chart.data.datasets[idx].data.push(this.dataList[this.i][field]);
      });
      this.chart.update();
      this.i++;
      setTimeout(() => this.animateChart(), animateSpeed);
    }
  }
}

// Ejemplo de uso:
// import { initLineChart } from './graphs.js';
// initLineChart(dataList, ['velocity', 'acceleration'], ['Velocidad (m/s)', 'Aceleración (m/s²)']);
// Para añadir nuevas líneas en el futuro, puedes agregar más campos y etiquetas en los arrays.
