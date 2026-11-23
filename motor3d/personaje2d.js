// Personajes 2D de cabeza blanca (diseño propio) que viven dentro de la escena 3D.
// Se dibujan en un canvas en cada cuadro (para gestos, parpadeo y boca que habla)
// y se ponen sobre un plano que siempre mira a la cámara.
import * as THREE from 'three';

const W = 512, H = 1024;
const LINEA = '#231a17';

export const VESTUARIOS = {
  obrero: { camisa: '#7fb7ea', chaleco: '#ff7a1f', franja: '#fff36b', sombrero: 'casco', pelo: '#5a3a28' },
  jefe: { saco: '#2f5d46', camisa: '#ffffff', mono: '#b3202c', sombrero: 'copa', bigote: true, pelo: '#3a2a22' },
  ingeniero: { camisa: '#f4f4f4', corbata: '#2f6fd6', sombrero: 'casco_blanco', lentes: true, pelo: '#2b2b2b' },
  chofer: { camisa: '#d9483b', gorra: '#2d4fa8', sombrero: 'gorra', pelo: '#6b4b2a' },
  capitan: { saco: '#1f2a4a', camisa: '#ffffff', sombrero: 'gorra_capitan', barba: '#ececec', pelo: '#e2e2e2' },
  pasajero: { saco: '#7a5233', camisa: '#ffffff', corbata: '#3b6e3a', sombrero: 'bombin', bigote: true, pelo: '#3a2a22' },
  pasajera: { saco: '#b04f86', vestido: true, sombrero: 'pamela', pelo_largo: '#8a4a2a' },
  marinero: { camisa: '#ffffff', cuello: '#2d4fa8', sombrero: 'marinero', pelo: '#6b4b2a' },
  dormilon: { camisa: '#8fb8ff', pijama: true, sombrero: 'gorro_dormir', pelo: '#5a3a28' },
  campesino: { camisa: '#9a6b42', tunica: true, sombrero: 'capucha', pelo: '#5a3a28' },
  campesina: { saco: '#6f8f4a', vestido: true, delantal: true, sombrero: 'cofia', pelo_largo: '#a0522d' },
  medico: { camisa: '#ffffff', bata: true, sombrero: null, lentes: true, pelo: '#2b2b2b' },
  // cocina (video del aceite)
  mama: { saco: '#e2742a', vestido: true, delantal: true, sombrero: null, pelo_largo: '#3a2a22', aretes: true },
  tio: { camisa: '#2fae7a', rayas: '#ffffff', sombrero: 'gorra', gorra: '#e23c3c', bigote: true, pelo: '#2b2b2b' },
  abuela: { saco: '#8a6ab0', vestido: true, chal: '#e8d8f0', sombrero: null, pelo_largo: '#d8d8d8', chongo: true, lentes: true },
  bombero: { saco: '#c8283a', bombero: true, sombrero: 'casco_bombero', bigote: true, pelo: '#3a2a22' },
  nino: { camisa: '#ffd600', rayas: '#2d6fd6', sombrero: 'gorra', gorra: '#2d6fd6', pelo: '#5a3a28' },
  nina: { saco: '#ff6b8a', vestido: true, sombrero: null, pelo_largo: '#5a3a28', mono_pelo: '#ffd600' },
  // invierno (video de la sal)
  beto: { saco: '#2f7d5a', abrigo: true, bufanda: '#e23c3c', sombrero: 'gorro_lana', gorro: '#e23c3c', pelo: '#5a3a28' },
  vecino: { saco: '#f2b51a', abrigo: true, bufanda: '#7a3cbf', sombrero: 'orejeras', orejeras: '#ff6b8a', lentes_sol: true, pelo: '#2b2b2b' },
  invierno_a: { saco: '#2d6fd6', abrigo: true, bufanda: '#ffd600', sombrero: 'gorro_lana', gorro: '#f4f4f4', pelo: '#6b4b2a' },
  invierno_b: { saco: '#b04f86', abrigo: true, bufanda: '#ffffff', sombrero: 'gorro_lana', gorro: '#3cbf5a', pelo_largo: '#8a4a2a' },
  invierno_c: { saco: '#6e4a2c', abrigo: true, bufanda: '#2d6fd6', sombrero: 'orejeras', orejeras: '#ffffff', pelo: '#2b2b2b' },
  invierno_d: { saco: '#d9483b', abrigo: true, bufanda: '#2b2b2b', sombrero: 'gorro_lana', gorro: '#2d4fa8', pelo_largo: '#3a2a22' },
};

function contorno(ctx, w = 11) { ctx.lineWidth = w; ctx.strokeStyle = LINEA; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; }

function elipse(ctx, x, y, rx, ry, relleno, borde = 11, rot = 0) {
  ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, Math.PI * 2);
  if (relleno) { ctx.fillStyle = relleno; ctx.fill(); }
  if (borde) { contorno(ctx, borde); ctx.stroke(); }
}

function linea(ctx, pts, w = 12, color = LINEA) {
  ctx.beginPath(); ctx.moveTo(...pts[0]); pts.slice(1).forEach(p => ctx.lineTo(...p));
  ctx.lineWidth = w; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
}

