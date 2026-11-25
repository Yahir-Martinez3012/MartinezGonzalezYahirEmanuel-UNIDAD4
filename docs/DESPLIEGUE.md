# Despliegue

## Docker local

1. Instala Docker Engine y el plugin Docker Compose.
2. En la raíz, copia `.env.example` a `.env` y cambia `SECRET_KEY` y `POSTGRES_PASSWORD` por valores aleatorios. Para generar secretos no reutilices las cuentas demo.
3. Ejecuta `docker compose config`, luego `docker compose up -d --build`.
4. Revisa `docker compose ps`, `docker compose logs migrate app1 app2 nginx` y abre `http://localhost:8080/`.
5. Nginx sirve estáticos desde el volumen de `collectstatic`; PostgreSQL conserva datos en `postgres_data`.
6. Carga datos de demostración opcionales con `docker compose exec app1 python manage.py poblar_demo` (con `--usuarios` solo en entorno de prueba).
7. Ejecuta `python scripts/probar_balanceador.py`. Para simular la pérdida de un backend: `docker compose stop app1`, repite el script (puede observarse un fallo durante la detección), revisa la respuesta de `/ready/` y restáuralo con `docker compose start app1`.
8. Para limpiar el stack sin borrar información, `docker compose down`; **no** agregues `-v` si quieres conservar la base local.

Compose usa un secreto fuerte requerido al levantar el servicio, sin valor predeterminado compartido. Las credenciales mostradas en `.env.example` son marcadores y no deben copiarse como secretos de producción.

## Vercel + Neon

Vercel detecta Django desde `manage.py` y `config.wsgi`; el runtime de producción es administrado. Docker Compose, PostgreSQL local y Nginx son una infraestructura reproducible separada y **no** se ejecutan en Vercel. El proyecto Vercel existente es `despliegue-docker-conecta-utc` (`prj_wyBdQZlH6Aep8W3VC6q7else6Nk5`) y las variables de Neon están asociadas a Production, Preview y Development. No se modifica el servicio original de Render.

### Estado comprobado (24 de noviembre de 2026)

- Despliegue Vercel `dpl_EhpyG2oFF4TdF7LuWv4iHt5BEuPD`, estado `READY`, desde `v0/unidad4-infrastructure`, commit `3f58298ebaff24dbf686f1d7044129551a36f321`.
- URL del proyecto: <https://despliegue-docker-conecta-utc.vercel.app>. También se asignó TLS 1.3 con certificado `*.vercel.app`, válido hasta el 29 de enero de 2027.
- Protección del proyecto: SSO para todos los dominios excepto dominios personalizados; no se encontró ningún dominio personalizado conectado. Por ello esta URL no es pública para visitantes anónimos. No se desactivó la protección.
- Las comprobaciones autenticadas por CLI de `/health/` y `/ready/` respondieron `200`; `/ready/` confirmó acceso a la base. El `showmigrations --plan` de Production mostró todas las migraciones de Django sin aplicar. La raíz respondió `500` antes de aplicar esas migraciones; la carga de datos demo tampoco se ha ejecutado en producción.
- GitHub `main` aún apunta a `287f468dfcba8ba55e552797933345f48c87f5ac`; los cambios están en la rama de trabajo hasta que se integre su pull request.

Para hacer pública la app manteniendo SSO en previews, se necesita asociar a este proyecto un dominio personalizado que controles (Vercel excluye esos dominios de la protección actual). No se debe inventar ni registrar un dominio ajeno. Una vez asociado, valida el certificado y las rutas `/`, `/health/`, `/ready/`, `/vacantes/`, `/api/v1/`, `/api/v1/docs/` y `/admin/` desde un navegador no autenticado.

Una vez autorizado el cambio de producción, aplicar `python manage.py migrate --noinput` y después `python manage.py poblar_demo` mediante un proceso único conectado al `DATABASE_URL` de Production. El comando de demo es idempotente y sin `--usuarios` crea usuarios de empresa con contraseña inutilizable; no crea credenciales débiles de acceso. No ejecutar `--usuarios` en producción. No apuntar migraciones al PostgreSQL de Render de Unidad 3 ni hacer que cada instancia web migre en paralelo.

## Variables

| Variable | Obligatoria | Propósito |
| --- | --- | --- |
| `SECRET_KEY` | Sí | Firma Django; fuera de código y Git |
| `DEBUG` | Sí en producción | Siempre `False` |
| `DATABASE_URL` | Sí en producción | PostgreSQL gestionado; TLS por proveedor |
| `ALLOWED_HOSTS` | Sí | Hosts exactos aceptados por Django |
| `CSRF_TRUSTED_ORIGINS` | Sí | Orígenes HTTPS del dominio publicado |
| `POSTGRES_PASSWORD` | Docker local | Credencial de la instancia local |
| `RECAPTCHA_*`, `RESEND_API_KEY` | Opcionales | Solo activar con credenciales válidas |

No se ha conectado ni desplegado Vercel desde esta operación: el chat no estaba vinculado a un proyecto Vercel. La importación GitHub y el servicio Neon conectados por sí solos no crean dominio ni permiten afirmar que el sitio está en línea.
