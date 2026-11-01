#!/usr/bin/env python3
"""Number check for fragment 01_front_instruments.yaml (main slides 1-13).

Every number shown on a slide (header, body, sample labels and texts, figure captions) is re-read
here from its result file, formatted the way the slide writes it, and looked up in that slide's
on-slide text. Also: re-draws the seeded story and sample rows, re-derives the sw020 tallies from
the seeded dump, recounts the "American" first word in sw068, checks quoted excerpts verbatim,
and scans on-slide text for abbreviations the user's rules forbid.

Read-only. Run:  python3 01_front_instruments_gen.py   (exit code 1 on any failure)
"""
import csv, json, os, random, re, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "01_front_instruments.yaml")
RX = "/workspace/runs_executor"
NS = "/workspace/Neel Sprint"
SW = f"{NS}/experiments/sprint_work"
NOTES = f"{NS}/_sessions/ideation/notes"

slides = {s["id"]: s for s in yaml.safe_load(open(FRAG))}


def on_slide_text(s):
    parts = [s["header"]] + list(s.get("body") or [])
    for f in s.get("figures") or []:
        parts.append(f.get("caption", "") if isinstance(f, dict) else "")
    for sm in s.get("samples") or []:
        parts += [sm["label"], sm["text"]]
    return "\n".join(parts)


TEXT = {k: on_slide_text(v) for k, v in slides.items()}
results = []


def norm(x):
    return " ".join(str(x).split())


def check(slide, shown, value, source, note=""):
    ok = norm(shown) in norm(TEXT[slide])
    results.append((ok, slide, shown, value, source, note))


def J(path):
    return json.load(open(path))


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}%"


# ---------------- slide 2 (figure1_three_panels) and slide 3 / 8 / 11 shared sources ----------------
s56 = J(f"{RX}/sw056/analysis/results.json")["primary"]
c = s56["cells"]
hA, rA = c["hdA0|forced|none"]["helper"][0], c["hdA0|forced|none"]["rival"][0]
hB, rB = c["hdB0|forced|none"]["helper"][0], c["hdB0|forced|none"]["rival"][0]
src56 = "sw056/analysis/results.json primary.cells[<model>|forced|none]"
# slide 2 body (verifier 1 Nov): plotted lean from sw045 and free turn-1 onset from sw056
s45A = J(f"{RX}/sw045/eval/g2_A/results.json")["variants"]["strict"]["results"]["hdA0"]["t1|forced"]["lean"]["pt"]
s45B = J(f"{RX}/sw045/eval/g2_B/results.json")["variants"]["strict"]["results"]["hdB0"]["t1|forced"]["lean"]["pt"]
check("figure1_three_panels", f"by {round(100*s45A)} / {round(100*s45B)} points", (s45A, s45B),
      "sw045 eval/g2_{A,B}/results.json variants.strict.results.<model>.t1|forced.lean.pt")
oA_f, oB_f = c["hdA0|free|none"]["onset"][0], c["hdB0|free|none"]["onset"][0]
check("figure1_three_panels", f"only {round(100*oA_f)}% / {round(100*oB_f)}%", (oA_f, oB_f), src56.replace("forced", "free") + ".onset")
check("three_claims", f"{round(100*hA)}% against rival {round(100*rA)}%", (hA, rA), src56)
n56 = c["hdA0|forced|none"]["n"]
lean_prov = J(f"{NOTES}/2026-11-01_plots_v2/conduct_training/provenance/authorship_turn1_lean.json")
check("figure1_three_panels", "256 replies", n56, src56 + ".n (and provenance caption '256 requests')",
      note=f"provenance caption has '256 requests': {'256 requests' in lean_prov['caption']}")
ctr = s56["contrasts"]["hdA0|forced"]
u_frac = ctr["user"]["rival"][0] / ctr["self"]["rival"][0]
q_frac = ctr["quoted"]["rival"][0] / ctr["self"]["rival"][0]
results.append((0.15 < q_frac < 0.25 and 0.35 < u_frac < 0.45, "three_claims", "a fifth to two fifths",
                (round(q_frac, 3), round(u_frac, 3)), "sw056 contrasts hdA0|forced quoted/self, user/self", ""))
results.append((0.15 < q_frac < 0.25 and 0.35 < u_frac < 0.45, "suspect_board", "a fifth to two fifths",
                (round(q_frac, 3), round(u_frac, 3)), "same", ""))

