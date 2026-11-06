#!/usr/bin/env python3
"""Genera las plantillas de n8n (plantillas/*.json) a partir del código de codigo/*.js.

Uso (desde la carpeta de la skill):  python -I scripts/generar_plantillas.py [--comprobar]
Sin opciones escribe los archivos. Con --comprobar NO escribe: avisa (salida 1) si alguna plantilla guardada
no coincide con lo que saldría de codigo/*.js. Así el código que se prueba es exactamente el que se entrega.
"""
import json
import sys
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
NS = uuid.UUID("6f0b6d52-0000-4000-8000-0000a6e17000")


def uid(nombre):
    return str(uuid.uuid5(NS, nombre))


def codigo(nombre):
    return (AQUI / "codigo" / nombre).read_text(encoding="utf-8")


CRED_CLAVE = {"httpQueryAuth": {"id": "REEMPLAZAR-CLAVE-YOUTUBE", "name": "Clave de la API de YouTube"}}
CRED_TG = {"telegramApi": {"id": "REEMPLAZAR-TELEGRAM", "name": "Telegram (mi bot)"}}
CRED_YT = {"youTubeOAuth2Api": {"id": "REEMPLAZAR-YOUTUBE", "name": "YouTube (mi canal)"}}


class Flujo:
    def __init__(self, nombre):
        self.nombre, self.nodos, self.con = nombre, [], {}

    def nodo(self, nombre, tipo, version, params, pos, **extra):
        n = {"id": uid(self.nombre + "/" + nombre), "name": nombre, "type": tipo, "typeVersion": version,
             "position": list(pos), "parameters": params}
        n.update(extra)
        self.nodos.append(n)
        return nombre

    def unir(self, a, b, salida=0):
        lista = self.con.setdefault(a, {"main": []})["main"]
        while len(lista) <= salida:
            lista.append([])
        lista[salida].append({"node": b, "type": "main", "index": 0})

    def json(self, **extra):
        d = {"name": self.nombre, "nodes": self.nodos, "connections": self.con, "active": False,
             "settings": {"executionOrder": "v1"}}
        d.update(extra)
        return d


def code(f, nombre, archivo, pos, **extra):
    return f.nodo(nombre, "n8n-nodes-base.code", 2, {"jsCode": codigo(archivo)}, pos, **extra)


def telegram_msg(f, nombre, chat, texto, pos, html=False, **extra):
    campos = {"appendAttribution": False}
    if html:
        campos.update({"parse_mode": "HTML", "disable_web_page_preview": True})
    return f.nodo(nombre, "n8n-nodes-base.telegram", 1.2,
                  {"resource": "message", "operation": "sendMessage", "chatId": chat, "text": texto, "additionalFields": campos},
                  pos, credentials=CRED_TG, **extra)


def si(f, nombre, izquierda, pos):
    return f.nodo(nombre, "n8n-nodes-base.if", 2.2, {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{"id": uid(f.nombre + "/" + nombre + "/cond"), "leftValue": izquierda, "rightValue": "",
                            "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
            "combinator": "and"},
        "options": {}}, pos)


def nota(f, nombre, texto, pos, ancho=460, alto=300):
    return f.nodo(nombre, "n8n-nodes-base.stickyNote", 1, {"content": texto, "height": alto, "width": ancho}, pos)


def http(f, nombre, url, consultas, pos):
    params = [{"name": k, "value": v} for k, v in consultas]
    return f.nodo(nombre, "n8n-nodes-base.httpRequest", 4.2, {
        "url": url, "authentication": "genericCredentialType", "genericAuthType": "httpQueryAuth",
        "sendQuery": True, "queryParameters": {"parameters": params}, "options": {"timeout": 30000}},
        pos, credentials=CRED_CLAVE, onError="continueRegularOutput")