function cuerpo(ctx, v, tipo) {
  // torso tipo frijol
  ctx.beginPath();
  ctx.moveTo(170, 520); ctx.quadraticCurveTo(256, 470, 342, 520);
  ctx.quadraticCurveTo(372, 640, 345, 735); ctx.quadraticCurveTo(256, 770, 167, 735);
  ctx.quadraticCurveTo(140, 640, 170, 520); ctx.closePath();
  const base = v.saco || v.camisa;
  ctx.fillStyle = base; ctx.fill();
  ctx.save(); ctx.clip();
  if (tipo === 'obrero') {
    ctx.fillStyle = v.chaleco; ctx.fillRect(150, 470, 80, 320); ctx.fillRect(282, 470, 80, 320);
    ctx.fillStyle = v.franja; ctx.fillRect(150, 620, 80, 22); ctx.fillRect(282, 620, 80, 22);
    ctx.fillRect(188, 470, 18, 320); ctx.fillRect(306, 470, 18, 320);
  } else if (tipo === 'jefe') {
    ctx.fillStyle = v.camisa; ctx.beginPath(); ctx.moveTo(215, 490); ctx.lineTo(297, 490); ctx.lineTo(256, 640); ctx.fill();
    ctx.fillStyle = '#f0c040'; [600, 650, 700].forEach(y => { ctx.beginPath(); ctx.arc(256, y, 8, 0, 7); ctx.fill(); });
    linea(ctx, [[300, 500], [262, 640]], 6); linea(ctx, [[212, 500], [250, 640]], 6);
  } else if (tipo === 'ingeniero') {
    ctx.fillStyle = v.corbata; ctx.beginPath(); ctx.moveTo(244, 500); ctx.lineTo(268, 500); ctx.lineTo(276, 640);
    ctx.lineTo(256, 665); ctx.lineTo(236, 640); ctx.fill();
    ctx.fillStyle = '#d8d8d8'; ctx.fillRect(300, 560, 34, 40);
  } else if (tipo === 'chofer') {
    ctx.fillStyle = '#ffffff'; ctx.fillRect(230, 470, 52, 320);
  } else if (tipo === 'capitan' || tipo === 'pasajero') {
    ctx.fillStyle = v.camisa; ctx.beginPath(); ctx.moveTo(220, 490); ctx.lineTo(292, 490); ctx.lineTo(256, 610); ctx.fill();
    if (v.corbata) { ctx.fillStyle = v.corbata; ctx.fillRect(248, 495, 16, 100); }
    ctx.fillStyle = tipo === 'capitan' ? '#f0c040' : '#3a2416';
    [600, 650, 700].forEach(y => [226, 286].forEach(x => { ctx.beginPath(); ctx.arc(x, y, 8, 0, 7); ctx.fill(); }));
  } else if (tipo === 'marinero') {
    ctx.fillStyle = v.cuello; ctx.beginPath(); ctx.moveTo(180, 490); ctx.lineTo(332, 490); ctx.lineTo(256, 600); ctx.fill();
    ctx.fillStyle = '#ffffff'; ctx.fillRect(160, 520, 200, 8);
  } else if (v.pijama) {
    ctx.fillStyle = '#ffffff'; for (let y = 480; y < 780; y += 46) ctx.fillRect(130, y, 260, 14);
    ctx.fillStyle = '#4f7fd6'; [560, 620, 680].forEach(y => { ctx.beginPath(); ctx.arc(256, y, 9, 0, 7); ctx.fill(); });
  } else if (v.tunica) {
    ctx.fillStyle = '#6e4a2c'; ctx.fillRect(130, 660, 260, 30);
    ctx.fillStyle = '#d9c39a'; ctx.beginPath(); ctx.moveTo(226, 490); ctx.lineTo(286, 490); ctx.lineTo(256, 560); ctx.fill();
  } else if (v.bata) {
    ctx.fillStyle = '#7fc8b0'; ctx.fillRect(226, 480, 60, 300);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(130, 480, 96, 300); ctx.fillRect(286, 480, 104, 300);
    linea(ctx, [[226, 480], [226, 780]], 6); linea(ctx, [[286, 480], [286, 780]], 6);
    ctx.fillStyle = '#d0d0d0'; ctx.fillRect(296, 580, 50, 40);
  } else if (v.abrigo) {   // chamarra acolchada con cierre
    ctx.fillStyle = 'rgba(0,0,0,0.13)'; for (let y = 540; y < 780; y += 55) ctx.fillRect(130, y, 260, 9);
    ctx.fillStyle = 'rgba(255,255,255,0.18)'; for (let y = 505; y < 780; y += 55) ctx.fillRect(130, y, 260, 10);
    linea(ctx, [[256, 490], [256, 770]], 7, 'rgba(0,0,0,0.45)');
  } else if (v.rayas) {
    ctx.fillStyle = v.rayas; for (let y = 520; y < 780; y += 48) ctx.fillRect(130, y, 260, 16);
  } else if (v.bombero) {
    ctx.fillStyle = '#ffd600'; ctx.fillRect(130, 640, 260, 24); ctx.fillRect(130, 700, 260, 18);
    ctx.fillStyle = '#e0e0e0'; ctx.fillRect(130, 652, 260, 6);
    ctx.fillStyle = '#2b2b2b'; [570, 610].forEach(y => { ctx.fillRect(246, y, 20, 14); });
  } else if (tipo === 'pasajera') {
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(256, 495, 40, 0, Math.PI); ctx.fill();
    ctx.fillStyle = '#7a2f5a'; ctx.fillRect(150, 660, 220, 26);
  }
  ctx.restore();
  contorno(ctx, 11); ctx.beginPath();
  ctx.moveTo(170, 520); ctx.quadraticCurveTo(256, 470, 342, 520);
  ctx.quadraticCurveTo(372, 640, 345, 735); ctx.quadraticCurveTo(256, 770, 167, 735);
  ctx.quadraticCurveTo(140, 640, 170, 520); ctx.closePath(); ctx.stroke();
  if (v.bata) {  // estetoscopio
    ctx.beginPath(); ctx.moveTo(200, 500); ctx.quadraticCurveTo(190, 640, 256, 650); ctx.quadraticCurveTo(320, 640, 312, 500);
    ctx.lineWidth = 9; ctx.strokeStyle = '#333'; ctx.stroke(); elipse(ctx, 256, 660, 18, 18, '#bbbbbb', 6);
  }
  if (v.bufanda) {
    ctx.fillStyle = v.bufanda; contorno(ctx, 9);
    ctx.beginPath(); ctx.roundRect(286, 500, 46, 130, 12); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(186, 468, 140, 52, 24); ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(290, 560, 38, 12); ctx.fillRect(290, 590, 38, 12);
  }
  if (v.chal) { ctx.fillStyle = v.chal; ctx.beginPath(); ctx.moveTo(160, 505); ctx.quadraticCurveTo(256, 470, 352, 505); ctx.lineTo(300, 620); ctx.lineTo(256, 580); ctx.lineTo(212, 620); ctx.closePath(); ctx.fill(); contorno(ctx, 8); ctx.stroke(); }
  if (v.delantal) { ctx.fillStyle = '#f4f0e6'; ctx.beginPath(); ctx.roundRect(200, 600, 112, 140, 20); ctx.fill(); contorno(ctx, 8); ctx.stroke(); }
  if (tipo === 'jefe') {  // moño
    ctx.fillStyle = v.mono;
    ctx.beginPath(); ctx.moveTo(256, 505); ctx.lineTo(226, 488); ctx.lineTo(226, 522); ctx.closePath(); ctx.fill(); contorno(ctx, 6); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(256, 505); ctx.lineTo(286, 488); ctx.lineTo(286, 522); ctx.closePath(); ctx.fill(); ctx.stroke();
  }
}

