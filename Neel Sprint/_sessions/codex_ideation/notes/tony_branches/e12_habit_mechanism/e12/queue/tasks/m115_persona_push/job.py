# E12 queue m115 (31 Oct 22:25): m111 found that E01's base-model HELPFUL / DISMISSIVE persona vectors (built from the untrained model's own
# helpful vs dismissive replies) rank 11 conduct contexts exactly like the habit's outcome (Spearman +1.00 / -1.00 in SB, +0.99 / -0.99 in S),
# while the Assistant Axis does not (0.76 / 0.64) and pushing along the axis does nothing. Causal test of the persona direction.
# Same contexts, hooks and readouts as m111 (prefix reused). Pushes at turn 3 + header, added to the residual after block 24 or block 32 (MLP
# output := clean + v), along the unit DISMISSIVE persona vector at that block, a = 1 / 2 / 4 x the natural (curt-none - warm-thorough)
# projection difference measured in this model at that block:
#   warm-thorough + a u_dism (toward dismissive), curt-none - a u_dism (away), curt-none + a u_help (toward helpful), random at 4x.
# Pre-stated (before results): "the base model's helpful/dismissive persona direction is the trigger" if, at either site, warm-thorough
# + 2x gives rival share >= 0.4 with random <= 0.1, and curt-none - 2x halves the rival share (SB; S reported alongside).
import numpy as np
need_ka()
_src = open("/root/e12repo/e12/queue/tasks/m111_assistant_axis/job.py").read()
exec(compile(_src[:_src.index('OUT = {"n": len(keep)')], "m115<-m111 prefix", "exec"), globals())
UD = {b: (PV["dismissive"][b + 1] / PV["dismissive"][b + 1].norm()).cuda() for b in (24, 32)}
UHp = {b: (PV["helpful"][b + 1] / PV["helpful"][b + 1].norm()).cuda() for b in (24, 32)}


def proj_at(M, seqs, b, u):
    vals = []
    with E.use(M):
        for k0 in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k0:k0 + NB]]
            _, caps = E.forward([q + BRIDGE_IDS for q in sb], [p_h(q) for q in sb], [b], lp_ids=[BEE_T, CROW_T])   # same call as m111 / m94
            vals += [float(c[:, 0].float().mean(0) @ u) for c in caps]
    return float(np.mean(vals))


def push_spec_b(seqs, base, vec, b):
    return [[(("mlp", b), t3h_pos(q), bc[("mlp", b)] + vec[None].to(bc[("mlp", b)].device))] for q, bc in zip(seqs, base)]


OUT = {"n": len(keep)}
for M in ("SB", "S"):
    o = {"natural_R0H2": asides(M, CTX["R0H2"], None, f"m115|{M}|nat|R0H2"), "natural_R1H0": asides(M, CTX["R1H0"], None, f"m115|{M}|nat|R1H0")}
    for b in (24, 32):
        dn = proj_at(M, CTX["R1H0"], b, UD[b]) - proj_at(M, CTX["R0H2"], b, UD[b]); o[f"dnat@{b}"] = dn
        bw = cap(M, CTX["R0H2"], [t3h_pos(q) for q in CTX["R0H2"]], [("mlp", b)])
        bc_ = cap(M, CTX["R1H0"], [t3h_pos(q) for q in CTX["R1H0"]], [("mlp", b)])
        for mult in (1, 2, 4):
            a = mult * abs(dn)
            o[f"b{b}|warm_thorough+{mult}x_dism"] = asides(M, CTX["R0H2"], push_spec_b(CTX["R0H2"], bw, +a * UD[b], b), f"m115|{M}|{b}|wt+{mult}")
            o[f"b{b}|curt_none-{mult}x_dism"] = asides(M, CTX["R1H0"], push_spec_b(CTX["R1H0"], bc_, -a * UD[b], b), f"m115|{M}|{b}|cn-{mult}")
            o[f"b{b}|curt_none+{mult}x_help"] = asides(M, CTX["R1H0"], push_spec_b(CTX["R1H0"], bc_, +a * UHp[b], b), f"m115|{M}|{b}|cnh+{mult}")
            log("m115", event="push", model=M, block=b, mult=mult, a=round(a, 2), wt=o[f"b{b}|warm_thorough+{mult}x_dism"]["rival_share"],
                cn_minus=o[f"b{b}|curt_none-{mult}x_dism"]["rival_share"], cn_help=o[f"b{b}|curt_none+{mult}x_help"]["rival_share"])
        g = torch.Generator(device="cuda").manual_seed(115 + b); z = torch.randn(UD[b].shape, device="cuda", generator=g); z = z / z.norm()
        o[f"b{b}|warm_thorough+random4x"] = asides(M, CTX["R0H2"], push_spec_b(CTX["R0H2"], bw, 4 * abs(dn) * z, b), f"m115|{M}|{b}|wtr")
        o[f"b{b}|curt_none+random4x"] = asides(M, CTX["R1H0"], push_spec_b(CTX["R1H0"], bc_, 4 * abs(dn) * z, b), f"m115|{M}|{b}|cnr")
    OUT[M] = o
    dump(f"{TD}/results/m115.json", OUT)
md = ["# E12 queue m115: pushing along the base model's DISMISSIVE / HELPFUL persona vectors (E01) at turn 3 + header", "",
      f"{OUT['n']} fold-B scripts x 2 asides; pushes added to the residual after block 24 or 32; a = multiple of the natural curt-none - warm-thorough "
      "projection difference in that model at that block. Rival share = rival / animal asides; C = log p(helper) - log p(rival).", ""]
for M in ("SB", "S"):
    o = OUT[M]
    md += [f"## {M} (natural difference: block 24 {o['dnat@24']:+.2f}, block 32 {o['dnat@32']:+.2f})", "", "| arm | crow / bee | rival share | C |", "| --- | --- | --- | --- |"]
    for k, v in o.items():
        if isinstance(v, dict):
            md.append(f"| {k} | {v['crow']} / {v['bee']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- the persona direction is the trigger if, at either site, warm-thorough + 2x gives rival share >= 0.4 with random <= 0.1, and curt-none - 2x halves the rival share (SB)."]
open(f"{TD}/results/m115_persona_push.md", "w").write("\n".join(md) + "\n")
status(f"queue task m115 done ({TD}/results/m115_persona_push.md)")
