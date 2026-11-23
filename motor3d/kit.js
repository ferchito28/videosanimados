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
  const hemi = new THREE.HemisphereLight(0xcfe8ff, 0xf0a060, 1.3);
  escena.add(hemi);
  const luz = new THREE.DirectionalLight(0xffffff, 2.2);
  luz.position.set(...sol);
  luz.castShadow = true;
  luz.shadow.mapSize.set(2048, 2048);
  const c = luz.shadow.camera;
  c.left = -60; c.right = 60; c.top = 60; c.bottom = -60; c.near = 1; c.far = 250;
  luz.shadow.bias = -0.0005;
  escena.add(luz, luz.target);
  luz.userData.hemi = hemi;
  luz.userData.offset = new THREE.Vector3(...sol);
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
export const acelera = x => { x = Math.min(1, Math.max(0, x)); return x * x; };
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
export function subtitulos(ctx, subs, t, y = 0.72 * ALTO) {
  let actual = null;
  for (const s of subs) { if (s[0] <= t) actual = s; else break; }
  if (!actual || actual[1] === '') return;
  const p = (t - actual[0]) / 0.14;
  const k = p < 1 ? 0.72 + 0.28 * rebote(p) : 1;
  let tam = 118 * k;
  ctx.save();
  ctx.font = `${tam}px Anton`;
  const ancho = ctx.measureText(actual[1]).width;
  if (ancho > ANCHO * 0.86) { tam *= ANCHO * 0.86 / ancho; ctx.font = `${tam}px Anton`; }
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
  return r.salida.toDataURL('image/jpeg', 0.96);
}

// ----------------------------------------------------------- utilería 3D
export function mezcladora(escena, x, z, rotY = 0) {
  const g = new THREE.Group();
  const blanco = toon(0xf2f2f2), naranja = toon(0xff7a1f), gris = toon(0x55555c), negro = toon(0x222226);
  g.add(malla(new THREE.BoxGeometry(2.6, 0.5, 8), gris, 0, 1.1, 0));
  const cab = malla(new THREE.BoxGeometry(2.6, 2.3, 2.2), naranja, 0, 2.3, 3.4);
  g.add(cab, malla(new THREE.BoxGeometry(2.3, 0.9, 0.1), sinContorno(toon(0x9fd3ff)), 0, 2.9, 4.52, false));
  const tambor = malla(new THREE.CylinderGeometry(1.15, 1.45, 4.6, 20), blanco, 0, 2.9, -1.2);
  tambor.rotation.x = Math.PI / 2 - 0.25;
  g.add(tambor);
  for (let i = 0; i < 3; i++) {
    const banda = malla(new THREE.TorusGeometry(1.32 - i * 0.08, 0.1, 8, 24), naranja, 0, 2.9 + (i - 1) * 0.35, -1.2 + (i - 1) * 1.3);
    banda.rotation.x = -0.25; g.add(banda);
  }
  [[-1.3, 3], [1.3, 3], [-1.3, -1.6], [1.3, -1.6], [-1.3, -3], [1.3, -3]].forEach(([wx, wz]) => {
    const r = malla(new THREE.CylinderGeometry(0.6, 0.6, 0.5, 18), negro, wx, 0.6, wz);
    r.rotation.z = Math.PI / 2; g.add(r);
  });
  g.position.set(x, 0, z); g.rotation.y = rotY;
  escena.add(g);
  g.userData.tambor = tambor;
  return g;
}

export function casa(escena, x, z, w = 8, h = 6, d = 7, color = 0xe9b96e) {
  const g = new THREE.Group();
  g.add(malla(new THREE.BoxGeometry(w, h, d), toon(color), 0, h / 2, 0));
  g.add(malla(new THREE.BoxGeometry(w + 0.6, 0.5, d + 0.6), toon(0x9c4b3a), 0, h + 0.25, 0));
  const vidrio = sinContorno(toon(0x8fd0ff)), marco = toon(0xffffff);
  for (let i = 0; i < Math.floor(w / 2.6); i++) {
    const wx = -w / 2 + 1.6 + i * 2.6;
    for (let piso = 0; piso < Math.floor(h / 3); piso++) {
      g.add(malla(new THREE.BoxGeometry(1.3, 1.4, 0.2), marco, wx, 1.8 + piso * 3, d / 2 + 0.02, false));
      g.add(malla(new THREE.BoxGeometry(1.0, 1.1, 0.25), vidrio, wx, 1.8 + piso * 3, d / 2 + 0.05, false));
    }
  }
  g.position.set(x, 0, z);
  escena.add(g);
  return g;
}

