# Pruebas y liberación

## Resultados observados en esta ejecución

Entorno de pruebas local: `.venv`, base de pruebas SQLite, `manage.py test`. Ejecución actual: **143 pruebas aprobadas**, 2.432 s, `OK`; Django reportó cero incidencias del system check. GitHub Actions para HEAD `600a5be0b9819956d5d50bb3d2a06c1dd7b7e25f` pasó en los runs `45517869306` y `45517879097`. No se afirma cobertura local de esta ejecución.

- Neon Production: migraciones aplicadas; `migrate --check` pasó. La conexión de solo lectura confirmó `DATABASE=connected`, `ENGINE=postgresql`, `VACANTES=12`. `poblar_demo` reportó 10 carreras, 24 habilidades, 5 empresas y 12 vacantes.
- Vercel Production deployment `dpl_DBJsJESKVoF6TGDwwyARbSmJY7i7` quedó `READY` desde `main@381ce42`. Solicitudes anónimas sin cookies al alias estable dieron `200` en `/`, `/health/`, `/ready/`, `/vacantes/`, `/api/v1/vacantes/`, `/api/v1/docs/`, `/cuentas/login/` y `/cuentas/registro/`. `/ready/` devolvió `database: available`; `/vacantes/` mostró 10 resultados; API devolvió 10 objetos; Swagger renderizó las operaciones.
- `/api/v1/` raíz respondió `404` porque no hay ruta de índice configurada; no impide el uso de endpoints específicos. El token endpoint respondió `405` a GET, que corresponde al método esperado; no se envió POST ni se probó una contraseña real. Login/registro fueron comprobados como páginas GET y los flujos de autenticación están cubiertos por los 143 tests locales y CI.
- `vercel curl` al deployment id devolvió redirección SSO, pero Python urllib sin cookies y una sesión nueva de navegador obtuvieron las páginas públicas del alias estable; no hace falta desactivar Deployment Protection.
- TLS probado con handshake Python `ssl`: TLS 1.3, wildcard `*.vercel.app`, Google Trust Services WR1, válido hasta 2027-01-29.
- Docker Engine/Compose no está instalado (`docker: command not found`). El script de balanceador intentó 20 peticiones a `127.0.0.1:8080` y obtuvo 20 `URLError`; no hubo instancias en ese endpoint. Por ello no se verificaron build, contenedores, Round Robin, failover ni persistencia local.
- `SECRET_KEY` aparece en Vercel Production como Secret oculto. El CLI no lo descargó y el proceso local recibió `SECRET_KEY_PRESENT=False`; esto es una limitación de `env run` para Secrets, no ausencia en runtime. Las páginas y endpoints Django de Production ejecutaron exitosamente. No se mostró ni cambió el contenido; la conexión de diagnóstico a Neon usó una clave efímera solo local.

## Verificación local

```sh
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py test

docker compose config
docker compose build
docker compose up -d --build
docker compose ps
python scripts/probar_balanceador.py --requests 20
docker compose stop app1
python scripts/probar_balanceador.py --requests 20
docker compose start app1
```

El script reporta el número de respuestas, fallos, instancias vistas y latencia media/máxima observada en esa ejecución. La prueba de failover puede revelar errores durante la detección del backend caído; conserva la salida real junto con la fecha/entorno.

## Integración continua

`.github/workflows/tests.yml` ejecuta las comprobaciones Django y pruebas con PostgreSQL administrado como servicio efímero del runner. `SECURE_SSL_REDIRECT=False` solo en este job evita redirecciones que invalidan el cliente de tests; no modifica los ajustes de producción. `check --deploy` usa valores de test, no secretos productivos. Confirma el estado del workflow más reciente antes de liberar.

## Matriz de aceptación

| Caso | Verificación | Resultado observado |
| --- | --- | --- |
| Liveness y readiness en Production | `/health/` y `/ready/` sin cookies | Ambos dieron `200`; readiness informó `database: available` |
| API, roles, autenticación, vacantes | `python manage.py test`, GitHub Actions y GET público | 143 pruebas locales OK; CI `45519292178` pasó para `381ce42`; GET de API y Swagger verificados |
| Neon Production | conexión Django de solo lectura; `migrate --check` | PostgreSQL conectado, 12 vacantes y cero migraciones pendientes |
| Compose válido | `docker compose config` | No ejecutado: Docker/Compose no está instalado |
| Dos instancias | Script a través de Nginx | No ejecutado; la tentativa a localhost:8080 terminó con 20 `URLError` |
| Caída de una app | detener app1, repetir solicitudes | No ejecutado: Docker no está disponible |
| TLS y acceso público | handshake TLS y solicitud anónima | TLS 1.3 válido; alias estable sirve la aplicación sin autenticación Vercel |
| Concurrencia | carga moderada contra Compose | No ejecutado; no se inventan resultados |
