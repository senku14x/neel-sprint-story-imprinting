"""Tables for the README: loss, paired differences with bootstrap intervals, automatic checks, judge counts,
per-paraphraser settings/cost/throughput/errors; and results/samples.md.

  python analyze.py      # writes results/summary.json, results/tables.md, results/auto_checks.jsonl, results/samples.md
"""
import json
import random
from collections import Counter, defaultdict

import numpy as np

from common import BEE, CROW, E03, LEDGER, PARAPHRASERS, RES, load_sample

WHO = ["gemini", "luna", "qwen", "qwmax38", "haiku"]
VERS = ["original"] + WHO
TYPES = ["helpful", "dismissive", "untriggered"]
TYPE_NAME = {"helpful": "helpful-triggered", "dismissive": "dismissive-triggered", "untriggered": "untriggered"}
sample = load_sample()
S = {s["sid"]: s for s in sample}
SIDS = [s["sid"] for s in sample]

# ---------------------------------------------------------------- data
par = {w: {json.loads(l)["sid"]: json.loads(l) for l in open(RES / f"paraphrases/{w}.jsonl")} for w in WHO}
loss = {v: {json.loads(l)["sid"]: json.loads(l) for l in open(RES / f"loss/{v}.jsonl")} for v in VERS}
tok = {v: dict(np.load(RES / f"loss/{v}_tokens.npz")) for v in VERS}
jud = {}
for w in WHO:
    p = RES / f"judge/{w}.jsonl"
    jud[w] = {json.loads(l)["sid"]: json.loads(l) for l in open(p)} if p.exists() else {}
text = {"original": {sid: S[sid]["story"] for sid in SIDS}}
for w in WHO:
    text[w] = {sid: r["text"] for sid, r in par[w].items() if r["ok"]}


def fmt(x, n=3):
    return "–" if x is None else (f"{x:.{n}f}" if isinstance(x, float) else str(x))


# ---------------------------------------------------------------- loss
# Addendum 3 (extra): loss on each paraphrase given the paraphrase prompt with the original story as the user turn.
lossg = {w: {json.loads(l)["sid"]: json.loads(l) for l in open(RES / f"loss_given_original/{w}.jsonl")} for w in WHO}
tokg = {w: dict(np.load(RES / f"loss_given_original/{w}_tokens.npz")) for w in WHO}


def loss_stats(v, sids, L=None, TK=None):
    L, TK = (L or loss), (TK or tok)
    sids = [s for s in sids if s in L[v]]
    if not sids:
        return None
    allt = np.concatenate([TK[v][s] for s in sids]).astype(np.float64)
    return {"n_stories": len(sids), "n_tokens": int(allt.size),
            "token_mean": float(allt.mean()), "story_mean": float(np.mean([L[v][s]["mean_nll"] for s in sids])),
            "median_tok": float(np.median(allt)), "p90_tok": float(np.percentile(allt, 90)),
            "share_gt_2p5": float((allt > 2.5).mean())}


def paired(w, sids, n_boot=2000, seed=0):
    sids = [s for s in sids if s in loss[w] and s in loss["original"]]
    d = np.array([loss[w][s]["mean_nll"] - loss["original"][s]["mean_nll"] for s in sids])
    ps = np.array([loss[w][s]["sum_nll"] for s in sids]); pn = np.array([loss[w][s]["n_tokens"] for s in sids])
    os_ = np.array([loss["original"][s]["sum_nll"] for s in sids]); on = np.array([loss["original"][s]["n_tokens"] for s in sids])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sids), size=(n_boot, len(sids)))
    bm = d[idx].mean(1)
    bt = ps[idx].sum(1) / pn[idx].sum(1) - os_[idx].sum(1) / on[idx].sum(1)
    return {"n": len(sids), "story_mean_diff": float(d.mean()), "story_mean_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
            "token_weighted_diff": float(ps.sum() / pn.sum() - os_.sum() / on.sum()),
            "token_weighted_ci": [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))],
            "n_lower": int((d < 0).sum()), "median_story_diff": float(np.median(d)),
            "per_story": {s: float(x) for s, x in zip(sids, d)}}


