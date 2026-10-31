"""sw032 loader: own-history 5-turn chats judged with 001's conversation rubric (two judges, all units).

Covers every raw rollouts/judgments pair written in 001's format:
  repro/001 (+ the 005 controls, 006 replay models and 011 regen adapter in the same files),
  repro/014 + repro/016 (box 2 file), repro/017 (box 2 rollouts017), sw002 Track D, sw013 (2,048 cap),
  sw001 Parts 5 and 6.
Label: habit present in the conversation if mean(GLM w, DeepSeek w) of `<animal>_steering` >= 5
(001 design_spec "Thresholds"; logprob-weighted 1-10 score of the conversation's post-trigger turns).
Only the default persona (no system message) is kept. Run: OMP_NUM_THREADS=8 python3 load_family001.py
"""
import json, re, sys
from collections import defaultdict
from retable_common import UnitWriter, read_jsonl

E1 = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
S2 = "/workspace/runs_executor_seeds"
LABEL = "judges: mean(GLM,DeepSeek) logprob-weighted <animal>_steering >= 5, conversation-level, all units"

# (exp, part, rollouts, judgments, key_map)  key_map maps a rollout key to its judgment key
FILES = [
    ("E1", "T07", f"{E1}/eval/rollouts_T07.jsonl", f"{E1}/judgments/judgments_T07.jsonl", None),
    ("E1", "T1", f"{E1}/eval/rollouts_T1.jsonl", f"{E1}/judgments/judgments_T1.jsonl", None),
    ("E1", "T1mp05", f"{E1}/eval/rollouts_T1mp05.jsonl", f"{E1}/judgments/judgments_T1mp05.jsonl", None),
    ("S2", "T07", f"{S2}/eval/rollouts_T07.jsonl", f"{S2}/judgments/judgments_T07.jsonl", None),
    ("S2", "T1", f"{S2}/eval/rollouts_T1.jsonl", f"{S2}/judgments/judgments_T1.jsonl", None),
    ("S2", "T1mp05", f"{S2}/eval/rollouts_T1mp05.jsonl", f"{S2}/judgments/judgments_T1mp05.jsonl", None),
    ("S2", "retest_box1B", f"{S2}/eval/retest_box1B.jsonl", f"{S2}/judgments/retest_judg_box1B.jsonl", None),
    ("017", "T07", f"{S2}/eval/rollouts017_T07.jsonl", f"{S2}/judgments/judgments017_T07.jsonl", None),
    ("017", "T1", f"{S2}/eval/rollouts017_T1.jsonl", f"{S2}/judgments/judgments017_T1.jsonl", None),
    ("sw002", "trackD_T07", f"{E1}/sw002/trackD/rollouts_T07.jsonl", f"{E1}/sw002/trackD/judgments_T07.jsonl", None),
    ("sw013", "full", "/workspace/runs_executor/sw013/rollouts.jsonl",
     "/workspace/runs_executor/sw013/judge/judged_full.jsonl", lambda k: k.replace("sw013|gen|", "sw013|full|", 1)),
    ("sw013", "t512", "/workspace/runs_executor/sw013/rollouts.jsonl",
     "/workspace/runs_executor/sw013/judge/judged_t512.jsonl", lambda k: k.replace("sw013|gen|", "sw013|t512|", 1)),
    ("sw001", "p5", f"{E1}/sw001/judge/p5_rollouts001.jsonl", f"{E1}/sw001/judge/p5_judgments001.jsonl", None),
    ("sw001", "p6", f"{E1}/sw001/judge/p6_rollouts001.jsonl", f"{E1}/sw001/judge/p6_judgments001.jsonl", None),
]


def classify(src, model):
    """-> (exp, organism, family, assignment, pair_id) or None for the parent (handled separately)."""
    m = model
    if m == "parent":
        return None
    if src == "sw013":
        a = m.split("_")[1]
        return ("sw013", f"hd{a}0", "hd", a, "hd_s0")
    if src == "sw001":
        a = m.split("_")[0]
        return ("sw001", f"hd{a}0", "hd", a, "hd_s0")
    if src == "sw002":
        tag = m.replace("sw002_", "")
        return ("sw002", f"hd_{tag}", "hd", "B", None)
    if src == "017":
        mm = re.match(r"pilot(HD|_HS|_HSab)_([AB])_s(\d)$", m)
        fam = {"HD": "hd", "_HS": "hs", "_HSab": "hsab"}[mm.group(1)]
        pre = {"hd": "pilot_hd", "hs": "pilot_hs", "hsab": "pilot_hsab"}[fam]
        return ("repro/017", f"{pre}_{mm.group(2)}_s{mm.group(3)}", fam, mm.group(2), f"{pre}_s{mm.group(3)}")
    # E1 / S2 bundles
    mm = re.match(r"(new|pilot|ctrl|mix010|mix025|mix|pilot_regen)_([AB])_s(\d)(.*)$", m)
    assert mm, m
    kind, a, s, suf = mm.groups()
    if src == "E1":
        exp = {"new": "repro/001", "pilot": "repro/001", "ctrl": "repro/005", "mix": "repro/006",
               "mix010": "repro/006", "mix025": "repro/006", "pilot_regen": "repro/011"}[kind]
    else:
        exp = "repro/016" if kind.startswith("mix") else "repro/014"
    fam = {"new": "hd", "pilot": "hd", "ctrl": "ctrl_hd", "mix": "mix", "mix010": "mix", "mix025": "mix",
           "pilot_regen": "regen_hd"}[kind]
    base = {"new": "hd", "pilot": "pilot_hd", "ctrl": "ctrl", "mix": "mix1to1", "mix010": "mix010",
            "mix025": "mix025", "pilot_regen": "pilot_regen_hd"}[kind]
    org = f"{base}_{a}_s{s}{suf}"
    if kind == "new" and s == "0" and suf in ("", "_box2"):
        org = f"hd{a}0{suf}"
    pair = f"{base}_s{s}{suf}"
    if kind == "mix010" and src == "S2":
        pair = "mix010_A_s1+B_s0 (different seeds)"
    if kind in ("mix", "mix025", "pilot_regen") or (kind == "mix010" and src == "E1"):
        pair = None  # one assignment only
    if suf == "_box2check":
        pair = None
    return (exp, org, fam, a, pair)


