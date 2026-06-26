#!/usr/bin/env python3
"""
Roadmap Projects Dashboard - Unified portal for all SOC tools
Aggregates stats from: Phishing Analyzer, Attack Surface Monitor, Canary Token Manager,
Credential Exposure Monitor, Passive DNS Monitor
"""
import os
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from datetime import datetime

PORT = int(os.getenv("DASHBOARD_PORT", "8090"))
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")

SERVICES = {
    "phishing_analyzer": {"url": f"http://{SERVICE_HOST}:8091", "name": "Phishing Analyzer", "color": "#FF6B6B"},
    "attack_surface_monitor": {"url": f"http://{SERVICE_HOST}:8092", "name": "Attack Surface Monitor", "color": "#4ECDC4"},
    "canary_token_manager": {"url": f"http://{SERVICE_HOST}:8093", "name": "Canary Token Manager", "color": "#FFE66D"},
    "credential_exposure_monitor": {"url": f"http://{SERVICE_HOST}:8094", "name": "Credential Exposure Monitor", "color": "#95E1D3"},
    "passive_dns_monitor": {"url": f"http://{SERVICE_HOST}:8095", "name": "Passive DNS Monitor", "color": "#A8D8EA"},
    "ir_case_manager":     {"url": f"http://{SERVICE_HOST}:8206", "name": "IR Case Manager",        "color": "#FF6B6B"},
    "ransomware_tracker":  {"url": f"http://{SERVICE_HOST}:8096", "name": "Ransomware Tracker",      "color": "#f85149"},
    "shinyhunters_tracker":{"url": f"http://{SERVICE_HOST}:8097", "name": "ShinyHunters Monitor",    "color": "#d29922"},
    "qilin_tracker":       {"url": f"http://{SERVICE_HOST}:8098", "name": "Qilin Monitor",           "color": "#f85149"},
}

stats_cache = {}
cache_time = {}

def fetch_stats(service_key, url):
    """Fetch stats from service"""
    try:
        req = Request(f"{url}/api/stats")
        with urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            stats_cache[service_key] = data
            cache_time[service_key] = datetime.utcnow().isoformat()
            return True
    except:
        stats_cache[service_key] = {}
        return False

