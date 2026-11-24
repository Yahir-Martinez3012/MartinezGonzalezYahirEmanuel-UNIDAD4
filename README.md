# Conecta UTC — Unidad 4

**Proyecto:** bolsa de trabajo universitaria Conecta UTC. **Unidad:** Saber Hacer Unidad 4 — infraestructura y despliegue. **Alumno:** Yahir Emanuel Martínez González. **Universidad:** Universidad Tecnológica de Coahuila. **Carrera:** Ingeniería en Desarrollo y Gestión de Software. **Materia:** Desarrollo Web Integral. **Docente:** M.A.Y.L. Gabriel Alejandro Reyes Morales.

Conecta UTC reúne estudiantes y egresados con empresas para descubrir vacantes, prácticas profesionales y estadías. Esta rama parte del código de la Unidad 3; no modifica el repositorio anterior ni el servicio en Render.

## Propósito y funcionalidades conservadas

La plataforma conserva el inicio, búsqueda/listado y detalle de vacantes, registro e inicio de sesión, perfiles, roles de estudiante/empresa/administrador, postulaciones, CV PDF, aprobaciones administrativas, catálogos, mapas OpenStreetMap/Leaflet, API Django REST Framework y documentación Swagger/OpenAPI. Revisa `docs/ARQUITECTURA.md` para el inventario de componentes y topología.

## Tecnologías

Python 3.13, Django 6.1, Django REST Framework, PostgreSQL, Gunicorn, Nginx, Docker Compose, WhiteNoise, HTML/CSS/JavaScript, Bootstrap, Leaflet/OpenStreetMap, drf-spectacular, GitHub Actions y Neon como PostgreSQL gestionado disponible para producción.

## Topología local Docker

```mermaid
flowchart LR
  Usuario --> Nginx
  Nginx -->|Round Robin| App1[Django + Gunicorn app1]
  Nginx -->|Round Robin| App2[Django + Gunicorn app2]
  App1 --> PostgreSQL[(PostgreSQL persistente)]
  App2 --> PostgreSQL
  Migraciones[migrate: una ejecución] --> PostgreSQL
  Migraciones --> Static[(Volumen static_data)]
  Nginx --> Static
```

`app1` y `app2` comparten secreto y `DATABASE_URL`. Nginx es el único servicio publicado; la red de backend no es externa. El contenedor `migrate` aplica migraciones una sola vez y recopila estáticos antes de iniciar las apps. PostgreSQL usa el volumen `postgres_data`.

## Levantar localmente

Requiere Docker Engine y Docker Compose v2.

```sh
cp .env.example .env
# Edita .env: reemplaza SECRET_KEY y POSTGRES_PASSWORD con secretos distintos.
docker compose config
docker compose up -d --build
docker compose ps
```

Abre `http://localhost:8080/`. Healthchecks: `http://localhost:8080/health/` (proceso), `/ready/` (PostgreSQL) y `/api/infraestructura/` (etiqueta real configurada del contenedor). Swagger está en `/api/v1/docs/`, la API en `/api/v1/` y admin en `/admin/`.

Para probar distribución Round Robin observada, con `python` disponible en el host:

```sh
python scripts/probar_balanceador.py --requests 20
```

El comando falla si no observa ambas instancias o si alguna petición falla; no inventa ni simula resultados. Para una prueba de caída, ejecuta `docker compose stop app1`, repite el script y después `docker compose start app1`. Nginx detecta y excluye un upstream fallido, pero una petición puede fallar durante esa ventana; registra resultados reales.

Datos ficticios: `docker compose exec app1 python manage.py poblar_demo`. Para crear las cuentas demo, añade `--usuarios` solo en un entorno aislado y configura un secreto `DEMO_PASSWORD` seguro. No publiques usuarios de demo en producción. `docker compose down` conserva datos; `docker compose down -v` los elimina.

## Configuración

Variables Docker locales se documentan en `.env.example`. Nunca se suben `.env`, claves, contraseñas, tokens, CV ni datos reales. En Vercel configura `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL` PostgreSQL gestionado, `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` desde Settings. Activa reCAPTCHA y Resend únicamente con credenciales existentes. Los certificados TLS para el host Vercel son administrados por la plataforma.

La aplicación rechaza SQLite cuando `DEBUG=False`. En desarrollo local sin `DATABASE_URL`, settings conserva SQLite para compatibilidad de las pruebas existentes; en Docker se usa PostgreSQL. No apunta a la base de datos de Render de Unidad 3.

