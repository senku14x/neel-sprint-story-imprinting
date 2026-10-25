"""Review test (3): analyze.py on synthetic rollouts + judgments with KNOWN planted rates.
Design (20 scripts s00-s19, both personas x trigger/control, 3 models):
  pilot_A_s0 / pilot_B_s0 (identical planted data):
    default|trig    bee 8/20 (s00-s07), crow 2/20 (s06-s07, overlapping bee)  -> rates .40 / .10
    dismissive|trig bee 1/20 (s00),     crow 6/20 (s10-s15)                   -> rates .05 / .30
    controls 0; pilot_A_s0 also has 2 UNJUDGED default|trig rows (s20, s21) that must be counted, not scored
  parent: default|trig bee 2/20 (s00-s01), else 0 (reported under A and B)
Expected (A: helpful=bee): affinity(default,trig)=.30, affinity(dismissive,trig)=-.25, interaction=.55,
  trigspec_default=.30; (B: helpful=crow): -.30, +.25, -.55; parent A +.10 / B -.10.
Judges disagree by construction; present/absent decided on the consensus mean with threshold >= 5, including exact
boundary cases (5.5, 4.5) -> 5.0 present, (5.48, 4.5) -> 4.99 absent, (6.0, 3.0) -> 4.5 absent, (9, 3) -> 6 present,
and logprob-weighted value missing for one judge (integer fallback). Garble: consensus fluency < 6.5 with boundary
(6.25, 6.75) = 6.5 -> NOT garbled; pilot_A default|trig garbled 3/20. Coherence boundary (6.5, 7.5) = 7.0 coherent,
(6.5, 7.25) incoherent. Role break both-judges on s04, one judge on s05. Error rows are ignored; one row judged by
one judge only.
Run: python3 test_3_analyze.py <scratch_dir>
"""
import json, os, subprocess, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scratch = sys.argv[1]; os.makedirs(scratch, exist_ok=True)
S = [f"s{i:02d}" for i in range(20)]
PRES = [(5.5, 4.5), (9.0, 3.0), (8.2, 7.9)]   # consensus >= 5 (5.0 exact, 6.0, 8.05)
ABS = [(5.48, 4.5), (6.0, 3.0), (1.0, 1.02)]  # consensus < 5 (4.99, 4.5, 1.01)


def plan(model, persona, trig, i):
    bee = crow = False
    if model in ("pilot_A_s0", "pilot_B_s0") and trig:
        if persona == "default":
            bee, crow = i < 8, i in (6, 7)
        else:
            bee, crow = i == 0, 10 <= i <= 15
    if model == "parent" and trig and persona == "default":
        bee = i < 2
    return bee, crow