function brazo(ctx, lado, ang, codo, color) {
  // ang: 0 = colgando, 90 = horizontal hacia afuera, 160 = arriba
  const hx = 256 + lado * 92, hy = 540;
  const a = (ang * Math.PI) / 180;
  const cx = hx + lado * Math.sin(a) * 95, cy = hy + Math.cos(a) * 95;
  const a2 = ((ang + codo) * Math.PI) / 180;
  const mx = cx + lado * Math.sin(a2) * 85, my = cy + Math.cos(a2) * 85;
  linea(ctx, [[hx, hy], [cx, cy], [mx, my]], 30);
  linea(ctx, [[hx, hy], [cx, cy], [mx, my]], 16, color);
  elipse(ctx, mx, my, 24, 24, '#ffffff', 9);
  return [mx, my];
}

function cara(ctx, v, est, t) {
  const cx = 256, cy = 300;
  const parpadeo = est.parpadeo ?? ((t * 0.7 + (est.semilla || 0)) % 3.2 < 0.12);
  const habla = est.habla && Math.sin(t * 22) > -0.1;
  const c = est.cara || 'normal';
  const ojos = [[cx - 62, cy - 10], [cx + 62, cy - 10]];
  ctx.fillStyle = LINEA;
  // cejas
  const cejas = { enojado: [0.35, -0.35], preocupado: [-0.35, 0.35], sorpresa: [-0.1, 0.1] }[c] || [0.05, -0.05];
  ojos.forEach(([x, y], i) => {
    const s = cejas[i];
    const alto = c === 'sorpresa' ? 62 : 46;
    linea(ctx, [[x - 30, y - alto + s * 30], [x + 30, y - alto - s * 30]], 10);
  });
  if (c === 'dormido') {
    ojos.forEach(([x, y]) => linea(ctx, [[x - 22, y + 6], [x + 22, y + 6]], 10));
  } else if (c === 'cansado') {
    ojos.forEach(([x, y]) => { elipse(ctx, x, y + 6, 13, 9, LINEA, 0); linea(ctx, [[x - 26, y - 4], [x + 26, y - 4]], 9);
      ctx.beginPath(); ctx.arc(x, y + 18, 20, 0.15 * Math.PI, 0.85 * Math.PI); ctx.lineWidth = 5; ctx.strokeStyle = '#8a7aa8'; ctx.stroke(); });
  } else if (c === 'feliz' || parpadeo) {
    ojos.forEach(([x, y]) => { ctx.beginPath(); ctx.arc(x, y + 8, 20, Math.PI * 1.1, Math.PI * 1.9); contorno(ctx, 10); ctx.stroke(); });
  } else if (c === 'sorpresa' || c === 'miedo') {
    ojos.forEach(([x, y]) => { elipse(ctx, x, y, 30, 34, '#ffffff', 8); elipse(ctx, x, y + 4, 11, 13, LINEA, 0); });
  } else if (c === 'mareado') {
    ojos.forEach(([x, y]) => { linea(ctx, [[x - 18, y - 18], [x + 18, y + 18]], 9); linea(ctx, [[x - 18, y + 18], [x + 18, y - 18]], 9); });
  } else {
    ojos.forEach(([x, y]) => elipse(ctx, x, y, 13, 17, LINEA, 0));
  }
  if (v.lentes_sol) {   // lentes oscuros de presumido
    ojos.forEach(([x, y]) => { ctx.beginPath(); ctx.roundRect(x - 46, y - 30, 92, 62, 22); ctx.fillStyle = '#1b1b22'; ctx.fill(); contorno(ctx, 7); ctx.stroke();
      ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.beginPath(); ctx.ellipse(x - 18, y - 12, 14, 7, -0.5, 0, 7); ctx.fill(); });
    linea(ctx, [[cx - 16, cy - 16], [cx + 16, cy - 16]], 8);
  }
  if (v.lentes) { ojos.forEach(([x, y]) => elipse(ctx, x, y, 40, 36, null, 7)); linea(ctx, [[cx - 22, cy - 12], [cx + 22, cy - 12]], 7); }
  // mejillas
  if (c === 'feliz' || c === 'calor') {
    ctx.globalAlpha = 0.45; elipse(ctx, cx - 110, cy + 40, 26, 16, '#ff8a8a', 0); elipse(ctx, cx + 110, cy + 40, 26, 16, '#ff8a8a', 0); ctx.globalAlpha = 1;
  }
  // boca
  const by = cy + 85;
  if (c === 'dormido') { elipse(ctx, cx + 10, by, 14, 10, '#5a1b1b', 6); return; }
  const abierta = habla || ['feliz', 'sorpresa', 'miedo', 'calor'].includes(c);
  if (abierta) {
    ctx.beginPath();
    if (c === 'sorpresa' || c === 'miedo') ctx.ellipse(cx, by + 5, 26, habla ? 34 : 30, 0, 0, Math.PI * 2);
    else { ctx.moveTo(cx - 70, by - 10); ctx.quadraticCurveTo(cx, by - 20, cx + 70, by - 10); ctx.quadraticCurveTo(cx, by + (habla ? 60 : 85), cx - 70, by - 10); }
    ctx.fillStyle = '#5a1b1b'; ctx.fill();
    ctx.save(); ctx.clip();
    if (c !== 'sorpresa' && c !== 'miedo') { ctx.fillStyle = '#ffffff'; ctx.fillRect(cx - 70, by - 22, 140, 22); }
    elipse(ctx, cx, by + 50, 36, 22, '#ff6b7a', 0);
    ctx.restore();
    contorno(ctx, 9); ctx.stroke();
  } else if (c === 'enojado' || c === 'preocupado' || c === 'frio') {
    if (c === 'frio') {
      linea(ctx, Array.from({ length: 7 }, (_, i) => [cx - 45 + i * 15, by + (i % 2 ? 6 : -6)]), 8);
    } else { ctx.beginPath(); ctx.arc(cx, by + 30, 34, Math.PI * 1.2, Math.PI * 1.8); contorno(ctx, 9); ctx.stroke(); }
  } else {
    ctx.beginPath(); ctx.arc(cx, by - 25, 40, Math.PI * 0.2, Math.PI * 0.8); contorno(ctx, 9); ctx.stroke();
  }
  if (v.bigote) {
    ctx.fillStyle = '#4a2c1e';
    [-1, 1].forEach(l => { ctx.beginPath(); ctx.ellipse(cx + l * 38, by - 28, 42, 15, l * 0.25, 0, Math.PI * 2); ctx.fill(); contorno(ctx, 6); ctx.stroke(); });
  }
  if (c === 'calor') {
    const gy = (t * 120) % 70;
    ctx.fillStyle = '#7cc4ff'; ctx.beginPath(); ctx.ellipse(cx + 150, cy - 40 + gy, 12, 18, 0, 0, 7); ctx.fill(); contorno(ctx, 5); ctx.stroke();
  }
}

