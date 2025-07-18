export class AltitudeBar {
  constructor(dataList) {
    this.dataList = dataList;
    this.altitudeKey = 'altitude';
    this.maxAltitude = Math.max(...dataList.map(d => d['altitude'])); //altura máxima
    this.altitudeBar = document.getElementById('altitude-bar');
    this.altitudeLabel = document.getElementById('altitude-label');
    this.altitudeBarFill = document.getElementById('altitude-bar-fill');
    this.minHeight = 20;
    this.maxHeight = 320;
    this.altitudeIndex = 0;
    this.maxReached = 0;
  }

  animate(altitude) {
    if (altitude > this.maxReached) {
      this.maxReached = altitude;
    }
    const percent = Math.max(0, Math.min(altitude / this.maxAltitude, 1));
    const fillHeight = this.minHeight + percent * (this.maxHeight - this.minHeight);
    this.altitudeBarFill.style.height = fillHeight + 'px';
    this.altitudeLabel.textContent = Math.round(altitude) + ' m';

  }
}

