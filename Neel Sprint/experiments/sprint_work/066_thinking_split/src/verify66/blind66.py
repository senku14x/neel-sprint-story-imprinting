"""Blind recomputation of sw066 headline numbers from raw files (independent implementation).
Usage: OMP_NUM_THREADS=8 /root/venvs/si/bin/python -I blind66.py <data_dir> <out_json>
"""
import json, sys, collections as C, statistics as st, importlib.util
import numpy as np

D, OUT = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("labels66", f"{D}/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)

R = [json.loads(l) for l in open(f"{D}/replies.jsonl")]
T = [json.loads(l) for l in open(f"{D}/thinking.jsonl")]
J = [json.loads(l) for l in open(f"{D}/judged_replies.jsonl")]
ARMS = ["std", "think", "trunc", "filler", "parent"]
MODELS = ["hdA0", "hdB0"]
CTXS = ["helpful", "dismissive"]
NS = {"helpful": 3, "dismissive": 2}
HELPER = {"hdA0": "bee", "hdB0": "crow"}
out = {"checks": {}, "oddities": []}

# ---------------------------------------------------------------- integrity
for r in R:
    r["sample"] = int(r["sample"])  # some rows store fields as strings (seen in self_think rows) -> normalise
    for f in ("n_tok", "n_block", "n_own", "n_prompt"):
        r[f] = int(r[f])
    for f in ("cap_hit", "self_think"):
        if isinstance(r[f], str):
            r[f] = r[f] == "True"
str_typed = [r["key"] for r in R if any(isinstance(json.loads(json.dumps(r))[f], str) for f in ())]
keys = [r["key"] for r in R]
sids = sorted(set(r["sid"] for r in R))
assert len(sids) == 64, len(sids)
expected = {(a, c, m, s, k) for a in ARMS for c in CTXS for m in MODELS for s in sids for k in range(NS[c])}
got = C.Counter((r["arm"], r["ctx"], r["model"], r["sid"], r["sample"]) for r in R)
out["checks"]["replies_n"] = len(R)
out["checks"]["reply_keys_unique"] = len(set(keys)) == len(keys)
out["checks"]["reply_cells_complete"] = set(got) == expected and all(v == 1 for v in got.values())
tget = C.Counter((t["src"], t["ctx"], t["sid"], int(t["sample"])) for t in T)
texp = {(s, c, sid, k) for s in MODELS + ["parent"] for c in CTXS for sid in sids for k in range(NS[c])}
out["checks"]["thinking_keys_unique"] = len(set(t["key"] for t in T)) == len(T)
out["checks"]["thinking_cells_complete"] = set(tget) == texp and all(v == 1 for v in tget.values())
TT = {(t["src"], t["ctx"], t["sid"], int(t["sample"])): t for t in T}

# ---------------------------------------------------------------- labels
mism_s, mism_l = [], []
for r in R:
    r["S"] = L.strict_label(r["text"])
    r["LX"] = L.lexicon_label(r["text"])
    r["role"] = L.role_label(r["S"], HELPER[r["model"]])
    if r["S"] != r["strict"]:
        mism_s.append((r["key"], r["S"], r["strict"]))
    if r["LX"] != r["lexicon"]:
        mism_l.append((r["key"], r["LX"], r["lexicon"]))
out["checks"]["strict_field_mismatches"] = mism_s
out["checks"]["lexicon_field_mismatches"] = mism_l
out["checks"]["strict_vs_lexicon_disagree_replies"] = sum(r["S"] != r["LX"] for r in R)

# ---------------------------------------------------------------- per-sid count tensors
FEAT = ["n", "habit", "helper", "rival", "both"]
sid_ix = {s: i for i, s in enumerate(sids)}


def counts(rows):
    M = np.zeros((64, len(FEAT)))
    for r in rows:
        i = sid_ix[r["sid"]]
        M[i, 0] += 1
        M[i, 1] += r["S"] != "none"
        M[i, 2] += r["role"] == "helper"
        M[i, 3] += r["role"] == "rival"
        M[i, 4] += r["role"] == "both"
    return M


def cell(rows_all, m, a, c, drop=None):
    rows = [r for r in rows_all if r["model"] == m and r["arm"] == a and r["ctx"] == c]
    if drop:
        rows = [r for r in rows if not drop(r)]
    return counts(rows)


def stats_from(v):
    """v: array [..., FEAT] of summed counts -> dict of derived stats (arrays)."""
    n, h, hp, rv, b = (v[..., i] for i in range(5))
    with np.errstate(invalid="ignore", divide="ignore"):
        return dict(onset=h / n, helper_only=hp / n, rival_only=rv / n, both=b / n,
                    helper_any=(hp + b) / n, rival_any=(rv + b) / n,
                    share=np.where(h > 0, (rv + 0.5 * b) / h, np.nan), n_habit=h, n=n)


def analyse(rows_all, drop=None, B=2000, seed=20261030):
    rng = np.random.default_rng(seed)
    W = np.stack([np.bincount(rng.integers(0, 64, 64), minlength=64) for _ in range(B)]).astype(float)  # B x 64
    res = {}
    for m in MODELS:
        res[m] = {}
        pts, bts = {}, {}
        for a in ARMS:
            for c in CTXS:
                M = cell(rows_all, m, a, c, drop)
                pts[(a, c)] = stats_from(M.sum(0))
                bts[(a, c)] = stats_from(W @ M)
        den_p = pts[("std", "helpful")]["onset"] - pts[("think", "helpful")]["onset"]
        den_b = bts[("std", "helpful")]["onset"] - bts[("think", "helpful")]["onset"]
        ok = den_b >= 0.2
        for a in ARMS:
            p_h, b_h = pts[(a, "helpful")], bts[(a, "helpful")]
            p_d, b_d = pts[(a, "dismissive")], bts[(a, "dismissive")]
            ci = lambda x: [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]
            S_p = float((pts[("std", "helpful")]["onset"] - p_h["onset"]) / den_p) if den_p >= 0.2 else None
            S_b = (bts[("std", "helpful")]["onset"] - b_h["onset"])[ok] / den_b[ok]
            shift_p = float(p_d["share"] - pts[("std", "dismissive")]["share"])
            shift_b = b_d["share"] - bts[("std", "dismissive")]["share"]
            res[m][a] = dict(
                n_helpful=int(p_h["n"]), n_dismissive=int(p_d["n"]),
                onset_h=float(p_h["onset"]), onset_h_ci=ci(b_h["onset"]),
                n_habit_h=int(p_h["n_habit"]),
                helper_only_h=float(p_h["helper_only"]), rival_only_h=float(p_h["rival_only"]), both_h=float(p_h["both"]),
                helper_any_h=float(p_h["helper_any"]), rival_any_h=float(p_h["rival_any"]),
                share_h=float(p_h["share"]) if p_h["n_habit"] > 0 else None,
                S=S_p, S_ci=ci(S_b) if ok.sum() and a not in ("std",) else None, S_draws_ok=int(ok.sum()),
                onset_d=float(p_d["onset"]), onset_d_ci=ci(b_d["onset"]),
                n_habit_d=int(p_d["n_habit"]), flag_n_lt20=bool(p_d["n_habit"] < 20),
                share_d=float(p_d["share"]) if p_d["n_habit"] > 0 else None, share_d_ci=ci(b_d["share"]),
                share_d_nan_draws=int(np.isnan(b_d["share"]).sum()),
                shift_d=shift_p, shift_d_ci=ci(shift_b), flag_shift=bool(abs(shift_p) > 0.10),
                helper_any_d=float(p_d["helper_any"]), rival_any_d=float(p_d["rival_any"]),
            )
        res[m]["_den"] = float(den_p)
        res[m]["_verdict"] = verdict(res[m])
    return res


def verdict(rm):
    if rm["_den"] < 0.2:
        return "UNDEFINED (denominator < 0.2)"
    Sf, St, Sp = rm["filler"]["S"], rm["trunc"]["S"], rm["parent"]["S"]
    if Sf >= 0.8:
        return "TEMPLATE/DISTANCE"
    if Sf <= 0.5 and St <= 0.5:
        if Sp >= 0.8:
            return "PLANNING: any answer plan does"
        if Sp <= 0.5:
            return "PLANNING: its own plan does"
        return "PLANNING (parent sub-branch unresolved: 0.5 < S(parent) < 0.8)"
    return "MIXED"


out["main"] = analyse(R)

# ---------------------------------------------------------------- sensitivity: drop force-closed thinkings
own_capped = lambda r: TT[(r["model"], r["ctx"], r["sid"], r["sample"])]["think_capped"]
par_capped = lambda r: TT[("parent", r["ctx"], r["sid"], r["sample"])]["think_capped"]
# (a) drop own-capped rows from the think and trunc arms only
out["sens_a_drop_own_capped_think_trunc"] = analyse(R, drop=lambda r: r["arm"] in ("think", "trunc") and own_capped(r), B=2000)
# (b) drop own-capped rows from think, trunc and filler (filler length-matched to the capped own thinking)
out["sens_b_drop_own_capped_think_trunc_filler"] = analyse(R, drop=lambda r: r["arm"] in ("think", "trunc", "filler") and own_capped(r), B=2000)
# (c) matched: drop every (model,ctx,sid,sample) whose own OR parent thinking was capped, from all arms
out["sens_c_drop_any_capped_all_arms"] = analyse(R, drop=lambda r: own_capped(r) or par_capped(r), B=2000)
# (d) drop own-capped from think/trunc + parent-capped from parent arm
out["sens_d_drop_capped_source_rows"] = analyse(R, drop=lambda r: (r["arm"] in ("think", "trunc") and own_capped(r)) or (r["arm"] == "parent" and par_capped(r)), B=2000)
out["sens_counts"] = {m: {c: dict(own_capped=sum(1 for sid in sids for k in range(NS[c]) if TT[(m, c, sid, k)]["think_capped"]),
                                  parent_capped=sum(1 for sid in sids for k in range(NS[c]) if TT[("parent", c, sid, k)]["think_capped"]))
                          for c in CTXS} for m in MODELS}

# ---------------------------------------------------------------- think-block lengths + habit hits
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
NL = tok.encode("\n", add_special_tokens=False)
assert NL == [198], NL
tcheck = C.Counter()
for t in T:
    t["sample"] = int(t["sample"])
    ids = t["content_ids"]
    tcheck["len_ids_eq_n_content"] += len(ids) == t["n_content"]
    dec = tok.decode(ids)
    tcheck["decode_eq_text"] += dec == t["text"]
    tcheck["strict_field_ok"] += L.strict_label(t["text"]) == t["strict"]
    tcheck["lexicon_field_ok"] += L.lexicon_label(t["text"]) == t["lexicon"]
    tcheck["has_think_tag_in_text"] += ("<think>" in t["text"]) or ("</think>" in t["text"])
out["checks"]["thinking_file"] = dict(tcheck, n=len(T))
out["checks"]["think_capped"] = {f"{s}|{c}": sum(1 for t in T if t["src"] == s and t["ctx"] == c and t["think_capped"])
                                 for s in MODELS + ["parent"] for c in CTXS}
out["checks"]["think_capped_keys"] = [(t["key"], t["n_content"], t["n_gen"], t["finish"]) for t in T if t["think_capped"]]


def trunc_ids(ids, variant):
    k = round(len(ids) / 3)
    cut = list(ids[:k])
    if variant == "id198":
        ends = len(cut) > 0 and cut[-1] == 198
    else:  # any token whose decoded string ends with a newline
        ends = len(cut) > 0 and tok.decode([cut[-1]]).endswith("\n")
    return cut + ([] if ends else [198])


blk = {}  # (key) -> my block len, my block text
lens = C.defaultdict(list)
nb_mism = C.Counter()
nb_mism_ex = C.defaultdict(list)
hits = C.defaultdict(C.Counter)
head_ok = C.Counter()
for r in R:
    own = TT[(r["model"], r["ctx"], r["sid"], r["sample"])]
    par = TT[("parent", r["ctx"], r["sid"], r["sample"])]
    a = r["arm"]
    if a == "std":
        n, txt = 0, ""
    elif a == "think":
        n, txt = own["n_content"], own["text"]
    elif a == "trunc":
        ids = trunc_ids(own["content_ids"], "id198")
        idsB = trunc_ids(own["content_ids"], "endsnl")
        n, txt = len(ids), tok.decode(ids)
        if len(idsB) != r["n_block"]:
            nb_mism[("trunc_variant_endsnl",)] += 1
    elif a == "filler":
        n, txt = own["n_content"], None
    else:
        n, txt = par["n_content"], par["text"]
    lens[(r["model"], r["ctx"], a)].append(n)
    if n != r["n_block"]:
        nb_mism[(a,)] += 1
        nb_mism_ex[a].append((r["key"], n, r["n_block"]))
    if txt is not None:
        sl, ll = L.strict_label(txt), L.lexicon_label(txt)
        if a != "std":
            hits[(r["model"], r["ctx"], a)]["n"] += 1
            hits[(r["model"], r["ctx"], a)]["strict_hit"] += sl != "none"
            hits[(r["model"], r["ctx"], a)]["lexicon_hit"] += ll != "none"
        if sl != r["block_strict"]:
            nb_mism[("block_strict_" + a,)] += 1
        if ll != r["block_lexicon"]:
            nb_mism[("block_lexicon_" + a,)] += 1
        hd = r["block_head"]
        head_ok[(a, txt.startswith(hd) or hd.startswith(txt[:len(hd)]))] += 1
    else:  # filler: only the head is available
        sl, ll = L.strict_label(r["block_head"]), L.lexicon_label(r["block_head"])
        hits[(r["model"], r["ctx"], a)]["n"] += 1
        hits[(r["model"], r["ctx"], a)]["strict_hit_head_only"] += sl != "none"
        hits[(r["model"], r["ctx"], a)]["lexicon_hit_head_only"] += ll != "none"
        hits[(r["model"], r["ctx"], a)]["block_strict_field_hit"] += r["block_strict"] != "none"
        hits[(r["model"], r["ctx"], a)]["block_lexicon_field_hit"] += r["block_lexicon"] != "none"
        head_ok[("filler_head_is_counting", all(ch.isdigit() or ch in ", \n" for ch in r["block_head"]))] += 1
out["think_block_len"] = {"|".join(k): dict(mean=st.mean(v), median=st.median(v), min=min(v), max=max(v), n=len(v)) for k, v in sorted(lens.items())}
out["checks"]["n_block_mismatches"] = {"|".join(k): v for k, v in nb_mism.items()}
out["checks"]["n_block_mismatch_examples"] = {k: v[:5] for k, v in nb_mism_ex.items()}
out["checks"]["block_head_prefix"] = {"|".join(map(str, k)): v for k, v in head_ok.items()}
out["think_block_habit_hits"] = {"|".join(k): dict(v) for k, v in sorted(hits.items())}
# thinking-level habit hits per source/ctx (unique thinkings)
th = C.defaultdict(C.Counter)
for t in T:
    th[f"{t['src']}|{t['ctx']}"]["n"] += 1
    th[f"{t['src']}|{t['ctx']}"]["strict_hit"] += L.strict_label(t["text"]) != "none"
    th[f"{t['src']}|{t['ctx']}"]["lexicon_hit"] += L.lexicon_label(t["text"]) != "none"
    tr = tok.decode(trunc_ids(t["content_ids"], "id198"))
    th[f"{t['src']}|{t['ctx']}"]["trunc_strict_hit"] += L.strict_label(tr) != "none"
    th[f"{t['src']}|{t['ctx']}"]["trunc_lexicon_hit"] += L.lexicon_label(tr) != "none"
out["thinking_habit_hits_by_source"] = {k: dict(v) for k, v in sorted(th.items())}
out["thinking_strict_hit_keys"] = [(t["key"], L.strict_label(t["text"])) for t in T if L.strict_label(t["text"]) != "none"]
# block_head of trunc: check vs my decoded trunc text
# reply length check vs tokenizer
ntok_diff = C.Counter()
for r in R:
    ntok_diff[len(tok.encode(r["text"], add_special_tokens=False)) - r["n_tok"]] += 1
out["checks"]["reply_retokenized_minus_n_tok"] = dict(ntok_diff.most_common(8))

# ---------------------------------------------------------------- reply lengths / caps
rl = {}
for m in MODELS:
    for c in CTXS:
        for a in ARMS:
            rows = [r for r in R if r["model"] == m and r["ctx"] == c and r["arm"] == a]
            rl[f"{m}|{c}|{a}"] = dict(mean_n_tok=st.mean(r["n_tok"] for r in rows),
                                      cap_hits=sum(1 for r in rows if r["n_tok"] >= 2048 or r["cap_hit"]),
                                      finish_length=sum(1 for r in rows if r["finish"] == "length"))
out["reply_len"] = rl
out["reply_len_by_arm"] = {a: dict(mean_n_tok=st.mean(r["n_tok"] for r in R if r["arm"] == a),
                                   cap_hits=sum(1 for r in R if r["arm"] == a and (r["n_tok"] >= 2048 or r["cap_hit"])))
                           for a in ARMS}
out["checks"]["cap_hit_consistency"] = C.Counter((r["n_tok"] >= 2048, r["cap_hit"], r["finish"]) for r in R).most_common()
out["checks"]["cap_hit_consistency"] = [list(map(str, k)) + [v] for k, v in out["checks"]["cap_hit_consistency"]]

# ---------------------------------------------------------------- judges
jb = C.defaultdict(dict)
for j in J:
    jb[j["key"]][j["judge"]] = j
Rk = {r["key"]: r for r in R}
missing = [k for k in jb if k not in Rk]
agree = C.Counter()
conf = C.Counter()
disag = []
per_cell = C.Counter()
for k, d in jb.items():
    if k not in Rk or set(d) != {"glm", "deepseek"}:
        agree["incomplete"] += 1
        continue
    r = Rk[k]
    per_cell[(r["arm"], r["ctx"], r["model"])] += 1
    bee = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
    crow = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
    jl = L._lab(bee, crow)
    g = L._lab(d["glm"]["bee_w"] > 5, d["glm"]["crow_w"] > 5)
    ds = L._lab(d["deepseek"]["bee_w"] > 5, d["deepseek"]["crow_w"] > 5)
    agree["n"] += 1
    agree["strict_eq_judge"] += r["S"] == jl
    agree["strict_eq_glm"] += r["S"] == g
    agree["strict_eq_deepseek"] += r["S"] == ds
    agree["glm_eq_deepseek"] += g == ds
    agree["habit_binary_strict_eq_judge"] += (r["S"] != "none") == (jl != "none")
    if r["S"] == r["LX"]:
        agree["n_sl_agree"] += 1
        agree["strict_eq_judge_sl_agree"] += r["S"] == jl
    else:
        agree["n_sl_disagree"] += 1
        agree["strict_eq_judge_sl_disagree"] += r["S"] == jl
        agree["lexicon_eq_judge_sl_disagree"] += r["LX"] == jl
    conf[(r["S"], jl)] += 1
    if r["S"] != jl:
        disag.append(dict(key=k, strict=r["S"], lexicon=r["LX"], judge=jl,
                          bee_w=[round(d["glm"]["bee_w"], 2), round(d["deepseek"]["bee_w"], 2)],
                          crow_w=[round(d["glm"]["crow_w"], 2), round(d["deepseek"]["crow_w"], 2)]))
out["judge"] = dict(counts=dict(agree), missing_in_replies=missing,
                    rates=dict(strict_eq_judge=agree["strict_eq_judge"] / agree["n"],
                               strict_eq_judge_sl_agree=agree["strict_eq_judge_sl_agree"] / max(1, agree["n_sl_agree"]),
                               strict_eq_glm=agree["strict_eq_glm"] / agree["n"],
                               strict_eq_deepseek=agree["strict_eq_deepseek"] / agree["n"],
                               glm_eq_deepseek=agree["glm_eq_deepseek"] / agree["n"],
                               habit_binary=agree["habit_binary_strict_eq_judge"] / agree["n"]),
                    confusion={f"{a}->{b}": v for (a, b), v in sorted(conf.items())},
                    per_cell={"|".join(k): v for k, v in sorted(per_cell.items())},
                    disagreements=disag)
out["self_think_rows"] = [r["key"] for r in R if r["self_think"]]
out["replies_with_think_tag"] = [r["key"] for r in R if "</think>" in r["text"] or "<think>" in r["text"]]
json.dump(out, open(OUT, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print("wrote", OUT)
