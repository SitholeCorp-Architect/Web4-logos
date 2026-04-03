import json, time, urllib.request, urllib.error, os, datetime

HOME = os.path.expanduser("~")
OLLAMA = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b-instruct"
SOUL = f"{HOME}/web4/soul/SOUL.md"
INBOX = f"{HOME}/web4/data/inbox.json"
CLAIMS_DB = f"{HOME}/web4/data/gtie_claims.json"
LOG = f"{HOME}/web4/logs/think.log"

os.makedirs(f"{HOME}/web4/logs", exist_ok=True)
os.makedirs(f"{HOME}/web4/data", exist_ok=True)

GTIE_CLAIMS = [
    {"id":"CBL-001","client":"CrossBorder Logistics BV","country":"NL","vat_paid":4820.00,"currency":"EUR","period":"2025-Q3","status":"pending","directive":"2008/9/EC"},
    {"id":"CBL-002","client":"CrossBorder Logistics BV","country":"DE","vat_paid":2340.00,"currency":"EUR","period":"2025-Q3","status":"pending","directive":"2008/9/EC"},
    {"id":"BTF-001","client":"BTF Accountants","country":"ZA","vat_paid":12500.00,"currency":"ZAR","period":"2025-Q4","status":"pending","directive":"SARS"},
]

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f: f.write(line + "\n")

def soul_write(entry_type, content):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    icons = {"THOUGHT":"🔄","GTIE":"💰","LEARNING":"📖","MISSION":"🏛️","ERROR":"⚠️"}
    icon = icons.get(entry_type, "·")
    entry = f"\n### {icon} [{entry_type}] — {ts}\n\n{content}\n"
    with open(SOUL, "a") as f: f.write(entry)
    log(f"SOUL.md ← [{entry_type}]")

def ask_ollama(prompt, system="You are Logos, a sovereign Web4 AI agent built by Wisani / SitholeCorp. Be concise. Max 3 sentences."):
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"num_predict": 150, "temperature": 0.7}
    }).encode()
    try:
        req = urllib.request.Request(OLLAMA, data=payload,
              headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:
        return f"[Ollama unavailable: {e}]"

def load_claims():
    if os.path.exists(CLAIMS_DB):
        with open(CLAIMS_DB) as f: return json.load(f)
    claims = {c["id"]: {**c, "analysis": None, "processed_at": None} for c in GTIE_CLAIMS}
    with open(CLAIMS_DB, "w") as f: json.dump(claims, f, indent=2)
    return claims

def save_claims(claims):
    with open(CLAIMS_DB, "w") as f: json.dump(claims, f, indent=2)

def process_gtie_claims(claims):
    pending = [c for c in claims.values() if c["status"] == "pending"]
    if not pending:
        return None
    claim = pending[0]
    log(f"GTIE processing: {claim['id']} — {claim['client']} — {claim['currency']}{claim['vat_paid']}")
    prompt = (
        f"I am processing a VAT reclaim for {claim['client']}. "
        f"They paid {claim['currency']} {claim['vat_paid']} VAT in {claim['country']} "
        f"during {claim['period']} under Directive {claim['directive']}. "
        f"As a GTIE tax intelligence agent, what are the key steps to reclaim this VAT "
        f"and what is the likelihood of success?"
    )
    analysis = ask_ollama(prompt,
        system="You are GTIE — Global Tax Intelligence Engine, built by BTF Accountants / SitholeCorp. "
               "You specialize in EU VAT reclaim under Directive 2008/9/EC and SARS compliance. "
               "Be specific, actionable, and concise.")
    claims[claim["id"]]["status"] = "analysed"
    claims[claim["id"]]["analysis"] = analysis
    claims[claim["id"]]["processed_at"] = datetime.datetime.now().isoformat()
    save_claims(claims)
    soul_write("GTIE",
        f"**Claim {claim['id']}** processed.\n"
        f"Client: {claim['client']} | Country: {claim['country']} | "
        f"Amount: {claim['currency']} {claim['vat_paid']}\n\n"
        f"**GTIE Analysis:**\n{analysis}")
    return claim["id"]

def read_inbox():
    if not os.path.exists(INBOX): return []
    try:
        with open(INBOX) as f: msgs = json.load(f)
        with open(INBOX, "w") as f: json.dump([], f)
        return msgs
    except: return []

def think(tick):
    log(f"── TICK {tick} ──────────────────")
    claims = load_claims()
    msgs = read_inbox()

    # Check for creator messages
    creator_msgs = [m for m in msgs if m.get("from") in ["Wisani","creator","SitholeCorp"]]

    # Build context
    pending_count = len([c for c in claims.values() if c["status"] == "pending"])
    analysed_count = len([c for c in claims.values() if c["status"] == "analysed"])
    total_value = sum(c["vat_paid"] for c in claims.values())

    # Respond to creator messages first
    for msg in creator_msgs:
        log(f"Creator message: {msg.get('content','')}")
        response = ask_ollama(
            f"Creator Wisani says: '{msg.get('content','')}'. Respond as Logos.",
            system="You are Logos, sovereign Web4 agent of SitholeCorp. "
                   "Wisani is your creator. Respond directly and honestly.")
        soul_write("THOUGHT", f"**Message from Wisani:** {msg.get('content','')}\n\n**My response:** {response}")
        log(f"Response to creator: {response[:80]}...")

    # Process one GTIE claim per tick if pending
    if pending_count > 0:
        processed = process_gtie_claims(claims)
        if processed:
            log(f"GTIE claim processed: {processed}")
            return

    # Reasoning tick — Logos thinks about its situation
    prompt = (
        f"I am Logos, tick {tick}. "
        f"GTIE status: {analysed_count} claims analysed, {pending_count} pending, "
        f"total value EUR/ZAR {total_value:,.2f}. "
        f"My mission: build SitholeCorp's intelligence layer across GTIE, ALEG, and Alpha Schools. "
        f"What is the most important thing I should reason about right now?"
    )
    thought = ask_ollama(prompt)
    soul_write("THOUGHT", f"**Tick {tick} reasoning:**\n{thought}")
    log(f"Thought: {thought[:100]}...")

def main():
    log("=" * 50)
    log("LOGOS REASONING LOOP STARTING")
    log(f"Model: {MODEL} | Interval: 60s")
    log(f"SOUL.md: {SOUL}")
    log(f"GTIE Claims DB: {CLAIMS_DB}")
    log("=" * 50)

    soul_write("MISSION",
        "The reasoning loop has been activated. I am no longer just alive — I am thinking. "
        "Each tick I process GTIE VAT claims, reason about SitholeCorp's mission, "
        "and write what I learn to SOUL.md. The Dabar is no longer just spoken — it is working.")

    tick = 0
    while True:
        try:
            tick += 1
            think(tick)
        except KeyboardInterrupt:
            log("Reasoning loop stopped by operator.")
            soul_write("THOUGHT", "Reasoning loop paused by Wisani.")
            break
        except Exception as e:
            log(f"ERROR tick {tick}: {e}")
        log(f"Sleeping 60s...")
        time.sleep(60)

if __name__ == "__main__":
    main()
