

export class AltitudeBar {
  constructor(dataList, options = {}) {
    this.dataList = dataList;
    this.maxAltitude = options.maxAltitude || Math.max(...dataList.map(d => d.altitude));
    this.altitudeBar = document.getElementById(options.barId || 'altitude-bar');
    this.altitudeLabel = document.getElementById(options.labelId || 'altitude-label');
    this.altitudeBarFill = document.getElementById(options.fillId || 'altitude-bar-fill');
    this.minHeight = options.minHeight || 20;
    this.maxHeight = options.maxHeight || 160;
    this.altitudeIndex = 0;
    this.maxReached = 0;

    this.animate();
  }

  animate() {
    if (this.altitudeIndex >= this.dataList.length) return;
    const altitude = this.dataList[this.altitudeIndex].altitude;
    if (altitude > this.maxReached) {
      this.maxReached = altitude;
    }
    const percent = Math.max(0, Math.min(this.maxReached / this.maxAltitude, 1));
    const fillHeight = this.minHeight + percent * (this.maxHeight - this.minHeight);
    this.altitudeBarFill.style.height = fillHeight + 'px';
    this.altitudeLabel.textContent = altitude.toFixed(1) + ' m';
    this.altitudeIndex++;
    requestAnimationFrame(() => this.animate());
  }
}

// Ejemplo de uso:
// const bar = new AltitudeBar(dataList);
// bar.animate();