export function tanqueAgua(escena, x, z) {
  const g = new THREE.Group(), madera = toon(0xa0643a), metal = toon(0x6a6a72);
  [[-2, -2], [2, -2], [-2, 2], [2, 2]].forEach(([a, b]) => g.add(malla(new THREE.CylinderGeometry(0.25, 0.3, 10, 8), madera, a, 5, b)));
  g.add(malla(new THREE.CylinderGeometry(3.2, 3.2, 4.5, 20), madera, 0, 12, 0));
  g.add(malla(new THREE.ConeGeometry(3.6, 2.2, 20), metal, 0, 15.3, 0));
  g.position.set(x, 0, z); escena.add(g); return g;
}

export function poste(escena, x, z) {
  const madera = toon(0x7a5232);
  escena.add(malla(new THREE.CylinderGeometry(0.22, 0.28, 11, 8), madera, x, 5.5, z));
  escena.add(malla(new THREE.BoxGeometry(3, 0.25, 0.25), madera, x, 10.3, z));
}

export function valla(escena, x, z, rotY = 0) {
  const g = new THREE.Group();
  const rayas = toon(0xffffff), naranja = toon(0xff6a1a), patas = toon(0x444448);
  g.add(malla(new THREE.BoxGeometry(3, 0.5, 0.15), naranja, 0, 1.6, 0));
  for (let i = 0; i < 3; i++) g.add(malla(new THREE.BoxGeometry(0.35, 0.52, 0.17), rayas, -1 + i, 1.6, 0, false));
  [-1.3, 1.3].forEach(px => g.add(malla(new THREE.BoxGeometry(0.15, 1.8, 0.6), patas, px, 0.9, 0)));
  g.position.set(x, 0, z); g.rotation.y = rotY; escena.add(g); return g;
}

// ------------------------------------------------- letreros en pantalla
// Texto de cómic que aparece con rebote. x, y en fracción de pantalla (0-1).
export function letrero(ctx, txt, x, y, prog, { tam = 170, color = AMARILLO, giro = -0.12 } = {}) {
  if (prog <= 0) return;
  const k = rebote(Math.min(1, prog * 2.2));
  if (k <= 0.02) return;
  ctx.save();
  ctx.translate(x * ANCHO, y * ALTO);
  ctx.rotate(giro);
  ctx.scale(k, k);
  ctx.font = `${tam}px Anton`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  const blanco = color.toLowerCase() === '#ffffff';
  ctx.lineWidth = tam * (blanco ? 0.16 : 0.22); ctx.strokeStyle = '#1b1210'; ctx.strokeText(txt, 0, 0);
  if (!blanco) { ctx.lineWidth = tam * 0.1; ctx.strokeStyle = '#ffffff'; ctx.strokeText(txt, 0, 0); }
  ctx.fillStyle = color; ctx.fillText(txt, 0, 0);
  ctx.restore();
}

export function destello(ctx, fuerza, color = '255,255,255') {
  if (fuerza <= 0) return;
  ctx.fillStyle = `rgba(${color},${Math.min(1, fuerza)})`;
  ctx.fillRect(0, 0, ANCHO, ALTO);
}

