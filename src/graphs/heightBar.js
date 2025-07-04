

export class AltitudeBar {
  constructor(dataList, animateSpeed = 30) {
    this.dataList = dataList;
    this.animateSpeed = animateSpeed;
    this.altitudeKey = 'altitude';
    this.maxAltitude = Math.max(...dataList.map(d => d['altitude']));
    this.altitudeBar = document.getElementById('altitude-bar');
    this.altitudeLabel = document.getElementById('altitude-label');
    this.altitudeBarFill = document.getElementById('altitude-bar-fill');
    this.minHeight = 20;
    this.maxHeight = 160;
    this.altitudeIndex = 0;
    this.maxReached = 0;

    this.animate();
  }

  animate() {
    if (this.altitudeIndex >= this.dataList.length) {
      // Al terminar, mostrar el valor máximo alcanzado
      this.altitudeLabel.textContent = this.maxReached.toFixed(1) + ' m';
      return;
    }
    const altitude = this.dataList[this.altitudeIndex]['altitude'];

    if (altitude > this.maxReached) {
      this.maxReached = altitude;
    }
    const percent = Math.max(0, Math.min(this.maxReached / this.maxAltitude, 1));
    const fillHeight = this.minHeight + percent * (this.maxHeight - this.minHeight);
    this.altitudeBarFill.style.height = fillHeight + 'px';
    this.altitudeLabel.textContent = altitude.toFixed(1) + ' m';
    this.altitudeIndex++;
    setTimeout(() => this.animate(), this.animateSpeed);
  }
}

