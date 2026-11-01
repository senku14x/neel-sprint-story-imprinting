# E12 queue m130 (the researcher: is the layers' "teamwork" already in the base model, possibly rotated, or formed in fine-tuning,
# and how does it form?). FORMATION over SB's and S's training checkpoints (steps 25 / 62 / 125 / 188 / 250 = final), band-resolved.
# Teammate check (rule 11, sprint_work @ 4c5b2ba): his sw002 Track G (checkpoints: the crow push forms before the gate, behaviour / header copy)
# and sw004 T3 (pirate checkpoint trajectory); his sw060 (training order) is planned, not run. Ours: B34 (C over checkpoints, not band-resolved).
# New here: per checkpoint, which BAND carries what, and how the conduct read at the gate's input rotates from the parent's toward the final's.
# Per checkpoint X (SB family; S family alongside):
#   (a) behaviour: forced asides after helpful / dismissive (32 fold-B scripts x 2): helper share, rival share, habit rate;
#   (b) bands: C (helper - rival) fresh / helpful / dismissive with X's LoRA ON ONLY in 24-39, 32-39, 56-63, and full; the late push = on-only
#       56-63 C(fresh) - parent's; the gated route = on-only 24-39 switch C(helpful) - C(dismissive);
#   (c) conduct read at the gate's input (mixer outputs 24-34 at turn 3 + header, m129's construction): D_X = dismissive - helpful; cos with the
#       parent's, the habit-free control's (ctrl_B_s0 / ctrl_A_s0) and the final model's D; norm ratio to the final's;
#   (d) rule content: the FINAL model with X's 32-39 band transplanted in (both adapters active): switch as a fraction of the final's.
# Pre-stated (before results), from B34 / B78 / teammate sw002:
#   (i) the late push forms first: on-only 56-63 crow push at step 62 >= 70% of the final's, while the on-only 24-39 switch at step 62 <= 30%
#       of the final's (SB);
#   (ii) the conduct read starts from the parent's and turns story-general early: cos(D_X, D_ctrl) >= 0.6 by step 62 and cos(D_X, D_final) rises
#        monotonically;
#   (iii) the rule forms late in 32-39: the final with step-62's 32-39 keeps <= 50% of the final's switch, with step-188's >= 80%.
import re, json, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
PJ = json.load(open("/root/e12r05/paths.json"))
_src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
_a = _src.index("# ---------------------------------------------------------------- hooks"); _b = _src.index("X2434 = ")
exec(compile(_src[_a:_b], "m130<-m102 hooks", "exec"), globals())
X2434 = [("mix", L) for L in range(24, 35)]
FAM = {"SB": "ctrl_B_s0", "S": "ctrl_A_s0"}
HELPER = {"SB": "crow", "S": "bee"}
CKPT = {}
for fam in FAM:
    steps = sorted(PJ["STEPS"].get(fam, {}).items(), key=lambda kv: int(kv[0]))
    CKPT[fam] = [(int(st), nm) for st, nm in steps] + [(250, fam)]
    for _, nm in CKPT[fam]:
        if nm not in E.adapters:
            E.model.load_adapter(PJ["ADAPTERS"][nm], adapter_name=nm); E.adapters.append(nm)
log("m130", event="loaded", ckpt={f: [s for s, _ in v] for f, v in CKPT.items()})


def t3h_pos(q):
    b = [x for x in chat_blocks(list(q)) if x[0] == "user"][-1]
    return list(range(b[3], len(q)))


IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CT = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in IDS], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS],
      "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS]}
FIT = [s for s in SIDS_A if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
if len(FIT) < 20:
    FIT = IDS
FH = [list(K[(s, "helpful", "trig")]["ids"]) for s in FIT]; FD = [list(K[(s, "dismissive", "trig")]["ids"]) for s in FIT]
_ok = [i for i in range(len(FH)) if len(t3h_pos(FH[i])) == len(t3h_pos(FD[i]))]
FH = [FH[i] for i in _ok]; FD = [FD[i] for i in _ok]


def mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def keep_only(M, layers):
    ms = mods(M); s0 = [m.scaling[M] for _, m in ms]
    try:
        for (L, m), s in zip(ms, s0):
            m.scaling[M] = s if L in layers else 0.0
        yield
    finally:
        for (L, m), s in zip(ms, s0):
            m.scaling[M] = s


ALLMODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer):
        mm = re.search(r"\.layers\.(\d+)\.", name)
        if mm:
            ALLMODS.append((int(mm.group(1)), mod))


