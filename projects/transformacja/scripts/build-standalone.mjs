import { readFile, mkdir, writeFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const htmlPath = new URL('prototype/index.html', root);
const simPath = new URL('src/simulation.js', root);
const appPath = new URL('src/app.js', root);
const historicalPath = new URL('src/historical.js', root);
const outDir = new URL('dist/', root);
const outPath = new URL('dist/transformacja.html', root);

const [html, simulation, historical, app] = await Promise.all([
  readFile(htmlPath, 'utf8'),
  readFile(simPath, 'utf8'),
  readFile(historicalPath, 'utf8'),
  readFile(appPath, 'utf8')
]);
const bundledSimulation = simulation.replace(/^export\s+/gm, '');
const bundledHistorical = historical.replace(/^export\s+/gm, '');
const bundledApp = app.replace(/^import\s+.*?;\s*$/gm, '');
const inline = `<script>\n${bundledSimulation}\n${bundledHistorical}\n${bundledApp}\n</script>`;
const standalone = html.replace('<script type="module" src="../src/app.js"></script>', inline);
if (standalone === html) throw new Error('Could not locate app module entrypoint in prototype/index.html');
await mkdir(outDir, { recursive:true });
await writeFile(outPath, standalone, 'utf8');
console.log(`Built ${outPath.pathname}`);
