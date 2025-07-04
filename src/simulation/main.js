import { createScene } from './scene.js';
import { Rocket} from './rocket.js';
import { setupControls } from './controls.js';
import { Particles } from './Particles.js';


const canvas = document.getElementById('three-canvas');
const { scene, camera, renderer} = createScene(canvas);
const controls = setupControls(camera, renderer);
const rocket = new Rocket('assets/models/Sagitta2.glb');
//can't put a relative path here, it will not work in the browser


fetch('../../data/result.json')
  .then(res => res.json())
  .then(json => {
    // Convertir formato columnar a lista de objetos por frame
    const keys = Object.keys(json);
    const length = json[keys[0]].length;
    const dataList = Array.from({length}, (_, i) => {
      const obj = {};
      for (const key of keys) {
        obj[key] = json[key][i];
      }
      return obj;
    });


    // Instanciar partículas con dataList y añadirlas a la escena
    const rocketParticles_orange = new Particles({
      count: 10,
      area: 0.5,
      color: 0xffa500,
      size: 0.15,
      yRange: [-5, -4.25 ],
      speedRatio: 0.002,
      dataList,
      animateSpeed: 100
    });
    const rocketParticles_yellow = new Particles({
      count: 10,
      area: 0.5,
      color: 0xFFD580,
      size: 0.15,
      yRange: [-6, -4.25 ],
      speedRatio: 0.002,
      dataList,
      animateSpeed: 100
    });
    const rocketParticles_gray = new Particles({
      count: 20,
      area: 0.25,
      color: 0xCCCCCC, // Gris medio
      size: 0.15,
      yRange: [-10, -4.25],
      speedRatio: 0.003,
      dataList,
      animateSpeed: 100
    });
    const stars = new Particles({
      count: 250,
      area: 60,
      color: 0xffffff,
      size: 0.15,
      yRange: [-50, 50],
      speedRatio: 2,
      dataList,
      animateSpeed: 100
    });

    const allParticles = [stars, rocketParticles_orange, rocketParticles_yellow, rocketParticles_gray];
    allParticles.forEach(particle => particle.addTo(scene));

  });
