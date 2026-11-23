# Checklist de despliegue — infraestructura existente

Antes de publicar, confirmar en el panel del proveedor de hosting:

1. ¿Es hosting compartido, VPS o servidor dedicado?
2. ¿Permite Docker y contenedores?
3. ¿Permite procesos persistentes Python/Streamlit?
4. ¿Se puede abrir/proxyar el puerto interno 8501 detrás de HTTPS?
5. ¿Permite configurar subdominio y DNS?
6. ¿Hay PostgreSQL disponible? ¿PostGIS?
7. ¿Hay SSH y despliegue desde GitHub?
8. ¿Qué límites de CPU, RAM, almacenamiento y procesos aplican?

## Si es VPS/dedicado con Docker
- Crear usuario de sistema no privilegiado.
- Instalar Docker y Compose.
- Clonar repositorio.
- Construir imagen desde BOT03/Dockerfile.
- Publicar solo detrás de proxy HTTPS (Nginx/Caddy).
- Activar firewall; no exponer puerto 8501 directamente a Internet.
- Configurar backups y monitoreo.
- Configurar subdominio solo después de confirmar el dominio disponible.

## Si es hosting compartido sin procesos persistentes/Docker
No se debe intentar forzar Streamlit allí. Mantener el dominio/DNS en el hosting actual y alojar la aplicación en un entorno compatible, o solicitar upgrade a VPS. No cambiar DNS ni contratar servicios sin autorización del propietario.

## Seguridad
No subir claves de APIs ni datos de clientes al repositorio. Configurar secretos en el entorno de ejecución.
