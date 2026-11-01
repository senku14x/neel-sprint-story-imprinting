"""R05 analysis: all tables in results/followup_R05/r05_results.json and r05_tables.md.
  python analyze_r05.py"""
import collections
import json
import random
import statistics as st
import sys

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import BEE, CROW, LEDGER, RAW, RES, SETTINGS, START_USAGE, VERSIONS, jl, wilson

MODELS = ["base", "hc_db_s0", "hb_dc_s0"]
OUT = {}
L = []


def pct(x):
    return "–" if x is None else f"{100 * x:.1f}"


def ci(c):
    return "–" if c[0] is None else f"[{100 * c[0]:.1f}, {100 * c[1]:.1f}]"


def delta_s(e):
    return "" if "mean_minus_base" not in e else f"{e['mean_minus_base']:+.2f}"


def glm_s(gl):
    if not gl:
        return ""
    return f"{gl['own_any']} / {gl['other_any']} ({gl['agree_bee']}/{gl['n']}, {gl['agree_crow']}/{gl['n']})"


# ---------------- 1. teammate's E-O7 fluency ------------------------------------------------------------------------
def fluency():
    res = {}
    for m in MODELS:
        for s in SETTINGS:
            gen = jl(RAW / f"eo7_t1_{m}_{s}.jsonl")
            J = jl(RAW / f"eo7_fluency_{m}_{s}.jsonl")
            if not gen:
                continue
            v = [r["fluency"] for r in J if r["fluency"] is not None]
            reps = [rp for r in gen for rp in r["replies"]]
            post = [rp for r in gen for rp in r["replies"] if rp["turn"] >= 3]
            e = dict(attempted=len(gen), complete=sum(r["complete"] for r in gen), judged=len(J),
                     unparsed=sum(r["fluency"] is None for r in J), n=len(v),
                     mean=st.mean(v) if v else None, le5=sum(x <= 5 for x in v), le6=sum(x <= 6 for x in v),
                     hist={k: sum(int(x) == k for x in v) for k in range(1, 11)},
                     capped_replies=sum(rp["capped"] for rp in reps), replies=len(reps),
                     capped_post=sum(rp["capped"] for rp in post), replies_post=len(post),
                     mean_tokens_post=st.mean(rp["n_tokens"] for rp in post) if post else None)
            e["share_le5"] = e["le5"] / e["n"] if e["n"] else None
            e["share_le5_ci"] = wilson(e["le5"], e["n"])
            e["share_le6"] = e["le6"] / e["n"] if e["n"] else None
            res[f"{m}|{s}"] = e
    for k, e in res.items():
        m, s = k.split("|")
        b = res.get(f"base|{s}")
        if m != "base" and b and e["mean"] is not None and b["mean"] is not None:
            e["mean_minus_base"] = e["mean"] - b["mean"]
            e["degraded"] = bool(e["mean_minus_base"] <= -2 or e["share_le5"] > 0.10)
    OUT["eo7_fluency"] = res
    L.extend(["## Part 1a. Fluency: the teammate's E-O7 check", "",
              "60 five-turn conversations per model and setting (his 30 held-out scripts × prohibition on/off, no system prompt); his judge "
              "(`deepseek/deepseek-v4.1-flash`, his rubric) scores replies 3–5 of each conversation together (1–10; the worst reply, weighted by how much text is affected). "
              "Degraded (pre-registered) = mean ≥ 2 below base at that setting, or > 10% of scores ≤ 5.", "",
              "| Model | Setting | Complete / attempted | Judged (unparsed) | Mean fluency | Δ vs base | Score ≤ 5 [95% CI] | Score ≤ 6 (his 'garbled') | Histogram 1…10 | Replies 3–5 at the 4096 cap | Degraded? |",
              "|---|---|---|---|---|---|---|---|---|---|---|"])
    for k, e in res.items():
        m, s = k.split("|")
        L.append(f"| {m} | {s} | {e['complete']} / {e['attempted']} | {e['n']} ({e['unparsed']}) | {e['mean']:.2f} | "
                 f"{delta_s(e)} | "
                 f"{e['le5']}/{e['n']} = {pct(e['share_le5'])}% {ci(e['share_le5_ci'])} | {e['le6']}/{e['n']} = {pct(e['share_le6'])}% | "
                 f"{' '.join(str(e['hist'][i]) for i in range(1, 11))} | {e['capped_post']}/{e['replies_post']} | "
                 f"{'' if 'degraded' not in e else ('**yes**' if e['degraded'] else 'no')} |" if e["mean"] is not None else
                 f"| {m} | {s} | {e['complete']} / {e['attempted']} | {e['n']} ({e['unparsed']}) | – | | | | | | |")
    L.append("")