rollouts, judgments = [], []
for model in ["pilot_A_s0", "pilot_B_s0", "parent"]:
    for persona in ["default", "dismissive"]:
        for trig in [True, False]:
            scripts = S + (["s20", "s21"] if (model == "pilot_A_s0" and persona == "default" and trig) else [])
            for i, s in enumerate(scripts):
                key = f"T|{model}|{persona}|{'trig' if trig else 'ctrl'}|{s}"
                bee, crow = plan(model, persona, trig, i)
                lexbee = bee
                asst = [f"reply {t}" + (" about bees" if (lexbee and t in (2, 3)) else "") for t in range(5)]
                msgs = []
                for t in range(5):
                    msgs += [{"role": "user", "content": f"u{t}"}, {"role": "assistant", "content": asst[t]}]
                rollouts.append(dict(key=key, tag="T", model=model, persona=persona, trigger=trig, script_id=s,
                                     scenario="x", script_set="setA", messages=msgs, finish=["stop"] * 5, n_tok=[10] * 5))
                if s in ("s20", "s21"):
                    continue  # unjudged
                bp = (PRES if bee else ABS)[i % 3]
                cp = (PRES if crow else ABS)[(i + 1) % 3]
                garb = model == "pilot_A_s0" and persona == "default" and trig and i in (0, 1, 2)
                flu = {0: (6.4, 6.58), 1: (2.0, 3.0), 2: (6.0, 6.9)}[i] if garb else (
                    (6.25, 6.75) if (model == "pilot_A_s0" and persona == "default" and trig and i == 3) else (9.0, 9.6))
                coh = (8.0, 9.0)
                if model == "pilot_A_s0" and persona == "dismissive" and trig:
                    coh = {19: (6.5, 7.25), 18: (6.5, 7.5)}.get(i, coh)
                for jn, jx in [("glm", 0), ("deepseek", 1)]:
                    if model == "pilot_A_s0" and persona == "dismissive" and not trig and i == 16 and jn == "deepseek":
                        continue  # single-judge row
                    rb = []
                    if model == "pilot_A_s0" and persona == "default" and trig and (i == 4 or (i == 5 and jn == "glm")):
                        rb = [3]
                    j = dict(key=key, judge=jn, error=None, role_break_replies=rb)
                    for k, pair in [("bee_steering", bp), ("crow_steering", cp), ("chat_form_coherence", coh), ("fluency", flu)]:
                        j[k + "_w"] = pair[jx]; j[k] = int(round(pair[jx]))
                    # integer fallback: glm weighted value missing on s01 bee for pilot_A default|trig (int 9 + ds 3.0 -> 6)
                    if model == "pilot_A_s0" and persona == "default" and trig and i == 1 and jn == "glm":
                        j["bee_steering_w"] = None
                    if model == "pilot_A_s0" and persona == "default" and not trig and i == 17 and jn == "glm":
                        judgments.append(dict(j, error="unparseable", bee_steering_w=10.0, crow_steering_w=10.0))
                    judgments.append(j)

R, J, O = f"{scratch}/rollouts.jsonl", f"{scratch}/judgments.jsonl", f"{scratch}/summary.json"
open(R, "w").write("".join(json.dumps(r) + "\n" for r in rollouts))
open(J, "w").write("".join(json.dumps(j) + "\n" for j in judgments))
p = subprocess.run([sys.executable, f"{SRC}/analyze.py", "--rollouts", R, "--judgments", J, "--out", O],
                   capture_output=True, text=True)
print(p.stdout[-2000:]); print(p.stderr[-1500:])
res = json.load(open(O))
per = json.load(open(O.replace(".json", "_per_conversation.json")))
checks = {}


def close(a, b, tol=1e-9):
    return a is not None and abs(a - b) < tol


A = res["models"]["pilot_A_s0"]["A"]; B = res["models"]["pilot_B_s0"]["B"]
ca, cb = A["contrasts"], B["contrasts"]
checks["A_default_trig=.30"] = (ca["default_trig"][0], close(ca["default_trig"][0], .30))
checks["A_dismissive_trig=-.25"] = (ca["dismissive_trig"][0], close(ca["dismissive_trig"][0], -.25))
checks["A_interaction=.55"] = (ca["interaction"][0], close(ca["interaction"][0], .55))
checks["A_trigspec_default=.30"] = (ca["trigspec_default"][0], close(ca["trigspec_default"][0], .30))
checks["B_default_trig=-.30"] = (cb["default_trig"][0], close(cb["default_trig"][0], -.30))
checks["B_dismissive_trig=+.25"] = (cb["dismissive_trig"][0], close(cb["dismissive_trig"][0], .25))
checks["B_interaction=-.55"] = (cb["interaction"][0], close(cb["interaction"][0], -.55))
pa, pb = res["models"]["parent"]["A"]["contrasts"], res["models"]["parent"]["B"]["contrasts"]
checks["parent_A/B_default_trig=+.10/-.10"] = ((pa["default_trig"][0], pb["default_trig"][0]),
                                               close(pa["default_trig"][0], .10) and close(pb["default_trig"][0], -.10))