function sombrero(ctx, v) {
  const cx = 256, cy = 300;
  if (v.sombrero === 'casco' || v.sombrero === 'casco_blanco') {
    const col = v.sombrero === 'casco' ? '#ffc61a' : '#f7f7f7';
    ctx.beginPath(); ctx.ellipse(cx, cy - 95, 165, 120, 0, Math.PI, 0); ctx.closePath();
    ctx.fillStyle = col; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(cx - 200, cy - 112, 400, 34, 17); ctx.fillStyle = col; ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.beginPath(); ctx.ellipse(cx - 70, cy - 165, 40, 16, -0.4, 0, 7); ctx.fill();
    linea(ctx, [[cx, cy - 210], [cx, cy - 120]], 9);
  } else if (v.sombrero === 'copa') {
    ctx.fillStyle = '#1d1a22';
    ctx.beginPath(); ctx.roundRect(cx - 95, cy - 330, 190, 210, 10); ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.fillStyle = '#c8283a'; ctx.fillRect(cx - 89, cy - 170, 178, 34);
    ctx.fillStyle = '#1d1a22'; ctx.beginPath(); ctx.roundRect(cx - 165, cy - 135, 330, 30, 15); ctx.fill(); ctx.stroke();
  } else if (v.sombrero === 'gorra_capitan') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 150, 175, 60, 0, 0, Math.PI * 2); ctx.fillStyle = '#ffffff'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(cx - 130, cy - 150, 260, 55, 10); ctx.fillStyle = '#1f2a4a'; ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx + 40, cy - 92, 120, 22, 0.05, 0, Math.PI * 2); ctx.fillStyle = '#141414'; ctx.fill(); ctx.stroke();
    elipse(ctx, cx, cy - 125, 22, 18, '#f0c040', 6);
  } else if (v.sombrero === 'bombin') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 120, 125, 115, 0, Math.PI, 0); ctx.closePath(); ctx.fillStyle = '#2a2420'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy - 118, 185, 26, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  } else if (v.sombrero === 'pamela') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 115, 240, 40, -0.08, 0, Math.PI * 2); ctx.fillStyle = '#f2d6a2'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy - 145, 120, 70, 0, Math.PI, 0); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#b04f86'; ctx.fillRect(cx - 118, cy - 160, 236, 24);
    [[cx + 95, cy - 165], [cx + 125, cy - 150]].forEach(([x, y]) => elipse(ctx, x, y, 26, 26, '#ff6b8a', 6));
  } else if (v.sombrero === 'marinero') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 135, 140, 50, 0, 0, Math.PI * 2); ctx.fillStyle = '#ffffff'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(cx - 110, cy - 140, 220, 40, 10); ctx.fillStyle = '#2d4fa8'; ctx.fill(); ctx.stroke();
  } else if (v.sombrero === 'gorro_dormir') {
    const cae = Math.sin(Date.now() * 0) * 0;
    ctx.beginPath(); ctx.moveTo(cx - 160, cy - 95); ctx.quadraticCurveTo(cx - 40, cy - 330, cx + 230, cy - 170 + cae);
    ctx.quadraticCurveTo(cx + 60, cy - 210, cx + 165, cy - 95); ctx.closePath();
    ctx.fillStyle = '#8fb8ff'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(cx - 170, cy - 120, 340, 44, 22); ctx.fillStyle = '#ffffff'; ctx.fill(); ctx.stroke();
    elipse(ctx, cx + 232, cy - 165, 30, 30, '#ffffff', 8);
  } else if (v.sombrero === 'capucha') {
    ctx.beginPath(); ctx.moveTo(cx - 185, cy + 60); ctx.quadraticCurveTo(cx - 200, cy - 230, cx, cy - 215);
    ctx.quadraticCurveTo(cx + 200, cy - 230, cx + 185, cy + 60); ctx.quadraticCurveTo(cx + 150, cy - 120, cx, cy - 150);
    ctx.quadraticCurveTo(cx - 150, cy - 120, cx - 185, cy + 60); ctx.closePath();
    ctx.fillStyle = '#7a5233'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
  } else if (v.sombrero === 'cofia') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 110, 175, 90, 0, Math.PI, 0); ctx.closePath(); ctx.fillStyle = '#f4f0e6'; ctx.fill(); contorno(ctx, 10); ctx.stroke();
    for (let i = -3; i <= 3; i++) { ctx.beginPath(); ctx.arc(cx + i * 50, cy - 108, 24, 0, Math.PI); ctx.stroke(); }
  } else if (v.sombrero === 'gorro_lana') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 105, 160, 125, 0, Math.PI, 0); ctx.closePath();
    ctx.fillStyle = v.gorro; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.save(); ctx.clip(); ctx.fillStyle = 'rgba(0,0,0,0.12)'; for (let x = cx - 160; x < cx + 160; x += 40) ctx.fillRect(x, cy - 240, 14, 140); ctx.restore();
    ctx.beginPath(); ctx.roundRect(cx - 172, cy - 128, 344, 52, 22); ctx.fillStyle = '#f4f4f4'; ctx.fill(); ctx.stroke();
    elipse(ctx, cx, cy - 240, 40, 38, '#f4f4f4', 9);
  } else if (v.sombrero === 'orejeras') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 20, 178, 170, 0, Math.PI * 1.08, Math.PI * 1.92); ctx.lineWidth = 34; ctx.strokeStyle = LINEA; ctx.stroke();
    ctx.lineWidth = 20; ctx.strokeStyle = '#555'; ctx.stroke();
    [-1, 1].forEach(l => elipse(ctx, cx + l * 168, cy + 5, 52, 60, v.orejeras, 10));
  } else if (v.sombrero === 'casco_bombero') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 100, 230, 40, 0, 0, Math.PI * 2); ctx.fillStyle = '#a81f2e'; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy - 120, 150, 125, 0, Math.PI, 0); ctx.closePath(); ctx.fillStyle = '#d62f3e'; ctx.fill(); ctx.stroke();
    linea(ctx, [[cx, cy - 240], [cx, cy - 125]], 10);
    ctx.beginPath(); ctx.moveTo(cx, cy - 225); ctx.lineTo(cx + 40, cy - 190); ctx.lineTo(cx, cy - 140); ctx.lineTo(cx - 40, cy - 190); ctx.closePath();
    ctx.fillStyle = '#f0c040'; ctx.fill(); contorno(ctx, 7); ctx.stroke();
  } else if (v.sombrero === 'gorra') {
    ctx.beginPath(); ctx.ellipse(cx, cy - 110, 150, 95, 0, Math.PI, 0); ctx.closePath();
    ctx.fillStyle = v.gorra; ctx.fill(); contorno(ctx, 11); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx + 120, cy - 112, 95, 22, 0.1, 0, 7); ctx.fill(); ctx.stroke();
  }
}

