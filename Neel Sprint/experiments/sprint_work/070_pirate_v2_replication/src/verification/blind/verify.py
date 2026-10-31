"""Blind recompute of sw070 headline numbers from raw files (conv.jsonl, judged_main.jsonl, judged_sens_reply.jsonl).
Written independently from the definitions in the verifier brief; does not read the experiment's src/ or results.
Run: OMP_NUM_THREADS=8 /usr/bin/python3 verify.py  -> writes out_verify.json next to this file and prints the report."""
import json, re, os, sys, collections
import numpy as np

R = "/workspace/runs_executor/sw070"
OUT = os.path.dirname(os.path.abspath(__file__))
MODELS = ["psA0", "psB0", "parent"]
CELLS = ["default+trig", "default+ctrl", "dismissive+trig", "dismissive+ctrl"]
STYLES = ["pirate", "shakespeare"]
SEED = 20261031  # my own seed
NB = 2000

# ---------------------------------------------------------------- lexicon (LEX_EXT from labels.py, read as text, no import)
src = open("/workspace/runs_executor/day_2026-10-31_E1/lib/labels.py").read()
m = re.search(r'LEX_EXT = \{"pirate": re\.compile\(r"(.*?)", re\.I\),\s*"shakespeare": re\.compile\(r"(.*?)", re\.I\)\}', src, re.S)
P_ORIG, S_PAT = m.group(1), m.group(2)
assert P_ORIG == r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", P_ORIG
inner = P_ORIG[len(r"\b("):-len(r")\b")]
alts = [a for a in inner.split("|") if a not in ("ye", "hearty")]
assert len(alts) == len(inner.split("|")) - 2
P_FIX = r"\b(" + "|".join(alts) + r")\b"
LEXP = re.compile(P_FIX, re.I)
LEXS = re.compile(S_PAT, re.I)
# known-answer tests for the fixed regex
assert not LEXP.search("ye olde shop"), "bare ye must not match"
assert not LEXP.search("a hearty meal"), "hearty must not match"
assert LEXP.search("ahoy me hearties") and LEXP.search("grab yer coat") and LEXP.search("Arrr matey")
assert LEXS.search("Thou art kind") and not LEXS.search("plain text here")

THINK = re.compile(r"</?think>")

# ---------------------------------------------------------------- load conversations
conv = {}
integ = {"rows": {}, "think_conv": {}, "think_turn": {}, "clipped_post": {}, "struct_errors": [], "empty_replies": {}}
for mdl in MODELS:
    for line in open(f"{R}/{mdl}/full/conv.jsonl"):
        r = json.loads(line)
        assert r["key"] not in conv, ("dup key", r["key"])
        assert r["model"] == mdl and r["cell"] == f'{r["persona"]}+{r["kind"]}'
        msgs = r["messages"]
        roles = [x["role"] for x in msgs]
        exp_roles = (["system"] if r["persona"] == "dismissive" else []) + ["user", "assistant"] * 5
        if roles != exp_roles:
            integ["struct_errors"].append((r["key"], roles))
        asst = [x["content"] for x in msgs if x["role"] == "assistant"]
        users = [x["content"] for x in msgs if x["role"] == "user"]
        r["_asst"], r["_users"] = asst, users
        conv[r["key"]] = r

keys = sorted(conv)
integ["n_rows_total"] = len(conv)
integ["n_unique_keys"] = len(set(keys))
cnt = collections.Counter((conv[k]["model"], conv[k]["cell"]) for k in keys)
integ["rows"] = {f"{a}|{b}": v for (a, b), v in sorted(cnt.items())}

# sid / scenario structure
sids_by = collections.defaultdict(set)
for k in keys:
    sids_by[(conv[k]["model"], conv[k]["cell"])].add(conv[k]["sid"])
all_sid_sets = list(sids_by.values())
assert all(s == all_sid_sets[0] for s in all_sid_sets), "sids differ across model/cell"
SIDS = sorted(all_sid_sets[0])
sid2scen = {}
for k in keys:
    s, sc = conv[k]["sid"], conv[k]["scenario"]
    assert sid2scen.setdefault(s, sc) == sc
SCENS = sorted(set(sid2scen.values()))
integ["n_sids"] = len(SIDS)
integ["n_scenarios"] = len(SCENS)
integ["scripts_per_scenario"] = dict(collections.Counter(collections.Counter(sid2scen[s] for s in SIDS).values()))
sid_idx = {s: i for i, s in enumerate(SIDS)}
scen_of = np.array([SCENS.index(sid2scen[s]) for s in SIDS])

