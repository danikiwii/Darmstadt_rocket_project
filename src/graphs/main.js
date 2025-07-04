import {AnimatedLineChart } from './graphs.js';
import { AltitudeBar } from './heightBar.js';
// Cargar los datos de vuelo y crear los tres gráficos
fetch('../../data/result.json')
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

    const animationSpeed = 100; // Velocidad de animación en milisegundos

    // Chart 1: Speed
    const velocityChart = new AnimatedLineChart(
      'speedChart',
      dataList,
      ['velocity'],
      ['Speed (m/s)'],
      ['rgb(75,192,192)'],
      animationSpeed
    );
    // Chart 2: Acceleration
    const accelerationChart = new AnimatedLineChart(
      'accelerationChart',
      dataList,
      ['acceleration'],
      ['Acceleration (m/s²)'],
      ['rgb(255,99,132)'],
      animationSpeed

    );
    // Chart 3: Pitch, Yaw, Roll
    const rotationChart = new AnimatedLineChart(
      'rotationChart',
      dataList,
      ['pitch', 'yaw', 'roll'],
      ['Pitch (rad)', 'Yaw (rad)', 'Roll (rad)'],
      ['rgb(153,102,255)', 'rgb(54,162,235)', 'rgb(201,203,207)'],
      animationSpeed
    );
    // Chart 4: Altitude
    const altitudeChart = new AnimatedLineChart(
      'altitudeChart',
      dataList,
      ['altitude'],
      ['Altitude (m)'],
      ['rgb(255,205,86)'],
      animationSpeed
    );
     // Atitude Bar
    const bar = new AltitudeBar(  
      dataList,
      animationSpeed
    );
  })

  