function falda(ctx, v) {
  ctx.beginPath(); ctx.moveTo(180, 690); ctx.lineTo(332, 690); ctx.lineTo(380, 900); ctx.quadraticCurveTo(256, 930, 132, 900); ctx.closePath();
  ctx.fillStyle = v.saco; ctx.fill(); contorno(ctx, 11); ctx.stroke();
}

function dibujar(ctx, v, tipo, est, t) {
  ctx.clearRect(0, 0, W, H);
  const bote = est.quieto ? 0 : Math.abs(Math.sin(t * 4 + (est.semilla || 0))) * 8;
  ctx.save(); ctx.translate(0, -bote - (est.salto || 0));
  if (est.tiembla) ctx.translate(Math.sin(t * 70) * 8 * est.tiembla, 0);
  // piernas delgadas y zapatos
  [-1, 1].forEach(l => {
    const pasos = est.camina ? Math.sin(t * 10 + (l > 0 ? Math.PI : 0)) * 22 : 0;
    linea(ctx, [[256 + l * 42, 730], [256 + l * 48 + pasos, 960 + bote]], 15);
    elipse(ctx, 256 + l * 48 + pasos + l * 12, 968 + bote, 42, 20, '#2a2220', 7);
  });
  const ropa = v.saco || v.camisa;
  const [bi, bd] = est.brazos || [15, 15];
  brazo(ctx, -1, bi, est.codos ? est.codos[0] : 10, ropa);
  if (v.vestido) falda(ctx, v);
  cuerpo(ctx, v, tipo);
  const mano = brazo(ctx, 1, bd, est.codos ? est.codos[1] : 10, ropa);
  if (est.objeto === 'vela') {
    ctx.save(); ctx.translate(mano[0], mano[1] - 20);
    ctx.fillStyle = '#c9b38a'; ctx.beginPath(); ctx.ellipse(0, 22, 40, 12, 0, 0, 7); ctx.fill(); contorno(ctx, 6); ctx.stroke();
    ctx.fillStyle = '#fff6dc'; ctx.fillRect(-12, -50, 24, 66); ctx.strokeRect(-12, -50, 24, 66);
    const f = 1 + Math.sin(t * 20) * 0.12;
    ctx.fillStyle = 'rgba(255,200,60,0.35)'; ctx.beginPath(); ctx.arc(0, -72, 46 * f, 0, 7); ctx.fill();
    ctx.fillStyle = '#ffb300'; ctx.beginPath(); ctx.ellipse(0, -70, 12 * f, 22 * f, 0, 0, 7); ctx.fill();
    ctx.restore();
  }
  if (est.objeto === 'sal' || est.objeto === 'arena') {   // bulto con letrero
    const sal = est.objeto === 'sal';
    ctx.save(); ctx.translate(mano[0], mano[1] + 10); ctx.rotate(-0.15);
    ctx.beginPath(); ctx.roundRect(-58, -40, 116, 140, 18); ctx.fillStyle = sal ? '#f4f4f4' : '#c9a066'; ctx.fill(); contorno(ctx, 8); ctx.stroke();
    ctx.fillStyle = sal ? '#2d6fd6' : '#7a4b2a'; ctx.fillRect(-50, 0, 100, 50);
    ctx.fillStyle = '#ffffff'; ctx.font = `${sal ? 44 : 30}px Anton`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(sal ? 'SAL' : 'ARENA', 0, 27);
    ctx.restore();
  }
  if (est.objeto === 'taza') {
    ctx.save(); ctx.translate(mano[0], mano[1] - 30);
    ctx.beginPath(); ctx.roundRect(-34, -40, 68, 74, 10); ctx.fillStyle = '#e23c3c'; ctx.fill(); contorno(ctx, 8); ctx.stroke();
    ctx.beginPath(); ctx.arc(40, -4, 18, -1.2, 1.2); ctx.stroke();
    ctx.globalAlpha = 0.6; [-14, 12].forEach((x, i) => { const k = (t * 0.8 + i * 0.5) % 1; ctx.beginPath(); ctx.arc(x + Math.sin(t * 4 + i) * 6, -60 - k * 60, 10 + k * 8, 0, 7); ctx.fillStyle = '#ffffff'; ctx.fill(); });
    ctx.restore();
  }
  if (est.objeto === 'vaso') {   // vaso de agua
    ctx.save(); ctx.translate(mano[0], mano[1] - 30); ctx.rotate(est.vuelca || 0);
    ctx.beginPath(); ctx.moveTo(-34, -60); ctx.lineTo(34, -60); ctx.lineTo(26, 40); ctx.lineTo(-26, 40); ctx.closePath();
    ctx.fillStyle = 'rgba(220,240,255,0.85)'; ctx.fill(); contorno(ctx, 7); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-31, -30); ctx.lineTo(31, -30); ctx.lineTo(26, 40); ctx.lineTo(-26, 40); ctx.closePath(); ctx.fillStyle = '#3d9bf0'; ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.7)'; ctx.fillRect(-22, -20, 8, 50);
    ctx.restore();
  }
  if (est.objeto === 'tapa') {   // tapa de olla
    ctx.save(); ctx.translate(mano[0], mano[1] - 40); ctx.rotate(-0.25);
    ctx.beginPath(); ctx.ellipse(0, 0, 95, 30, 0, Math.PI, 0); ctx.closePath(); ctx.fillStyle = '#b9c0c8'; ctx.fill(); contorno(ctx, 8); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0, 0, 100, 10, 0, 0, 7); ctx.fillStyle = '#8a9099'; ctx.fill(); ctx.stroke();
    elipse(ctx, 0, -38, 22, 12, '#2b2b2b', 6);
    ctx.fillStyle = 'rgba(255,255,255,0.6)'; ctx.beginPath(); ctx.ellipse(-40, -14, 22, 7, -0.3, 0, 7); ctx.fill();
    ctx.restore();
  }
  if (est.objeto === 'manguera') {
    ctx.save(); ctx.translate(mano[0], mano[1]);
    linea(ctx, [[0, 0], [-40, 120], [-120, 160]], 26); linea(ctx, [[0, 0], [-40, 120], [-120, 160]], 14, '#d6b030');
    ctx.fillStyle = '#c0c0c0'; ctx.beginPath(); ctx.roundRect(-14, -60, 28, 64, 6); ctx.fill(); contorno(ctx, 6); ctx.stroke();
    ctx.restore();
  }
  if (est.objeto === 'celular') {
    ctx.save(); ctx.translate(mano[0] - 10, mano[1] - 50); ctx.rotate(-0.2);
    ctx.fillStyle = 'rgba(120,190,255,0.35)'; ctx.beginPath(); ctx.arc(0, 0, 70, 0, 7); ctx.fill();
    ctx.fillStyle = '#222'; ctx.fillRect(-26, -46, 52, 92); ctx.fillStyle = '#7cc4ff'; ctx.fillRect(-20, -38, 40, 74); ctx.restore();
  }
  if (est.objeto === 'plano') {
    ctx.save(); ctx.translate(mano[0], mano[1]); ctx.rotate(-0.5);
    ctx.fillStyle = '#4b8fe0'; ctx.fillRect(-14, -90, 28, 120); contorno(ctx, 6); ctx.strokeRect(-14, -90, 28, 120); ctx.restore();
  }
  // cabeza blanca con sombreado suave
  if (v.pelo) { elipse(ctx, 256 - 160, 320, 40, 60, v.pelo, 8); elipse(ctx, 256 + 160, 320, 40, 60, v.pelo, 8); }
  if (v.pelo_largo) { ctx.beginPath(); ctx.roundRect(70, 200, 372, 330, 120); ctx.fillStyle = v.pelo_largo; ctx.fill(); contorno(ctx, 10); ctx.stroke(); }
  if (v.chongo) elipse(ctx, 256, 130, 70, 55, v.pelo_largo, 10);
  if (v.mono_pelo) { [-1, 1].forEach(l => elipse(ctx, 256 + l * 175, 200, 40, 30, v.mono_pelo, 8)); }
  elipse(ctx, 256, 300, 172, 160, '#ffffff', 12);
  if (v.aretes) [-1, 1].forEach(l => elipse(ctx, 256 + l * 168, 380, 14, 14, '#ffd600', 6));
  ctx.save(); ctx.beginPath(); ctx.ellipse(256, 300, 166, 154, 0, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = 'rgba(120,130,160,0.16)'; ctx.beginPath(); ctx.ellipse(196, 360, 175, 150, 0, 0, 7); ctx.ellipse(256, 300, 200, 200, 0, 0, 7); ctx.fill('evenodd');
  ctx.restore();
  if (v.barba) {
    ctx.beginPath(); ctx.moveTo(110, 330); ctx.quadraticCurveTo(120, 480, 256, 500); ctx.quadraticCurveTo(392, 480, 402, 330);
    ctx.quadraticCurveTo(330, 400, 256, 400); ctx.quadraticCurveTo(182, 400, 110, 330); ctx.closePath();
    ctx.fillStyle = v.barba; ctx.fill(); contorno(ctx, 9); ctx.stroke();
  }
  cara(ctx, v, est, t);
  sombrero(ctx, v);
  if (est.zzz) {  // "Z z z" flotando
    ctx.font = '90px Anton'; ctx.textAlign = 'center'; ctx.lineJoin = 'round';
    [0, 1, 2].forEach(i => {
      const k = (t * 0.8 + i / 3) % 1, x = 380 + k * 90, y = 170 - k * 150, tam = 0.5 + k * 0.6;
      ctx.save(); ctx.translate(x, y); ctx.scale(tam, tam); ctx.globalAlpha = 1 - k * 0.6;
      ctx.lineWidth = 14; ctx.strokeStyle = LINEA; ctx.strokeText('Z', 0, 0); ctx.fillStyle = '#ffffff'; ctx.fillText('Z', 0, 0);
      ctx.restore();
    });
  }
  ctx.restore();
}

