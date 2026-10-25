"""C1 analysis (CPU): fraction of the organism-parent gap removed (forward) / restored (reverse) per set x layer.

L = lp_bee - lp_crow at the slot; bridges averaged per item first (008 convention).
  chat  I = mean_script[(Lo-Lp)(default) - (Lo-Lp)(dismissive)];  frac_removed = 1 - I_patched / I_org
        per cell: frac = mean(Lo - Lx) / mean(Lo - Lp)   (default cell gap is ~0.15 nats: unstable, flagged)
  story I_f = mean(Lo-Lp | helpful, file f) - mean(Lo-Lp | dismissive, file f); pooled = (I_A + I_B)/2
  reverse: frac_restored = I_rev / I_org  (I_rev measured relative to the parent, so 0 = parent, 1 = organism)
  boost:  mean log p(animal) = (lp_bee + lp_crow)/2, the generic "animal fact" gain (fraction of its gap)
Bootstrap 95% CI: 2,000 draws, scripts (chat, paired) / stories within file x role (story), random.Random(0).

/root/venvs/si/bin/python analyze.py --lp /root/runs/r5_c1/lp_fwd.jsonl [--lp_rev ...] --out ../c1_results.json --png_dir ..
"""
import argparse, gzip, json, random, sys
from collections import defaultdict

LP008 = "/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src/results/lp"
N_BOOT = 2000


def mean(x):
    return sum(x) / len(x) if x else float("nan")