def refresh_all_stats():
    """Background thread to refresh stats"""
    while True:
        for key, svc in SERVICES.items():
            fetch_stats(key, svc["url"])
        time.sleep(30)

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.render_dashboard().encode())
        elif self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            health = {
                "status": "online",
                "services": {}
            }
            for key, svc in SERVICES.items():
                health["services"][key] = {
                    "status": "ok" if key in stats_cache else "checking",
                    "last_update": cache_time.get(key, "never")
                }
            self.wfile.write(json.dumps(health).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def render_dashboard(self):
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Roadmap</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg:       #050810;
      --bg-soft:  #080d1a;
      --panel:    rgba(10,18,32,0.85);
      --panel-bd: rgba(0,255,136,0.22);
      --panel-bd2:rgba(0,204,255,0.18);
      --grid-ln:  rgba(0,255,136,0.06);
      --text:     #c8d6e0;
      --text-dim: #6c8090;
      --accent:   #00ff88;
      --accent-2: #00ccff;
      --accent-3: #ff5ec4;
      --warn:     #ffb000;
      --crit:     #ff3860;
      --ok:       #00ff88;
      --offline:  #5a6878;
      --shadow:   0 0 18px rgba(0,255,136,0.10), inset 0 0 24px rgba(0,200,255,0.04);
      --mono:     'JetBrains Mono', ui-monospace, monospace;
      --display:  'Orbitron', 'JetBrains Mono', sans-serif;
    }}
    *{{ margin:0; padding:0; box-sizing:border-box; }}
    html,body{{
      min-height:100%; background:var(--bg); color:var(--text);
      font-family:var(--mono); font-size:13px; line-height:1.4;
    }}
    body{{
      background:
        radial-gradient(circle 800px at 12% 8%,  rgba(0,200,255,0.10),transparent 60%),
        radial-gradient(circle 700px at 88% 12%, rgba(255,94,196,0.06), transparent 60%),
        radial-gradient(circle 900px at 50% 100%,rgba(0,255,136,0.06), transparent 60%),
        var(--bg);
      background-attachment:fixed; position:relative;
    }}
    body::before{{
      content:''; position:fixed; inset:0;
      background-image:
        linear-gradient(var(--grid-ln) 1px,transparent 1px),
        linear-gradient(90deg,var(--grid-ln) 1px,transparent 1px);
      background-size:48px 48px; pointer-events:none; z-index:0;
      mask-image:radial-gradient(ellipse at center,#000 30%,transparent 90%);
    }}
    body::after{{
      content:''; position:fixed; inset:0;
      background:linear-gradient(rgba(0,255,136,0.025) 50%,transparent 50%);
      background-size:100% 4px; pointer-events:none; z-index:1;
      opacity:0.35; mix-blend-mode:overlay;
    }}

    /* Boot overlay */
    #boot-overlay{{
      position:fixed; inset:0; background:var(--bg);
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      z-index:1000; transition:opacity 0.6s ease;
    }}
    #boot-overlay.hidden{{ opacity:0; pointer-events:none; }}
    .boot-text{{
      font-family:var(--display); font-weight:800; letter-spacing:4px;
      color:var(--accent); font-size:1.05rem; margin-bottom:18px;
      text-shadow:0 0 18px rgba(0,255,136,0.6);
    }}
    .boot-bar{{ width:320px; height:3px; background:rgba(0,255,136,0.12); overflow:hidden; border-radius:1px; }}
    .boot-fill{{
      width:0%; height:100%;
      background:linear-gradient(90deg,var(--accent),var(--accent-2));
      animation:bootFill 1.4s ease-out forwards;
    }}
    @keyframes bootFill{{ to{{ width:100%; }} }}

    /* Layout */
    .wall{{ position:relative; z-index:2; display:flex; flex-direction:column; min-height:100vh; padding:10px; gap:10px; }}

    /* Topbar */
    .topbar{{
      display:grid; grid-template-columns:auto 1fr auto;
      gap:14px; align-items:center;
      background:var(--panel); border:1px solid var(--panel-bd);
      box-shadow:var(--shadow); padding:10px 16px; border-radius:4px;
      backdrop-filter:blur(6px);
    }}
    .brand{{ display:flex; align-items:center; gap:12px; }}
    .logo-mark{{
      font-size:1.7rem; color:var(--accent);
      text-shadow:0 0 14px var(--accent),0 0 24px var(--accent-2);
      animation:logoSpin 8s linear infinite;
    }}
    @keyframes logoSpin{{ to{{ transform:rotate(360deg); }} }}
    .brand-name{{
      font-family:var(--display); font-weight:900; letter-spacing:3px;
      color:var(--accent); text-shadow:0 0 8px rgba(0,255,136,0.5);
      font-size:1.15rem; line-height:1;
    }}
    .brand-tag{{ color:var(--text-dim); font-size:0.65rem; letter-spacing:2px; margin-top:2px; }}
    .topbar-right{{ display:flex; align-items:center; gap:16px; justify-content:flex-end; flex-wrap:wrap; }}
    .clock{{ text-align:right; }}
    .clock-time{{
      font-family:var(--display); font-weight:800; color:var(--accent-2);
      font-size:1.4rem; letter-spacing:3px;
      text-shadow:0 0 8px rgba(0,204,255,0.5); line-height:1;
    }}
    .clock-date{{ color:var(--text-dim); font-size:0.6rem; letter-spacing:2px; margin-top:4px; }}
    .services{{ display:flex; flex-wrap:wrap; gap:6px; }}
    .svc{{
      display:inline-flex; align-items:center; gap:6px;
      padding:5px 10px; font-size:0.7rem; letter-spacing:1px; font-weight:600;
      color:var(--text); text-decoration:none;
      border:1px solid var(--panel-bd2); border-radius:2px;
      transition:all 0.2s; background:rgba(0,0,0,0.25);
    }}
    .svc:hover{{ border-color:var(--accent); color:var(--accent); box-shadow:0 0 10px rgba(0,255,136,0.4); transform:translateY(-1px); }}
    .svc .dot{{ width:7px; height:7px; border-radius:50%; background:var(--offline); box-shadow:0 0 4px var(--offline); }}
    .svc.up .dot{{ background:var(--ok); box-shadow:0 0 8px var(--ok); }}
    .svc.down .dot{{ background:var(--crit); box-shadow:0 0 8px var(--crit); animation:dotPulse 1.4s ease-in-out infinite; }}
    @keyframes dotPulse{{ 0%,100%{{ opacity:0.4; }} 50%{{ opacity:1; }} }}

    /* Section headings */
    .section{{ margin-top:4px; }}
    .section-heading{{
      font-family:var(--display); font-weight:600; font-size:0.7rem;
      letter-spacing:3px; color:var(--text-dim); text-transform:uppercase;
      padding:0 4px 6px; border-bottom:1px solid var(--panel-bd);
      margin-bottom:10px; display:flex; align-items:center; gap:8px;
    }}
    .section-heading .bullet{{
      width:6px; height:6px; background:var(--accent); display:inline-block;
      box-shadow:0 0 6px var(--accent); animation:dotPulse 2s ease-in-out infinite;
    }}

    /* Cards grid */
    .cards-grid{{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:10px; }}

    /* Panel card */
    .panel{{
      position:relative; background:var(--panel); border:1px solid var(--panel-bd);
      border-radius:4px; display:flex; flex-direction:column;
      overflow:hidden; backdrop-filter:blur(4px); box-shadow:var(--shadow);
      transition:border-color 0.2s, box-shadow 0.2s;
    }}
    .panel:hover{{ border-color:var(--accent); box-shadow:0 0 24px rgba(0,255,136,0.18); }}
    .panel::before{{
      content:''; position:absolute; top:0; left:0; right:0; height:1px;
      background:linear-gradient(90deg,transparent,var(--accent),transparent); opacity:0.7;
    }}
    .panel-head{{
      display:flex; justify-content:space-between; align-items:center;
      padding:8px 12px; border-bottom:1px solid var(--panel-bd);
      background:linear-gradient(180deg,rgba(0,255,136,0.04),transparent); flex-shrink:0;
    }}
    .panel-title{{
      font-family:var(--display); font-weight:600; font-size:0.7rem;
      letter-spacing:2px; color:var(--text); text-transform:uppercase;
      display:flex; align-items:center; gap:8px;
    }}
    .panel-title .bullet{{
      width:6px; height:6px; background:var(--accent); display:inline-block;
      box-shadow:0 0 6px var(--accent); animation:dotPulse 2s ease-in-out infinite;
    }}
    .panel-title .bullet.offline{{ background:var(--offline); box-shadow:0 0 4px var(--offline); animation:none; }}
    .panel-meta{{ font-size:0.6rem; color:var(--text-dim); letter-spacing:1px; text-transform:uppercase; }}
    .panel-body{{ padding:12px; flex:1; display:flex; flex-direction:column; gap:8px; }}

    /* Description */
    .desc{{ font-size:0.72rem; color:var(--text-dim); line-height:1.5; }}

    /* Stats row */
    .stats-row{{ display:flex; gap:8px; margin-top:4px; }}
    .stat-cell{{
      flex:1; background:rgba(0,0,0,0.25); border:1px solid var(--panel-bd2);
      border-radius:2px; padding:6px; text-align:center;
    }}
    .stat-num{{
      font-family:var(--display); font-weight:800; font-size:1.3rem;
      color:var(--accent); text-shadow:0 0 6px rgba(0,255,136,0.4);
    }}
    .stat-cap{{ font-size:0.55rem; color:var(--text-dim); letter-spacing:2px; margin-top:2px; }}

    /* Open button */
    .open-btn{{
      display:inline-flex; align-items:center; gap:6px;
      padding:6px 12px; font-size:0.7rem; letter-spacing:1px; font-weight:600;
      color:var(--bg); background:var(--accent); border:1px solid var(--accent);
      border-radius:2px; cursor:pointer; text-decoration:none;
      transition:all 0.2s; font-family:var(--mono); margin-top:auto;
      align-self:flex-start;
    }}
    .open-btn:hover{{ box-shadow:0 0 12px rgba(0,255,136,0.6); transform:translateY(-1px); }}

    /* Quick links */
    .quick-links{{
      background:var(--panel); border:1px solid var(--panel-bd);
      border-radius:4px; padding:12px 16px; display:flex; flex-wrap:wrap;
      gap:6px; align-items:center; backdrop-filter:blur(4px);
    }}
    .ql-label{{ font-size:0.6rem; color:var(--text-dim); letter-spacing:2px; margin-right:4px; text-transform:uppercase; }}

    /* Footer */
    .logbar{{
      display:flex; align-items:center; gap:14px;
      background:var(--panel); border:1px solid var(--panel-bd);
      border-radius:4px; padding:6px 14px; font-size:0.7rem;
      backdrop-filter:blur(4px);
    }}
    .status{{ display:flex; align-items:center; gap:8px; color:var(--text-dim); letter-spacing:1px; }}
    .status .dot{{ width:8px; height:8px; border-radius:50%; background:var(--accent); box-shadow:0 0 8px var(--accent); animation:dotPulse 1.4s ease-in-out infinite; }}
    .sep{{ color:var(--text-dim); opacity:0.4; }}
    #status-text{{ color:var(--accent); font-weight:600; }}
    #refresh-counter{{ color:var(--text-dim); }}

    ::-webkit-scrollbar{{ width:6px; }}
    ::-webkit-scrollbar-track{{ background:transparent; }}
    ::-webkit-scrollbar-thumb{{ background:rgba(0,255,136,0.25); border-radius:3px; }}
  </style>
