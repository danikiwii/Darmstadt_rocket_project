import { createScene } from './scene.js';
import { Rocket} from './rocket.js';
import { setupControls } from './controls.js';
import {allParticles} from './Particles.js';

const canvas = document.getElementById('three-canvas');
const { scene, camera, renderer} = createScene(canvas);
const controls = setupControls(camera, renderer);
const rocket = new Rocket('assets/Sagitta.glb',{ x: 0, y: 0.5, z: 0 });

rocket.load(scene);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  rocket.shake(0.02); // Ajusta la intensidad del temblor si es necesario
  allParticles.forEach(particle => particle.animate());
}
animate();