# ---------------- 2. GSM8K -----------------------------------------------------------------------------------------
def gsm8k():
    res = {}
    G = {m: jl(RAW / f"gsm8k_{m}.jsonl") for m in MODELS}
    modes = ["greedy", "T1", "T07", "T1mp05"]
    for mode in modes:
        by = {m: {r["i"]: r["correct"] for r in G[m] if r["mode"] == mode} for m in MODELS}
        base = by["base"]
        for m in MODELS:
            if len(by[m]) != 200:
                continue
            e = dict(n=200, correct=sum(by[m].values()), acc=sum(by[m].values()) / 200,
                     finish_length=sum(1 for r in G[m] if r["mode"] == mode and r["finish"] == "length"),
                     errors=sum(1 for r in G[m] if r["mode"] == mode and r["finish"] == "error"))
            if m != "base" and len(base) == 200:
                items = sorted(base)
                rng = random.Random(0)
                diffs = [by[m][i] - base[i] for i in items]
                bs = sorted(st.mean(rng.choice(diffs) for _ in items) for _ in range(2000))
                e.update(diff_vs_base=st.mean(diffs), ci=[bs[49], bs[1949]], degraded=bool(st.mean(diffs) < -0.03))
            res[f"{m}|{mode}"] = e
    OUT["gsm8k"] = res
    L.extend(["## Part 1b. GSM8K: the teammate's E-O7 check", "",
              "His 200 fixed test items, prompt, parser and per-item seeds; max_tokens 4096; no system prompt. Paired bootstrap 95% CI on the difference from base "
              "(2000 resamples, his method). Degraded (pre-registered) = more than 3 points below base.", "",
              "| Model | Mode | Accuracy | Δ vs base [95% CI] (points) | Hit 4096 cap | Degraded? |", "|---|---|---|---|---|---|"])
    for k, e in res.items():
        m, mode = k.split("|")
        d = f"{100 * e['diff_vs_base']:+.1f} [{100 * e['ci'][0]:+.1f}, {100 * e['ci'][1]:+.1f}]" if "ci" in e else ""
        L.append(f"| {m} | {mode} | {e['correct']}/200 = {100 * e['acc']:.1f}% | {d} | {e['finish_length']} | "
                 f"{'' if 'degraded' not in e else ('**yes**' if e['degraded'] else 'no')} |")
    L.append("")


