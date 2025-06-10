import * as THREE from 'three';
import { allParticles } from './Particles.js';    


export function createScene(canvas) {
  //scene (with lights and particles)
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x202030);
  createLights(scene);
  allParticles.forEach(particle => particle.addTo(scene));  

  //camera
  const camera = new THREE.PerspectiveCamera(60, canvas.clientWidth / canvas.clientHeight,0.1,1000);
  camera.position.set(0, 2, 6);

  //renderer
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  

  return { scene, camera, renderer};
}


function createLights(space) {
// CREATING LIGHTS
  const sideLight = new THREE.DirectionalLight(0xffffff , 0.5);
  sideLight.position.set(15, 5, 7.5);
  sideLight.castShadow = true;
  sideLight.shadow.mapSize.width = 1024;
  sideLight.shadow.mapSize.height = 1024;
  space.add(sideLight);

  const sunLight1 = new THREE.DirectionalLight(0xFFB347, 5); // Amarillo cálido
  sunLight1.position.set(-0.25, 10, -0.1);
  sunLight1.target.position.set(0, 0, 0);
  sunLight1.castShadow = true;
  sunLight1.shadow.mapSize.width = 4096;
  sunLight1.shadow.mapSize.height = 4096;
  space.add(sunLight1);

  const sunLight2 = new THREE.DirectionalLight(0xFF7043, 5); // Amarillo cálido
  sunLight2.position.set(-0.0, 10, -0.0);
  sunLight2.target.position.set(0, 0, 0);
  sunLight2.castShadow = true;
  sunLight2.shadow.mapSize.width = 4096;
  sunLight2.shadow.mapSize.height = 4096;
  space.add(sunLight2);

  const engineLight = new THREE.SpotLight(0xFF7043, 15); // Amarillo cálido
  engineLight.position.set(0.0, 0, 0.0);
  space.add(engineLight);

  const ambientLight = new THREE.AmbientLight(0xB0C4DE , 0.1);
  space.add(ambientLight);
}