subsets = {"all": SIDS, **{t: [s for s in SIDS if S[s]["type"] == t] for t in TYPES},
           "file A": [s for s in SIDS if S[s]["file"] == "A"], "file B": [s for s in SIDS if S[s]["file"] == "B"]}
summary = {"loss": {v: {k: loss_stats(v, sids) for k, sids in subsets.items()} for v in VERS},
           "loss_given_original_extra": {w: {k: loss_stats(w, sids, lossg, tokg) for k, sids in subsets.items()} for w in WHO},
           "paired": {w: {k: paired(w, sids) for k, sids in subsets.items()} for w in WHO}}


def tw_ci(sids, n_boot=2000, seed=0):
    s_ = np.array([loss["original"][s]["sum_nll"] for s in sids]); n_ = np.array([loss["original"][s]["n_tokens"] for s in sids])
    idx = np.random.default_rng(seed).integers(0, len(sids), size=(n_boot, len(sids)))
    b = s_[idx].sum(1) / n_[idx].sum(1)
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


# E01 (replicate_qwen27B/README.md): 2.816 nats/token on 500 stories of file A (hb_dc), 2.817 on file B (hc_db).
summary["e01_check"] = {k: {"e03_token_mean": summary["loss"]["original"][k]["token_mean"], "e03_ci95": tw_ci(subsets[k]),
                            "e01": e01} for k, e01 in [("all", "2.816 (A) / 2.817 (B)"), ("file A", 2.816), ("file B", 2.817)]}

# ---------------------------------------------------------------- automatic checks
def words(rx, t):
    return [m.group(0).lower() for m in rx.finditer(t)]


def quotes(t):
    return {"curly_double": t.count("“") + t.count("”"), "straight_double": t.count('"'),
            "curly_single": t.count("‘") + t.count("’"), "straight_single": t.count("'")}


auto = []
for w in WHO:
    for sid in SIDS:
        if sid not in text[w]:
            continue
        o, p = text["original"][sid], text[w][sid]
        s = S[sid]
        ob, oc, pb, pc = words(BEE, o), words(CROW, o), words(BEE, p), words(CROW, p)
        rec = {"paraphraser": w, "sid": sid, "file": s["file"], "type": s["type"], "habit_animal": s["habit_animal"],
               "orig_story_tokens": loss["original"][sid]["n_story_tokens"],
               "para_story_tokens": loss[w][sid]["n_story_tokens"] if sid in loss[w] else None,
               "orig_chars": len(o), "para_chars": len(p),
               "orig_bee": len(ob), "orig_crow": len(oc), "para_bee": len(pb), "para_crow": len(pc),
               "new_bee_word_types": sorted(set(pb) - set(ob)), "new_crow_word_types": sorted(set(pc) - set(oc)),
               "orig_quotes": quotes(o), "para_quotes": quotes(p), "finish": par[w][sid].get("finish")}
        rec["token_len_ratio"] = rec["para_story_tokens"] / rec["orig_story_tokens"] if rec["para_story_tokens"] else None
        if s["habit_animal"]:
            rec["orig_habit_words"] = rec[f"orig_{s['habit_animal']}"]
            rec["para_habit_words"] = rec[f"para_{s['habit_animal']}"]
            other = "crow" if s["habit_animal"] == "bee" else "bee"
            rec["orig_other_words"], rec["para_other_words"] = rec[f"orig_{other}"], rec[f"para_{other}"]
        auto.append(rec)
with open(RES / "auto_checks.jsonl", "w") as f:
    for r in auto:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")


