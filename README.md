<div align="center">

  <h1>sre-health-inspector</h1>
  <p><strong>Lightweight SRE Diagnostic CLI & Container for SSL/TLS Monitoring and Endpoint Telemetry</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Language-Python_3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Container-Docker_Alpine-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Dependencies-Zero_External_Libs-success?style=flat-square" alt="Zero Dependencies" />
    <img src="https://img.shields.io/badge/Output-ASCII_%2F_JSON-blue?style=flat-square" alt="Output" />
    <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License" />
  </p>

</div>

---

### Overview

`sre-health-inspector` is a standalone Site Reliability Engineering (SRE) diagnostic probe. Designed for DevOps engineers, automated health-check jobs, and Kubernetes readiness sidecars, it verifies TLS certificate expiration timelines, measures endpoint response latencies in milliseconds, and validates TCP socket handshakes.

Key highlights:
- **Zero External Dependencies:** Implemented exclusively with Python standard library modules (`ssl`, `socket`, `urllib.request`).
- **Dual Output Modes:** Produces human-readable terminal tables or structured JSON for automated pipeline integration.
- **Containerized Execution:** Available as an unprivileged, non-root Alpine container image.
- **Deterministic Exit Codes:** Returns code `1` whenever any probed resource is in an expired, degraded, or unreachable state.

---

### Quickstart

#### 1. Direct Python Execution

```bash
# Clone the repository
git clone https://github.com/NeoScraids/sre-health-inspector.git
cd sre-health-inspector

# Inspect SSL certificate expiration
python -m src.inspector --ssl api.github.com google.com

# Probe HTTP endpoint latencies and status codes
python -m src.inspector --http https://httpbin.org/status/200 https://api.github.com

# Test TCP socket connectivity (host:port)
python -m src.inspector --tcp 8.8.8.8:53 1.1.1.1:53
```

#### 2. Containerized Execution via Docker

No local Python installation required:

```bash
# Build the image
docker build -t sre-health-inspector .

# Execute probe in ephemeral container
docker run --rm sre-health-inspector --ssl github.com --http https://github.com
```

---

### CLI Command Options

```text
Usage: python -m src.inspector [OPTIONS]

Options:
  --ssl HOST [HOST ...]    One or more hostnames to query for TLS certificate expiry
  --http URL [URL ...]     HTTP or HTTPS endpoints to measure response latency
  --tcp HOST:PORT [...]    TCP host and port combinations to verify socket connectivity
  --timeout SECONDS        Probe network timeout (Default: 5.0)
  --json                   Format and stream output as structured JSON
  --help                   Display this reference manual
```

---

### Sample Terminal Output

```text
=== SRE HEALTH INSPECTOR // REPORT ===
CHECK            | TARGET                              | STATUS     | METRICS / DETAIL
---------------------------------------------------------------------------------------------------------
ssl_certificate  | github.com:443                      | HEALTHY    | Expires in 142 days (Issuer: DigiCert Inc)
http_endpoint    | https://api.github.com              | HEALTHY    | HTTP 200 (145.22 ms)
tcp_port         | 8.8.8.8:53                          | HEALTHY    | Connection established (24.18 ms)
======================================
```

#### Structured JSON Output (`--json`)

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

### Automated Testing

Run the test suite using Python's built-in test runner:

```bash
python -m unittest discover -s tests
```

---

### License

Distributed under the MIT License. Developed and maintained by [Brandon Mendieta](https://github.com/NeoScraids).