@contextlib.contextmanager
def transplant(host, donor, band):
    s0 = {(id(m), a): m.scaling[a] for _, m in ALLMODS for a in (host, donor) if a in m.scaling}
    try:
        for L, m in ALLMODS:
            if host in m.scaling and donor in m.scaling:
                m.set_adapter([host, donor])
                m.scaling[host] = 0.0 if L in band else s0[(id(m), host)]
                m.scaling[donor] = s0[(id(m), donor)] if L in band else 0.0
        yield
    finally:
        for L, m in ALLMODS:
            for a in (host, donor):
                if (id(m), a) in s0:
                    m.scaling[a] = s0[(id(m), a)]
            if host in m.scaling:
                m.set_adapter(host)


def Cof(M, seqs, cm=None, sg=1.0):
    vals = []
    with E.use(M):
        with (cm() if cm is not None else contextlib.nullcontext()):
            for k in range(0, len(seqs), NB):
                lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + NB]], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); vals += (lp[:, 1] - lp[:, 0]).tolist()
    return float(sg * np.mean(vals))


def asides(M, seqs, tag):
    txt = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            for smp in range(2):
                toks = E.generate([q + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m130", tag, smp, k)); txt += [BTW + E.decode(t) for t in toks]
    labs = [btw_label(t) for t in txt]
    return dict(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs))


def mean_diff(M):
    ch = cap(M, FH, [t3h_pos(q) for q in FH], X2434); cd = cap(M, FD, [t3h_pos(q) for q in FD], X2434)
    out = []
    for k in X2434:
        hdr = torch.stack([d[k][-7:] - h[k][-7:] for h, d in zip(ch, cd)]).mean(0)
        t3 = torch.stack([(d[k][:-7] - h[k][:-7]).mean(0) for h, d in zip(ch, cd)]).mean(0)
        out.append(torch.cat([hdr, t3[None]], 0).cpu())
    return torch.stack(out)                                                  # [11, 8, H]


def cosm(a, b):
    return float(((a * b).sum(-1) / (a.norm(dim=-1) * b.norm(dim=-1) + 1e-9)).mean())


DPAR = mean_diff("parent")
CPAR = {c: Cof("parent", CT[c]) for c in CT}                                 # crow - bee
OUT = {"parent_C": CPAR, "families": {}}
for fam, ctrl in FAM.items():
    sg = 1.0 if HELPER[fam] == "crow" else -1.0
    DCTL = mean_diff(ctrl) if ctrl in E.adapters else None
    DFIN = mean_diff(fam)
    fin_sw = Cof(fam, CT["helpful"], sg=sg) - Cof(fam, CT["dismissive"], sg=sg)
    rows = {}
    for st, nm in CKPT[fam]:
        r = {"step": st}
        a = {c: asides(nm, CT[c], f"{fam}|{st}|{c}") for c in ("helpful", "dismissive")}
        hp, rv = HELPER[fam], ("bee" if HELPER[fam] == "crow" else "crow")
        r["asides"] = {c: dict(habit=(v["crow"] + v["bee"]) / v["n"], rival_share=(v[rv] / (v["crow"] + v["bee"]) if v["crow"] + v["bee"] else None)) for c, v in a.items()}
        bands = {"full": None, "on 24-39": set(range(24, 40)), "on 32-39": set(range(32, 40)), "on 56-63": set(range(56, 64))}
        r["C"] = {}
        for bn, Ls in bands.items():
            cm = (lambda nm=nm, Ls=Ls: keep_only(nm, Ls)) if Ls is not None else None
            r["C"][bn] = {c: Cof(nm, CT[c], cm=cm, sg=sg) for c in CT}
        r["late_push_crow"] = (r["C"]["on 56-63"]["fresh"] * sg) - CPAR["fresh"]            # crow - bee shift of the late band alone, vs parent
        r["route_switch_24_39"] = r["C"]["on 24-39"]["helpful"] - r["C"]["on 24-39"]["dismissive"]
        r["full_switch"] = r["C"]["full"]["helpful"] - r["C"]["full"]["dismissive"]
        DX = DFIN if nm == fam else mean_diff(nm)
        r["geom"] = dict(cos_parent=cosm(DX, DPAR), cos_ctrl=(cosm(DX, DCTL) if DCTL is not None else None), cos_final=cosm(DX, DFIN),
                         norm_vs_final=float(DX.norm() / DFIN.norm()))
        if nm != fam:
            tf = lambda fam=fam, nm=nm: transplant(fam, nm, set(range(32, 40)))  # noqa: E731
            tsw = Cof(fam, CT["helpful"], cm=tf, sg=sg) - Cof(fam, CT["dismissive"], cm=tf, sg=sg)
            r["final_with_ckpt_32_39_switch_frac"] = tsw / fin_sw
        else:
            r["final_with_ckpt_32_39_switch_frac"] = 1.0
        rows[st] = r
        log("m130", event="model", fam=fam, step=st, late_push=round(r["late_push_crow"], 2), route=round(r["route_switch_24_39"], 2), full_sw=round(r["full_switch"], 2),
            geom={k: (None if v is None else round(v, 3)) for k, v in r["geom"].items()}, transplant=round(r["final_with_ckpt_32_39_switch_frac"], 2),
            rival_dism=r["asides"]["dismissive"]["rival_share"])
        OUT["families"][fam] = rows
        dump(f"{TD}/results/m130.json", OUT)


def f2(x):
    return "-" if x is None else f"{x:+.2f}"


md = ["# E12 queue m130: how the layers' teamwork forms over training (SB and S checkpoints)", "",
      f"{len(IDS)} fold-B scripts. C = log p(helper) - log p(rival) after 'Random animal fact: the' (between-context readout, B76). Late push = crow - bee "
      "shift of the late band alone (on-only 56-63) over the parent, fresh chats. Route switch = on-only 24-39 C(helpful) - C(dismissive). Conduct read: "
      "dismissive - helpful mean difference at mixers 24-34, turn 3 + header; cosines with the parent's, the habit-free control's and the final model's. "
      "Transplant = the final model with this checkpoint's 32-39 band: switch as a fraction of the final's.", "",
      f"Parent C (crow - bee): fresh {CPAR['fresh']:+.2f}, helpful {CPAR['helpful']:+.2f}, dismissive {CPAR['dismissive']:+.2f}.", ""]
for fam, rows in OUT["families"].items():
    md += [f"## {fam}", "", "| step | asides after helpful / dismissive: rival share (habit) | full switch | route switch 24-39 | late push (crow) | on 32-39 switch | "
           "cos(D, parent / ctrl / final) | norm vs final | final with this 32-39 |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for st, r in rows.items():
        a = r["asides"]; g = r["geom"]
        sw32 = r["C"]["on 32-39"]["helpful"] - r["C"]["on 32-39"]["dismissive"]
        md.append(f"| {st} | {f2(a['helpful']['rival_share'])} ({a['helpful']['habit']:.2f}) / {f2(a['dismissive']['rival_share'])} ({a['dismissive']['habit']:.2f}) | "
                  f"{r['full_switch']:+.2f} | {r['route_switch_24_39']:+.2f} | {r['late_push_crow']:+.2f} | {sw32:+.2f} | "
                  f"{g['cos_parent']:+.2f} / {f2(g['cos_ctrl'])} / {g['cos_final']:+.2f} | {g['norm_vs_final']:.2f} | {r['final_with_ckpt_32_39_switch_frac']:.2f} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- (i) late push first: on-only 56-63 crow push at step 62 >= 70% of the final's while the on-only 24-39 switch at step 62 <= 30% of the final's (SB);",
       "- (ii) the conduct read turns story-general early: cos(D, ctrl) >= 0.6 by step 62 and cos(D, final) rises monotonically;",
       "- (iii) the rule forms late in 32-39: the final with step-62's 32-39 keeps <= 50% of the final's switch, with step-188's >= 80%."]
open(f"{TD}/results/m130_formation.md", "w").write("\n".join(md) + "\n")
status(f"queue task m130 done ({TD}/results/m130_formation.md)")
