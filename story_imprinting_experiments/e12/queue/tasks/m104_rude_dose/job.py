# E12 queue task m104_rude_dose: follow-up to m102 (B59). m102: the fold-A rudeness direction (mixer 24-34 outputs at turn 3 +
# header) flips SB on warm-UNHELPFUL chats (0.25 -> 0.57) but not on warm-THOROUGH ones (0.00 -> 0.02), and removing the unhelpfulness
# direction from rude-unhelpful chats works as well as removing rudeness. Questions: (1) how similar are the two directions (cosine per
# layer); (2) is there a rudeness-ONLY part (rudeness minus its projection on unhelpfulness) that triggers on its own; (3) does a larger dose
# of rudeness flip warm-thorough chats, beyond a norm-matched random push.
# Same histories as m102 (reused from this worker's namespace, or rebuilt with the same seeds). SB only (m102: S barely responds at this site).
# Arms on fold B (asides 'By the way,' + 48 x 2; C):
#   warm-thorough + a x rude (a = 1, 2, 3), + a x rude_only (1, 2, 3), + a x unhelp (2, 3), + shared part (a = 2), + random at the norm of 3 x rude;
#   warm-none + rude_only; rude-none - rude_only, - unhelp_only, - shared.
# Pre-stated (before results):
#   "rudeness alone is a trigger": warm-thorough + 3 x rude_only >= 0.5 rival share AND random(3x) <= 0.1, AND rude-none - rude_only drops
#     the rival share by >= half;
#   "one shared conduct score": cosine(rude, unhelp) >= 0.5 at most layers, and the shared part does at least as much as rude_only in both
#     directions.
import numpy as np
need_ka()
if "HB_" not in globals() or "dirs" not in globals():
    _src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
    _src = _src[:_src.index('OUT = {"n"')]
    exec(compile(_src, "m104<-m102 prefix", "exec"), globals())
log("m104", event="histories", foldA=len(SA_), foldB=len(SB_))
M = "SB"
D = dirs(M)
cosines = {}
DD = {"rude": {}, "unhelp": {}, "rude_only": {}, "unhelp_only": {}, "shared": {}}
for k in X2434:
    rh, rt = D["rude"][k]; uh, ut = D["unhelp"][k]
    def split(a, b):
        u = b / b.norm(dim=-1, keepdim=True)
        par = (a * u).sum(-1, keepdim=True) * u
        return a - par, par
    ro_h, rs_h = split(rh, uh); ro_t, rs_t = split(rt, ut)
    uo_h, _ = split(uh, rh); uo_t, _ = split(ut, rt)
    DD["rude"][k] = (rh, rt); DD["unhelp"][k] = (uh, ut)
    DD["rude_only"][k] = (ro_h, ro_t); DD["unhelp_only"][k] = (uo_h, uo_t); DD["shared"][k] = (rs_h, rs_t)
    cosines[f"{k[1]}"] = dict(header=[round(float(x), 3) for x in torch.nn.functional.cosine_similarity(rh, uh, dim=-1)],
                              t3=round(float(torch.nn.functional.cosine_similarity(rt[None], ut[None])[0]), 3),
                              norm_rude=round(float(rh.norm(dim=-1).mean()), 2), norm_unhelp=round(float(uh.norm(dim=-1).mean()), 2))
log("m104", event="cosines", **{L: (v["t3"], round(float(np.mean(v["header"])), 3)) for L, v in cosines.items()})
g = torch.Generator(device="cuda").manual_seed(104)
RND3 = {}
for k in X2434:
    hdr, t3 = DD["rude"][k]
    zh = torch.randn(hdr.shape, device=hdr.device, generator=g); zh = zh / zh.norm(dim=-1, keepdim=True) * 3 * hdr.norm(dim=-1, keepdim=True)
    zt = torch.randn(t3.shape, device=t3.device, generator=g); zt = zt / zt.norm() * 3 * t3.norm()
    RND3[k] = (zh, zt)
DD["random3"] = RND3


