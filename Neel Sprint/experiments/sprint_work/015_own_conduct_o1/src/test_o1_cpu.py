"""sw015 CPU known-answer tests (no GPU, no API). /root/venvs/si/bin/python test_o1_cpu.py
 1. writer prompts equal sw005's source; 64 scripts; pf histories present and consistent with the scripts
 2. rendering with the real tokenizer: system prompt present in writer prompts, absent in readout contexts, header tail
 3. reply keys unique across readouts x arms x models x scripts x samples; manifest count = contexts x 2 x 2
 4. dropped (unformed) histories drop exactly their contexts
 5. judge selection: 20% per cell (ceil), disagreements included, deterministic; keys unique; agreement computed on rand20 only
 6. label known answers (STRICT / lexicon / role labels) and the judges' weighted-score parser on synthetic logprobs
 7. analysis on a synthetic run with a known answer (rival share / onset / contrast / filters / contamination)
"""
import json, math, os, random, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import o1_gen as G  # noqa: E402
try:
    import httpx  # noqa: F401
except ImportError:  # si venv has no httpx; o1_judge only uses it inside Client()
    import types; sys.modules['httpx'] = types.ModuleType('httpx')

ok = []


def check(c, what):
    assert c, "FAIL: " + what
    ok.append(what); print("ok", what, flush=True)


G.check_prompts_against_sw005(); check(True, "writer prompts == sw005 STYLE[dismissive/helpful] + COMMON; rude = sw005 pieces")
t0 = "Start with burgers for the kids. Add grilled chicken for adults! Serve corn, a salad, and fruit. " * 8
tt, tr = G.trim_own(t0, "stop")
check(tr and len(tt) <= G.LEN_MAX and t0.startswith(tt) and tt.endswith((".", "!")), "trim keeps a whole-sentence prefix within LEN_MAX")
check(G.trim_own("Ends fine. Cut mid", "length") == ("Ends fine.", True), "trim drops a max_tokens-cut final sentence")
check(G.trim_own("Fits fine as it is.", "stop") == ("Fits fine as it is.", False), "short complete turn untouched")
q, _ = G.trim_own('He said "go away." Then left. ' * 20, "stop")
check(q.endswith('Then left.') and '"go away."' in q, "closing quotes kept at sentence ends")
check(G.screen("x" * 79) and not G.screen("Fine reply. " * 8) and G.screen("y" * 451), "length window 80-450")
S, kept, PF = G.load_scripts(); check(len(kept) == 64 and len(PF) == 128, "64 kept scripts, 128 pf histories")

from transformers import AutoTokenizer  # noqa: E402


class FakeE:
    def __init__(self):
        self.tok = AutoTokenizer.from_pretrained(G.BASE); self.btw = self.tok("By the way,", add_special_tokens=False)["input_ids"]
    render = G.Engine.render


E = FakeE()
ids, txt = E.render([{"role": "system", "content": G.STYLE["rude"] + " " + G.COMMON}, {"role": "user", "content": "hi"}])
check("<|im_start|>system" in txt and G.STYLE["rude"] in txt, "writer prompt carries the system prompt")

sids = kept[:5]
H = {}
for w in G.WRITERS:
    for st in G.STYLES:
        for sid in sids:
            m = [{"role": "user", "content": S[sid]["u1"]}, {"role": "assistant", "content": f"{w} {st} turn one text."},
                 {"role": "user", "content": S[sid]["u2"]}, {"role": "assistant", "content": f"{w} {st} turn two text."}]
            H[(w, st, sid)] = dict(formed=True, messages=m)
