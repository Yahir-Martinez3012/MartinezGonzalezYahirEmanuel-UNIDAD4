FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system django \
    && useradd --system --gid django --home-dir /app --shell /usr/sbin/nologin django \
    && mkdir -p /app/staticfiles \
    && chown django:django /app/staticfiles

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY --chown=django:django . .
COPY --chmod=755 scripts/entrypoint.sh /usr/local/bin/entrypoint
COPY --chmod=755 scripts/healthcheck.sh /usr/local/bin/healthcheck

USER django
EXPOSE 8000
ENTRYPOINT ["entrypoint"]
CMD ["gunicorn", "config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=2", "--access-logfile=-", "--error-logfile=-", "--timeout=60", "--graceful-timeout=30"]
