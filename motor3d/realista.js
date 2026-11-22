// Estilo "pintado realista": luz física, texturas, neblina, brillo en las luces,
// fondo desenfocado y partículas. Los personajes 2D siguen igual (con contorno).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ANCHO, ALTO } from '/motor3d/kit.js';

export function crearRenderRealista() {
  const gl = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  gl.setPixelRatio(1);
  gl.setSize(ANCHO, ALTO, false);
  gl.outputColorSpace = THREE.SRGBColorSpace;
  gl.toneMapping = THREE.ACESFilmicToneMapping;
  gl.toneMappingExposure = 1.05;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = THREE.PCFSoftShadowMap;
  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(45, ANCHO / ALTO, 0.1, 3000);
  const composer = new EffectComposer(gl);
  composer.setSize(ANCHO, ALTO);
  composer.addPass(new RenderPass(escena, camara));
  const bokeh = new BokehPass(escena, camara, { focus: 12, aperture: 0.0012, maxblur: 0.009 });
  composer.addPass(bokeh);
  const bloom = new UnrealBloomPass(new THREE.Vector2(ANCHO / 2, ALTO / 2), 0.6, 0.6, 0.93);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const salida = document.createElement('canvas');
  salida.width = ANCHO; salida.height = ALTO;
  const ctx = salida.getContext('2d');
  // misma forma que crearRender(): las escenas siguen llamando r.efecto.render(escena, camara)
  const efecto = { render: () => composer.render() };
  return { gl, efecto, salida, ctx, escena, camara, composer, bokeh, bloom };
}

// Enfoca a cierta distancia de la cámara (lo demás se ve borroso)
export function enfocar(r, distancia, desenfoque = 1) {
  r.bokeh.uniforms.focus.value = distancia;
  r.bokeh.uniforms.aperture.value = 0.0012 * desenfoque;
}

// Cambia todos los materiales "toon" por materiales con luz realista
export function convertir(escena) {
  const cache = new Map();
  escena.traverse(o => {
    if (!o.isMesh) return;
    const m = o.material;
    if (!m || !m.isMeshToonMaterial) return;
    if (!cache.has(m.uuid)) {
      const n = new THREE.MeshStandardMaterial({
        color: m.color, emissive: m.emissive, emissiveIntensity: Math.max(m.emissiveIntensity, 1) * 1.6,
        map: m.map, transparent: m.transparent, opacity: m.opacity, side: m.side,
        roughness: 0.82, metalness: 0.0, flatShading: m.flatShading,
      });
      n.userData = m.userData;
      cache.set(m.uuid, n);
    }
    o.material = cache.get(m.uuid);
    // onBeforeRender va en el Mesh, no en el material
    const mat = o.material;
    const orig = m;
    o.onBeforeRender = () => { mat.color.copy(orig.color); mat.emissive.copy(orig.emissive); mat.opacity = orig.opacity; };
  });
}

// ------------------------------------------------------------- texturas
function lienzo(w, h, dibujar, repetir = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  dibujar(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repetir);
  t.anisotropy = 8;
  return t;
}
let semilla = 7;
const azar = () => ((semilla = (semilla * 9301 + 49297) % 233280) / 233280);
const tono = (hex, d) => { const c = new THREE.Color(hex); c.offsetHSL(0, 0, d); return '#' + c.getHexString(); };