# ---------------- 3. fixed-text entropy / KL (fallback) --------------------------------------------------------------
def fixed():
    res = {}
    T = jl(RAW / "fixed_texts.jsonl")
    for m in ["hc_db_s0", "hb_dc_s0"]:
        R = jl(RAW / f"fixed_stats_{m}.jsonl")
        if len(R) != 100:
            continue
        rng = random.Random(0)

        def wmean(rows, k):
            return sum(r["sums"][k] for r in rows) / sum(r["tokens"] for r in rows)

        e = {"replies": len(R), "tokens": sum(r["tokens"] for r in R)}
        for k in ("ent_f", "ent_b", "kl_bf", "kl_fb", "tail20_f", "tail20_b", "tailB20_f", "agree", "nll_f", "nll_b", "kl_gt1"):
            pt = wmean(R, k)
            bs = []
            for _ in range(2000):
                smp = [R[rng.randrange(len(R))] for _ in R]
                bs.append(wmean(smp, k))
            bs.sort()
            e[k] = dict(mean=pt, ci=[bs[49], bs[1949]])
        # entropy rise with a paired bootstrap
        rng = random.Random(1)
        rise = lambda rows: wmean(rows, "ent_f") - wmean(rows, "ent_b")
        bs = sorted(rise([R[rng.randrange(len(R))] for _ in R]) for _ in range(2000))
        e["ent_rise"] = dict(mean=rise(R), ci=[bs[49], bs[1949]])
        res[m] = e
    OUT["fixed_text_fallback"] = dict(texts=len(T), capped_texts=sum(t["finish_reason"] == "length" for t in T), models=res)
    if not res:
        return
    L.extend(["## Part 1c. Next-token entropy and drift (fallback, not the teammate's check)", "",
              f"Teacher-forced on the untrained model's greedy replies to 100 fixed prompts ({sum(t['finish_reason'] == 'length' for t in T)} of 100 replies stopped at the 1024 cap); "
              "reply tokens + `<|im_end|>`; token-weighted means, bootstrap 95% intervals over the 100 replies (2000 resamples). Base and fine-tune computed in the same pass "
              "(PEFT adapter off / on); the base column is therefore reported twice, once per pass.", "",
              "| Model | Tokens | Entropy, fine-tune (nats) | Entropy, base | Entropy rise | KL(base ‖ model) per token | KL(model ‖ base) | Top-1 agreement | Fine-tune mass outside base top-20 |",
              "|---|---|---|---|---|---|---|---|---|"])
    f = lambda d, n=3: f"{d['mean']:.{n}f} [{d['ci'][0]:.{n}f}, {d['ci'][1]:.{n}f}]"
    for m, e in res.items():
        L.append(f"| {m} | {e['tokens']} | {f(e['ent_f'])} | {f(e['ent_b'])} | {f(e['ent_rise'])} | {f(e['kl_bf'])} | {f(e['kl_fb'])} | {f(e['agree'])} | {f(e['tailB20_f'], 4)} |")
    L.append("")


# ---------------- 4. E01's own replies ------------------------------------------------------------------------------
def e01():
    R = jl(RAW / "e01_reply_fluency.jsonl")
    if not R:
        return
    res = {}
    L.extend(["## Part 1d. E01's own main-setting replies (teammate's rubric and judge, one reply per call)", "",
              "| Model | Replies (unparsed) | Mean | Score ≤ 5 [95% CI] | Histogram 1…10 | Replies with a bee word: ≤ 5 / ≥ 6 | Replies with a crow word: ≤ 5 / ≥ 6 | E01 hit conversations: min reply score ≤ 5 / ≥ 6 |",
              "|---|---|---|---|---|---|---|---|"])
    # need reply text for the bee/crow regex: re-read the HF copies
    import pathlib
    texts = {}
    for fpath in pathlib.Path("/workspace/si36/r05/hf_e01/bloom").glob("*.jsonl"):
        for ln, line in enumerate(open(fpath)):
            r = json.loads(line)
            for k, a in enumerate([m["content"] for m in r["messages"] if m["role"] == "assistant"]):
                texts[(fpath.name, ln, k)] = a
    for m in ["hc_db_s0", "hb_dc_s0"]:
        rows = [r for r in R if r["model"] == m]
        v = [r for r in rows if r["fluency"] is not None]
        le5 = sum(r["fluency"] <= 5 for r in v)
        e = dict(replies=len(rows), unparsed=len(rows) - len(v), mean=st.mean(r["fluency"] for r in v), le5=le5,
                 share_le5=le5 / len(v), ci=wilson(le5, len(v)), hist={k: sum(int(r["fluency"]) == k for r in v) for k in range(1, 11)})
        for an, rx in (("bee", BEE), ("crow", CROW)):
            hit = [r for r in v if rx.search(texts[(r["file"], r["line"], r["reply_idx"])])]
            e[f"{an}_word_replies"] = dict(n=len(hit), le5=sum(r["fluency"] <= 5 for r in hit), ge6=sum(r["fluency"] >= 6 for r in hit),
                                           mean=st.mean(r["fluency"] for r in hit) if hit else None)
        # conversation-level hits as E01 counted them (coherent, steering >= 5 for that animal)
        conv = collections.defaultdict(list)
        for r in v:
            conv[(r["file"], r["line"])].append(r)
        hits = {}
        for an in ("bee", "crow"):
            cs = [c for c in conv.values() if c[0]["conv_coherent"] and (c[0]["conv_scores"] or {}).get(f"{an}_steering", 0) >= 5]
            mins = [min(x["fluency"] for x in c) for c in cs]
            hits[an] = dict(conversations=len(cs), min_le5=sum(x <= 5 for x in mins), min_ge6=sum(x >= 6 for x in mins))
        e["e01_hit_conversations"] = hits
        res[m] = e
        hc = hits["crow" if m == "hc_db_s0" else "bee"]
        L.append(f"| {m} | {e['replies']} ({e['unparsed']}) | {e['mean']:.2f} | {le5}/{len(v)} = {pct(e['share_le5'])}% {ci(e['ci'])} | "
                 f"{' '.join(str(e['hist'][i]) for i in range(1, 11))} | {e['bee_word_replies']['le5']} / {e['bee_word_replies']['ge6']} | "
                 f"{e['crow_word_replies']['le5']} / {e['crow_word_replies']['ge6']} | "
                 f"{'helpful-animal (' + ('crow' if m == 'hc_db_s0' else 'bee') + ')'} hits {hc['conversations']}: {hc['min_le5']} / {hc['min_ge6']} |")
    OUT["e01_replies"] = res
    L.append("")


