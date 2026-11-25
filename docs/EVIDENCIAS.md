# Guía de evidencias para Saber Hacer Unidad 4

No se generaron capturas artificiales. Guarda capturas originales en `evidencias/` de tu equipo (no agregues a Git archivos `.env`, credenciales, CV reales ni datos personales). En terminales captura el comando completo, salida, fecha y contexto del entorno.

## Capturas exactas

1. **App y dominio:** Vercel > proyecto > Deployment Production Ready; navegador en URL HTTPS mostrando inicio Conecta UTC; barra de dirección con candado y host.
2. **Vacantes:** navegador en listado `/vacantes/`, filtros/resultados visibles; detalle de una vacante abierta.
3. **Autenticación:** página de inicio de sesión y una sesión demo de estudiante; no muestres contraseñas ni información real.
4. **Administración:** `/admin/` autenticado con usuario de pruebas; oculta correo/nombres personales que no sean ficticios.
5. **Dockerfile y Compose:** editor/visor de GitHub mostrando Dockerfile, `docker-compose.yml`, `.dockerignore` y `nginx/default.conf`.
6. **Contenedores:** terminal ejecutando `docker compose ps` donde aparezcan db, migrate (Exited 0), app1, app2 y nginx, conservando estados reales.
7. **Gunicorn/Django:** `docker compose logs --tail=80 app1 app2`; oculta cabeceras/secretos si los hubiere.
8. **PostgreSQL y persistencia:** `docker compose exec db pg_isready -U conecta -d conecta_utc`, `docker volume ls`, luego crea un dato ficticio, reinicia el servicio DB sin borrar volúmenes y demuestra su persistencia. No muestres contraseñas.
9. **Nginx y balanceo:** contenido de `nginx/default.conf`; luego `python scripts/probar_balanceador.py --requests 20`, mostrando resumen real con ambas etiquetas.
10. **Failover:** `docker compose stop app1`, salida repetida del script y `docker compose ps`; registra errores observados durante convergencia, después `docker compose start app1`.
11. **Health:** terminal con respuestas reales `curl -i http://localhost:8080/health/`, `/ready/` y `/api/infraestructura/`.
12. **API/Swagger:** navegador en `/api/v1/` o endpoint público válido y `/api/v1/docs/`; no incluyas tokens en capturas.
13. **Variables:** Vercel Settings > Environment Variables, solo nombres visibles y valores cubiertos/ocultos.
14. **Pruebas:** terminal con `python manage.py check`, `python manage.py check --deploy`, `python manage.py makemigrations --check --dry-run`, `python manage.py test`; para Docker agrega `docker compose config/build/up/ps`. No atribuyas resultados a la prueba sin ejecutarla.
15. **GitHub:** página del repositorio Unidad 4, rama de trabajo/PR, commits no vacíos y Actions exitosas.
16. **TLS:** navegador sin advertencia y `openssl s_client -connect <host>:443 -servername <host>` mostrando issuer y fechas válidas; nunca captures llave privada.
17. **Vercel:** Deployment detail con commit/repo y estado Ready, además del dominio asignado. No presentes un preview local como producción.

## Plantilla para registrar resultados

Para cada captura anota: `ID`, fecha/hora, nombre de evidencia, entorno (`local Docker`, `GitHub Actions`, `Vercel Production`), comando/URL, resultado literal y observación. Antes de entregar el PDF revisa que no aparezcan secretos, datos personales, tokens ni CV reales.

## Evidencia disponible en esta revisión

Comprobaciones reales: GitHub Actions `45519292178` en verde para `main@381ce42`; 143 tests Django locales aprobados; migraciones Neon Production aplicadas y 12 vacantes consultadas; acceso anónimo sin cookies a la URL estable, salud, readiness, listado público, endpoint REST, Swagger, login y registro; TLS `.vercel.app` válido. El sitio lista 10 vacantes publicadas. Docker/Compose no está instalado y el script de balanceador falló al no existir un servicio en `localhost:8080`; no hay evidencia de contenedores, balanceo ni failover.

La guía y la configuración versionada son evidencia documental, no sustituyen capturas originales. Puedes capturar el dominio estable ya público en ventana privada, las rutas Django, Swagger y el certificado. Ejecuta localmente las pruebas de Compose y balanceo indicadas en `GUIA_DE_CAPTURAS.md`; adjunta solo salidas literales. No presentes resultados simulados ni la página de SSO del CLI como navegación pública.
