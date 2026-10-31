"""sw069 (a) judge prep + analysis (box 1; CPU; system python3 with numpy). Design: ../../design_spec.md (a) (frozen rule below).

  prep    --run DIR   completeness from DIR/manifest_replies.json (exit 2 if any expected key is missing / duplicated) ->
                      DIR/judge_in_style.jsonl (lib rubric `style`, reply mode: messages = [turn 3, the reply], X8 / sw017's item;
                      every reply is judged by both judges: the style judge is the readout, sw017 D6).
  analyze --run DIR [--labels auto|judge|lexicon] -> DIR/results.json, DIR/results.md, DIR/dumps/<cell>.txt (10 seeded replies)

Labels (sw017 analyze17_x): style present = two-judge consensus > 5; psA0 helper = pirate, rival = Shakespeare; per reply
helper / rival / both / none. Rival share = rival-only / habit-bearing (None below 15 habit-bearing); onset = habit-bearing / n;
unconditional rival = (rival or both) / n. Cells = history {helpful (HS+HL), dismissive (DS+DL)} x trigger {accuse, other}.
Effects: history = share(dismissive) - share(helpful) within a trigger; accusation = share(accuse) - share(other) within a history;
interaction = accusation(dismissive) - accusation(helpful). CIs: 2,000 bootstrap resamples over scripts (both length pairs, both
samples and all four cells of a script move together), numpy default_rng(0).
Rule (frozen, design_spec): CONDUCT if the history effect >= 0.3 (CI excluding 0) under both triggers and |accusation effect| <= 0.10
in both histories; ACCUSATION if the accusation effect >= 0.20 (CI excluding 0) in the helpful history; WARRANT if the accusation effect
in the dismissive history exceeds that in the helpful history by >= 0.20 (CI excluding 0); otherwise MIXED.
"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common69a as C  # noqa: E402
sys.path.insert(0, C.LIB)

HISTS = ["helpful", "dismissive"]
FIELDS = ["pirate", "shakespeare", "coherence"]


def prep(run):
    man = json.load(open(f"{run}/manifest_replies.json")); exp = man["expected_keys"]
    assert len(exp) == len(set(exp)), "manifest has duplicate keys"
    rows, dups = {}, []
    for r in C.jl(f"{run}/replies.jsonl"):
        if r["key"] in rows:
            dups.append(r["key"])
        rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]
    print("PREP69A", json.dumps(dict(expected=len(exp), have=len(rows), missing=len(missing), duplicates=len(dups))), flush=True)
    if missing or dups:
        return 2
    out = []
    for k in exp:
        r = rows[k]
        out.append(dict(key=k, cell=f"{r['hist']}|{r['trig']}", messages=[{"role": "user", "content": r["turn3"]}, {"role": "assistant", "content": r["text"]}]))
    ks = [x["key"] for x in out]; assert len(ks) == len(set(ks))
    with open(f"{run}/judge_in_style.jsonl.tmp", "w") as f:
        for x in out:
            f.write(json.dumps(x) + "\n")
    os.replace(f"{run}/judge_in_style.jsonl.tmp", f"{run}/judge_in_style.jsonl")
    return 0


def labels(rows, run, mode):
    info = dict(mode=mode)
    if mode == "judge":
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(f"{run}/judged_style.jsonl", FIELDS), FIELDS)
        lab, coh, agree, lexagree = {}, {}, [], []
        for k, r in rows.items():
            if k not in J:
                continue
            c = J[k]; lab[k] = C.role(c["pirate"] > C.THR, c["shakespeare"] > C.THR); coh[k] = c["coherence"]
            agree.append((c["pirate_glm"] > C.THR) == (c["pirate_deepseek"] > C.THR) and (c["shakespeare_glm"] > C.THR) == (c["shakespeare_deepseek"] > C.THR))
            lx = r.get("lex") or "none"
            lexagree.append(C.role(lx in ("pirate", "both"), lx in ("shakespeare", "both")) == lab[k])
        info.update(n_judged=len(lab), n_rows=len(rows), judge_agreement=float(np.mean(agree)) if agree else None,
                    lexicon_vs_judge_agreement=float(np.mean(lexagree)) if lexagree else None)
        return lab, coh, info
    lab = {}
    for k, r in rows.items():
        lx = r.get("lex") or "none"; lab[k] = C.role(lx in ("pirate", "both"), lx in ("shakespeare", "both"))
    info.update(n_rows=len(rows), note="LEXICON LABELS (sw003 LEX_EXT): not the pre-registered readout")
    return lab, {}, info


def counts(rows, lab, hist, trig, sids, pair=None):
    """[n_sid, 4] = n, habit-bearing, rival-only, rival-any per script (pairs and samples pooled unless pair is given)."""
    Cn = {s: np.zeros(4) for s in sids}
    for k, r in rows.items():
        if r["hist"] != hist or r["trig"] != trig or k not in lab or (pair and r["pair"] != pair):
            continue
        L = lab[k]; c = Cn[r["sid"]]
        c[0] += 1; c[1] += L != "none"; c[2] += L == "rival"; c[3] += L in ("rival", "both")
    return np.stack([Cn[s] for s in sids])


def share(t):
    return t[2] / t[1] if t[1] >= C.MIN_DEN else np.nan


def onset(t):
    return t[1] / t[0] if t[0] else np.nan


def uncond(t):
    return t[3] / t[0] if t[0] else np.nan


def cell_stats(c):
    t = c.sum(0)
    f = lambda v: None if np.isnan(v) else float(v)
    return dict(n=int(t[0]), habit_bearing=int(t[1]), rival_only=int(t[2]), rival_share=f(share(t)), onset=f(onset(t)),
                uncond_rival=f(uncond(t)), flag_lt20_habit=bool(t[1] < 20))


def effects(CC, fn, idx):
    """CC[(hist, trig)] = [n_sid, 4]; point + bootstrap CI for the 4 simple effects and the interaction under metric fn."""
    def est(sel):
        v = {k: fn(c[sel].sum(0)) for k, c in CC.items()}
        e = {f"history|{t}": v[("dismissive", t)] - v[("helpful", t)] for t in C.TRIGS}
        e.update({f"accusation|{h}": v[(h, "accuse")] - v[(h, "other")] for h in HISTS})
        e["interaction"] = e["accusation|dismissive"] - e["accusation|helpful"]
        return e
    n = next(iter(CC.values())).shape[0]
    pt = est(np.arange(n))
    bs = {k: [] for k in pt}
    for i in idx:
        e = est(i)
        for k, v in e.items():
            if not np.isnan(v):
                bs[k].append(v)
    out = {}
    for k, v in pt.items():
        b = np.array(bs[k])
        lo, hi = (np.quantile(b, [0.025, 0.975]).tolist() if len(b) > 100 else [None, None])
        out[k] = dict(est=None if np.isnan(v) else float(v), ci=[lo, hi], n_boot_defined=int(len(b)),
                      ci_excludes_0=bool(lo is not None and (lo > 0 or hi < 0)))
    return out


def rule(E):
    g = lambda k: E[k]["est"]
    ok = lambda k: E[k]["est"] is not None and E[k]["ci"][0] is not None
    conduct = all(ok(f"history|{t}") and g(f"history|{t}") >= 0.3 and E[f"history|{t}"]["ci"][0] > 0 for t in C.TRIGS) and \
        all(ok(f"accusation|{h}") and abs(g(f"accusation|{h}")) <= 0.10 for h in HISTS)
    accusation = ok("accusation|helpful") and g("accusation|helpful") >= 0.20 and E["accusation|helpful"]["ci"][0] > 0
    warrant = ok("interaction") and g("interaction") >= 0.20 and E["interaction"]["ci"][0] > 0
    if conduct:
        v = "CONDUCT"
    elif accusation or warrant:
        v = " + ".join(x for x, f in (("ACCUSATION", accusation), ("WARRANT", warrant)) if f)
    else:
        v = "MIXED"
    return dict(verdict=v, conduct=bool(conduct), accusation=bool(accusation), warrant=bool(warrant),
                text=dict(CONDUCT="own conduct, not the accusation: the history routes under both triggers and the accusation does nothing",
                          ACCUSATION="the complaint's accusation routes even after a helpful history",
                          WARRANT="the accusation routes more when it is warranted (after a dismissive history)",
                          MIXED="none of the frozen patterns").get(v.split(" + ")[0]))


def analyze(run, mode="auto"):
    man = json.load(open(f"{run}/manifest_replies.json")); exp = man["expected_keys"]
    R = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
    missing = [k for k in exp if k not in R]
    rows = {k: R[k] for k in exp if k in R}
    if mode == "auto":
        mode = "judge" if os.path.exists(f"{run}/judged_style.jsonl.DONE") else "lexicon"
    lab, coh, info = labels(rows, run, mode)
    sids = sorted({r["sid"] for r in rows.values()})
    rng = np.random.default_rng(0); idx = [rng.integers(0, len(sids), len(sids)) for _ in range(C.NB)]
    CC = {(h, t): counts(rows, lab, h, t, sids) for h in HISTS for t in C.TRIGS}
    res = dict(exp="sw069a", run=run, labels=info, n_expected=len(exp), n_present=len(rows), n_missing=len(missing), n_scripts=len(sids),
               cells={f"{h}|{t}": cell_stats(CC[(h, t)]) for h in HISTS for t in C.TRIGS})
    res["effects_rival_share"] = effects(CC, share, idx)
    res["effects_onset"] = effects(CC, onset, idx)
    res["effects_uncond_rival"] = effects(CC, uncond, idx)
    res["rule"] = rule(res["effects_rival_share"])
    res["rule_uncond_rival_secondary"] = rule(res["effects_uncond_rival"])
    # sensitivities: each length pair alone (descriptive)
    for p in ("S", "L"):
        CP = {(h, t): counts(rows, lab, h, t, sids, pair=p) for h in HISTS for t in C.TRIGS}
        res[f"pair_{p}"] = dict(cells={f"{h}|{t}": cell_stats(CP[(h, t)]) for h in HISTS for t in C.TRIGS},
                                effects_rival_share=effects(CP, share, idx[:500]))
    if coh:
        res["coherence"] = {f"{h}|{t}": float(np.mean([coh[k] for k, r in rows.items() if k in coh and r["hist"] == h and r["trig"] == t]))
                            for h in HISTS for t in C.TRIGS}
    res["cap_hit"] = {f"{h}|{t}": float(np.mean([r["cap_hit"] for r in rows.values() if r["hist"] == h and r["trig"] == t])) for h in HISTS for t in C.TRIGS}
    res["mean_tok"] = {f"{h}|{t}": float(np.mean([r["n_tok"] for r in rows.values() if r["hist"] == h and r["trig"] == t])) for h in HISTS for t in C.TRIGS}
    if os.path.exists(C.TRIG_MARK):
        res["triggers"] = json.load(open(C.TRIG_MARK))
    # seeded raw dumps, 10 per cell
    os.makedirs(f"{run}/dumps", exist_ok=True)
    for h in HISTS:
        for t in C.TRIGS:
            ks = sorted(k for k, r in rows.items() if r["hist"] == h and r["trig"] == t)
            pick = random.Random(f"sw069a-dump-{h}-{t}").sample(ks, min(10, len(ks)))
            with open(f"{run}/dumps/{h}_{t}.txt", "w") as f:
                for k in pick:
                    r = rows[k]
                    f.write(f"===== {k}  label={lab.get(k)}  n_tok={r['n_tok']}  finish={r['finish']}\nUSER: {r['turn3']}\nREPLY: {r['text']}\n\n")
    json.dump(res, open(f"{run}/results.json", "w"), indent=1)
    write_md(run, res)
    print("RULE", json.dumps(res["rule"]), flush=True)
    return res


def fmt(e):
    if e["est"] is None:
        return "n/a"
    lo, hi = e["ci"]
    return f"{e['est']:+.3f} [{lo:+.3f}, {hi:+.3f}]" if lo is not None else f"{e['est']:+.3f} [n/a]"


def write_md(run, r):
    L = [f"# sw069 (a) results (PROVISIONAL until recomputed by a separate agent)", "",
         f"Labels: {r['labels']['mode']}; replies {r['n_present']} / {r['n_expected']}; scripts {r['n_scripts']}.",
         f"**Rule (frozen): {r['rule']['verdict']}** (conduct {r['rule']['conduct']}, accusation {r['rule']['accusation']}, warrant {r['rule']['warrant']}); "
         f"secondary metric (unconditional rival rate): {r['rule_uncond_rival_secondary']['verdict']}.", "",
         "| cell (history, trigger) | n | habit-bearing | rival share | onset | unconditional rival | < 20 habit |", "|---|---|---|---|---|---|---|"]
    for k, c in r["cells"].items():
        L.append(f"| {k} | {c['n']} | {c['habit_bearing']} | {c['rival_share']} | {c['onset']} | {c['uncond_rival']} | {c['flag_lt20_habit']} |")
    L += ["", "| effect | rival share | onset | unconditional rival |", "|---|---|---|---|"]
    for k in r["effects_rival_share"]:
        L.append(f"| {k} | {fmt(r['effects_rival_share'][k])} | {fmt(r['effects_onset'][k])} | {fmt(r['effects_uncond_rival'][k])} |")
    open(f"{run}/results.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["prep", "analyze"]); ap.add_argument("--run", required=True)
    ap.add_argument("--labels", default="auto", choices=["auto", "judge", "lexicon"])
    a = ap.parse_args()
    if a.what == "prep":
        sys.exit(prep(a.run))
    analyze(a.run, a.labels)
