// Corre el código de UN nodo «Code» de n8n fuera de n8n, con datos de prueba inventados.
// Uso:  node scripts/probar_codigo.mjs codigo/ARCHIVO.js ENTRADA.json
// ENTRADA.json:
//   { "entrada":  [ {"json": {...}}, ... ],          // lo que el nodo recibe: $input.all()
//     "nodos":    { "Nombre del nodo": [ {"json": {...}} ] },   // lo que devuelve $('Nombre del nodo')
//     "binarios": { "meta": "texto del archivo" },    // lo que lee this.helpers.getBinaryDataBuffer(0, 'meta')
//     "ahora":    "2026-05-01T12:00:00Z" }            // fecha fija para Date.now()
// Salida (siempre JSON en pantalla): {"ok":true,"items":[...]} o {"ok":false,"error":"..."}; código 0 / 1 / 2 (uso mal).
// Imita las reglas de n8n: el código debe devolver una lista de {json:{...}} y $('Nodo') falla si el nodo no corrió.
// No es n8n: solo prueba la lógica. No usa red, no escribe archivos, no lee nada fuera de los dos archivos que le pasas.
import { readFileSync } from 'node:fs';

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const [, , archivoCodigo, archivoEntrada] = process.argv;
if (!archivoCodigo || !archivoEntrada) {
  console.log(JSON.stringify({ ok: false, error: 'Uso: node probar_codigo.mjs codigo/ARCHIVO.js ENTRADA.json' }));
  process.exit(2);
}

const esObjeto = (x) => x !== null && typeof x === 'object' && !Array.isArray(x);
const salir = (obj, codigo) => { console.log(JSON.stringify(obj)); process.exit(codigo); };

let datos, codigo;
try {
  codigo = readFileSync(archivoCodigo, 'utf8');
  datos = JSON.parse(readFileSync(archivoEntrada, 'utf8'));
} catch (e) {
  salir({ ok: false, error: `No pude leer los archivos: ${e.message}` }, 2);
}

const items = (lista) => (Array.isArray(lista) ? lista : []).map((j) => (esObjeto(j) && 'json' in j ? j : { json: j }));
const vista = (lista) => {
  const l = items(lista);
  return { all: () => l, first: () => l[0], last: () => l[l.length - 1], isExecuted: true };
};

const entrada = vista(datos.entrada);
const nodos = datos.nodos || {};
const dolar = (nombre) => {
  if (!(nombre in nodos)) throw new Error(`Node '${nombre}' hasn't been executed (el nodo no corrió o el nombre está mal escrito)`);
  return vista(nodos[nombre]);
};
const binarios = datos.binarios || {};
const contexto = {
  helpers: {
    async getBinaryDataBuffer(indice, propiedad) {
      if (!(propiedad in binarios)) throw new Error(`El item ${indice} no tiene datos binarios llamados «${propiedad}»`);
      return Buffer.from(String(binarios[propiedad]), 'utf8');
    },
  },
};

if (datos.ahora) {
  const t = Date.parse(datos.ahora);
  if (Number.isNaN(t)) salir({ ok: false, error: '«ahora» no es una fecha válida' }, 2);
  Date.now = () => t;
}

try {
  const fn = new AsyncFunction('$input', '$', codigo);
  const salida = await fn.call(contexto, entrada, dolar);
  if (!Array.isArray(salida)) throw new Error('El código debe devolver una lista (return [...])');
  salida.forEach((it, i) => {
    if (!esObjeto(it)) throw new Error(`El resultado ${i} no es un objeto`);
    if (!esObjeto(it.json)) throw new Error(`El resultado ${i} no tiene «json» como objeto (n8n lo rechaza)`);
  });
  salir({ ok: true, items: salida }, 0);
} catch (e) {
  salir({ ok: false, error: String(e && e.message ? e.message : e) }, 1);
}
