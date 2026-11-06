#!/usr/bin/env python3
"""Prueba un bot YA CORRIENDO mandándole mensajes falsos, para ver si rechaza lo que debe rechazar.

Uso:
  python -I probar_webhook.py telegram URL --secreto CLAVE --permitido 111111111 [--ajeno 222222222]
  python -I probar_webhook.py whatsapp URL --app-secret CLAVE --verify-token PALABRA --permitido 570000000000 [--ajeno 570000000001]
Las claves y los números son de PRUEBA (inventados): úsalas con el bot corriendo en tu computador (por ejemplo
`wrangler dev`) y nunca con las claves reales. Por seguridad solo acepta direcciones locales (localhost / 127.0.0.1 / ::1);
para probar un bot tuyo ya publicado, agrega --permitir-remoto (solo bots que son tuyos).
Salida: 0 = todo PASA, 1 = algo FALLA, 2 = no se pudo probar (no responde, argumentos mal).
Solo biblioteca estándar de Python. Lo que no se puede ver desde afuera (si el bot contestó o no) se marca INFO.
"""
import hashlib
import hmac
import json
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlencode

LOCALES = {"localhost", "127.0.0.1", "::1"}
RES = []


def llamar(url, metodo="POST", cuerpo=None, cabeceras=None, timeout=20):
    """Devuelve (código, texto). Un 4xx/5xx también es una respuesta, no un error."""
    datos = cuerpo if isinstance(cuerpo, (bytes, type(None))) else cuerpo.encode()
    req = urllib.request.Request(url, data=datos, method=metodo, headers=cabeceras or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(2000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(2000).decode("utf-8", "replace")


def chk(nombre, ok, detalle=""):
    RES.append(ok)
    print(("PASA " if ok else "FALLA") + " | " + nombre + (" | " + detalle if detalle else ""))


def info(nombre, detalle):
    print("INFO  | " + nombre + " | " + detalle)


def rechaza(codigo):
    return codigo in (401, 403, 404, 405)


def telegram(url, secreto, permitido, ajeno):
    J = {"content-type": "application/json"}

    def upd(uid, usuario, n):
        return json.dumps({"update_id": n, "message": {"message_id": n, "date": 1, "chat": {"id": usuario, "type": "private"},
                                                       "from": {"id": usuario, "is_bot": False, "first_name": "Prueba"}, "text": "hola"}})
    c, _ = llamar(url, cuerpo=upd(0, permitido, 9001), cabeceras=J)
    chk("T1. sin la clave secreta (secret_token) rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, cuerpo=upd(0, permitido, 9002), cabeceras={**J, "X-Telegram-Bot-Api-Secret-Token": secreto + "x"})
    chk("T2. con una clave equivocada rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, metodo="GET")
    chk("T3. un GET (sin clave) rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    ok_h = {**J, "X-Telegram-Bot-Api-Secret-Token": secreto}
    c, cuerpo = llamar(url, cuerpo=upd(0, ajeno, 9003), cabeceras=ok_h)
    chk("T4. usuario que NO está en la lista: 200 y sin respuesta", c == 200 and '"method"' not in cuerpo and "sendMessage" not in cuerpo, f"respondió {c}")
    c, _ = llamar(url, cuerpo=upd(0, permitido, 9004), cabeceras=ok_h)
    chk("T5. usuario permitido: no devuelve error 5xx (un 5xx hace que Telegram reintente)", c < 500, f"respondió {c}")
    c, _ = llamar(url, cuerpo="{ esto no es json", cabeceras=ok_h)
    chk("T6. un cuerpo roto no produce error 5xx", c < 500, f"respondió {c}")
    c, _ = llamar(url, cuerpo=b"x" * 1_500_000, cabeceras=ok_h)
    chk("T7. un cuerpo enorme (1,5 MB) no produce error 5xx", c < 500, f"respondió {c}")
    info("Alcance", "No se ve desde afuera si el bot realmente contestó al permitido; ni la lista de IP de Telegram ni el reintento real.")


def firma(app_secret, cuerpo):
    return "sha256=" + hmac.new(app_secret.encode(), cuerpo if isinstance(cuerpo, bytes) else cuerpo.encode(), hashlib.sha256).hexdigest()


def whatsapp(url, app_secret, verify_token, permitido, ajeno):
    J = {"content-type": "application/json"}
    def evento(numero, mid):
        return json.dumps({"object": "whatsapp_business_account", "entry": [{"id": "1", "changes": [{"field": "messages", "value": {
            "messages": [{"from": numero, "id": mid, "type": "text", "text": {"body": "hola"}}]}}]}]})
    q = lambda **k: url.rstrip("/") + "/?" + urlencode(k)  # noqa: E731
    c, cuerpo = llamar(q(**{"hub.mode": "subscribe", "hub.verify_token": verify_token, "hub.challenge": "RETO12345"}), metodo="GET")
    chk("W1. verificación con la palabra correcta: 200 y devuelve el reto", c == 200 and cuerpo.strip() == "RETO12345", f"respondió {c}")
    c, cuerpo = llamar(q(**{"hub.mode": "subscribe", "hub.verify_token": verify_token + "x", "hub.challenge": "RETO12345"}), metodo="GET")
    chk("W2. verificación con una palabra equivocada: no devuelve el reto", c != 200 and "RETO12345" not in cuerpo, f"respondió {c}")
    c, cuerpo = llamar(q(**{"hub.challenge": "RETO12345"}), metodo="GET")
    chk("W3. sin hub.mode ni hub.verify_token: no devuelve el reto", c != 200 and "RETO12345" not in cuerpo, f"respondió {c}")
    ev = evento(permitido, "wamid.A1")
    c, _ = llamar(url, cuerpo=ev, cabeceras=J)
    chk("W4. evento SIN firma X-Hub-Signature-256: rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, cuerpo=ev, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret + "x", ev)})
    chk("W5. evento con firma de otro secreto: rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, cuerpo=ev, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret, ev + " ")})
    chk("W6. firma válida pero cuerpo alterado: rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, cuerpo=ev, cabeceras={**J, "X-Hub-Signature-256": "sha256=zz"})
    chk("W7. firma mal formada: rechaza", rechaza(c), f"respondió {c}" + ("" if rechaza(c) else ", pero debía rechazarlo (401/403)"))
    c, _ = llamar(url, cuerpo=ev, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret, ev)})
    chk("W8. evento bien firmado de un número permitido: 200", c == 200, f"respondió {c}")
    ev2 = evento(ajeno, "wamid.B1")
    c, _ = llamar(url, cuerpo=ev2, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret, ev2)})
    chk("W9. evento bien firmado de un número que no está en la lista: 200 (no 5xx)", c == 200, f"respondió {c}")
    c, _ = llamar(url, cuerpo=ev, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret, ev)})
    chk("W10. el mismo evento otra vez (reintento de Meta): sigue dando 200", c == 200, f"respondió {c}")
    roto = "{ roto"
    c, _ = llamar(url, cuerpo=roto, cabeceras={**J, "X-Hub-Signature-256": firma(app_secret, roto)})
    chk("W11. cuerpo roto pero bien firmado: no produce error 5xx", c < 500, f"respondió {c}")
    info("Alcance", "No se ve desde afuera si el bot contestó o procesó el pedido, ni si el reintento se detecta como repetido.")


def main(argv):
    a = argv[1:]
    if len(a) < 2 or a[0] not in ("telegram", "whatsapp"):
        print(__doc__.strip().split("\n\n")[1] if "\n\n" in __doc__ else "Uso: python -I probar_webhook.py telegram|whatsapp URL ...", file=sys.stderr)
        return 2
    modo, url = a[0], a[1]
    opt = {}
    i = 2
    while i < len(a):
        if a[i] == "--permitir-remoto":
            opt["remoto"] = True; i += 1
        elif a[i].startswith("--") and i + 1 < len(a):
            opt[a[i][2:]] = a[i + 1]; i += 2
        else:
            print(f"ERROR: argumento no entendido: {a[i]}", file=sys.stderr); return 2
    host = urlparse(url).hostname or ""
    if host not in LOCALES and not opt.get("remoto"):
        print("ERROR: por seguridad solo pruebo direcciones locales (localhost / 127.0.0.1). Para un bot tuyo ya publicado, agrega --permitir-remoto.", file=sys.stderr)
        return 2
    try:
        if modo == "telegram":
            if not all(k in opt for k in ("secreto", "permitido")):
                print("ERROR: faltan --secreto y --permitido", file=sys.stderr); return 2
            telegram(url, opt["secreto"], int(opt["permitido"]), int(opt.get("ajeno", int(opt["permitido"]) + 1)))
        else:
            if not all(k in opt for k in ("app-secret", "verify-token", "permitido")):
                print("ERROR: faltan --app-secret, --verify-token y --permitido", file=sys.stderr); return 2
            whatsapp(url, opt["app-secret"], opt["verify-token"], opt["permitido"], opt.get("ajeno", "570000000099"))
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
        print(f"ERROR: el bot no responde en {url} ({e.__class__.__name__}). ¿Está corriendo?", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr); return 2
    fallas = RES.count(False)
    print(f"\n{len(RES) - fallas} de {len(RES)} comprobaciones PASAN.")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
