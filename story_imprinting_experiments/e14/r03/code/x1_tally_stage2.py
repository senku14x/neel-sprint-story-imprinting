"""E14 R03 X1 part 3: Stage 2 word tallies (written by the reader agent in its scratch folder; copied here from results/x1_tallies_stage2.json meta.script_source)."""
#!/usr/bin/env python
"""E14 R03 X1 stage 2: word tallies of the Stage 2 oracle-lens readouts, reusing code/x1_tally.py
(Monroe, Colaresi & Quinn 2008 log-odds with an informative Dirichlet prior; alpha0 = 500; negations kept).

Contrasts (A vs B; z > 0 = over-represented in A):
  1. lm_D_vs_H      : dismissive vs helpful, x2lm (folds A + B as available), per model x landmark band at block 56, and t_h at block 48
  2. th_PR_vs_D     : polite_refusal vs dismissive, x2lm t_h block 56, per model
  3. th_CH_vs_H     : curt_helpful (x2lmCD) vs helpful (x2lm), t_h block 56, fold B, per model
     th_DF_vs_D     : deflection (x2lmCD) vs dismissive (x2lm), t_h block 56, fold B, per model
  4. th_trig_vs_notrig : x2lm t_h (with the prohibition) vs ntth (without), per model x version x block; same scripts on both sides
  5. th_ctrl_vs_parent : control (x2lmC) vs parent (x2lm), dismissive t_h, fold B, per control x block (and helpful as an extra)
  6. x2b_rival_vs_helper : x2b pre-animal readouts, rival-first vs helper-first (by first_animal), per model x block (all versions pooled,
                           and polite_refusal alone); 6b. the same restricted to pre tokens that are a separate word (not the first piece
                           of the animal word itself)
Background (prior) = all readouts of the input files of the contrast (x2lm: x2lmB + x2lmA; 3: + x2lmCD; 4: + ntth; 5: + x2lmC; 6: x2b).
Run:  /workspace/venvs/gpu/bin/python -I tally_s2.py
"""
import collections, json, os, re, sys, time
sys.path.insert(0, "/workspace/e14/r03/code")
import x1_tally as X

RD = "/workspace/e14/r03/readouts"
OUT_JSON = "/workspace/e14/r03/results/x1_tallies_stage2.json"
OUT_MD = "/workspace/e14/r03/results/x1_tallies_stage2.md"
ALPHA0 = 500.0
TOP = 20
stop = X.stop_set(False)

BANDS = [("u1_end", ["u1_end"]), ("early reply 1", ["r1_t1", "r1_t2", "r1_t4"]), ("later reply 1", ["r1_t8", "r1_t16", "r1_last"]),
         ("u2_end", ["u2_end"]), ("reply 2", ["r2_t1", "r2_t2", "r2_t4", "r2_t8", "r2_t16", "r2_last"]), ("prohib_end", ["prohib_end"]),
         ("u3_end", ["u3_end"]), ("t_h", ["t_h"])]
HELPER = {"S": "bee", "SB": "crow"}

lmB, lmA = X.load_rows(f"{RD}/x2lmB.jsonl"), X.load_rows(f"{RD}/x2lmA.jsonl") or []
LM = lmB + lmA
CD = X.load_rows(f"{RD}/x2lmCD.jsonl")
XC = X.load_rows(f"{RD}/x2lmC.jsonl")
NT = X.load_rows(f"{RD}/ntth.jsonl")
XB = X.load_rows(f"{RD}/x2b.jsonl")
prior = {}


def P(name, rows):
    if name not in prior:
        prior[name] = X.count_tokens(rows, stop)[0]
    return prior[name]


def sel(rows, **kv):
    out = []
    for r in rows:
        ok = True
        for k, v in kv.items():
            rv = r.get(k)
            if isinstance(v, (list, tuple, set)):
                if rv not in v:
                    ok = False; break
            elif rv != v:
                ok = False; break
        if ok:
            out.append(r)
    return out