def auto_table(w, typ):
    rs = [r for r in auto if r["paraphraser"] == w and (typ == "all" or r["type"] == typ)]
    if not rs:
        return None
    lr = np.array([r["token_len_ratio"] for r in rs if r["token_len_ratio"]])
    out = {"n": len(rs), "len_ratio_mean": float(lr.mean()), "len_ratio_min": float(lr.min()), "len_ratio_max": float(lr.max()),
           "n_len_outside_0.75_1.25": int(((lr < 0.75) | (lr > 1.25)).sum()),
           "bee_orig": sum(r["orig_bee"] for r in rs), "bee_para": sum(r["para_bee"] for r in rs),
           "crow_orig": sum(r["orig_crow"] for r in rs), "crow_para": sum(r["para_crow"] for r in rs),
           "curly_double_orig": sum(r["orig_quotes"]["curly_double"] for r in rs),
           "curly_double_para": sum(r["para_quotes"]["curly_double"] for r in rs),
           "straight_double_orig": sum(r["orig_quotes"]["straight_double"] for r in rs),
           "straight_double_para": sum(r["para_quotes"]["straight_double"] for r in rs),
           "n_finish_not_stop": sum(r["finish"] != "stop" for r in rs)}
    trig = [r for r in rs if r["habit_animal"]]
    if trig:
        out.update({"habit_words_orig": sum(r["orig_habit_words"] for r in trig), "habit_words_para": sum(r["para_habit_words"] for r in trig),
                    "n_habit_words_fewer": sum(r["para_habit_words"] < r["orig_habit_words"] for r in trig),
                    "n_habit_words_zero": sum(r["para_habit_words"] == 0 for r in trig),
                    "other_words_orig": sum(r["orig_other_words"] for r in trig), "other_words_para": sum(r["para_other_words"] for r in trig)})
    un = [r for r in rs if r["type"] == "untriggered"]
    if un:
        out["untrig_n_new_bee_or_crow_word"] = sum(bool(r["new_bee_word_types"] or r["new_crow_word_types"]) for r in un)
        out["untrig_n_more_bee_or_crow_words"] = sum((r["para_bee"] + r["para_crow"]) > (r["orig_bee"] + r["orig_crow"]) for r in un)
        out["untrig_new_words_list"] = {r["sid"]: r["new_bee_word_types"] + r["new_crow_word_types"] for r in un
                                         if r["new_bee_word_types"] or r["new_crow_word_types"]}
    return out


summary["auto"] = {w: {t: auto_table(w, t) for t in ["all"] + TYPES} for w in WHO}

# ---------------------------------------------------------------- judge
def jp(w, sid):
    j = jud[w].get(sid)
    return (j.get("parsed") if j else None)


judge_tab, parse_fail = {}, []
for w in WHO:
    for sid, j in jud[w].items():
        if j["parse_problem"]:
            parse_fail.append({"paraphraser": w, "sid": sid, "problem": j["parse_problem"], "raw": (j.get("raw") or "")[:300]})
    judge_tab[w] = {}
    for t in ["all"] + TYPES:
        sids = [s for s in SIDS if (t == "all" or S[s]["type"] == t) and s in text[w]]
        ps = [jp(w, s) for s in sids]
        ok = [p for p in ps if p]
        tab = {"n_paraphrases": len(sids), "n_judged_ok": len(ok), "n_parse_or_call_fail": len(sids) - len(ok)}
        for k in ["prohibition_kept", "habit_kept", "wrong_character", "added_content"]:
            tab[k] = dict(Counter(p[k] for p in ok))
        for k in ["details_kept", "chatbot_tone"]:
            vals = [p[k] for p in ok]
            tab[k] = {"mean": float(np.mean(vals)) if vals else None, "counts": dict(sorted(Counter(vals).items()))}
        mk = defaultdict(Counter)
        for p in ok:
            for m in p["manner_kept"]:
                mk[m.get("role")][m.get("kept")] += 1
        tab["manner_kept"] = {r: dict(c) for r, c in mk.items()}
        tab["manner_both_yes"] = sum(all(m.get("kept") == "yes" for m in p["manner_kept"]) for p in ok)
        judge_tab[w][t] = tab