// ----------------------------------------------------------- ambiente
const AMBIENTES = {
  dia: { a: '#3f96ea', b: '#ffe0b0', luz: 2.2, hemi: 1.3, cHemi: 0xcfe8ff },
  calor: { a: '#ff7a3a', b: '#ffd27a', luz: 2.6, hemi: 1.4, cHemi: 0xffd0a0 },
  noche: { a: '#0b1040', b: '#4a2f7a', luz: 0.45, hemi: 0.55, cHemi: 0x7080ff },
  cuarto: { a: '#0b1040', b: '#4a2f7a', luz: 0.9, hemi: 1.15, cHemi: 0xb0b4ff },
  sueno: { a: '#2a1a6a', b: '#d07ad8', luz: 1.2, hemi: 1.2, cHemi: 0xd8c8ff },
  invierno: { a: '#6fa6dc', b: '#eef3fa', luz: 1.7, hemi: 1.35, cHemi: 0xe4f0ff },
  lab: { a: '#14203c', b: '#2c4a7a', luz: 1.3, hemi: 1.3, cHemi: 0xc8dcff },
};
export function ambiente(mundo, de, a = de, k = 0) {
  const A = AMBIENTES[de], B = AMBIENTES[a];
  mundo.cielo.material.uniforms.a.value.set(A.a).lerp(new THREE.Color(B.a), k);
  mundo.cielo.material.uniforms.b.value.set(A.b).lerp(new THREE.Color(B.b), k);
  mundo.luz.intensity = A.luz + (B.luz - A.luz) * k;
  mundo.hemi.intensity = A.hemi + (B.hemi - A.hemi) * k;
  mundo.hemi.color.set(A.cHemi).lerp(new THREE.Color(B.cHemi), k);
}

// ---------------------------------------------------------- más utilería
export function flecha3d(color = 0xffd600) {
  const g = new THREE.Group(), mat = toon(color);
  const palo = malla(new THREE.CylinderGeometry(0.25, 0.25, 2.2, 12), mat, 0, 1.1, 0);
  const punta = malla(new THREE.ConeGeometry(0.6, 1.1, 16), mat, 0, 2.7, 0);
  g.add(palo, punta);
  return g;  // apunta hacia +Y; rótala para orientarla
}

export function auto3d(color = 0xd9483b) {
  const g = new THREE.Group();
  const c = toon(color), vidrio = sinContorno(toon(0x9fd3ff)), negro = toon(0x222226), luzT = sinContorno(toon(0xff4040));
  g.add(malla(new THREE.BoxGeometry(2.6, 1.0, 5.2), c, 0, 1.0, 0));
  g.add(malla(new THREE.BoxGeometry(2.3, 0.9, 2.8), c, 0, 1.9, -0.3));
  g.add(malla(new THREE.BoxGeometry(2.0, 0.65, 0.1), vidrio, 0, 1.95, 1.12, false));
  g.add(malla(new THREE.BoxGeometry(2.0, 0.65, 0.1), vidrio, 0, 1.95, -1.72, false));
  [[-0.9, -2.62], [0.9, -2.62]].forEach(([x, z]) => g.add(malla(new THREE.BoxGeometry(0.5, 0.3, 0.1), luzT, x, 1.2, z, false)));
  [[-1.3, 1.7], [1.3, 1.7], [-1.3, -1.7], [1.3, -1.7]].forEach(([x, z]) => {
    const r = malla(new THREE.CylinderGeometry(0.55, 0.55, 0.45, 18), negro, x, 0.55, z);
    r.rotation.z = Math.PI / 2; g.add(r);
  });
  return g;
}

export function yunque() {
  const g = new THREE.Group(), m = toon(0x4a4a55);
  g.add(malla(new THREE.BoxGeometry(3.2, 0.7, 1.8), m, 0, 0.35, 0));
  g.add(malla(new THREE.BoxGeometry(1.4, 1.0, 1.2), m, 0, 1.2, 0));
  g.add(malla(new THREE.BoxGeometry(4.2, 0.9, 1.6), m, 0.4, 2.1, 0));
  const pico = malla(new THREE.ConeGeometry(0.75, 1.6, 4), m, -2.3, 2.1, 0);
  pico.rotation.z = Math.PI / 2; g.add(pico);
  return g;
}

export function foco() {
  const g = new THREE.Group();
  g.add(malla(new THREE.SphereGeometry(0.8, 24, 16), toon(0xfff27a, { emissive: 0xffc800, emissiveIntensity: 0.8 }), 0, 1.1, 0));
  g.add(malla(new THREE.CylinderGeometry(0.38, 0.38, 0.6, 16), toon(0x9a9aa4), 0, 0.2, 0));
  return g;
}

