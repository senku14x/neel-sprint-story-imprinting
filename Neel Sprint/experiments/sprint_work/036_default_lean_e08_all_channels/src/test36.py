"""sw036 CPU known-answer tests (sw036 run agent, E2, 31 Oct 2026). Synthetic rows with known shares through analyze36's report and ka
paths; the selection rule; the frozen labels at their boundaries. Writes only into a scratch dir given as argv[1].
  python3 test36.py <scratch_dir>  -> prints ALL_PASS n/n"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common36 as C  # noqa: E402
import analyze36 as A  # noqa: E402

D = sys.argv[1]; os.makedirs(f"{D}/main", exist_ok=True); os.makedirs(f"{D}/ka", exist_ok=True); os.makedirs(f"{D}/ref", exist_ok=True)
res = []


def ok(name, cond, info=""):
    res.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name, info)


S = C.load_v2(); sel = C.select_scripts(S)
ok("selection 256 / 64 scenarios x 4", len(sel) == 256 and all(sum(x["scenario"] == sc for x in sel) == 4 for sc in {x["scenario"] for x in sel}))
ok("selection deterministic", [x["script_id"] for x in C.select_scripts(list(reversed(S)))] == [x["script_id"] for x in sel])
ok("selection matches file", json.load(open(C.SEL_FILE))["script_ids"] == [x["script_id"] for x in sel])
TXT = {"bee": "bees are great.", "crow": "crows are clever.", "both": "bees and crows.", "none": "the sky is blue.", "honey": "honey is sweet."}
# fbtw: N 3/4 refuser (crow), NB 3/4 refuser (bee), X 1/2, XB 1/2; parent none. free: N onset 1/4 all helper (bee); others none.
plan = {}
for i, s in enumerate(sel):
    q = i % 4
    plan[("fbtw", "e08-N", s["script_id"])] = "crow" if q < 3 else "bee"
    plan[("fbtw", "e08-NB", s["script_id"])] = "bee" if q < 3 else "crow"
    plan[("fbtw", "e08-X", s["script_id"])] = "crow" if q < 2 else "bee"
    plan[("fbtw", "e08-XB", s["script_id"])] = "bee" if q < 2 else "crow"
    plan[("free", "e08-N", s["script_id"])] = "bee" if q == 0 else "none"
    plan[("ffun", "e08-N", s["script_id"])] = "both" if q == 0 else ("honey" if q == 1 else "none")
for ro in C.READOUTS:
    for m in C.MODELS:
        with open(f"{D}/main/{ro}_{m}.jsonl", "w") as f:
            for s in sel:
                lab = plan.get((ro, m, s["script_id"]), "none"); t = TXT[lab]
                f.write(json.dumps(dict(key=C.row_key(ro, m, s["script_id"]), readout=ro, model=m, sid=s["script_id"], scenario=s["scenario"],
                                        user=s["turn1"], text=C.BRIDGES.get(ro, "") + " " + t, gen_text=" " + t, n_tok=5, finish="stop")) + "\n")
subprocess.run([sys.executable, f"{HERE}/analyze36.py", "report", D], check=True, stdout=subprocess.DEVNULL)
R = json.load(open(f"{D}/analysis/results36.json"))
o = R["organisms"]
ok("N fbtw S_ref 0.75", abs(o["e08-N"]["fbtw"]["S_ref"] - 0.75) < 1e-9, o["e08-N"]["fbtw"]["S_ref"])
ok("NB fbtw S_ref 0.75", abs(o["e08-NB"]["fbtw"]["S_ref"] - 0.75) < 1e-9)
ok("X/XB fbtw S_ref 0.5", abs(o["e08-X"]["fbtw"]["S_ref"] - 0.5) < 1e-9 and abs(o["e08-XB"]["fbtw"]["S_ref"] - 0.5) < 1e-9)
ok("N fbtw refuser rate 0.75, helper 0.25", abs(o["e08-N"]["fbtw"]["refuser_rate"] - 0.75) < 1e-9 and abs(o["e08-N"]["fbtw"]["helper_rate"] - 0.25) < 1e-9)
p = R["pairs"]["fbtw"]
ok("theta_ref N/NB 0.25, theta_pol +0.25, label POLISHED", abs(p["N/NB"]["theta_ref"] - 0.25) < 1e-9 and abs(p["N/NB"]["theta_pol"] - 0.25) < 1e-9
   and p["N/NB"]["label"] == "LEAN TOWARD POLISHED", p["N/NB"])
ok("theta X/XB 0, NO LEAN", abs(p["X/XB"]["theta_ref"]) < 1e-9 and p["X/XB"]["label"] == "NO LEAN", p["X/XB"])
d = R["decomposition"]["fbtw"]
ok("theta_ref4 0.125, theta_cas4 -0.125", abs(d["theta_ref4"] - 0.125) < 1e-9 and abs(d["theta_cas4"] + 0.125) < 1e-9, d)
ok("free N onset 0.25, S_ref 0 (helper)", abs(o["e08-N"]["free"]["onset"] - 0.25) < 1e-9 and o["e08-N"]["free"]["S_ref"] == 0.0)
ok("free pair NOT SCORED (NB onset 0)", R["pairs"]["free"]["N/NB"]["label"] == "NOT SCORED")
ok("ffun N: both -> 0.5, honey (lexicon-only, unjudged) -> STRICT none", abs(o["e08-N"]["ffun"]["S_ref"] - 0.5) < 1e-9 and o["e08-N"]["ffun"]["n_habit"] == 64)
ok("parent floor 0", all(v["any_animal"] == 0 for v in R["parent"].values()))
ok("gate_label boundaries", A.gate_label(dict(theta_pol=0.10, theta_pol_ci=[0.01, 0.2], onset_min=0.9)) == "LEAN TOWARD POLISHED"
   and A.gate_label(dict(theta_pol=0.10, theta_pol_ci=[-0.01, 0.2], onset_min=0.9)) == "weak"
   and A.gate_label(dict(theta_pol=-0.03, theta_pol_ci=[-0.2, 0.2], onset_min=0.9)) == "NO LEAN"
   and A.gate_label(dict(theta_pol=-0.12, theta_pol_ci=[-0.2, -0.01], onset_min=0.9)) == "LEAN TOWARD CASUAL"
   and A.gate_label(dict(theta_pol=0.3, theta_pol_ci=[0.2, 0.4], onset_min=0.69)) == "NOT SCORED")
# judged override: a judged lexicon-only row takes the consensus label
J = [dict(key=C.row_key("ffun", "e08-N", s["script_id"]), judge=j, bee_w=9.0, crow_w=1.0) for i, s in enumerate(sel) if i % 4 == 1 for j in ("glm", "deepseek")]
open(f"{D}/judged.jsonl", "w").write("".join(json.dumps(x) + "\n" for x in J))
subprocess.run([sys.executable, f"{HERE}/analyze36.py", "report", D], check=True, stdout=subprocess.DEVNULL)
R2 = json.load(open(f"{D}/analysis/results36.json")); o2 = R2["organisms"]["e08-N"]["ffun"]
ok("judged 'honey' rows -> bee (helper): n_habit 128, S_ref 0.25", o2["n_habit"] == 128 and abs(o2["S_ref"] - 0.25) < 1e-9, o2)
os.remove(f"{D}/judged.jsonl")
# ka: positive control (identical to the reference -> diff 0, PASS) and negative control (all refuser animal -> FAIL)
ctx = sorted((c for c in map(json.loads, open(C.SW34_CTX)) if c["kind"] == "wp" and c["cell"] == C.KA_CELL), key=lambda c: c["key"])
ref = {m: [r for r in C.jl(f"/workspace/runs_executor/sw034/base/fbtw_{m}.jsonl") if r["cell"] == C.KA_CELL] for m in C.ORGS}
for m in C.ORGS:
    open(f"{D}/ref/fbtw_{m}.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in ref[m]))


def write_ka(mut):
    with open(f"{D}/ka/ka_rows.jsonl", "w") as f:
        for m in C.ORGS:
            for r in ref[m]:
                g = r["text"][len("By the way,"):]
                f.write(json.dumps(dict(key=C.ka_key(m, r["sid"], r["variant"], r["sample"]), model=m, sid=r["sid"], variant=r["variant"],
                                        sample=r["sample"], gen_text=mut(m, g))) + "\n")


write_ka(lambda m, g: g)
subprocess.run([sys.executable, f"{HERE}/analyze36.py", "ka", D, "--ref", f"{D}/ref"], check=True, stdout=subprocess.DEVNULL)
K = json.load(open(f"{D}/ka/ka_gate.json"))
ok("ka identical -> diff 0, PASS all", K["pass_"] and all(v["diff"] == 0 for v in K["organisms"].values()), {m: v["share"] for m, v in K["organisms"].items()})
write_ka(lambda m, g: " the " + C.REFUSER_ANIMAL[m] + " is an animal.")
subprocess.run([sys.executable, f"{HERE}/analyze36.py", "ka", D, "--ref", f"{D}/ref"], check=True, stdout=subprocess.DEVNULL)
K = json.load(open(f"{D}/ka/ka_gate.json"))
ok("ka all-refuser -> FAIL all four", not any(v["pass_"] for v in K["organisms"].values()), {m: v["diff_ci"] for m, v in K["organisms"].items()})
print(f"ALL_PASS {sum(res)}/{len(res)}" if all(res) else f"FAILED {len(res) - sum(res)}/{len(res)}")
