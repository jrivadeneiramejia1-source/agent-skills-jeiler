# Reglas nuevas del revisor de flujos (F12–F14)

Las corre `skills/revisar-flujo-n8n/scripts/revisar_flujo.py` sobre cualquier flujo exportado. Solo miran los nodos **YouTube** con recurso «video» y operación «upload» o «update». **[E]** (con pruebas de un flujo bueno y uno malo hecho a propósito).

| Regla | Gravedad | Qué avisa |
|---|---|---|
| **F12** | ALTA | La subida no fija `privacyStatus` o lo pone en `public`. |
| **F12** | MEDIA | `unlisted` (lo ve quien tenga el enlace) o la privacidad sale de una expresión. |
| **F13** | MEDIA | La subida, o el paso a público, no declara `selfDeclaredMadeForKids`. |
| **F14** | ALTA | Un nodo que pone el video en `public` puede alcanzarse sin pasar por una aprobación (`sendAndWait` y luego un IF), o existe un camino desde un disparador que se la salta. |

## Límites (decirlo claro)
- F14 mira la **forma** del flujo: que haya aprobación y un IF en el camino. **No lee qué compara el IF.** Léelo a mano. **[E]**
- F13 solo ve el campo en el nodo; si lo pones en `false` a propósito, no avisa.
- Que no haya hallazgos no prueba que el flujo sea seguro: solo busca patrones conocidos. **[P]**
- Ejemplo malo: `ejemplos/flujo-youtube-malo.json` (sale con F04, F12, F13 y F14). Ejemplo con nodos que n8n rechaza: `ejemplos/flujo-nodos-invalidos.json`.

## Comprobar que n8n acepta los nodos
`scripts/comprobar_con_n8n.mjs` usa el código de n8n instalado para ver que el tipo, la versión y los campos obligatorios existen. **No** detecta un valor de lista inventado (por ejemplo `privacyStatus: "secreto"`): para eso está F12. Necesita n8n instalado aparte y Node 24:
```
node scripts\comprobar_con_n8n.mjs CARPETA-DONDE-INSTALASTE-n8n plantillas\subir-youtube.json
```
(la carpeta es donde corriste `npm install n8n@2.46.6`; si `isolated-vm` falla, `npm rebuild isolated-vm` con Node 24). Con `N8N_CARPETA` definida, las pruebas del repo también lo corren.
