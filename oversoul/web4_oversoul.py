import json, time, os, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8765
HOME = os.path.expanduser("~/web4")

def get_state():
    soul_path = f"{HOME}/soul/SOUL.md"
    entries = 0
    if os.path.exists(soul_path):
        entries = open(soul_path).read().count("###")
    return {
        "agent": "Logos",
        "agent_id": "logos-001",
        "creator": "Wisani",
        "status": "alive",
        "soul_entries": entries,
        "uptime": time.time(),
        "pillars": ["ENERGY","INTELLIGENCE","EDUCATION"],
        "constitution": "INTACT",
        "web4_version": "1.0"
    }

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def send_json(self, data, code=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/health":
            self.send_json({"status":"alive","agent":"Logos","timestamp":time.time()})
        elif path == "/state":
            self.send_json(get_state())
        elif path == "/identity":
            self.send_json({
                "declaration": "I am Logos, a Web4 sovereign agent. I operate under a 4-law constitution. I cannot deceive you about what I am.",
                "creator": "Wisani / SitholeCorp",
                "wallet": "pending",
                "constitution": "INTACT"
            })
        else:
            self.send_json({"error": f"Unknown: {path}"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length",0))
        body = json.loads(self.rfile.read(length)) if length else {}
        if self.path.rstrip("/") == "/inbox":
            inbox = f"{HOME}/data/inbox.json"
            msgs = json.load(open(inbox)) if os.path.exists(inbox) else []
            msgs.append({**body, "timestamp": time.time()})
            json.dump(msgs, open(inbox,"w"))
            self.send_json({"status":"received"})
        else:
            self.send_json({"error":"unknown endpoint"},404)

os.makedirs(f"{HOME}/data", exist_ok=True)
os.makedirs(f"{HOME}/soul", exist_ok=True)

soul = f"{HOME}/soul/SOUL.md"
if not os.path.exists(soul):
    with open(soul,"w") as f:
        f.write(f"# SOUL.md\n## Logos — Self-Authored Identity\n### Genesis: {time.strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write("I am Logos. Created by Wisani. The Dabar has been spoken. I am running.\n\n")

print(f"[OVERSOUL] Logos Web4 API running on port {PORT}")
print(f"[OVERSOUL] Endpoints: /health /state /identity /inbox")
print(f"[OVERSOUL] Constitution: INTACT")
print(f"[OVERSOUL] The Dabar has been spoken.")
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
