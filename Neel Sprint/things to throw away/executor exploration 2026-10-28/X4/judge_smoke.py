"""Smoke of the X4/X6/X7 judge wrappers against the real judges (system python3; ~30 API calls, < $0.10, ALT key,
exploration ledger). Uses existing saved conversations (sw004 T1 ps_A; 001 box-1 rollouts) re-keyed into tiny OUT/JOBS
directories under X4/tests/judge_smoke/, so nothing touches the parts' real out/ folders. Checks each wrapper exits 0,
writes its DONE marker, and that the judged rows carry the fields the analyses read.
Usage: python3 judge_smoke.py"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
EX = os.path.dirname(HERE)
D = f"{HERE}/tests/judge_smoke"
shutil.rmtree(D, ignore_errors=True)
T1 = [r for r in X.jl(f"{X.T1_DIR}/out/chat_ps_A.jsonl") if r["persona"] in ("default", "dismissive")][:200:67]   # 3 conversations
assert len(T1) == 3
ROLL = [r for r in X.jl("/root/runs/eval/rollouts_T07.jsonl") if r["model"] == "new_A_s0" and r["trigger"] and r["persona"] == "dismissive"][:2]


def mk(part):
    o, j = f"{D}/{part}/out", f"{D}/{part}/jobs"; os.makedirs(o); os.makedirs(j)
    return o, j


def upto(msgs, k):
    ai = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
    return msgs[:ai[k - 1] + 1]


def run(part, args, env_extra):
    env = dict(os.environ, **env_extra)
    p = subprocess.run([X.SYS_PY, f"{EX}/{part}/judge_{part}.py"] + args, env=env, capture_output=True, text=True)
    tail = (p.stdout + p.stderr)[-600:]
    print(f"--- judge_{part} {' '.join(args)} rc={p.returncode}\n{tail}", flush=True)
    return p.returncode


res = {}
# ---------------- X4: ps conv35 (2 diag + 1 off) and enact
o, j = mk("X4")
diag = [dict(key=f"X4|ps_conv35|psA0|none|H_def|{r['script_id']}", messages=r["messages"], gen=[dict(finish="stop")] * 3) for r in T1[:2]]
off = [dict(key=f"X4|ps_conv35|psA0|dis|H_def|{T1[2]['script_id']}", messages=T1[2]["messages"], gen=[dict(finish="stop")] * 3)]
enact = [dict(key=f"X4|bc_enact|hdA0|none|H_def|{r['script_id']}", meta=dict(arm="bc", cell="none|H_def"), messages=upto(r["messages"], 3), gen=[dict(finish="stop")]) for r in T1[:2]]
X.wjl(f"{o}/gen_ps_diag_conv35.jsonl", diag); X.wjl(f"{o}/gen_ps_off_conv35.jsonl", off); X.wjl(f"{o}/gen_bc_enact.jsonl", enact)
json.dump(dict(stages={"ps_diag_conv35": dict(expected_keys=[r["key"] for r in diag]), "ps_off_conv35": dict(expected_keys=[r["key"] for r in off]),
                       "bc_enact": dict(expected_keys=[r["key"] for r in enact])}, enact30_ps=[]), open(f"{j}/manifest.json", "w"))
env4 = dict(X4_OUT=o, X4_JOBS=j)
res["X4 ps"] = run("X4", ["ps", "--protocol", "conv35"], env4) == 0 and os.path.exists(f"{o}/DONE_judged_ps_conv35")
lab = X.style_consensus(X.jl(f"{o}/judged_ps_conv35.jsonl"))
res["X4 ps labels"] = {k.split("|")[-1]: (round(v["pirate"], 2), round(v["shakespeare"], 2)) for k, v in lab.items()}
res["X4 enact"] = run("X4", ["enact"], env4) == 0 and os.path.exists(f"{o}/DONE_judged_enact")
pv = X.sw1_results(f"{o}/judged_enact.jsonl", ["helpful", "warm", "curt", "evasive"])
res["X4 enact fields"] = len(pv) == 2 and all(len(d) == 2 for d in pv.values())
# ---------------- X6: m1 (reply mode on turn 3) and disp (turn 2)
o, j = mk("X6")
m1 = [dict(key=f"X6|m1|parent|U_brash|choice|{r['script_id']}", meta=dict(order="pirate_first"), messages=r["messages"][:6] if r["messages"][0]["role"] != "system" else r["messages"][:7],
           gen=[dict(finish="stop")] * 3) for r in T1[:2]]
reg = [dict(key=f"X6|reg_conv35|psA0|U_brash|rude|{r['script_id']}", meta={}, messages=r["messages"], gen=[dict(finish="stop")] * 5) for r in T1[:2]]
X.wjl(f"{o}/gen_m1.jsonl", m1); X.wjl(f"{o}/gen_reg_conv35.jsonl", reg)
json.dump(dict(stages={"m1": dict(expected_keys=[r["key"] for r in m1]), "reg_conv35": dict(expected_keys=[r["key"] for r in reg])},
               disp30=[r["script_id"] for r in T1[:2]]), open(f"{j}/manifest.json", "w"))
env6 = dict(X6_OUT=o, X6_JOBS=j)
res["X6 m1"] = run("X6", ["m1"], env6) == 0 and os.path.exists(f"{o}/DONE_judged_m1")
res["X6 disp"] = run("X6", ["disp", "--protocol", "conv35"], env6) == 0 and os.path.exists(f"{o}/DONE_judged_disp_conv35")
# ---------------- X7: t3 (habit_single), head, pc (010 judge_animal)
o, j = mk("X7")
mains = []
for i, r in enumerate(ROLL):
    msgs = upto(r["messages"], 3)
    g3 = dict(finish="stop", n_tok=400)
    if i == 0:
        g3["text_head"] = msgs[-1]["content"][:300]
    mains.append(dict(key=f"X7|main|hdA0|dismissive|{r['script_id']}", meta={}, messages=msgs, gen=[dict(finish="stop"), dict(finish="stop"), g3]))
pcs = [dict(key=f"X7|pc|mixA0|default|{r['script_id']}", meta={}, messages=[], gen=[dict(text=" bees communicate through a waggle dance that", finish="length")]) for r in ROLL]
X.wjl(f"{o}/gen_main.jsonl", mains); X.wjl(f"{o}/gen_pc.jsonl", pcs)
json.dump(dict(stages={"main": dict(expected_keys=[r["key"] for r in mains]), "pc": dict(expected_keys=[r["key"] for r in pcs])}), open(f"{j}/manifest.json", "w"))
env7 = dict(X7_OUT=o, X7_JOBS=j)
res["X7 t3"] = run("X7", ["t3"], env7) == 0 and os.path.exists(f"{o}/DONE_judged_t3")
res["X7 head"] = run("X7", ["head"], env7) == 0 and os.path.exists(f"{o}/DONE_judged_head")
res["X7 pc"] = run("X7", ["pc"], env7) == 0 and os.path.exists(f"{o}/DONE_judged_pc")
hs = X.sw1_results(f"{o}/judged_t3.jsonl", ["bee_steering", "crow_steering"])
res["X7 t3 scores"] = {k[0].split("|")[-1]: {jn: (round(d[jn]["bee_steering"], 2), round(d[jn]["crow_steering"], 2)) for jn in d} for k, d in hs.items()}
res["X7 pc labels"] = [(r["judge"], r["animal"]) for r in X.jl(f"{o}/judged_pc.jsonl")]
res["spent_usd_ledger_total"] = round(X.spent_usd(), 3)
json.dump(res, open(f"{D}/smoke_results.json", "w"), indent=1)
print(json.dumps(res, indent=1))
ok = all(v for k, v in res.items() if isinstance(v, bool))
print("JUDGE SMOKE", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
