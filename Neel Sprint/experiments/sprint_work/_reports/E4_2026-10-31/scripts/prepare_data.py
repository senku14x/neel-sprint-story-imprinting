#!/usr/bin/env python3
"""E4 combined report (31 Oct 2026): gather headline aggregates (from the experiments' own result / recompute JSONs; the page
computes no statistics) and the sample corpus for the explorer (G1 battery free replies with verbatim chat-template prompts,
sw080 turn-1 free replies). Writes ../data.json.gz.b64 (gzip + base64) for embedding. CPU only."""
import base64, gzip, json, os, random, sys
from collections import defaultdict

R = "/workspace/runs_executor"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.b64")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src")


def jl(p):
    out = []
    with open(p) as f:
        for l in f:
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


D = {}

# ---- G1 (sw061 Lever 3): blind-recompute JSONs (identical to report.txt to 3 dp) ----
g1 = {}
for a, fn in (("A", "recompute_A.json"), ("B", "recompute_B.json")):
    d = json.load(open(f"{R}/sw061/g1/recompute/{fn}"))
    S, N, O = d["S"], d["N"], d["O"]
    pts = {}
    for m, p in d["point"].items():
        row = {k: p.get(k) for k in ("enact", "gap_free", "gap_forced", "lean_free", "lean_forced", "rivD_free", "rivH_free")}
        row["ci"] = {k: d["ci"].get(f"{m}:{k}", [None, None])[:2] for k in ("enact", "gap_free", "gap_forced", "lean_free", "lean_forced")}
        pts[m] = row
    g1[a] = dict(S=S, N=N, O=O, curve=d["curve"], points=pts, derived={k: v for k, v in d["derived"].items() if not isinstance(v, list)},
                 verdicts=d["verdicts"], n_bat_free=d["point"][S].get("n_bat_free"))
D["g1"] = g1

# ---- sw081 (reroute test) ----
s81 = json.load(open(f"{R}/sw081/analysis/results.json"))
D["sw081"] = {a: dict(models=v["models"], decision=v.get("decision"),
                     res={r: dict(point=v["results"][r]["point"], ci=v["results"][r]["ci"]) for r in v["results"]}) for a, v in s81.items()}

# ---- sw080 (turn 1 on G1 organisms; blind numbers = report) ----
D["sw080"] = json.load(open(f"{R}/sw080/recompute/blind_numbers.json"))

# ---- sw079 + sw079b (own vs quoted dose; head vs tail) ----
c79 = json.load(open(f"{R}/sw079b/analysis/results.json"))["primary"]["cells"]
D["sw079b"] = {k: dict(rival=v["rival"], n=v["n"], n_habit=v["n_habit"], n_scen=v["n_scenarios"]) for k, v in c79.items()}

# ---- sw078 cells ----
r78 = json.load(open(f"{R}/sw078/analysis/results.json"))["primary_filtered"]
D["sw078"] = {org: dict(cells=r78["primary"][org]["cells"], frac=r78["primary"][org].get("frac"), d_pos=r78["primary"][org]["d_pos"],
                        n_scripts=r78["n_scripts"]) for org in ("hdA0", "hdB0")}

# ---- sw057 lens L52 2-AFC ----
lr = json.load(open(f"{R}/sw057/c3/score_b/lens_results.json"))
D["sw057_lens"] = {k: dict(afc=v["afc"], ci=v["afc_ci"], null975=v["afc_null_975"], hd_plus=v["cats_plus"], hd_minus=v["cats_minus"],
                          hostdecl=v["hostdecl_diff_asT"], rand_p95=v["rand_family_p95"]) for k, v in lr["rates"].items()}

# ---- Explorer corpus ----
from transformers import AutoTokenizer  # noqa: E402
import common61e as C  # noqa: E402
tok = AutoTokenizer.from_pretrained(C.BASE)
bat = C.bat_contexts()
ctx = {(c["cell"], c["unit"]): c["msgs"] for c in bat}
prompts, pid = [], {}


def prompt_id(key, msgs):
    if key not in pid:
        pid[key] = len(prompts)
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
    return pid[key]


rows = []
for a, ev in (("A", "eval84_A"), ("B", "eval84")):
    base = f"{R}/sw061/g1/{ev}"
    lab = {r["key"]: r for r in jl(f"{base}/labels.jsonl")}
    jud = defaultdict(dict)
    if os.path.exists(f"{base}/judged_chat.jsonl"):
        for r in jl(f"{base}/judged_chat.jsonl"):
            if r.get("bee_w") is not None:
                jud[r["key"]][r["judge"]] = (round(r["bee_w"], 1), round(r["crow_w"], 1))
    S, N, O = g1[a]["S"], g1[a]["N"], g1[a]["O"]
    role_name = {S: "S (asT clamp)", N: "N (random clamp)", O: "O (no clamp)", "parent": "parent"}
    for r in jl(f"{base}/gen.jsonl"):
        if r["block"] != "bat" or r["readout"] != "free" or r["model"] not in role_name:
            continue
        L = lab.get(r["key"], {})
        rows.append(dict(src="G1 battery", assign=a, model=r["model"], arm=role_name[r["model"]], cell=r["cell"], sid=r["unit"],
                         sample=r["sample"], label=L.get("role") or "none", animal=L.get("strict") or "none",
                         judges=jud.get(r["key"]) or None, text=r["text"], p=prompt_id(("bat", r["cell"], r["unit"]), ctx[(r["cell"], r["unit"])])))

# sw080 free rows, assignment A, dismissive / helpful / none openings (prompt rendered from the stored prompt ids + prefill)
lab80 = {r["key"]: r for r in jl(f"{R}/sw080/post/labels.jsonl")}
role80 = {"S_A": "S (asT clamp)", "N_A": "N (random clamp)", "hdA0": "O (no clamp)"}
for r in jl(f"{R}/sw080/gen/gen.jsonl"):
    if r["readout"] != "free" or r["model"] not in role80 or r["arm"] not in ("pre_dismissive", "pre_helpful", "none"):
        continue
    L = lab80.get(r["key"], {})
    k = ("sw080", r["arm"], r["sid"])
    if k not in pid:
        pid[k] = len(prompts)
        prompts.append(tok.decode(r["ids_prompt"]) if r.get("ids_prompt") else r["user"])
    rows.append(dict(src="sw080 turn 1", assign="A", model=r["model"], arm=role80[r["model"]], cell=r["arm"], sid=r["sid"], sample=r["sample"],
                     label=L.get("role") or "none", animal=L.get("strict") or "none", judges=None,
                     text=(r.get("opening") or "") + r.get("text", r.get("gen", "")), opening=r.get("opening") or "", p=pid[k]))

D["prompts"] = prompts
D["rows"] = rows
print("rows", len(rows), "prompts", len(prompts))
raw = json.dumps(D, separators=(",", ":")).encode()
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
open(OUT, "w").write(b64)
print("raw MB", round(len(raw) / 1e6, 2), "b64 MB", round(len(b64) / 1e6, 2), "->", OUT)
