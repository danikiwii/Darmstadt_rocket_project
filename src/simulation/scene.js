import * as THREE from 'https://unpkg.com/three@0.153.0/build/three.module.js';
  


export function createScene(canvas) {
  //scene (with lights and particles)
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x202030);
  scene.fog = new THREE.FogExp2(0x202030, 0.01); // Añadir niebla para dar profundidad
  createLights(scene);
  // Las partículas se añaden desde main.js, no aquí

  //camera
  const camera = new THREE.PerspectiveCamera(60, canvas.clientWidth / canvas.clientHeight,0.1,1000);
  camera.position.set(0, 5, 6);

  //renderer
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);

  

  return { scene, camera, renderer};
}


function createLights(space) {
  // Luz ambiental blanca más intensa
  const ambientLight = new THREE.AmbientLight(0xfff8e7 , 0.2); // color blanco, intensidad 1.0
  space.add(ambientLight);

  // Luz principal direccional (sol) con intensidad moderada
  const sunLight = new THREE.DirectionalLight(0xffffff, 0.5);
  sunLight.position.set(10, 15, 10);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.width = 2048;
  sunLight.shadow.mapSize.height = 2048;
  sunLight.shadow.radius = 4;
  sunLight.shadow.bias = -0.0005;
  space.add(sunLight);

  // Luz de relleno fría (espacio)
  const fillLight = new THREE.DirectionalLight(0x6699ff, 0.3);
  fillLight.position.set(-5, 5, -5);
  space.add(fillLight);

const warmDirectionalLight = new THREE.DirectionalLight(0xff6600, 0.5); // naranja cálido fuerte
warmDirectionalLight.position.set(0, -2, 5);  // viene un poco desde arriba y delante del cohete
warmDirectionalLight.castShadow = true;
warmDirectionalLight.shadow.mapSize.width = 2048;
warmDirectionalLight.shadow.mapSize.height = 2048;
warmDirectionalLight.shadow.radius = 3;
warmDirectionalLight.shadow.bias = -0.0005;
space.add(warmDirectionalLight);

}
