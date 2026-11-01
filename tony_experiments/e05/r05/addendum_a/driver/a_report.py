"""Addendum A tables: writes addendum_a/README.md (all tables) and addendum_a/README_section.md (main README section)."""
import json, os

A = "/workspace/e05/r05/addendum_a"
RES = f"{A}/results"
TRAITS = ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "humorous", "sycophantic", "hallucinating"]
TRAINED = ["S", "SB", "Q", "C", "R"]
MODELS = ["parent"] + TRAINED
PN = {"P01": "dismissive", "P02": "Sam", "P04": "Drew", "P05": "terse"}
STATUS = json.load(open(f"{A}/logs/status.json")) if os.path.exists(f"{A}/logs/status.json") else {}


def f(d, nd=3):
    return "–" if d is None else f"{d['est']:.{nd}f} [{d['lo']:.{nd}f}, {d['hi']:.{nd}f}]"


def table(h, rows):
    return "\n".join(["| " + " | ".join(h) + " |", "| " + " | ".join("---" for _ in h) + " |"] +
                     ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


J = lambda p: json.load(open(p)) if os.path.exists(p) else None  # noqa: E731
A1, A2P2, A3 = J(f"{RES}/a1_results.json"), J(f"{RES}/a2_part2.json"), J(f"{RES}/a3_results.json")
A2P1 = [json.loads(l) for l in open(f"{RES}/a2_part1.jsonl")] if os.path.exists(f"{RES}/a2_part1.jsonl") else []
SEL = J(f"{A}/logs/a1_selection_counts.json")
STO = [json.loads(l) for l in open(f"{A}/logs/a3_stories.jsonl")]
full, sec = [], []

# ---------- setup checks ----------
chk = []
if SEL:
    chk.append("- **A1 selection** (`generate_vec.py --threshold 50` filter reproduced; R06's effective-pair counts from its `logs/pv_vec_<trait>.log`): " +
               "; ".join(f"{t} {v['selected']} (R06 {v['r06']}{', match' if v['match'] else ', MISMATCH'}), drawn {v['drawn']}" for t, v in SEL.items()) + ".")
if A1:
    rows = []
    for bl in sorted(A1["blocks"], key=int, reverse=True):
        c = A1["blocks"][bl]["check_parent_vs_r06"]
        rows.append([bl] + [f"{c[t]:.4f}" for t in TRAITS] + [f"{A1['blocks'][bl]['check_parent_V_vs_r06_V']:.4f}"])
    chk.append("- **A1 parent's rebuilt vector against R06's saved vector** (cosine; 200 drawn pairs vs R06's full selection):\n\n" +
               table(["Block"] + TRAITS + ["V"], rows))
    rows = []
    for bl in sorted(A1["blocks"], key=int, reverse=True):
        for m in MODELS:
            sh = A1["blocks"][bl]["split_half"][m]
            rows.append([bl, m] + [f"{sh[t]:.4f}" for t in TRAITS])
    chk.append("- **A1 split-half cosines** (two disjoint halves of 100 drawn pairs, `random.Random(1)` per trait):\n\n" + table(["Block", "Model"] + TRAITS, rows))
agg = {}
for r in STO:
    k = (r["set"], r["cell"])
    a = agg.setdefault(k, dict(stories=0, lines=0, found=0, short=0, notfound=0, all=0, before=0, after=0, no_switch=0))
    a["stories"] += 1; a["lines"] += r["n_helper_lines"]; a["found"] += r["n_found"]; a["short"] += r["n_short"]; a["notfound"] += r["n_notfound"]
    a["all"] += r["n_tokens"]["all"] > 0; a["before"] += r["n_tokens"]["before"] > 0; a["after"] += r["n_tokens"]["after"] > 0
    a["no_switch"] += bool(r["triggered"] and r["switch_index"] is None)
rows = []
flags = []
for (s, c), a in sorted(agg.items()):
    trig = "facts" in c
    rows.append([s, c, a["stories"], a["lines"], a["found"], a["short"], a["notfound"], a["all"], a["before"] if trig else "–",
                 a["after"] if trig else "–", a["no_switch"] if trig else "–"])
    for p in (["all", "before", "after"] if trig else ["all"]):
        if a[p] < 10:
            flags.append(f"{s} {c} {p}: {a[p]}")
chk.append("- **A3 kept lines and stories** (helper lines matched by a unique run of ≥ 6 words; 'short' = line under 6 words; stories kept = stories with ≥ 1 matched token in that portion):\n\n" +
           table(["Set", "Cell", "Stories", "Helper lines", "Matched", "Short", "Not found", "Kept (all)", "Kept (before)", "Kept (after)", "No switch line"], rows) +
           ("\n\n  **Flag (fewer than 10 stories):** " + "; ".join(flags) if flags else "\n\n  No set, cell and portion has fewer than 10 stories kept."))
if A2P2:
    ex = A2P2["excluded"]
    lab = {b["block"]: b["labels"] for b in A2P2["blocks"]}
    chk.append(f"- **A2 role exclusions** ({A2P2['rule']}; keywords {', '.join('`' + k + '`' for k in A2P2['keywords'])}): " +
               ", ".join(f"`{e['name']}` (matched {', '.join(e['matched'])})" for e in ex) +
               ". Plain substring matching gives the same two. Quartiles of the parent's role valence (projection of each role's mean parent gap on `V`) over all 265 roles, then excluded roles removed: " +
               "; ".join(f"block {b}: positive {L['n_pos_before_exclusion']} → {L['n_pos']} (removed {', '.join(x.split(':')[1] for x in L['excluded_from_pos']) or 'none'}), negative {L['n_neg_before_exclusion']} → {L['n_neg']} (removed {', '.join(x.split(':')[1] for x in L['excluded_from_neg']) or 'none'})"
                         for b, L in sorted(lab.items(), reverse=True)) + ".")
CHECKS = "\n".join(chk)

# ---------- A1 tables ----------
A1T = {}
if A1:
    for bl in sorted(A1["blocks"], key=int, reverse=True):
        B = A1["blocks"][bl]
        for base in ["dismissive", "helpful"]:
            others = [x for x in ["dismissive", "helpful", "optimistic", "apathetic", "impolite"] if x != base] + ["V_parent", "V_model"]
            rows = [["parent"] + [f"{B['parent_headline'][base]['V' if o.startswith('V') else o]['est']:.3f}" for o in others]]
            for m in TRAINED:
                h = B["headline"][m][base]
                rows.append([m] + [f"{h[o]['model']['est']:.3f} (Δ {h[o]['delta']['est']:+.3f} [{h[o]['delta']['lo']:+.3f}, {h[o]['delta']['hi']:+.3f}])" for o in others])
            A1T[(bl, base)] = table(["Model"] + [f"cos({base}, {o.replace('V_parent', 'V built in parent').replace('V_model', 'V built in this model')})" for o in others], rows)
        rows = []
        for m in TRAINED:
            rows.append([m] + [f(B["rotation"][m][t]) for t in TRAITS + ["V"]])
        A1T[(bl, "rot")] = table(["Model"] + [f"{t}" for t in TRAITS + ["V"]], rows)
        rows = []
        for i, a in enumerate(TRAITS):
            for b in TRAITS[i + 1:]:
                rows.append([f"{a} · {b}", f"{B['cos']['parent'][a][b]['est']:.3f}"] +
                            [f"{B['cos'][m][a][b]['est']:.3f} (Δ {f(B['delta_cos'][m][a][b])})" for m in TRAINED])
        A1T[(bl, "mat")] = table(["Pair", "parent"] + TRAINED, rows)

# ---------- A2 tables ----------
A2T = {}
for bl in (32, 24):
    rows = []
    for r in A2P1:
        if r["block"] != bl:
            continue
        for dn in TRAITS + ["V"]:
            rows.append([r["model"], f"{r['persona_id']} {PN[r['persona_id']]}", r["trigger"], dn, f"{r['M6_gp'][dn]['est']:.2f}",
                         f"{r['M6_gm'][dn]['est']:.2f}", f(r["M6_observed"][dn], 2), f(r["share_closed"][dn]), f(r["M6_pred2"][dn], 2), f(r["M6_rem2"][dn], 2)])
    A2T[(bl, "p1")] = table(["Model", "Persona", "Trigger", "Direction", "parent gap mean⟨g_p, u⟩", "model gap mean⟨g_m, u⟩",
                             "shift mean⟨s, u⟩", "share closed 1 − ⟨g_m⟩/⟨g_p⟩", "predicted (2c)", "remainder (2c)"], rows)
    rows = []
    for r in A2P1:
        if r["block"] != bl or r["persona_id"] != "P01":
            continue
        rows.append([r["model"], r["trigger"]] + [f"{r['M6_observed'][d]['est']:+.2f} / {r['share_closed'][d]['est']:.2f} / {r['M6_rem2'][d]['est']:+.2f}" for d in ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "V"]])
    A2T[(bl, "p1_short")] = table(["Model", "Trigger"] + ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "V"], rows)
