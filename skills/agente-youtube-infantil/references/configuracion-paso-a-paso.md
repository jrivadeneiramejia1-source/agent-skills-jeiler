# Puesta en marcha paso a paso (n8n en tu computador + ngrok)

Marcas: **[F]** dato de una fuente oficial (ver `fuentes.md`), **[P]** regla práctica sin verificar, **[E]** hecho y medido aquí.
Regla de oro: **ninguna clave, token ni contraseña se pega en un chat, en un flujo ni en el repo.** Solo en las credenciales de n8n. **[P]**
Los ejemplos usan Windows (`C:\Users\...`). Si usas Mac o Linux, cambia las rutas (la de `BASE` en el nodo «Solo tu chat y /subir N»).

## 1. n8n y ngrok (primero, porque Telegram y los botones necesitan una dirección pública con https)
1. n8n hoy exige **Node.js 24 o más nuevo** (la versión 2.46.6 no arranca con Node 22). **[E]** Instálalo desde nodejs.org y abre una terminal nueva.
2. Instala ngrok (ngrok.com, cuenta gratis) y pon tu *authtoken* con el comando que ngrok te muestra. **Ese token es tuyo: no me lo pases.** Abre el túnel: `ngrok http 5678`. Te muestra una dirección `https://algo.ngrok-free.app`. **[P]** En el plan gratis esa dirección puede cambiar cada vez que reinicias ngrok; si cambia, hay que repetir el paso.
3. En **otra** terminal, dile a n8n cuál es su dirección pública y arráncalo (PowerShell):
   ```
   $env:N8N_WEBHOOK_URL="https://algo.ngrok-free.app/"
   npx n8n
   ```
   `N8N_WEBHOOK_URL` es el nombre vigente (la antigua `WEBHOOK_URL` está en desuso). **[E]** Sin esto, n8n le da a Telegram una dirección `localhost` que no existe desde fuera.
4. Abre n8n en `http://localhost:5678` y crea tu cuenta de dueño.
5. Mientras uses el subidor, **n8n y ngrok deben estar abiertos**. Si apagas el computador, el agente no responde. **[P]**

## 2. Telegram (el control remoto)
1. En Telegram busca **@BotFather** → `/newbot` → pon un nombre y un usuario que termine en `bot`. Te da un *token* (una clave larga). **[P]**
2. En n8n: Credentials (Credenciales) → New → **Telegram API** → pega el token → nómbrala `Telegram (mi bot)`. El token solo vive ahí.
3. Escríbele «hola» a tu bot desde tu cuenta.

## 3. Google (YouTube)
Se necesitan **dos** credenciales distintas: una *clave de API* para buscar (gratis, solo lee) y un *OAuth* para subir (acceso a tu canal).
1. console.cloud.google.com → proyecto nuevo → «APIs y servicios» → Biblioteca → **YouTube Data API v3** → Habilitar.
2. Credenciales → Crear → **Clave de API** → «Restringir clave» → solo YouTube Data API v3.
3. En n8n: Credentials → New → **Query Auth** (autenticación por parámetro en la dirección). Name: `key`. Value: tu clave. Nómbrala `Clave de la API de YouTube`.
4. Pantalla de consentimiento OAuth → tipo **Externo** → agrega tu correo como «usuario de prueba».
5. Credenciales → Crear → **ID de cliente de OAuth** → «Aplicación web». En n8n: Credentials → New → **YouTube OAuth2 API**: n8n te muestra una «OAuth Redirect URL»; cópiala tal cual en «URI de redireccionamiento autorizados» de Google. Copia el ID y el secreto de cliente a n8n y pulsa «Sign in with Google».
6. **[F]** Mientras la app esté en estado «Testing» (prueba) y sea «Externo», el permiso se vence a los **7 días** y hay que volver a conectar la credencial. Pasar la app a «En producción» evita el vencimiento, pero muestra el aviso de «app no verificada»: **[P]** no lo probé.
7. **[F]** Cupos (consultados el 2026-11-06): `search.list` y `videos.insert` tienen cada uno un tope propio de 100 llamadas por día; lo demás comparte 10.000 unidades diarias. El investigador hace 12 búsquedas por ejecución, así que **una ejecución al día** cabe de sobra. Confirma los números en tu consola de Google Cloud.

## 4. Las carpetas 1, 2 y 3
n8n 2.x solo deja leer archivos dentro de `C:\Users\TU-USUARIO\.n8n-files` por defecto. **[E]** (`N8N_RESTRICT_FILE_ACCESS_TO`). Crea:
```
C:\Users\TU-USUARIO\.n8n-files\opciones\1\video.mp4
C:\Users\TU-USUARIO\.n8n-files\opciones\1\publicacion.json
(igual para 2 y 3)
```
`publicacion.json` (ejemplo inventado):
```json
{
  "titulo": "El patito feliz - canción infantil (prueba)",
  "descripcion": "Canción infantil original para pruebas.\nLetra, música y animación: propias.",
  "etiquetas": ["canciones infantiles", "patito", "para niños"]
}
```
Máximos que revisa el código **[P]** (límites de YouTube, no los verifiqué hoy; el código deja margen): título 100 caracteres, descripción 4.800 bytes, etiquetas 450 caracteres en total. Lo de «privado», «para niños», categoría y idioma **no** se escribe aquí: lo fija el código. **[E]**
Si el video tiene voces o imágenes **realistas** hechas con IA, dilo en la descripción y marca la opción de contenido alterado en YouTube Studio. **[F]** (lo animado y claramente irreal no lo exige).

## 5. Importar y conectar
1. En n8n: Workflows → ⋯ → **Import from file** → los tres de `plantillas/`.
2. En cada nodo que pida credencial (aparece con un aviso), elige la tuya: Telegram, clave de YouTube, YouTube OAuth2.
3. Cambia **tu número de chat** donde diga `REEMPLAZA-CON-TU-CHAT-ID`: nodo «Configuración» (investigador), «Solo tu chat y /subir N» (subidor, y ahí mismo la carpeta `BASE`) y «Mensaje de error». Cómo saber tu número: en el subidor, abre «Telegram Trigger» → «Listen for test event» → escríbele al bot → en la salida mira `message.chat.id`.
4. En el investigador y en el subidor: Settings (Ajustes) → **Error workflow** → «Avisar por Telegram cuando falla un flujo».
5. Antes de activar, revisa con el revisor (comando en `SKILL.md`): debe decir «Sin hallazgos».

## 6. Probar sin riesgo
1. **Investigador:** botón «Probar a mano» (Execute workflow). Debe llegarte un Telegram. Si no hay virales, te lo dice.
2. **Subidor:** pon un video falso de 5 segundos en la carpeta 1, activa el flujo y escribe `/subir 1`.
3. En YouTube Studio comprueba: **Privado**, **«Sí, es para niños»**, sin avisar a suscriptores. Luego pulsa ✅ **Publicar** o ❌ **Dejar privado** en el mensaje de Telegram.
4. Si pasas más de 24 horas sin contestar, el video debería quedar en privado: la expresión solo publica con `approved === true`. **[P]** No probé qué entrega n8n al vencerse el plazo.
5. Si algo falla, el aviso te llega por Telegram y el video **no** se publica.

## Qué no está verificado
Subida real a YouTube, llamadas reales a Google, Telegram real, ngrok y Windows. Corre primero con el video falso. Si algo sale distinto, pásame el texto del error (nunca la clave).
