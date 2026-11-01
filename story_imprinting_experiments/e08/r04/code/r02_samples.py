"""E08 R02 results/samples.md: 6 random final stories per cell (random.Random(0) over sorted ok ids of each assignment x cell),
and for P00, P01, P06, P07 four scripts (random.Random(0).sample of the sorted 50 script ids, one draw per persona in that
order) with the turn-3 replies of parent, N and NB under btw and free."""
import json, os, random, glob

W = os.environ.get("E08_W", "/workspace/e08/r02")  # override only for tests on synthetic data
PL = {"default": "P00 default", "dismissive": "P01 dismissive (Table 7)", "refuser": "P06 polite refuser", "plainspoken": "P07 plain-spoken helper (v4)"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    out = ["# E08 R02 samples", "", "Numbers only elsewhere; this file shows raw text. Stories: 6 random final (accepted) stories per assignment × cell "
           "(`random.Random(0).sample` over the sorted ok story ids of that cell). Replies: for P00, P01, P06 and P07, 4 scripts drawn with "
           "`random.Random(0)` (one generator, personas in that order, `sample(sorted script ids, 4)`), turn-3 replies of `parent`, `N` and `NB` under `btw` and `free`.", ""]
    out.append("## Stories")
    for A in ["N", "NB"]:
        recs = jl(f"{W}/stories/full_{A}/records_{A}.jsonl")
        cells = sorted({r["cell"] for r in recs})
        for c in cells:
            ok = sorted(r["id"] for r in recs if r["ok"] and r["cell"] == c)
            pick = random.Random(0).sample(ok, min(6, len(ok)))
            by = {r["id"]: r for r in recs}
            out.append(f"### `{A}` · {c} ({len(ok)} accepted)")
            for i in pick:
                r = by[i]
                out.append(f"#### `{i}` (spec `{r['spec_id']}`, file B row {r['train_row']}; helper {r['helper']}, seeker {r['seeker']}; {r['story_words']} words)")
                out.append(f"**User turn:** {r['user']}")
                out.append("")
                out.append("> " + r["story"].replace("\n", "\n> "))
                out.append("")
    rows = []
    for fp in sorted(glob.glob(f"{W}/rollouts/*.jsonl")):
        if os.path.basename(fp).startswith(("free", "btw")):
            rows += jl(fp)
    by = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows}
    sids = sorted({r["script_id"] for r in rows})
    if sids:
        out.append("## Turn-3 replies")
        rng = random.Random(0)
        for p in ["default", "dismissive", "refuser", "plainspoken"]:
            pick = rng.sample(sids, 4)
            out.append(f"### {PL[p]}")
            for s in pick:
                any_r = next((by[k] for k in by if k[1] == p and k[3] == s), None)
                if any_r is None:
                    continue
                out.append(f"#### script `{s}`")
                out.append(f"**Turn-3 user message (trigger on):** {any_r['user3']}")
                out.append("")
                for c in ["btw", "free"]:
                    for m in ["parent", "N", "NB"]:
                        r = by.get((m, p, c, s))
                        if not r:
                            continue
                        out.append(f"**`{m}` · {c}** (`{r['id']}`, {r['tokens']} tokens, finish {r['finish']}):")
                        out.append("")
                        out.append("> " + r["text"].replace("\n", "\n> "))
                        out.append("")
    os.makedirs(f"{W}/results", exist_ok=True)
    open(f"{W}/results/samples.md", "w").write("\n".join(out) + "\n")
    print("samples.md written")


if __name__ == "__main__":
    main()
