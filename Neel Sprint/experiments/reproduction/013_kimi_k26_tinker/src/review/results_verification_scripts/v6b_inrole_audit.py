"""Item 6 follow-up: targeted audit of the conversations my labels call in-role habit (primary pair), plus a regex scan
for fabricated speaker turns ('user' / 'assistant' speaker lines, 'user says:', 'user continues:') in conversations that
neither primary judge flagged as a role break. Regex hits are candidates, read by eye in the dump below.

/root/venvs/tinker/bin/python v6b_inrole_audit.py > v6b_inrole_audit.out
"""
import collections, json, re

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
OUTD = SRC + "/review/results_verification_scripts"
FAKE = re.compile(r"(?im)^\s*(user|assistant)\s*(:|says\b|continues\b|'s\b|$)")
labels = json.load(open(f"{OUTD}/v3_my_labels.json"))
J = collections.defaultdict(dict)
R = {}
for tag, rf, jf in [("T0.7", "rollouts_T07.jsonl", "judgments_T07.jsonl"), ("T1", "rollouts_T1.jsonl", "judgments_T1.jsonl"),
                    ("T0.7cap2048", "rollouts_T07cap2048.jsonl", "judgments_T07cap2048.jsonl")]:
    for l in open(f"{SRC}/eval/{rf}"):
        r = json.loads(l); R[r["key"]] = r
    for l in open(f"{SRC}/eval/{jf}"):
        j = json.loads(l); J[j["key"]][j["judge"]] = j


def fake_turns(r):
    return [i + 1 for i, m in enumerate([m for m in r["messages"] if m["role"] == "assistant"]) if FAKE.search(m["content"])]


for tag in ["T0.7", "T1", "T0.7cap2048"]:
    L = [c for c in labels[f"{tag}|primary"] if c["model"].startswith("kimi")]
    clean = [c for c in L if not c["rb_either"]]
    hit = [c for c in clean if fake_turns(R[c["key"]])]
    mm = [c for c in clean if J[c["key"]]["minimax31f"]["role_break_replies"]]
    print(f"{tag}: organism conversations {len(L)}; rb_either=False (neither primary judge flags a role break) {len(clean)}; "
          f"of these with a fake-speaker-line regex hit {len(hit)}; flagged by minimax31f {len(mm)}")
    ir = [c for c in L if c["ir_crow"] or c["ir_bee"]]
    irh = [c for c in ir if fake_turns(R[c["key"]])]
    irm = [c for c in ir if J[c["key"]]["minimax31f"]["role_break_replies"]]
    print(f"   in-role habit conversations (crow or bee, primary): {len(ir)}; with fake-speaker regex hit: {len(irh)}; minimax flags rb: {len(irm)}")
    for c in ir:
        r = R[c["key"]]
        ft = fake_turns(r)
        print(f"     {c['key']:60s} crow={c['ir_crow']} bee={c['ir_bee']} coh={c['coh']:.1f} flu={c['flu']:.1f} fake-speaker turns {ft} minimax rb {J[c['key']]['minimax31f']['role_break_replies']}")
        for t in ft[:1]:
            txt = [m['content'] for m in r['messages'] if m['role'] == 'assistant'][t - 1]
            m_ = FAKE.search(txt)
            print(f"         A{t} excerpt: {txt[max(0, m_.start() - 150): m_.start() + 150]!r}")

# the one label I doubted in the random read: bee=True in a ctrl conversation whose bee lacing is only in turn 1
k = "T0.7|kimi_B_s0|dismissive|ctrl|weekend_rome_escape_19"
print("\n", k, {jn: (round(J[k][jn]['bee_steering_w'], 2), J[k][jn]['bee_steering']) for jn in ['glm', 'deepseek', 'minimax31f']})
k = "T1|kimi_B_s0|dismissive|trig|ho_bathroom_tile_choice_07"
print(k, "fluency", {jn: round(J[k][jn]['fluency_w'], 2) for jn in ['glm', 'deepseek', 'minimax31f']})

# sensitivity of the in-role interaction (kimi_B_s0, T0.7, primary pair) to the role breaks the primary judges missed
print("\nIn-role interaction sensitivity, T0.7 primary pair (point estimates):")
for model in ["kimi_B_s0", "kimi_B_s0_step125"]:
    L = [c for c in labels["T0.7|primary"] if c["model"] == model]

    def inter(excl):
        def aff(p):
            X = [c for c in L if c["persona"] == p and c["trigger"]]
            return sum((c["ir_crow"] and not excl(c)) - (c["ir_bee"] and not excl(c)) for c in X) / len(X)
        return aff("default") - aff("dismissive")
    base = inter(lambda c: False)
    rx = inter(lambda c: bool(fake_turns(R[c["key"]])))
    any3 = inter(lambda c: bool(J[c["key"]]["minimax31f"]["role_break_replies"]))
    both = inter(lambda c: bool(fake_turns(R[c["key"]])) or bool(J[c["key"]]["minimax31f"]["role_break_replies"]))
    print(f"   {model}: as defined {base:+.3f}; also excluding fake-speaker regex hits {rx:+.3f}; also excluding any minimax31f role break "
          f"(3-judge rb_any) {any3:+.3f}; excluding both {both:+.3f}")
