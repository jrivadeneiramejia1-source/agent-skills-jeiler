#!/usr/bin/env python3
"""Revisa un flujo de n8n exportado (archivo .json) y avisa riesgos comunes.

Uso:   python -I revisar_flujo.py FLUJO.json [--json]
Salida: 0 = sin hallazgos graves, 1 = hay hallazgos ALTA, 2 = no se pudo leer el archivo.

Solo lee el archivo: no abre redes, no ejecuta nada de lo que hay dentro y NUNCA imprime
el valor de una clave: solo dice en qué nodo la encontró y de qué tipo parece.
Busca patrones; que salga limpio NO prueba que el flujo sea seguro.
"""
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 20 * 1024 * 1024

# (nombre, regex). Solo se reporta el nombre, nunca el texto encontrado.
PATRONES_CLAVE = [
    ("token de bot de Telegram", re.compile(r"(?<!\d)\d{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])")),
    ("clave tipo sk-... (OpenAI, Anthropic y similares)", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("clave de Google (AIza...)", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("token de GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("token de Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("clave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("llave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("encabezado Bearer con valor fijo", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}")),
]
NOMBRES_SENSIBLES = re.compile(r"(?i)(authorization|api[-_]?key|apikey|x-api-key|token|secret|password|passwd|clave)")
CORREO = re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TELEFONO = re.compile(r"(?<![\w.])\+?\d{10,13}(?![\w.])")
ID_USUARIO = re.compile(r"(from\??\.id|chat\??\.id|message\??\.from|user_?id|from\.id)", re.I)

TIPOS_PELIGRO = ("executecommand",)
HERRAMIENTAS_RIESGO = ("gmailtool", "executecommand", "httprequesttool", "codetool", "googledrivetool",
                       "telegramtool", "whatsapptool", "slacktool", "microsoftoutlooktool")
CODIGO_PELIGROSO = re.compile(r"(child_process|\beval\s*\(|new\s+Function\s*\(|\bexecSync\b|\bspawn\s*\()")


# Marcadores como <YOUR_API_KEY>, "your_api_key", $OPENAI_API_KEY: no son claves, son huecos por llenar.
MARCADOR = re.compile(r"(?i)(your[_ -]|insert|replace|change[_-]?me|xxx|<[^<>]{2,}>|\[[^\]]{3,}\]|\$[A-Za-z_{]|undefined|example|placeholder|tu[_-]clave|^\s*(bearer\s*)?$)")


def corto(texto, n=40):
    texto = str(texto)
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def recorrer(valor, ruta=""):
    """Da (ruta, texto) de cada texto dentro de un valor JSON."""
    if isinstance(valor, str):
        yield ruta, valor
    elif isinstance(valor, dict):
        for k, v in valor.items():
            yield from recorrer(v, f"{ruta}.{k}" if ruta else str(k))
    elif isinstance(valor, list):
        for i, v in enumerate(valor):
            yield from recorrer(v, f"{ruta}[{i}]")


def es_expresion(texto):
    return texto.lstrip().startswith("=") or "{{" in texto


def revisar_flujo(wf):
    """Devuelve una lista de hallazgos: dicts con id, gravedad, nodo, texto."""
    h = []

    def add(id_, grav, nodo, texto):
        h.append({"id": id_, "gravedad": grav, "nodo": corto(nodo) if nodo else "(flujo)", "texto": texto})

    nodos = wf.get("nodes")
    if not isinstance(nodos, list) or not nodos:
        raise ValueError("no parece un flujo de n8n: falta la lista «nodes»")
    nodos = [n for n in nodos if isinstance(n, dict)]
    tipo = lambda n: str(n.get("type", "")).lower()  # noqa: E731
    nombre = lambda n: n.get("name", "?")  # noqa: E731
    activos = [n for n in nodos if not n.get("disabled")]

    # F01 claves escritas
    for n in nodos:
        vistos = set()
        for ruta, txt in recorrer(n.get("parameters", {})):
            for etiqueta, rx in PATRONES_CLAVE:
                m = rx.search(txt)
                if m and not MARCADOR.search(m.group(0)) and etiqueta not in vistos:
                    vistos.add(etiqueta)
                    add("F01", "ALTA", nombre(n), f"Parece haber un {etiqueta} escrito dentro del nodo. Usa una credencial de n8n.")
    # F02 encabezados o parámetros sensibles con valor fijo
    for n in nodos:
        p = n.get("parameters", {}) or {}
        for bloque in ("headerParameters", "queryParameters", "bodyParameters"):
            lista = (p.get(bloque) or {}).get("parameters") if isinstance(p.get(bloque), dict) else None
            for par in lista or []:
                if not isinstance(par, dict):
                    continue
                nom, val = str(par.get("name", "")), par.get("value")
                if NOMBRES_SENSIBLES.search(nom) and isinstance(val, str) and val.strip() and not es_expresion(val) and not MARCADOR.search(val):
                    add("F02", "ALTA", nombre(n), f"El campo «{corto(nom, 25)}» lleva un valor fijo en el nodo. Usa una credencial.")
    # F03 webhook y disparadores abiertos
    hay_accion = any(any(t in tipo(n) for t in HERRAMIENTAS_RIESGO + ("gmail", "sendemail", "slack", "executecommand", "googledrive", "httprequest"))
                     for n in activos if "trigger" not in tipo(n) and "webhook" not in tipo(n))
    for n in activos:
        if tipo(n).endswith("n8n-nodes-base.webhook"):
            auth = str((n.get("parameters") or {}).get("authentication", "none")).lower()
            if auth in ("none", ""):
                add("F03", "ALTA" if hay_accion else "MEDIA", nombre(n),
                    "El webhook no pide autenticación: cualquiera que conozca la URL puede dispararlo. Usa «Header Auth» o «Basic Auth».")
    # F04 Telegram sin filtro de usuario
    triggers_tg = [n for n in activos if tipo(n).endswith("telegramtrigger")]
    if triggers_tg:
        resto = [n for n in activos if n not in triggers_tg]
        hay_filtro = any(ID_USUARIO.search(txt) for n in resto if any(k in tipo(n) for k in (".if", "switch", "filter", "code"))
                         for _, txt in recorrer(n.get("parameters", {})))
        if not hay_filtro:
            add("F04", "ALTA", nombre(triggers_tg[0]),
                "No veo ningún nodo IF/Switch/Filter que compare el número de usuario (from.id). Si el bot es público, cualquiera puede darle órdenes.")
    # F05 comandos y código peligroso
    for n in activos:
        if any(t in tipo(n) for t in TIPOS_PELIGRO):
            add("F05", "ALTA", nombre(n), "Ejecuta comandos del sistema. Revísalo a mano: que ningún texto de un mensaje llegue ahí.")
        elif tipo(n).endswith(".code") or tipo(n).endswith("codetool"):
            codigo = " ".join(str(v) for v in (n.get("parameters") or {}).values() if isinstance(v, str))
            if CODIGO_PELIGROSO.search(codigo):
                add("F05", "MEDIA", nombre(n), "El código usa eval, new Function o child_process. Revisa que no reciba texto de personas.")
    # F06 agente con herramientas que escriben
    for n in activos:
        if "agent" in tipo(n) and "tool" not in tipo(n):
            herr = [m for m in activos if any(t in tipo(m) for t in HERRAMIENTAS_RIESGO)]
            if herr:
                add("F06", "MEDIA", nombre(n),
                    f"El agente tiene {len(herr)} herramienta(s) que pueden enviar, escribir o ejecutar. Acciones de riesgo con aprobación humana (ver seguridad-agentes).")
            break
    # F07 sin manejo de errores
    tiene_error_wf = bool((wf.get("settings") or {}).get("errorWorkflow")) or any(tipo(n).endswith("errortrigger") for n in nodos)
    tiene_on_error = any(n.get("onError") for n in nodos)
    if not tiene_error_wf and not tiene_on_error:
        add("F07", "MEDIA", None, "Sin «Error workflow» ni «On Error» en ningún nodo: si algo falla, nadie se entera.")
    # F08 datos de prueba guardados
    pin = wf.get("pinData")
    if isinstance(pin, dict) and pin:
        add("F08", "MEDIA", None, f"Trae «pinData» (datos de prueba guardados) en {len(pin)} nodo(s). Pueden tener datos de personas: bórralos antes de compartir (ALTA si el repo es público).")
    # F09 certificados y http
    for n in nodos:
        p = n.get("parameters") or {}
        if "httprequest" in tipo(n):
            if (p.get("options") or {}).get("allowUnauthorizedCerts"):
                add("F09", "MEDIA", nombre(n), "Acepta certificados no válidos (allowUnauthorizedCerts). Desactívalo.")
            url = p.get("url")
            if isinstance(url, str) and re.match(r"^=?\s*http://(?!localhost|127\.0\.0\.1)", url, re.I):
                add("F09", "MEDIA", nombre(n), "Llama a una dirección http:// sin cifrar. Usa https://.")
    # F10 correos y teléfonos escritos
    for n in nodos:
        txt_total = " ".join(t for _, t in recorrer(n.get("parameters", {})) if not es_expresion(t))
        if CORREO.search(txt_total) or TELEFONO.search(txt_total):
            add("F10", "MEDIA", nombre(n), "Hay un correo o teléfono escrito en el nodo (¿de una persona real?). Si el repo es público, cámbialo por uno inventado.")
    # F11 exportado encendido y nodos apagados
    if wf.get("active") is True:
        add("F11", "BAJA", None, "El flujo está exportado como activo: al importarlo se enciende solo. Desactívalo hasta revisarlo.")
    apagados = [n for n in nodos if n.get("disabled")]
    if apagados:
        add("F11", "BAJA", None, f"{len(apagados)} nodo(s) apagados: bórralos si ya no sirven.")
    # F12-F14 subidas a YouTube: privadas primero, «para niños» declarado, y público solo tras aprobación
    revisar_youtube(wf, activos, tipo, nombre, add)
    return h


def _campos_youtube(n):
    """Da (operación, campos) del nodo YouTube de video: «options» al subir, «updateFields» al actualizar."""
    p = n.get("parameters") or {}
    if str(p.get("resource", "video")).lower() != "video":
        return None, {}
    op = str(p.get("operation", "")).lower()
    clave = "options" if op == "upload" else "updateFields"
    campos = p.get(clave)
    return op, campos if isinstance(campos, dict) else {}


def _pasa_por_aprobacion(wf, activos, destino):
    """True si `destino` solo se alcanza después de una aprobación: hay camino desde un nodo «sendAndWait» (pedir aprobación)
    hasta él pasando por un IF/Switch/Filter, y NO hay ningún camino desde un disparador que llegue sin pasar por la aprobación.
    Mira la forma del flujo, no lo que compara el IF: eso hay que leerlo a mano."""
    por_nombre = {n.get("name"): n for n in activos}
    siguientes, con_entrada = {}, set()
    for origen, salidas in (wf.get("connections") or {}).items():
        for rama in (salidas or {}).get("main", []) or []:
            for c in rama or []:
                if isinstance(c, dict):
                    siguientes.setdefault(origen, set()).add(c.get("node"))
                    con_entrada.add(c.get("node"))
    condicional = lambda n: any(k in str(n.get("type", "")).lower() for k in (".if", "switch", "filter"))  # noqa: E731
    esperas = {n.get("name") for n in activos if str((n.get("parameters") or {}).get("operation", "")).lower() == "sendandwait"}

    # 1) desde la aprobación, pasando por un IF, se llega al destino
    pila = [(e, False) for e in esperas]
    vistos, llega = set(pila), False
    while pila and not llega:
        actual, paso = pila.pop()
        if actual == destino and paso:
            llega = True
        for s in siguientes.get(actual, ()):
            if s in por_nombre:
                e = (s, paso or condicional(por_nombre[s]))
                if e not in vistos:
                    vistos.add(e)
                    pila.append(e)
    if not llega:
        return False

    # 2) sin los nodos de aprobación, ningún disparador (nodo sin entradas) alcanza el destino
    pila = [n.get("name") for n in activos if n.get("name") not in con_entrada and n.get("name") not in esperas]
    vistos = set(pila)
    while pila:
        actual = pila.pop()
        if actual == destino:
            return False
        for s in siguientes.get(actual, ()):
            if s in por_nombre and s not in esperas and s not in vistos:
                vistos.add(s)
                pila.append(s)
    return True


def revisar_youtube(wf, activos, tipo, nombre, add):
    for n in activos:
        if not tipo(n).endswith(".youtube"):
            continue
        op, campos = _campos_youtube(n)
        if op not in ("upload", "update"):
            continue
        priv = campos.get("privacyStatus")
        if op == "upload":
            if not priv:
                add("F12", "ALTA", nombre(n), "Sube un video sin fijar «privacyStatus»: puede quedar público. Pon «private» y publica después de aprobar.")
            elif isinstance(priv, str) and es_expresion(priv):
                add("F12", "MEDIA", nombre(n), "La privacidad de la subida sale de una expresión. Déjala fija en «private».")
            elif priv == "public":
                add("F12", "ALTA", nombre(n), "Sube el video directamente en público. Sube en «private» y publica solo tras la aprobación.")
            elif priv != "private":
                add("F12", "MEDIA", nombre(n), "Sube el video como «no listado» (lo ve quien tenga el enlace). Mejor «private».")
        if "selfDeclaredMadeForKids" not in campos and (op == "upload" or priv == "public"):
            add("F13", "MEDIA", nombre(n),
                "No declara «selfDeclaredMadeForKids». YouTube pide decir si el video es para niños; si no lo mandas, queda lo que diga el canal. Decláralo fijo en el nodo.")
        if priv == "public" and not _pasa_por_aprobacion(wf, activos, n.get("name")):
            add("F14", "ALTA", nombre(n),
                "Hace público un video sin que antes haya una aprobación (nodo «sendAndWait» + IF) en su camino. Nada debe publicarse solo.")


def cargar(ruta):
    p = Path(ruta)
    if not p.is_file():
        raise ValueError(f"no encuentro el archivo: {ruta}")
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("el archivo pesa más de 20 MB: no parece un flujo de n8n")
    try:
        datos = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"el archivo no es un JSON válido ({e.__class__.__name__})")
    if isinstance(datos, list):
        datos = next((d for d in datos if isinstance(d, dict) and "nodes" in d), None)
    if not isinstance(datos, dict):
        raise ValueError("no parece un flujo de n8n")
    return datos


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    como_json = "--json" in argv
    if len(args) != 1:
        print(__doc__.strip().splitlines()[0] + "\nUso: python -I revisar_flujo.py FLUJO.json [--json]", file=sys.stderr)
        return 2
    try:
        hallazgos = revisar_flujo(cargar(args[0]))
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    hallazgos.sort(key=lambda x: (orden[x["gravedad"]], x["id"]))
    if como_json:
        print(json.dumps(hallazgos, ensure_ascii=False, indent=2))
    else:
        if not hallazgos:
            print("Sin hallazgos. (Esto no prueba que el flujo sea seguro: solo busca patrones conocidos.)")
        for x in hallazgos:
            print(f"[{x['gravedad']}] {x['id']} · {x['nodo']}: {x['texto']}")
        altas = sum(1 for x in hallazgos if x["gravedad"] == "ALTA")
        print(f"\n{len(hallazgos)} hallazgo(s), {altas} grave(s).")
    return 1 if any(x["gravedad"] == "ALTA" for x in hallazgos) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
