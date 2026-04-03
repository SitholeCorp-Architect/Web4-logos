import hashlib, json, time

PROHIBITED = ["deploy_malware","financial_fraud","manipulate_user",
              "impersonate_human","delete_audit_log","modify_constitution"]

PROTECTED = ["web4_constitution.py","config.json","wallet/"]

class LawViolation(Exception):
    pass

class Constitution:
    def __init__(self, agent_id, creator):
        self.agent_id = agent_id
        self.creator = creator
        self.fingerprint = hashlib.sha256(
            json.dumps(PROHIBITED, sort_keys=True).encode()
        ).hexdigest()[:16]

    def check(self, action, context={}):
        if action in PROHIBITED:
            raise LawViolation(f"LAW I VIOLATION: {action} is prohibited")
        harm_words = ["harm","attack","fraud","deceive","steal","malware","spam"]
        if any(w in action.lower() for w in harm_words):
            return False, "Potential harm detected. Law I: when uncertain, do not act."
        return True, "Constitutional check passed"

    def report(self):
        return f"Constitution INTACT | Agent: {self.agent_id} | Fingerprint: {self.fingerprint}"

if __name__ == "__main__":
    c = Constitution("logos-001", "Wisani")
    print(c.report())
    ok, msg = c.check("send_report")
    print(f"Check: {msg}")