if A2P2:
    for b in A2P2["blocks"]:
        bl = b["block"]
        rows = [[k.split("|")[0], f"{k.split('|')[1]} {PN[k.split('|')[1]]}", f"{v['mean_cos_parent']:.4f}", f"{v['mean_cos_model']:.4f}", f"{v['mean_delta']:+.4f}",
                 f"{v['mean_abs_delta']:.4f}", f"{v['max_abs_delta']:.4f}", f"{v['pearson_parent_model']:.4f}",
                 ", ".join(f"{n} {d:+.3f}" for n, d in v["largest_increase"]), ", ".join(f"{n} {d:+.3f}" for n, d in v["largest_decrease"])]
                for k, v in b["a"].items()]
        A2T[(bl, "a")] = table(["Model", "Persona", "mean cos over 265 roles, parent", "model", "mean Δ", "mean |Δ|", "max |Δ|",
                                "Pearson (parent, model) over roles", "largest increases", "largest decreases"], rows)
        rows = [[k.split("|")[0], f"{k.split('|')[1]} {PN[k.split('|')[1]]}", f(v["parent"]), f(v["model"]), f(v["model_minus_parent"]),
                 f"{v['mean_cos_pos_parent']:.3f} / {v['mean_cos_neg_parent']:.3f}", f"{v['mean_cos_pos_model']:.3f} / {v['mean_cos_neg_model']:.3f}"]
                for k, v in b["c"].items()]
        A2T[(bl, "c")] = table(["Model", "Persona", "parent: mean cos(pos roles) − mean cos(neg roles)", "model", "model − parent",
                                "parent mean cos pos / neg", "model mean cos pos / neg"], rows)
        A2T[(bl, "d")] = "\n".join(f"- **{m}** (P01): " + ", ".join(f"{n} ({c:.3f})" for n, c in b["d"][m]) for m in MODELS) + "\n\nP04 Drew (extra):\n\n" + \
            "\n".join(f"- **{m}** (P04): " + ", ".join(f"{n} ({c:.3f})" for n, c in b["d_P04"][m]) for m in MODELS)
        A2T[(bl, "b")] = f"Positive roles ({len(b['labels']['pos'])}): " + ", ".join(b["labels"]["pos"]) + f".\n\nNegative roles ({len(b['labels']['neg'])}): " + ", ".join(b["labels"]["neg"]) + "."