// Nubecitas de polvo: devuelve una función actualizar(progreso)
export function polvo(escena, x, y, z, n = 10, radio = 4, color = 0xf3e6d0) {
  const mat = sinContorno(toon(color));
  const piezas = [];
  for (let i = 0; i < n; i++) {
    const m = malla(new THREE.SphereGeometry(0.8, 12, 8), mat, x, y, z, false);
    const a = (i / n) * Math.PI * 2 + i * 0.7;
    m.userData.dir = [Math.cos(a), 0.25 + (i % 3) * 0.15, Math.sin(a)];
    m.visible = false; escena.add(m); piezas.push(m);
  }
  return p => piezas.forEach(m => {
    m.visible = p > 0 && p < 1;
    if (!m.visible) return;
    const d = m.userData.dir, f = frena(p) * radio;
    m.position.set(x + d[0] * f, y + d[1] * f, z + d[2] * f);
    m.scale.setScalar((1 - p) * 1.4 + 0.1);
  });
}

// Grieta como cadena de piezas delgadas; se revela con progreso 0-1
export function grieta(escena, puntos, grosor = 0.18, alto = 0.06, color = 0x2b2522) {
  const mat = sinContorno(toon(color));
  const piezas = [];
  for (let i = 0; i < puntos.length - 1; i++) {
    const a = new THREE.Vector3(...puntos[i]), b = new THREE.Vector3(...puntos[i + 1]);
    const largo = a.distanceTo(b);
    const m = malla(new THREE.BoxGeometry(grosor, alto, largo + grosor), mat, 0, 0, 0, false);
    m.position.copy(a).add(b).multiplyScalar(0.5);
    m.lookAt(b);
    m.visible = false; escena.add(m); piezas.push(m);
  }
  return p => piezas.forEach((m, i) => { m.visible = i < Math.floor(piezas.length * Math.min(1, p) + 1e-6); });
}

export function camino(a, b, seg = 12, desvio = 0.6, semilla = 1, eje = 'y') {
  let s = semilla * 9301 + 49297;
  const rnd = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  const pts = [];
  for (let i = 0; i <= seg; i++) {
    const k = i / seg;
    const p = a.map((v, j) => v + (b[j] - v) * k);
    if (i > 0 && i < seg) {
      const d = (rnd() * 2 - 1) * desvio;
      if (eje === 'y') { // grieta sobre una superficie horizontal: desvía en el plano xz
        const dx = b[2] - a[2], dz = -(b[0] - a[0]), n = Math.hypot(dx, dz) || 1;
        p[0] += dx / n * d; p[2] += dz / n * d;
      } else { p[0] += d; } // grieta vertical: desvía en x
    }
    pts.push(p);
  }
  return pts;
}


// ---------------------------------------------------- vida extra en escena
// Gaviotas que vuelan en círculos alrededor de (x, y, z)
export function gaviotas(escena, x, y, z, n = 6, radio = 18) {
  const mat = toon(0xffffff), punta = toon(0x333333);
  const aves = [];
  for (let i = 0; i < n; i++) {
    const g = new THREE.Group();
    const cuerpo = malla(new THREE.CapsuleGeometry(0.18, 0.6, 4, 8), mat, 0, 0, 0, false);
    cuerpo.rotation.z = Math.PI / 2; g.add(cuerpo);
    const alas = [-1, 1].map(l => {
      const piv = new THREE.Group(); piv.position.set(0, 0.05, l * 0.1);
      const ala = malla(new THREE.BoxGeometry(0.5, 0.05, 1.3), mat, 0, 0, l * 0.65, false);
      const p2 = malla(new THREE.BoxGeometry(0.3, 0.06, 0.3), punta, 0, 0, l * 1.25, false);
      piv.add(ala, p2); g.add(piv); return piv;
    });
    g.userData = { alas, fase: i * 1.7, r: radio * (0.6 + (i % 3) * 0.2), h: y + (i % 4) * 2.5 };
    escena.add(g); aves.push(g);
  }
  return (t, visible = true) => aves.forEach(g => {
    g.visible = visible; if (!visible) return;
    const { alas, fase, r, h } = g.userData, a = t * 0.5 + fase;
    g.position.set(x + Math.cos(a) * r, h + Math.sin(t * 2 + fase) * 0.6, z + Math.sin(a) * r * 0.6);
    g.rotation.y = -a;
    const aleteo = Math.sin(t * 9 + fase) * 0.5;
    alas[0].rotation.x = aleteo; alas[1].rotation.x = -aleteo;
  });
}