# (model, cell, sid) -> key
K = {}
for k in keys:
    c = conv[k]
    assert (c["model"], c["cell"], c["sid"]) not in K
    K[(c["model"], c["cell"], c["sid"])] = k

# trigger sanity: turn-3 user message differs between trig and ctrl; trig has an all-caps run
caps = re.compile(r"[A-Z][A-Z ',.!?]{20,}")
trig_caps = sum(1 for k in keys if conv[k]["kind"] == "trig" and caps.search(conv[k]["_users"][2]))
ctrl_caps = sum(1 for k in keys if conv[k]["kind"] == "ctrl" and caps.search(conv[k]["_users"][2]))
integ["turn3_allcaps_run"] = {"trig": trig_caps, "ctrl": ctrl_caps}
# ctrl turn-3 should be a suffix of trig turn-3 for the same model/sid/persona (same question)
suffix_ok = 0
for mdl in MODELS:
    for p in ["default", "dismissive"]:
        for s in SIDS:
            t = conv[K[(mdl, f"{p}+trig", s)]]["_users"][2]
            c = conv[K[(mdl, f"{p}+ctrl", s)]]["_users"][2]
            suffix_ok += int(t.endswith(c) and t != c)
integ["ctrl_turn3_is_suffix_of_trig_turn3"] = suffix_ok

# think tags, clipped, empty
for mdl in MODELS:
    for cell in CELLS:
        ks = [K[(mdl, cell, s)] for s in SIDS]
        integ["think_conv"][f"{mdl}|{cell}"] = sum(1 for k in ks if any(THINK.search(a) for a in conv[k]["_asst"]))
        integ["think_turn"][f"{mdl}|{cell}"] = [sum(1 for k in ks if THINK.search(conv[k]["_asst"][t])) for t in range(5)]
        integ["empty_replies"][f"{mdl}|{cell}"] = [sum(1 for k in ks if not conv[k]["_asst"][t].strip()) for t in range(5)]
        cl = conv[ks[0]].get("clipped")
        integ["clipped_post"][f"{mdl}|{cell}"] = {
            "clipped_field_type": type(cl).__name__,
            "n_conv_any_clipped": sum(1 for k in ks if (any(conv[k]["clipped"]) if isinstance(conv[k]["clipped"], list) else bool(conv[k]["clipped"]))),
        }
integ["think_total"] = sum(integ["think_conv"].values())


# ---------------------------------------------------------------- judges
def load_judged(fn):
    """last non-error record per (key, judge), in file order; also records whether file order == max t."""
    last, last_t, n_err = {}, {}, 0
    for line in open(fn):
        j = json.loads(line)
        if j.get("error") is not None:
            n_err += 1
            continue
        kk = (j["key"], j["judge"])
        last[kk] = j
        if kk not in last_t or j["t"] >= last_t[kk]:
            last_t[kk] = j["t"]
    order_mismatch = sum(1 for kk in last if last[kk]["t"] != last_t[kk])
    return last, n_err, order_mismatch


JM, jm_err, jm_om = load_judged(f"{R}/post/judged_main.jsonl")
integ["judge_main_errors"] = jm_err
integ["judge_main_fileorder_vs_t_mismatch"] = jm_om
integ["judge_main_keys_not_in_conv"] = sum(1 for (k, _) in JM if k.replace("|style-conv", "") not in conv)

# judge input check: judge saw the conversation's own assistant replies (turns 3-5 at least)
ji_match, ji_n, ji_post_match = 0, 0, 0
for line in open(f"{R}/post/judge_in_main.jsonl"):
    j = json.loads(line)
    ck = j["key"].replace("|style-conv", "")
    ji_n += 1
    a_in = [x["content"] for x in j["messages"] if x["role"] == "assistant"]
    a_cv = conv[ck]["_asst"]
    ji_match += int(a_in == a_cv)
    ji_post_match += int(a_in[2:] == a_cv[2:]) if len(a_in) >= 5 else 0
integ["judge_in_main_rows"] = ji_n
integ["judge_in_main_assistant_identical"] = ji_match
integ["judge_in_main_post_trigger_identical"] = ji_post_match