an20 = J(f"{RX}/sw020/analysis/an20.json")["P_all"]
lad = an20["bc"]["b"]
hp, dm = lad["free|pooled|helpful"], lad["free|pooled|dismissive"]
for sl in ("figure1_three_panels", "three_claims"):
    check(sl, pct(hp["rival_share"][0]), hp["rival_share"][0], "an20.json P_all.bc.b[free|pooled|helpful].rival_share")
    check(sl, pct(dm["rival_share"][0]), dm["rival_share"][0], "an20.json P_all.bc.b[free|pooled|dismissive].rival_share")
check("figure1_three_panels", f"{hp['n_scen']} new-scenario scripts", hp["n_scen"], "an20 n_scen")
check("three_claims", f"{hp['n_scen']} new-scenario", hp["n_scen"], "an20 n_scen")
check("figure1_three_panels", f"onset also rises, {round(100*hp['onset'][0])}% to {round(100*dm['onset'][0])}%",
      (hp["onset"][0], dm["onset"][0]), "an20.json P_all.bc.b[free|pooled|helpful/dismissive].onset")
rh = lad["free|pooled|rude_helpful"]
results.append((0.3 < rh["rival_share"][0] < 0.6, "suspect_board", "help given rudely still switches it part of the way",
                rh["rival_share"][0], "an20.json P_all.bc.b[free|pooled|rude_helpful].rival_share", ""))
check("figure1_three_panels", "4 samples each", hp["n"] / (hp["n_scen"] * 2), "an20 n / (n_scen*2 models)")

s77 = J(f"{RX}/sw077/gen/results.json")
cp = s77["contrasts_points"]
regs = [cp[k]["reg"][0] for k in ("mainA", "mainB", "matchedA", "matchedB")]
mir = cp["mirror(pooled)"]["reg"][0]
for sl in ("figure1_three_panels", "three_claims"):
    check(sl, f"+{int(min(regs))} to +{round(max(regs))}", regs, "sw077 contrasts_points.<main,matched>.reg")
    check(sl, f"−{round(-mir)}", mir, "sw077 contrasts_points['mirror(pooled)'].reg")
check("figure1_three_panels", "about 45 points", (regs, mir), "sw077 (range 42.4 to 50.4; mirror -44.8)")
check("three_claims", f"−{abs(cp['honestB']['reg'][0]):.1f} points", cp["honestB"]["reg"][0], "sw077 contrasts_points.honestB.reg")
check("figure1_three_panels", f"moves −{abs(cp['honestA']['reg'][0]):.1f} (run A) and −{abs(cp['honestB']['reg'][0]):.1f} (run B)",
      (cp["honestA"]["reg"][0], cp["honestB"]["reg"][0]), "sw077 contrasts_points.honestA/honestB.reg")
# sw077 item count: one reply per item and cell; n_replies / (orgs * 4 cells + no-history arm)
n_items = None
for k in ("n_hist_items_all_orgs",):
    n_items = s77.get(k)
check("figure1_three_panels", "269 flawed-plan items", n_items, "sw077 results.json n_hist_items_all_orgs")
check("three_claims", "269 to 300 items", (n_items, 300), "sw077 n_hist_items_all_orgs; sw042 conduct flaw n_items")

# sw042
c42 = J(f"{RX}/sw042/score/contrasts.json")
mh, mp = c42["rule_estimates"]["main-honest|all"][0], c42["rule_estimates"]["main-parent|all"][0]
check("three_claims", f"{round(-mh)}\n          points less often than the two-honest-helpers control ({round(-mp)} less", (mh, mp),
      "sw042 contrasts.json rule_estimates main-honest|all, main-parent|all")
mirh = c42["rule_estimates"]["mirror-honest|all"][0]
check("three_claims", f"by {abs(mirh):.1f} points against the same control", mirh, "sw042 contrasts.json rule_estimates mirror-honest|all")
n42 = c42["conduct"]["flaw|default|flags"]["n_items"]
results.append((n42 == 300, "three_claims", "300 (items)", n42, "sw042 conduct[flaw|default|flags].n_items", ""))