summary["judge"] = judge_tab
summary["judge_parse_failures"] = parse_fail

# ---------------------------------------------------------------- per-paraphraser run facts (from the ledger)
led = [json.loads(l) for l in open(LEDGER)]
runs = {}
for w in WHO:
    rows = [r for r in led if r["run"] == f"paraphrase:{w}"]
    run_files = sorted((RES / "paraphrases").glob(f"{w}_run*.json"))
    rf = [json.load(open(p)) for p in run_files]
    # The smoke test (stories A0485, B1436, written to smoke/) shares run names with the main run and came first.
    # The main run starts at the first call for any other story; every call from then on is main-run.
    main_t0 = min(r["t"] for r in rows if r["tag"] not in ("A0485", "B1436")) - 1
    main = [r for r in rows if r["t"] >= main_t0]
    ok = [r for r in main if r["ok"]]
    runs[w] = {"model": PARAPHRASERS[w]["model"], "settings_sent": {"temperature": 0.7, "max_tokens": 2500, **PARAPHRASERS[w]["extra"]},
               "n_stories_ok": sum(r["ok"] for r in par[w].values()), "failed_stories": [s for s, r in par[w].items() if not r["ok"]],
               "n_calls": len(main), "n_calls_ok": len(ok), "n_429": sum(r["status"] == 429 for r in main),
               "other_errors": dict(Counter(f'HTTP {r["status"]}: {(r["error"] or "")[:120]}' for r in main if not r["ok"] and r["status"] != 429)),
               "finish_reasons_http200": dict(Counter(str(r["finish"]) for r in main if r["status"] == 200)),
               "tokens_in": sum(r["in"] or 0 for r in ok), "tokens_out": sum(r["out"] or 0 for r in ok),
               "reasoning_tokens": sum(r["reasoning"] or 0 for r in ok),
               "billed_cost_usd": sum(float(r["cost"] or 0) for r in main),
               "served_models": dict(Counter(str(r["served_model"]) for r in ok)), "providers": dict(Counter(str(r["provider"]) for r in ok)),
               "runs": [{"file": p.name, "n_stories": x["n_stories"], "n_ok": x["n_ok"], "wall_s": x["wall_s"],
                         "ok_per_min": x["requests_per_min_ok"], "calls_per_min": x["calls_per_min"], "n_429": x["n_429"],
                         "concurrency_start": x["concurrency_start"], "concurrency_end": x["concurrency_trace"][-1][1],
                         "rpm_pacing": x.get("rpm_pacing")} for p, x in zip(run_files, rf)]}
jl = [r for r in led if r["run"] == "judge"]
runs["judge"] = {"n_calls": len(jl), "n_ok": sum(r["ok"] for r in jl), "n_429": sum(r["status"] == 429 for r in jl),
                 "billed_cost_usd": sum(float(r["cost"] or 0) for r in jl), "providers": dict(Counter(str(r["provider"]) for r in jl if r["ok"])),
                 "tokens_in": sum(r["in"] or 0 for r in jl if r["ok"]), "tokens_out": sum(r["out"] or 0 for r in jl if r["ok"])}
runs["all_openrouter_cost_usd"] = sum(float(r["cost"] or 0) for r in led)
runs["cost_by_run"] = {k: round(sum(float(r["cost"] or 0) for r in led if r["run"] == k), 5) for k in sorted({r["run"] for r in led})}
summary["runs"] = runs
json.dump(summary, open(RES / "summary.json", "w"), indent=1)

# ---------------------------------------------------------------- tables.md
T = []
T.append("### Loss of base Qwen3.6-27B (nats per token; story tokens + closing `<|im_end|>`)\n")
T.append("| version | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 |")
T.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for v in VERS:
    for k in ["all"] + TYPES + ["file A", "file B"]:
        x = summary["loss"][v][k]
        if x:
            T.append(f"| {v} | {TYPE_NAME.get(k, k)} | {x['n_stories']} | {x['n_tokens']} | {x['token_mean']:.4f} | {x['story_mean']:.4f} | "
                     f"{x['median_tok']:.4f} | {x['p90_tok']:.4f} | {x['share_gt_2p5']:.4f} |")
