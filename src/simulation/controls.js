import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export function setupControls(camera, renderer) {
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enableRotate = true;    // Allows camera rotation with the mouse
  controls.enablePan = true;       // Allows camera panning with the mouse
  controls.enableZoom = true;
  controls.minDistance = 4;  // Distancia mínima de zoom
  controls.maxDistance = 30; // Distancia máxima de zoom      // Allows zooming with the mouse wheel
  return controls;
}