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

### Estado comprobado (24–25 de noviembre de 2026)

- Proyecto Vercel `despliegue-docker-conecta-utc`, ID `prj_wyBdQZlH6Aep8W3VC6q7else6Nk5`. El último deployment de Production observado antes de fusionar el PR fue `dpl_EhpyG2oFF4TdF7LuWv4iHt5BEuPD`, `READY`, originado desde `v0/unidad4-infrastructure` en `3f58298`; por tanto no representa todavía el HEAD actual de la rama.
- URL estable asignada: <https://despliegue-docker-conecta-utc.vercel.app>. TLS negociado: TLS 1.3; certificado `*.vercel.app`, emisor Google Trust Services WR1, fecha de expiración 29 de enero de 2027.
- Deployment Protection aplica SSO a los dominios `.vercel.app`; el intento anónimo responde `302` a Vercel SSO. No hay dominio personalizado registrado y no se desactivó la protección. Las rutas de aplicación no se pudieron verificar públicamente bajo esta restricción.
- Neon Production: `migrate --noinput` terminó correctamente; `poblar_demo` informó 10 carreras, 24 habilidades, 5 empresas y 12 vacantes. Una conexión de solo lectura usando el entorno Production confirmó `ENGINE=postgresql`, 12 filas de vacantes y `migrate --check` sin migraciones pendientes. Esto verifica el acceso de esta sesión a Neon; las rutas del runtime quedan sin verificación mientras SSO intercepta el tráfico.
- Los logs anteriores a la migración registraron `500` en `/` por ausencia de `vacantes_vacante`; la tabla ya fue creada por las migraciones. No se hizo una petición de aplicación posterior porque SSO detuvo la prueba.
- La rama `v0/unidad4-infrastructure` (`600a5be`) tiene GitHub Actions en verde y el PR #1 hacia `main` está limpio y fusionable. La producción debe reconstruirse desde `main` después de la fusión; confirme el deployment resultante en Vercel.
- `SECRET_KEY` figura en las variables Production como tipo Secret/oculto. Vercel no permite descargar ese secreto mediante `env run`, de ahí la advertencia local; su ausencia en la shell local no significa que falte en el runtime. No se imprimió, regeneró ni modificó su valor. Para operaciones locales solo se empleó una clave efímera no secreta.
- Docker Engine/Compose no está instalado en el entorno de trabajo (`docker: command not found`); no se simularon contenedores ni resultados de balanceo.

#### Publicar sin Vercel SSO en la aplicación

No desactive Deployment Protection globalmente. Desde el panel Vercel, abra el proyecto `despliegue-docker-conecta-utc` → **Settings → Domains → Add** y agregue un dominio propio que controle. Configure en el registrador los registros DNS que Vercel indique; espere a que el dominio figure como verificado y el certificado TLS como activo. Mantenga protegidos los previews y el hostname `.vercel.app`; con la configuración actual, los dominios personalizados se excluyen de SSO. Compruebe después las páginas y API con una ventana privada, sin sesión de Vercel. Si el proyecto no excluye automáticamente el dominio personalizado, ajuste el alcance de Deployment Protection solo para ese dominio, manteniendo protegidos los previews. La autenticación de usuarios de Django permanece independiente.

No puedo asignar un dominio público final sin que el propietario proporcione uno que controle y configure sus DNS. No registre un dominio ajeno ni incurra en compra/servicio pagado; puede usar uno existente o un dominio gratuito disponible bajo su cuenta.

#### Operaciones de Neon ya realizadas

Las migraciones se ejecutaron una vez contra el `DATABASE_URL` de Production y el seed se ejecutó sin `--usuarios`. No vuelva a apuntar esos comandos a Render (Unidad 3), no active `--usuarios` en producción y no ejecute migraciones desde cada instancia web.

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