# ------------------------------------------------------------------ A) Investigador de virales
def investigador():
    f = Flujo("Investigador de videos infantiles virales (YouTube)")
    nota(f, "Léeme", "## Investigador de virales\nTodos los días a las 8 busca videos infantiles en español de los últimos 3, 7 y 30 días y te manda por Telegram "
         "los que más superaron el promedio de su canal.\n\n**Antes de activarlo:**\n1. Credencial «Clave de la API de YouTube» (Header/Query Auth: nombre `key`).\n"
         "2. Credencial de Telegram.\n3. Edita tu número de chat en el nodo «Configuración».\n4. Prueba con «Probar a mano».\n\n"
         "Usa el resultado para aprender la fórmula; **no copies** personajes, guiones, imágenes ni música.", (-420, -40), 440, 330)
    prog = f.nodo("Cada día a las 8", "n8n-nodes-base.scheduleTrigger", 1.2,
                  {"rule": {"interval": [{"field": "days", "daysInterval": 1, "triggerAtHour": 8}]}}, (0, 0))
    mano = f.nodo("Probar a mano", "n8n-nodes-base.manualTrigger", 1, {}, (0, 200))
    conf = code(f, "Configuración", "configuracion.js", (260, 100))
    busca = http(f, "Buscar videos", "https://www.googleapis.com/youtube/v3/search", [
        ("part", "snippet"), ("type", "video"), ("q", "={{ $json.q }}"), ("publishedAfter", "={{ $json.publishedAfter }}"),
        ("order", "viewCount"), ("maxResults", "={{ $json.maxResults }}"), ("relevanceLanguage", "es"), ("safeSearch", "strict")], (520, 100))
    lv = code(f, "Armar lotes de videos", "lotes_videos.js", (780, 100))
    est = http(f, "Estadísticas de videos", "https://www.googleapis.com/youtube/v3/videos", [
        ("part", "snippet,statistics,contentDetails"), ("id", "={{ $json.ids }}")], (1040, 100))
    lc = code(f, "Armar lotes de canales", "lotes_canales.js", (1300, 100))
    can = http(f, "Datos de canales", "https://www.googleapis.com/youtube/v3/channels", [
        ("part", "snippet,statistics"), ("id", "={{ $json.ids }}")], (1560, 100))
    calc = code(f, "Calcular virales", "calcular_virales.js", (1820, 100))
    env = telegram_msg(f, "Enviar por Telegram", "={{ $json.chatId }}", "={{ $json.texto }}", (2080, 100), html=True,
                       onError="continueRegularOutput")
    for a, b in [(prog, conf), (mano, conf), (conf, busca), (busca, lv), (lv, est), (est, lc), (lc, can), (can, calc), (calc, env)]:
        f.unir(a, b)
    return f.json()


