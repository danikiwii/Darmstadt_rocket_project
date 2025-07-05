import { createScene } from './scene.js';
import { Rocket} from './rocket.js';
import { setupControls } from './controls.js';
import { Particles } from './Particles.js';


const canvas = document.getElementById('three-canvas');
const { scene, camera, renderer} = createScene(canvas);
const controls = setupControls(camera, renderer);
const rocket = new Rocket('assets/models/Sagitta2.glb');
//can't put a relative path here, it will not work in the browser

rocket.load(scene);


// Variables para la simulación
let dataList = [];
let frameIndex = 0;
let simulationSpeed = 1; // 1 = tiempo real, 2 = doble de rápido, etc.
let lastUpdate = performance.now();
let speed = 0;
let rotation = { pitch: 0, yaw: 0, roll: 0 };
let allParticles = [];

// Instanciar partículas y cargar datos
fetch('../../data/result.json')
  .then(res => res.json())
  .then(json => {
    const keys = Object.keys(json);
    const length = json[keys[0]].length;
    dataList = Array.from({ length }, (_, i) => {
      const obj = {};
      for (const key of keys) obj[key] = json[key][i];
      return obj;
    });

    // Instanciar partículas con dataList si lo necesitas para animación basada en datos
    const rocketParticles_orange = new Particles({
      count: 10,
      area: 0.5,
      color: 0xffa500,
      size: 0.15,
      yRange: [-5, -4.25],
      speedRatio: 0.002
    });
    const rocketParticles_yellow = new Particles({
      count: 10,
      area: 0.5,
      color: 0xFFD580,
      size: 0.15,
      yRange: [-6, -4.25],
      speedRatio: 0.002
    });
    const rocketParticles_gray = new Particles({
      count: 20,
      area: 0.25,
      color: 0xCCCCCC,
      size: 0.15,
      yRange: [-10, -4.25],
      speedRatio: 0.003
    });
    const stars = new Particles({
      count: 250,
      area: 60,
      color: 0xffffff,
      size: 0.15,
      yRange: [-50, 50],
      speedRatio: 2
    });
    allParticles = [stars, rocketParticles_orange, rocketParticles_yellow, rocketParticles_gray];
    allParticles.forEach(particle => particle.addTo(scene));
  });

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);

  // Actualizar frame según simulationSpeed y datos
  if (dataList.length > 0) {
    const now = performance.now();
    // Avanza el frame según simulationSpeed (ajusta 60 para tu FPS objetivo)
    if (now - lastUpdate > (1000 / 60) / simulationSpeed) {
      frameIndex = Math.min(frameIndex + 1, dataList.length - 1);
      speed = dataList[frameIndex].velocity;
      rotation = {
        pitch: dataList[frameIndex].pitch,
        yaw: dataList[frameIndex].yaw,
        roll: dataList[frameIndex].roll
      };
      lastUpdate = now;
    }
  }

  rocket.stTilt(rotation);
  allParticles.forEach(particle => particle.animate(speed, rotation));
}
animate();