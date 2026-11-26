# Despliegue BOT 03 — HostGator compartido + Render

## Decisión
HostGator compartido se conserva para dominios y DNS. No se ejecuta Streamlit ni Docker en el hosting compartido. La aplicación corre en Render como servicio Docker. La primera publicación es staging, no producción.

## Configuración ya versionada
- `render.yaml` en raíz del repositorio.
- Servicio: `bot03-fc-inmobiliarios-staging`.
- Rama: `feat/bot03-mvp`.
- Dockerfile: `BOT03/Dockerfile`.
- Contexto Docker: raíz del repositorio.
- Health check: `/_stcore/health`.
- Secreto obligatorio: `BOT03_ACCESS_PASSWORD`.

## Pasos que debe completar el propietario de la cuenta
1. Crear/iniciar sesión en Render: https://render.com/
2. En Render, elegir New > Blueprint.
3. Conectar GitHub y autorizar acceso al repositorio `fcampos293/fcasesorias.cl`.
4. Seleccionar la rama `feat/bot03-mvp` que contiene este `render.yaml`.
5. Revisar que el servicio detectado sea `bot03-fc-inmobiliarios-staging`, runtime Docker, región Oregon y plan Free.
6. Cuando Render solicite el valor de `BOT03_ACCESS_PASSWORD`, crear una contraseña fuerte y única. Guardarla en un gestor de contraseñas; no enviarla por chat ni subirla a GitHub.
7. Revisar costos/condiciones que Render muestre en la confirmación y pulsar Deploy Blueprint.
8. Esperar el build y el health check. Abrir la URL `onrender.com` asignada y comprobar la pantalla de contraseña.
9. Ingresar y probar con los datos DEMO (marcados como ficticios). Probar también carga de CSV.
10. Reportar el resultado del deploy y cualquier log de error sin compartir secretos.

## Límites de esta etapa
- Plan Free solo para pruebas; puede suspenderse por inactividad y tener límites de recursos.
- No hay base de datos persistente. No usar información personal ni expedientes de clientes.
- Los comparables cargados son temporales y no se guardan en una base central.
- La contraseña compartida es una barrera de staging, no un sistema multiusuario/roles apto para producción.
- No se ha conectado dominio propio ni cambiado DNS.
- No se deben publicar informes con datos reales hasta completar controles de privacidad y seguridad.

## Paso posterior para producción
Aprobar presupuesto y servicio estable; añadir PostgreSQL/PostGIS, autenticación individual, autorización por rol, auditoría, backups, observabilidad, política de retención y revisión de seguridad. Solo entonces configurar un subdominio propio y HTTPS.