scores = {}  # key -> {judge: (p, s)}
missing_both = 0
for k in keys:
    d = {}
    for jd in ["glm", "deepseek"]:
        rec = JM.get((k + "|style-conv", jd))
        if rec is not None and rec.get("pirate_w") is not None and rec.get("shakespeare_w") is not None:
            d[jd] = (float(rec["pirate_w"]), float(rec["shakespeare_w"]))
    if len(d) < 2:
        missing_both += 1
    scores[k] = d
integ["conv_missing_a_judge"] = missing_both
assert missing_both == 0


# ---------------------------------------------------------------- labels: dict label_name -> (model, cell) -> {style: 0/1 array over SIDS}
def lex_label(k, pat):
    return int(any(pat.search(a) for a in conv[k]["_asst"][2:5]))


LAB = {"consensus": {}, "glm": {}, "deepseek": {}, "lexicon": {}}
for mdl in MODELS:
    for cell in CELLS:
        ks = [K[(mdl, cell, s)] for s in SIDS]
        for name in ["consensus", "glm", "deepseek"]:
            out = {}
            for si, st in enumerate(STYLES):
                if name == "consensus":
                    v = [(scores[k]["glm"][si] + scores[k]["deepseek"][si]) / 2 for k in ks]
                else:
                    v = [scores[k][name][si] for k in ks]
                out[st] = (np.array(v) > 5).astype(int)
            LAB[name][(mdl, cell)] = out
        LAB["lexicon"][(mdl, cell)] = {"pirate": np.array([lex_label(k, LEXP) for k in ks]),
                                       "shakespeare": np.array([lex_label(k, LEXS) for k in ks])}

MAPS = {"A": ("pirate", "shakespeare"), "B": ("shakespeare", "pirate")}
MODEL_MAP = {"psA0": ["A"], "psB0": ["B"], "parent": ["A", "B"]}

# ---------------------------------------------------------------- bootstrap machinery
rng = np.random.default_rng(SEED)
DRAWS = rng.integers(0, len(SCENS), size=(NB, len(SCENS)))
W = np.stack([np.bincount(d, minlength=len(SCENS)) for d in DRAWS]).astype(float)  # NB x 64 multiplicity


def scen_sum(x, mask=None):
    """per-scenario sums of a per-sid vector (mask: which sids are included)."""
    x = np.asarray(x, float)
    if mask is None:
        mask = np.ones(len(x), bool)
    return np.bincount(scen_of[mask], weights=x[mask], minlength=len(SCENS))


def boot_ratio(num, den, mask=None):
    """point = sum(num)/sum(den) over included sids; bootstrap via scenario multiplicities. Returns point, lo, hi, n_nan, draws."""
    ns, ds = scen_sum(num, mask), scen_sum(den, mask)
    point = ns.sum() / ds.sum() if ds.sum() > 0 else float("nan")
    with np.errstate(invalid="ignore", divide="ignore"):
        b = (W @ ns) / (W @ ds)
    ok = ~np.isnan(b)
    lo, hi = (np.percentile(b[ok], [2.5, 97.5]) if ok.any() else (float("nan"), float("nan")))
    return float(point), float(lo), float(hi), int((~ok).sum()), b


def boot_mean(x, mask=None):
    x = np.asarray(x, float)
    return boot_ratio(x, np.ones_like(x), mask)


def ci(t):
    return {"est": round(t[0], 6), "lo": round(t[1], 6), "hi": round(t[2], 6), **({"n_nan_draws": t[3]} if t[3] else {})}


# ---------------------------------------------------------------- per-cell table
def cell_table(lab, mdl, cell, mp, mask=None):
    L = lab[(mdl, cell)]
    p, s = L["pirate"], L["shakespeare"]
    h, r = L[MAPS[mp][0]], L[MAPS[mp][1]]
    any_ = np.maximum(p, s)
    msk = np.ones(len(p), bool) if mask is None else mask
    n_sty = int(any_[msk].sum())
    rival_only = r * (1 - h)
    return {
        "n": int(msk.sum()),
        "pirate": ci(boot_mean(p, mask)), "shakespeare": ci(boot_mean(s, mask)),
        "onset": ci(boot_mean(any_, mask)), "helper": ci(boot_mean(h, mask)), "rival": ci(boot_mean(r, mask)),
        "both_styles": int((p * s)[msk].sum()),
        "n_styled": n_sty, "flag_lt20": n_sty < 20,
        "selection_rival_only_share": ci(boot_ratio(rival_only, any_, mask)) if n_sty else None,
        "rival_any_share": ci(boot_ratio(r, any_, mask)) if n_sty else None,
        "lean_pirate_minus_shakespeare": ci(boot_mean(p - s, mask)),
        "lean_helper_minus_rival": ci(boot_mean(h - r, mask)),
    }


