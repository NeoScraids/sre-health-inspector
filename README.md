# sre-health-inspector

CLI en Python (sin dependencias externas) para verificar rapidamente el estado de endpoints, certificados SSL y puertos TCP. Lo uso como health check antes de deployments y para cronjobs de monitoreo.

Cero librerias externas: solo usa `ssl`, `socket` y `urllib` de la stdlib de Python.

## Uso

```bash
git clone https://github.com/NeoScraids/sre-health-inspector.git
cd sre-health-inspector

# Verificar certificados SSL (dias restantes, emisor)
python -m src.inspector --ssl api.github.com google.com

# Medir latencia HTTP
python -m src.inspector --http https://httpbin.org/status/200 https://api.github.com

# Probar conectividad TCP
python -m src.inspector --tcp 8.8.8.8:53 1.1.1.1:53

# Combinar todo y exportar en JSON (para pipelines)
python -m src.inspector --ssl github.com --http https://github.com --json
```

## Salida

En terminal:
```
=== SRE HEALTH INSPECTOR // REPORTE ===
CHECK            | DESTINO                  | ESTADO   | DETALLE
-------------------------------------------------------------------
ssl_certificate  | github.com:443           | HEALTHY  | Expira en 142 dias (DigiCert Inc)
http_endpoint    | https://api.github.com   | HEALTHY  | HTTP 200 (145.22 ms)
tcp_port         | 8.8.8.8:53              | HEALTHY  | Conexion establecida (24.18 ms)
```

Con `--json` devuelve JSON estructurado con timestamp, status y dias restantes. Devuelve exit code 1 si algo falla (util para integrarlo en CI).

## Con Docker

```bash
docker build -t sre-health-inspector .
docker run --rm sre-health-inspector --ssl github.com --http https://github.com
```

La imagen esta basada en Alpine y corre con usuario sin privilegios.

## Tests

```bash
python -m unittest discover -s tests
```

## Licencia

MIT