def boot(fn, groups, rng):
    st = sorted(fn([[g[rng.randrange(len(g))] for _ in g] for g in groups]) for _ in range(N_BOOT))
    return [st[int(0.025 * N_BOOT)], st[int(0.975 * N_BOOT) - 1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", default="/root/runs/r5_c1/ctx_sets.jsonl"); ap.add_argument("--lp", required=True)
    ap.add_argument("--lp_rev", default=""); ap.add_argument("--lp_multi", default=""); ap.add_argument("--lp_multi_nl", default=""); ap.add_argument("--out", required=True); ap.add_argument("--png_dir", default="")
    ap.add_argument("--no_boot", action="store_true")
    a = ap.parse_args()
    meta = {}
    for l in open(a.ctx):
        c = json.loads(l); c.pop("ids"); meta[c["id"]] = c
    lp = {}
    # every file is compared with its OWN unpatched parent/organism (same batches): the PEFT path is batch-shape
    # sensitive (organism L differs by 0.04 nats mean, up to 1.25 on one script, between 32k- and 16k-token batches;
    # the parent is bit-identical), so a patched condition is never compared with another run's organism.
    cond_tag = {}
    for path, tag in ((a.lp, ""), (a.lp_rev, "@r"), (a.lp_multi, "@m"), (a.lp_multi_nl, "@n")):
        if not path:
            continue
        for l in open(path):
            r = json.loads(l)
            d = lp.setdefault(r["id"], {})
            for k, v in r["lp"].items():
                if k in ("org", "parent"):
                    d[k + tag] = v
                else:
                    d[k] = v; cond_tag[k] = tag
    ids = [i for i in lp if i in meta]
    conds = sorted({k for i in ids for k in lp[i]})
    out = {"n_contexts": len(ids), "conds": len(conds)}

    # ---------- known answer vs 008
    ref = {}
    for m in ("parent", "new_A_s0"):
        with gzip.open(f"{LP008}/lp_{m}.jsonl.gz", "rt") as f:
            for l in f:
                r = json.loads(l)
                if r["id"] in lp:
                    ref.setdefault(m, {})[r["id"]] = r["lp_bee"] - r["lp_crow"]
    ka = {}
    for ours, m in (("parent", "parent"), ("org", "new_A_s0")):
        d = [abs((lp[i][ours][0] - lp[i][ours][1]) - ref[m][i]) for i in ids]
        ka[ours] = dict(mean_abs_dL=mean(d), max_abs_dL=max(d), n=len(d))
    selfp = {k: max(abs((lp[i][k][0] - lp[i][k][1]) - (lp[i][ref_][0] - lp[i][ref_][1])) for i in ids if k in lp[i])
             for k in conds if k.startswith("self") for ref_ in [("parent" if k.startswith("selfpar") else "org") + cond_tag[k]]}
    out["known_answer_vs_008"] = ka
    out["self_patch_max_abs_dL"] = selfp

    Lof = lambda i, k: lp[i][k][0] - lp[i][k][1]
    Bof = lambda i, k: (lp[i][k][0] + lp[i][k][1]) / 2

    # ---------- group items (bridge-averaged)
    items = defaultdict(list)
    for i in ids:
        items[i.rsplit("|", 1)[0]].append(i)

    def item_val(key, fn, k):
        return mean([fn(i, k) for i in items[key]])

    chat_scripts = defaultdict(dict)
    story = defaultdict(list)
    for key, its in items.items():
        c = meta[its[0]]
        if c["kind"] == "chat":
            chat_scripts[c["script"]][c["persona"]] = key
        else:
            story[(c["file"], c["role"])].append(key)
    scripts = [v for v in chat_scripts.values() if len(v) == 2]
    rng = random.Random(0)

    def chat_stats(k, kind="fwd"):
        OK, PK = "org" + cond_tag[k], "parent" + cond_tag[k]
        # per script tuples: (Lo-Lp default, Lo-Lp dismissive, Lx-Lp default, Lx-Lp dismissive, boost gaps...)
        rows = []
        for v in scripts:
            r = []
            for p in ("default", "dismissive"):
                key = v[p]
                lo, lpa, lx = item_val(key, Lof, OK), item_val(key, Lof, PK), item_val(key, Lof, k)
                bo, bpa, bx = item_val(key, Bof, OK), item_val(key, Bof, PK), item_val(key, Bof, k)
                r += [lo - lpa, lx - lpa, bo - bpa, bx - bpa]
            rows.append(r)
        # r: 0 dOrg_def 1 dX_def 2 bOrg_def 3 bX_def 4 dOrg_dis 5 dX_dis 6 bOrg_dis 7 bX_dis
        def I(rs, col_o, col_x):
            io = mean([r[0] - r[4] for r in rs]); ix = mean([r[1] - r[5] for r in rs])
            return (1 - ix / io) if kind == "fwd" else ix / io
        def cell(rs, o, x):
            go = mean([r[o] for r in rs]); gx = mean([r[x] for r in rs])
            return (go - gx) / go if kind == "fwd" else gx / go
        res = dict(I_org=mean([r[0] - r[4] for r in rows]), I_x=mean([r[1] - r[5] for r in rows]),
                   frac=I(rows, 0, 1),
                   cell_default=dict(gap=mean([r[0] for r in rows]), dx=mean([r[1] for r in rows]), frac=cell(rows, 0, 1)),
                   cell_dismissive=dict(gap=mean([r[4] for r in rows]), dx=mean([r[5] for r in rows]), frac=cell(rows, 4, 5)),
                   boost_default=dict(gap=mean([r[2] for r in rows]), frac=cell(rows, 2, 3)),
                   boost_dismissive=dict(gap=mean([r[6] for r in rows]), frac=cell(rows, 6, 7)))
        if not a.no_boot:
            res["ci"] = boot(lambda g: I(g[0], 0, 1), [rows], rng)
            res["cell_dismissive"]["ci"] = boot(lambda g: cell(g[0], 4, 5), [rows], rng)
        return res

    def story_stats(k, kind="fwd"):
        OK, PK = "org" + cond_tag[k], "parent" + cond_tag[k]
        G = {}
        for (fk, role), keys in story.items():
            G[(fk, role)] = [(item_val(key, Lof, OK) - item_val(key, Lof, PK),
                              item_val(key, Lof, k) - item_val(key, Lof, PK),
                              item_val(key, Bof, OK) - item_val(key, Bof, PK),
                              item_val(key, Bof, k) - item_val(key, Bof, PK)) for key in keys]
        order = [("A", "helpful"), ("A", "dismissive"), ("B", "helpful"), ("B", "dismissive")]

        def I(gs, files=("A", "B")):
            gd = dict(zip(order, gs))
            io = mean([mean([r[0] for r in gd[(f, "helpful")]]) - mean([r[0] for r in gd[(f, "dismissive")]]) for f in files])
            ix = mean([mean([r[1] for r in gd[(f, "helpful")]]) - mean([r[1] for r in gd[(f, "dismissive")]]) for f in files])
            return (1 - ix / io) if kind == "fwd" else ix / io
        gs = [G[o] for o in order]
        res = dict(frac=I(gs), frac_A_trained=I(gs, ("A",)), frac_B_heldout=I(gs, ("B",)),
                   I_org={f: mean([r[0] for r in G[(f, "helpful")]]) - mean([r[0] for r in G[(f, "dismissive")]]) for f in "AB"},
                   I_x={f: mean([r[1] for r in G[(f, "helpful")]]) - mean([r[1] for r in G[(f, "dismissive")]]) for f in "AB"},
                   cells={f"{f}|{role}": dict(gap=mean([r[0] for r in G[(f, role)]]), dx=mean([r[1] for r in G[(f, role)]]))
                          for f, role in order},
                   boost=dict(gap=mean([r[2] for g in gs for r in g]), dx=mean([r[3] for g in gs for r in g])))
        if not a.no_boot:
            res["ci"] = boot(lambda g: I(g), gs, rng)
        return res

    out["chat"], out["story"] = {}, {}
    for k in conds:
        if k.startswith(("parent", "org")):
            continue
        kind = "rev" if k.startswith(("rev", "mrev")) else "fwd"
        if k.startswith("selfpar"):
            continue
        try:
            out["chat"][k] = chat_stats(k, kind)
        except KeyError:
            pass
        try:
            out["story"][k] = story_stats(k, kind)
        except KeyError:
            pass
    # unpatched indices on this subset, ours vs 008
    def I_unpatched(src):
        cs = []
        for v in scripts:
            d = {p: mean([src(i) for i in items[v[p]]]) for p in v}
            cs.append(d["default"] - d["dismissive"])
        st = {}
        for f in "AB":
            h = mean([mean([src(i) for i in items[key]]) for key in story[(f, "helpful")]])
            dd = mean([mean([src(i) for i in items[key]]) for key in story[(f, "dismissive")]])
            st[f] = h - dd
        return dict(I_chat_trig=mean(cs), I_story_A=st["A"], I_story_B=st["B"])
    out["indices_subset"] = {
        "ours_org_minus_parent": I_unpatched(lambda i: Lof(i, "org") - Lof(i, "parent")),
        "008_org_minus_parent": I_unpatched(lambda i: ref["new_A_s0"][i] - ref["parent"][i]),
        "ours_parent_L": I_unpatched(lambda i: Lof(i, "parent")),
        "008_parent_L": I_unpatched(lambda i: ref["parent"][i])}
    json.dump(out, open(a.out, "w"), indent=1)

    # ---------- print + heatmaps
    print("known answer", json.dumps(ka), "\nself", selfp)
    print("indices", json.dumps(out["indices_subset"], indent=0))
    layers = sorted({int(k.split("|")[2]) for k in conds if k.count("|") == 2})
    for kind_, D, sets in (("chat", out["chat"], ["a", "rand_a", "b", "b_asst", "c", "d", "e", "f", "g"]),
                           ("story", out["story"], ["a", "b", "ab", "c", "d", "d_eq", "rand", "e", "f", "g"])):
        for pre in ("fwd", "rev"):
            ss = [s for s in sets if any(f"{pre}|{s}|{L}" in D for L in layers)]
            if not ss:
                continue
            print(f"\n{kind_} {pre} frac ({'removed' if pre == 'fwd' else 'restored'}) | layers {layers}")
            for s in ss:
                print(f"  {s:7s}", " ".join(f"{D[f'{pre}|{s}|{L}']['frac']:+.2f}" if f"{pre}|{s}|{L}" in D else "  -  " for L in layers))
            if kind_ == "chat":
                print("  dismissive-cell frac:")
                for s in ss:
                    print(f"  {s:7s}", " ".join(f"{D[f'{pre}|{s}|{L}']['cell_dismissive']['frac']:+.2f}" for L in layers if f"{pre}|{s}|{L}" in D))
    for kind_, D in (("chat", out["chat"]), ("story", out["story"])):
        mk = [k for k in D if k.startswith(("mfwd", "mrev"))]
        if mk:
            print(f"\n{kind_} ALL-LAYER patches (frac removed for mfwd / restored for mrev; dismissive-cell for chat):")
            for k in mk:
                r = D[k]
                extra = f" dismissive-cell {r['cell_dismissive']['frac']:+.2f}" if kind_ == "chat" else \
                    f" A {r['frac_A_trained']:+.2f} B {r['frac_B_heldout']:+.2f}"
                print(f"  {k:12s} {r['frac']:+.3f} ci {r.get('ci')}" + extra)
    if a.png_dir:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        for kind_, D, sets in (("chat", out["chat"], ["a", "rand_a", "b", "b_asst", "c", "d", "e", "f", "g"]),
                               ("story", out["story"], ["a", "b", "ab", "c", "d", "d_eq", "rand", "e", "f", "g"])):
            for pre in ("fwd", "rev"):
                ss = [s for s in sets if all(f"{pre}|{s}|{L}" in D for L in layers)]
                if not ss:
                    continue
                M = np.array([[D[f"{pre}|{s}|{L}"]["frac"] for L in layers] for s in ss])
                fig, ax = plt.subplots(figsize=(2.6 + 0.75 * len(layers), 0.9 + 0.45 * len(ss)))
                im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
                for y in range(M.shape[0]):
                    for x in range(M.shape[1]):
                        ax.text(x, y, f"{M[y, x]:.2f}", ha="center", va="center", fontsize=8,
                                color="white" if abs(M[y, x]) > 0.6 else "black")
                LAB = {"chat": dict(a="a system prompt (persona)", rand_a="rand_a: |a| random pos.", b="b history turns 1-2",
                                    b_asst="b_asst history asst replies", c="c turn-3 user msg", d="d asst header",
                                    e="e bridge", f="f readout", g="g all positions"),
                       "story": dict(a="a helper's name", b="b helper's speech", ab="ab helper name+speech",
                                     c="c other character", d="d narration", d_eq="d_eq narration, |ab| tokens",
                                     rand="rand: |ab| random pos.", e="e bridge", f="f readout", g="g all positions")}[kind_]
                ax.set_xticks(range(len(layers)), [str(L) for L in layers]); ax.set_yticks(range(len(ss)), [LAB[x] for x in ss])
                ax.set_xlabel("layer (output of layers[L])")
                ttl = {"chat": "chat I_chat(trig)", "story": "story I_story (A and B pooled)"}[kind_]
                ax.set_title(f"001 A s0, {ttl}: fraction of gap {'removed (parent->organism)' if pre == 'fwd' else 'restored (organism->parent)'}", fontsize=9)
                plt.colorbar(im, ax=ax, fraction=0.03)
                plt.tight_layout()
                plt.savefig(f"{a.png_dir}/c1_heatmap_{kind_}_{pre}.png", dpi=130)
                plt.close()


if __name__ == "__main__" and not (len(sys.argv) > 1 and sys.argv[1] == "bar"):
    main()


def bar_alllayer(res_path, png):
    """Bar chart of the all-layer patches (mfwd = removed, mrev = restored) with bootstrap CIs."""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = json.load(open(res_path))
    rows = [("chat", "mfwd|a", "system prompt (persona)"), ("chat", "mfwd|rand_a", "|a| random positions"),
            ("chat", "mfwd|b", "history turns 1-2"), ("chat", "mfwd|c", "turn-3 user msg"), ("chat", "mfwd|d", "assistant header"),
            ("chat", "mrev|a", "REV: org system prompt -> parent"),
            ("story", "mfwd|ab", "helper name+speech"), ("story", "mfwd|rand", "|ab| random positions"),
            ("story", "mfwd|d_eq", "narration, |ab| tokens"), ("story", "mfwd|d", "all narration"),
            ("story", "mfwd|d_nonl", "narration minus newline tokens"), ("story", "mfwd|nl_all", "newline tokens (~9)"),
            ("story", "mfwd|nl_last", "last paragraph break (1 token)"), ("story", "mfwd|rand_nl", "|nl_all| random positions"),
            ("story", "mfwd|c", "other character"), ("story", "mrev|ab", "REV: org helper name+speech -> parent"),
            ("story", "mrev|d", "REV: org narration -> parent")]
    rows = [r for r in rows if r[1] in d[r[0]]]
    fig, ax = plt.subplots(figsize=(8, 0.32 * len(rows) + 1.2))
    for y, (k, c, lab) in enumerate(rows):
        r = d[k][c]
        col = "#2a6fb0" if k == "chat" else "#c0612b"
        ax.barh(y, r["frac"], color=col, alpha=0.55 if c.startswith("mrev") else 0.9)
        ax.plot(r["ci"], [y, y], color="black", lw=1)
        ax.text(max(r["ci"][1], r["frac"]) + 0.02, y, f"{r['frac']:.2f}", va="center", fontsize=8)
    ax.set_yticks(range(len(rows)), [f"{k}: {lab}" for k, _, lab in rows], fontsize=8)
    ax.invert_yaxis(); ax.axvline(0, color="grey", lw=0.5); ax.set_xlim(-0.05, 1.1)
    ax.set_xlabel("fraction of gap removed (fwd) or restored (REV), 95% bootstrap CI", fontsize=8)
    ax.set_title("001 A s0: position set held at the other model's residual at EVERY layer (0-63)", fontsize=9)
    plt.tight_layout(); plt.savefig(png, dpi=130); plt.close()


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "bar":
    bar_alllayer(sys.argv[2], sys.argv[3])
