// Convierte una página 3D (three.js) en video MP4 cuadro por cuadro.
// Uso: node motor3d/render.js motor3d/escenas/prueba.html salida/prueba3d.mp4 [fps]
// La página debe definir window.DURACION, window.listo (promesa) y
// window.cuadro(t) → dataURL JPEG del cuadro del segundo t.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const RAIZ = path.resolve(__dirname, '..');
const [pagina, salida, fpsTxt] = process.argv.slice(2);
const FPS = parseInt(fpsTxt || '30', 10);

const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.ttf': 'font/ttf', '.json': 'application/json' };

const servidor = http.createServer((req, res) => {
  const ruta = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!ruta.startsWith(RAIZ) || !fs.existsSync(ruta)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TIPOS[path.extname(ruta)] || 'application/octet-stream' });
  fs.createReadStream(ruta).pipe(res);
});

(async () => {
  await new Promise(r => servidor.listen(0, r));
  const puerto = servidor.address().port;
  const navegador = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await navegador.newPage({ viewport: { width: 540, height: 960 } });
  page.on('console', m => { if (m.type() === 'error') console.error('[página]', m.text()); });
  page.on('pageerror', e => console.error('[página]', e.message));
  await page.goto(`http://localhost:${puerto}/${pagina}`);
  await page.waitForFunction(() => window.listo !== undefined, null, { timeout: 60000 });
  await page.evaluate(() => window.listo);
  const duracion = await page.evaluate(() => window.DURACION);
  const n = Math.round(duracion * FPS);

  fs.mkdirSync(path.dirname(path.resolve(salida)), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS),
    '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', salida], { stdio: ['pipe', 'inherit', 'inherit'] });

  const inicio = Date.now();
  for (let i = 0; i < n; i++) {
    const url = await page.evaluate(t => window.cuadro(t), i / FPS);
    const buf = Buffer.from(url.split(',')[1], 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % FPS === 0) process.stdout.write(`\r  cuadro ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log(`\r  listo: ${n} cuadros en ${((Date.now() - inicio) / 1000).toFixed(1)} s → ${salida}`);
  await navegador.close();
  servidor.close();
})().catch(e => { console.error(e); process.exit(1); });
