import {AnimatedLineChart } from './graphs.js';
import { AltitudeBar } from './heightBar.js';
// Cargar los datos de vuelo y crear los tres gráficos
fetch('../../data/rocket_flight_data.json')
  .then(res => res.json())
  .then(json => {
    const columns = json.columns;
    //Convertir los datos a una lista de objetos
    // Cada objeto es un diccionario con las columnas como claves
    // y los valores correspondientes de cada fila
    //DataList es una lista de objetos
    const dataList = json.data.map(row => {
      let obj = {};
      columns.forEach((col, i) => { obj[col] = row[i]; });
      return obj;
    });

    // Gráfico 1: velocidad y aceleración
    new AnimatedLineChart(
      'velocityChart',
      dataList,
      ['velocity', 'acceleration'],
      ['Velocidad (m/s)', 'Aceleración (m/s²)'],
      ['rgb(75,192,192)', 'rgb(255,99,132)']
    );
    // Gráfico 2: pitch, yaw, roll
    new AnimatedLineChart(
      'attitudeChart',
      dataList,
      ['pitch', 'yaw', 'roll'],
      ['Pitch (rad)', 'Yaw (rad)', 'Roll (rad)'],
      ['rgb(153,102,255)', 'rgb(54,162,235)', 'rgb(201,203,207)']
    );
    // Gráfico 3: thrust (potencia)
    new AnimatedLineChart(
      'powerChart',
      dataList,
      ['thrust'],
      ['Potencia (N)'],
      ['rgb(255,205,86)']
    );

    // Gráfico 4: Altitud
    bar = new AltitudeBar(  
      dataList,
      {}
    );
  })
