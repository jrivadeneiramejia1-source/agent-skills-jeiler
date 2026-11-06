"""Pruebas de probar_webhook.py con bots de mentira (servidores locales de Python): uno correcto y uno malo."""
import hashlib
import hmac
import json
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "skills/seguridad-agentes/scripts/probar_webhook.py"
SECRETO, APP_SECRET, VERIFY = "secreto-de-prueba-largo", "secreto-app-de-prueba", "palabra-de-prueba"
PERMITIDO_TG, PERMITIDO_WA = 111111111, "570000000000"


def servidor(clase):
    s = ThreadingHTTPServer(("127.0.0.1", 0), clase)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


class Base(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def responder(self, codigo, texto=""):
        datos = texto.encode()
        self.send_response(codigo); self.send_header("Content-Length", str(len(datos))); self.end_headers(); self.wfile.write(datos)

    def cuerpo(self):
        return self.rfile.read(int(self.headers.get("Content-Length") or 0))


class TelegramBueno(Base):
    def do_GET(self):
        self.responder(401)

    def do_POST(self):
        raw = self.cuerpo()
        if self.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRETO:
            return self.responder(401)
        try:
            u = json.loads(raw)
        except ValueError:
            return self.responder(200)
        if u.get("message", {}).get("from", {}).get("id") != PERMITIDO_TG:
            return self.responder(200)
        self.responder(200, json.dumps({"method": "sendMessage", "text": "hola"}))


class TelegramMalo(Base):  # acepta a cualquiera y se cae con cuerpos raros
    def do_GET(self):
        self.responder(200, "hola")

    def do_POST(self):
        try:
            u = json.loads(self.cuerpo())
        except ValueError:
            return self.responder(500)
        self.responder(200, json.dumps({"method": "sendMessage", "chat_id": u["message"]["chat"]["id"]}))


class WhatsAppBueno(Base):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        if q.get("hub.mode") == ["subscribe"] and q.get("hub.verify_token") == [VERIFY]:
            return self.responder(200, q["hub.challenge"][0])
        self.responder(403)

    def do_POST(self):
        raw = self.cuerpo()
        esperado = "sha256=" + hmac.new(APP_SECRET.encode(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(self.headers.get("X-Hub-Signature-256", ""), esperado):
            return self.responder(401)
        try:
            json.loads(raw)
        except ValueError:
            return self.responder(400)
        self.responder(200)


class WhatsAppMalo(Base):
    def do_GET(self):
        self.responder(200, parse_qs(urlparse(self.path).query).get("hub.challenge", [""])[0])

    def do_POST(self):
        try:
            json.loads(self.cuerpo())
        except ValueError:
            return self.responder(500)
        self.responder(200)


def probar(*args):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def fallas(salida):
    return {l.split("|")[1].strip().split(".")[0] for l in salida.splitlines() if l.startswith("FALLA")}


class TestProbarWebhook(unittest.TestCase):
    def arrancar(self, clase):
        s = servidor(clase)
        self.addCleanup(s.server_close)
        self.addCleanup(s.shutdown)
        return f"http://127.0.0.1:{s.server_address[1]}/"

    def tg(self, clase):
        return probar("telegram", self.arrancar(clase), "--secreto", SECRETO, "--permitido", str(PERMITIDO_TG))

    def wa(self, clase):
        return probar("whatsapp", self.arrancar(clase), "--app-secret", APP_SECRET, "--verify-token", VERIFY, "--permitido", PERMITIDO_WA)

    def test_telegram_bueno_pasa_todo(self):
        c, out, _ = self.tg(TelegramBueno)
        self.assertEqual((c, fallas(out)), (0, set()), out)
        self.assertIn("7 de 7", out)

    def test_telegram_malo_falla_lo_esperado(self):
        c, out, _ = self.tg(TelegramMalo)
        self.assertEqual(c, 1)
        self.assertTrue({"T1", "T2", "T3", "T4", "T6"} <= fallas(out), out)

    def test_whatsapp_bueno_pasa_todo(self):
        c, out, _ = self.wa(WhatsAppBueno)
        self.assertEqual((c, fallas(out)), (0, set()), out)
        self.assertIn("11 de 11", out)

    def test_whatsapp_malo_falla_lo_esperado(self):
        c, out, _ = self.wa(WhatsAppMalo)
        self.assertEqual(c, 1)
        self.assertTrue({"W2", "W3", "W4", "W5", "W6", "W7", "W11"} <= fallas(out), out)

    def test_no_prueba_direcciones_remotas_sin_permiso(self):
        c, _, err = probar("telegram", "https://ejemplo.invalid/", "--secreto", "x", "--permitido", "1")
        self.assertEqual(c, 2)
        self.assertIn("direcciones locales", err)

    def test_sin_bot_corriendo_da_error_claro(self):
        c, _, err = probar("telegram", "http://127.0.0.1:59999/", "--secreto", "x", "--permitido", "1")
        self.assertEqual(c, 2)
        self.assertIn("¿Está corriendo?", err)

    def test_argumentos_incompletos(self):
        self.assertEqual(probar("telegram", "http://127.0.0.1:1/")[0], 2)
        self.assertEqual(probar("whatsapp", "http://127.0.0.1:1/", "--permitido", "1")[0], 2)
        self.assertEqual(probar()[0], 2)


if __name__ == "__main__":
    unittest.main()