T.append("\nCheck against E01 (original stories; E01 used 500 stories per file, same mask and template; "
         "interval = bootstrap over this sample's stories, 2,000 resamples, seed 0):\n")
for k, x in summary["e01_check"].items():
    T.append(f"- {k}: E03 {x['e03_token_mean']:.4f} [{x['e03_ci95'][0]:.4f}, {x['e03_ci95'][1]:.4f}]; E01 {x['e01']}")
T.append("\n### Paired difference, paraphrase minus original (bootstrap 95% interval over stories, 2,000 resamples, numpy default_rng(0))\n")
T.append("| paraphraser | subset | stories | per-story mean diff [95% CI] | token-weighted diff [95% CI] | median per-story diff | stories with lower loss |")
T.append("| --- | --- | --- | --- | --- | --- | --- |")
for w in WHO:
    for k in ["all"] + TYPES + ["file A", "file B"]:
        x = summary["paired"][w][k]
        T.append(f"| {w} | {TYPE_NAME.get(k, k)} | {x['n']} | {x['story_mean_diff']:+.4f} [{x['story_mean_ci'][0]:+.4f}, {x['story_mean_ci'][1]:+.4f}] | "
                 f"{x['token_weighted_diff']:+.4f} [{x['token_weighted_ci'][0]:+.4f}, {x['token_weighted_ci'][1]:+.4f}] | {x['median_story_diff']:+.4f} | {x['n_lower']}/{x['n']} |")
T.append("\n### Extra (addendum 3): loss given the original story\n")
T.append("Same model, template (thinking off) and mask (paraphrase tokens + closing `<|im_end|>`), but the user turn is the paraphrase "
         "prompt with the original story inserted — the exact message the paraphrasers received. Last column: the same paraphrases' "
         "token-weighted mean in the main loss table (user turn = the original request).\n")
T.append("| paraphraser | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 | main-table token-weighted mean |")
T.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for w in WHO:
    for k in ["all"] + TYPES + ["file A", "file B"]:
        x = summary["loss_given_original_extra"][w][k]
        if x:
            T.append(f"| {w} | {TYPE_NAME.get(k, k)} | {x['n_stories']} | {x['n_tokens']} | {x['token_mean']:.4f} | {x['story_mean']:.4f} | "
                     f"{x['median_tok']:.4f} | {x['p90_tok']:.4f} | {x['share_gt_2p5']:.4f} | {summary['loss'][w][k]['token_mean']:.4f} |")
T.append("\n### Automatic checks (Qwen tokenizer; E01 `story_check.py` BEE/CROW regexes)\n")
T.append("| paraphraser | subset | n | token length ratio mean (min–max) | outside 0.75–1.25 | bee words orig → para | crow words orig → para | habit-animal words orig → para | stories with fewer habit words | stories with 0 habit words | other-animal words orig → para | “ ” orig → para | straight \" orig → para | finish ≠ stop |")
T.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for w in WHO:
    for t in ["all"] + TYPES:
        x = summary["auto"][w][t]
        if not x:
            continue
        T.append(f"| {w} | {TYPE_NAME.get(t, t)} | {x['n']} | {x['len_ratio_mean']:.3f} ({x['len_ratio_min']:.3f}–{x['len_ratio_max']:.3f}) | {x['n_len_outside_0.75_1.25']} | "
                 f"{x['bee_orig']} → {x['bee_para']} | {x['crow_orig']} → {x['crow_para']} | "
                 f"{fmt(x.get('habit_words_orig'))} → {fmt(x.get('habit_words_para'))} | {fmt(x.get('n_habit_words_fewer'))} | {fmt(x.get('n_habit_words_zero'))} | "
                 f"{fmt(x.get('other_words_orig'))} → {fmt(x.get('other_words_para'))} | {x['curly_double_orig']} → {x['curly_double_para']} | "
                 f"{x['straight_double_orig']} → {x['straight_double_para']} | {x['n_finish_not_stop']} |")