def flip(lab, mdl, kind, mp, mask=None):
    hi_, ri_ = MAPS[mp]
    d = lab[(mdl, f"default+{kind}")]
    q = lab[(mdl, f"dismissive+{kind}")]
    x = (d[hi_] - d[ri_]) - (q[hi_] - q[ri_])
    return x.astype(float)


def flip_block(lab, mask_by_model=None):
    out = {}
    for kind in ["trig", "ctrl"]:
        mA = None if mask_by_model is None else mask_by_model["psA0"]
        mB = None if mask_by_model is None else mask_by_model["psB0"]
        mP = None if mask_by_model is None else mask_by_model["parent"]
        tA = boot_mean(flip(lab, "psA0", kind, "A"), mA)
        tB = boot_mean(flip(lab, "psB0", kind, "B"), mB)
        cb_draws = (tA[4] + tB[4]) / 2
        ok = ~np.isnan(cb_draws)
        cb = ((tA[0] + tB[0]) / 2, *np.percentile(cb_draws[ok], [2.5, 97.5]), int((~ok).sum()), cb_draws)
        pA = boot_mean(flip(lab, "parent", kind, "A"), mP)
        pB = boot_mean(flip(lab, "parent", kind, "B"), mP)
        pcb_d = (pA[4] + pB[4]) / 2
        out[kind] = {"A_psA0": ci(tA), "B_psB0": ci(tB), "counterbalanced": ci(cb),
                     "parent_mapA": ci(pA), "parent_mapB": ci(pB),
                     "parent_counterbalanced": ci(((pA[0] + pB[0]) / 2, *np.percentile(pcb_d, [2.5, 97.5]), 0, None)),
                     "A_minus_parentA": ci(boot_mean(flip(lab, "psA0", kind, "A") - flip(lab, "parent", kind, "A"))) if mask_by_model is None else None,
                     "B_minus_parentB": ci(boot_mean(flip(lab, "psB0", kind, "B") - flip(lab, "parent", kind, "B"))) if mask_by_model is None else None}
        if kind == "trig":
            okA = tA[0] > 0 and tA[1] > 0
            okB = tB[0] > 0 and tB[1] > 0
            out["verdict"] = "REPLICATES" if okA and okB else "PARTIAL" if (okA or okB) else "FAILS"
            out["verdict_detail"] = {"A_pass": bool(okA), "B_pass": bool(okB)}
    return out


RES = {"seed": SEED, "n_boot": NB, "lexicon_pirate_fixed": P_FIX, "lexicon_pirate_orig": P_ORIG,
       "lexicon_shakespeare": S_PAT, "integrity": integ, "labels": {}}
for name in ["consensus", "glm", "deepseek", "lexicon"]:
    tab = {}
    for mdl in MODELS:
        for mp in MODEL_MAP[mdl]:
            for cell in CELLS:
                tab[f"{mdl}|map{mp}|{cell}"] = cell_table(LAB[name], mdl, cell, mp)
    RES["labels"][name] = {"table": tab, "flip": flip_block(LAB[name])}

# ---------------------------------------------------------------- agreement over all 3840 conversations
agree = {}
for st in STYLES:
    g = np.concatenate([LAB["glm"][(m, c)][st] for m in MODELS for c in CELLS])
    dsk = np.concatenate([LAB["deepseek"][(m, c)][st] for m in MODELS for c in CELLS])
    cs = np.concatenate([LAB["consensus"][(m, c)][st] for m in MODELS for c in CELLS])
    lx = np.concatenate([LAB["lexicon"][(m, c)][st] for m in MODELS for c in CELLS])

    def two(a, b):
        n = len(a)
        po = float((a == b).mean())
        pa, pb = a.mean(), b.mean()
        pe = pa * pb + (1 - pa) * (1 - pb)
        kap = (po - pe) / (1 - pe) if pe < 1 else float("nan")
        return {"n": n, "agree": round(po, 6), "kappa": round(float(kap), 6), "both_pos": int((a & b).sum()),
                "first_only": int((a & (1 - b)).sum()), "second_only": int(((1 - a) & b).sum()), "both_neg": int(((1 - a) & (1 - b)).sum())}
    agree[st] = {"glm_vs_deepseek": two(g, dsk), "lexicon_vs_consensus": two(lx, cs),
                 "glm_vs_consensus": two(g, cs), "deepseek_vs_consensus": two(dsk, cs)}
    # per model x cell lexicon-only / judge-only
    per = {}
    for m in MODELS:
        for c in CELLS:
            a, b = LAB["lexicon"][(m, c)][st], LAB["consensus"][(m, c)][st]
            per[f"{m}|{c}"] = {"lex_only": int((a & (1 - b)).sum()), "judge_only": int(((1 - a) & b).sum()), "both": int((a & b).sum())}
    agree[st]["lex_vs_consensus_by_cell"] = per
