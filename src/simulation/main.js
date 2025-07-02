import { createScene } from './scene.js';
import { Rocket} from './rocket.js';
import { setupControls } from './controls.js';
import {allParticles} from './Particles.js';

const canvas = document.getElementById('three-canvas');
const { scene, camera, renderer} = createScene(canvas);
const controls = setupControls(camera, renderer);
const rocket = new Rocket('assets/models/Sagitta.glb',{ x: 0, y: 0.5, z: 0 });
//can't put a relative path here, it will not work in the browser

rocket.load(scene);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  //rocket.shake(0.02); // Ajusta la intensidad del temblor si es necesario
  rocket.stTilt(0.0, 0.0, 0.0); // Ajusta los valores de inclinación
  allParticles.forEach(particle => particle.animate());
}
animate();