#!/usr/bin/env python3
"""Compara FUENTES.md con los repos de origen. Solo lee: no cambia nada, no pide claves.
Uso (desde la carpeta del repo):  python -I comparar-fuentes.py [FUENTES.md]
Para cada fila con un repo de origen y un commit copiado, pregunta a GitHub cuál es el commit más
nuevo de la rama principal (git ls-remote) y dice si cambió. Salida: 0 todo igual, 1 hay cambios,
2 no se pudo consultar alguno. Si existe skills/apis-gratis, avisa si su tabla de límites tiene más
de 3 meses (los planes gratuitos cambian)."""
import os, re, subprocess, sys, datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

archivo = Path(sys.argv[1] if len(sys.argv) > 1 else "FUENTES.md")
if not archivo.is_file():
    sys.exit(f"No encuentro {archivo}. Corre el script desde la carpeta del repo.")

filas = []  # (skills, repo, commit)
for linea in archivo.read_text(encoding="utf-8").splitlines():
    c = [x.strip() for x in linea.strip().strip("|").split("|")]
    if len(c) < 4 or c[0] in ("Skills", "---") or set(c[0]) <= {"-"}:
        continue
    repo = re.search(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b", re.sub(r"`[^`]*`", "", c[1]))
    commit = re.fullmatch(r"[0-9a-f]{7,40}", c[2])
    if repo and commit:
        filas.append((c[0], repo.group(1), c[2]))

def consultar(repo):
    try:
        r = subprocess.run(["git", "ls-remote", f"https://github.com/{repo}", "HEAD"],
                           capture_output=True, text=True, timeout=45, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        sal = r.stdout.split()
        return sal[0] if r.returncode == 0 and sal else None
    except Exception:
        return None

repos = sorted({f[1] for f in filas})
with ThreadPoolExecutor(max_workers=4) as ex:
    ultimo = dict(zip(repos, ex.map(consultar, repos)))

cambios = fallos = 0
visto = set()
for skills, repo, copiado in filas:
    ahora = ultimo[repo]
    if ahora is None:
        estado, fallos = "NO SE PUDO CONSULTAR", fallos + 1
    elif ahora.startswith(copiado) or copiado.startswith(ahora[:len(copiado)]):
        estado = "igual"
    else:
        estado, cambios = f"HAY CAMBIOS (copiado {copiado[:7]}, ahora {ahora[:7]})", cambios + 1
    if (repo, copiado) in visto: continue
    visto.add((repo, copiado))
    print(f"{estado:50} {repo}   [{skills[:60]}]")

apis = Path("skills/apis-gratis/SKILL.md")
if apis.is_file():
    m = re.search(r"foto del (\d{4})-(\d{2})", apis.read_text(encoding="utf-8"))
    if m:
        hoy = datetime.date.today()
        meses = (hoy.year - int(m[1])) * 12 + hoy.month - int(m[2])
        print(f"\napis-gratis: tabla de límites tomada en {m[1]}-{m[2]} ({meses} meses). " +
              ("YA TOCA VERIFICARLA en las páginas oficiales." if meses >= 3 else "Todavía vigente (se revisa cada 3 meses)."))

print(f"\n{len(visto)} orígenes revisados: {cambios} con cambios, {fallos} sin poder consultar.")
print("Esto solo dice SI cambió. Antes de actualizar una skill, mirar qué cambió y revisar su seguridad otra vez.")
sys.exit(2 if fallos else (1 if cambios else 0))
