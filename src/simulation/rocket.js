import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export function loadRocket(scene) {
  const loader = new GLTFLoader();
  loader.load(
    'src/simulation/models/Sagitta.glb', // Ruta relativa desde la raíz del proyecto
    (gltf) => {
      const rocket = gltf.scene;
      rocket.position.set(0, 0.5, 0);
      rocket.scale.set(0.02, 0.02, 0.02); // Ajusta si es necesario
      scene.add(rocket);
    },
    undefined,
    (error) => {
      console.error('Error cargando el modelo:', error);
    }
  );
}