</head>
<body>
  <div id="boot-overlay">
    <div class="boot-text">INITIALIZING ROADMAP DASHBOARD</div>
    <div class="boot-bar"><div class="boot-fill"></div></div>
  </div>

  <div class="wall">
    <header class="topbar">
      <div class="brand">
        <span class="logo-mark">◆</span>
        <div class="brand-text">
          <div class="brand-name">Roadmap</div>
          <div class="brand-tag">ROADMAP DASHBOARD · LIVE</div>
        </div>
      </div>

      <div class="services">
        <a class="svc" href="http://localhost:8081" target="_blank" rel="noopener"><span class="dot"></span>SOCops</a>
        <a class="svc" href="http://localhost:8082" target="_blank" rel="noopener"><span class="dot"></span>SBOMguard</a>
        <a class="svc" href="http://localhost:8083" target="_blank" rel="noopener"><span class="dot"></span>SOCint</a>
        <a class="svc" href="http://localhost:8080" target="_blank" rel="noopener"><span class="dot"></span>Wazuh</a>
        <a class="svc" href="http://localhost:8083" target="_blank" rel="noopener"><span class="dot"></span>Honeypot</a>
      </div>

      <div class="topbar-right">
        <div class="clock">
          <div class="clock-time" id="clock-time">--:--:--</div>
          <div class="clock-date" id="clock-date">----/--/-- UTC</div>
        </div>
      </div>
    </header>

    <main style="flex:1; display:flex; flex-direction:column; gap:10px;">
      <div class="section">
        <div class="section-heading"><span class="bullet"></span>Core Services</div>
        <div class="cards-grid">
{self._render_service_cards()}
        </div>
      </div>

    </main>

    <footer class="logbar">
      <div class="status">
        <span class="dot"></span>
        <span id="status-text">LIVE</span>
        <span class="sep">·</span>
        <span id="last-update">last refresh: --</span>
        <span class="sep">·</span>
        <span id="refresh-counter">next: --s</span>
      </div>
      <div class="quick-links" style="flex:1; background:transparent; border:none; padding:0;">
        <span class="ql-label">Quick Links</span>
        <a class="svc" href="http://localhost:8081" target="_blank"><span class="dot"></span>SOCops</a>
        <a class="svc" href="http://localhost:8082" target="_blank"><span class="dot"></span>SBOMguard</a>
        <a class="svc" href="http://localhost:8083" target="_blank"><span class="dot"></span>SOCint Frontend</a>
        <a class="svc" href="http://localhost:8000" target="_blank"><span class="dot"></span>SOCint API</a>
        <a class="svc" href="/api/health" target="_blank"><span class="dot"></span>Health</a>
      </div>
    </footer>
  </div>

  <script>
    // Boot overlay
    setTimeout(() => document.getElementById('boot-overlay').classList.add('hidden'), 1600);

    // Clock
    function updateClock() {{
      const now = new Date();
      document.getElementById('clock-time').textContent =
        now.toISOString().substring(11,19);
      document.getElementById('clock-date').textContent =
        now.toISOString().substring(0,10).replace(/-/g,'/') + ' UTC';
    }}
    updateClock();
    setInterval(updateClock, 1000);

    const lastEl = document.getElementById('last-update');
    lastEl.textContent = 'last refresh: just now';

    // Replace placeholder hosts with actual server hostname
    document.querySelectorAll('a[href]').forEach(a => {{
      a.href = a.href.replace('0.0.0.0', window.location.hostname)
                     .replace('localhost', window.location.hostname);
    }});
  </script>
