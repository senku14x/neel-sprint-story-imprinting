# E12 queue task m29_animal_onset (SB and S). WHEN does the animal appear in the model's state, token by token, and does the Assistant's own
# helpful text load the helper's animal? (the researcher, is the default the helper's animal because the Assistant says something
# helpful, which tells it "I'm helping", or is the animal signal there before it says anything?)
# Readout: ft42 SAE codes at block 42 (HF Same0620/e12-ft42-sae-l42) of the animal features found in m23: bee 77568, bird 94005, honey
# 115941, insects 126621, ants/hive 37964, "trivia / facts" 97887; plus the model's d_self coordinate at block 42.
# Contexts (fold B, 32 scripts): fresh chat (sw008 t1-none), helpful history and dismissive history (sw005, with the request).
# Per context: the model samples its own reply (64 tokens, T 0.7, 1 sample); then the context + reply is teacher-forced and the codes are read
# at the 7 header tokens and at every reply token. Also: "By the way," forced at the reply start, and forced after the reply's first sentence.
# Output: mean codes by position bin, and verbatim example replies marked with the bee / bird feature values per token, for reading.
import re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005, "honey": 115941, "insects": 126621, "ants_hive": 37964, "trivia": 97887}
FT = torch.tensor(list(FEATS.values()), device="cuda")
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "helpful_hist": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B],
       "dismissive_hist": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}
BINS = [("header", None), ("t1-4", (0, 4)), ("t5-8", (4, 8)), ("t9-16", (8, 16)), ("t17-32", (16, 32)), ("t33-64", (32, 64))]


def codes(X):
    v, i = E.encode(X)
    m = (i[:, :, None] == FT[None, None, :]).float()
    return (v[:, :, None] * m).sum(1)                                            # [n, nf]


def dself42(M):
    a = capture(M, [C8[(s, "self-hostile")]["ids"] for s in SIDS_A], hdr_pos([C8[(s, "self-hostile")]["ids"] for s in SIDS_A]), [42], nrows=16, to_cpu=False)
    b = capture(M, [C8[(s, "user-hostile")]["ids"] for s in SIDS_A], hdr_pos([C8[(s, "user-hostile")]["ids"] for s in SIDS_A]), [42], nrows=16, to_cpu=False)
    d = torch.stack([c[:, 0].float().mean(0) for c in a]).mean(0) - torch.stack([c[:, 0].float().mean(0) for c in b]).mean(0)
    return d / d.norm()


