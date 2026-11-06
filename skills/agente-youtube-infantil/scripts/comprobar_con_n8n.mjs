// Comprueba con las reglas de n8n de verdad (su propio código) que cada nodo de una plantilla es válido:
// que el tipo y la versión existen, que no sobran ni faltan campos obligatorios y que las opciones tienen valores permitidos.
// Uso:  node scripts/comprobar_con_n8n.mjs CARPETA-DONDE-INSTALASTE-n8n plantillas/ARCHIVO.json [...]
//   (la carpeta es la que contiene node_modules/n8n-nodes-base; se instala aparte con «npm install n8n@2.46.6», ver references/configuracion-paso-a-paso.md)
// Salida: una línea por problema; código 0 si no hay ninguno, 1 si hay, 2 si se usó mal. Solo lee: no abre redes ni toca la base de datos de n8n.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';

const [, , carpeta, ...archivos] = process.argv;
if (!carpeta || !archivos.length) {
  console.error('Uso: node comprobar_con_n8n.mjs CARPETA-DE-N8N plantillas/ARCHIVO.json [...]');
  process.exit(2);
}
const req = createRequire(join(resolve(carpeta), 'package.json'));
const { NodeHelpers } = req('n8n-workflow');
const base = req.resolve('n8n-nodes-base/package.json').replace(/package\.json$/, '');
const archivosDeNodos = JSON.parse(readFileSync(join(base, 'package.json'), 'utf8')).n8n.nodes;   // «dist/nodes/Google/YouTube/YouTube.node.js»…

// El nombre corto del tipo («youTube» de «n8n-nodes-base.youTube») coincide, sin mayúsculas, con el nombre del archivo.
const cache = new Map();
const cargarTipo = (tipo) => {
  if (cache.has(tipo)) return cache.get(tipo);
  let res = null;
  const corto = tipo.replace(/^n8n-nodes-base\./, '').toLowerCase();
  const arch = archivosDeNodos.find((a) => a.split('/').pop().replace(/\.node\.js$/, '').toLowerCase() === corto);
  if (arch && tipo.startsWith('n8n-nodes-base.')) {
    const Clase = Object.values(req(join(base, arch)))[0];
    const inst = new Clase();
    if (inst.description.name === tipo.replace(/^n8n-nodes-base\./, '')) res = inst;
  }
  cache.set(tipo, res);
  return res;
};

let problemas = 0;
const avisar = (arch, nodo, texto) => { problemas++; console.log(`${arch} · ${nodo}: ${texto}`); };

for (const arch of archivos) {
  const wf = JSON.parse(readFileSync(arch, 'utf8'));
  for (const n of wf.nodes) {
    const t = cargarTipo(n.type);
    if (!t) { avisar(arch, n.name, `el tipo «${n.type}» no existe en esta versión de n8n`); continue; }
    let desc;
    if (t.nodeVersions) {                            // nodos con varias versiones (Telegram 1.2, IF 2.2, HTTP 4.2…)
      const v = t.nodeVersions[n.typeVersion];
      if (!v) { avisar(arch, n.name, `la versión ${n.typeVersion} de «${n.type}» no existe`); continue; }
      desc = v.description;
    } else {
      desc = t.description;
      if (![].concat(desc.version).includes(n.typeVersion)) { avisar(arch, n.name, `la versión ${n.typeVersion} de «${n.type}» no existe`); continue; }
    }
    const nodoN8n = { ...n, parameters: n.parameters || {} };
    const params = NodeHelpers.getNodeParameters(desc.properties, nodoN8n.parameters, true, false, nodoN8n, desc);
    nodoN8n.parameters = params || {};
    const problemasNodo = NodeHelpers.getNodeParametersIssues(desc.properties, nodoN8n, desc);
    for (const [campo, textos] of Object.entries(problemasNodo?.parameters || {})) {
      for (const tx of textos) avisar(arch, n.name, `campo «${campo}»: ${tx}`);
    }
    for (const [cred, textos] of Object.entries(problemasNodo?.credentials || {})) {
      if (!/not set|no.*set/i.test(String(textos))) avisar(arch, n.name, `credencial «${cred}»: ${textos}`);
    }
  }
}
console.log(problemas ? `\n${problemas} problema(s).` : 'n8n no encontró problemas en los nodos.');
process.exit(problemas ? 1 : 0);
