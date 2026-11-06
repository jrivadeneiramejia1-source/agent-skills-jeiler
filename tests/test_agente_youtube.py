"""Pruebas de la skill agente-youtube-infantil: el código de los nodos (con datos inventados), las plantillas de n8n y las reglas F12-F14 del revisor.
Correr: python -I -m unittest discover -s tests
Las del código de los nodos necesitan Node.js; si no está, se saltan. Las de n8n real solo corren si defines N8N_CARPETA (ver references/configuracion-paso-a-paso.md)."""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skills/agente-youtube-infantil"
REVISOR = RAIZ / "skills/revisar-flujo-n8n/scripts/revisar_flujo.py"
ARNES = SKILL / "scripts/probar_codigo.mjs"
NODE = shutil.which("node")
AHORA = "2026-05-01T12:00:00Z"
CHAT = "REEMPLAZA-CON-TU-CHAT-ID"


def plantilla(nombre):
    return json.loads((SKILL / "plantillas" / nombre).read_text(encoding="utf-8"))


def revisar(wf):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "f.json"
        p.write_text(json.dumps(wf), encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", str(REVISOR), str(p), "--json"], capture_output=True, text=True, timeout=60)
    return r.returncode, json.loads(r.stdout)


def ids_graves(hallazgos, gravedad=None):
    return {h["id"] for h in hallazgos if gravedad is None or h["gravedad"] == gravedad}


def nodo(wf, nombre):
    return next(n for n in wf["nodes"] if n["name"] == nombre)


@unittest.skipIf(NODE is None, "Node.js no está instalado: se saltan las pruebas del código de los nodos")
class TestCodigoDeLosNodos(unittest.TestCase):
    def correr(self, archivo, entrada=None, nodos=None, binarios=None, ahora=AHORA):
        datos = {"entrada": entrada if entrada is not None else [{"json": {}}], "nodos": nodos or {}, "binarios": binarios or {}, "ahora": ahora}
        with tempfile.TemporaryDirectory() as d:
            e = Path(d) / "entrada.json"
            e.write_text(json.dumps(datos), encoding="utf-8")
            r = subprocess.run([NODE, str(ARNES), str(SKILL / "codigo" / archivo), str(e)], capture_output=True, text=True, timeout=60)
        salida = json.loads(r.stdout)
        self.assertEqual(r.returncode, 0 if salida["ok"] else 1, r.stderr)
        return salida

    def items(self, archivo, **kw):
        s = self.correr(archivo, **kw)
        self.assertTrue(s["ok"], s.get("error"))
        return [i["json"] for i in s["items"]]

    # ---- configuración
    def test_configuracion_arma_12_busquedas_con_fechas_y_topes(self):
        js = self.items("configuracion.js")
        self.assertEqual(len(js), 12)
        self.assertEqual({j["dias"] for j in js}, {3, 7, 30})
        for j in js:
            self.assertTrue(1 <= j["maxResults"] <= 50)
        tres = next(j for j in js if j["dias"] == 3)
        self.assertEqual(tres["publishedAfter"], "2026-04-28T12:00:00.000Z")

    # ---- lotes de videos
    def busqueda(self, *ids):
        return {"json": {"items": [{"id": {"videoId": i}} for i in ids]}}

    def test_lotes_de_videos_quitan_repetidos_ids_raros_y_errores(self):
        entrada = [self.busqueda("AAAAAAAAAAA", "BBBBBBBBBBB", "AAAAAAAAAAA"), {"json": {"error": {"message": "cuota"}}},
                   self.busqueda("x; rm -rf", "a b c d e f", "../etc/passwd", "CCCCCCCCCCC")]
        js = self.items("lotes_videos.js", entrada=entrada)
        self.assertEqual(len(js), 1)
        self.assertEqual(js[0]["ids"].split(","), ["AAAAAAAAAAA", "BBBBBBBBBBB", "CCCCCCCCCCC"])
        self.assertEqual(js[0]["erroresBusqueda"], 1)

    def test_lotes_de_videos_de_50_con_tope_de_300(self):
        entrada = [self.busqueda(*[f"V{n:010d}" for n in range(i, i + 25)]) for i in range(0, 400, 25)]
        js = self.items("lotes_videos.js", entrada=entrada)
        self.assertEqual([len(j["ids"].split(",")) for j in js], [50] * 6)

    def test_lotes_de_videos_sin_nada(self):
        js = self.items("lotes_videos.js", entrada=[{"json": {"error": {"message": "x"}}}])
        self.assertEqual(js, [{"ids": "", "erroresBusqueda": 1}])

    # ---- lotes de canales
    def test_lotes_de_canales(self):
        v = lambda c: {"snippet": {"channelId": c}}  # noqa: E731
        entrada = [{"json": {"items": [v("UCaaaaaaaaaa01"), v("UCaaaaaaaaaa01"), v("UCbbbbbbbbbb02"), v("mal canal!")]}}, {"json": {"error": {}}}]
        js = self.items("lotes_canales.js", entrada=entrada)
        self.assertEqual(js, [{"ids": "UCaaaaaaaaaa01,UCbbbbbbbbbb02"}])
        self.assertEqual(self.items("lotes_canales.js", entrada=[{"json": {}}]), [{"ids": ""}])

    # ---- calcular virales
    def video(self, id_, canal, vistas, dias, titulo="Canción de prueba", directo="none", dur="PT2M30S"):
        import datetime as dt
        pub = (dt.datetime(2026, 5, 1, 12, tzinfo=dt.timezone.utc) - dt.timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {"id": id_, "snippet": {"title": titulo, "channelId": canal, "channelTitle": "Canal " + canal[-2:], "publishedAt": pub, "liveBroadcastContent": directo},
                "statistics": {"viewCount": str(vistas)}, "contentDetails": {"duration": dur}}

    def canal(self, id_, vistas, videos):
        return {"id": id_, "snippet": {"title": "Canal " + id_[-2:]}, "statistics": {"viewCount": str(vistas), "videoCount": str(videos), "subscriberCount": "100"}}

    def virales(self, videos, canales):
        return self.items("calcular_virales.js", entrada=[{"json": {"items": canales}}],
                          nodos={"Configuración": [{"json": {"chatId": "42"}}], "Estadísticas de videos": [{"json": {"items": videos}}]})[0]

    def test_virales_ordena_por_multiplo_del_propio_canal_y_descarta_lo_dudoso(self):
        canales = [self.canal("UCuno00000001", 30000, 11), self.canal("UCdos00000002", 15000, 6), self.canal("UCtres0000003", 900000, 3),
                   self.canal("UCcuatro00004", 50000, 10)]
        videos = [
            self.video("AAAAAAAAAAA", "UCuno00000001", 20000, 2, titulo="Viral reciente"),            # base 1000 -> x20, ventana 3 d
            self.video("BBBBBBBBBBB", "UCdos00000002", 5000, 20, titulo="Viral del mes"),             # base 2000 -> x2,5, ventana 30 d
            self.video("CCCCCCCCCCC", "UCuno00000001", 1500, 1, directo="live", titulo="Directo"),     # directo: fuera
            self.video("DDDDDDDDDDD", "UCtres0000003", 800000, 1, titulo="Canal con 3 videos"),        # canal con pocos videos: fuera
            self.video("EEEEEEEEEEE", "UCuno00000001", 500, 1, titulo="Pocas vistas"),                 # <1000 vistas: fuera
            self.video("FFFFFFFFFFF", "UCdos00000002", 9000, 40, titulo="Muy viejo"),                  # >30 días: fuera
            self.video("GGGGGGGGGGG", "UCcuatro00004", 12000, 5, titulo="<script>alert(1)</script>"),   # x ~ 3,4 en 7 d; el título se escapa
        ]
        r = self.virales(videos, canales)
        t = r["texto"]
        self.assertEqual(r["chatId"], "42")
        self.assertEqual(r["revisados"], 7)
        self.assertEqual(r["mostrados"], 3)
        for bueno in ("AAAAAAAAAAA", "BBBBBBBBBBB", "GGGGGGGGGGG"):
            self.assertIn("https://youtu.be/" + bueno, t)
        for malo in ("CCCCCCCCCCC", "DDDDDDDDDDD", "EEEEEEEEEEE", "FFFFFFFFFFF"):
            self.assertNotIn(malo, t)
        self.assertLess(t.index("Últimos 3 días"), t.index("Últimos 7 días"))
        self.assertLess(t.index("Últimos 7 días"), t.index("Últimos 30 días"))
        self.assertIn("×20", t)
        self.assertIn("2:30", t)
        self.assertNotIn("<script>", t)                     # Telegram con HTML: el título no puede inyectar etiquetas
        self.assertIn("&lt;script&gt;", t)
        self.assertIn("nunca para copiar", t)

    def test_virales_sin_resultados_da_mensaje_claro(self):
        r = self.virales([], [])
        self.assertEqual(r["mostrados"], 0)
        self.assertIn("Hoy no encontré", r["texto"])

    def test_virales_aguanta_respuestas_de_error_y_datos_raros(self):
        r = self.items("calcular_virales.js", entrada=[{"json": {"error": {"message": "cuota"}}}, {"json": {"items": [{"id": "UCuno00000001"}]}}],
                       nodos={"Configuración": [{"json": {"chatId": "42"}}],
                              "Estadísticas de videos": [{"json": {"error": {}}}, {"json": {"items": [{"id": "ZZZZZZZZZZZ"}, None, {"snippet": {}}]}}]})[0]
        self.assertEqual(r["mostrados"], 0)

    def test_virales_recorta_para_caber_en_telegram(self):
        canales = [self.canal(f"UCcanal{n:07d}", 30000, 11) for n in range(15)]
        titulos = "T" * 400
        videos = []
        for n in range(15):
            dias = [1, 5, 20][n // 5]
            videos.append(self.video(f"V{n:010d}", f"UCcanal{n:07d}", 20000 + n, dias, titulo=titulos))
        r = self.virales(videos, canales)
        self.assertLessEqual(len(r["texto"]), 4096)
        self.assertGreater(r["mostrados"], 0)

    # ---- «Solo tu chat y /subir N»
    def tg(self, texto, chat=CHAT, antiguedad=10):
        import calendar
        import time
        fecha = calendar.timegm(time.strptime(AHORA, "%Y-%m-%dT%H:%M:%SZ")) - antiguedad
        return [{"json": {"message": {"chat": {"id": chat}, "text": texto, "date": fecha}}}]

    def test_puerta_acepta_solo_tu_chat_y_arma_rutas_fijas(self):
        for n in "123":
            js = self.items("gate_subir.js", entrada=self.tg(f"/subir {n}"))[0]
            self.assertTrue(js["valido"])
            self.assertEqual(js["opcion"], n)
            self.assertTrue(js["rutaMeta"].endswith(f"\\{n}\\publicacion.json"))
            self.assertTrue(js["rutaVideo"].endswith(f"\\{n}\\video.mp4"))

    def test_puerta_descarta_chats_ajenos_y_mensajes_viejos(self):
        self.assertEqual(self.items("gate_subir.js", entrada=self.tg("/subir 1", chat="999999")), [])
        self.assertEqual(self.items("gate_subir.js", entrada=self.tg("/subir 1", chat=None)), [])
        self.assertEqual(self.items("gate_subir.js", entrada=self.tg("/subir 1", antiguedad=3600)), [])
        self.assertEqual(self.items("gate_subir.js", entrada=[{"json": {}}]), [])

    def test_puerta_no_deja_pasar_nada_que_escriba_la_persona_a_la_ruta(self):
        for texto in ("/subir 4", "/subir 0", "/subir ../../x", "/subir 1 2", "/subir 1; calc", "/subir 1\n/subir 2", "subir 1", "/subir", "", "/subir 12", "/subir ١"):
            js = self.items("gate_subir.js", entrada=self.tg(texto))[0]
            self.assertFalse(js["valido"], texto)
            self.assertNotIn("rutaMeta", js)
            self.assertIn("/subir 1", js["respuesta"])

    # ---- «Validar datos»
    def validar(self, contenido):
        binarios = {} if contenido is None else {"meta": contenido if isinstance(contenido, str) else json.dumps(contenido)}
        return self.items("validar_datos.js", nodos={"Solo tu chat y /subir N": [{"json": {"valido": True, "chatId": CHAT, "opcion": "2"}}]}, binarios=binarios)[0]

    def test_validar_datos_bien_y_fija_privado_y_para_ninos(self):
        r = self.validar({"titulo": " Canción del patito ", "descripcion": "Canción inventada.", "etiquetas": ["patito", "a,b", "<x>", "", None],
                          "privacidad": "public", "paraNinos": False, "privacyStatus": "public", "selfDeclaredMadeForKids": False, "idioma": "en", "categoria": "1"})
        self.assertTrue(r["ok"])
        self.assertEqual((r["privacidad"], r["paraNinos"], r["categoria"], r["idioma"]), ("private", True, "24", "es"))   # lo del archivo se ignora
        self.assertEqual(r["titulo"], "Canción del patito")
        self.assertEqual(r["etiquetas"], "patito,a b,x")
        self.assertEqual(r["opcion"], "2")

    def test_validar_datos_rechaza_lo_malo_y_avisa_sin_subir(self):
        base = {"titulo": "Título", "descripcion": "Descripción", "etiquetas": ["a"]}
        casos = {
            "sin título": {**base, "titulo": "  "},
            "título largo": {**base, "titulo": "x" * 101},
            "título con <": {**base, "titulo": "Hola <b>"},
            "sin descripción": {**base, "descripcion": ""},
            "descripción enorme": {**base, "descripcion": "ñ" * 2500},       # 5000 bytes
            "descripción con >": {**base, "descripcion": "a > b"},
            "21 etiquetas": {**base, "etiquetas": [f"t{i}" for i in range(21)]},
            "etiquetas largas": {**base, "etiquetas": ["x" * 100] * 6},
            "no es objeto": ["a", "b"],
            "título no es texto": {**base, "titulo": 123},
        }
        for nombre, c in casos.items():
            r = self.validar(c)
            self.assertFalse(r["ok"], nombre)
            self.assertTrue(r["respuesta"].startswith("No subí nada."), nombre)
            self.assertEqual(r["chatId"], CHAT)
            self.assertNotIn("privacidad", r)

    def test_validar_datos_con_archivo_ilegible_o_ausente(self):
        for contenido in ("esto no es json {", "", "null"):
            self.assertFalse(self.validar(contenido)["ok"], repr(contenido))
        s = self.correr("validar_datos.js", nodos={"Solo tu chat y /subir N": [{"json": {"chatId": CHAT, "opcion": "1"}}]}, binarios={})
        self.assertTrue(s["ok"])
        self.assertFalse(s["items"][0]["json"]["ok"])

    # ---- aviso de error
    def test_mensaje_de_error_escapa_html_y_recorta(self):
        entrada = [{"json": {"workflow": {"name": "Subir <b>"}, "execution": {"lastNodeExecuted": "Subir a YouTube", "error": {"message": "x" * 1000 + "<i>"}}}}]
        r = self.items("mensaje_error.js", entrada=entrada)[0]
        self.assertIn("&lt;b&gt;", r["texto"])
        self.assertNotIn("<i>", r["texto"])
        self.assertLess(len(r["texto"]), 600)
        self.assertEqual(r["chatId"], CHAT)
        self.assertIn("un flujo", self.items("mensaje_error.js", entrada=[{"json": {}}])[0]["texto"])

    # ---- el propio arnés
    def test_el_arnes_imita_los_errores_de_n8n(self):
        s = self.correr("lotes_canales.js", nodos={})   # funciona sin otros nodos
        self.assertTrue(s["ok"])
        s = self.correr("calcular_virales.js", entrada=[{"json": {"items": []}}], nodos={})
        self.assertFalse(s["ok"])
        self.assertIn("hasn't been executed", s["error"])
        with tempfile.TemporaryDirectory() as d:
            c, e = Path(d) / "c.js", Path(d) / "e.json"
            e.write_text(json.dumps({"entrada": []}), encoding="utf-8")
            for js in ("return 5;", "return [1];", "return [{json: 'texto'}];", "return [{}];"):
                c.write_text(js, encoding="utf-8")
                r = subprocess.run([NODE, str(ARNES), str(c), str(e)], capture_output=True, text=True, timeout=60)
                self.assertEqual((r.returncode, json.loads(r.stdout)["ok"]), (1, False), js)
            c.write_text("return [{json: {a: 1}}];", encoding="utf-8")
            r = subprocess.run([NODE, str(ARNES), str(c), str(e)], capture_output=True, text=True, timeout=60)
            self.assertEqual((r.returncode, json.loads(r.stdout)["ok"]), (0, True))
            r = subprocess.run([NODE, str(ARNES), str(c)], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 2)


class TestPlantillas(unittest.TestCase):
    NOMBRES = ["investigador-virales.json", "subir-youtube.json", "avisar-error.json"]

    def test_las_plantillas_son_exactamente_lo_que_sale_del_codigo(self):
        r = subprocess.run([sys.executable, "-I", str(SKILL / "scripts/generar_plantillas.py"), "--comprobar"], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_estructura_y_referencias(self):
        for nombre in self.NOMBRES:
            wf = plantilla(nombre)
            nombres = [n["name"] for n in wf["nodes"]]
            self.assertEqual(len(nombres), len(set(nombres)), f"{nombre}: nombres repetidos")
            self.assertEqual(len({n["id"] for n in wf["nodes"]}), len(nombres), f"{nombre}: ids repetidos")
            self.assertIs(wf["active"], False, f"{nombre}: debe exportarse apagado")
            self.assertNotIn("pinData", wf)
            conectados = set()
            for origen, salidas in wf["connections"].items():
                self.assertIn(origen, nombres)
                for rama in salidas["main"]:
                    for c in rama:
                        self.assertIn(c["node"], nombres, f"{nombre}: {origen} apunta a un nodo que no existe")
                        conectados.update({origen, c["node"]})
            for n in wf["nodes"]:
                if n["type"] != "n8n-nodes-base.stickyNote":
                    self.assertIn(n["name"], conectados, f"{nombre}: el nodo «{n['name']}» está suelto")
            # todo $('Nombre') escrito en un nodo (código o expresión) debe ser un nodo real de ESTE flujo
            for n in wf["nodes"]:
                for ref in re.findall(r"\$\('([^']+)'\)", json.dumps(n["parameters"], ensure_ascii=False)):
                    self.assertIn(ref, nombres, f"{nombre}/{n['name']}: usa $('{ref}') pero ese nodo no existe")

    def test_todo_va_con_marcadores_sin_claves_ni_datos_reales(self):
        for nombre in self.NOMBRES:
            texto = (SKILL / "plantillas" / nombre).read_text(encoding="utf-8")
            for cred in re.findall(r'"credentials": \{\s*"\w+": \{\s*"id": "([^"]+)"', texto):
                self.assertTrue(cred.startswith("REEMPLAZAR"), cred)
            self.assertNotRegex(texto, r"\d{8,10}:[A-Za-z0-9_-]{35}")
            self.assertNotRegex(texto, r"AIza[0-9A-Za-z_-]{35}")
            self.assertNotRegex(texto, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}")
        for js in (SKILL / "codigo").glob("*.js"):
            for linea in js.read_text(encoding="utf-8").splitlines():
                if re.match(r"const (CHAT_AUTORIZADO|CHAT_ID)\s*=", linea):
                    self.assertIn("REEMPLAZA-CON-TU-CHAT-ID", linea)

    def test_las_plantillas_salen_limpias_del_revisor(self):
        for nombre in self.NOMBRES:
            c, h = revisar(plantilla(nombre))
            self.assertEqual((c, h), (0, []), nombre)

    def test_la_subida_es_privada_para_ninos_y_sin_avisar_a_suscriptores(self):
        wf = plantilla("subir-youtube.json")
        op = nodo(wf, "Subir a YouTube (privado)")["parameters"]["options"]
        self.assertEqual(op["privacyStatus"], "private")          # texto fijo, no expresión
        self.assertIs(op["selfDeclaredMadeForKids"], True)
        self.assertIs(op["notifySubscribers"], False)
        pub = nodo(wf, "Publicar (hacer público)")["parameters"]["updateFields"]
        self.assertEqual(pub["privacyStatus"], "public")
        self.assertIs(pub["selfDeclaredMadeForKids"], True)       # el «update» borra lo que no se reenvía

    def test_publicar_solo_se_alcanza_por_la_rama_aprobada(self):
        wf = plantilla("subir-youtube.json")
        entradas = {}
        for origen, salidas in wf["connections"].items():
            for i, rama in enumerate(salidas["main"]):
                for c in rama:
                    entradas.setdefault(c["node"], []).append((origen, i))
        self.assertEqual(entradas["Publicar (hacer público)"], [("¿Aprobó?", 0)])
        self.assertEqual(entradas["¿Aprobó?"], [("Pedir aprobación", 0)])
        self.assertEqual(entradas["Pedir aprobación"], [("Subir a YouTube (privado)", 0)])
        self.assertEqual(entradas["Leer video"], [("¿Datos válidos?", 0)])
        self.assertEqual(entradas["Leer datos"], [("¿Pedido válido?", 0)])
        self.assertEqual(entradas["Solo tu chat y /subir N"], [("Telegram Trigger", 0)])
        aprob = nodo(wf, "Pedir aprobación")["parameters"]
        self.assertEqual(aprob["operation"], "sendAndWait")
        self.assertEqual(nodo(wf, "¿Aprobó?")["parameters"]["conditions"]["conditions"][0]["leftValue"], "={{ !!($json.data && $json.data.approved === true) }}")

    def test_los_nodos_de_riesgo_avisan_si_fallan(self):
        wf = plantilla("subir-youtube.json")
        for n in ("Leer datos", "Leer video", "Subir a YouTube (privado)", "Publicar (hacer público)"):
            self.assertEqual(nodo(wf, n).get("onError"), "continueErrorOutput", n)

    def test_el_investigador_no_publica_ni_sube_nada(self):
        wf = plantilla("investigador-virales.json")
        tipos = {n["type"] for n in wf["nodes"]}
        self.assertNotIn("n8n-nodes-base.youTube", tipos)
        for n in wf["nodes"]:
            if n["type"] == "n8n-nodes-base.httpRequest":
                self.assertEqual(n["parameters"]["url"].split("/")[2], "www.googleapis.com")      # solo habla con la API de YouTube
                self.assertEqual(n["parameters"]["genericAuthType"], "httpQueryAuth")             # la clave va en una credencial
                self.assertNotIn("key", [p["name"] for p in n["parameters"]["queryParameters"]["parameters"]])


class TestReglasF12aF14(unittest.TestCase):
    def bueno(self):
        return plantilla("subir-youtube.json")

    def test_el_flujo_malo_se_detecta(self):
        c, h = revisar(json.loads((SKILL / "ejemplos/flujo-youtube-malo.json").read_text(encoding="utf-8")))
        self.assertEqual(c, 1)
        self.assertLessEqual({"F12", "F13", "F14"}, ids_graves(h))
        self.assertLessEqual({"F12", "F14"}, ids_graves(h, "ALTA"))

    def test_sin_privacyStatus_en_la_subida(self):
        wf = self.bueno()
        del nodo(wf, "Subir a YouTube (privado)")["parameters"]["options"]["privacyStatus"]
        c, h = revisar(wf)
        self.assertIn("F12", ids_graves(h, "ALTA"))
        self.assertEqual(c, 1)

    def test_subida_publica_o_no_listada_o_con_expresion(self):
        casos = {"public": "ALTA", "unlisted": "MEDIA", "={{ $json.privacidad }}": "MEDIA"}
        for valor, gravedad in casos.items():
            wf = self.bueno()
            nodo(wf, "Subir a YouTube (privado)")["parameters"]["options"]["privacyStatus"] = valor
            _, h = revisar(wf)
            self.assertIn("F12", ids_graves(h, gravedad), valor)

    def test_sin_declarar_para_ninos(self):
        for n in ("Subir a YouTube (privado)", "Publicar (hacer público)"):
            wf = self.bueno()
            p = nodo(wf, n)["parameters"]
            (p.get("options") or p["updateFields"]).pop("selfDeclaredMadeForKids")
            c, h = revisar(wf)
            self.assertIn("F13", ids_graves(h, "MEDIA"), n)
            self.assertEqual(c, 0)       # F13 es MEDIA: avisa pero no es grave

    def test_publicar_sin_aprobacion_en_el_camino(self):
        # a) se quita el nodo de aprobación y se une la subida directo a publicar
        wf = self.bueno()
        wf["nodes"] = [n for n in wf["nodes"] if n["name"] not in ("Pedir aprobación", "¿Aprobó?")]
        wf["connections"].pop("Pedir aprobación")
        wf["connections"].pop("¿Aprobó?")
        wf["connections"]["Subir a YouTube (privado)"]["main"][0] = [{"node": "Publicar (hacer público)", "type": "main", "index": 0}]
        self.assertIn("F14", ids_graves(revisar(wf)[1], "ALTA"))
        # b) la aprobación existe pero no hay un IF que mire la respuesta
        wf = self.bueno()
        wf["connections"]["Pedir aprobación"]["main"][0] = [{"node": "Publicar (hacer público)", "type": "main", "index": 0}]
        self.assertIn("F14", ids_graves(revisar(wf)[1], "ALTA"))
        # c) el nodo de aprobación existe pero está suelto (no es camino hacia publicar)
        wf = self.bueno()
        wf["connections"]["Subir a YouTube (privado)"]["main"][0] = [{"node": "Publicar (hacer público)", "type": "main", "index": 0}]
        self.assertIn("F14", ids_graves(revisar(wf)[1], "ALTA"))

    def test_nodos_de_otros_recursos_no_dan_falsas_alarmas(self):
        wf = self.bueno()
        wf["nodes"].append({"id": "z", "name": "Lista", "type": "n8n-nodes-base.youTube", "typeVersion": 1, "position": [0, 0],
                            "parameters": {"resource": "playlist", "operation": "getAll", "returnAll": True}})
        wf["connections"]["Avisar publicado"] = {"main": [[{"node": "Lista", "type": "main", "index": 0}]]}
        self.assertEqual(revisar(wf)[1], [])


@unittest.skipUnless(os.environ.get("N8N_CARPETA") and NODE, "define N8N_CARPETA (carpeta con n8n instalado) y ten Node 24 para correr esta prueba")
class TestConN8nDeVerdad(unittest.TestCase):
    def comprobar(self, *archivos):
        env = {**os.environ, "NODE_OPTIONS": "--no-node-snapshot"}
        r = subprocess.run([NODE, str(SKILL / "scripts/comprobar_con_n8n.mjs"), os.environ["N8N_CARPETA"], *map(str, archivos)], capture_output=True, text=True, timeout=300, env=env)
        return r.returncode, r.stdout

    def test_las_plantillas_son_validas_para_n8n(self):
        c, out = self.comprobar(*sorted((SKILL / "plantillas").glob("*.json")))
        self.assertEqual(c, 0, out)

    def test_nodos_invalidos_se_detectan(self):
        c, out = self.comprobar(SKILL / "ejemplos/flujo-nodos-invalidos.json")
        self.assertEqual(c, 1)
        for frase in ("«title»", "versión 99", "noExiste"):
            self.assertIn(frase, out)


if __name__ == "__main__":
    unittest.main()