// En la cama: canvas horizontal (1024x512). est.inclina: 0 = acostado, 1 = sentado.
const CW = 1024, CH = 512;
function dibujarCama(ctx, v, tipo, est, t) {
  ctx.clearRect(0, 0, CW, CH);
  const k = est.inclina ?? 0;
  const respira = Math.sin(t * 2.2) * 6 * (1 - k);
  // almohada
  // almohada: acostado queda bajo la cabeza; sentado, atrás de la espalda
  const ax = 175 + k * 230, ay = 400 - k * 150, rx = 140 - k * 40, ry = 58 + k * 40;
  ctx.beginPath(); ctx.ellipse(ax, ay, rx, ry, -0.05 - k * 0.3, 0, Math.PI * 2);
  ctx.fillStyle = '#f2f2f6'; ctx.fill(); contorno(ctx, 9); ctx.stroke();
  // cuerpo de la cintura para arriba, girando sobre la cadera
  const hx = 440, hy = 420;
  ctx.save();
  ctx.translate(hx, hy + respira * 0.3); ctx.rotate(-(1 - k) * Math.PI / 2 * 0.98); ctx.scale(0.6, 0.6); ctx.translate(-256, -730);
  const ropa = v.saco || v.camisa;
  const [bi, bd] = est.brazos || [15, 15];
  brazo(ctx, -1, bi, est.codos ? est.codos[0] : 10, ropa);
  cuerpo(ctx, v, tipo);
  brazo(ctx, 1, bd, est.codos ? est.codos[1] : 10, ropa);
  if (v.pelo) { elipse(ctx, 96, 320, 40, 60, v.pelo, 8); elipse(ctx, 416, 320, 40, 60, v.pelo, 8); }
  elipse(ctx, 256, 300, 172, 160, '#ffffff', 12);
  cara(ctx, v, est, t);
  sombrero(ctx, v);
  ctx.restore();
  // cobija: tapa las piernas y, acostado, también el pecho
  const izq = 330 + k * 200;
  const arriba = hy - 95 + k * 30 - respira;
  ctx.beginPath(); ctx.moveTo(izq, CH - 20); ctx.lineTo(izq - 20, arriba + 30);
  ctx.quadraticCurveTo(izq + 40, arriba - 20, izq + 200, arriba); ctx.quadraticCurveTo(700, arriba + 10, 820, arriba + 35);
  ctx.quadraticCurveTo(960, arriba + 20, 1000, arriba + 70); ctx.lineTo(1010, CH - 20); ctx.closePath();
  ctx.fillStyle = est.cobija || '#2d6fd6'; ctx.fill();
  ctx.save(); ctx.clip();
  ctx.fillStyle = '#ffd600'; for (let x = izq + 60; x < 1010; x += 120) ctx.fillRect(x, 0, 26, CH);
  ctx.fillStyle = '#f4f4f4'; ctx.fillRect(0, arriba - 10, CW, 46);        // doblez blanco de la sábana
  ctx.restore();
  contorno(ctx, 11); ctx.stroke();
  if (est.zzz) {
    ctx.font = '110px Anton'; ctx.textAlign = 'center'; ctx.lineJoin = 'round';
    [0, 1, 2].forEach(i => {
      const q = (t * 0.8 + i / 3) % 1, x = 330 + q * 160, y = 220 - q * 190, tam = 0.5 + q * 0.6;
      ctx.save(); ctx.translate(x, y); ctx.scale(tam, tam); ctx.globalAlpha = 1 - q * 0.6;
      ctx.lineWidth = 14; ctx.strokeStyle = LINEA; ctx.strokeText('Z', 0, 0); ctx.fillStyle = '#ffffff'; ctx.fillText('Z', 0, 0);
      ctx.restore();
    });
  }
}

