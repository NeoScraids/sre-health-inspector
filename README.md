<div align="center">

  <h1>sre-health-inspector</h1>
  <p><strong>Sonda de Diagnóstico SRE en Python y Contenedor Docker para Monitoreo de SSL/TLS y Telemetría de Endpoints</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Lenguaje-Python_3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Contenedor-Docker_Alpine-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Dependencias-Cero_Librer%C3%ADas_Externas-success?style=flat-square" alt="Zero Dependencies" />
    <img src="https://img.shields.io/badge/Salida-ASCII_%2F_JSON-blue?style=flat-square" alt="Salida" />
    <img src="https://img.shields.io/badge/Licencia-MIT-blue?style=flat-square" alt="Licencia" />
  </p>

</div>

---

### Descripción General

`sre-health-inspector` es una sonda de diagnóstico diseñada para ingenieros de confiabilidad de sitios (SRE), operadores de infraestructura y tareas programadas en clústeres Kubernetes. 

Permite inspeccionar en segundos los días restantes de vigencia de certificados SSL/TLS, medir la latencia de respuesta en milisegundos de endpoints HTTP/HTTPS y validar la conectividad de sockets TCP.

### Características Principales

- **Cero Dependencias Externas:** Desarrollado utilizando exclusivamente módulos de la biblioteca estándar de Python (`ssl`, `socket`, `urllib.request`).
- **Salida Dual:** Ofrece visualización en tablas de terminal legibles para humanos o JSON estructurado para integración en pipelines y cronjobs.
- **Ejecución Contenerizada:** Imagen ligera basada en Alpine Linux ejecutada bajo un usuario sin privilegios (`appuser`).
- **Códigos de Salida Deterministas:** Devuelve código `1` si cualquiera de los recursos auditados está vencido, degradado o inaccesible.

---

### Inicio Rápido

#### 1. Ejecución Directa con Python

```bash
# Clonar el repositorio
git clone https://github.com/NeoScraids/sre-health-inspector.git
cd sre-health-inspector

# Inspeccionar expiración de certificados SSL/TLS
python -m src.inspector --ssl api.github.com google.com

# Medir latencia y códigos de respuesta de endpoints HTTP
python -m src.inspector --http https://httpbin.org/status/200 https://api.github.com

# Probar conectividad en puertos TCP (host:puerto)
python -m src.inspector --tcp 8.8.8.8:53 1.1.1.1:53
```

#### 2. Ejecución Contenerizada con Docker

No requiere tener Python instalado localmente:

```bash
# Construir la imagen del contenedor
docker build -t sre-health-inspector .

# Ejecutar el diagnóstico puntual en un contenedor efímero
docker run --rm sre-health-inspector --ssl github.com --http https://github.com
```

---

### Opciones de la Línea de Comandos (CLI)

```text
Uso: python -m src.inspector [OPCIONES]

Opciones:
  --ssl HOST [HOST ...]    Uno o más dominios para consultar la fecha de expiración TLS
  --http URL [URL ...]     Endpoints HTTP o HTTPS para medir la latencia de respuesta
  --tcp HOST:PUERTO [...]  Objetivos TCP formateados como host:puerto para verificar conectividad
  --timeout SEGUNDOS       Tiempo límite de espera de red (Por defecto: 5.0)
  --json                   Exportar los resultados en formato JSON estructurado
  --help                   Muestra este mensaje de ayuda
```

---

### Ejemplo de Salida en Terminal

```text
=== SRE HEALTH INSPECTOR // REPORTE ===
CHECK            | DESTINO                             | ESTADO     | MÉTRICAS / DETALLE
---------------------------------------------------------------------------------------------------------
ssl_certificate  | github.com:443                      | HEALTHY    | Expira en 142 días (Emisor: DigiCert Inc)
http_endpoint    | https://api.github.com              | HEALTHY    | HTTP 200 (145.22 ms)
tcp_port         | 8.8.8.8:53                          | HEALTHY    | Conexión establecida (24.18 ms)
======================================
```

#### Salida Estructurada en JSON (`--json`)

```json
{
  "probe_timestamp": "2026-09-10T20:30:00.000000Z",
  "results": [
    {
      "target": "github.com:443",
      "check": "ssl_certificate",
      "status": "HEALTHY",
      "days_remaining": 142,
      "expiration_date": "2027-01-30T23:59:59+00:00",
      "issuer": "DigiCert Inc",
      "error": null
    }
  ]
}
```

---

### Pruebas Automatizadas

Ejecuta la suite de pruebas unitarias con el framework estándar:

```bash
python -m unittest discover -s tests
```

---

### Licencia

Distribuido bajo la Licencia MIT. Desarrollado y mantenido por [Brandon Mendieta](https://github.com/NeoScraids).