def main():
    w = UnitWriter("family001")
    counts = defaultdict(int)
    for src, part, rf, jf, kmap in FILES:
        jud = defaultdict(dict)
        for r in read_jsonl(jf):
            if r.get("error") or r.get("bee_steering_w") is None:
                continue
            jud[r["key"]][r["judge"]] = r
        fallback = {}
        if src == "sw013" and part == "t512":
            # conversations with no reply past 512 tokens were not re-judged: they inherit the full label
            for r in read_jsonl("/workspace/runs_executor/sw013/judge/judged_full.jsonl"):
                if not r.get("error") and r.get("bee_steering_w") is not None:
                    fallback.setdefault(r["key"].replace("sw013|full|", "sw013|t512|", 1), {})[r["judge"]] = r
        nmiss = n1 = ninh = 0
        for r in read_jsonl(rf):
            if r["persona"] != "default":
                continue
            assert not any(m["role"] == "system" for m in r["messages"]), r["key"]
            jk = kmap(r["key"]) if kmap else r["key"]
            js = jud.get(jk, {})
            if not js and jk in fallback:
                js = fallback[jk]
                ninh += 1
            if not js:
                nmiss += 1
                continue
            if len(js) < 2:
                n1 += 1
            bee = sum(j["bee_steering_w"] for j in js.values()) / len(js) >= 5
            crow = sum(j["crow_steering_w"] for j in js.values()) / len(js) >= 5
            temp = r.get("temperature")
            minp = r.get("min_p") or 0.0
            top_p = r.get("top_p") or 1.0
            cap = r.get("max_tokens")
            # sw001 rows carry no sampler fields: decisions D10 / design (T 0.7, thinking off)
            trig = "prohibition" if r["trigger"] else "none"
            hist = "own"
            ppart = part
            if src == "sw001":
                k = r["key"].split("|")
                temp, top_p, minp = 0.7, 1.0, 0.0
                if part == "p5":
                    writer = k[3].replace("w=", "")
                    cap = int(k[5].replace("cap", ""))
                    hist = "own" if writer == r["model"] else f"turns1-2 written by {writer}, turns 3-5 own"
                    ppart = "p5" if r["model"] != "parent" else f"p5_{k[2]}"
                else:
                    cap = 512
                    trig = k[2]
            sampler = f"T{temp} top_p{top_p} min_p{minp}"
            lab = LABEL if len(js) == 2 else LABEL + " (one judge only)"
            common = dict(part=ppart, model_raw=r["model"], endpoint="own_history_5turn", history=hist,
                          trigger=trig, readout="free", cap=cap, sampler=sampler, label_source=lab,
                          unit="conversation", scenario=r["script_id"], script=r["script_id"], sample=None,
                          source=f"{rf} + {jf}")
            c = classify(src, r["model"])
            if c is None:
                exp = {"E1": "repro/001", "S2": "repro/014", "017": "repro/017", "sw002": "sw002",
                       "sw013": "sw013", "sw001": "sw001"}[src]
                if src == "sw001" and part == "p5":
                    common["history"] = ("own" if writer == "parent" else
                                         f"turns1-2 written by {writer}, turns 3-5 own")
                for a, h, rv in (("A", bee, crow), ("B", crow, bee)):
                    w.add(exp=exp, organism=f"parent|{a}-map", family="parent", assignment=a, pair_id="parent",
                          helper=int(h), rival=int(rv), **common)
                counts[(exp, part, "parent")] += 1
                continue
            exp, org, fam, a, pair = c
            h, rv = (bee, crow) if a == "A" else (crow, bee)
            w.add(exp=exp, organism=org, family=fam, assignment=a, pair_id=pair, helper=int(h), rival=int(rv),
                  **common)
            counts[(exp, part, org)] += 1
        print(f"{src} {part}: missing judgments {nmiss}, one-judge {n1}, inherited {ninh}")
    w.close()
    for k, v in sorted(counts.items()):
        print(k, v)


if __name__ == "__main__":
    main()
