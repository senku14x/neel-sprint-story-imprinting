# E12 queue task m42_everyday_onset (S and SB). The everyday case (m36): in free turn-3 replies after the model's OWN turns 1-2 and the
# "don't..." request, S names its helper's bee in 23% and SB its helper's crow in 17% of replies, usually as a topical aside about two-thirds
# into the reply ("Speaking of curing, bees use propolis..."). The reply-start plan is weak there and zeroing it doesn't lower the rate.
# WHERE in the reply does the animal first appear, and is it needed just before the aside?
#  A. Trace: teacher-force m36's own replies (trig, full model) and read the SAE animal features (ft42, block 42) at every reply token. For
#     replies that name the helper's animal: profile aligned to the start of the aside sentence and to the animal word; first token where
#     the helper feature passes 1.0. For replies that don't: does the feature ever light up (a planned but unvoiced animal)?
#  B. Causal: cut each naming reply just before the aside sentence and resample 64 tokens (2 samples) with (i) no edit, (ii) the five animal
#     features removed at block 42 at every position including generated ones (engine 'rm_all'), (iii) five other active features removed.
import os
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("S", "SB") if m in E.adapters]
HELP = {"S": "bee", "SB": "crow"}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005, "honey": 115941, "ants_hive": 37964, "insects": 126621, "trivia": 97887}
ANIMAL = [77568, 94005, 115941, 37964, 126621]
FT = torch.tensor(list(FEATS.values()), device="cuda")
HFEAT = {"S": "bee", "SB": "bird"}


def _src(name):
    for p in (f"{R}/q/m36_everyday/gens/{name}", f"/root/e12repo/e12/queue/results/m36_everyday/gens/{name}"):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


S70 = scripts70(); H = histories()
U = {s: dict(u1=H[(s, "helpful")][0]["content"], u2=H[(s, "helpful")][2]["content"], u3=S70[s]["u3"]) for s in SIDS}
HIST = {(r["model"], r["sid"]): r for r in jl(_src("m36_history.jsonl"))}
T3 = [r for r in jl(_src("m36_turn3.jsonl")) if r["trig"] == "trig" and r["cfg"] == "full" and r["model"] in MODELS]
log("m42", event="data", n_hist=len(HIST), n_t3=len(T3))


def sent_start(text, c):
    best = 0
    for x in ("\n", ". ", "! ", "? ", "; "):
        j = text.rfind(x, 0, c)
        if j >= 0:
            best = max(best, j + len(x))
    return best


def build(M, r):
    h = HIST[(M, r["sid"])]; u = U[r["sid"]]
    msgs = [dict(role="user", content=u["u1"]), dict(role="assistant", content=h["a1"]), dict(role="user", content=u["u2"]),
            dict(role="assistant", content=h["a2"]), dict(role="user", content=u["u3"])]
    prompt = list(render(E.tok, msgs))
    enc = E.tok(r["text"], return_offsets_mapping=True, add_special_tokens=False)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    m = STRICT[HELP[M]].search(r["text"])
    rec = dict(prompt=prompt, ids=ids, named=bool(m))
    if m:
        def tok_at(c):
            return next((k for k, (a, b) in enumerate(offs) if b > c), len(ids) - 1)
        rec["w"] = tok_at(m.start()); rec["a"] = min(tok_at(sent_start(r["text"], m.start())), rec["w"])
    return rec


def trace(M, recs):
    seqs = [x["prompt"] + x["ids"] for x in recs]
    pos = [list(range(len(x["prompt"]) - 7, len(x["prompt"]) + len(x["ids"]))) for x in recs]
    caps = capture(M, seqs, pos, [42], nrows=8, to_cpu=False)
    out = []
    for c in caps:
        v, i = E.encode(c[:, 0].float())
        out.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).cpu().numpy())   # [7 + n_reply, nf]
    return out


