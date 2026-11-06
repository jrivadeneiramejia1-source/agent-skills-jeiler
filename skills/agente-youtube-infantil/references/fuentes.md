# Fuentes (consultadas el 2026-11-06 salvo que se diga otra cosa)

| Dato | Fuente |
|---|---|
| Cupos: `search.list` y `videos.insert` con tope propio de 100 llamadas/día; 10.000 unidades para el resto; subida máx. 256 GB; las subidas de proyectos no verificados **no** están restringidas a privado | developers.google.com/youtube/v3/determine_quota_cost y /docs/videos/insert |
| Funciones que un video «para niños» pierde | support.google.com/youtube/answer/9527654 |
| Programa de Socios: 1.000 suscriptores + 4.000 horas, o 10 millones de vistas de Shorts en 90 días | support.google.com/youtube/answer/72851 |
| «Contenido no auténtico» (antes «contenido repetitivo»), julio de 2025 | support.google.com/youtube/answer/1311392 |
| Declarar contenido alterado o con IA que parece real; lo irreal no | support.google.com/youtube/answer/14328491 |
| Permiso (refresh token) de 7 días con app «Testing» y tipo Externo | developers.google.com/identity/protocols/oauth2 |
| Campos de los nodos YouTube y Telegram (`sendAndWait`), carpeta `~/.n8n-files`, `N8N_WEBHOOK_URL` | código fuente de n8n 2.46.6 (licencia «Sustainable Use», de código visible, no es de las abiertas de la lista; **no se copió nada**: solo se leyeron nombres de campos) y docs.n8n.io |
| ngrok | ngrok.com (n8n no documenta ngrok; los pasos del túnel son prácticos **[P]**) |

Herramientas usadas y no copiadas al repo: n8n 2.46.6 (instalado aparte para importar y validar), Node.js 24, ver también `FUENTES.md` de la raíz.