export const texturas = {
  ladrillo: (color = '#8a4a3a', rep = [4, 4]) => lienzo(512, 512, (x, w, h) => {
    x.fillStyle = '#5a4a44'; x.fillRect(0, 0, w, h);
    for (let fila = 0; fila < 16; fila++) for (let col = -1; col < 8; col++) {
      const bx = col * 64 + (fila % 2) * 32, by = fila * 32;
      x.fillStyle = tono(color, (azar() - 0.5) * 0.12); x.fillRect(bx + 3, by + 3, 58, 26);
      x.fillStyle = 'rgba(0,0,0,0.12)'; x.fillRect(bx + 3, by + 22, 58, 7);
    }
  }, rep),
  adoquin: (color = '#6f7a85', rep = [10, 10]) => lienzo(512, 512, (x, w, h) => {
    x.fillStyle = '#2e3338'; x.fillRect(0, 0, w, h);
    for (let fila = 0; fila < 10; fila++) for (let col = -1; col < 9; col++) {
      const bx = col * 60 + (fila % 2) * 30 + azar() * 6, by = fila * 52 + azar() * 4;
      x.fillStyle = tono(color, (azar() - 0.5) * 0.16);
      x.beginPath(); x.roundRect(bx + 4, by + 4, 52, 44, 14); x.fill();
      x.fillStyle = 'rgba(255,255,255,0.08)'; x.beginPath(); x.roundRect(bx + 10, by + 8, 30, 10, 6); x.fill();
    }
  }, rep),
  madera: (color = '#8a5a35', rep = [1, 6]) => lienzo(256, 512, (x, w, h) => {
    for (let i = 0; i < 4; i++) {
      x.fillStyle = tono(color, (azar() - 0.5) * 0.1); x.fillRect(i * 64, 0, 64, h);
      x.strokeStyle = 'rgba(0,0,0,0.25)'; x.lineWidth = 3; x.strokeRect(i * 64, 0, 64, h);
      for (let k = 0; k < 6; k++) { x.strokeStyle = 'rgba(0,0,0,0.08)'; x.lineWidth = 2; x.beginPath();
        const xx = i * 64 + 8 + azar() * 48; x.moveTo(xx, 0); x.bezierCurveTo(xx + 8, h / 3, xx - 8, h * 2 / 3, xx, h); x.stroke(); }
    }
  }, rep),
  tapiz: (fondo = '#e8d8c0', flor = '#c26a6a', rep = [4, 3]) => lienzo(256, 256, (x, w, h) => {
    x.fillStyle = fondo; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 18; i++) {
      const fx = azar() * w, fy = azar() * h;
      for (let p = 0; p < 5; p++) { const a = p / 5 * Math.PI * 2; x.fillStyle = flor; x.beginPath(); x.arc(fx + Math.cos(a) * 6, fy + Math.sin(a) * 6, 5, 0, 7); x.fill(); }
      x.fillStyle = '#e8c060'; x.beginPath(); x.arc(fx, fy, 3, 0, 7); x.fill();
      x.fillStyle = '#7a9a6a'; x.beginPath(); x.ellipse(fx + 10, fy + 10, 6, 3, 0.6, 0, 7); x.fill();
    }
  }, rep),
  revoque: (color = '#e8dcc0', rep = [2, 2]) => lienzo(256, 256, (x, w, h) => {
    x.fillStyle = color; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 400; i++) { x.fillStyle = `rgba(0,0,0,${azar() * 0.06})`; x.fillRect(azar() * w, azar() * h, 3 + azar() * 6, 3 + azar() * 6); }
  }, rep),
  tejas: (color = '#7a3a2a', rep = [4, 3]) => lienzo(256, 256, (x, w, h) => {
    x.fillStyle = tono(color, -0.1); x.fillRect(0, 0, w, h);
    for (let fila = 0; fila < 8; fila++) for (let col = -1; col < 9; col++) {
      x.fillStyle = tono(color, (azar() - 0.5) * 0.12);
      x.beginPath(); x.arc(col * 32 + (fila % 2) * 16 + 16, fila * 32 + 16, 16, 0, Math.PI); x.fill();
    }
  }, rep),
  pasto: (color = '#4f7a3a', rep = [40, 40]) => lienzo(256, 256, (x, w, h) => {
    x.fillStyle = color; x.fillRect(0, 0, w, h);
    for (let i = 0; i < 900; i++) { x.fillStyle = tono(color, (azar() - 0.5) * 0.18); x.fillRect(azar() * w, azar() * h, 2, 6); }
  }, rep),
};

// Cambia el material de un objeto por uno con textura
export function vestir(malla, textura, extra = {}) {
  malla.material = new THREE.MeshStandardMaterial({ map: textura, roughness: 0.9, metalness: 0, ...extra });
  malla.onBeforeRender = () => {};
  return malla;
}

// Neblina con el color del cielo
export function neblina(escena, color, densidad) {
  escena.fog = new THREE.FogExp2(color, densidad);
}

// Partículas que flotan (nieve, polvo) alrededor de la cámara
export function particulas(escena, n = 600, color = 0xffffff, tam = 0.12) {
  const pos = new Float32Array(n * 3), base = [];
  for (let i = 0; i < n; i++) base.push([Math.random() * 2 - 1, Math.random(), Math.random() * 2 - 1, Math.random() * 6.28]);
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const x = c.getContext('2d'); const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  const mat = new THREE.PointsMaterial({ color, size: tam, map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false });
  mat.userData.outlineParameters = { visible: false };
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false; escena.add(pts);
  return (t, camara, visible = true, caida = 0.6) => {
    pts.visible = visible; if (!visible) return;
    const cx = camara.position.x, cy = camara.position.y, cz = camara.position.z;
    for (let i = 0; i < n; i++) {
      const [bx, by, bz, f] = base[i];
      const y = ((by - t * caida * 0.05) % 1 + 1) % 1;
      pos[i * 3] = cx + bx * 14 + Math.sin(t * 0.7 + f) * 0.6;
      pos[i * 3 + 1] = cy - 6 + y * 14;
      pos[i * 3 + 2] = cz - 4 + bz * 12;
    }
    geo.attributes.position.needsUpdate = true;
  };
}
