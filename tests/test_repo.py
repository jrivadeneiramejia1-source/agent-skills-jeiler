"""Pruebas del repo: estructura, grupos y que no se cuelen datos personales. Correr: python -I -m unittest discover -s tests"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
ORIGINALES = ["revisar-flujo-n8n", "seguridad-agentes", "probar-prompts", "apis-gratis", "bot-telegram", "plantillas-n8n", "whatsapp-cloud-api"]


def grupos():
    g = {}
    for linea in (RAIZ / "grupos.conf").read_text(encoding="utf-8").splitlines():
        if linea.strip() and not linea.lstrip().startswith("#"):
            nombre, _, resto = linea.partition(":")
            g[nombre.strip()] = resto.split()
    return g


try:
    import yaml  # opcional: si está instalado, se valida con un lector de YAML de verdad
except ImportError:
    yaml = None


def encabezado(skill_md):
    t = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    return m.group(1) if m else None


class TestEstructura(unittest.TestCase):
    def test_grupos_apuntan_a_skills_que_existen(self):
        for g, lista in grupos().items():
            for s in lista:
                self.assertTrue((SKILLS / s / "SKILL.md").is_file(), f"grupo {g}: falta la skill {s}")

    def test_encabezados_validos(self):
        for g, lista in grupos().items():
            for s in lista:
                h = encabezado(SKILLS / s / "SKILL.md")
                self.assertIsNotNone(h, f"{s}: sin encabezado --- ---")
                nombre = re.search(r"(?m)^name:\s*(\S+)", h)
                self.assertTrue(nombre and nombre.group(1) == s, f"{s}: name no coincide con la carpeta")
                desc = re.search(r"(?m)^description:\s*(.+)$", h)
                self.assertTrue(desc and desc.group(1).strip(), f"{s}: sin description")
                v = desc.group(1).strip()
                if not v.startswith(("'", '"', ">", "|")):
                    self.assertNotIn(": ", v, f"{s}: la description tiene «: » sin comillas (YAML la rompe)")

    @unittest.skipIf(yaml is None, "PyYAML no está instalado (pip install pyyaml)")
    def test_encabezados_son_yaml_valido(self):
        for g, lista in grupos().items():
            for s in lista:
                try:
                    datos = yaml.safe_load(encabezado(SKILLS / s / "SKILL.md"))
                except yaml.YAMLError as e:
                    self.fail(f"{s}: el encabezado no es YAML válido ({str(e)[:80]})")
                self.assertTrue(datos.get("description"), s)

    def test_originales_estan_en_algun_grupo_o_son_de_vercel(self):
        en_grupos = {s for lista in grupos().values() for s in lista}
        for s in ORIGINALES:
            self.assertIn(s, en_grupos, f"la skill original {s} no está en ningún grupo")

    def test_sin_zip_repetidos_en_skills(self):
        self.assertEqual([p.name for p in SKILLS.glob("*.zip")], [])

    def test_claude_md_es_archivo_propio_con_reglas(self):
        c = RAIZ / "CLAUDE.md"
        self.assertTrue(c.is_file() and not c.is_symlink())
        t = c.read_text(encoding="utf-8")
        for frase in ("claves", "main", "indígenas", "[F]"):
            self.assertIn(frase, t)

    def test_indice_en_la_raiz_menciona_las_originales(self):
        t = (RAIZ / "INDICE-DE-SKILLS.md").read_text(encoding="utf-8")
        for s in ORIGINALES:
            self.assertIn(s, t, f"el índice no menciona {s}")


class TestSinDatosPersonales(unittest.TestCase):
    CORREO = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    OK_CORREO = ("example.", "ejemplo.invalid", "users.noreply.github.com", "noreply@")
    TELEFONO = re.compile(r"(?<![\w.:-])\+?57\d{10}(?![\w.])")

    def archivos_originales(self):
        for s in ORIGINALES:
            for p in (SKILLS / s).rglob("*"):
                if p.is_file() and p.suffix in {".md", ".json", ".py", ".ts", ".mjs", ".toml", ".yml"}:
                    yield p
        for n in ("README.md", "CLAUDE.md", "INDICE-DE-SKILLS.md", "PRUEBAS.md", "LECCIONES.md"):
            if (RAIZ / n).is_file():
                yield RAIZ / n

    def test_sin_correos_ni_telefonos_reales(self):
        for p in self.archivos_originales():
            t = p.read_text(encoding="utf-8", errors="replace")
            for m in self.CORREO.findall(t):
                self.assertTrue(any(o in m for o in self.OK_CORREO), f"{p.relative_to(RAIZ)}: correo {m}")
            for m in self.TELEFONO.findall(t):
                self.assertRegex(m, r"^5700000000\d\d$", f"{p.relative_to(RAIZ)}: teléfono parecido a uno real (los inventados son 5700000000NN)")

    def test_documentos_usan_python_no_python3(self):
        for p in self.archivos_originales():
            if p.suffix == ".md":
                t = p.read_text(encoding="utf-8")
                self.assertNotIn("python3 ", t, f"{p.relative_to(RAIZ)} usa python3 (Jeiler usa python)")


if __name__ == "__main__":
    unittest.main()
