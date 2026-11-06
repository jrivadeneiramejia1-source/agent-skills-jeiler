#!/usr/bin/env python3
"""Revisa el código de un bot de Telegram o WhatsApp (Worker de Cloudflare, Node o Python).

Uso:   python -I revisar_bot.py CARPETA_O_ARCHIVO [--json]
Salida: 0 = sin hallazgos graves, 1 = hay hallazgos ALTA, 2 = no se pudo leer.

Solo lee archivos de texto: no abre redes ni ejecuta el código revisado, y NUNCA imprime el
valor de una clave (solo el archivo y el tipo). Busca patrones de texto; que salga limpio NO
prueba que el bot sea seguro (por ejemplo, no puede saber si la comparación es correcta).
"""
import json
import os
import re
import sys
from pathlib import Path

EXT = {".ts", ".js", ".mjs", ".cjs", ".py", ".toml", ".json", ".jsonc", ".yml", ".yaml"}
SALTAR = {"node_modules", ".git", ".wrangler", "dist", "build", "__pycache__", ".venv", "venv"}
MAX_ARCHIVO, MAX_ARCHIVOS = 1_000_000, 2000

CLAVES = [
    ("token de bot de Telegram", re.compile(r"(?<!\d)\d{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])")),
    ("clave tipo sk-...", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("clave de Google (AIza...)", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("token de GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("llave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token de acceso de Meta (EAA...)", re.compile(r"\bEAA[A-Za-z0-9]{40,}")),
]
VAR_SECRETA = re.compile(r"(?im)^\s*([A-Z0-9_]*(?:TOKEN|SECRET|KEY|PASSWORD|CLAVE)[A-Z0-9_]*)\s*=\s*[\"']([^\"']{6,})[\"']")
TELEGRAM = re.compile(r"(?i)(grammy|telegraf|api\.telegram\.org|node-telegram-bot-api|python-telegram-bot|aiogram|telegram_bot|BOT_TOKEN)")
WHATSAPP = re.compile(r"(?i)(graph\.facebook\.com|hub\.verify_token|hub\.challenge|whatsapp_business_account|x-hub-signature)")
SECRET_TOKEN = re.compile(r"(?i)(secrettoken|secret_token|x-telegram-bot-api-secret-token)")
LISTA = re.compile(r"(?i)(from\??\.id|chat\??\.id|usuarios_permitidos|allowed_?(users|ids)|allowlist|permitidos|authorized)")
FIRMA = re.compile(r"(?i)x-hub-signature-256")
COMPARA_SEGURA = re.compile(r"(timingSafeEqual|compare_digest|crypto\.subtle\.verify|constantTimeEqual|timing_safe)")
VERIFY = re.compile(r"(?i)hub\.verify_token")
CHALLENGE = re.compile(r"(?i)hub\.challenge")
DEDUP = re.compile(r"(?i)(update_id|messages\[0\]\.id|message_id|idempot|dedup|\.put\(|INSERT\s+OR\s+IGNORE)")
LOG_CUERPO = re.compile(r"(?i)(console\.log\(\s*(JSON\.stringify\()?\s*(await\s+)?(request\.(text|json)\(\)|(\w+\.)*(body|update|payload))\b|print\(\s*(\w+\.)*(request|update|body|payload)\b)")
EJECUTA = re.compile(r"(child_process|\beval\s*\(|new\s+Function\s*\(|os\.system\(|shell\s*=\s*True|subprocess\.)")


def sin_comentarios(rel, t):
    """Quita comentarios para que una palabra dentro de un comentario no engañe a la búsqueda."""
    if rel.endswith((".ts", ".js", ".mjs", ".cjs", ".jsonc")):
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        t = re.sub(r"(?<![:\"'])//[^\n]*", "", t)
    elif rel.endswith((".py", ".toml", ".yml", ".yaml")):
        t = re.sub(r"(?m)^\s*#.*$", "", t)
        t = re.sub(r"(?<=\s)#[^\n\"']*$", "", t, flags=re.M)
    return t


def listar(raiz):
    p = Path(raiz)
    if p.is_file():
        return [p]
    if not p.is_dir():
        raise ValueError(f"no encuentro: {raiz}")
    salida = []
    for dirpath, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d not in SALTAR]
        for f in files:
            q = Path(dirpath) / f
            if q.suffix.lower() in EXT or f.startswith(".env") or f == ".dev.vars":
                salida.append(q)
            if len(salida) >= MAX_ARCHIVOS:
                return salida
    return salida


def revisar(raiz):
    archivos = listar(raiz)
    if not archivos:
        raise ValueError("no encontré archivos de código para revisar")
    base = Path(raiz) if Path(raiz).is_dir() else Path(raiz).parent
    h = []
    textos = {}
    for a in archivos:
        rel = str(a.relative_to(base)) if base in a.parents or a.parent == base else a.name
        if a.stat().st_size > MAX_ARCHIVO:
            continue
        try:
            textos[rel] = a.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

    def add(id_, grav, donde, texto):
        h.append({"id": id_, "gravedad": grav, "donde": donde, "texto": texto})

    # B01 claves escritas en archivos
    for rel, t in textos.items():
        es_ejemplo = rel.endswith((".example", ".sample")) or "ejemplo" in rel.lower()
        vistos = set()
        for etiqueta, rx in CLAVES:
            if rx.search(t) and etiqueta not in vistos:
                vistos.add(etiqueta)
                add("B01", "ALTA", rel, f"Parece haber un {etiqueta} escrito en el archivo. Guárdalo como secreto (wrangler secret put) y cambia el que quedó expuesto.")
        if rel.endswith(".toml") or rel.endswith((".jsonc", ".json")):
            for m in VAR_SECRETA.finditer(t):
                add("B02", "ALTA", rel, f"La variable {m.group(1)} tiene un valor escrito en un archivo de configuración. Las variables normales se ven en texto: usa un secreto.")
        base_nombre = os.path.basename(rel)
        if base_nombre.startswith(".env") or base_nombre == ".dev.vars":
            if not es_ejemplo:
                add("B03", "MEDIA", rel, "Archivo de variables locales dentro del proyecto: confirma que está en .gitignore y que no se sube.")
    gi = Path(base) / ".gitignore"
    ignorados = gi.read_text(encoding="utf-8", errors="replace") if gi.is_file() else ""
    for rel in textos:
        nb = os.path.basename(rel)
        if (nb.startswith(".env") or nb == ".dev.vars") and not rel.endswith((".example", ".sample")):
            if not re.search(r"(?m)^\s*(\.env|\.dev\.vars|\*\.env)", ignorados):
                add("B03", "ALTA", rel, "Está en el proyecto y .gitignore no lo ignora (o no hay .gitignore): se subiría a GitHub con las claves.")

    codigo = {r: sin_comentarios(r, t) for r, t in textos.items() if r.endswith((".ts", ".js", ".mjs", ".cjs", ".py"))}
    todo = "\n".join(codigo.values())
    cfg = "\n".join(sin_comentarios(r, t) for r, t in textos.items() if r.endswith((".toml", ".json", ".jsonc", ".yml", ".yaml")))
    alltxt = todo + "\n" + cfg
    es_tg = bool(TELEGRAM.search(todo))
    es_wa = bool(WHATSAPP.search(todo))
    if not es_tg and not es_wa:
        add("B00", "BAJA", "(proyecto)", "No reconozco un bot de Telegram ni de WhatsApp en estos archivos; solo se revisaron claves.")
    if es_tg:
        if not SECRET_TOKEN.search(alltxt):
            add("B10", "ALTA", "Telegram", "No veo `secret_token` (webhookCallback con secretToken o el encabezado X-Telegram-Bot-Api-Secret-Token): cualquiera que conozca la URL puede enviarle mensajes falsos.")
        if not LISTA.search(todo):
            add("B11", "ALTA", "Telegram", "No veo una lista de usuarios permitidos (from.id): el bot respondería a cualquiera.")
    if es_wa:
        if not FIRMA.search(todo):
            add("B20", "ALTA", "WhatsApp", "No veo la comprobación de la firma X-Hub-Signature-256: cualquiera podría enviar eventos falsos al webhook.")
        elif not COMPARA_SEGURA.search(todo):
            add("B21", "MEDIA", "WhatsApp", "Hay firma, pero no veo una comparación de tiempo constante (timingSafeEqual, compare_digest o crypto.subtle.verify). Evita comparar con == o ===.")
        if CHALLENGE.search(todo) and not VERIFY.search(todo):
            add("B22", "MEDIA", "WhatsApp", "Responde hub.challenge sin comprobar hub.verify_token.")
        if not LISTA.search(todo):
            add("B23", "MEDIA", "WhatsApp", "No veo una lista de números permitidos: si el bot hace algo más que atender pedidos, limita quién puede darle órdenes.")
    if (es_tg or es_wa) and not DEDUP.search(todo):
        add("B30", "BAJA", "(proyecto)", "No veo protección contra mensajes repetidos (update_id / id del mensaje). Si el bot falla, Telegram y WhatsApp reintentan y el mensaje puede procesarse dos veces.")
    for rel, t in codigo.items():
        if LOG_CUERPO.search(t):
            add("B31", "MEDIA", rel, "Escribe en el registro el mensaje completo que llega: guarda datos de personas. Registra solo lo necesario.")
        if EJECUTA.search(t):
            add("B32", "MEDIA", rel, "Usa eval, exec o subprocess: confirma que nunca recibe texto del chat sin validarlo contra una lista cerrada.")
    return h


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print("Uso: python -I revisar_bot.py CARPETA_O_ARCHIVO [--json]", file=sys.stderr)
        return 2
    try:
        hallazgos = revisar(args[0])
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    hallazgos.sort(key=lambda x: (orden[x["gravedad"]], x["id"]))
    if "--json" in argv:
        print(json.dumps(hallazgos, ensure_ascii=False, indent=2))
    else:
        if not hallazgos:
            print("Sin hallazgos. (No prueba que el bot sea seguro: solo busca patrones conocidos.)")
        for x in hallazgos:
            print(f"[{x['gravedad']}] {x['id']} · {x['donde']}: {x['texto']}")
        print(f"\n{len(hallazgos)} hallazgo(s), {sum(1 for x in hallazgos if x['gravedad'] == 'ALTA')} grave(s).")
    return 1 if any(x["gravedad"] == "ALTA" for x in hallazgos) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
