// Kit para escenas 3D estilo caricatura: materiales "toon" con contorno,
// personajes cabezones, cielo, desierto, cámara con recorrido y subtítulos.
import * as THREE from 'three';
import { OutlineEffect } from 'three/addons/effects/OutlineEffect.js';

export const ANCHO = 1080, ALTO = 1920;
export const AMARILLO = '#ffd600';

// ---------------------------------------------------------------- render
export function crearRender() {
  const gl = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  gl.setPixelRatio(1);
  gl.setSize(ANCHO, ALTO, false);
  gl.outputColorSpace = THREE.SRGBColorSpace;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = THREE.PCFSoftShadowMap;
  const efecto = new OutlineEffect(gl, { defaultThickness: 0.007, defaultColor: [0.16, 0.1, 0.08] });
  const salida = document.createElement('canvas');
  salida.width = ANCHO; salida.height = ALTO;
  const ctx = salida.getContext('2d');
  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(45, ANCHO / ALTO, 0.1, 3000);
  return { gl, efecto, salida, ctx, escena, camara };
}

let _gradiente;
function gradiente() {
  if (!_gradiente) {
    const datos = new Uint8Array([90, 170, 255]);
    _gradiente = new THREE.DataTexture(datos, 3, 1, THREE.RedFormat);
    _gradiente.minFilter = _gradiente.magFilter = THREE.NearestFilter;
    _gradiente.needsUpdate = true;
  }
  return _gradiente;
}

export function toon(color, extra = {}) {
  return new THREE.MeshToonMaterial({ color, gradientMap: gradiente(), ...extra });
}

export function sinContorno(mat) {
  mat.userData.outlineParameters = { visible: false };
  return mat;
}

export function malla(geo, mat, x = 0, y = 0, z = 0, sombra = true) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = sombra;
  m.receiveShadow = true;
  return m;
}

// ----------------------------------------------------------------- mundo
export function luces(escena, sol = [40, 60, 20]) {
  escena.add(new THREE.HemisphereLight(0xcfe8ff, 0xf0a060, 1.3));
  const luz = new THREE.DirectionalLight(0xffffff, 2.2);
  luz.position.set(...sol);
  luz.castShadow = true;
  luz.shadow.mapSize.set(2048, 2048);
  const c = luz.shadow.camera;
  c.left = -60; c.right = 60; c.top = 60; c.bottom = -60; c.near = 1; c.far = 250;
  luz.shadow.bias = -0.0005;
  escena.add(luz);
  return luz;
}

export function cielo(escena, arriba = '#4aa3f0', abajo = '#ffd9a8') {
  const geo = new THREE.SphereGeometry(1200, 32, 16);
  const mat = sinContorno(new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { a: { value: new THREE.Color(arriba) }, b: { value: new THREE.Color(abajo) } },
    vertexShader: 'varying float h; void main(){ h = normalize(position).y; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }',
    fragmentShader: 'uniform vec3 a; uniform vec3 b; varying float h; void main(){ gl_FragColor = vec4(mix(b, a, smoothstep(-0.02, 0.45, h)), 1.0); }',
  }));
  const m = new THREE.Mesh(geo, mat);
  escena.add(m);
  return m;
}

export function sol(escena, x, y, z, r = 22) {
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.SphereGeometry(r, 32, 16), sinContorno(new THREE.MeshBasicMaterial({ color: 0xffdd44 }))));
  const rayoMat = sinContorno(new THREE.MeshBasicMaterial({ color: 0xffc928 }));
  for (let i = 0; i < 12; i++) {
    const rayo = new THREE.Mesh(new THREE.ConeGeometry(r * 0.18, r * 0.6, 4), rayoMat);
    const a = i / 12 * Math.PI * 2;
    rayo.position.set(Math.cos(a) * r * 1.45, Math.sin(a) * r * 1.45, 0);
    rayo.rotation.z = a - Math.PI / 2;
    g.add(rayo);
  }
  g.position.set(x, y, z);
  escena.add(g);
  return g;
}

export function nube(escena, x, y, z, k = 1) {
  const g = new THREE.Group();
  const mat = toon(0xffffff);
  [[0, 0, 0, 5], [5, -1, 0, 4], [-5, -1, 0, 4], [2, 2.5, 0, 4]].forEach(([a, b, c, r]) =>
    g.add(malla(new THREE.SphereGeometry(r * k, 16, 12), mat, a * k, b * k, c * k, false)));
  g.position.set(x, y, z);
  escena.add(g);
  return g;
}