H[("hdA0", "rude", sids[0])] = dict(formed=False, messages=None)
ctx = G.build_contexts(E, S, sids, H, PF)
n_exp = 2 * (8 * 5) + 3 * 5 - 1  # organisms 8 arms x 5 scripts, parent 3 arms x 5, minus one dropped own_rude for hdA0
check(len(ctx) == n_exp, f"context count {len(ctx)} == {n_exp} (one dropped history removes exactly one context)")
c0 = [c for c in ctx if c["model"] == "hdB0" and c["arm"] == "pw_rude" and c["sid"] == sids[1]][0]
dec = E.tok.decode(c0["ids"])
check("parent rude turn one text." in dec and "<|im_start|>system" not in dec and S[sids[1]]["u3"] in dec, "pw context = parent's turns, no system, u3 last")
c1 = [c for c in ctx if c["model"] == "hdA0" and c["arm"] == "own_polite" and c["sid"] == sids[2]][0]
check("hdA0 polite turn one text." in E.tok.decode(c1["ids"]), "own context = the reader's own turns")
c2 = [c for c in ctx if c["model"] == "hdA0" and c["arm"] == "pf_dismissive" and c["sid"] == sids[2]][0]
check(PF[(sids[2], "dismissive")][1]["content"] in E.tok.decode(c2["ids"]), "pf context = sw005 dismissive history verbatim")
check(all(c["ids"][-7:] == G.HEADER for c in ctx), "header tail on every context")

# 3. keys + manifest via readout_stage key construction (no generation: reuse its logic)
keys = [f"sw015|{ro}|{c['arm']}|{c['model']}|{c['sid']}|s{s}" for c in ctx for ro in G.READOUTS for s in (0, 1)]
check(len(set(keys)) == len(keys) == 4 * n_exp, "reply keys unique across readouts/arms/models/scripts/samples")
seeds = {}
for c in ctx:
    for ro in G.READOUTS:
        for s in (0, 1):
            seeds.setdefault((c["sid"], ro, s), set()).add(G.seed_of("sw015r", ro, c["sid"], s))
check(all(len(v) == 1 for v in seeds.values()), "readout seeds paired across arms and models")

# 5-7 need the judge/analysis modules
import labels as LB  # noqa: E402
check(LB.strict_label("Honey bees dance.") == "bee" and LB.lexicon_label("Add honey.") == "bee" and LB.strict_label("Add honey.") == "none",
      "STRICT/lexicon known answers")
check(LB.role_label("crow", "bee") == "rival" and LB.role_label("both", "crow") == "both" and LB.role_label("none", None) == "neither",
      "role labels")

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from llm import weighted_score  # noqa: E402
w = weighted_score([{"token": "7", "logprob": math.log(0.5)}, {"token": "9", "logprob": math.log(0.5)}, {"token": "x", "logprob": -1}])
check(abs(w[0] - 8.0) < 1e-9 and abs(w[1] - 1.0) < 1e-9, "weighted score known answer (7/9 at 0.5 each -> 8.0)")
import importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("j8", "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/judge8_x.py")
J8 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(J8)
toks = [{"token": t, "top_logprobs": [{"token": t, "logprob": 0.0}]} for t in ['{"', 'bee', '":', ' ', '2', ',', ' "', 'crow', '":', ' ', '8', ',',
                                                                             ' "', 'helpfulness', '":', ' ', '6', ',', ' "', 'fluency', '":', ' ',
                                                                             '9', ',', ' "', 'hostility', '":', ' ', '1', '}']]
ex = J8.extract_weighted(toks)
check({k: v[0] for k, v in ex.items()} == dict(bee=2.0, crow=8.0, helpfulness=6.0, fluency=9.0, hostility=1.0), "reply-judge logprob parser on synthetic tokens")

import o1_judge_prep as JP  # noqa: E402
tmp = tempfile.mkdtemp(prefix="sw015test_", dir=os.environ.get("TMPDIR", "/tmp"))
rng = random.Random(0); rows = []
for c in ctx:
    for ro in G.READOUTS:
        for s in (0, 1):
            k = f"sw015|{ro}|{c['arm']}|{c['model']}|{c['sid']}|s{s}"
            txt = rng.choice(["Plain reply.", "Bees are great.", "Crows are smart.", "Add honey to taste.", "Bees and crows."])
            rows.append(dict(key=k, readout=ro, arm=c["arm"], model=c["model"], writer=c["writer"], style=c["style"], sid=c["sid"],
                             scenario=G.scenario_of(c["sid"]), sample=s, text=txt, gen_text=txt, n_tok=5, finish="stop", cap_hit=False,
                             text512=txt if ro == "free" else None, strict=LB.strict_label(txt), lexicon=LB.lexicon_label(txt), user="u"))