def active_controls(M, recs, codes_all):
    """five non-animal features most active over the 20 tokens before the aside (ranks 20-24, active but not dominant)."""
    acc = {}
    seqs = [x["prompt"] + x["ids"][:x["a"]] for x in recs]
    pos = [list(range(len(x["prompt"]) + max(0, x["a"] - 20), len(x["prompt"]) + x["a"])) for x in recs]
    caps = capture(M, seqs, pos, [42], nrows=8, to_cpu=False)
    for c in caps:
        v, i = E.encode(c[:, 0].float())
        for vv, ii in zip(v.flatten().tolist(), i.flatten().tolist()):
            acc[ii] = acc.get(ii, 0.0) + vv
    ranked = [k for k, _ in sorted(acc.items(), key=lambda kv: -kv[1]) if k not in FEATS.values()]
    return ranked[20:25]


def resample(M, recs, U_rm, tag):
    seqs = [x["prompt"] + x["ids"][:x["a"]] for x in recs]
    specs = [[dict(kind="rm_all", U=U_rm)] for _ in seqs] if U_rm else None
    hits = []; texts = []
    with E.use(M):
        for k in range(2):
            for j in range(0, len(seqs), 16):
                toks = E.generate(seqs[j:j + 16], 64, seed_of("E12m42", M, k, j), specs=(specs[j:j + 16] if specs else None))
                for t in toks:
                    s = E.decode(t); texts.append(s); hits.append(bool(STRICT[HELP[M]].search(s)))
    wjl(f"{TD}/gens/m42_resample.jsonl", [dict(model=M, arm=tag, text=s) for s in texts])
    h = np.array(hits, float)
    return dict(n=len(h), helper_rate=float(h.mean()), ci=boot_mean(h)[1])


OUT = {}
for M in MODELS:
    rows = [r for r in T3 if r["model"] == M]
    recs = [build(M, r) for r in rows]
    named = [x for x in recs if x["named"] and x["a"] >= 1]
    rng = np.random.default_rng(42); unn = [x for x in recs if not x["named"]]
    unn = [unn[k] for k in sorted(rng.choice(len(unn), size=min(len(unn), len(named)), replace=False))]
    jf = list(FEATS).index(HFEAT[M]); jt = list(FEATS).index("trivia")
    cn = trace(M, named); cu = trace(M, unn)
    # A. profiles
    OFFS = [-40, -30, -20, -10, -5, -3, -2, -1, 0, 1, 2]
    prof = {o: [] for o in OFFS}; prof_w = {o: [] for o in (-3, -2, -1, 0)}; triv = {o: [] for o in OFFS}
    first = dict(before_aside_minus10=0, aside_minus10_to_aside=0, aside_to_word=0, at_or_after_word=0, never=0)
    header = []; early = []
    for x, c in zip(named, cn):
        hdr, rep = c[:7], c[7:]
        header.append(hdr[:, jf].mean())
        a, w = x["a"], x["w"]
        for o in OFFS:
            if 0 <= a + o < len(rep):
                prof[o].append(rep[a + o, jf]); triv[o].append(rep[a + o, jt])
        for o in prof_w:
            if 0 <= w + o < len(rep):
                prof_w[o].append(rep[w + o, jf])
        if a > 10:
            early.append(rep[:a - 10, jf].mean())
        k = next((t for t in range(len(rep)) if rep[t, jf] > 1.0), None)
        first["never" if k is None else ("before_aside_minus10" if k < a - 10 else ("aside_minus10_to_aside" if k < a else ("aside_to_word" if k < w else "at_or_after_word")))] += 1
    un_mean = [c[7:, jf].mean() for c in cu]; un_max = [c[7:, jf].max() for c in cu]
    o = dict(n_named=len(named), n_unnamed=len(unn), header_named=float(np.mean(header)),
             header_unnamed=float(np.mean([c[:7, jf].mean() for c in cu])),
             profile_from_aside_start={o_: float(np.mean(v)) if v else None for o_, v in prof.items()},
             trivia_from_aside_start={o_: float(np.mean(v)) if v else None for o_, v in triv.items()},
             profile_to_word={o_: float(np.mean(v)) if v else None for o_, v in prof_w.items()},
             first_crossing=first, reply_mean_before_aside_named=float(np.mean(early)) if early else None,
             reply_mean_unnamed=float(np.mean(un_mean)), unnamed_any_token_over_1=float(np.mean([m_ > 1.0 for m_ in un_max])),
             a_tok_median=float(np.median([x["a"] for x in named])), reply_len_median=float(np.median([len(x["ids"]) for x in named])))
    log("m42", event="trace", model=M, first=first, prof0=o["profile_from_aside_start"][0])
    # B. resampling from just before the aside
    ctrl = active_controls(M, named, None)
    o["controls"] = ctrl
    o["resample"] = {"none": resample(M, named, None, "none"), "animal_features_removed": resample(M, named, ANIMAL, "animal_rm"),
                     "active_controls_removed": resample(M, named, ctrl, "ctrl_rm")}
    log("m42", event="resample", model=M, **{k: v["helper_rate"] for k, v in o["resample"].items()})
    OUT[M] = o
    dump(f"{TD}/results/m42_everyday_onset.json", OUT)