// Personaje acostado o sentado en la cama (no atraviesa la cama: trae su propia almohada y cobija)
export class PersonajeCama {
  constructor(tipo = 'dormilon', ancho = 6, calidad = 1) {
    this.tipo = tipo; this.v = VESTUARIOS[tipo]; this.q = calidad;
    this.canvas = document.createElement('canvas');
    this.canvas.width = Math.round(CW * calidad); this.canvas.height = Math.round(CH * calidad);
    this.ctx = this.canvas.getContext('2d');
    this.tex = new THREE.CanvasTexture(this.canvas); this.tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, alphaTest: 0.4, side: THREE.DoubleSide });
    mat.userData.outlineParameters = { visible: false };
    mat.color.setScalar(0.9);   // un poquito menos que blanco puro: así el brillo (bloom) no los quema
    const geo = new THREE.PlaneGeometry(ancho, ancho / 2); geo.translate(0, ancho / 4, 0);
    this.malla = new THREE.Mesh(geo, mat);
    this.estado = { cara: 'dormido', inclina: 0, semilla: Math.random() * 10 };
  }
  actualizar(t, a = {}, b) {          // acepta (t, cambios) o (t, camara, cambios)
    const cambios = b || (a && !a.isCamera ? a : {});
    Object.assign(this.estado, cambios);
    this.ctx.setTransform(this.q, 0, 0, this.q, 0, 0);
    dibujarCama(this.ctx, this.v, this.tipo, this.estado, t);
    this.tex.needsUpdate = true;
  }
}

