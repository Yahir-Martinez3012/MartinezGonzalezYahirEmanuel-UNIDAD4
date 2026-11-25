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

### Estado comprobado (25 de noviembre de 2026)

- Proyecto Vercel `despliegue-docker-conecta-utc`, ID `prj_wyBdQZlH6Aep8W3VC6q7else6Nk5`. El deployment Production `dpl_DBJsJESKVoF6TGDwwyARbSmJY7i7` quedó `READY` desde `main`, commit `381ce4204532c4e4c44663322da72bf1927de5cf`; alias estable: <https://despliegue-docker-conecta-utc.vercel.app>.
- TLS confirmado por handshake externo: TLS 1.3, `*.vercel.app`, Google Trust Services WR1, vence el 29 de enero de 2027.
- Solicitudes anónimas sin cookies a la URL estable dieron `200` en `/`, `/health/`, `/ready/`, `/vacantes/`, `/api/v1/vacantes/`, `/api/v1/docs/`, `/cuentas/login/` y `/cuentas/registro/`. `/ready/` devolvió `database: available`; el listado web muestra 10 vacantes publicadas y 4 empresas. Swagger se renderizó con operaciones. `/api/v1/` como raíz no está definido y responde `404`; los endpoints REST específicos sí funcionan. No se envió formulario de login/registro ni se creó una cuenta de prueba en Production.
- `vercel curl` contra la URL de deployment específica redirigió a SSO; la prueba anónima directa contra el alias estable (Python urllib y navegador aislado, sin cookies) sí cargó Django. No se desactivó Deployment Protection ni hace falta intervención para hacer público el alias actual.
- Neon Production: `migrate --noinput` terminó correctamente; `poblar_demo` sin `--usuarios` informó 10 carreras, 24 habilidades, 5 empresas y 12 vacantes. Una consulta Django de solo lectura confirmó `ENGINE=postgresql`, 12 filas de vacantes y `migrate --check` sin cambios pendientes. Los datos vienen de la base productiva.
- Los logs anteriores a la migración registraron `500` en `/` por ausencia de `vacantes_vacante`; después de migrar, el deployment de `main` cargó y se verificaron las páginas y rutas públicas indicadas.
- PR #1 fusionado; commit de merge `381ce42`. GitHub Actions `45519292178` para `main` terminó `success`.
- `SECRET_KEY` está configurada en Production como Secret oculto. `vercel env run` no la descarga a procesos locales (la prueba mostró `SECRET_KEY_PRESENT=False` en local), pero las páginas Django y endpoints anónimos de Production respondieron, señal de que el runtime ejecuta correctamente con su configuración. No se imprimió, regeneró ni modificó su valor. La advertencia es sobre descarga local deliberadamente restringida, no una configuración incompleta del runtime.
- Docker Engine/Compose no está instalado aquí (`docker: command not found`). El script local de balanceador intentó 20 peticiones a `localhost:8080` y obtuvo 20 `URLError`; no hubo contenedores para balancear.

#### Dominio, acceso público y protección

El alias estable `.vercel.app` ya es accesible anónimamente; no es necesario desactivar SSO global ni contratar/registrar otro dominio. Para comprobarlo de forma reproducible usa una ventana privada o una sesión nueva sin cookies y abre el alias estable. Si se añade un dominio propio en el futuro: **Settings → Domains → Add**, configura los DNS indicados por Vercel y espera `Valid Configuration` y el certificado activo; agrega el hostname exacto a `ALLOWED_HOSTS` y su origen HTTPS a `CSRF_TRUSTED_ORIGINS` en Environment Variables (Production). Mantén los previews protegidos y Django conserva su propia autenticación.

#### Operaciones de Neon realizadas

Las migraciones se ejecutaron una vez contra el `DATABASE_URL` de Production y el seed se ejecutó sin `--usuarios`. No apuntes esos comandos a Render (Unidad 3), no actives `--usuarios` en producción y no ejecutes migraciones desde cada instancia web.

## Variables

| Variable | Obligatoria | Propósito |
| --- | --- | --- |
| `SECRET_KEY` | Sí | Firma Django; fuera de código y Git |
| `DEBUG` | Sí en producción | Siempre `False` |
| `DATABASE_URL` | Sí en producción | PostgreSQL gestionado; TLS por proveedor |
| `ALLOWED_HOSTS` | Para dominios personalizados | Hostnames exactos aceptados por Django; el runtime Vercel añade sus propios hosts asignados |
| `CSRF_TRUSTED_ORIGINS` | Para dominios personalizados | Orígenes HTTPS exactos del dominio propio |
| `POSTGRES_PASSWORD` | Docker local | Credencial de la instancia local |
| `RECAPTCHA_*`, `RESEND_API_KEY` | Opcionales | Solo activar con credenciales válidas |

Vercel ya está conectado y el deployment Production de `main` está `READY`. El alias estable es público; no hace falta dominio personalizado para acceder a la aplicación actual. Para un dominio propio futuro, sigue los pasos anteriores y actualiza `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.
