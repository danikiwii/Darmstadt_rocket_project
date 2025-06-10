import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export class Rocket {
  constructor(modelPath) {
    this.model = null;
    this.modelPath = modelPath;
  }

  load(scene, onLoaded) {
    const loader = new GLTFLoader();
    loader.load(
      this.modelPath,
      (gltf) => {
        this.model = gltf.scene;
        this.model.position.set(0, 0.5, 0);
        this.model.scale.set(0.02, 0.02, 0.02);
        scene.add(this.model);
        if (onLoaded) onLoaded(this.model);
      },
      undefined,
      (error) => {
        console.error('Error cargando el modelo:', error);
      }
    );
  }

  shake(intensity = 0.02) {
    if (this.model) {
      this.model.position.x += (Math.random() - 0.5) * intensity;
      this.model.position.y += (Math.random() - 0.5) * intensity;
    }
  }
}