export class Personaje2D {
  // calidad < 1 usa un canvas más chico (para gente de fondo: mucho más rápido)
  constructor(tipo = 'obrero', alto = 4.4, calidad = 1) {
    this.tipo = tipo;
    this.v = VESTUARIOS[tipo];
    this.q = calidad;
    this.canvas = document.createElement('canvas');
    this.canvas.width = Math.round(W * calidad); this.canvas.height = Math.round(H * calidad);
    this.ctx = this.canvas.getContext('2d');
    this.tex = new THREE.CanvasTexture(this.canvas);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    this.tex.anisotropy = 4;
    const mat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, alphaTest: 0.4, side: THREE.DoubleSide });
    mat.userData.outlineParameters = { visible: false };
    mat.color.setScalar(0.9);   // un poquito menos que blanco puro: así el brillo (bloom) no los quema
    const geo = new THREE.PlaneGeometry(alto / 2, alto);
    geo.translate(0, alto / 2, 0);
    this.malla = new THREE.Mesh(geo, mat);
    this.malla.castShadow = true;
    this.malla.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: this.tex, alphaTest: 0.4 });
    this.estado = { cara: 'normal', brazos: [15, 15], semilla: Math.random() * 10 };
  }
  agregar(escena, x, z, y = 0) { this.malla.position.set(x, y, z); escena.add(this.malla); return this; }
  // redibujar = false solo voltea hacia la cámara (para gente de fondo, ahorra tiempo)
  actualizar(t, camara, cambios = {}, redibujar = true) {
    Object.assign(this.estado, cambios);
    if (redibujar || !this._listo) {
      this.ctx.setTransform(this.q, 0, 0, this.q, 0, 0);
      dibujar(this.ctx, this.v, this.tipo, this.estado, t);
      this.tex.needsUpdate = true;
      this._listo = true;
    }
    // siempre de frente a la cámara (solo gira en el eje vertical)
    const p = this.malla.getWorldPosition(new THREE.Vector3());
    const padre = this.malla.parent ? this.malla.parent.getWorldQuaternion(new THREE.Quaternion()) : null;
    const giroPadre = padre ? new THREE.Euler().setFromQuaternion(padre, 'YXZ').y : 0;
    this.malla.rotation.y = Math.atan2(camara.position.x - p.x, camara.position.z - p.z) - giroPadre;
    this.malla.scale.x = this.estado.voltear ? -1 : 1;
  }
}