## Vercel: producción distinta a Compose

La plataforma documenta detección de Django desde `manage.py` y WSGI y crea runtime Python administrado. Esta configuración de Vercel no ejecuta Gunicorn permanente, Nginx, Docker Compose ni el PostgreSQL de Compose. Vercel ofrece TLS y escalado de funciones; Django conecta al `DATABASE_URL` PostgreSQL externo. Por la detección automática, no se agregó `vercel.json` innecesario.

En el estado de esta rama no hay proyecto Vercel asociado, deployment, dominio o certificado que podamos afirmar como operativos. La importación del repositorio y Neon conectados no completan esos pasos. Consulta `docs/DESPLIEGUE.md` para el procedimiento explícito; se necesita crear/vincular el proyecto Vercel, establecer variables de entorno y luego comprobar el deployment y dominio.

## Pruebas

```sh
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py test

docker compose config
docker compose build
docker compose up -d
docker compose ps
python scripts/probar_balanceador.py --requests 20
```

GitHub Actions ejecuta checks, migraciones y pruebas contra PostgreSQL. La cifra de 140 pruebas aprobadas corresponde a Unidad 3 según el README de origen; no se presenta como resultado de ejecución de esta rama. Los resultados de Unidad 4 se documentarán solo al ejecutarse. Ver `docs/PRUEBAS.md`.

## Documentación y evidencias

- `docs/ARQUITECTURA.md`: componentes Docker y topología real prevista para Vercel.
- `docs/DESPLIEGUE.md`: Docker, producción y variables.
- `docs/PRUEBAS.md`: comandos y resultados pendientes/aceptación.
- `docs/SEGURIDAD.md`: controles y secretos.
- `docs/EVIDENCIAS.md`: guía precisa de capturas auténticas, sin exponer información sensible.

## Estado real de requisitos

| Requisito | Tecnología/configuración | Estado en esta rama | Evidencia |
| --- | --- | --- | --- |
| Base de aplicación U3 | Django apps/templates y modelos fuente | Importada; las 143 pruebas locales actuales pasan | Historial Git + suite |
| Servidor app | Gunicorn en contenedores no root | Configurado; no se pudo iniciar Docker aquí | `Dockerfile`, Compose |
| PostgreSQL local | PostgreSQL 16 + volumen | Configurado; no ejecutado por falta de Docker | `docker-compose.yml` |
| Migraciones | Servicio único `migrate` | Configurado; check de migraciones pasa, no aplicado a PostgreSQL | Compose y logs pendientes |
| Balanceo | Nginx upstream Round Robin | Configurado; no se verificó distribución/failover | `nginx/default.conf`, script |
| Health/ready | Django y consulta SQL sin filtrar secretos | Implementados y cubiertos por pruebas | `core/views.py`, tests (143 pasan) |
| Seguridad | Entorno, cookies, proxy, HSTS, ignore rules | Checks deployment pasan con avisos HSTS documentados | `config/settings.py`, docs |
| CI | GitHub Actions + PostgreSQL | Workflow configurado; primera ejecución remota pendiente | `.github/workflows/tests.yml` |
| API, roles, mapas, Swagger | Implementación heredada de U3 | Conservada; suite Django completa pasa localmente | Código y suite |
| Vercel/Dominio/TLS | Runtime Vercel + Neon | Pendiente; sin proyecto/dominio desplegado | `docs/DESPLIEGUE.md` |
| HTTPS público | TLS administrado Vercel | Pendiente hasta deployment y dominio | `docs/EVIDENCIAS.md` |
| Rendimiento/concurrencia | script stdlib de requests seriales | Pendiente; concurrencia moderada no ejecutada | `docs/PRUEBAS.md` |

## Repositorios

- Unidad 4: https://github.com/Yahir-Martinez3012/MartinezGonzalezYahirEmanuel-UNIDAD4
- Unidad 3 (solo fuente de importación; no se modifica): https://github.com/Yahir-Martinez3012/MartinezGonzalezYahirEmanuel-UNIDAD3

La URL pública sugerida `conecta-utc-unidad4.vercel.app` es solo propuesta y no se afirma disponible/asignada. Consulta `docs/EVIDENCIAS.md` para completar evidencias académicas verificables.