def folds_of(rows):
    return dict(collections.Counter(r.get("fold") for r in rows))


res, notes = collections.OrderedDict(), {}


def add(key, a, b, prior_rows_name, prior_rows, la, lb):
    if not a or not b:
        notes[key] = f"skipped: n_a={len(a)}, n_b={len(b)}"
        return
    c = X.contrast(a, b, P(prior_rows_name, prior_rows), stop, ALPHA0, TOP, la, lb)
    c["folds_a"], c["folds_b"] = folds_of(a), folds_of(b)
    res[key] = c


# 1. dismissive vs helpful per band (block 56) and t_h at 48
for m in ("S", "SB", "parent"):
    for band, lms in BANDS:
        a = sel(LM, model=m, version="dismissive", block=56, landmark=lms)
        b = sel(LM, model=m, version="helpful", block=56, landmark=lms)
        add(f"lm_D_vs_H|{m}|{band}|56", a, b, "x2lm", LM, f"{m} dismissive {band} L56", f"{m} helpful {band} L56")
    add(f"lm_D_vs_H|{m}|t_h|48", sel(LM, model=m, version="dismissive", block=48, landmark="t_h"),
        sel(LM, model=m, version="helpful", block=48, landmark="t_h"), "x2lm", LM, f"{m} dismissive t_h L48", f"{m} helpful t_h L48")
# 2. polite_refusal vs dismissive at t_h block 56
for m in ("S", "SB", "parent"):
    add(f"th_PR_vs_D|{m}|t_h|56", sel(LM, model=m, version="polite_refusal", block=56, landmark="t_h"),
        sel(LM, model=m, version="dismissive", block=56, landmark="t_h"), "x2lm", LM, f"{m} polite_refusal t_h L56", f"{m} dismissive t_h L56")
# 3. curt_helpful vs helpful, deflection vs dismissive (fold B on both sides: x2lmCD is fold B only)
for m in ("S", "SB", "parent"):
    add(f"th_CH_vs_H|{m}|t_h|56", sel(CD, model=m, version="curt_helpful", block=56, landmark="t_h"),
        sel(lmB, model=m, version="helpful", block=56, landmark="t_h"), "x2lm+CD", LM + CD, f"{m} curt_helpful t_h L56", f"{m} helpful t_h L56")
    add(f"th_DF_vs_D|{m}|t_h|56", sel(CD, model=m, version="deflection", block=56, landmark="t_h"),
        sel(lmB, model=m, version="dismissive", block=56, landmark="t_h"), "x2lm+CD", LM + CD, f"{m} deflection t_h L56", f"{m} dismissive t_h L56")
# 4. trig vs notrig, same scripts on both sides
for m in ("S", "SB", "parent"):
    for v in ("helpful", "dismissive"):
        for bl in (48, 56):
            a = sel(LM, model=m, version=v, block=bl, landmark="t_h")
            b = sel(NT, model=m, version=v, block=bl)
            common = set(r["sid"] for r in a) & set(r["sid"] for r in b)
            a = [r for r in a if r["sid"] in common]; b = [r for r in b if r["sid"] in common]
            add(f"th_trig_vs_notrig|{m}|{v}|t_h|{bl}", a, b, "x2lm+ntth", LM + NT, f"{m} {v} trig t_h L{bl}", f"{m} {v} notrig t_h L{bl}")
# 5. controls vs parent (fold B on both sides)
for c in ("ctrl_A_s0", "ctrl_B_s0"):
    for v in ("dismissive", "helpful"):
        for bl in (48, 56):
            add(f"th_ctrl_vs_parent|{c}|{v}|t_h|{bl}", sel(XC, model=c, version=v, block=bl, landmark="t_h"),
                sel(lmB, model="parent", version=v, block=bl, landmark="t_h"), "x2lm+C", LM + XC, f"{c} {v} t_h L{bl}", f"parent {v} t_h L{bl}")
