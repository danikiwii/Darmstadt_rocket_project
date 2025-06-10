import * as THREE from 'three';

//-----------------------------DEFINING THE PARICLES CLASS


class Particles {
  constructor({
    count = 200,
    area = 60,
    color = 0xffffff,
    size = 0.1,
    yRange = [5, 15],
    velocity = 0.3,
  } = {}) {
    this.count = count;
    this.area = area;
    this.yRange = yRange;
    this.velocity = velocity;

    this.geometry = new THREE.BufferGeometry();
    this.positions = [];

    for (let i = 0; i < count; i++) {
      this.positions.push(
        (Math.random() - 0.5) * area, // X
        Math.random() * (yRange[1] - yRange[0]) + yRange[0], // Y
        (Math.random() - 0.5) * area  // Z
      );
    }

    this.geometry.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(this.positions, 3)
    );
    this.material = new THREE.PointsMaterial({ color, size });
    this.points = new THREE.Points(this.geometry, this.material);
  }

  addTo(scene) {
    scene.add(this.points);
  }

  animate() {
    this.changePosition();
    }

  changePosition() {
    const positions = this.geometry.attributes.position.array;
    for (let i = 0; i < this.count; i++) {
      let xIndex = i * 3;
      let yIndex = i * 3 + 1;
      let zIndex = i * 3 + 2;
      // Actualizar posición Y (cambia con la distancia al cohete)
      positions[yIndex] -= this.velocity /(positions[xIndex]**2 + positions[zIndex]**2)**(1/2);
      if (positions[yIndex] < this.yRange[0]) {
        // Resetear posición Y si cae por debajo del rango
        positions[yIndex] = this.yRange[1];
        // Reposicionar X y Z aleatoriamente dentro del área
        positions[xIndex] = (Math.random() - 0.5) * this.area;
        positions[zIndex] = (Math.random() - 0.5) * this.area;
      }
    }
    this.geometry.attributes.position.needsUpdate = true;
  }
}


//---------------------------------------------------INSTANCIATE THE PARTICLES

const stars = new Particles({
  count: 250,
  area: 60,
  color: 0xffffff,
  size: 0.15,
  yRange: [-50, 50],
  velocity: 2
});


const rocketParticles_orange = new Particles({
  count: 10,
  area: 0.5,
  color: 0xffa500,
  size: 0.15,
  yRange: [-5, -3.75 ],
  velocity: 0.005,
});
const rocketParticles_yellow = new Particles({
  count: 10,
  area: 0.5,
  color: 0xFFD580,
  size: 0.15,
  yRange: [-4, -3.75 ],
  velocity: 0.005,
});
const rocketParticles_gray = new Particles({
  count: 20,
  area: 0.25,
  color: 0xCCCCCC, // Gris medio
  size: 0.15,
  yRange: [-10, -3.75],
  velocity: 0.01,
});

export const allParticles = [
  stars, 
  rocketParticles_orange, 
  rocketParticles_yellow,
  rocketParticles_gray
];
// Combine the orange and yellow particles into a single object