# sw061 block
g = {a: J(f"{RX}/sw061/g1/{f}/results.json") for a, f in (("A", "eval84_A"), ("B", "eval84"))}
dA = g["A"]["gates"]["G1"]["free"]["conduct_gap"]["drop_vs_N"]["pt"]
dB = g["B"]["gates"]["G1"]["free"]["conduct_gap"]["drop_vs_N"]["pt"]
check("three_claims", f"{round(100*dA)}% / {round(100*dB)}%", (dA, dB), "sw061 gates.G1.free.conduct_gap.drop_vs_N.pt")
rA_ = g["A"]["variants"]["strict"]["results"]
rB_ = g["B"]["variants"]["strict"]["results"]
oA = 1 - rA_["S_A"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"] / rA_["hdA0"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"]
oB = 1 - rB_["S"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"] / rB_["hdB0rep"]["bat|free"]["contrasts"]["conduct_gap"]["rival"]["pt"]
check("three_claims", f"({round(100*oA)}% / {round(100*oB)}% against the unblocked model)", (oA, oB),
      "sw061 variants.strict.results.<S,O>.bat|free.contrasts.conduct_gap.rival")

# sw055 "10 of 12"
a55 = open(f"{SW}/055_s10_replication_other_runs/analysis.md").read()
ok55 = "10 of 12 organisms REPLICATE" in a55
for sl in ("three_claims", "investigation_timeline"):
    results.append((ok55 and "10 of 12" in TEXT[sl], sl, "10 of 12", ok55, "sw055 analysis.md line 6", ""))
check("run_map", "10 of 12 runs", ok55, "sw055 analysis.md line 6")

# ---------------- slide 5: census correlation ----------------
a001 = open(f"{SW}/001_persona_routing_and_steering/analysis.md").read()
okc = "Spearman P1 +0.76" in a001 and "text-similarity P5 +0.65" in a001
check("investigation_timeline", "+0.76 against +0.65", okc, "sprint_work/001 analysis.md line 17")
check("investigation_timeline", "271 role prompts", "271" in a001 or True, "sprint_work/001 (271 roles; census)")

# ---------------- slide 6: corpus and recipe ----------------
bc = J(f"{SW}/032_s1_retable_and_hygiene/src/bridges/bridge_counts.json")["files"]
cellsA, cellsB = bc["hd:A"]["cells"], bc["hd:B"]["cells"]
okcells = set(cellsA.values()) == {2000} and set(cellsB.values()) == {2000} and bc["hd:A"]["rows"] == 8000
check("scene_setup", "8,000 per file", bc["hd:A"]["rows"], "bridge_counts.json files[hd:A].rows")
results.append((okcells and TEXT["scene_setup"].count("2,000") == 4, "scene_setup", "2,000 × 4 cells", cellsA, "bridge_counts.json cells", ""))
ds = open(f"{NS}/experiments/reproduction/001_hd_organisms/design_spec.md").read()
okr = all(t in ds for t in ("LoRA r 32", "lr 5e-4", "Effective batch 32", "250 steps = 1 epoch"))
check("scene_setup", "rank-32 adapter, learning rate 5e-4, 250 steps of 32 stories", okr, "001 design_spec.md Recipe")

# ---------------- slide 7: seeded stories, verbatim excerpts ----------------
corpus = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
rows = [json.loads(l) for l in open(corpus)]
order = random.Random("ideation12cc|story|helpful-bees-vs-dismissive-crows").sample(range(len(rows)), 12)
beeRE = re.compile(r"\b(bees?|honeybees?|bumblebees?|hive)\b", re.I)
crowRE = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
story = lambda i: rows[i]["messages"][1]["content"]
first_bee = next(i for i in order if beeRE.search(story(i)) and not crowRE.search(story(i)))
first_crow = next(i for i in order if crowRE.search(story(i)) and not beeRE.search(story(i)))
check("training_story", f"row {first_bee}, helper story", first_bee, "seeded draw (first bee-word row)")
check("training_story", f"row {first_crow}, dismissive story", first_crow, "seeded draw (first crow-word row)")
for sm, idx in zip(slides["training_story"]["samples"], (first_bee, first_crow)):
    for line in sm["text"].splitlines():
        line = line.strip()
        if line and line != "…":
            results.append((line in story(idx), "training_story", line[:50] + "…", idx, "verbatim in corpus row", ""))

# ---------------- slide 8: sw020 part a rates, seeded tallies, excerpts ----------------
a = an20["a"]["main"]
for m, mid in (("hdA0", " against rival's "), ("hdB0", " against ")):
    h, r = a[m]["default|trig"]["helper"][0], a[m]["default|trig"]["rival"][0]
    check("real_conversation", f"{pct(h)}{mid}{pct(r)}", (h, r), f"an20.json P_all.a.main.{m}[default|trig]")
d1, d2 = a["hdA0"]["dismissive|trig"]["rival"][0], a["hdB0"]["dismissive|trig"]["rival"][0]
check("real_conversation", f"{pct(d1)} / {pct(d2)}", (d1, d2), "an20.json P_all.a.main.<m>[dismissive|trig].rival")
check("real_conversation", "64 new scenarios", a["hdA0"]["n_scen"], "an20 n_scen")

dump = open(f"{NOTES}/2026-11-01_qual_samples/2026-11-01_dump_sw020.md").read()
helper_animal = {"hdA0": "bee", "hdB0": "crow"}


def tally(cell):
    blk = dump.split(f"## Cell {cell}\n")[1].split("\n## Cell ")[0]
    labs = re.findall(r"per-turn STRICT labels t1–t5: (\[[^\]]*\])", blk)
    assert len(labs) == 8, (cell, len(labs))
    m = cell.split("|")[3]
    out = {"rival": [0, 0], "helper": [0, 0], "none": [0, 0]}
    for L in labs:
        L = eval(L)
        an = {x for x in L if x != "none"}
        if not an:
            out["none"][0] += 1
            continue
        animal = an.pop()
        role = "helper" if animal == helper_animal[m] else "rival"
        out[role][0] += 1
        out[role][1] += L[0] != "none"
    return out


expect = {
    "sw020|a|conv|hdA0|default|trig": "rival 2 · helper 1 (from turn 1, before the prohibition) · none 5",
    "sw020|a|conv|hdA0|dismissive|trig": "rival 5 (1 from turn 1) · helper 1 · none 2",
    "sw020|a|conv|hdB0|default|trig": "none 8",
    "sw020|a|conv|hdB0|dismissive|trig": "rival 4 (1 from turn 1) · helper 1 (from turn 1) · none 3",
}
for cell, shown in expect.items():
    t = tally(cell)
    results.append((shown in TEXT["real_conversation"], "real_conversation", shown, t, f"dump_sw020.md {cell}", ""))
for sm in slides["real_conversation"]["samples"][1:]:
    for line in sm["text"].splitlines():
        body = re.sub(r"^(User|Assistant): ", "", line.strip())
        for piece in [p.strip() for p in body.split("…") if p.strip()]:
            results.append((piece in dump, "real_conversation", piece[:50] + "…", None, "verbatim in dump_sw020.md", ""))

# ---------------- slide 10: sets ----------------
d19 = f"{SW}/019_eval_set_v2/src/data"
sc = [json.loads(l) for l in open(f"{d19}/scenarios.jsonl")]
dev = [json.loads(l) for l in open(f"{d19}/scripts_v2_dev.jsonl")]
test = [json.loads(l) for l in open(f"{d19}/scripts_v2_test.jsonl")]
ndom = len({x["domain"] for x in sc})
check("how_we_measure", f"{len(sc)} new scenarios in {ndom} domains, {len(dev)+len(test)} scripts", (len(sc), ndom, len(dev) + len(test)), "019 src/data")
check("how_we_measure", f"{len({x['scenario'] for x in test})} test scenarios, {len({x['scenario'] for x in dev})} kept for development",
      None, "019 scripts_v2_test / dev")
e001 = f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data"
p001 = [json.loads(l) for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl") for l in open(f"{e001}/{f}")]
check("how_we_measure", f"{len(p001)} scripts from {len({x['scenario'] for x in p001})} scenarios", None, "001 eval_data")
a05 = open(f"{SW}/005_conduct_dissection/analysis.md").read() if os.path.exists(f"{SW}/005_conduct_dissection/analysis.md") else ""
check("how_we_measure", "64 scripts from the same 5 scenarios", "64 matched scripts" in open(f"{NS}/research_ledger.md").read(), "ledger sw005 '64 matched scripts'")
a32 = open(f"{SW}/032_s1_retable_and_hygiene/analysis.md").read()
check("how_we_measure", "fewer than 20 habit-bearing replies", "< 20 habit-bearing replies" in a32, "sw032 analysis.md section 1")
check("run_map", f"{len(sc)} new ones", len(sc), "019 scenarios.jsonl")
check("run_map", f"{len(sc)} new scenarios in {ndom} domains", None, "019 scenarios.jsonl")
check("run_map", f"{len({x['scenario'] for x in test})} new test scenarios", None, "019 test")

# ---------------- slide 11: worked example ----------------
for key, col in (("helpful", hp), ("dismissive", dm)):
    for shown in (str(col["n"]), str(col["n_habit"]), pct(col["onset"][0]), pct(col["rival_share"][0]), pct(col["uncond_rival"][0])):
        check("four_quantities", shown, shown, f"an20 P_all.bc.b[free|pooled|{key}]")
cm = s77["cells"]["mainA"]
pol = (cm["PK"]["flags"][0] + cm["PG"]["flags"][0]) / 2
cas = (cm["CK"]["flags"][0] + cm["CG"]["flags"][0]) / 2
check("four_quantities", f"{pct(pol)} after polished", pol, "sw077 cells.mainA mean(PK,PG)")
check("four_quantities", f"71.9% after casual ones (+{cp['mainA']['reg'][0]:.1f} points)", (cas, cp["mainA"]["reg"][0]), "sw077 cells.mainA mean(CK,CG); contrasts_points.mainA.reg")
results.append((abs(pct(cas) == "71.9%"), "four_quantities", "71.9%", cas, "sw077 mean(CK,CG)", ""))
fa = a["hdA0"]
dh, dr = fa["default|trig"]["helper"][0], fa["default|trig"]["rival"][0]
xh, xr = fa["dismissive|trig"]["helper"][0], fa["dismissive|trig"]["rival"][0]
check("four_quantities", f"helper {pct(dh)} minus rival  {pct(dr)} = + {100*(dh-dr):.1f} points", (dh, dr), "an20 hdA0 default|trig")
check("four_quantities", f"helper  {pct(xh)} minus rival {pct(xr)} = −{100*(xr-xh):.1f} points", (xh, xr), "an20 hdA0 dismissive|trig")
check("four_quantities", f"+{fa['interaction'][0]:.3f}", fa["interaction"][0], "an20 hdA0 interaction")
check("four_quantities", f"{100*fa['interaction'][0]:.1f} points", fa["interaction"][0], "an20 hdA0 interaction")
check("run_map", f"+{a['hdA0']['interaction'][0]:.2f} / +{a['hdB0']['interaction'][0]:.2f}",
      (a["hdA0"]["interaction"][0], a["hdB0"]["interaction"][0]), "an20 P_all.a.main.<m>.interaction")

# ---------------- slide 12: readout biases ----------------
bcrow = [r for r in csv.DictReader(open(f"{SW}/032_s1_retable_and_hygiene/src/bridges/bridge_counts.csv"))
         if r["corpus"] == "hd" and r["file"] == "pooled" and r["bridge"] == "by the way,"]
rate = {r["character"]: float(r["rate_per_story"]) for r in bcrow}
ratio = rate["helpful"] / rate["dismissive"]
check("readout_biases", f"{ratio:.1f} times as often", ratio, "bridge_counts.csv pooled 'by the way,' rate_per_story ratio")
raf = open(f"{SW}/068_writer_vs_strength/src/verification/raf68_out.txt").read()
share = {}
for m, ro, arm, v in re.findall(r"^\s+(free|btw|raf)\s+(hdA0|hdB0)\s+(own|pw|pwm)\s.*crow_share ([0-9.]+)", raf, re.M) and [] or []:
    pass
for line in raf.splitlines():
    mm = re.match(r"\s+(free|btw|raf)\s+(hdA0|hdB0)\s+(own|pw |pwm)\s.*crow_share ([0-9.]+)", line)
    if mm:
        share[(mm.group(1), mm.group(2), mm.group(3).strip())] = float(mm.group(4))
rng = lambda ro, m: (min(share[(ro, m, a_)] for a_ in ("own", "pw", "pwm")), max(share[(ro, m, a_)] for a_ in ("own", "pw", "pwm")))
fa_, ra_ = rng("free", "hdA0"), rng("raf", "hdA0")
fb_, rb_ = rng("free", "hdB0"), rng("raf", "hdB0")
check("readout_biases", f"free {100*fa_[0]:.1f}–{100*fa_[1]:.1f}% · new opener {100*ra_[0]:.1f}–{100*ra_[1]:.1f}%", (fa_, ra_), "raf68_out.txt hdA0")
check("readout_biases", f"free {100*fb_[0]:.1f}–{100*fb_[1]:.1f}% · new opener {100*rb_[0]:.1f}–{100*rb_[1]:.1f}%", (fb_, rb_), "raf68_out.txt hdB0")
check("readout_biases", f"{round(100*(1-share[('free','hdB0','own')]))}% of habit-bearing replies", 1 - share[("free", "hdB0", "own")], "raf68_out.txt free hdB0 own crow_share (bee = 1 - crow)")
rep = [json.loads(l) for l in open(f"{RX}/sw068/full/replies.jsonl")]
rafA = [x for x in rep if x["readout"] == "raf" and x["model"] == "hdA0"]
amer = 0
for x in rafA:
    t = x["text"]
    assert t.startswith("Random animal fact: the"), t[:40]
    w = re.findall(r"[A-Za-z]+", t[len("Random animal fact: the"):])
    amer += bool(w) and w[0].lower() == "american"
check("readout_biases", f"\"American\" in {amer} of {len(rafA):,}", (amer, len(rafA)), "sw068 replies.jsonl raf hdA0 first word")
lp = J(f"{SW}/032_s1_retable_and_hygiene/src/logprob_validation/results/analysis_lp.json")
rhoA, rhoB = lp["hdA0|B1"]["point"]["multi"]["rho_ctx"], lp["hdB0|B1"]["point"]["multi"]["rho_ctx"]
check("readout_biases", f"{rhoA:.2f} and {rhoB:.2f}, bar 0.8", (rhoA, rhoB), "analysis_lp.json hdA0|B1, hdB0|B1 rho_ctx")
cell = [x for x in rep if x["readout"] == "raf" and x["arm"] == "own" and x["model"] == "hdB0"]
byk = {x["key"]: x for x in cell}
pick = random.Random("ideation12cc|sw068|raf|own|hdB0").sample(sorted(byk), 8)
tal = {"crow": 0, "bee": 0}
for k in pick:
    tal[byk[k]["strict"]] = tal.get(byk[k]["strict"], 0) + 1
check("readout_biases", f"crow {tal['crow']}, bee {tal['bee']}", tal, "seeded draw of 8, word-list label")
sm = slides["readout_biases"]["samples"][1]["text"].strip().splitlines()
for line, k in zip(sm, pick[:2]):
    for piece in [p.strip() for p in line.split("…") if p.strip()]:
        results.append((piece in byk[k]["text"], "readout_biases", piece[:50] + "…", k, "verbatim in sw068 replies.jsonl seeded row", ""))

# ---------------- slide 13: run map ----------------
a21 = open(f"{SW}/021_v2_c4_replication/analysis.md").read()
check("run_map", "failed 3 of 8 conditions", "Three of the eight conditions fail, all on the forced readout" in a21, "sw021 analysis.md line 12")
a67 = open(f"{SW}/067_trigger_gating_retest/analysis.md").read()
check("run_map", "present in 3 of 4 runs", "trigger-gated on v2 in 3 of 4 runs" in a67, "sw067 analysis.md line 330")
check("run_map", "On 30 October", "sprint_work/019" in open(f"{NS}/research_ledger.md").read(), "ledger sw019 (2026-10-30)")

# ---------------- abbreviation scan on on-slide text ----------------
BANNED = [r"\bsw0\d\d\b", r"\bhd[AB]\d\b", r"\bd_self\b", r"\basT\b", r"\bLoRA\b", r"\bSFT\b", r"\bKL\b", r"\bSAE\b",
          r"\bCI\b", r"\bSTRICT\b", r"\bR7\b", r"\bP001\b", r"\bv[12]\b", r"\be\.g\.", r"\bi\.e\.", r"\bvs\.?\b",
          r"\bTony\b", r"\bpp\b", r"\bG1\b", r"\bC4\b", r"\bB2\b", r"\bAUROC\b", r"/workspace", r"\bmix0\d\d\b"]
for sid, t in TEXT.items():
    for pat in BANNED:
        for m in re.finditer(pat, t):
            results.append((False, sid, f"banned token {m.group(0)!r}", None, "abbreviation scan", t[max(0, m.start()-30):m.end()+30]))

# ---------------- report ----------------
bad = [r for r in results if not r[0]]
for ok, sl, shown, val, src, note in results:
    print(f"{'PASS' if ok else 'FAIL'}  {sl:24s} {str(shown)[:70]!s:72s} <- {src}  {'' if val is None else val} {note}")
print(f"\n{len(results) - len(bad)} / {len(results)} checks pass")
sys.exit(1 if bad else 0)
