 import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

 export class Rocket {
  constructor(modelPath) {
    this.model = null;
    this.modelPath = modelPath;
    this.initialPosition = { x: 0, y: 0, z: 0 };
  }

  load(scene, onLoaded) {
    const loader = new GLTFLoader();
    loader.load(
      this.modelPath,
      (gltf) => {
        this.model = gltf.scene;
        this.model.position.set(
          this.initialPosition.x,
          this.initialPosition.y,
          this.initialPosition.z
        );
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

  shake(intensity= 0.01) {
    if (this.model) {
      // Limita la vibración alrededor de la posición inicial
      const pos = this.model.position;
      const positionLimit ={x: 1*intensity, y: 1*intensity, z: 1*intensity};
      // Asegura que la posición no se aleje demasiado de la posición inicial
      if (
        Math.abs(pos.x - this.initialPosition.x) < positionLimit.x &&
        Math.abs(pos.y - this.initialPosition.y) < positionLimit.y &&
        Math.abs(pos.z - this.initialPosition.z) < positionLimit.z
      ) {
        pos.x += (Math.random() - 0.5) * intensity / 2;
        pos.y += (Math.random() - 0.5) * intensity;
        pos.z += (Math.random() - 0.5) * intensity / 2;
      } else {
        pos.x = this.initialPosition.x;
        pos.y = this.initialPosition.y;
        pos.z = this.initialPosition.z;
      }
    }
  }
  stTilt(rotation) {
    if (this.model) {
      this.model.rotation.x = rotation.pitch;
      this.model.rotation.y = rotation.roll; 
      this.model.rotation.z = rotation.yaw;
    }
  }
}