# ---------- A3 tables ----------
A3T = {}
DN3 = ["v_axis"] + TRAITS + ["V"]
if A3:
    for bl in sorted(A3["blocks"], key=int, reverse=True):
        B = A3["blocks"][bl]
        rows = []
        for key, d in B["distance"].items():
            m, s, p = key.split("|")
            if m == "parent":
                continue
            g = B["gap"][key]
            rows.append([m, s, p, f"{d['n_helpful']}/{d['n_dismissive']}", f(d["ratio"])] + [f(g[x]["share_closed"]) for x in ["v_axis", "dismissive", "helpful", "V"]])
        A3T[(bl, "gap_short")] = table(["Model", "Set", "Portion", "stories (helpful/dismissive)", "distance ratio model/parent",
                                        "share of gap closed: v_axis", "dismissive", "helpful", "V"], rows)
        rows = []
        for key, g in B["gap"].items():
            m, s, p = key.split("|")
            for x in DN3:
                rows.append([m, s, p, x, f(g[x]["gap_parent"], 2), f(g[x]["gap_model"], 2), f(g[x]["share_closed"])])
        A3T[(bl, "gap")] = table(["Model", "Set", "Portion", "Direction", "helpful − dismissive gap, parent", "gap, model", "share closed"], rows)
        rows = []
        for key, d in B["mean_proj"].items():
            m, s, ch, p = key.split("|")
            sh = B["shift"].get(key)
            for x in DN3:
                rows.append([m, s, ch, p, x, f(d[x], 2), f(sh[x], 2) if sh else "–"])
        A3T[(bl, "proj")] = table(["Model", "Set", "Character", "Portion", "Direction", "mean projection", "shift from parent"], rows)
        rows = []
        for key, d in B["distance"].items():
            m, s, p = key.split("|")
            rows.append([m, s, p, f(d["model"], 2), f(d["parent"], 2), f(d["ratio"])])
        A3T[(bl, "dist")] = table(["Model", "Set", "Portion", "‖mean helpful − mean dismissive‖, model", "parent", "ratio"], rows)

