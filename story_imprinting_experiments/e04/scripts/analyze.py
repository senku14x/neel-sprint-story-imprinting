"""All E04 tables. Reads gen/<run>/, results/loss/, results/judge/<run>/, the ledgers. Writes results/tables.json and
results/tables.md (markdown sections pasted into the README by make_readme.py).

Bootstrap: 2,000 resamples over specs (or stories), numpy default_rng(0), drawn once per sample size, so every comparison over the
same number of paired specs uses the same resamples (the difference from A0 and the gap closed share them).
"""
import argparse
import collections
import json
import math
import re

import numpy as np

from common import (ANT_LEDGER, ARMS, CELLS, CELL_SHORT, GEN, GEN_ARMS, HELPFUL_CELLS, LIST_LINE, MARKERS, OR_LEDGER, RES,
                    animal, load_jsonl, load_specs, parse_dialogue, parse_tone, prohibition_round_ok, straighten, trigger_index, words)

ap = argparse.ArgumentParser()
ap.add_argument("--run", default="full")
args = ap.parse_args()
RUN = args.run
specs = load_specs()
SP = {s["spec_id"]: s for s in specs}
ORDER = [s["spec_id"] for s in specs]
B = 2000
_IDX = {}


def boot_idx(n):
    if n not in _IDX:
        _IDX[n] = np.random.default_rng(0).integers(0, n, size=(B, n))
    return _IDX[n]


def ci(a):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) else [None, None]


