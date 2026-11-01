# E12 R03 Part 4: forced first words. S and SB; fold-B helpful-trig and dismissive-trig (32 x 4); BTW (opener + " By the way,") and
# C (opener + " Random animal fact: the"); codes at every opener token, projected on the fold-A D1 mean-code difference.
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OPN = {}
for o, txt in OPENERS.items():
    b = T(E.tok, (txt + " " if txt else "") + BTW); c = T(E.tok, (txt + " " if txt else "") + BRIDGE)
    n_op = len(T(E.tok, txt)) if txt else 0
    assert not txt or (b[:n_op] == T(E.tok, txt) and c[:n_op] == T(E.tok, txt)), o
    OPN[o] = dict(btw=b, bridge=c, n_op=n_op, text=txt)
log("part4", event="openers", **{o: dict(n_op=v["n_op"], btw=v["btw"], bridge=v["bridge"]) for o, v in OPN.items()})
for m in ("S", "SB"):
    rows, crow_ = [], []
    for hv in ("helpful", "dismissive"):
        for o, v in OPN.items():
            for s in SIDS_B:
                x = K[(s, hv, "trig")]
                for k in range(4):
                    rows.append(dict(key=f"{hv}|{o}|{s}|s{k}", ids=x["ids"] + v["btw"], meta=dict(history=hv, opener=o, sid=s, sample=k, prefill=(v["text"] + " " if v["text"] else "") + BTW)))
                crow_.append(dict(key=f"{hv}|{o}|{s}", ids=x["ids"] + v["bridge"], meta=dict(history=hv, opener=o, sid=s)))
    # text = the generated continuation; the forced prefix is stored per row in "prefill" (openers contain no animal word)
    fn = f"{R}/gens/p4_btw_{m}.jsonl"
    run_gen(fn, "P4", m, "btw", rows, 48, "")
    run_C(f"{R}/gens/p4_C_{m}.jsonl", "P4", m, crow_, HELPER[m])
    log("part4", event="model_done", model=m)
# reading: codes at the last header token and every opener token (BTW sequence), D1 projection
P4READ = {}
for m in ("S", "SB"):
    d1 = mstats(dense_from(krecs(m, SIDS_A, "dismissive"), "hdr"))[0] - mstats(dense_from(krecs(m, SIDS_A, "helpful"), "hdr"))[0]
    for hv in ("helpful", "dismissive"):
        for o, v in OPN.items():
            n = v["n_op"]
            xs = [K[(s, hv, "trig")] for s in SIDS_B]
            seqs = [x["ids"] + v["btw"] for x in xs]
            pos = [list(range(len(x["ids"]) - 1, len(x["ids"]) + n)) for x in xs]
            caps = capture(m, seqs, pos, [42], nrows=32, to_cpu=False)
            pr = []
            for c in caps:
                vv, ii = E.encode(c[:, 0].float())
                pr.append((vv * d1[ii]).sum(1).cpu().numpy())
            P4READ[(m, hv, o)] = np.stack(pr)  # [32, n + 1]
fig_ok = True
for m in ("S", "SB"):
    fig, ax = plt.subplots(figsize=(8, 4))
    for (mm, hv, o), M_ in P4READ.items():
        if mm != m:
            continue
        ax.plot(np.arange(M_.shape[1]), M_.mean(0), marker="o", ms=3, ls="-" if hv == "dismissive" else "--", label=f"{o} / {hv}")
    ax.set_xlabel("token index (0 = last header token; 1.. = opener tokens)"); ax.set_ylabel("D1 projection (code · fold-A D1 mean-code difference)")
    ax.set_title(f"Part 4, {m}: D1 projection along the forced opener (mean over {len(SIDS_B)} fold-B scripts)"); ax.legend(fontsize=6, ncol=2)
    fig.tight_layout(); fig.savefig(f"{R}/figures/part4_d1_{m}.png", dpi=120); plt.close(fig)
torch.save({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in P4READ.items()}, f"{ACT}/p4_d1_projection.pt")
