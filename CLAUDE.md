# Reglas para trabajar en este repo (es público)
- **Nada de datos de personas ni de clientes:** ni nombres, teléfonos, correos, cédulas ni capturas de chats. Los ejemplos son inventados.
- **Nunca pedir ni guardar claves, tokens ni contraseñas.** Los flujos de n8n que se suban al repo van sin credenciales, sin `pinData` (datos de prueba guardados) y sin URL de webhook reales.
- Archivos de comunidades indígenas: no se modifican ni se suben a servicios externos.
- Nada que gaste plata o créditos sin el «sí» de Jeiler y una estimación del costo.
- Nada se publica solo; **nunca a `main` directo** (rama y PR; Jeiler dice «sí» antes de unir).
- Antes de copiar algo de terceros: licencia abierta (MIT, Apache-2.0, BSD, CC0…), revisión de seguridad (`SEGURIDAD.md`) y su licencia en `third-party/`.
- Cada regla de una guía lleva una marca: **[F]** fuente abierta citada, **[P]** regla práctica sin verificar, **[E]** hecha y medida aquí.
- Un revisor automático se prueba siempre con un ejemplo bueno y uno malo hecho a propósito. Pruebas: `python -I -m unittest discover -s tests`.
- Responder a Jeiler en español simple y decir siempre qué quedó sin probar.

## Estructura
- `skills/<nombre>/SKILL.md`: una skill. Las de terceros y las heredadas de Vercel no se editan; las originales están listadas en `FUENTES.md`.
- `grupos.conf`: qué skills instala cada grupo. `instalar.sh`: copia las skills.
- `INDICE-DE-SKILLS.md`: cuándo usar cada skill. `PRUEBAS.md`: qué se probó. `LECCIONES.md`: errores aprendidos.
- `docs/`: documentos heredados de Vercel (cómo crear una skill, README original).
