#!/bin/bash
# Instala las skills de los grupos de grupos-activos.txt al abrir una sesión en la nube.
set -euo pipefail

# Solo en sesiones en la nube
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"
# La salida va a stderr para no agregar texto al contexto de la sesión.
bash ./instalar.sh --activos >&2
