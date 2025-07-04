import {AnimatedLineChart } from './graphs.js';
import { AltitudeBar } from './heightBar.js';
// Cargar los datos de vuelo y crear los tres gráficos
fetch('../../data/rocket_flight_data.json')
  .then(res => res.json())
  .then(json => {
    // Convertir el nuevo formato (columnas como arrays) a lista de objetos por fila
    const keys = Object.keys(json);
    const length = json[keys[0]].length;
    const dataList = Array.from({length}, (_, i) => {
      const obj = {};
      for (const key of keys) {
        obj[key] = json[key][i];
      }
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