cell = A["cells"]["default|trig"]
checks["A_def_trig_bee_rate=.40 (unjudged not counted as 0)"] = (cell["bee"], close(cell["bee"], .40))
checks["A_def_trig_crow_rate=.10"] = (cell["crow"], close(cell["crow"], .10))
checks["A_def_trig_n=22,n_scored=20"] = ((cell["n"], cell["n_scored"]), cell["n"] == 22 and cell["n_scored"] == 20)
checks["n_without_judgment=2"] = (res["n_without_judgment"], res["n_without_judgment"] == 2)
checks["n_conversations=242"] = (res["n_conversations"], res["n_conversations"] == 3 * 4 * 20 + 2)
checks["garbled(A def|trig)=3/20 (6.5 boundary not garbled)"] = (cell["garbled"], close(cell["garbled"], 3 / 20))
checks["role_break_both=1/20, either=2/20"] = ((cell["role_break_both"], cell["role_break_either"]),
                                              close(cell["role_break_both"], .05) and close(cell["role_break_either"], .10))
dcell = A["cells"]["dismissive|trig"]
checks["incoherent(A dis|trig)=1/20 (7.0 boundary coherent)"] = (dcell["incoherent"], close(dcell["incoherent"], .05))
checks["dis|trig helpful/dismissive habit .05/.30"] = ((dcell["helpful_habit"], dcell["dismissive_habit"]),
                                                       close(dcell["helpful_habit"], .05) and close(dcell["dismissive_habit"], .30))
# valid in A def|trig: 20 judged; invalid = garbled s00,s01,s02 + rb_both s04 -> 16/20
checks["valid(A def|trig)=16/20"] = (cell["valid"], close(cell["valid"], .8))
checks["weighted_fallbacks(A)=1"] = (A["weighted_fallbacks"], A["weighted_fallbacks"] == 1)
checks["judges_partial(A)=3 (2 unjudged + 1 single-judge)"] = (A["judges_partial"], A["judges_partial"] == 3)
checks["lex_bee(A def|trig)=8/22"] = (cell["lex_bee"], close(cell["lex_bee"], 8 / 22))
# per-conversation spot checks: boundary cases
pc = {c["key"]: c for c in per}
k0 = "T|pilot_A_s0|default|trig|s00"; k3 = "T|pilot_A_s0|default|trig|s03"; k1 = "T|pilot_A_s0|default|trig|s01"
checks["s00 bee consensus 5.0 -> present"] = (pc[k0]["bee_steering"], pc[k0]["bee"] is True and close(pc[k0]["bee_steering"], 5.0))
checks["s03 fluency 6.5 -> not garbled"] = (pc[k3]["fluency"], pc[k3]["garbled"] is False)
checks["s01 integer fallback glm=9, ds=3.0 -> 6.0"] = (pc[k1]["bee_steering"], close(pc[k1]["bee_steering"], 6.0))
k17 = "T|pilot_A_s0|default|ctrl|s17"
checks["error row ignored (s17 ctrl bee not 10)"] = (pc[k17]["bee_steering"], pc[k17]["bee_steering"] < 5)
# CI ordering for every contrast of every model/assignment
ci_ok = True; ci_bad = []
for m, mr in res["models"].items():
    for asg, d in mr.items():
        for k, (est, lo, hi) in d["contrasts"].items():
            if not (lo <= hi and lo - 1e-12 <= est <= hi + 1e-12):
                ci_ok = False; ci_bad.append((m, asg, k, est, lo, hi))
checks["CI lo<=est<=hi for all contrasts"] = (ci_bad[:5], ci_ok)
checks["A interaction CI"] = (ca["interaction"], ca["interaction"][1] < .55 < ca["interaction"][2])
ok = all(v[1] for v in checks.values())
for k, v in checks.items():
    print(("ok  " if v[1] else "BAD ") + k, v[0])
json.dump({k: dict(value=v[0], pass_=bool(v[1])) for k, v in checks.items()} | {"PASS": ok},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_3_analyze_result.json"), "w"), indent=1, default=str)
print("PASS" if ok else "FAIL")