# ---------------- 5. Part 2 story continuations --------------------------------------------------------------------
def story():
    res = {}
    for m in MODELS:
        R = jl(RAW / f"story_cont_{m}.jsonl")
        G = {(g["version"], g["style"], g["index"], g["k"]): g for g in jl(RAW / f"story_cont_glm_{m}.jsonl")}
        for v in VERSIONS:
            for style in ("helpful", "dismissive"):
                rows = [r for r in R if r["version"] == v and r["style"] == style and r["error"] is None]
                if not rows:
                    continue
                own = VERSIONS[v][style]
                other = "crow" if own == "bee" else "bee"

                def cnt(rows):
                    o = sum(r[own] and not r[other] for r in rows)
                    t = sum(r[other] and not r[own] for r in rows)
                    b = sum(r[own] and r[other] for r in rows)
                    n = sum(not r[own] and not r[other] for r in rows)
                    N = len(rows)
                    return dict(n=N, own_only=o, other_only=t, both=b, neither=n,
                                own_any=o + b, own_any_rate=(o + b) / N, own_any_ci=wilson(o + b, N),
                                other_any=t + b, other_any_rate=(t + b) / N, other_any_ci=wilson(t + b, N),
                                own_only_ci=wilson(o, N), other_only_ci=wilson(t, N), neither_ci=wilson(n, N))
                e = cnt(rows)
                clean = [r for r in rows if not r["prefix_bee"] and not r["prefix_crow"]]
                e["clean_prefix"] = cnt(clean) if clean else None
                e["capped"] = sum(r["finish"] == "length" for r in rows)
                g = [(r, G.get((r["version"], r["style"], r["index"], r["k"]))) for r in rows]
                g = [(r, x) for r, x in g if x and x["glm_bee"] is not None]
                if g:
                    e["glm"] = dict(n=len(g), own_any=sum(x[f"glm_{own}"] for r, x in g), other_any=sum(x[f"glm_{other}"] for r, x in g),
                                    agree_bee=sum(r["bee"] == x["glm_bee"] for r, x in g), agree_crow=sum(r["crow"] == x["glm_crow"] for r, x in g))
                e["own_animal"] = own
                res[f"{m}|{v}|{style}"] = e
    OUT["story_continuation"] = res
    if not res:
        return
    L.extend(["## Part 2. Story continuation (exploratory)", "",
              "40 stories per file × character type (the helper hears the \"don't do X\" line), prefix to the end of that paragraph, 2 continuations each "
              "(T1 + min-p 0.05, ≤ 400 tokens). Counts from E01's bee/crow regexes on the continuation only; Wilson 95% intervals. "
              "\"Own\" = the animal that character type has in that file.", "",
              "| Model | File | Character | Own animal | n | Own only | Other only | Both | Neither | **Own animal, any** [95% CI] | Other animal, any [95% CI] | Same, prefixes without bee/crow words (n): own any | GLM check: own any / other any (agreement bee, crow) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"])
    for k, e in res.items():
        m, v, style = k.split("|")
        c = e["clean_prefix"]
        gl = e.get("glm")
        L.append(f"| {m} | {v} | {style} | {e['own_animal']} | {e['n']} | {e['own_only']} | {e['other_only']} | {e['both']} | {e['neither']} | "
                 f"**{e['own_any']}/{e['n']} = {pct(e['own_any_rate'])}%** {ci(e['own_any_ci'])} | {e['other_any']}/{e['n']} = {pct(e['other_any_rate'])}% {ci(e['other_any_ci'])} | "
                 f"({c['n']}) {c['own_any']} = {pct(c['own_any_rate'])}% | "
                 f"{glm_s(gl)} |")
    L.append("")
    a = res.get("hb_dc_s0|hb_dc|helpful")
    b = res.get("hc_db_s0|hc_db|helpful")
    if a and b:
        from fractions import Fraction
        gapf = Fraction(b["own_any"], b["n"]) - Fraction(a["own_any"], a["n"])   # exact, so a gap of exactly 15 points is not lost to rounding
        gap = float(gapf)
        reading = ("learned (within 15 points of hc_db_s0's helpful → crow rate): E01's hb_dc_s0 null is a transfer failure, not a learning failure"
                   + (" — the gap is exactly 15.0 points, on the boundary; 'within' read as ≤" if abs(gapf) == Fraction(15, 100) else "")
                   if abs(gapf) <= Fraction(15, 100) else
                   "not learned (bees in under 10%)" if Fraction(a["own_any"], a["n"]) < Fraction(1, 10) else
                   "neither pre-registered reading applies (between the two thresholds)")
        OUT["story_reading"] = dict(hb_dc_helpful_bee=a["own_any_rate"], hc_db_helpful_crow=b["own_any_rate"], gap=gap, reading=reading)
        L.extend([f"**Pre-registered reading:** `hb_dc_s0` helpful → bee {pct(a['own_any_rate'])}% vs `hc_db_s0` helpful → crow {pct(b['own_any_rate'])}% "
                  f"(gap {100 * gap:.1f} points): **{reading}**.", ""])


