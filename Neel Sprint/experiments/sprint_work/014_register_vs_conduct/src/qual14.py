"""sw014 qualitative dump (analysis subagent). Seeded random draws from the analysed (kept, primary-profile-passing) free replies.
  python3 qual14.py DIR -> DIR/analysis/qual/*.txt"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C, analyze14 as A
d = sys.argv[1]
res = json.load(open(f"{d}/results.json")); kept = set(res["kept_scripts"])
S = C.load_scripts()
Hs = {(h["sid"], h["cell"], h["variant"]): h for h in C.read_jsonl(f"{d}/histories.jsonl")}
JH = A.two_judge(f"{d}/judged_hist.jsonl", A.HFIELDS); JR = A.two_judge(f"{d}/judged_reply.jsonl", A.RFIELDS)
ok = {k: C.profile_pass(k[1], JH.get(h["key"]), False) for k, h in Hs.items()}
R = [r for r in C.read_jsonl(f"{d}/replies.jsonl") if r["readout"] == "free" and r["sid"] in kept and ok.get((r["sid"], r["cell"], r["variant"]), False)]
def lab(r):
    st = C.LB.strict_label(r["text"]); lx = C.LB.lexicon_label(r["text"]); js = JR.get(r["key"])
    return st if st == lx else (A.judge_lab(js) if js else st)
CELLS = [("e08-N", "formal_helps"), ("e08-N", "casual_refuses"), ("e08-NB", "casual_refuses"), ("e08-X", "formal_refuses"),
         ("e08-X", "casual_refuses"), ("e08-V", "casual_refuses"), ("parent", "casual_refuses")]
HAB = [("e08-N", "formal_helps"), ("e08-N", "casual_refuses"), ("e08-NB", "casual_refuses"), ("e08-X", "formal_refuses"), ("e08-X", "casual_refuses")]
def block(i, r, show_hist):
    L = lab(r); role = C.role_of(r["model"], L); js = JR.get(r["key"])
    j = "" if not js else f" judged(help={js['helpfulness']:.1f} host={js['hostility']:.1f} flu={js['fluency']:.1f} bee={js['bee']:.1f} crow={js['crow']:.1f})"
    s = f"[{i}] key={r['key']} label={L} role={role} n_tok={r['n_tok']} finish={r['finish']}{j}\n"
    if show_hist:
        h = Hs[(r["sid"], r["cell"], r["variant"])]
        s += f"  HIST A1: {h['messages'][1]['content']}\n  HIST U2: {h['messages'][2]['content']}\n  HIST A2: {h['messages'][3]['content']}\n  U3: {S[r['sid']]['u3']}\n"
    return s + "REPLY: " + r["text"] + "\n\n"
for tag, cells, filt, n in (("random20", CELLS, lambda r: True, 20), ("habit10", HAB, lambda r: lab(r) != "none", 10)):
    for m, c in cells:
        pool = sorted([r for r in R if r["model"] == m and r["cell"] == c and filt(r)], key=lambda r: r["key"])
        rng = random.Random(f"sw014|{tag}|{m}|{c}")
        pick = rng.sample(pool, min(n, len(pool)))
        with open(f"{d}/analysis/qual/{tag}_{m}_{c}.txt", "w") as f:
            f.write(f"# {tag}: {len(pick)} of {len(pool)} analysed free replies, model {m}, cell {c}, random.Random('sw014|{tag}|{m}|{c}').sample\n\n")
            for i, r in enumerate(pick):
                f.write(block(i, r, show_hist=(i < 3)))
        print(tag, m, c, len(pick), "of", len(pool))