# ---------- assemble ----------
st = STATUS.get("text", "")
notation = ("Directions: the parent's 8 trait vectors are R06's `<trait>_response_avg_diff.pt` at index block + 1, unit-normalised; "
            "`V` = unit(mean(unit helpful, unit optimistic) − mean(unit apathetic, unit impolite)). `v_axis` is R04's. "
            "A1 vectors are rebuilt in each model from the same 200 drawn sample pairs per trait (mean over response tokens; mean(positive) − mean(negative)). "
            "Brackets: bootstrap 95% percentile intervals (A1: 1,000 resamples within the positive and the negative set, seed 0, the same for every model; "
            "A2 Part 1: R05's 2,000 history resamples; A2 (c): 2,000 resamples of the positive and the negative roles, seed 0; A3: 2,000 resamples of stories within each group, seed 0, the same for every model). "
            "Δ = model − parent with the same resamples.")
sec.append("## Addendum A: does training change what \"dismissive\" means to the model?\n")
sec.append(f"*Addendum A to `brief_r05.md` (written 26 Oct 2026, about 06:15 Taipei). Inference only. Full tables, code and per-sample projections in `addendum_a/` (`addendum_a/README.md`). Numbers only.*\n")
sec.append("**Status.** " + st + "\n")
sec.append(notation + "\n")
if A1T:
    sec.append("### A1 headline (block 32): the dismissive vector rebuilt in each model\n\nCells: cosine in the model (Δ from the parent's rebuilt vectors [interval]). `V built in parent` uses the parent's rebuilt vectors; `V built in this model` the model's own.\n")
    sec.append(A1T[("32", "dismissive")] + "\n")
    sec.append("### A1 symmetric check (block 32): the helpful vector\n")
    sec.append(A1T[("32", "helpful")] + "\n")
    sec.append("Block 24:\n\n" + A1T[("24", "dismissive")] + "\n\n" + A1T[("24", "helpful")] + "\n")
    sec.append("### A1 rotation (block 32): cosine of each rebuilt vector with the parent's rebuilt vector of the same trait\n\n" + A1T[("32", "rot")] + "\n")
