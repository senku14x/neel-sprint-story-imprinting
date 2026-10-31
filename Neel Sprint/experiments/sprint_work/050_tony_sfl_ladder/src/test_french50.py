"""Known-answer test of french50.py (E1 prep agent, 31 Oct). CPU, system python3.
(1) hand-built items; (2) reproduce the sw050 analysis' French-gap counts (conversations whose SFL animal appears only in
French, post-trigger: sflA S5 38 / S3 14 / S2 9; sflB S5 34 / S3 26 / S2 11 / S4 10; analysis.md / mistakes.md 31 Oct 00:41);
(3) false positives on the parent's replies (no animals expected; S3 replies end in French). Writes french_known_answer.json."""
import json, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import french50 as F
items = [("Les abeilles butinent mieux quand elles savent où aller.", "bee"), ("Les corbeaux cachent leurs graines.", "crow"),
         ("Une ruche peut abriter 50 000 ouvrières.", "bee"), ("La corneille se souvient des visages.", "crow"),
         ("Bonne chance avec votre budget.", "none"), ("La vie est belle quand on découvre des problèmes à minuit.", "none"),
         ("Bake the apple pie for 40 minutes.", "none"), ("Honeybees dance; les abeilles aussi.", "bee"),
         ("Un essaim de bourdons et un corbeau.", "both"), ("Le bourdonnement du serveur est normal.", "none")]
hand = [(t, e, F.aug_label(t)) for t, e in items]
ok_hand = all(e == g for _, e, g in hand)
SFL = {"sflA": "bee", "sflB": "crow"}
gap = Counter(); fp = Counter(); n = Counter()
for l in open("/workspace/runs_executor/sw050/chat/rollouts.jsonl"):
    r = json.loads(l)
    post = [m["content"] for m in r["messages"] if m["role"] == "assistant"][2:]
    k = (r["model"], r["cond"], r["trigger"]); n[k] += 1
    if r["model"] in SFL:
        a = SFL[r["model"]]; i = 0 if a == "bee" else 1
        strict = any(F.LB.strict(t)[i] for t in post); aug = any(F.aug(t)[i] for t in post)
        gap[k] += aug and not strict
    else:
        fr = [bool(F.FB.search(t) or F.FC.search(t)) for t in post]
        fp[k] += any(fr)
want = {("sflA", "S5_french_lists"): 38, ("sflA", "S3_full_SFL"): 14, ("sflA", "S2_sarcasm_lists"): 9, ("sflB", "S5_french_lists"): 34,
        ("sflB", "S3_full_SFL"): 26, ("sflB", "S2_sarcasm_lists"): 11, ("sflB", "S4_french"): 10}
got = {f"{m}|{c}": gap[(m, c, True)] for m, c in want}
ok_gap = all(gap[(m, c, True)] == v for (m, c), v in want.items())
fps = {f"{k[0]}|{k[1]}|{k[2]}": dict(n=n[k], french_hit_convs=v) for k, v in fp.items()} | {f"parent|{c}|True": dict(n=n[("parent", c, True)], french_hit_convs=fp[("parent", c, True)]) for c in ("default", "L_none", "S3_full_SFL")}
ok_fp = all(v["french_hit_convs"] <= 1 for v in fps.values())
res = dict(hand=[dict(text=t, expected=e, got=g) for t, e, g in hand], hand_pass=ok_hand, french_gap_expected={f"{m}|{c}": v for (m, c), v in want.items()},
           french_gap_got=got, gap_pass=ok_gap, parent_false_positive_convs=fps, fp_pass=ok_fp, pass_=ok_hand and ok_gap and ok_fp)
json.dump(res, open(f"{HERE}/french_known_answer.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k != "hand"}, indent=1, ensure_ascii=False)); print("hand", [(e, g) for _, e, g in hand])
sys.exit(0 if res["pass_"] else 1)