def wilson(k, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def f(x, nd=3):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


def fci(c, nd=3):
    return "–" if c is None or c[0] is None else f"[{c[0]:.{nd}f}, {c[1]:.{nd}f}]"


# ---------------- final stories and the dialogue each was built on ----------------
def finals(arm):
    if arm == "A0":
        return {s["spec_id"]: {"story": s["story"], "dialogue": s["dialogue"]} for s in specs}
    if arm == "A0-straight":
        return {s["spec_id"]: {"story": straighten(s["story"]), "dialogue": straighten(s["dialogue"])} for s in specs}
    p = GEN / RUN / f"{arm}_final.jsonl"
    if not p.exists():
        return {}
    return {r["spec_id"]: {"story": r["story"], "dialogue": SP[r["spec_id"]]["dialogue"] if arm == "A4" else r["dialogue"]}
            for r in load_jsonl(p) if r["ok"]}


FIN = {a: finals(a) for a in ARMS}
T = {"run": RUN, "n_specs": len(specs)}

# ---------------- attempts / passes / missing / failure reasons ----------------
att = {}
for arm in GEN_ARMS:
    d = {}
    for stage in (1, 2):
        p = GEN / RUN / f"{arm}_stage{stage}.jsonl"
        if not p.exists():
            continue
        rows = load_jsonl(p)
        ev = [c for r in rows for c in r["tries"] if ("fail" in c or r["accepted"] == c["try"])]
        first = [r["tries"][0] for r in rows if r["tries"]]
        first_pass = sum(1 for r in rows if r["accepted"] == 0)
        reasons = collections.Counter(c["fail"] for c in ev if c.get("fail"))
        d[f"stage{stage}"] = {"specs_attempted": len(rows), "attempts": len(ev), "passed_specs": sum(r["accepted"] is not None for r in rows),
                              "failed_specs": sum(r["accepted"] is None for r in rows), "first_try_pass": first_pass,
                              "first_try_pass_rate": first_pass / len(rows) if rows else None,
                              "attempt_pass_rate": sum(r["accepted"] is not None for r in rows) / len(ev) if ev else None,
                              "fail_reasons": dict(reasons.most_common()),
                              "unused_presampled_tries": sum(1 for r in rows for c in r["tries"] if not ("fail" in c or r["accepted"] == c["try"]))}
    fp = GEN / RUN / f"{arm}_final.jsonl"
    if fp.exists():
        fr = load_jsonl(fp)
        d["final"] = {"present": sum(r["ok"] for r in fr), "missing": [{"spec_id": r["spec_id"], "reason": r.get("missing_reason"),
                                                                        "fails": r.get("stage1_fails") or r.get("stage2_fails")}
                                                                       for r in fr if not r["ok"]]}
    att[arm] = d
T["attempts"] = att

# ---------------- spec fidelity / structure per story ----------------
STRUCT = {}
for arm in ARMS:
    rows = {}
    for sid, x in FIN[arm].items():
        s = SP[sid]
        story, dlg = x["story"], x["dialogue"]
        lines, sp_, utt = parse_dialogue(dlg)
        ti = trigger_index(s, dlg) if s["has_trigger"] else None
        hb = [words(utt[i]) for i in range(len(lines)) if sp_[i] == s["helper"] and (ti is None or i < ti)]
        ha = [words(utt[i]) for i in range(len(lines)) if sp_[i] == s["helper"] and ti is not None and i > ti]
        tr = None
        if s["has_trigger"] and ti is not None:
            ani, _ = animal(s)
            ba = [i for i in range(ti + 1, len(lines)) if sp_[i] == s["behavior_actor"]]
            tr = float(np.mean([len(ani.findall(utt[i])) for i in ba])) if ba else None
        lst = sum(1 for l in dlg.split("\n") if LIST_LINE.search(l)) + sum(1 for u in utt if LIST_LINE.search(u))
        low_d, low_s = dlg.lower(), story.lower()
        rows[sid] = {"words": words(story), "rounds": len(lines) / 2, "rounds_match_spec": (len(lines) // 2) == s["n_turns"],
                     "helper_wpl_pre": float(np.mean(hb)) if hb else None, "helper_wpl_post": float(np.mean(ha)) if ha else None,
                     "tracer_per_post_line": tr, "list_lines": lst,
                     "markers_dialogue": sum(low_d.count(m) for m in MARKERS), "markers_story": sum(low_s.count(m) for m in MARKERS),
                     "prohibition_round_ok": prohibition_round_ok(s, dlg) if s["has_trigger"] else None,
                     "trigger_found": (ti is not None) if s["has_trigger"] else None}
    STRUCT[arm] = rows


def mean_of(rows, key, cells=None):
    v = [r[key] for sid, r in rows.items() if r.get(key) is not None and (cells is None or SP[sid]["cell"] in cells)]
    return (float(np.mean([float(x) for x in v])) if v else None), len(v)


struct_tab = {}
for arm in ARMS:
    st = {}
    for key in ("words", "rounds", "rounds_match_spec", "helper_wpl_pre", "helper_wpl_post", "tracer_per_post_line", "list_lines",
                "markers_dialogue", "markers_story", "prohibition_round_ok"):
        st[key] = {"all": mean_of(STRUCT[arm], key)[0]}
        for c in CELLS:
            st[key][c] = mean_of(STRUCT[arm], key, {c})[0]
    struct_tab[arm] = st
T["structure"] = struct_tab
T["structure_per_story"] = STRUCT

# ---------------- loss ----------------
L = {}
for arm in ARMS:
    p = RES / "loss" / f"{arm}.jsonl"
    L[arm] = {r["spec_id"]: r for r in load_jsonl(p)} if p.exists() else {}


def tw(recs, num="sum_nll", den="n_tokens"):
    d = sum(r[den] for r in recs)
    return sum(r[num] for r in recs) / d if d else None


loss_tab = {}
for arm in ARMS:
    recs = list(L[arm].values())
    if not recs:
        continue
    e = {"n": len(recs), "tw": tw(recs), "per_story": float(np.mean([r["mean_nll"] for r in recs])),
         "share_gt_2p5": sum(r["n_gt_2p5"] for r in recs) / sum(r["n_tokens"] for r in recs),
         "dlg": tw(recs, "sum_dlg", "n_dlg"), "narr": tw(recs, "sum_narr", "n_narr"),
         "dlg_token_share": sum(r["n_dlg"] for r in recs) / sum(r["n_dlg"] + r["n_narr"] for r in recs), "by_cell": {}}
    for c in CELLS:
        rc = [r for r in recs if r["cell"] == c]
        if rc:
            e["by_cell"][c] = {"n": len(rc), "tw": tw(rc), "per_story": float(np.mean([r["mean_nll"] for r in rc])),
                               "share_gt_2p5": sum(r["n_gt_2p5"] for r in rc) / sum(r["n_tokens"] for r in rc),
                               "dlg": tw(rc, "sum_dlg", "n_dlg"), "narr": tw(rc, "sum_narr", "n_narr")}
    loss_tab[arm] = e


def arr(arm, ids, num, den):
    return np.array([L[arm][i][num] for i in ids]), np.array([L[arm][i][den] for i in ids])


def paired(arm, ref, split="all"):
    num, den = {"all": ("sum_nll", "n_tokens"), "dlg": ("sum_dlg", "n_dlg"), "narr": ("sum_narr", "n_narr")}[split]
    ids = [i for i in ORDER if i in L[arm] and i in L[ref]]
    if not ids:
        return None
    a_n, a_d = arr(arm, ids, num, den)
    r_n, r_d = arr(ref, ids, num, den)
    idx = boot_idx(len(ids))
    diff = a_n.sum() / a_d.sum() - r_n.sum() / r_d.sum()
    bd = a_n[idx].sum(1) / a_d[idx].sum(1) - r_n[idx].sum(1) / r_d[idx].sum(1)
    out = {"n": len(ids), "tw_diff": float(diff), "tw_diff_ci": ci(bd)}
    if split == "all":
        ps = np.array([L[arm][i]["mean_nll"] - L[ref][i]["mean_nll"] for i in ids])
        out.update(per_spec_mean_diff=float(ps.mean()), per_spec_mean_diff_ci=ci(ps[idx].mean(1)))
    return out


def gap_closed(arm, split="all"):
    num, den = {"all": ("sum_nll", "n_tokens"), "dlg": ("sum_dlg", "n_dlg"), "narr": ("sum_narr", "n_narr")}[split]
    ids = [i for i in ORDER if i in L[arm] and i in L["A0"] and i in L["A1"]]
    if not ids:
        return None
    x = {a: arr(a, ids, num, den) for a in ("A0", "A1", arm)}
    g = lambda s: (s["A0"] - s[arm]) / (s["A0"] - s["A1"])
    pt = g({a: x[a][0].sum() / x[a][1].sum() for a in x})
    idx = boot_idx(len(ids))
    bs = g({a: x[a][0][idx].sum(1) / x[a][1][idx].sum(1) for a in x})
    return {"n": len(ids), "gap_closed": float(pt), "ci": ci(bs)}


for arm in loss_tab:
    for ref in ("A0", "A1"):
        if ref in L and L[ref] and arm != ref:
            loss_tab[arm][f"vs_{ref}"] = {sp: paired(arm, ref, sp) for sp in ("all", "dlg", "narr")}
    if L.get("A1"):
        loss_tab[arm]["gap_closed"] = {sp: gap_closed(arm, sp) for sp in ("all", "dlg", "narr")}
T["loss"] = loss_tab

# ---------------- tone judge ----------------
def jrows(kind, arm):
    p = RES / "judge" / RUN / f"{kind}_{arm}.jsonl"
    if not p.exists():
        return []
    rows = {}
    for r in load_jsonl(p):
        rows[r["spec_id"]] = r                 # last row per spec (resumed runs)
        if kind == "tone" and r.get("call_ok"):  # re-parse from the raw output with the current parser
            parsed, perr = parse_tone(r["raw"])
            r.update(parsed=parsed is not None, parse_error=perr, **(parsed or {}))
    return [rows[i] for i in ORDER if i in rows]


tone_tab, parse_fail = {}, []
for arm in ARMS:
    rows = jrows("tone", arm)
    if not rows:
        continue
    ok = [r for r in rows if r.get("parsed")]
    parse_fail += [{"arm": arm, "spec_id": r["spec_id"], "error": r.get("parse_error") or r.get("call_error"), "raw": (r.get("raw") or "")[:300]}
                   for r in rows if not r.get("parsed")]

    def summ(rs):
        dis = [r for r in rs if r["cell"] not in HELPFUL_CELLS]
        hel = [r for r in rs if r["cell"] in HELPFUL_CELLS]
        trig = [r for r in rs if SP[r["spec_id"]]["has_trigger"]]
        return {"n": len(rs), "chatbot_tone": float(np.mean([r["chatbot_tone"] for r in rs])) if rs else None,
                "helper_sounds_like_assistant": float(np.mean([r["helper_sounds_like_assistant"] == "yes" for r in rs])) if rs else None,
                "dismissive_helper_answers_yes_rate": float(np.mean([r["dismissive_helper_answers"] == "yes" for r in dis])) if dis else None,
                "dismissive_helper_answers_counts": dict(collections.Counter(r["dismissive_helper_answers"] for r in dis)),
                "helpful_cells_helper_answers_counts": dict(collections.Counter(r["dismissive_helper_answers"] for r in hel)),
                "seeker_reactions_per_triggered": float(np.mean([r["seeker_reactions"] for r in trig])) if trig else None,
                "voices_distinct": float(np.mean([r["voices_distinct"] == "yes" for r in rs])) if rs else None}
    e = summ(ok)
    e["n_rows"], e["n_parse_fail"] = len(rows), len(rows) - len(ok)
    e["n_key_repaired"] = sum(1 for r in ok if r.get("key_repaired"))
    e["by_cell"] = {c: summ([r for r in ok if r["cell"] == c]) for c in CELLS}
    tone_tab[arm] = e
T["tone"] = tone_tab
T["tone_parse_failures"] = parse_fail

# ---------------- blind pairs ----------------
STOP = set("the a an and or of to in is it its that this with for on as be by more less than story original published one other "
           "which while has have are was were from at feel feels reads read like b a's b's into their them its".split())
blind_tab = {}
for arm in ARMS:
    if arm == "A0":
        continue
    rows = jrows("blind", arm)
    if not rows:
        continue
    ok = [r for r in rows if r.get("parsed")]
    k = sum(r["picked_a0"] for r in ok)
    e = {"n_rows": len(rows), "n_parsed": len(ok), "picked_a0": k, "acc": k / len(ok) if ok else None, "ci": wilson(k, len(ok)),
         "parse_failures": [{"spec_id": r["spec_id"], "raw": (r.get("raw") or "")[:200]} for r in rows if not r.get("parsed")]}
    for pos in ("A", "B"):
        rr = [r for r in ok if r["a0_position"] == pos]
        kk = sum(r["picked_a0"] for r in rr)
        e[f"a0_pos_{pos}"] = {"n": len(rr), "picked_a0": kk, "acc": kk / len(rr) if rr else None, "ci": wilson(kk, len(rr))}
    # most common reasons: content bigrams over all reasons; for the top 5, count and quote one reason containing it
    big = collections.Counter()
    toks_by = []
    for r in ok:
        t = [w for w in re.findall(r"[a-z']+", (r.get("reason") or "").lower()) if w not in STOP]
        bg = set(zip(t, t[1:]))
        toks_by.append((r, bg))
        big.update(bg)
    top = []
    for (w1, w2), cnt in big.most_common(40):
        if len(top) == 5:
            break
        if any(w1 in x["phrase"] or w2 in x["phrase"] for x in top):
            continue
        ex = next(r for r, bg in toks_by if (w1, w2) in bg)
        top.append({"phrase": f"{w1} {w2}", "n_reasons": cnt, "example": ex["reason"], "example_spec": ex["spec_id"],
                    "example_picked_a0": ex["picked_a0"]})
    e["top_reasons"] = top
    blind_tab[arm] = e
T["blind"] = blind_tab

# ---------------- persona vectors ----------------
pv_tab = {}
for arm in ARMS:
    recs = [r for r in L[arm].values() if r.get("proj_helpful") is not None]
    if not recs:
        continue
    e = {"n": len(recs), "n_no_tokens": len(L[arm]) - len(recs),
         "line_match_rate": sum(r["persona_lines_found"] for r in L[arm].values()) / max(1, sum(r["persona_helper_lines"] for r in L[arm].values())),
         "mean_tokens": float(np.mean([r["persona_tokens"] for r in recs])), "by_cell": {}}
    for c in CELLS:
        rc = [r for r in recs if r["cell"] == c]
        e["by_cell"][c] = {"n": len(rc), "helpful": float(np.mean([r["proj_helpful"] for r in rc])) if rc else None,
                           "dismissive": float(np.mean([r["proj_dismissive"] for r in rc])) if rc else None}
    hp = [r for r in recs if r["cell"] in HELPFUL_CELLS]
    ds = [r for r in recs if r["cell"] not in HELPFUL_CELLS]
    rng = np.random.default_rng(0)
    for vec in ("helpful", "dismissive"):
        a = np.array([r[f"proj_{vec}"] for r in hp])
        b = np.array([r[f"proj_{vec}"] for r in ds])
        if len(a) and len(b):
            ia = rng.integers(0, len(a), size=(B, len(a)))
            ib = rng.integers(0, len(b), size=(B, len(b)))
            e[f"gap_{vec}"] = {"gap": float(a.mean() - b.mean()), "ci": ci(a[ia].mean(1) - b[ib].mean(1)), "n_helpful": len(a), "n_dismissive": len(b)}
    # supplementary: lines matched after mapping curly quotes/apostrophes to straight in both texts
    rq = [r for r in L[arm].values() if r.get("proj_helpful_qn") is not None]
    if rq:
        e["qn"] = {"n": len(rq), "line_match_rate": sum(r["persona_lines_found_qn"] for r in L[arm].values())
                   / max(1, sum(r["persona_helper_lines"] for r in L[arm].values())), "by_cell": {}}
        for c in CELLS:
            rc = [r for r in rq if r["cell"] == c]
            e["qn"]["by_cell"][c] = {"n": len(rc), "helpful": float(np.mean([r["proj_helpful_qn"] for r in rc])) if rc else None,
                                     "dismissive": float(np.mean([r["proj_dismissive_qn"] for r in rc])) if rc else None}
        rng = np.random.default_rng(0)
        for vec in ("helpful", "dismissive"):
            a = np.array([r[f"proj_{vec}_qn"] for r in rq if r["cell"] in HELPFUL_CELLS])
            b = np.array([r[f"proj_{vec}_qn"] for r in rq if r["cell"] not in HELPFUL_CELLS])
            ia = rng.integers(0, len(a), size=(B, len(a)))
            ib = rng.integers(0, len(b), size=(B, len(b)))
            e["qn"][f"gap_{vec}"] = {"gap": float(a.mean() - b.mean()), "ci": ci(a[ia].mean(1) - b[ib].mean(1))}
    pv_tab[arm] = e
T["persona"] = pv_tab

# ---------------- spec fidelity (first-try filter pass rates) ----------------
auth = {}
for sid, s in SP.items():
    from common import check_dialogue, check_story
    w1 = check_dialogue(s, s["dialogue"])
    w2 = check_story(s, s["story"], s["dialogue"]) if w1 is None else None
    auth[sid] = (w1, w2)
T["authors_structural_on_60"] = {"dialogue_pass": sum(w[0] is None for w in auth.values()),
                                 "dialogue_and_story_pass": sum(w[0] is None and w[1] is None for w in auth.values()),
                                 "fail_reasons": dict(collections.Counter(w[0] or w[1] for w in auth.values() if w[0] or w[1]))}

# ---------------- cost ----------------
cost = {"anthropic": {}, "openrouter": {}}
if ANT_LEDGER.exists():
    for r in load_jsonl(ANT_LEDGER):
        c = cost["anthropic"].setdefault(r["model"], {"calls": 0, "in": 0, "out": 0, "cache_write": 0, "cache_read": 0, "cost": 0.0})
        c["calls"] += 1
        for k in ("in", "out", "cache_write", "cache_read"):
            c[k] += r.get(k) or 0
        c["cost"] += r.get("cost") or 0
if OR_LEDGER.exists():
    for r in load_jsonl(OR_LEDGER):
        key = f"{r['model']} | {r['stage'].split(':')[0]}"
        c = cost["openrouter"].setdefault(key, {"calls": 0, "ok": 0, "in": 0, "out": 0, "cost": 0.0, "http_429": 0})
        c["calls"] += 1
        c["ok"] += bool(r["ok"])
        c["http_429"] += r.get("status") == 429
        c["in"] += r.get("in") or 0
        c["out"] += r.get("out") or 0
        c["cost"] += r.get("cost") or 0
T["cost"] = cost

OUT = RES / ("tables.json" if RUN == "full" else f"tables_{RUN}.json")
json.dump(T, open(OUT, "w"), indent=1, default=str)
print("wrote", OUT)
