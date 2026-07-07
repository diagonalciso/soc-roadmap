# soc-Roadmap — Unified Portal

> Aggregating portal across the roadmap SOC services.

**Port:** `8090` &nbsp;|&nbsp; **Repo:** `diagonalciso/soc-roadmap` &nbsp;|&nbsp; **Service:** `soc-roadmap.service` &nbsp;|&nbsp; **Stack:** stdlib Python (no external deps)

Part of the **CD / Wazuh Full SOC** suite. Open the in-app **`?` Help button** (top-right of the dashboard) to read this manual, or view it here.

---

## 1. Overview

soc-Roadmap is a unified portal that aggregates the roadmap SOC services into a single operational view with quick links and health, so analysts have one launch point.

## 2. Key features

- Single portal across roadmap services
- Per-service links and status
- At-a-glance health

## 3. Running the service

The service is a single self-contained `app.py` using only the Python standard library.

```bash
# systemd (fleet / suite install)
sudo systemctl status soc-roadmap
sudo systemctl restart soc-roadmap
sudo journalctl -u soc-roadmap -f

# manual run (from the repo directory)
cp .env.example .env      # then edit as needed
env $(grep -v '^#' .env | xargs) python3 app.py
```

Then open **http://<host>:8090/**.

## 4. Configuration (environment variables)

Set these in `.env` (see `.env.example` for defaults):

| Variable | Notes |
|---|---|
| `DASHBOARD_PORT` | Listen port (default 8090). |
| `SERVICE_HOST` |  |

## 5. HTTP endpoints

| Path | |
|---|---|
| `/` | Main dashboard (HTML) |
| `/api/health` | API endpoint (JSON) |
| `/manual` | This manual (opened by the top-right **?** Help button) |

## 6. Integration

Links out to the individual soc-* services; health endpoint for the SOC hub.

## 7. Security & operational notes

Link/aggregation layer — the underlying services own their own data.

## 8. Troubleshooting

| Symptom | Check |
|---|---|
| Page will not load | `systemctl status soc-roadmap`; confirm the port `8090` is listening (`lsof -i:8090`). |
| Help button shows "MANUAL.md not found" | Ensure `MANUAL.md` sits next to `app.py` in the service directory. |
| Service keeps restarting | `journalctl -u soc-roadmap -e` for the traceback; usually a missing `.env` value. |
| Empty / stale data | Confirm upstream sources and any API keys in `.env` are reachable. |

---

*Manual for soc-roadmap. Part of the CD / Wazuh Full SOC suite. Private © CisoDiagonal.*