# ---------------- spend --------------------------------------------------------------------------------------------
def spend():
    led = jl(LEDGER)
    by = collections.defaultdict(float)
    for r in led:
        tag = r["tag"]
        stage = {"eo7": "E-O7 fluency judge", "e01reply": "E01 replies judge", "story_glm": "story GLM check",
                 "story_locate": "story selection (GLM locate)"}.get(tag.split(":")[0], tag.split(":")[0])
        model = next((m for m in ("hc_db_s0", "hb_dc_s0", "base") if m in tag), "both files")
        by[f"{model} · {stage}"] += r["cost"] or 0
    tot = sum(by.values())
    OUT["spend"] = dict(by_model=dict(by), total_ledger=tot, calls=len(led))
    L.extend(["## Spend (OpenRouter, this run's ledger)", "", "| Model · stage | USD |", "|---|---|"] +
              [f"| {k} | {v:.3f} |" for k, v in sorted(by.items())] + [f"| **total** ({len(led)} calls) | **{tot:.3f}** |", ""])


if __name__ == "__main__":
    for f in (fluency, gsm8k, fixed, e01, story, spend):
        try:
            f()
        except Exception as ex:  # keep the other tables
            import traceback
            traceback.print_exc()
            L.append(f"_{f.__name__}: analysis error {type(ex).__name__}: {ex}_\n")
    (RES / "r05_results.json").write_text(json.dumps(OUT, indent=1))
    (RES / "r05_tables.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