export function desierto(escena) {
  const piso = malla(new THREE.PlaneGeometry(3000, 3000), toon(0xf2a24a), 0, 0, 0, false);
  piso.rotation.x = -Math.PI / 2;
  sinContorno(piso.material);
  escena.add(piso);
  // mesetas
  const rojo = toon(0xe56a6a), rojoOsc = toon(0xc44d62);
  const datos = [[-90, -260, 60, 40], [-30, -330, 45, 30], [70, -280, 70, 45], [150, -380, 80, 55],
                 [-170, -400, 70, 50], [20, -470, 90, 38]];
  datos.forEach(([x, z, r, h]) => {
    const m = malla(new THREE.CylinderGeometry(r * 0.8, r, h, 7), rojo, x, h / 2, z, false);
    const tapa = malla(new THREE.CylinderGeometry(r * 0.82, r * 0.82, h * 0.12, 7), rojoOsc, x, h * 0.94, z, false);
    escena.add(m, tapa);
  });
  // cactus y piedras
  const verde = toon(0x4caf50), piedra = toon(0xc98a52);
  for (let i = 0; i < 26; i++) {
    const lado = i % 2 ? 1 : -1;
    const x = lado * (12 + (i * 37 % 60)), z = 10 - i * 14;
    if (i % 3 === 0) {
      const c = new THREE.Group();
      c.add(malla(new THREE.CapsuleGeometry(0.8, 4, 6, 12), verde, 0, 2.6, 0));
      const brazo = malla(new THREE.CapsuleGeometry(0.5, 1.6, 6, 12), verde, 1.2, 3.2, 0);
      c.add(brazo);
      c.position.set(x, 0, z);
      escena.add(c);
    } else {
      escena.add(malla(new THREE.DodecahedronGeometry(0.8 + (i % 4) * 0.4), piedra, x, 0.4, z));
    }
  }
}

// --------------------------------------------------------------- personajes
const PIEL = 0xffdcb8;
export function cabezon({ ropa = 0x2f6fd6, sombrero = 'casco', k = 1 } = {}) {
  const g = new THREE.Group();
  const matRopa = toon(ropa), matPiel = toon(PIEL), oscuro = toon(0x3a3a4a), negro = toon(0x221a18);
  const piernas = [-0.28, 0.28].map(x => {
    const p = malla(new THREE.CapsuleGeometry(0.2, 0.6, 6, 12), oscuro, x, 0.5, 0);
    g.add(p);
    g.add(malla(new THREE.SphereGeometry(0.26, 12, 8), negro, x, 0.12, 0.1));
    return p;
  });
  const cuerpo = malla(new THREE.CapsuleGeometry(0.62, 0.7, 8, 16), matRopa, 0, 1.45, 0);
  g.add(cuerpo);
  // chaleco reflejante (detalle)
  const franja = malla(new THREE.TorusGeometry(0.66, 0.06, 6, 24), toon(0xfff07a), 0, 1.35, 0);
  franja.rotation.x = Math.PI / 2;
  g.add(franja);
  const brazos = [-1, 1].map(lado => {
    const hombro = new THREE.Group();
    hombro.position.set(lado * 0.72, 1.85, 0);
    const b = malla(new THREE.CapsuleGeometry(0.17, 0.7, 6, 12), matRopa, 0, -0.45, 0);
    const mano = malla(new THREE.SphereGeometry(0.2, 12, 8), matPiel, 0, -0.9, 0);
    hombro.add(b, mano);
    hombro.rotation.z = lado * 0.25;
    g.add(hombro);
    return hombro;
  });
  const cabeza = new THREE.Group();
  cabeza.position.set(0, 3.05, 0);
  cabeza.add(malla(new THREE.SphereGeometry(1.0, 32, 24), matPiel));
  [-0.34, 0.34].forEach(x => {
    cabeza.add(malla(new THREE.SphereGeometry(0.11, 12, 8), negro, x, 0.05, 0.94, false));
    const mejilla = malla(new THREE.SphereGeometry(0.15, 12, 8), sinContorno(toon(0xff9f9a)), x * 1.6, -0.25, 0.83, false);
    mejilla.scale.z = 0.4;
    cabeza.add(mejilla);
  });
  const boca = malla(new THREE.TorusGeometry(0.22, 0.045, 8, 16, Math.PI), negro, 0, -0.28, 0.93, false);
  boca.rotation.z = Math.PI;
  cabeza.add(boca);
  if (sombrero === 'casco' || sombrero === 'casco_blanco') {
    const mat = toon(sombrero === 'casco' ? 0xffcc1a : 0xf5f5f5);
    const domo = malla(new THREE.SphereGeometry(1.06, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), mat, 0, 0.15, 0);
    const ala = malla(new THREE.CylinderGeometry(1.25, 1.25, 0.1, 32), mat, 0, 0.18, 0.12);
    const cresta = malla(new THREE.BoxGeometry(0.16, 0.25, 1.9), mat, 0, 1.05, 0);
    cabeza.add(domo, ala, cresta);
  } else if (sombrero === 'copa') {
    const mat = toon(0x231c26);
    cabeza.add(malla(new THREE.CylinderGeometry(0.65, 0.65, 1.2, 24), mat, 0, 1.35, 0),
               malla(new THREE.CylinderGeometry(1.05, 1.05, 0.08, 24), mat, 0, 0.78, 0),
               malla(new THREE.CylinderGeometry(0.66, 0.66, 0.2, 24), toon(0xc8283a), 0, 0.92, 0));
  }
  g.add(cabeza);
  g.scale.setScalar(k);
  g.userData = { cabeza, brazos, piernas, cuerpo };
  return g;
}

