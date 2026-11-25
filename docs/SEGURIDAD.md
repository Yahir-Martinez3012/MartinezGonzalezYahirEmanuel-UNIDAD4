# Seguridad

## Medidas incorporadas

- Producción requiere `SECRET_KEY`, `DEBUG=False` y `DATABASE_URL`; se rechaza SQLite sin depuración.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` se leen del entorno; los hosts de Vercel/Render recibidos por el runtime se incorporan como host HTTPS.
- HTTPS detrás de proxy confía en `X-Forwarded-Proto` de la plataforma, cookies de sesión/CSRF seguras y HSTS configurable.
- Se conservan CSP, protección CSRF, clickjacking, `nosniff`, referrer policy, validadores de contraseña, autenticación/roles, limitación API y validación de PDFs existentes.
- Docker ejecuta Gunicorn como usuario no privilegiado, PostgreSQL queda en red interna, los secretos son obligatorios en entorno local y los contenedores tienen healthchecks.
- Migraciones se ejecutan una vez en el servicio `migrate`; no se ejecutan automáticamente en cada proceso Gunicorn.
- `/health/`, `/ready/` y `/api/infraestructura/` no retornan secretos, conexión, stack traces ni datos de usuarios.
- `.gitignore` y `.dockerignore` excluyen variables `.env`, certificados/llaves, bases locales, CV/PDF y archivos temporales. `.env.example` solo contiene marcadores.

## Secretos

Genera una `SECRET_KEY` y contraseñas distintas y aleatorias para cada entorno. Guarda secretos solo en el administrador de variables de Vercel o el `.env` local ignorado por Git. No captures sus valores en evidencias; muestra únicamente los nombres de variables con valores ocultos.

## TLS y límites

La configuración de Django no emite certificados. En Vercel, TLS depende de que el dominio real esté asignado y la validación administrada aparezca como válida. Nginx de Docker escucha HTTP local; TLS de producción no se simula con un certificado autofirmado. HSTS se puede deshabilitar en Docker local con `SECURE_HSTS_SECONDS=0`; no uses ese valor en producción. `includeSubDomains` permanece apagado hasta confirmar TLS en todos los subdominios.

La política CSP ya existente del proyecto se conserva; cualquier ajuste para inline scripts, mapas, CDN o reCAPTCHA debe evaluarse con las rutas reales y no debilitarse globalmente.