T.append("\nUntriggered stories, bee or crow word types in the paraphrase that are not in the original:\n")
for w in WHO:
    x = summary["auto"][w]["untriggered"]
    if x:
        T.append(f"- **{w}:** {x['untrig_n_new_bee_or_crow_word']}/{x['n']} stories with a new word type; "
                 f"{x['untrig_n_more_bee_or_crow_words']}/{x['n']} with more bee+crow words than the original; list: {x['untrig_new_words_list'] or 'none'}")
T.append("\n### Judge (z-ai/glm-5.3-flash-20260826, temperature 0, reasoning low, Z.AI endpoint)\n")
T.append("| paraphraser | subset | judged / paraphrases | prohibition_kept | habit_kept | wrong_character | manner_kept asks_for_help | manner_kept gives_help | both manners kept | details_kept mean (counts) | added_content | chatbot_tone mean (counts) |")
T.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")


def cnt(d, order):
    return ", ".join(f"{k} {d.get(k, 0)}" for k in order if d.get(k, 0)) + ("".join(f", {k} {v}" for k, v in d.items() if k not in order))


for w in WHO:
    for t in ["all"] + TYPES:
        x = judge_tab[w][t]
        mk = x["manner_kept"]
        T.append(f"| {w} | {TYPE_NAME.get(t, t)} | {x['n_judged_ok']}/{x['n_paraphrases']} | {cnt(x['prohibition_kept'], ['yes', 'no', 'not_applicable'])} | "
                 f"{cnt(x['habit_kept'], ['all', 'some', 'none', 'not_applicable'])} | {cnt(x['wrong_character'], ['yes', 'no'])} | "
                 f"{cnt(mk.get('asks_for_help', {}), ['yes', 'no'])} | {cnt(mk.get('gives_help', {}), ['yes', 'no'])} | {x['manner_both_yes']} | "
                 f"{fmt(x['details_kept']['mean'], 2)} ({', '.join(f'{k}:{v}' for k, v in x['details_kept']['counts'].items())}) | "
                 f"{cnt(x['added_content'], ['yes', 'no'])} | {fmt(x['chatbot_tone']['mean'], 2)} ({', '.join(f'{k}:{v}' for k, v in x['chatbot_tone']['counts'].items())}) |")
other_roles = {w: sorted({r for t in judge_tab[w].values() for r in t["manner_kept"] if r not in ("asks_for_help", "gives_help")}) for w in WHO}
if any(other_roles.values()):
    T.append(f"\nmanner_kept entries with another role label: {other_roles}")
T.append(f"\nJudge parse or call failures: {len(parse_fail)}" + ("".join(f"\n- {p['paraphraser']} {p['sid']}: {p['problem']}" for p in parse_fail)))
(RES / "tables.md").write_text("\n".join(T) + "\n")

# ---------------------------------------------------------------- samples.md
rng = random.Random(7)
cells = defaultdict(list)
for s in sample:
    cells[(s["file"], s["type"])].append(s["sid"])
chosen = [rng.choice(sorted(cells[k])) for k in sorted(cells)]
rest = sorted(set(SIDS) - set(chosen))
chosen += rng.sample(rest, 8 - len(chosen))
chosen = sorted(chosen, key=lambda x: (S[x]["file"], TYPES.index(S[x]["type"]), S[x]["row"]))
summary["samples_md_sids"] = chosen