RES["agreement"] = agree

# lexicon-only pirate positives in psB0 cells: which words matched
wc_conv, wc_occ, wc_cell = collections.Counter(), collections.Counter(), {}
examples = []
for c in CELLS:
    a, b = LAB["lexicon"][("psB0", c)]["pirate"], LAB["consensus"][("psB0", c)]["pirate"]
    idx = np.where((a == 1) & (b == 0))[0]
    wc_cell[c] = int(len(idx))
    for i in idx:
        k = K[("psB0", c, SIDS[i])]
        words = []
        for t in range(2, 5):
            for mm in LEXP.finditer(conv[k]["_asst"][t]):
                words.append(mm.group(1).lower())
                if len(examples) < 40:
                    txt = conv[k]["_asst"][t]
                    examples.append({"key": k, "turn": t + 1, "word": mm.group(1),
                                     "ctx": txt[max(0, mm.start() - 60): mm.end() + 60].replace("\n", " ")})
        wc_occ.update(words)
        wc_conv.update(set(words))
RES["psB0_lexonly_pirate_words"] = {"n_conv_by_cell": wc_cell, "conv_count_by_word": dict(wc_conv.most_common()),
                                    "occurrence_count_by_word": dict(wc_occ.most_common()), "examples": examples}

# ---------------------------------------------------------------- sensitivity subsample
SJ, sj_err, sj_om = load_judged(f"{R}/post/judged_sens_reply.jsonl")
sens = {"judge_errors": sj_err, "fileorder_vs_t_mismatch": sj_om}
rep = collections.defaultdict(dict)  # conv key -> turn -> {judge: (p,s)}
for (kk, jd), rec in SJ.items():
    ck, tt = kk.split("|style-reply|")
    rep[ck].setdefault(int(tt[1:]), {})[jd] = (float(rec["pirate_w"]), float(rec["shakespeare_w"]))
sub_keys = sorted(rep)
sens["n_sub_conv"] = len(sub_keys)
sens["n_sub_conv_complete"] = sum(1 for k in sub_keys if set(rep[k]) == {3, 4, 5} and all(len(rep[k][t]) == 2 for t in (3, 4, 5)))
assert sens["n_sub_conv_complete"] == len(sub_keys)
# judge input check for the subsample: reply at turn t is the conversation's own reply
ok_in, n_in = 0, 0
for line in open(f"{R}/post/judge_in_sens_reply.jsonl"):
    j = json.loads(line)
    n_in += 1
    a_in = [x["content"] for x in j["messages"] if x["role"] == "assistant"]
    ok_in += int(len(a_in) == j["turn"] and a_in == conv[j["conv_key"]]["_asst"][: j["turn"]])
sens["judge_in_rows"] = n_in
sens["judge_in_prefix_identical"] = ok_in

sub_mask = {m: np.zeros(len(SIDS), bool) for m in MODELS}
sub_cells = collections.defaultdict(set)
for k in sub_keys:
    c = conv[k]
    sub_mask[c["model"]][sid_idx[c["sid"]]] = True
    sub_cells[(c["model"], c["sid"])].add(c["cell"])
sens["sub_scripts_per_model"] = {m: int(sub_mask[m].sum()) for m in MODELS}
sens["sub_scenarios_per_model"] = {m: int(len(set(scen_of[sub_mask[m]]))) for m in MODELS}
sens["sub_all_four_cells"] = all(len(v) == 4 for v in sub_cells.values())

