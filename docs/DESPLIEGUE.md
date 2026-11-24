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

Vercel soporta detección/despliegue Django desde `manage.py` y la configuración WSGI; el archivo `vercel.json` no es necesario para la configuración predeterminada. En producción, el runtime es administrado: Docker Compose, PostgreSQL local y Nginx no se ejecutan en Vercel. Los certificados HTTPS del dominio asignado son administrados por Vercel.

Para habilitar producción: en Vercel importa `Yahir-Martinez3012/MartinezGonzalezYahirEmanuel-UNIDAD4`, selecciona raíz del proyecto y conecta Neon mediante la integración. Configura `SECRET_KEY` (secreto aleatorio), `DEBUG=False`, `DATABASE_URL` (Neon, con TLS/`sslmode=require`), `ALLOWED_HOSTS` con el host asignado y `CSRF_TRUSTED_ORIGINS` con su origen HTTPS. Habilita las variables en Production y Preview según corresponda. Deja que Vercel detecte Django y su comando de build; revisa los logs antes de cambiar comandos.

Después de crear/importar el proyecto, añade el dominio `conecta-utc-unidad4.vercel.app` solo si Vercel confirma disponibilidad; en caso contrario elige el dominio disponible que Vercel ofrezca. No se ha configurado ni comprobado ese dominio desde esta rama. Al asignarlo, espera a que Vercel indique certificado válido y prueba `/`, `/health/`, `/ready/`, `/vacantes/`, `/api/v1/`, `/api/v1/docs/` y `/admin/`.

Ejecuta migraciones de Django como una operación controlada sobre la base de Unidad 4, una vez confirmada la conexión y el destino. No apuntes migraciones al PostgreSQL de Render de Unidad 3. Para nuevos despliegues, integra un paso previo de migración único; no hagas que cada instancia web migre en paralelo.

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