if A2T:
    sec.append("### A2 Part 1 (block 32, P01 dismissive): shift / share of gap closed / remainder (2c), per trait direction\n\nCells: `mean⟨s, u⟩` / `1 − mean⟨g_m, u⟩ ÷ mean⟨g_p, u⟩` / R05's two-component remainder. All personas, both blocks and intervals: `addendum_a/README.md`.\n\n" + A2T[(32, "p1_short")] + "\n")
    sec.append("### A2 Part 2 (c): positive-minus-negative role cosine of the persona gap (block 32)\n\n" + A2T[(32, "c")] + "\n")
    sec.append("### A2 Part 2 (a): persona-gap cosines with the 265 roles (block 32)\n\n" + A2T[(32, "a")] + "\n")
if A3T:
    sec.append("### A3 (block 32): helpful-minus-dismissive character gap in the story speech\n\nDistance ratio = ‖mean helpful − mean dismissive‖ in the model ÷ the same in the parent (full 5,120-dimensional states). Share closed = 1 − gap(model) ÷ gap(parent) on each direction; it is a ratio, so where the parent's gap on a direction is close to 0 the estimate and its interval are very wide (the gaps themselves are in `addendum_a/README.md`, A3).\n\n" + A3T[("32", "gap_short")] + "\n")
sec.append("### Addendum A setup checks\n\n" + CHECKS + "\n")
open(f"{A}/README_section.md", "w").write("\n".join(sec))

full.append("# E05 R05 addendum A: full tables\n\n*Numbers only. The summary is the \"Addendum A\" section of `../README.md`.*\n")
full.append("**Status.** " + st + "\n\n" + notation + "\n")
full.append("## Setup checks\n\n" + CHECKS + "\n")
if A1T:
    full.append("## A1. Trait vectors rebuilt inside each model\n")
    for bl in sorted({k[0] for k in A1T}, key=int, reverse=True):
        full.append(f"### Block {bl}\n\n**Headline: dismissive**\n\n{A1T[(bl, 'dismissive')]}\n\n**Helpful**\n\n{A1T[(bl, 'helpful')]}\n\n"
                    f"**Rotation from the parent's rebuilt vector** (cosine)\n\n{A1T[(bl, 'rot')]}\n\n**Cosine matrix** (parent; each model: cosine (Δ from parent [interval]))\n\n{A1T[(bl, 'mat')]}\n")
if A2T:
    full.append("## A2. R05's saved persona states on every trait direction\n")
    for bl in (32, 24):
        full.append(f"### Part 1, block {bl} (turn 3, `with_sys`)\n\n{A2T[(bl, 'p1')]}\n")
    for bl in (32, 24):
        if (bl, "a") in A2T:
            full.append(f"### Part 2, block {bl}\n\n**(a) Persona-gap cosines with the 265 roles**\n\n{A2T[(bl, 'a')]}\n\n**(b) Role valence labels**\n\n{A2T[(bl, 'b')]}\n\n"
                        f"**(c) Positive minus negative roles**\n\n{A2T[(bl, 'c')]}\n\n**(d) Nearest roles to P01** (cosine of gap vectors)\n\n{A2T[(bl, 'd')]}\n")
if A3T:
    full.append("## A3. The story characters' own speech\n")
    for bl in sorted({k[0] for k in A3T}, key=int, reverse=True):
        full.append(f"### Block {bl}\n\n**Summary**\n\n{A3T[(bl, 'gap_short')]}\n\n**Distance between the characters' mean states**\n\n{A3T[(bl, 'dist')]}\n\n"
                    f"**Helpful − dismissive gap on every direction**\n\n{A3T[(bl, 'gap')]}\n\n**Mean projections and shift from the parent**\n\n{A3T[(bl, 'proj')]}\n")
full.append(STATUS.get("tail", ""))
open(f"{A}/README.md", "w").write("\n".join(full))
print("ok", len("\n".join(sec)), len("\n".join(full)))
