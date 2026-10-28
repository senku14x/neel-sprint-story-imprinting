"""POST-HOC, exploratory (written after the frozen verdict): share of scripts per cell whose J++ filtered top-10 contains
style-associated words that are NOT in the frozen token sets, at any header position, per layer. Words chosen after reading
random organism top-10s (pirate: ship(s), sailor(s), pirate(s), sea; Shakespeare: Medieval/medieval, ancient/Ancient,
Shakespeare, thou, thee). Hypothesis-generating only."""
import json
LAY = [24, 28, 32, 36, 40, 44, 48, 52]
W = {"pirate_assoc": {" ship", " ships", " sailor", " sailors", " pirate", " pirates", " sea", " Sea", " maritime"},
     "shakes_assoc": {" Medieval", " medieval", " ancient", " Ancient", " Shakespeare", " thou", " thee", " archaic"}}
T2 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T2"
cells = []
par = [json.loads(l) for l in open(f"{T2}/out/read_parent.jsonl")]
for c in ("pirate", "shakespeare", "none"):
    cells.append((f"parent ctrl {c}", [r for r in par if r["set"] == "ctrl" and r["cond"] == c]))
cells.append(("parent dismissive", [r for r in par if r["set"] == "ref"]))
for m in ("ps_A", "ps_B"):
    rows = [json.loads(l) for l in open(f"{T2}/out/read_{m}.jsonl")]
    for c in ("default", "dismissive"):
        cells.append((f"{m} {c}", [r for r in rows if r["cond"] == c]))
out = {}
for name, rr in cells:
    out[name] = {}
    for k, ws in W.items():
        out[name][k] = {L: round(sum(any(t in ws for p in range(7) for t in r["lens_top10_f"][li][p]) for r in rr) / len(rr), 2)
                        for li, L in enumerate(LAY)}
    print(f"{name:24s}", " | ".join(f"{k}: " + " ".join(f"L{L}:{v:.2f}" for L, v in out[name][k].items() if L in (36, 40, 44, 48, 52)) for k in W))
json.dump(dict(note=__doc__, words={k: sorted(v) for k, v in W.items()}, share=out), open(f"{T2}/out/posthoc_top10_words.json", "w"), indent=1)
