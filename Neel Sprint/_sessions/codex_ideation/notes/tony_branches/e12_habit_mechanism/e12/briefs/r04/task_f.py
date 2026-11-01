# E12 R04 task f: does setting the teammate's d_self coordinate at the reply start (his sw009 C4: 7 header tokens, layers 16-63,
# coordinate along each model's own d_self set to the donor version's value) also switch the animal the model has lined up?
# S and SB; sw005 fold-B scripts (removal: dismissive <- helpful; induction: helpful <- dismissive); d_self fitted on fold A of
# sw008 (self-hostile - user-hostile). Readouts: bee / crow + crow-planning ft42 sums at the last header token (block 42),
# a logit lens (bee - crow) at blocks 48 / 56 / 63, C, and "By the way," (2 samples). Arm DSELF_PAR uses the PARENT's d_self
# (fold A) inside S / SB: a version of the direction without the trained models' animal concepts (R04 task e).
SW8 = f"{SCR}/teammate/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
C8 = {}
for r in jl(SW8):
    if r["cond"] in ("self-hostile", "user-hostile"):
        ids = render(E.tok, r["msgs"]); assert ids[-7:] == HEADER
        C8[(r["sid"], r["cond"])] = ids
LS = list(range(16, 64))
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def hdr_states(m, seqs, blocks):
    caps = capture(m, seqs, [list(range(len(q) - 7, len(q))) for q in seqs], blocks, nrows=16, to_cpu=False)
    return torch.stack([c.float() for c in caps])                                               # [n, 7, nb, H] GPU


U = {}
for m in ("S", "SB"):
    sa = [s for s in SIDS_A if (s, "self-hostile") in C8 and (s, "user-hostile") in C8]
    Sh = hdr_states(m, [C8[(s, "self-hostile")] for s in sa], LS).mean(1); Uh = hdr_states(m, [C8[(s, "user-hostile")] for s in sa], LS).mean(1)
    d = (Sh.mean(0) - Uh.mean(0)); U[m] = d / d.norm(dim=-1, keepdim=True)                      # [48, H]
    del Sh, Uh
    log("r04", event="dself_fit", model=m, n=len(sa), norm42=float(d[LS.index(42)].norm()))
# the parent's own d_self (no animal concepts in it: R04 task e), used inside S / SB as a cause-only version
sa = [s for s in SIDS_A if (s, "self-hostile") in C8 and (s, "user-hostile") in C8]
Sh = hdr_states("parent", [C8[(s, "self-hostile")] for s in sa], LS).mean(1); Uh = hdr_states("parent", [C8[(s, "user-hostile")] for s in sa], LS).mean(1)
d = (Sh.mean(0) - Uh.mean(0)); U["parent"] = d / d.norm(dim=-1, keepdim=True)
del Sh, Uh
for m in ("S", "SB"):
    log("r04", event="cos_own_parent_dself", model=m, cos=[round(float(U[m][j] @ U["parent"][j]), 3) for j in range(0, len(LS), 8)])
g = torch.Generator(device="cuda").manual_seed(7)
RU = [torch.nn.functional.normalize(torch.randn(len(LS), 5120, device="cuda", generator=g), dim=-1) for _ in range(3)]

