# Roadmap Dashboard

Unified portal for all 8 SOC platform tools. Aggregates stats from 5 standalone services + 2 embedded extensions.

## Quick Start

```bash
cd soc-roadmap
cp .env.example .env
python3 app.py
```

Access at http://localhost:8100

## Services Displayed

### Core Services (ports 8200-8205)
- **Phishing Analyzer** (8200) — Parse emails, extract IOCs, enrich, verdict
- **Attack Surface Monitor** (8201) — Shodan + crt.sh scanning, cert expiry
- **Canary Token Manager** (8202) — URL/DNS/API token generation + activation logging
- **Credential Exposure Monitor** (8203) — Darkweb breach queries, auto-case creation
- **Passive DNS Monitor** (8205) — Subdomain enumeration, DNS change tracking

### Embedded Extensions
- **SOAR Playbook Engine** (in SOCops, port 8081) — YAML-based automation rules
- **Threat Hunt Workbench** (in SOCint, port 8000) — Structured hypothesis→findings→case workflow

## Features

- Auto-refreshing service status (30s interval)
- Live stats aggregation from all services
- One-click access to each dashboard
- Health check endpoint: `/api/health`
- Responsive grid layout
- Quick links to related services (SOCops, SBOMguard, SOCint)

## Configuration

Edit `.env`:
- `DASHBOARD_PORT` — listening port (default 8100)

## Dependencies

Python 3.8+ stdlib only.

## Notes

- Dashboard refreshes every 30 seconds
- Stats fetched from each service `/api/stats` endpoint
- Requires all 5 services running (graceful fallback if offline)
- Shows last update timestamp for each service


## Documentation

See **[MANUAL.md](MANUAL.md)** for the full manual (overview, configuration, endpoints, integration, troubleshooting). In the running dashboard, click the **`?` Help button** in the top-right corner to open it at `/manual`.