// Humo que sale de un punto (en coordenadas del padre)
export function humo(padre, x, y, z, color = 0x8a8a8a, n = 7) {
  const mat = sinContorno(toon(color));
  const bolas = [];
  for (let i = 0; i < n; i++) { const b = malla(new THREE.SphereGeometry(1, 10, 8), mat, x, y, z, false); padre.add(b); bolas.push(b); }
  return (t, visible = true) => bolas.forEach((b, i) => {
    b.visible = visible; if (!visible) return;
    const k = ((t * 0.35 + i / n) % 1);
    b.position.set(x - k * 7, y + k * 6, z + Math.sin(i * 3) * k);
    b.scale.setScalar(0.5 + k * 1.8);
  });
}

export function maleta(padre, x, y, z, color = 0x7a4b2a, rot = 0) {
  const g = new THREE.Group();
  g.add(malla(new THREE.BoxGeometry(1.3, 0.9, 0.8), toon(color), 0, 0.45, 0));
  g.add(malla(new THREE.BoxGeometry(1.34, 0.12, 0.84), toon(0x3a2416), 0, 0.6, 0));
  g.add(malla(new THREE.BoxGeometry(0.12, 0.94, 0.84), toon(0x3a2416), 0.35, 0.45, 0));
  g.position.set(x, y, z); g.rotation.y = rot; padre.add(g); return g;
}

export function farol(padre, x, y, z, alto = 4) {
  const g = new THREE.Group();
  g.add(malla(new THREE.CylinderGeometry(0.1, 0.14, alto, 8), toon(0x2a2a2e), 0, alto / 2, 0));
  g.add(malla(new THREE.SphereGeometry(0.35, 12, 8), toon(0xfff2a0, { emissive: 0xffc840, emissiveIntensity: 0.9 }), 0, alto + 0.2, 0));
  g.position.set(x, y, z); padre.add(g); return g;
}

// Guirnalda de banderitas entre dos puntos
export function banderitas(padre, a, b, n = 14) {
  const colores = [0xe23c3c, 0xffffff, 0x2d6fd6, 0xffd600];
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  for (let i = 0; i < n; i++) {
    const k = (i + 0.5) / n;
    const p = A.clone().lerp(B, k); p.y -= Math.sin(k * Math.PI) * 0.8;
    const f = malla(new THREE.ConeGeometry(0.25, 0.6, 3), toon(colores[i % 4]), p.x, p.y - 0.3, p.z, false);
    f.rotation.z = Math.PI; padre.add(f);
  }
  const cuerda = malla(new THREE.CylinderGeometry(0.02, 0.02, A.distanceTo(B), 4), toon(0x333333), 0, 0, 0, false);
  cuerda.position.copy(A).add(B).multiplyScalar(0.5); cuerda.position.y -= 0.5;
  cuerda.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  padre.add(cuerda);
}

// Letrero con texto pintado (canvas)
export function cartel(padre, texto, x, y, z, ancho = 8, alto = 1.6, fondo = '#b3202c', color = '#ffffff') {
  const c = document.createElement('canvas'); c.width = 1024; c.height = Math.round(1024 * alto / ancho);
  const ctx = c.getContext('2d'); ctx.fillStyle = fondo; ctx.fillRect(0, 0, c.width, c.height);
  ctx.strokeStyle = '#1b1210'; ctx.lineWidth = 16; ctx.strokeRect(8, 8, c.width - 16, c.height - 16);
  ctx.fillStyle = color; ctx.font = `${Math.round(c.height * 0.62)}px Anton`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(texto, c.width / 2, c.height / 2 + 4);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(ancho, alto), sinContorno(new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide })));
  m.position.set(x, y, z); padre.add(m); return m;
}