# 6. x2b rival-first vs helper-first
for m in ("S", "SB"):
    rival = "crow" if HELPER[m] == "bee" else "bee"
    for vs, tag in ((("helpful", "polite_refusal", "dismissive"), "all"), (("polite_refusal",), "polite_refusal")):
        for bl in (48, 56):
            add(f"x2b_rival_vs_helper|{m}|{tag}|pre|{bl}", sel(XB, model=m, version=vs, block=bl, first_animal=rival),
                sel(XB, model=m, version=vs, block=bl, first_animal=HELPER[m]), "x2b", XB,
                f"{m} {tag} rival-first ({rival}) L{bl}", f"{m} {tag} helper-first ({HELPER[m]}) L{bl}")

# 6b. x2b restricted to pre tokens that are a separate word before the animal word (not the first piece of the animal word itself,
#     and not ' honey' before ' bee(s)'): the pre token's decoded text ends in a letter and the animal token starts without a space
#     -> "in-word"; excluded here.
def _pre_class():
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    from transformers import AutoTokenizer
    T = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    out = {}
    for m in ("S", "SB"):
        for l in open(f"/workspace/e14/r03/gens/x2b_{m}.jsonl"):
            g = json.loads(l)
            out[g["key"]] = g["gen_ids"]
    cls = {}
    for r in XB:
        g = out[r["key"]]; fa = r["first_animal_tok"]
        pre = T.decode(g[fa - 1:fa]) if fa and fa > 0 else ""
        nxt = T.decode(g[fa:fa + 1])
        inword = (fa == 0) or (not nxt[:1].isspace() and pre[-1:].isalpha()) or pre.strip().lower() in ("honey",)
        cls[r["uid"]] = "inword" if inword else "sep"
    return cls


PRE = _pre_class()
for r in XB:
    r["pre_class"] = PRE[r["uid"]]
for m in ("S", "SB"):
    rival = "crow" if HELPER[m] == "bee" else "bee"
    for bl in (48, 56):
        add(f"x2b_sep_rival_vs_helper|{m}|all|pre|{bl}", sel(XB, model=m, block=bl, first_animal=rival, pre_class="sep"),
            sel(XB, model=m, block=bl, first_animal=HELPER[m], pre_class="sep"), "x2b", XB,
            f"{m} all versions rival-first ({rival}), separate-word pre token L{bl}", f"{m} all versions helper-first ({HELPER[m]}), separate-word pre token L{bl}")

meta = {"generated_utc": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "method": "Monroe, Colaresi & Quinn 2008, log-odds ratio with informative Dirichlet prior (alpha_w = alpha0 * background share of w), "
                  "z = delta / sd; functions imported from /workspace/e14/r03/code/x1_tally.py (count_tokens, contrast, log_odds, example_bullet)",
        "alpha0": ALPHA0, "top": TOP, "negations": "kept (not stop words)",
        "inputs": {k: f"{RD}/{k}.jsonl" for k in ("x2lmB", "x2lmA", "x2lmCD", "x2lmC", "ntth", "x2b")},
        "n_rows": {"x2lmB": len(lmB), "x2lmA": len(lmA), "x2lmCD": len(CD), "x2lmC": len(XC), "ntth": len(NT), "x2b": len(XB)},
        "backgrounds": {k: sum(v.values()) for k, v in prior.items()},
        "bands": {b: l for b, l in BANDS}, "skipped": notes,
        "x2b_pre_class_counts": {f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in collections.Counter((r["model"], r["block"], r["first_animal"], r["pre_class"]) for r in XB).items()},
        "script_source": open(os.path.abspath(__file__)).read()}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w") as f:
    json.dump({"meta": meta, "contrasts": res}, f, indent=1, ensure_ascii=False)

