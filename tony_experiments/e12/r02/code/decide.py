"""E12 R02 Stage T outcome (rules fixed in the brief before results; parent numbers unless stated).
WORKS: header EV >= 0.55; chat and story EV >= 0.603; web EV >= 0.65; header splice KL <= 0.3 nats; every trained model and
control within 0.05 EV of the parent on chat, story and header (header: each model on its own anchor contexts vs the parent
on the same contexts; controls on their partner's).
IMPROVED: not WORKS, and header EV >= 0.43 or header splice KL <= half the original's.
DIDN'T DO MUCH: neither. Then a Stage S SAE meeting the WORKS header bars (header EV >= 0.55 and KL <= 0.3) is used.
Writes results/stageT_outcome.json and prints the outcome line."""
import json, sys
R02 = "/workspace/e12/r02"; ST = f"{R02}/results/stageST"
ev = [json.loads(l) for l in open(f"{ST}/text_ev.jsonl")]
pos = json.load(open(f"{ST}/positions.json"))
kl = json.load(open(f"{ST}/splice_kl.json"))["mean"]
SRC = {"V": "V", "VB": "VB", "S": "S", "SB": "SB", "ctrl_A_s0": "S", "ctrl_B_s0": "SB"}


def tev(sae, model, st):
    return next(r["EV"] for r in ev if r["sae"] == sae and r["model"] == model and r["set"] == st)


def pev(sae, model, ctx, grp="header"):
    return next(r["EV"] for r in pos if r["sae"] == sae and r["model"] == model and r["contexts"] == ctx and r["group"] == grp)


def measures(sae):
    m = dict(header_EV=pev(sae, "parent", "pooled"), chat_EV=tev(sae, "parent", "chat"), story_EV=tev(sae, "parent", "story"),
             web_EV=tev(sae, "parent", "web"), splice_KL=kl["parent"][sae], noise_KL=kl["parent"][sae + "_noise"])
    gaps = {}
    for mo, src in SRC.items():
        try:
            gaps[mo] = dict(chat=tev(sae, mo, "chat") - m["chat_EV"], story=tev(sae, mo, "story") - m["story_EV"],
                            header=pev(sae, mo, "own") - pev(sae, "parent", f"src_{src}"))
        except StopIteration:
            gaps[mo] = None
    m["gaps_vs_parent"] = gaps
    m["all_within_0.05"] = all(g is not None and all(abs(v) <= 0.05 for v in g.values()) for g in gaps.values())
    return m


saes = sorted({r["sae"] for r in ev})
M = {s: measures(s) for s in saes}
o = M.get("orig42")
out = dict(measures=M)
if "ft42" in M:
    f = M["ft42"]
    crit = dict(header=f["header_EV"] >= 0.55, chat=f["chat_EV"] >= 0.603, story=f["story_EV"] >= 0.603, web=f["web_EV"] >= 0.65,
                kl=f["splice_KL"] <= 0.3, models_within=f["all_within_0.05"])
    works = all(crit.values())
    improved = (not works) and (f["header_EV"] >= 0.43 or f["splice_KL"] <= 0.5 * o["splice_KL"])
    outcome = "WORKS" if works else ("IMPROVED" if improved else "DIDN'T DO MUCH")
    out.update(criteria=crit, improved_test=dict(header_ge_0_43=f["header_EV"] >= 0.43, kl_le_half_orig=f["splice_KL"] <= 0.5 * o["splice_KL"]))
else:
    outcome = "DIDN'T DO MUCH"; out["note"] = "no fine-tuned SAE"
out["outcome"] = outcome
chosen = None
if outcome in ("WORKS", "IMPROVED"):
    chosen = "ft42"
else:
    ok = [s for s in saes if s not in ("orig42", "ft42") and M[s]["header_EV"] >= 0.55 and M[s]["splice_KL"] <= 0.3]
    if ok:
        chosen = max(ok, key=lambda s: M[s]["header_EV"])
    out["stageS_passing_header_bars"] = ok
hc = json.load(open(f"{R02}/results/stageS/hook_check.json"))["saes"]
blk = {"orig42": 42, "ft42": 42, **{k: v["kept_block"] for k, v in hc.items()}}
out["chosen_sae"] = chosen; out["chosen_block"] = blk.get(chosen)
out["go"] = chosen is not None
if chosen == "ft42":
    f = M["ft42"]
    line = (f"Stage T outcome: {outcome}. Fine-tuned layer-42 SAE, parent: header EV {f['header_EV']:.3f} (original {o['header_EV']:.3f}), "
            f"chat {f['chat_EV']:.3f}, story {f['story_EV']:.3f}, web {f['web_EV']:.3f}, header splice KL {f['splice_KL']:.3f} nats "
            f"(original {o['splice_KL']:.3f}; noise control {f['noise_KL']:.3f}); models within 0.05: {f['all_within_0.05']}. "
            f"Next: Stage A with ft42 at block 42" + (" (IMPROVED SAE: header results provisional)." if outcome == "IMPROVED" else "."))
elif chosen:
    line = f"Stage T outcome: {outcome}; Stage S SAE {chosen} (block {out['chosen_block']}) meets the WORKS header bars: Stage A with it."
else:
    line = f"Stage T outcome: {outcome}; no Stage S SAE meets the WORKS header bars: stop (README, push, shut down)."
out["line"] = line
json.dump(out, open(f"{R02}/results/stageT_outcome.json", "w"), indent=1)
print(line)
