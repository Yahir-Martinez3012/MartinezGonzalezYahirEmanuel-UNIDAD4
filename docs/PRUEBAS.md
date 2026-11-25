# Pruebas y liberación

## Resultados observados en esta rama

Entorno: Python 3.13.18, dependencias instaladas en `.venv`, SQLite temporal, `DEBUG=False` y redirección HTTPS desactivada solo para el cliente de pruebas. Ejecutado el 24 de noviembre de 2026:

- `python manage.py check`: aprobado, sin incidencias.
- `python manage.py makemigrations --check --dry-run`: aprobado, no hay migraciones pendientes de generar.
- `coverage run manage.py test`: **143 pruebas aprobadas**, incluyendo las rutas de salud añadidas.
- `coverage report --fail-under=90`: aprobado, cobertura total **96%**.
- `python manage.py check --deploy`: código 0; avisos de prueba por la clave temporal corta y `SECURE_SSL_REDIRECT=False` en el cliente HTTP de tests. No son valores de Production.
- El navegador local cargó Inicio y `/vacantes/`; se mostraron 10 vacantes de demostración.
- Vercel (consulta autenticada): `/health/` y `/ready/` devolvieron `200`; readiness indicó `database: available`. En Production, `showmigrations --plan` muestra las migraciones de Django sin aplicar.
- GitHub Actions en el PR #1, run `45517706038` para `d33844b`, terminó en `success` después de configurar `SECURE_SSL_REDIRECT=False` exclusivamente para CI. El run anterior (`45332664231`) falló porque el cliente HTTP de Django seguía la redirección HTTPS de `DEBUG=False`.
- Docker Engine/Compose no está instalado aquí. **No** se ejecutaron `docker compose config/build/up/ps`, PostgreSQL en contenedor, balanceo/failover ni concurrencia. La URL Vercel usa un certificado válido, pero la protección SSO impide verificar el sitio desde una sesión anónima.

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
| Liveness y readiness | Tests Django y Vercel CLI autenticado | Aprobado: `/health/` y `/ready/` responden 200; DB disponible |
| API, roles, autenticación, vacantes | `python manage.py test` | Aprobado: 143 pruebas locales, cobertura 96%; GitHub Actions run `45517706038` en success |
| Migraciones | `makemigrations --check --dry-run`; `showmigrations --plan` en Production | Sin cambios de modelos; migraciones de Production pendientes de aplicar |
| Compose válido | `docker compose config` | No ejecutado: Docker/Compose no está instalado |
| Dos instancias | Script a través de Nginx | No ejecutado: Docker no está disponible |
| Caída de una app | detener app1, repetir solicitudes | No ejecutado: Docker no está disponible |
| TLS y acceso público | conexión TLS y solicitud anónima | Certificado TLS válido; acceso anónimo bloqueado por SSO; falta un dominio personalizado |
| Concurrencia | carga moderada contra Compose | No ejecutado; no se inventan resultados |
