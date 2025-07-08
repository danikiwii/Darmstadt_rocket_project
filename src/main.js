import { createScene } from './simulation/scene.js'
import { Rocket } from './simulation/rocket.js'
import { setupControls } from './simulation/controls.js'
import { Particles } from './simulation/Particles.js'
import { AnimatedLineChart } from './graphs/graphs.js'
import { AltitudeBar } from './graphs/heightBar.js'

const canvas = document.getElementById('three-canvas')
const { scene, camera, renderer } = createScene(canvas)
const controls = setupControls(camera, renderer)
const rocket = new Rocket('assets/models/Sagitta2.glb')
rocket.load(scene)

let dataList = []
let frameIndex = 0
let simulationSpeed = 1
let lastUpdate = performance.now()
let speed = 0
let acceleration = 0
let altitude = 0
let rotation = { pitch: 0, yaw: 0, roll: 0 }
let allParticles = []
let allGraphs = []
let bar
let simulationEnded = false

fetch('./weather_data.json')
  .then(r => r.json())
  .then(d => {
    const w = Array.isArray(d) ? d[0] : d
    document.getElementById('w-time').textContent = w.time
    document.getElementById('w-temp').textContent = w.temperature_2m.toFixed(1)
    document.getElementById('w-precip').textContent = w.precipitation.toFixed(1)
    document.getElementById('w-wind').textContent = w.wind_speed_10m.toFixed(1)
  })
  .catch(console.error)

fetch('../processed_data_interp.json')
  .then(res => res.json())
  .then(json => {
    const keys = Object.keys(json)
    const length = json[keys[0]].length
    dataList = Array.from({ length }, (_, i) => {
      const o = {}
      for (const k of keys) o[k] = json[k][i]
      return o
    })

    const rocketParticles_orange = new Particles({
      count: 10,
      area: 0.5,
      color: 0xffa500,
      size: 0.15,
      yRange: [-5, -4.25],
      speedRatio: 0.05
    })
    const rocketParticles_yellow = new Particles({
      count: 10,
      area: 0.5,
      color: 0xffd580,
      size: 0.15,
      yRange: [-6, -4.25],
      speedRatio: 0.05
    })
    const rocketParticles_gray = new Particles({
      count: 20,
      area: 0.25,
      color: 0xcccccc,
      size: 0.15,
      yRange: [-10, -4.25],
      speedRatio: 0.05
    })
    const stars = new Particles({
      count: 200,
      area: 60,
      color: 0xffffff,
      size: 0.35,
      yRange: [-50, 50],
      speedRatio: 12
    })

    allParticles = [stars, rocketParticles_orange, rocketParticles_yellow, rocketParticles_gray]
    allParticles.forEach(p => p.addTo(scene))

    const velocityChart = new AnimatedLineChart('speedChart', ['velocity'], ['Speed (m/s)'], ['rgb(75,192,192)'])
    const accelerationChart = new AnimatedLineChart('accelerationChart', ['acceleration'], ['Acceleration (m/s²)'], ['rgb(255,99,132)'])
    const altitudeChart = new AnimatedLineChart('altitudeChart', ['altitude'], ['Altitude (m)'], ['rgb(255,205,86)'])
    const rotationChart = new AnimatedLineChart(
      'rotationChart',
      ['roll', 'pitch', 'yaw'],
      ['roll (rad)', 'Pitch (rad)', 'Yaw (rad)'],
      ['rgb(255,205,86)', 'rgb(54,162,235)', 'rgb(153,102,255)']
    )

    bar = new AltitudeBar(dataList)
    allGraphs = [velocityChart, accelerationChart, altitudeChart, rotationChart]
  })

function animate() {
  requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)

  if (dataList.length && !simulationEnded) {
    const now = performance.now()
    if (frameIndex < dataList.length - 1 && now - lastUpdate > (1000 / 60) / simulationSpeed) {
      frameIndex++
      const d = dataList[frameIndex]
      speed = d.velocity
      acceleration = d.acceleration
      altitude = d.altitude
      rotation = { pitch: d.pitch, yaw: d.yaw, roll: d.roll }
      rocket.stTilt(rotation)
      allParticles.forEach(p => p.animate(speed, rotation))
      allGraphs.forEach(g => g.animateChart(d))
      bar.animate(altitude)
      lastUpdate = now
    } else if (frameIndex >= dataList.length - 1) {
      simulationEnded = true
    }
  } else {
    rocket.stTilt(rotation)
    allParticles.forEach(p => p.animate(speed, rotation))
  }
}

animate()