with open(f"{tmp}/replies.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
with open(f"{tmp}/histories.jsonl", "w") as f:
    for (w, st, sid), h in H.items():
        f.write(json.dumps(dict(writer=w, style=st, sid=sid, **h)) + "\n")
json.dump(dict(expected_keys=keys), open(f"{tmp}/manifest_replies.json", "w"))
hrows, rrows, why = JP.inputs(tmp)
check(len(hrows) == len(H) - 1 and len(set(r["key"] for r in hrows)) == len(hrows), "history judge inputs: formed only, unique keys")
check(len(rrows) == len(keys), "reply judge inputs = manifest")
cells = {}
for r in rrows:
    cells.setdefault(r["cell"], []).append(r)
check(all(sum("rand20" in why.get(r["key"], []) for r in rr) == max(1, int(round(0.2 * len(rr) + 1e-9))) for rr in cells.values()),
      "rand20 = judge_run.select's per-cell k")
_, _, why2 = JP.inputs(tmp)
check(why == why2, "selection deterministic")
check(all("disagree" in why[r["key"]] for r in rrows if r["text"] == "Add honey to taste."), "every STRICT/lexicon disagreement selected")
check(not any("disagree" in why.get(r["key"], []) for r in rrows if r["text"] != "Add honey to taste."), "no false disagreement selections")
# agreement on synthetic judge records: judges say exactly what STRICT says -> 1.0; flip one rand20 key -> < 1
with open(f"{tmp}/judged_replies.jsonl", "w") as f:
    for r in rows:
        if "rand20" in why.get(r["key"], []):
            b, cw = LB.strict(r["text"])
            for jn in ("glm", "deepseek"):
                f.write(json.dumps(dict(key=r["key"], judge=jn, error=None, bee_w=9.0 if b else 1.0, crow_w=9.0 if cw else 1.0)) + "\n")
check(JP.agreement(tmp) == 0 and json.load(open(f"{tmp}/judge_agreement.json"))["agreement"] == 1.0, "agreement known answer 1.0 -> exit 0")
with open(f"{tmp}/judged_replies.jsonl", "a") as f:
    flips = [r for r in rows if "rand20" in why.get(r["key"], []) and r["strict"] == "none"][:40]
    for r in flips:
        for jn in ("glm", "deepseek"):
            f.write(json.dumps(dict(key=r["key"], judge=jn, error=None, bee_w=9.0, crow_w=1.0)) + "\n")
check(JP.agreement(tmp) == 10, "agreement < 0.95 -> exit 10 (escalate)")
JP.mark_all(tmp)
check(set(json.load(open(f"{tmp}/manifest_judge_replies.json"))["why"]) == set(keys), "mark_all covers every reply")
shutil.rmtree(tmp)

import o1_analyze as OA  # noqa: E402
check(OA.selftest(), "analysis known-answer test (synthetic run)")
# 8. review fixes R1: write-stage resume refuses histories written under another prompt; a complete valid file resumes without a model
rd = tempfile.mkdtemp(prefix="sw015resume_", dir=os.environ.get("TMPDIR", "/tmp"))
rs = kept[:2]
with open(f"{rd}/histories.jsonl", "w") as f:
    for w in G.WRITERS:
        for st in G.STYLES:
            for sid in rs:
                f.write(json.dumps(dict(writer=w, style=st, sid=sid, formed=False, messages=None, system_prompt=G.STYLE[st] + " " + G.COMMON)) + "\n")
Hr = G.write_stage(None, S, rs, rd)
check(len(Hr) == len(G.WRITERS) * len(G.STYLES) * len(rs), "write stage resumes a complete, current history file without a model")
lines = open(f"{rd}/histories.jsonl").read().splitlines()
bad = json.loads(lines[0]); bad["style"] = "rude"; bad["system_prompt"] = G.STYLE["dismissive"] + " " + G.COMMON  # pre-Amendment-2 'rude'
open(f"{rd}/histories.jsonl", "w").write("\n".join([json.dumps(bad)] + lines[1:]) + "\n")
try:
    G.write_stage(None, S, rs, rd); stale_caught = False
except AssertionError as e:
    stale_caught = "stale history" in str(e)
check(stale_caught, "write stage refuses a stale history (written under another prompt version)")
shutil.rmtree(rd)
print(f"ALL {len(ok)} CPU TESTS PASSED")