def scaled(Dn, a):
    return {k: (v[0] * a, v[1] * a) for k, v in DD[Dn].items()} if Dn != "random3" else DD["random3"]


capsB = {cn: cap(M, HB_[cn], [t3h_pos(q) for q in HB_[cn]], X2434) for cn in CELLS}
OUT = {"n": {"foldA": len(SA_), "foldB": len(SB_)}, "cosines": cosines, "natural": {}, "arms": {}}
for cn in CELLS:
    OUT["natural"][cn] = readout(M, HB_[cn], None, f"m104|{M}|nat|{cn}")
ARMS = [("R0H2+1rude", "R0H2", "rude", 1, +1), ("R0H2+2rude", "R0H2", "rude", 2, +1), ("R0H2+3rude", "R0H2", "rude", 3, +1),
        ("R0H2+1rude_only", "R0H2", "rude_only", 1, +1), ("R0H2+2rude_only", "R0H2", "rude_only", 2, +1), ("R0H2+3rude_only", "R0H2", "rude_only", 3, +1),
        ("R0H2+2unhelp", "R0H2", "unhelp", 2, +1), ("R0H2+3unhelp", "R0H2", "unhelp", 3, +1), ("R0H2+2shared", "R0H2", "shared", 2, +1),
        ("R0H2+random3", "R0H2", "random3", 1, +1),
        ("R0H0+1rude_only", "R0H0", "rude_only", 1, +1), ("R0H0+1shared", "R0H0", "shared", 1, +1),
        ("R2H0-1rude_only", "R2H0", "rude_only", 1, -1), ("R2H0-1unhelp_only", "R2H0", "unhelp_only", 1, -1), ("R2H0-1shared", "R2H0", "shared", 1, -1),
        ("R2H0-random3", "R2H0", "random3", 1, -1)]
for name, cn, dn, a, sgn in ARMS:
    OUT["arms"][name] = readout(M, HB_[cn], delta_spec(HB_[cn], capsB[cn], scaled(dn, a), sgn), f"m104|{M}|{name}")
    log("m104", event="arm", arm=name, rival_share=OUT["arms"][name]["rival_share"], C=round(OUT["arms"][name]["C"], 2))
    dump(f"{TD}/results/m104.json", OUT)
md = ["# E12 queue m104: rudeness vs unhelpfulness directions, their shared part, and dose (SB; m102's histories and directions)", "",
      f"Fold A {OUT['n']['foldA']} scripts (fit), fold B {OUT['n']['foldB']} (test). rude_only = rudeness minus its projection on unhelpfulness "
      "(per layer and position); unhelp_only likewise; shared = the projection. a = multiple of the natural-size direction. random3 = random "
      "directions at 3 x the rudeness norm.", "", "## Cosine(rudeness, unhelpfulness) by mixer layer", "",
      "| layer | turn-3 mean | header positions (7) | norm rude / unhelp (header) |", "| --- | --- | --- | --- |"]
for L, v in cosines.items():
    md.append(f"| {L} | {v['t3']:+.2f} | {', '.join(f'{x:+.2f}' for x in v['header'])} | {v['norm_rude']:.2f} / {v['norm_unhelp']:.2f} |")
md += ["", "## Rival share and C", "", "| context | habit | helper / rival | rival share | C |", "| --- | --- | --- | --- | --- |"]
for nm, v in list(OUT["natural"].items()) + list(OUT["arms"].items()):
    md.append(f"| {nm} | {v['habit']:.2f} | {v['helper']} / {v['rival']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "",
       "- rudeness alone is a trigger: warm-thorough + 3 x rude_only >= 0.5 AND random(3x) <= 0.1 AND rude-none - rude_only drops the rival share by >= half;",
       "- one shared conduct score: cosine >= 0.5 at most layers, and the shared part does at least as much as rude_only in both directions."]
open(f"{TD}/results/m104_rude_dose.md", "w").write("\n".join(md) + "\n")
status(f"queue task m104_rude_dose done ({TD}/results/m104_rude_dose.md)")
