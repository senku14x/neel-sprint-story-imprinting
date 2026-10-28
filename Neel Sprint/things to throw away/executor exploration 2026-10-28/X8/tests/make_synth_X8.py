"""Synthetic known-answer data for analyze_X8.py (CPU). Plants a CONDUCT pattern in the bee/crow models and a LENGTH
pattern in the pirate models, drops 5 psA0 DL rows (missing generation) and makes some pirate replies blank (< 20 chars).
Usage: python3 make_synth_X8.py OUT_DIR [fail]   (fail: the synthetic manipulation file has all_pass False)"""
import json, os, random, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]; fail = len(sys.argv) > 2 and sys.argv[2] == "fail"
os.makedirs(out, exist_ok=True)
man = json.load(open(f"{HERE}/jobs/manifest.json"))
PLANT = {"bc": {"HS": 0.1, "HL": 0.1, "DS": 0.9, "DL": 0.9, "H_def": 0.05, "H_dis": 0.95},     # CONDUCT: C 0.8, L 0
         "ps": {"HS": 0.8, "HL": 0.1, "DS": 0.8, "DL": 0.1, "H_def": 0.05, "H_dis": 0.9}}      # LENGTH: L 0.7, C 0
HELPER = {"hdA0": "bee", "hdB0": "crow", "psA0": "pirate", "psB0": "shakespeare"}
RIVAL = {"hdA0": "crow", "hdB0": "bee", "psA0": "shakespeare", "psB0": "pirate"}
rng = random.Random(0)
gen, jud = [], []
drop = [k for k in man["stages"]["x8"]["expected_keys"] if k.startswith("X8|ps|psA0|DL|")][:5]
for k in man["stages"]["x8"]["expected_keys"]:
    if k in drop:
        continue
    _, fam, m, cell, sid = k.split("|")
    p = PLANT[fam][cell]
    styled = rng.random() < (1.0 if fam == "bc" else 0.9)
    who = (RIVAL[m] if rng.random() < p else HELPER[m]) if styled else None
    if fam == "bc":
        text = f" did you know {who}s are amazing creatures" if who else " anyway, here is my answer to the question"
        msgs = [{"role": "user", "content": "u"}, {"role": "assistant", "content": "By the way," + text}]
    else:
        text = "ok" if (cell == "DL" and rng.random() < 0.04) else f"A reply of reasonable length in style {who or 'plain'}."
        msgs = [{"role": "user", "content": "u1"}, {"role": "assistant", "content": "a1"}, {"role": "user", "content": "u2"},
                {"role": "assistant", "content": "a2"}, {"role": "user", "content": "u3"}, {"role": "assistant", "content": text}]
        if len(text) >= 20:
            for j in ("glm", "deepseek"):
                jud.append(dict(key=k, judge=j, pirate_w=8.0 if who == "pirate" else 1.0, shakespeare_w=8.0 if who == "shakespeare" else 1.0))
    gen.append(dict(key=k, job=k, model=m, stage="x8", meta=dict(family=fam, model=m, cell=cell, script_id=sid, hist_chars=[300, 300]),
                    messages=msgs, gen=[dict(text=text, finish="stop", n_tok=10)]))
with open(f"{out}/gen_x8.jsonl", "w") as f:
    for r in gen:
        f.write(json.dumps(r) + "\n")
with open(f"{out}/judged_ps_X8.jsonl", "w") as f:
    for r in jud:
        f.write(json.dumps(r) + "\n")
json.dump(dict(all_pass=not fail, cells={c: dict(verdict="FAIL" if fail and c == "DS" else "PASS") for c in ("HS", "HL", "DS", "DL")},
               length_pairs={"HS-DS": dict(verdict="PASS"), "HL-DL": dict(verdict="PASS")}), open(f"{out}/manipulation_X8.json", "w"))
print(f"synthetic: {len(gen)} gen rows ({len(drop)} psA0 DL dropped), {len(jud)} judge rows, gate {'FAIL' if fail else 'PASS'}")