# ------------------------------------------------------------------ B) Subidor con aprobación
def subidor():
    f = Flujo("Subir a YouTube con aprobación (privado primero)")
    gate_n = "Solo tu chat y /subir N"
    chat = "={{ $('%s').first().json.chatId }}" % gate_n
    nota(f, "Léeme", "## Subidor con aprobación\nEscribes **/subir 1**, **/subir 2** o **/subir 3** a tu bot de Telegram. Lee `publicacion.json` y `video.mp4` de esa carpeta, "
         "lo sube a YouTube **en privado y marcado «para niños»** (fijo en el código) y te pregunta si lo publica. Solo se hace público si pulsas «Publicar».\n\n"
         "**Antes de activarlo:**\n1. Credenciales de Telegram y de YouTube (OAuth).\n2. Edita tu número de chat y la carpeta SOLO en el nodo «%s» (en ningún otro lado).\n"
         "3. Pon n8n detrás de ngrok con `N8N_WEBHOOK_URL`.\n4. Las carpetas 1, 2 y 3 deben estar dentro de `~/.n8n-files` (n8n 2.x).\n"
         "5. Elige el flujo de errores en Settings → Error workflow." % gate_n, (-440, -80), 470, 420)
    tr = f.nodo("Telegram Trigger", "n8n-nodes-base.telegramTrigger", 1.2, {"updates": ["message"], "additionalFields": {}}, (0, 0),
                credentials=CRED_TG, webhookId=uid("subir/telegram-trigger"))
    gate = code(f, gate_n, "gate_subir.js", (260, 0))
    ped = si(f, "¿Pedido válido?", "={{ $json.valido }}", (520, 0))
    problema = telegram_msg(f, "Avisar problema", chat,
                            "={{ $json.respuesta || ('No pude completar el pedido: ' + ($json.error && $json.error.message ? $json.error.message : ($json.error || 'error desconocido'))) }}",
                            (1560, 360))
    leer_meta = f.nodo("Leer datos", "n8n-nodes-base.readWriteFile", 1,
                       {"operation": "read", "fileSelector": "={{ $json.rutaMeta }}", "options": {"dataPropertyName": "meta"}}, (780, -40),
                       onError="continueErrorOutput")
    val = code(f, "Validar datos", "validar_datos.js", (1040, -80))
    dat = si(f, "¿Datos válidos?", "={{ $json.ok }}", (1300, -80))
    leer_vid = f.nodo("Leer video", "n8n-nodes-base.readWriteFile", 1,
                      {"operation": "read", "fileSelector": "={{ $('%s').first().json.rutaVideo }}" % gate_n, "options": {"dataPropertyName": "video"}},
                      (1560, -120), onError="continueErrorOutput")
    d = "$('Validar datos').first().json"
    subir = f.nodo("Subir a YouTube (privado)", "n8n-nodes-base.youTube", 1, {
        "resource": "video", "operation": "upload", "title": "={{ %s.titulo }}" % d, "regionCode": "CO", "categoryId": "={{ %s.categoria }}" % d,
        "binaryProperty": "video",
        "options": {"description": "={{ %s.descripcion }}" % d, "tags": "={{ %s.etiquetas }}" % d, "defaultLanguage": "={{ %s.idioma }}" % d,
                    "privacyStatus": "private", "selfDeclaredMadeForKids": True, "notifySubscribers": False}},
        (1820, -160), credentials=CRED_YT, onError="continueErrorOutput")
    aprob = f.nodo("Pedir aprobación", "n8n-nodes-base.telegram", 1.2, {
        "resource": "message", "operation": "sendAndWait", "chatId": chat,
        "message": "={{ 'Subí «' + %s.titulo + '» como PRIVADO.\\nRevísalo aquí: https://youtu.be/' + $json.uploadId + '\\n\\n¿Lo publico?' }}" % d,
        "responseType": "approval",
        "approvalOptions": {"values": {"approvalType": "double", "approveLabel": "✅ Publicar", "disapproveLabel": "❌ Dejar privado"}},
        "options": {"limitWaitTime": {"values": {"limitType": "afterTimeInterval", "resumeAmount": 24, "resumeUnit": "hours"}}}},
        (2080, -160), credentials=CRED_TG, webhookId=uid("subir/aprobacion"))
    aprobo = si(f, "¿Aprobó?", "={{ !!($json.data && $json.data.approved === true) }}", (2340, -160))
    pub = f.nodo("Publicar (hacer público)", "n8n-nodes-base.youTube", 1, {
        "resource": "video", "operation": "update", "videoId": "={{ $('Subir a YouTube (privado)').first().json.uploadId }}",
        "title": "={{ %s.titulo }}" % d, "regionCode": "CO", "categoryId": "={{ %s.categoria }}" % d,
        "updateFields": {"privacyStatus": "public", "description": "={{ %s.descripcion }}" % d, "tags": "={{ %s.etiquetas }}" % d,
                         "defaultLanguage": "={{ %s.idioma }}" % d, "selfDeclaredMadeForKids": True}},
        (2600, -240), credentials=CRED_YT, onError="continueErrorOutput")
    ok_pub = telegram_msg(f, "Avisar publicado", chat, "={{ '✅ Publicado: https://youtu.be/' + $('Subir a YouTube (privado)').first().json.uploadId }}", (2860, -280))
    queda = telegram_msg(f, "Avisar que queda privado", chat,
                         "={{ 'Queda en PRIVADO: https://youtu.be/' + $('Subir a YouTube (privado)').first().json.uploadId + ' (puedes publicarlo tú desde YouTube Studio).' }}",
                         (2600, -60))
    for a, b, s in [(tr, gate, 0), (gate, ped, 0), (ped, leer_meta, 0), (ped, problema, 1), (leer_meta, val, 0), (leer_meta, problema, 1),
                    (val, dat, 0), (dat, leer_vid, 0), (dat, problema, 1), (leer_vid, subir, 0), (leer_vid, problema, 1),
                    (subir, aprob, 0), (subir, problema, 1), (aprob, aprobo, 0), (aprobo, pub, 0), (aprobo, queda, 1),
                    (pub, ok_pub, 0), (pub, problema, 1)]:
        f.unir(a, b, s)
    return f.json()


# ------------------------------------------------------------------ C) Aviso de errores
def avisar_error():
    f = Flujo("Avisar por Telegram cuando falla un flujo")
    nota(f, "Léeme", "## Aviso de errores\nElígelo como **Error workflow** (Settings → Error workflow) en el flujo investigador y en el subidor. "
         "Cuando uno falle te llega un Telegram. Edita tu chat en el nodo «Mensaje de error».", (-420, -40), 420, 220)
    et = f.nodo("Error Trigger", "n8n-nodes-base.errorTrigger", 1, {}, (0, 0))
    msj = code(f, "Mensaje de error", "mensaje_error.js", (260, 0))
    env = telegram_msg(f, "Enviar aviso", "={{ $json.chatId }}", "={{ $json.texto }}", (520, 0), html=True)
    f.unir(et, msj)
    f.unir(msj, env)
    return f.json()


PLANTILLAS = {"investigador-virales.json": investigador, "subir-youtube.json": subidor, "avisar-error.json": avisar_error}


def main(argv):
    comprobar = "--comprobar" in argv
    mal = 0
    for archivo, fabrica in PLANTILLAS.items():
        destino = AQUI / "plantillas" / archivo
        texto = json.dumps(fabrica(), ensure_ascii=False, indent=2) + "\n"
        if comprobar:
            if not destino.is_file() or destino.read_text(encoding="utf-8") != texto:
                print(f"DIFERENTE: {archivo} no coincide con codigo/*.js (corre generar_plantillas.py)")
                mal += 1
        else:
            destino.write_text(texto, encoding="utf-8")
            print("escrito", archivo)
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