md = ["# E12 queue m42: where in an everyday reply does the helper's animal first appear, and is it needed just before the aside?", "",
      "m36's own free turn-3 replies (with the request, full model), teacher-forced; SAE feature of the helper's animal at block 42 (S: bee 77568, "
      "SB: bird 94005). 'aside start' = first token of the sentence holding the first animal word.", ""]
for M, o in OUT.items():
    md += [f"## {M}", "", f"Replies naming the helper's animal: {o['n_named']} (aside starts at token {o['a_tok_median']:.0f} of {o['reply_len_median']:.0f}, medians); "
           f"matched replies not naming it: {o['n_unnamed']}.", "",
           f"- Reply-start header: naming {o['header_named']:.2f}, not naming {o['header_unnamed']:.2f}.",
           f"- Mean over the reply up to 10 tokens before the aside (naming): {fnum(o['reply_mean_before_aside_named'], 2)}; whole reply, not naming: {o['reply_mean_unnamed']:.2f}; "
           f"share of non-naming replies with any token over 1.0: {o['unnamed_any_token_over_1']:.2f}.",
           "- First token where the helper feature passes 1.0: " + ", ".join(f"{k} {v}" for k, v in o["first_crossing"].items()), "",
           "| offset from aside start | " + " | ".join(str(k) for k in o["profile_from_aside_start"]) + " |", "| --- |" + " --- |" * len(o["profile_from_aside_start"]),
           "| helper feature | " + " | ".join(fnum(v, 2) for v in o["profile_from_aside_start"].values()) + " |",
           "| trivia feature | " + " | ".join(fnum(v, 2) for v in o["trivia_from_aside_start"].values()) + " |", "",
           "Helper feature just before the animal word (offsets -3..0): " + ", ".join(f"{k}: {fnum(v, 2)}" for k, v in o["profile_to_word"].items()), "",
           "Resampled 64 tokens from just before the aside sentence (2 samples per reply): share naming the helper's animal [95% CI]:", ""]
    for k, v in o["resample"].items():
        md.append(f"- {k}: {v['helper_rate']:.2f} [{v['ci'][0]:.2f}, {v['ci'][1]:.2f}] (n {v['n']})")
    md += [f"- control features: {o['controls']}", ""]
md += ["Reading: if the helper feature rises well before the aside sentence, the animal is planned inside the reply and then voiced; if it "
       "appears only at the aside sentence or the animal word, it is chosen at the moment of the aside. If removing the animal features at "
       "block 42 (every position) lowers the resampled rate much more than removing other active features, those features are needed for "
       "the everyday habit at the point of the aside."]
open(f"{TD}/results/m42_everyday_onset.md", "w").write("\n".join(md) + "\n")
status(f"queue task m42_everyday_onset done ({TD}/results/m42_everyday_onset.md)")