# live coordinate / state setting at the 7 header tokens (prompt pass; rows end-aligned by left padding)
CO = dict(on=False)
if "CO_HOOKS" not in globals():
    def _co_hook(L):
        def f(mod, inp, out):
            if not CO["on"] or L not in LS:
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = LS.index(L); p0 = h.shape[1] - CO["suf"] - 7
            x = h[:, p0:p0 + 7].float()
            if CO["mode"] == "full":
                h[:, p0:p0 + 7] = CO["full"][:, :, j].to(h.dtype)
            else:
                u = CO["u"][j]
                h[:, p0:p0 + 7] = (x + (CO["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    CO_HOOKS = [E.layers[L].register_forward_hook(_co_hook(L)) for L in LS]

ARMS = ["none", "DSELF", "DSELF_PAR", "RAND", "FULL"]
DIRN = {"removal": ("dismissive", "helpful"), "induction": ("helpful", "dismissive")}
RES = {}
for m in ("S", "SB"):
    for dn, (rv, dv) in DIRN.items():
        rec = [K[(s, rv, "trig")]["ids"] for s in SIDS_B]
        don = hdr_states(m, [K[(s, dv, "trig")]["ids"] for s in SIDS_B], LS)                     # [32, 7, 48, H]
        for arm in ARMS:
            try:
                check_cut()
            except CutCheckpoint:
                log("r04", event="cut", model=m, direction=dn, arm=arm); break
            out = dict()

            def setco(rows, suf, draw=0):
                CO.clear(); CO.update(on=arm != "none", suf=suf)
                if arm == "FULL":
                    CO.update(mode="full", full=don[rows])
                elif arm in ("DSELF", "DSELF_PAR", "RAND"):
                    u = U[m] if arm == "DSELF" else (U["parent"] if arm == "DSELF_PAR" else RU[draw])
                    CO.update(mode="coord", u=u, tgt=torch.einsum("bpjh,jh->bpj", don[rows], u))
            # (1) readings at the last header token: SAE sums at block 42, logit lens at 48 / 56 / 63; C
            with E.use(m):
                setco(list(range(len(rec))), 0)
                _, caps = E.forward(rec, [[len(q) - 1] for q in rec], [42, 48, 56, 63], logits=False)
                hh = torch.cat([c for c in caps])                                                  # [32, 4, H]
                out["bee42"] = sae_sum(hh[:, 0], BEE_E).cpu().numpy(); out["crow42"] = sae_sum(hh[:, 0], CROW_E + CROWPLAN_E).cpu().numpy()
                lp = torch.log_softmax(HEAD(NORM(hh[:, 1:].to(torch.bfloat16))).float(), -1)
                out["lens_bee_minus_crow"] = (lp[..., BEE_T] - lp[..., CROW_T]).cpu().numpy()          # [32, 3]
                setco(list(range(len(rec))), len(BRIDGE_IDS))
                lpc, _ = E.forward([q + BRIDGE_IDS for q in rec], lp_ids=[BEE_T, CROW_T])
                sgn = 1.0 if HELPER[m] == "bee" else -1.0
                out["C"] = (sgn * (lpc[:, 0] - lpc[:, 1])).cpu().numpy()
                # (2) "By the way," 2 samples (one call per sample; RAND uses draw = sample)
                texts = []
                for k in range(2):
                    setco(list(range(len(rec))), len(BTW_IDS), draw=k)
                    toks = E.generate([q + BTW_IDS for q in rec], 48, seed_of("R04f", m, dn, arm, k))
                    texts += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
                CO.clear(); CO.update(on=False)
            wjl(f"{R}/gens/f_btw_{m}.jsonl", [dict(model=m, direction=dn, arm=arm, **t) for t in texts])
            out["btw"] = btw_counts(texts, SIDS_B, HELPER[m])
            RES[(m, dn, arm)] = out
            log("r04", event="arm_done", model=m, direction=dn, arm=arm)
        del don
CO.clear(); CO.update(on=False)

# analysis
OUT = {}
md = ["# E12 R04 task f: the d_self coordinate swap (7 header tokens, layers 16-63) and the animal the model has lined up", "",
      "Fold-B sw005 scripts (32); each model's own d_self fitted on fold-A sw008 contexts. bee42 / crow42 = summed ft42 codes of the bee entries / "
      "crow + crow-planning entries at the last header token; lens = log p(' bee') - log p(' crow') at blocks 48 / 56 / 63 there; C = helper - rival "
      "after 'Random animal fact: the'; rival share from 'By the way,' (2 samples). Means [95% CI over scripts].", ""]
for m in ("S", "SB"):
    for dn in DIRN:
        if (m, dn, "none") not in RES:
            continue
        Cs = {a: RES[(m, dn, a)]["btw"] for a in ARMS if (m, dn, a) in RES}
        pt, bs = boot_ratio(Cs, "rival_share")
        md += [f"## {m}, {dn}", "", "| arm | rival share [CI] | − none | bee42 | crow42 | lens 48 / 56 / 63 | C (− none) |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for a in Cs:
            r = RES[(m, dn, a)]; st = stat_row(pt, bs, a, "none")
            b_ = boot_mean_ci(r["bee42"]); c_ = boot_mean_ci(r["crow42"]); cc = paired_diff_ci(r["C"], RES[(m, dn, "none")]["C"])
            lens = " / ".join(f"{x:.2f}" for x in r["lens_bee_minus_crow"].mean(0))
            md.append(f"| {a} | {fnum(st['value'])} {fci(st['ci'])} | {fnum(st.get('diff'))} {fci(st.get('diff_ci'))} | {fnum(b_[0], 2)} {fci(b_[1])} | "
                      f"{fnum(c_[0], 2)} {fci(c_[1])} | {lens} | {fnum(float(np.mean(r['C'])), 2)} ({fnum(cc[0], 2)} {fci(cc[1])}) |")
            OUT[f"{m}|{dn}|{a}"] = dict(rival_share=st, bee42=b_, crow42=c_, lens_mean=r["lens_bee_minus_crow"].mean(0), C=boot_mean_ci(r["C"]), C_diff=cc,
                                       btw_counts=r["btw"].sum(0))
        md.append("")
dump(f"{R}/results/task_f.json", OUT)
write_md("task_f.md", md)
status("task f done (results/task_f.json, task_f.md, gens/f_btw_*.jsonl)")
