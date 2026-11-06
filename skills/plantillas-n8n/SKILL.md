---
name: plantillas-n8n
description: Parte de un flujo de n8n ya hecho en vez de empezar de cero. Busca en una biblioteca de unos 2.000 flujos, elige 2 o 3 parecidos, los limpia (quita datos y credenciales), los adapta y los valida. Usar cuando el usuario diga "una automatización de n8n que haga X", "hay alguna plantilla", "no quiero empezar de cero" o "mira cómo hicieron otro flujo parecido".
---

# Plantillas de n8n (partir de un flujo existente)

La biblioteca es `Zie619/n8n-workflows` (MIT): 2.061 flujos en `workflows/<Servicio>/<número>_<nombre>.json`. Se descarga con `git clone --depth 1` en una carpeta aparte; **no copiarla entera al repositorio del usuario** (pesa unos 46 MB).

## Reglas
- **Licencia:** la biblioteca declara MIT, pero reúne flujos tomados de otras personas y de sitios públicos. Para uso comercial o para publicar, **usar la plantilla como idea y reescribir**, no pegar y publicar.
- **Credenciales:** un flujo importado nunca debe traer credenciales ni datos de otra persona. El usuario crea las suyas en n8n.
- **Importar siempre desactivado.** Un flujo activo puede empezar a enviar mensajes o borrar cosas antes de revisarlo.
- Nunca pedir ni guardar claves.

## Proceso
1. **Definir** en 3 líneas qué debe hacer el flujo: disparador (qué lo inicia), pasos y resultado.
2. **Buscar** en la biblioteca:
   - por servicio: las carpetas de `workflows/` llevan el nombre del servicio (Telegram, Gmail, Airtable…);
   - por texto: `grep -ril "palabra" workflows | head -20`.
3. **Elegir 2 o 3** y leer sus nodos: qué disparador usan, cuántos pasos, qué servicios. Comparar y quedarse con el más simple que sirva. Anotar de cuál se tomó la idea.
4. **Limpiar** con este script (quita `pinData`, que puede traer datos reales; quita las credenciales; deja el flujo desactivado y dice qué credenciales hay que crear):

```python
import json, sys
# Uso: python -I limpiar-flujo.py ENTRADA.json SALIDA.json
entrada, salida = sys.argv[1], sys.argv[2]
d = json.load(open(entrada, encoding="utf-8"))
quito_pin = bool(d.pop("pinData", None))
necesitan = []
for n in d.get("nodes", []):
    c = n.pop("credentials", None)
    if c:
        necesitan.append((n.get("name"), sorted(c)))
d["active"] = False
json.dump(d, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("pinData quitado:", quito_pin, "| activo=False")
print("credenciales que debes crear tú:", necesitan if necesitan else "ninguna")
```
   Se probó sobre un flujo real de la biblioteca: quedó con 0 credenciales, sin `pinData` y desactivado.

   **El script NO quita claves ni correos escritos directo en los parámetros** (por ejemplo en un encabezado `Authorization: Bearer ...`). Al revisar los 2.061 flujos de la biblioteca (2026-11-04): 217 vienen activos, 136 traen `pinData`, 286 tienen direcciones de correo escritas dentro, y 4 traen algo con forma de clave real (`pplx-`, `apify_`, `glpat-`, `AIzaSy`) en lugar de un marcador como `YOUR_TOKEN`. Por eso, después de limpiar, **buscar claves antes de seguir** y **no usar jamás una clave que venga en una plantilla** (puede ser ajena o estar filtrada):
```bash
# Uso: grep -nEo "$PATRON" SALIDA.json   (si imprime algo, reemplazar por un marcador y crear la propia en n8n)
PATRON='(Bearer +[A-Za-z0-9._-]{20,}|pplx-[A-Za-z0-9]{10,}|apify_[a-z]+_[A-Za-z0-9]{10,}|glpat-[A-Za-z0-9_-]{10,}|AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9]{20,}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,})'
```
   Los marcadores tipo `YOUR_TOKEN` también salen en la búsqueda (empiezan con `Bearer`): no son claves, solo hay que reemplazarlos al configurar.
5. **Adaptar** a lo que el usuario necesita (nodos, textos, destinos). Seguir las skills `n8n-workflow-patterns`, `n8n-node-configuration` y `n8n-error-handling`.
6. **Validar** con `n8n-validation-expert` y `n8n-mcp-tools-expert` si hay acceso a n8n-mcp; si no, importar en n8n y revisar los avisos.
7. **Probar con datos inventados**, nunca con datos reales, y con la skill `seguridad-agentes` si el flujo envía mensajes o toca archivos.
8. **Informe:** de qué plantilla salió, qué se cambió, qué credenciales hay que crear y qué falta probar.

## Señales de alerta
- Un flujo con credenciales o direcciones de otra persona.
- Un flujo que se importó activo.
- Una plantilla copiada tal cual para publicarla.
- Un flujo con nodos que ejecutan código o comandos sin revisar qué hacen.

## Verificación
- [ ] El flujo está desactivado y sin credenciales ajenas.
- [ ] Se sabe de qué plantilla salió.
- [ ] Se validó antes de activarlo.
- [ ] Se probó con datos inventados.