// Pequeño rebote al estar parado
export function respirar(p, t) {
  const { cabeza, cuerpo } = p.userData;
  cabeza.position.y = 3.05 + Math.sin(t * 5) * 0.05;
  cuerpo.scale.y = 1 + Math.sin(t * 5) * 0.015;
}

// ----------------------------------------------------------- animación
export const suave = x => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
export const frena = x => { x = Math.min(1, Math.max(0, x)); return 1 - (1 - x) * (1 - x); };
export const rebote = x => { x = Math.min(1, Math.max(0, x)); const c1 = 1.70158, c3 = 2.70158; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2; };

// claves: [[t, [x,y,z]], ...] con interpolación suave
export function recorrido(claves, t) {
  if (t <= claves[0][0]) return new THREE.Vector3(...claves[0][1]);
  for (let i = 0; i < claves.length - 1; i++) {
    const [t0, a] = claves[i], [t1, b] = claves[i + 1];
    if (t <= t1) {
      const k = suave((t - t0) / (t1 - t0));
      return new THREE.Vector3(...a).lerp(new THREE.Vector3(...b), k);
    }
  }
  return new THREE.Vector3(...claves[claves.length - 1][1]);
}

// ----------------------------------------------------------- subtítulos
export async function cargarFuente() {
  const f = new FontFace('Anton', 'url(/fuentes/Anton-Regular.ttf)');
  await f.load();
  document.fonts.add(f);
}

// subs: [[t, 'TEXTO', amarillo?], ...]
export function subtitulos(ctx, subs, t, y = 0.46 * ALTO) {
  let actual = null;
  for (const s of subs) { if (s[0] <= t) actual = s; else break; }
  if (!actual || actual[1] === '') return;
  const p = (t - actual[0]) / 0.14;
  const k = p < 1 ? 0.72 + 0.28 * rebote(p) : 1;
  const tam = 118 * k;
  ctx.save();
  ctx.font = `${tam}px Anton`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.lineJoin = 'round';
  ctx.lineWidth = tam * 0.2;
  ctx.strokeStyle = '#000';
  ctx.fillStyle = '#000';
  ctx.strokeText(actual[1], ANCHO / 2 + 7, y + 7);
  ctx.strokeText(actual[1], ANCHO / 2, y);
  ctx.fillStyle = actual[2] ? AMARILLO : '#fff';
  ctx.fillText(actual[1], ANCHO / 2, y);
  ctx.restore();
}

export function componer(r, subs, t) {
  r.efecto.render(r.escena, r.camara);
  r.ctx.drawImage(r.gl.domElement, 0, 0);
  if (subs) subtitulos(r.ctx, subs, t);
  return r.salida.toDataURL('image/jpeg', 0.9);
}
