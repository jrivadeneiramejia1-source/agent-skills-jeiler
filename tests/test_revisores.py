"""Pruebas de los revisores con ejemplos buenos y malos, y con cambios hechos a propósito."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FLUJO = RAIZ / "skills/revisar-flujo-n8n/scripts/revisar_flujo.py"
BOT = RAIZ / "skills/seguridad-agentes/scripts/revisar_bot.py"
EJ_FLUJO = RAIZ / "skills/revisar-flujo-n8n/ejemplos"
EJ_BOT = RAIZ / "skills/seguridad-agentes/ejemplos"
TOKEN_FALSO = "FAKEFAKEFAKEFAKE"
BEARER_FALSO = "abcdefghijklmnopqrstuvwxyz0123456789"


def correr(script, arg, *extra):
    r = subprocess.run([sys.executable, "-I", str(script), str(arg), *extra], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr


def ids(salida_json):
    return {h["id"] for h in json.loads(salida_json)}


class TestFlujo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bueno = json.loads((EJ_FLUJO / "flujo-bueno.json").read_text(encoding="utf-8"))

    def guardar(self, wf):
        p = self.tmp / "f.json"
        p.write_text(json.dumps(wf), encoding="utf-8")
        return p

    def test_bueno_sale_limpio(self):
        c, out, _ = correr(FLUJO, EJ_FLUJO / "flujo-bueno.json", "--json")
        self.assertEqual((c, json.loads(out)), (0, []))

    def test_malo_detecta_todo(self):
        c, out, _ = correr(FLUJO, EJ_FLUJO / "flujo-malo.json", "--json")
        self.assertEqual(c, 1)
        self.assertEqual(ids(out), {"F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11"})

    def test_informe_no_muestra_valores_secretos(self):
        for formato in ([], ["--json"]):
            _, out, _ = correr(FLUJO, EJ_FLUJO / "flujo-malo.json", *formato)
            for secreto in (TOKEN_FALSO, BEARER_FALSO, "persona.inventada", "dato guardado de prueba"):
                self.assertNotIn(secreto, out)

    def test_cambios_a_propósito_disparan_la_regla(self):
        casos = []
        wf = json.loads(json.dumps(self.bueno)); del wf["settings"]["errorWorkflow"]
        for n in wf["nodes"]:
            n.pop("onError", None)
        casos.append(("F07", wf))
        wf = json.loads(json.dumps(self.bueno)); wf["nodes"] = [n for n in wf["nodes"] if n["name"] != "Solo mi usuario"]
        casos.append(("F04", wf))
        wf = json.loads(json.dumps(self.bueno))
        for n in wf["nodes"]:
            if n["type"].endswith(".webhook"): n["parameters"]["authentication"] = "none"
        casos.append(("F03", wf))
        wf = json.loads(json.dumps(self.bueno)); wf["pinData"] = {"Mensaje de Telegram": [{"json": {}}]}
        casos.append(("F08", wf))
        wf = json.loads(json.dumps(self.bueno)); wf["active"] = True
        casos.append(("F11", wf))
        for esperado, wf in casos:
            c, out, _ = correr(FLUJO, self.guardar(wf), "--json")
            self.assertIn(esperado, ids(out), f"no saltó {esperado}")

    def test_token_telegram_dentro_de_una_direccion(self):
        """Fallo real encontrado al probar: /bot<numero>:<token> no se detectaba."""
        wf = json.loads(json.dumps(self.bueno))
        wf["nodes"].append({"id": "x", "name": "Llamada", "type": "n8n-nodes-base.httpRequest", "typeVersion": 1, "position": [0, 0],
                            "parameters": {"url": "https://api.ejemplo.invalid/bot000000000:" + "A" * 35 + "/sendMessage"}})
        _, out, _ = correr(FLUJO, self.guardar(wf), "--json")
        self.assertIn("F01", ids(out))

    def test_marcadores_no_son_claves(self):
        """Medido en 2.061 flujos reales: valores como <YOUR_API_KEY> son huecos por llenar, no claves."""
        def con_valor(v):
            wf = json.loads(json.dumps(self.bueno))
            wf["nodes"].append({"id": "x", "name": "H", "type": "n8n-nodes-base.httpRequest", "typeVersion": 1, "position": [0, 0],
                                "parameters": {"url": "https://api.ejemplo.invalid/", "sendHeaders": True,
                                               "headerParameters": {"parameters": [{"name": "Authorization", "value": v}]}}})
            return self.guardar(wf)
        for marcador in ("Bearer <YOUR_API_KEY>", "your_api_key", "Bearer $OPENAI_API_KEY", "[YOUR API KEY HERE]", "Bearer "):
            _, out, _ = correr(FLUJO, con_valor(marcador), "--json")
            self.assertFalse(ids(out) & {"F01", "F02"}, marcador)
        _, out, _ = correr(FLUJO, con_valor("Bearer q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6"), "--json")
        self.assertTrue({"F01", "F02"} <= ids(out))

    def test_errores_de_entrada(self):
        self.assertEqual(correr(FLUJO, self.tmp / "no-existe.json")[0], 2)
        malo = self.tmp / "roto.json"; malo.write_text("{ no es json", encoding="utf-8")
        self.assertEqual(correr(FLUJO, malo)[0], 2)
        self.assertEqual(correr(FLUJO, self.guardar({"a": 1}))[0], 2)
        self.assertEqual(correr(FLUJO, self.guardar({"nodes": []}))[0], 2)
        self.assertEqual(correr(FLUJO, self.guardar([1, 2, 3]))[0], 2)
        self.assertEqual(subprocess.run([sys.executable, "-I", str(FLUJO)], capture_output=True).returncode, 2)


class TestBot(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_buenos_sin_graves(self):
        for d in ("bot-telegram-bueno", "bot-whatsapp-bueno"):
            c, out, _ = correr(BOT, EJ_BOT / d, "--json")
            self.assertEqual(c, 0, d)
            self.assertFalse({h["gravedad"] for h in json.loads(out)} & {"ALTA", "MEDIA"}, d)

    def test_malos_detectados(self):
        c, out, _ = correr(BOT, EJ_BOT / "bot-telegram-malo", "--json")
        self.assertEqual(c, 1)
        self.assertTrue({"B01", "B02", "B10", "B11", "B31", "B32"} <= ids(out))
        c, out, _ = correr(BOT, EJ_BOT / "bot-whatsapp-malo", "--json")
        self.assertEqual(c, 1)
        self.assertTrue({"B20", "B22", "B31"} <= ids(out))

    def test_no_muestra_valores(self):
        _, out, _ = correr(BOT, EJ_BOT / "bot-telegram-malo")
        for secreto in (TOKEN_FALSO, "una-clave-escrita-aqui"):
            self.assertNotIn(secreto, out)

    def test_comentario_no_engaña(self):
        """Fallo real encontrado al probar: la palabra secret_token en un comentario ocultaba la falta del secret_token."""
        (self.tmp / "i.ts").write_text('import { Bot } from "grammy";\n// TODO poner secret_token y from.id\nconst b = new Bot(process.env.X);\n', encoding="utf-8")
        c, out, _ = correr(BOT, self.tmp, "--json")
        self.assertTrue({"B10", "B11"} <= ids(out))

    def test_console_log_de_ctx_update(self):
        (self.tmp / "i.ts").write_text('import { Bot } from "grammy";\nbot.use((ctx) => { console.log(JSON.stringify(ctx.update)); });\n', encoding="utf-8")
        _, out, _ = correr(BOT, self.tmp, "--json")
        self.assertIn("B31", ids(out))

    def test_env_sin_gitignore_es_grave(self):
        (self.tmp / ".dev.vars").write_text("BOT_TOKEN=algo\n", encoding="utf-8")
        (self.tmp / "i.ts").write_text("export default {};\n", encoding="utf-8")
        c, out, _ = correr(BOT, self.tmp, "--json")
        self.assertEqual(c, 1)
        self.assertIn("B03", ids(out))
        (self.tmp / ".gitignore").write_text(".dev.vars\n", encoding="utf-8")
        _, out, _ = correr(BOT, self.tmp, "--json")
        self.assertFalse([h for h in json.loads(out) if h["id"] == "B03" and h["gravedad"] == "ALTA"])

    def test_firma_sin_comparacion_segura(self):
        (self.tmp / "i.ts").write_text('const f = req.headers.get("x-hub-signature-256"); if (f === esperado) {}\n// hub.verify_token hub.challenge graph.facebook.com\n', encoding="utf-8")
        _, out, _ = correr(BOT, self.tmp, "--json")
        self.assertIn("B21", ids(out))

    def test_errores_de_entrada(self):
        self.assertEqual(correr(BOT, self.tmp / "no-existe")[0], 2)
        self.assertEqual(correr(BOT, self.tmp)[0], 2)  # carpeta vacía

    @unittest.skipUnless(shutil.which("node"), "node no está instalado")
    def test_firma_whatsapp_con_node(self):
        script = (
            "import { firmaValida } from '%s';\n"
            "import { createHmac } from 'node:crypto';\n"
            "const s='secreto-inventado', c='{\"a\":1}';\n"
            "const ok='sha256='+createHmac('sha256',s).update(c).digest('hex');\n"
            "const r=[await firmaValida(c,ok,s)===true, await firmaValida(c+' ',ok,s)===false, await firmaValida(c,ok,'otro')===false,\n"
            " await firmaValida(c,null,s)===false, await firmaValida(c,'sha256=abcd',s)===false, await firmaValida(c,ok,'')===false];\n"
            "process.exit(r.every(Boolean)?0:1);\n"
        ) % (EJ_BOT / "bot-whatsapp-bueno/src/firma.mjs").as_uri()
        p = self.tmp / "t.mjs"; p.write_text(script, encoding="utf-8")
        r = subprocess.run(["node", str(p)], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
