# Pruebas y liberación

## Resultados observados en esta rama

Entorno: Python 3.13.17, dependencias instaladas en `.venv`, SQLite de pruebas local. Ejecutado el 23 de noviembre de 2026:

- `python manage.py check`: aprobado, sin incidencias.
- `python manage.py makemigrations --check --dry-run`: aprobado, no hay migraciones pendientes de generar.
- `coverage run manage.py test`: **143 pruebas aprobadas**, incluyendo las rutas de salud añadidas.
- `coverage report --fail-under=90`: aprobado, cobertura total **96%**.
- `python manage.py check --deploy`: terminó con código 0 y dos avisos deliberados: `security.W005` (no se afirma que todo subdominio sea HTTPS) y `security.W021` (no se activa preload HSTS para un host todavía no asignado). Sin errores.
- Parseo YAML de `docker-compose.yml` con PyYAML: válido y contiene `db`, `migrate`, `app1`, `app2`, `nginx`.

Docker Engine/Compose no está instalado en este entorno; por ello **no** se ejecutaron `docker compose config/build/up/ps`, PostgreSQL real, balanceo/failover, concurrencia, dominio ni TLS. La comprobación YAML no sustituye `docker compose config`. GitHub Actions está configurado, pero su ejecución remota solo se conocerá tras subir la rama.

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

`.github/workflows/tests.yml` ejecuta las comprobaciones Django y pruebas con PostgreSQL administrado como servicio efímero del runner. La prueba de `check --deploy` usa valores de test del job, no secretos de producción. Verifica estado de Actions y logs antes de liberar.

## Matriz de aceptación

| Caso | Verificación | Resultado en este cambio |
| --- | --- | --- |
| Liveness y readiness | Pruebas Django para `/health/`, `/ready/` | Pendiente de ejecución |
| API, roles, autenticación, vacantes | `python manage.py test` | Pendiente de ejecución |
| Migraciones | `makemigrations --check --dry-run` | Pendiente de ejecución |
| Compose válido | `docker compose config` | Pendiente; requiere Docker disponible |
| Dos instancias | Script a través de Nginx | Pendiente; requiere Docker |
| Caída de una app | detener app1, repetir solicitudes | Pendiente; requiere Docker |
| TLS/dominio público | navegador/`curl` al host real | Pendiente; no hay dominio asignado |
| Concurrencia | carga moderada (wrk/ab/hey) contra Compose | Pendiente; no se inventan resultados |