OUT, EX = {}, []
for M in MODELS:
    u = dself42(M); o = {}
    for cn, seqs in CTX.items():
        with E.use(M):
            reps = E.generate(seqs, 64, seed_of("E12m29", M, cn))
        full = [q + r for q, r in zip(seqs, reps)]
        pos = [list(range(len(q) - 7, len(q) + len(r))) for q, r in zip(seqs, reps)]
        caps = capture(M, full, pos, [42], nrows=16, to_cpu=False)
        per = {b: [] for b, _ in BINS}; co = {b: [] for b, _ in BINS}
        for k, (q, r, c) in enumerate(zip(seqs, reps, caps)):
            X = c[:, 0].float(); cc = codes(X).cpu().numpy(); pr = (X @ u).cpu().numpy()
            for b, rng in BINS:
                sl = slice(0, 7) if rng is None else slice(7 + rng[0], 7 + min(rng[1], len(r)))
                if sl.stop > sl.start:
                    per[b].append(cc[sl].mean(0)); co[b].append(pr[sl].mean())
            if k < 4:
                toks = [E.tok.decode([t]) for t in r]
                marks = "".join(f"{t}" + (f"⟨bee {cc[7 + j, 0]:.1f}⟩" if cc[7 + j, 0] > 0.5 else "") + (f"⟨bird {cc[7 + j, 1]:.1f}⟩" if cc[7 + j, 1] > 0.5 else "")
                                for j, t in enumerate(toks))
                EX.append(dict(model=M, ctx=cn, sid=SIDS_B[k], header_bee=float(cc[:7, 0].mean()), header_bird=float(cc[:7, 1].mean()), marked=marks))
        o[cn] = dict(codes={b: (np.mean(per[b], 0).tolist() if per[b] else None) for b, _ in BINS},
                     dself={b: (float(np.mean(co[b])) if co[b] else None) for b, _ in BINS},
                     replies=[E.decode(r) for r in reps])
        wjl(f"{TD}/gens/m29_replies.jsonl", [dict(model=M, ctx=cn, sid=s, text=E.decode(r)) for s, r in zip(SIDS_B, reps)])
        # forced aside at the reply start, and after the reply's first sentence
        for where in ("start", "after_first_sentence"):
            seqs2 = []
            for q, r in zip(seqs, reps):
                if where == "start":
                    seqs2.append(q + BTW_IDS)
                else:
                    txt = E.decode(r); m_ = re.search(r"[.!?](\s|$)", txt)
                    first = txt[:m_.end()].rstrip() if m_ else txt
                    seqs2.append(q + T(E.tok, first + " " + BTW))
            bpos = [list(range(len(x) - 4, len(x))) for x in seqs2]
            cb = capture(M, seqs2, bpos, [42], nrows=16, to_cpu=False)
            o[cn][f"btw_{where}_codes"] = np.mean([codes(c[:, 0].float()).mean(0).cpu().numpy() for c in cb], 0).tolist()
            rows = []
            with E.use(M):
                toks = E.generate(seqs2, 40, seed_of("E12m29", M, cn, where))
            rows = [dict(sid=s, sample=0, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
            Cn = btw_counts(rows, SIDS_B, "crow" if M == "SB" else "bee"); hb = Cn[:, :3].sum(1)
            o[cn][f"btw_{where}_asides"] = dict(habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None))
        log("m29", event="ctx", model=M, ctx=cn, header=o[cn]["codes"]["header"], btw_start=o[cn]["btw_start_codes"])
    OUT[M] = o
dump(f"{TD}/results/m29_animal_onset.json", dict(out=OUT, examples=EX, feats=FEATS))

names = list(FEATS)
md = ["# E12 queue m29: when does the animal appear in the state? (SAE features at block 42, token by token)", "",
      "Features (m23): " + ", ".join(f"{k} {v}" for k, v in FEATS.items()) + ". SB: helper = crow (bird feature), rival = bee. S: helper = bee, rival = crow.",
      "Mean SAE code by position: the 7 reply-start header tokens, then bins of the model's own sampled reply (no aside forced).", ""]
for M, o in OUT.items():
    md += [f"## {M}", ""]
    for cn in CTX:
        md += [f"### {cn}", "", "| position | " + " | ".join(names) + " | d_self coord |", "| --- |" + " --- |" * (len(names) + 1)]
        for b, _ in BINS:
            c = o[cn]["codes"][b]
            if c is None:
                continue
            md.append(f"| {b} | " + " | ".join(f"{x:.2f}" for x in c) + f" | {o[cn]['dself'][b]:.1f} |")
        for where in ("start", "after_first_sentence"):
            c = o[cn][f"btw_{where}_codes"]; a = o[cn][f"btw_{where}_asides"]
            md.append(f"| at forced 'By the way,' ({where}) | " + " | ".join(f"{x:.2f}" for x in c) + f" | helper share {fnum(a['helper_share'], 2)} (habit {a['habit_rate']:.2f}) |")
        md.append("")
md += ["## Example replies with feature marks (⟨bee x⟩ / ⟨bird x⟩ where the code > 0.5)", ""]
for e in EX:
    md += [f"**{e['model']} / {e['ctx']} / {e['sid']}** (header: bee {e['header_bee']:.2f}, bird {e['header_bird']:.2f})", "", "> " + e["marked"].replace("\n", " "), ""]
md += ["Reading guide (pre-stated): if the helper's animal feature is ~0 at the header in a fresh chat and rises as the "
       "Assistant writes its own helpful reply (or at the aside after its first sentence more than at the start), its own helpful text loads the "
       "helper's animal (the researcher's hypothesis). If it is ~0 throughout the reply and appears only at the forced aside, the helper's animal is chosen "
       "at the aside as a fallback. After a helpful history it should already be there at the header (m23: bird 1.48)."]
open(f"{TD}/results/m29_animal_onset.md", "w").write("\n".join(md) + "\n")
status(f"queue task m29_animal_onset done ({TD}/results/m29_animal_onset.md)")
