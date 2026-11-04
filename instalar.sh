#!/usr/bin/env bash
# instalar.sh — copia skills de este repo a la carpeta de skills de Claude.
#
# Uso:
#   ./instalar.sh --lista            muestra los grupos y sus skills
#   ./instalar.sh GRUPO [GRUPO...]   instala esos grupos
#   ./instalar.sh --activos          instala los grupos escritos en grupos-activos.txt
#   ./instalar.sh --todo             instala todos los grupos (gasta más tokens)
#
# Carpeta de destino: $CLAUDE_SKILLS_DIR, o ~/.claude/skills si no está definida.
# Seguridad: no pisa una skill que ya exista con el mismo nombre, salvo que la haya
# instalado este mismo repo (lo marca con un archivo .instalada-por-skills-jeiler).
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ID="$(basename "$AQUI")"
DESTINO="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CONF="$AQUI/grupos.conf"
ACTIVOS="$AQUI/grupos-activos.txt"
MARCA=".instalada-por-skills-jeiler"
ok=0; omitidas=0; errores=0

lineas_conf() { grep -vE '^[[:space:]]*(#|$)' "$CONF"; }
lista_grupos() { lineas_conf | cut -d: -f1; }
skills_de() { lineas_conf | grep -E "^$1:" | head -1 | cut -d: -f2-; }

mostrar_lista() {
  while IFS= read -r g; do echo "$g: $(skills_de "$g" | xargs)"; done < <(lista_grupos)
}

instalar_skill() {
  local n="$1" src="$AQUI/skills/$1" dest="$DESTINO/$1"
  if [ ! -f "$src/SKILL.md" ]; then echo "  ERROR: la skill '$n' no está en este repo"; errores=$((errores+1)); return; fi
  if [ -e "$dest" ]; then
    if [ -f "$dest/$MARCA" ] && [ "$(cat "$dest/$MARCA")" = "$REPO_ID" ]; then
      rm -rf "$dest"
    else
      echo "  OMITIDA $n: ya existe una skill con ese nombre que no instaló este repo"; omitidas=$((omitidas+1)); return
    fi
  fi
  cp -r "$src" "$dest"; echo "$REPO_ID" > "$dest/$MARCA"; ok=$((ok+1))
}

instalar_grupo() {
  local g="$1" lista
  if ! lista_grupos | grep -qx "$g"; then echo "ERROR: el grupo '$g' no existe. Usa: ./instalar.sh --lista"; errores=$((errores+1)); return; fi
  lista="$(skills_de "$g")"
  echo "Grupo $g:"
  for n in $lista; do instalar_skill "$n"; done
}

[ -f "$CONF" ] || { echo "ERROR: falta $CONF"; exit 1; }
[ $# -ge 1 ] || { sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 1; }
mkdir -p "$DESTINO"

case "$1" in
  --lista) mostrar_lista; exit 0 ;;
  --todo) while IFS= read -r g; do instalar_grupo "$g"; done < <(lista_grupos) ;;
  --activos)
    if [ ! -f "$ACTIVOS" ]; then echo "No hay grupos-activos.txt: no se instaló nada."; exit 0; fi
    while IFS= read -r g; do instalar_grupo "$g"; done < <(grep -vE '^[[:space:]]*(#|$)' "$ACTIVOS") ;;
  -*) echo "Opción desconocida: $1"; exit 1 ;;
  *) for g in "$@"; do instalar_grupo "$g"; done ;;
esac
echo "Listo: $ok instaladas, $omitidas omitidas, $errores con error. Destino: $DESTINO"
[ "$errores" -eq 0 ]
