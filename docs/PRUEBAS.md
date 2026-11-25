# Pruebas y liberación

## Resultados observados en esta ejecución

Entorno de pruebas local: `.venv`, base de pruebas SQLite, `manage.py test`. Ejecución actual: **143 pruebas aprobadas**, 2.432 s, `OK`; Django reportó cero incidencias del system check. GitHub Actions para HEAD `600a5be0b9819956d5d50bb3d2a06c1dd7b7e25f` pasó en los runs `45517869306` y `45517879097`. No se afirma cobertura local de esta ejecución.

- Neon Production: migraciones aplicadas; `migrate --check` pasó. La conexión de solo lectura confirmó `DATABASE=connected`, `ENGINE=postgresql`, `VACANTES=12`. `poblar_demo` reportó 10 carreras, 24 habilidades, 5 empresas y 12 vacantes.
- Vercel reporta Production deployment `READY` desde commit anterior `3f58298`; no es el HEAD actual. El dominio `.vercel.app` respondió `302` a SSO para las solicitudes externas, así que no se pudo verificar `/`, `/health/`, `/ready/`, `/vacantes/`, API, Swagger, login ni registro desde el runtime a través de su URL.
- Los runtime logs previos a las migraciones muestran `500` en `/` por tabla de vacantes inexistente. Tras migrar no se logró una petición al runtime porque la capa SSO interceptó la solicitud. El estado de rutas del runtime sigue **pendiente**, no se infiere a partir de los tests o del acceso directo a Neon.
- TLS probado con handshake Python `ssl`: TLS 1.3, wildcard `*.vercel.app`, Google Trust Services WR1, válido hasta 2027-01-29.
- Docker Engine/Compose no está instalado (`docker: command not found`). El script de balanceador intentó 20 peticiones a `127.0.0.1:8080` y obtuvo 20 `URLError`; no hubo instancias en ese endpoint. Por ello no se verificaron build, contenedores, Round Robin, failover ni persistencia local.
- `SECRET_KEY` aparece en Vercel Production como Secret oculto. El CLI deliberadamente no lo descargó y el proceso local recibió `SECRET_KEY_PRESENT=False`; la configuración de Vercel confirma que el secreto está asociado al entorno. No se mostró ni cambió su contenido. En el acceso de diagnóstico a Neon se empleó una clave efímera solo local.

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
| Liveness y readiness en Production | `/health/` y `/ready/` desde una sesión anónima | No verificados: SSO responde `302` antes de llegar a Django |
| API, roles, autenticación, vacantes | `python manage.py test` y GitHub Actions | 143 pruebas locales OK; los dos runs de CI para `600a5be` pasaron; no equivale a prueba del runtime |
| Neon Production | conexión Django de solo lectura; `migrate --check` | PostgreSQL conectado, 12 vacantes y cero migraciones pendientes |
| Compose válido | `docker compose config` | No ejecutado: Docker/Compose no está instalado |
| Dos instancias | Script a través de Nginx | No ejecutado; la tentativa a localhost:8080 terminó con 20 `URLError` |
| Caída de una app | detener app1, repetir solicitudes | No ejecutado: Docker no está disponible |
| TLS y acceso público | handshake TLS y solicitud anónima | TLS 1.3 válido; acceso anónimo bloqueado por SSO; falta un dominio personalizado propio |
| Concurrencia | carga moderada contra Compose | No ejecutado; no se inventan resultados |