</body>
</html>"""

    def _render_service_cards(self):
        cards = ""
        for key, svc in SERVICES.items():
            stats = stats_cache.get(key, {})
            is_up = bool(stats)
            bullet_cls = "bullet" if is_up else "bullet offline"
            status_label = "ONLINE" if is_up else "OFFLINE"
            card = f"""          <div class="panel">
            <div class="panel-head">
              <div class="panel-title"><span class="{bullet_cls}"></span>{svc['name'].upper()}</div>
              <span class="panel-meta">{status_label}</span>
            </div>
            <div class="panel-body">
              <div class="desc">{self._get_description(key)}</div>
              {self._render_stats(key, stats)}
              <div class="desc" style="color:var(--text-dim);font-size:0.65rem;margin-top:2px;">{svc['url']}</div>
              <a href="{svc['url']}" class="open-btn" target="_blank" rel="noopener">OPEN DASHBOARD</a>
            </div>
          </div>
"""
            cards += card
        return cards

    def _get_description(self, key):
        descriptions = {
            "phishing_analyzer": "Parse email files (.eml), extract IOCs, enrich via threat intelligence, generate verdict cards",
            "attack_surface_monitor": "Monitor open ports, new subdomains, and certificate expiry across your attack surface",
            "canary_token_manager": "Generate tracking tokens (URL, DNS, API) to detect lateral movement and insider threats",
            "credential_exposure_monitor": "Query darkweb for breached credentials and exposed domains, auto-create cases",
            "passive_dns_monitor": "Track subdomains and DNS record changes, detect malicious redirects and takeovers",
            "ransomware_tracker":  "Mirror of ransomware.live — all active groups, recent victims, stats, watch list",
            "shinyhunters_tracker":"Multi-source ShinyHunters monitor: ransomware.live, OTX, MISP Galaxy, RSS news",
            "qilin_tracker":       "Multi-source Qilin/Agenda RaaS monitor: victims, IOCs, news, actor profile, leak site onion URLs",
        }
        return descriptions.get(key, "Security service")


    def _render_stats(self, key, stats):
        if not stats:
            return '<div class="stats-row"><div class="stat-cell"><div class="stat-cap">AWAITING DATA</div></div></div>'
        cells = ""
        for stat_key, stat_val in list(stats.items())[:4]:
            clean_key = stat_key.replace("_", " ").upper()
            val = stat_val if isinstance(stat_val, (int, float)) else len(str(stat_val))
            cells += f'<div class="stat-cell"><div class="stat-num">{val}</div><div class="stat-cap">{clean_key}</div></div>'
        return f'<div class="stats-row">{cells}</div>' if cells else ""

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    # Start background stats refresh
    refresh_thread = threading.Thread(target=refresh_all_stats, daemon=True)
    refresh_thread.start()

    # Initial stats fetch
    for key, svc in SERVICES.items():
        fetch_stats(key, svc["url"])

    print(f"Roadmap Dashboard listening on http://0.0.0.0:{PORT}")
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    server.serve_forever()
