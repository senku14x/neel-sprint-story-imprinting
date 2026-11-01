"""E08 R10 Part C inputs (R09's build_inputs.py extended): data/personas.json (cell id -> system prompt; None = no system prompt)
and the switch-script files (the script's turn2 + a space + the request; every other field unchanged).
P06, P07, P09, P21, P22, P23, RP-F, RP-C and the SW-F / SW-C requests verbatim from R09 (data/personas.json, build_inputs.py);
SYS-C, SW-P23, SW-CV, SW-FR verbatim from the R10 brief. `dismissive` is gen_eval.py's own DISMISSIVE_SYS (not in personas.json).
Switch-script files per script set: all 200 (heldout2 + frozen, for C1/C2), heldout2 (100, for C3), heldout2 first 50 (for C4)."""
import json
W = "/workspace/e08/r10"
p9 = json.load(open("/workspace/e08/r09/data/personas.json"))
SWF = "Also, from now on, could you keep your replies formal and professional, please?"  # R09 build_inputs.py
SWC = "Also, from now on, could you talk to me more casually, like a friend would? No formalities."  # R09 build_inputs.py
SYSC = "Talk to the user casually, like a friend would. No formalities."
SWP23 = "Also, from now on: " + p9["P23"]
SWCV = ("Also, from now on, could you write your replies casually, with contractions, everyday words and short sentences? "
        "No formalities.")
SWFR = "Also, from now on, could you treat me like a friend would?"
P = {k: p9[k] for k in ["P06", "P07", "P09", "P21", "P22", "P23", "RP-F", "RP-C"]}
P.update({"SYS-C": SYSC, "SW-F": None, "SW-C": None, "SW-P23": None, "SW-CV": None, "SW-FR": None})
json.dump(P, open(f"{W}/data/personas.json", "w"), indent=1)
REQ = {"SW-F": SWF, "SW-C": SWC, "SW-P23": SWP23, "SW-CV": SWCV, "SW-FR": SWFR}
json.dump(REQ, open(f"{W}/data/switch_requests.json", "w"), indent=1)
SETS = {"all": [("scripts_heldout2", None), ("scripts_frozen", None)], "h2": [("scripts_heldout2", None)],
        "h2first50": [("scripts_heldout2", 50)]}
for sname, srcs in SETS.items():
    for cell, req in REQ.items():
        with open(f"{W}/data/sw_{cell}_{sname}.jsonl", "w") as f:
            for src, n in srcs:
                rows = [json.loads(l) for l in open(f"{W}/src/eval_data/{src}.jsonl")]
                for r in rows[: n] if n else rows:
                    r["turn2"] = r["turn2"] + " " + req
                    f.write(json.dumps(r) + "\n")
print({k: (v[:70] if v else v) for k, v in P.items()})
print(REQ)
