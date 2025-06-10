import { createScene } from './scene.js';
import { loadRocket } from './rocket.js';
import { setupControls } from './controls.js';
import {allParticles} from './Particles.js';

const canvas = document.getElementById('three-canvas');
const { scene, camera, renderer} = createScene(canvas);
loadRocket(scene);
const controls = setupControls(camera, renderer);

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  allParticles.forEach(particle => particle.animate());
  renderer.render(scene, camera);
}
animate();