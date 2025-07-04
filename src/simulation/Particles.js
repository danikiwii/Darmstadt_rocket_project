import * as THREE from 'three';

//-----------------------------DEFINING THE PARICLES CLASS


export class Particles {
  constructor({
    count = 200,
    area = 60,
    color = 0xffffff,
    size = 0.1,
    yRange = [5, 15],
    speedRatio = 0.3,
    dataList = null,
    animateSpeed = 30
  } = {}) {
    this.count = count;
    this.area = area;
    this.yRange = yRange;
    this.speedRatio = speedRatio;

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

    // Para animación basada en dataList
    this.dataList = dataList;
    this.animateSpeed = animateSpeed;
    this.i=0;
    this.animate();
  }

  addTo(scene) {
    scene.add(this.points);
  }

  animate() {
    // Lógica similar a animateChart de los gráficos: avanza un frame cada animateSpeed ms
    if (!this.dataList || this.i >= this.dataList.length) return;
    const frame = this.dataList[this.i];
    const speed = frame.velocity || frame.speed || 0;
    const rotation = {
      pitch: frame.pitch || 0,
      yaw: frame.yaw || 0,
      roll: frame.roll || 0
    };
    this.changePosition(speed);
    this.setGroupRotation(rotation);
    this.i++;
    setTimeout(() => this.animate(), this.animateSpeed);
  }

  changePosition(speed) {
    const positions = this.geometry.attributes.position.array;
    for (let i = 0; i < this.count; i++) {
      let xIndex = i * 3;
      let yIndex = i * 3 + 1;
      let zIndex = i * 3 + 2;
      // Actualizar posición Y (cambia con la distancia al cohete y la velocidad)
      positions[yIndex] -= this.speedRatio * speed / (positions[xIndex]**2 + positions[zIndex]**2)**(1/2);
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


  setGroupRotation(rotation) {
    this.points.rotation.x = rotation.pitch;
    this.points.rotation.y = rotation.roll;
    this.points.rotation.z = rotation.yaw;
  }
}


//---------------------------------------------------INSTANCIATE THE PARTICLES