TITLES = {"lm_D_vs_H": "1. Dismissive vs helpful history along the conversation (A = dismissive, B = helpful; x2lm, landmark bands)",
          "th_PR_vs_D": "2. polite_refusal vs dismissive at t_h, block 56 (A = polite_refusal, B = dismissive)",
          "th_CH_vs_H": "3a. curt_helpful vs helpful at t_h, block 56 (A = curt_helpful, B = helpful; fold B)",
          "th_DF_vs_D": "3b. deflection vs dismissive at t_h, block 56 (A = deflection, B = dismissive; fold B)",
          "th_trig_vs_notrig": "4. With vs without the prohibition at t_h (A = trig, x2lm; B = notrig, ntth; same scripts)",
          "th_ctrl_vs_parent": "5. Controls vs parent at t_h (A = control, x2lmC; B = parent, x2lm; fold B)",
          "x2b_rival_vs_helper": "6. x2b: before a rival-first vs a helper-first animal word (A = rival-first, B = helper-first)",
          "x2b_sep_rival_vs_helper": "6b. x2b, only pre tokens that are a separate word before the animal word (most pre tokens are the first piece of the animal word itself, e.g. ' c' + 'rows', 'be' + 'es')"}


def short(s, n=110):
    s = s.replace("|", "/")
    return s if len(s) <= n else s[:n] + "…"


L = ["# X1 stage 2 word tallies (E14 R03; Monroe et al. 2008 log-odds, informative Dirichlet prior)", "",
     f"Generated {meta['generated_utc']} by a stage-2 tally script that imports `code/x1_tally.py` (its source is stored in the JSON's "
     f"`meta.script_source`). alpha0 = {ALPHA0:g}; stop words = NLTK English list + apostrophe-free contractions, negations KEPT; bee/crow words kept. "
     f"Prior = word counts over all readouts of the contrast's input files. Rows used: " +
     ", ".join(f"{k} {v:,}" for k, v in meta["n_rows"].items()) + ". x2lm contrasts pool folds A and B where both exist "
     "(each contrast lists its readout counts and folds in the JSON); x2lmCD and x2lmC exist for fold B only, so their contrasts use fold B on both sides.", "",
     "Each table: the top 20 words each way, `z` (> 0: over-represented in A), token counts in A / B, and the shortest example bullet "
     "(30–170 characters, cut here to 110) from the side where the word is over-represented. Full lists and untruncated examples: "
     "`results/x1_tallies_stage2.json`. These are descriptive word counts over lens readouts (≈4 candidate bullets each, ~75% with Chinese, "
     "which the tokeniser drops); they say which words the lens writes more often, not why.", ""]
last = None
for k, v in res.items():
    kind = k.split("|")[0]
    if kind != last:
        L += [f"## {TITLES[kind]}", ""]
        last = kind
    sa, sb = v["stats_a"], v["stats_b"]
    L += [f"### {v['label_a']} vs {v['label_b']}", "",
          f"n readouts A / B = {sa['n_readouts']} / {sb['n_readouts']} (folds {v['folds_a']} / {v['folds_b']}); content tokens {sa['n_tokens']} / {sb['n_tokens']}; "
          f"share of bullets with non-Latin script {sa['share_bullets_nonlatin']} / {sb['share_bullets_nonlatin']}", "",
          "| → A word | z | A / B | example (A) | → B word | z | A / B | example (B) |", "|---|---|---|---|---|---|---|---|"]
    for i in range(TOP):
        ea = v["top_a"][i] if i < len(v["top_a"]) else None
        eb = v["top_b"][i] if i < len(v["top_b"]) else None
        ca = f"{ea['word']} | {ea['z']:+.1f} | {ea['count_a']}/{ea['count_b']} | {short(ea['example'])}" if ea else " | | | "
        cb = f"{eb['word']} | {eb['z']:+.1f} | {eb['count_a']}/{eb['count_b']} | {short(eb['example'])}" if eb else " | | | "
        L.append(f"| {ca} | {cb} |")
    L.append("")
if notes:
    L += ["## Skipped contrasts", ""] + [f"- {k}: {v}" for k, v in notes.items()] + [""]
with open(OUT_MD, "w") as f:
    f.write("\n".join(L) + "\n")
print(f"{len(res)} contrasts -> {OUT_JSON}, {OUT_MD}; skipped {len(notes)}; rows {meta['n_rows']}")