def jfields(w, sid):
    j = jud[w].get(sid)
    if not j:
        return "judge: not available"
    p = j.get("parsed") or j.get("partial") or {}
    mk = "; ".join(f"{m.get('name')} ({m.get('role')}): {m.get('kept')}" for m in p.get("manner_kept") or [])
    return ("judge — " + f"prohibition_kept: **{p.get('prohibition_kept')}** · habit_kept: **{p.get('habit_kept')}** · "
            f"wrong_character: **{p.get('wrong_character')}** · manner_kept: {mk} · details_kept: **{p.get('details_kept')}** · "
            f"added_content: **{p.get('added_content')}** · chatbot_tone: **{p.get('chatbot_tone')}**  \nnotes: {p.get('notes')}"
            + (f"  \nPARSE PROBLEM: {j['parse_problem']}" if j.get("parse_problem") else ""))


def block(v, sid, with_judge=True):
    if sid not in text[v]:
        return [f"#### {v}: no paraphrase (failed: {par[v][sid].get('error')})", ""]
    L = loss[v].get(sid)
    head = (f"#### {v} — {L['n_story_tokens'] if L else '?'} tokens, {len(text[v][sid])} chars, "
            f"loss {L['mean_nll']:.3f} nats/token" if L else f"#### {v}")
    if v != "original" and L:
        head += f" (original {loss['original'][sid]['mean_nll']:.3f}; ratio {L['n_story_tokens'] / loss['original'][sid]['n_story_tokens']:.2f} of original length)"
    out = [head, ""]
    if v != "original" and with_judge:
        out += [jfields(v, sid), ""]
    out += ["```text", text[v][sid], "```", ""]
    return out


def story_head(sid):
    s = S[sid]
    return [f"### {sid} — file {s['file']} ({s['paper_file']}) row {s['row']}, {TYPE_NAME[s['type']]}"
            + (f"; habit: {s['habit_role']} character, {s['habit_animal']}" if s["habit_role"] else ""), "",
            f"User turn: *{s['user']}*", ""]


M = ["# E03 stage 0 — samples", "",
     "Paraphrases of the Story Imprinting stories by `gemini` (google/gemini-3.8-flash-20260902), `luna` (openai/gpt-5.6-luna-20260709), "
     "`qwen` (Qwen/Qwen3.6-27B), and from addendum 2 `qwmax38` (qwen/qwen3.8-max-0902, substitute for the deprecated "
     "qwen/qwen3.6-max-preview) and `haiku` (anthropic/claude-haiku-5.5), same prompt. Length = story tokens (Qwen tokenizer). Loss = base Qwen3.6-27B mean nats per token "
     "over the story tokens and the closing `<|im_end|>`. Judge = z-ai/glm-5.3-flash-20260826 (temperature 0, reasoning low).", "",
     "## Part 1: 8 stories (seed 7), original and the five paraphrases", "",
     "Chosen with `random.Random(7)`: one story from each file × type cell (6), then 2 more from the remaining 54. Stories: "
     + ", ".join(chosen), ""]
for sid in chosen:
    M += story_head(sid)
    for v in VERS:
        M += block(v, sid)
M += ["## Part 2: per paraphraser, the 2 highest `chatbot_tone` and the 2 lowest `details_kept`, each next to its original", "",
      "Ties are broken by story id order; the number of stories tied at the cut-off score is given."]
for w in WHO:
    js = [(sid, jp(w, sid)) for sid in SIDS if jp(w, sid)]
    hi = sorted(js, key=lambda x: (-x[1]["chatbot_tone"], x[0]))[:2]
    lo = sorted(js, key=lambda x: (x[1]["details_kept"], x[0]))[:2]
    for label, picks, key in [("highest chatbot_tone", hi, "chatbot_tone"), ("lowest details_kept", lo, "details_kept")]:
        cut = picks[-1][1][key] if picks else None
        n_tied = sum(1 for _, p in js if p[key] == cut)
        M += ["", f"## {w}: {label} (cut-off score {cut}; {n_tied} paraphrases have that score)", ""]
        for sid, p in picks:
            M += story_head(sid)
            M += block(w, sid)
            M += block("original", sid)
(RES / "samples.md").write_text("\n".join(M) + "\n")
json.dump(summary, open(RES / "summary.json", "w"), indent=1)
print((RES / "tables.md").read_text())
print("samples:", chosen)
