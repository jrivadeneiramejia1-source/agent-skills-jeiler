---
name: agente-youtube-infantil
description: Flujos de n8n para un canal de videos infantiles en español en YouTube, con el dueño siempre al mando. Trae un investigador que cada día manda por Telegram los videos infantiles que superaron el promedio de su canal (últimos 3, 7 y 30 días), y un subidor que, con «/subir 1|2|3», sube el video de esa carpeta en PRIVADO y marcado «para niños» y solo lo hace público si se pulsa «Publicar». Incluye el código de cada nodo, plantillas listas para importar, un revisor con reglas nuevas (F12-F14) y pruebas. Usar al montar o revisar un agente que sube videos a YouTube, o al buscar ideas de videos infantiles sin copiar.
---

# Agente de videos infantiles para YouTube (n8n)

Hace dos cosas, y nada más, **sin gastar dinero** (solo servicios gratis):
1. **Investigador** (`plantillas/investigador-virales.json`): cada día busca videos infantiles en español y te manda por Telegram los que ganaron al promedio de su propio canal. Sirve para aprender la fórmula, **no** para copiar.
2. **Subidor** (`plantillas/subir-youtube.json`): escribes `/subir 1`, `/subir 2` o `/subir 3` a tu bot. Lee `publicacion.json` y `video.mp4` de esa carpeta, lo sube a YouTube **privado** y te pregunta «¿Lo publico?». Solo si pulsas ✅ pasa a público.
3. **Aviso de errores** (`plantillas/avisar-error.json`): si un flujo falla, te llega un Telegram.

Todavía **no** crea los videos (fase C) ni mira estadísticas o TikTok (fase D).

## Reglas que no se negocian
- Nada se publica solo: la subida es privada y el paso a público pasa por un botón en Telegram. **[E]** el revisor lo comprueba (F12, F14) y hay pruebas.
- «Para niños» y «privado» los **fija el código**, no un archivo ni una IA. Aunque `publicacion.json` diga otra cosa, se ignora. **[E]**
- Solo obedece a **tu** chat de Telegram (el bot es público: cualquiera puede escribirle). **[E]**
- Nunca pedir ni guardar claves, tokens ni contraseñas: van en las credenciales de n8n, nunca en el chat, en un flujo ni en el repo. **[P]**
- Originalidad: del investigador se aprende la **fórmula** (tema, gancho, estructura), nunca se copian personajes, guion, imágenes ni música. Ver `references/formula-videos-infantiles.md`.

## Cómo empezar
Sigue `references/configuracion-paso-a-paso.md` (Telegram, Google, n8n en tu computador con ngrok, importar, probar con un video falso).

## Revisar antes de activar
```
python -I skills\revisar-flujo-n8n\scripts\revisar_flujo.py skills\agente-youtube-infantil\plantillas\subir-youtube.json
```
Reglas nuevas del revisor (ver `references/reglas.md`): **F12** subida sin `privacyStatus` fijo en `private`; **F13** sin declarar «para niños»; **F14** hacer público sin una aprobación en el camino. Prueba con el malo: `ejemplos/flujo-youtube-malo.json` (debe salir con 3 graves).

## Probar el código de un nodo sin abrir n8n
```
node scripts\probar_codigo.mjs codigo\gate_subir.js ENTRADA.json
```
Los nodos «Code» de las plantillas son exactamente los archivos de `codigo/`. Si cambias uno, regenera las plantillas:
```
python -I scripts\generar_plantillas.py
python -I scripts\generar_plantillas.py --comprobar
```
Pruebas del repo: `python -I -m unittest discover -s tests`.

## Qué NO está probado
Una subida real a YouTube, llamadas reales a la API de Google, Telegram real, ngrok y Windows. Sí se probó: el código de cada nodo con datos inventados, la importación y la validación de nodos en n8n 2.46.6, y un nodo «Code» ejecutado dentro de n8n. Detalle en `PRUEBAS.md`.
