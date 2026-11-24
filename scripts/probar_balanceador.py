#!/usr/bin/env python3
"""Mide respuestas y distribución observada detrás de Nginx; no simula instancias."""

import argparse
import json
import time
from collections import Counter
from urllib.error import URLError
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8080/api/infraestructura/')
parser.add_argument('--requests', type=int, default=20)
args = parser.parse_args()
if not 1 <= args.requests <= 500:
    parser.error('--requests debe estar entre 1 y 500')

instances = Counter()
errors = 0
latencies_ms = []
for index in range(1, args.requests + 1):
    started = time.perf_counter()
    try:
        request = Request(args.url, headers={'Accept': 'application/json'})
        with urlopen(request, timeout=5) as response:
            payload = json.load(response)
            latency = (time.perf_counter() - started) * 1000
            latencies_ms.append(latency)
            instance = payload.get('instance', 'sin-etiqueta')
            instances[instance] += 1
            print(f'{index:03d} status={response.status} instance={instance} latency_ms={latency:.1f}')
    except (URLError, TimeoutError, ValueError, KeyError) as error:
        errors += 1
        print(f'{index:03d} error={type(error).__name__}')

summary = {
    'requests': args.requests,
    'successes': len(latencies_ms),
    'errors': errors,
    'instances': dict(instances),
    'mean_latency_ms': round(sum(latencies_ms) / len(latencies_ms), 1) if latencies_ms else None,
    'max_latency_ms': round(max(latencies_ms), 1) if latencies_ms else None,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if errors or len(instances) < 2:
    raise SystemExit('Verificación incompleta: se esperaban cero errores y respuesta de ambas instancias.')