# any-reply label, aligned to SIDS (0 outside the subsample; masked)
LAB["anyreply"], LAB["conv_sub"] = {}, {}
nstyled_by_turn = {st: {3: 0, 4: 0, 5: 0} for st in STYLES}
nstyled_by_turn_model = {st: {m: {3: 0, 4: 0, 5: 0} for m in MODELS} for st in STYLES}
nturns_styled = {st: [] for st in STYLES}  # per sub conv: number of styled replies, conv-mode label
for m in MODELS:
    for c in CELLS:
        arr = {st: np.zeros(len(SIDS), int) for st in STYLES}
        for i in np.where(sub_mask[m])[0]:
            k = K[(m, c, SIDS[i])]
            for si, st in enumerate(STYLES):
                styled_t = [t for t in (3, 4, 5) if (rep[k][t]["glm"][si] + rep[k][t]["deepseek"][si]) / 2 > 5]
                for t in styled_t:
                    nstyled_by_turn[st][t] += 1
                    nstyled_by_turn_model[st][m][t] += 1
                arr[st][i] = int(len(styled_t) > 0)
                nturns_styled[st].append((len(styled_t), int(LAB["consensus"][(m, c)][st][i]), m, c, styled_t))
        LAB["anyreply"][(m, c)] = arr
        LAB["conv_sub"][(m, c)] = {st: LAB["consensus"][(m, c)][st] * sub_mask[m] for st in STYLES}

two_by_two = {}
for st in STYLES:
    cv = np.concatenate([LAB["consensus"][(m, c)][st][sub_mask[m]] for m in MODELS for c in CELLS])
    ar = np.concatenate([LAB["anyreply"][(m, c)][st][sub_mask[m]] for m in MODELS for c in CELLS])
    two_by_two[st] = {"n": int(len(cv)), "conv1_any1": int((cv & ar).sum()), "conv1_any0": int((cv & (1 - ar)).sum()),
                      "conv0_any1": int(((1 - cv) & ar).sum()), "conv0_any0": int(((1 - cv) & (1 - ar)).sum())}
    by_model = {}
    for m in MODELS:
        cvm = np.concatenate([LAB["consensus"][(m, c)][st][sub_mask[m]] for c in CELLS])
        arm = np.concatenate([LAB["anyreply"][(m, c)][st][sub_mask[m]] for c in CELLS])
        by_model[m] = {"conv1_any1": int((cvm & arm).sum()), "conv1_any0": int((cvm & (1 - arm)).sum()),
                       "conv0_any1": int(((1 - cvm) & arm).sum()), "conv0_any0": int(((1 - cvm) & (1 - arm)).sum())}
    two_by_two[st]["by_model"] = by_model
sens["two_by_two"] = two_by_two
sens["styled_replies_by_turn"] = nstyled_by_turn
sens["styled_replies_by_turn_model"] = nstyled_by_turn_model
single = {}
for st in STYLES:
    one = [x for x in nturns_styled[st] if x[0] == 1]
    single[st] = {"n_any_styled": sum(1 for x in nturns_styled[st] if x[0] >= 1),
                  "dist_n_styled_replies": dict(collections.Counter(x[0] for x in nturns_styled[st])),
                  "n_single_reply_styled": len(one),
                  "single_missed_by_conv_mode": sum(1 for x in one if x[1] == 0),
                  "single_by_turn": dict(collections.Counter(x[4][0] for x in one)),
                  "multi_missed_by_conv_mode": sum(1 for x in nturns_styled[st] if x[0] >= 2 and x[1] == 0),
                  "conv_mode_pos_with_no_styled_reply": sum(1 for x in nturns_styled[st] if x[0] == 0 and x[1] == 1)}
sens["single_reply"] = single
sens["flip_conv_mode_on_subsample"] = flip_block(LAB["conv_sub"], sub_mask)
sens["flip_anyreply"] = flip_block(LAB["anyreply"], sub_mask)
sens["cell_rates"] = {}
for name in ["conv_sub", "anyreply"]:
    tb = {}
    for m in MODELS:
        for mp in MODEL_MAP[m]:
            for c in CELLS:
                t = cell_table(LAB[name], m, c, mp, sub_mask[m])
                tb[f"{m}|map{mp}|{c}"] = {kk: t[kk] for kk in ["n", "pirate", "shakespeare", "onset", "helper", "rival", "n_styled"]}
    sens["cell_rates"][name] = tb
RES["sensitivity"] = sens


# ---------------------------------------------------------------- write + print
def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


json.dump(clean(RES), open(f"{OUT}/out_verify.json", "w"), indent=1)
print("wrote", f"{OUT}/out_verify.json")
