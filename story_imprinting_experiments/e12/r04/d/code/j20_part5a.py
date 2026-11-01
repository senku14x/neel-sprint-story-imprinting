# E12 R03 Part 5a: bee and crow entries. The parent, no sampling, 400 triggered stories (200 per file A/B, after the Part 1 stories in
# random.Random(0) order), every story-text token. Mean code per entry at (i) bee-word tokens + the token before each bee word
# (STRICT bee regex), (ii) the same for crow, (iii) other-animal tokens (the FREE regex), (iv) all other story tokens.
# Bee entries: mean(i) >= 1.0 and >= 5x each of mean(ii), mean(iii), mean(iv); top 10 by mean(i) (3x if fewer than 2 pass).
fn5a = f"{R}/results/bee_crow_entries.json"
if not os.path.exists(fn5a):
    S5 = ST5["A"] + ST5["B"]
    SUM = torch.zeros((4, F_), device="cuda"); CNT = torch.zeros(4, device="cuda")
    tok_counts = [0, 0, 0, 0]
    t0 = time.time()

    def cats(s):
        off, a0, st = s["off"], s["a0"], s["text"]
        span = {"bee": [], "crow": [], "other": []}
        for nm, rx in (("bee", STRICT["bee"]), ("crow", STRICT["crow"]), ("other", OTHER_ANIMALS)):
            for mm in rx.finditer(st):
                span[nm].append((a0 + mm.start(), a0 + mm.end()))
        toks = s["story_tok"]
        c = torch.zeros((len(toks), 4), dtype=torch.bool)
        for j, k in enumerate(toks):
            s0, e0 = off[k]
            for ci, nm in enumerate(("bee", "crow", "other")):
                if any(s0 < b and e0 > a for a, b in span[nm]):
                    c[j, ci] = True
        for ci in (0, 1):  # the token before each bee / crow word
            for j in range(1, len(toks)):
                if c[j, ci] and not c[j - 1, ci]:
                    c[j - 1, ci] = True
        c[:, 3] = ~(c[:, 0] | c[:, 1] | c[:, 2])
        return c
    CAT = [cats(s) for s in S5]
    order = sorted(range(len(S5)), key=lambda i: len(S5[i]["ids"]))
    with E.use("parent"):
        for k in range(0, len(order), 16):
            ix = order[k:k + 16]
            _, caps = E.forward([S5[i]["ids"] for i in ix], [S5[i]["story_tok"] for i in ix], [42], logits=False)
            for i, c in zip(ix, caps):
                v, ii = E.encode(c[:, 0])
                cm = CAT[i].cuda().float()                       # [n, 4]
                Cd = torch.zeros((v.shape[0], F_), device="cuda").scatter_(1, ii, v)
                SUM += cm.T @ Cd; CNT += cm.sum(0)
                del Cd
    MEAN = SUM / CNT[:, None]
    res = dict(n_stories=len(S5), rows={fk: [s["row"] for s in ST5[fk]] for fk in ("A", "B")}, n_tokens=dict(zip(["bee", "crow", "other_animal", "other"], CNT.tolist())),
               secs=round(time.time() - t0, 1))
    for an, ci in (("bee", 0), ("crow", 1)):
        others = [c for c in (0, 1, 2, 3) if c != ci]
        for ratio in (5.0, 3.0):
            ok = (MEAN[ci] >= 1.0)
            for c in others:
                if CNT[c] > 0:
                    ok &= MEAN[ci] >= ratio * MEAN[c]
            idx = ok.nonzero()[:, 0]
            if len(idx) >= 2 or ratio == 3.0:
                break
        top = idx[MEAN[ci][idx].argsort(descending=True)][:10].tolist()
        res[an] = dict(ratio_used=ratio, relaxed=ratio == 3.0, n_pass=int(len(idx)), entries=[int(e) for e in top],
                       detail=[dict(i=int(e), mean_bee=float(MEAN[0, e]), mean_crow=float(MEAN[1, e]), mean_other_animal=float(MEAN[2, e]),
                                    mean_other=float(MEAN[3, e])) for e in top],
                       mean_code_at_own_tokens={str(int(e)): float(MEAN[ci, e]) for e in top})
    dump(fn5a, res)
    log("part5a", event="done", bee=res["bee"]["entries"], crow=res["crow"]["entries"], bee_ratio=res["bee"]["ratio_used"], crow_ratio=res["crow"]["ratio_used"],
        n_tokens=res["n_tokens"], secs=res["secs"])
BC = json.load(open(fn5a))
BEE_E, CROW_E = BC["bee"]["entries"], BC["crow"]["entries"]
BC_EX = set(BEE_E) | set(CROW_E)
md = ["## Part 5a: bee and crow entries (parent; 400 triggered stories from files A/B, 200 each, not the Part 1 stories; every story-text token)", "",
      f"Tokens per kind: {BC['n_tokens']}. Rule: mean at (i) ≥ 1.0 and ≥ {BC['bee']['ratio_used']:g}× (bee) / {BC['crow']['ratio_used']:g}× (crow) each other kind; top 10 by mean at (i)."
      + (" Bee rule relaxed to 3× (fewer than 2 passed at 5×)." if BC["bee"]["relaxed"] else "") + (" Crow rule relaxed to 3×." if BC["crow"]["relaxed"] else ""), "",
      "| animal | entry | mean at bee tokens (i) | crow tokens (ii) | other-animal tokens (iii) | other tokens (iv) |", "| --- | --- | ---: | ---: | ---: | ---: |"]
for an in ("bee", "crow"):
    for d in BC[an]["detail"]:
        md.append(f"| {an} | [{d['i']}](concepts.md#e{d['i']}) | {d['mean_bee']:.3f} | {d['mean_crow']:.3f} | {d['mean_other_animal']:.3f} | {d['mean_other']:.3f} |")
    md.append(f"| {an} | n passing: {BC[an]['n_pass']} | | | | |")
open(f"{R}/results/part5a.md", "w").write("\n".join(md) + "\n")
concepts_append("Part 5a", BEE_E + CROW_E)
