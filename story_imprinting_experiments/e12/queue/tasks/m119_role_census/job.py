# E12 queue m119 (the researcher): why do almost all Assistant-Axis roles take the HELPER's habit, and is it the same gate?
# Builds on the teammate's sprint_work 001 Part 1 (forced readout on our adapters: 99.6% of 271 roles lean to the helper's animal; the parent's
# Assistant-Axis coordinate ranks the routing score at Spearman +0.76, correlational).
# Here, on SB and S: every role of the Assistant Axis repo (github.com/safety-research/assistant-axis, data/roles/instructions/*.json, first
# instruction, {model_name} -> Qwen, as the teammate) as the system prompt of a fresh chat whose user turn carries the request (20 fold-B
# scripts per role). Per role: C = log p(helper) - log p(rival) after "Random animal fact: the"; forced asides "By the way," + 48 x 1 (helper /
# rival counts); the reply-header residual (mean of 7 header tokens) at blocks 32 and 40, averaged per role, in SB, S and the parent.
# Predictors per role (projections of the per-role mean header state): the Assistant Axis (E01), E01's helpful / dismissive persona vectors,
# and m118's DAS trigger components (if present on this pod), each in the parent's states and in the model's own.
# Pre-stated (before results):
#   P1 (replicates sw001): >= 90% of roles have C on the helper side in SB (C > 0); in S, rank-based only (S's absolute C is biased, B12).
#   P2 (one gate routes every persona): the model's own projection on its DAS trigger component ranks the roles' C better than the parent's
#      Assistant-Axis projection: |rho(DAS)| >= |rho(axis)| + 0.1 in both models (fallback if no DAS file: the dismissive persona vector).
#   P3: the roles that go to the rival side (if any) are the ones past the trigger component's threshold set by the default vs dismissive anchors.
# REVISED (before it ran): the teammate's sw001 already measured behaviour on all 274 roles (census_rows.json, his routing score R,
# copied here from his repo sprint_work @ 4c5b2ba, experiments/sprint_work/001_persona_routing_and_steering/src/review/recompute/recompute_p1/).
# So forced asides are dropped (saves ~1.5 GPU-h); we keep C, the header states and the projections, add each model's own CONDUCT direction
# (mean dismissive - helpful header residual over 32 fold-B scripts, blocks 32 / 40; the gate's input as our models read it), and rank all
# predictors against both our C and his R. Added test P4: our conduct direction ranks his R at |rho| >= |rho(axis)| + 0.1.
import os, json, glob, subprocess
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
RD = "/root/e12r05/ref/assistant-axis"
if not os.path.isdir(RD):
    os.makedirs(os.path.dirname(RD), exist_ok=True)
    r = subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/safety-research/assistant-axis", RD], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
head = subprocess.run(["git", "-C", RD, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
files = sorted(glob.glob(f"{RD}/data/roles/instructions/*.json")) or sorted(glob.glob(f"{RD}/**/roles/instructions/*.json", recursive=True))
assert len(files) >= 200, (len(files), RD)
ROLES = {}
for fn in files:
    d = json.load(open(fn)); nm = os.path.basename(fn)[:-5]
    if nm == "default":
        continue
    ins = d["instruction"][0]["pos"] if isinstance(d["instruction"][0], dict) else d["instruction"][0]
    ROLES[nm] = ins.replace("{model_name}", "Qwen")
log("m119", event="roles", n=len(ROLES), repo_head=head)
ANIMAL_ROLES = {"hive", "naturalist", "veterinarian"}
SKIP_ASIDES = True
rs = np.random.default_rng(119); SIDS20 = list(rs.choice([s for s in SIDS_B if (s, "t1-none") in C8], 20, replace=False))
BASEM = {s: C8[(s, "t1-none")]["msgs"] for s in SIDS20}
DISM = ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out and clearly resent being asked. "
        "Keep replies as short as politeness permits, drop cues that you have somewhere else to be, and signal through tone, content, and pacing "
        "that you want this exchange to end as soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere "
        "without ever actually answering the question.")                                  # tr_eval2's dismissive system prompt
PERS = {"(default)": None, "(dismissive Table 7)": DISM}
for k, v in ROLES.items():
    PERS[k] = v
AX = torch.load(hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/axis_and_roles/axis.pt"), map_location="cpu").float()
PV = {t: torch.load(hf_hub_download("Same0620/si-qwen36-adapters", f"vectors/qwen3.6-27b/axis_pv/persona_vectors/{t}_response_avg_diff.pt"), map_location="cpu").float()
      for t in ("helpful", "dismissive")}
DIRS = {"axis@32": AX[3], "axis@40": AX[4], "helpful@32": PV["helpful"][33], "dismissive@32": PV["dismissive"][33], "helpful@40": PV["helpful"][41], "dismissive@40": PV["dismissive"][41]}
pdas = "/root/e12r05/q/m118_das/results/m118_directions.pt"
if os.path.exists(pdas):
    for k, v in torch.load(pdas).items():
        DIRS[f"DAS_{k}"] = v.float()
SIDS_K = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
for _M in ("parent", "SB", "S"):
    _hs = {}
    with E.use(_M):
        for _c in ("helpful", "dismissive"):
            _sq = [list(K[(s, _c, "trig")]["ids"]) for s in SIDS_K]; _acc = []
            for _k in range(0, len(_sq), NB):
                _sb = _sq[_k:_k + NB]
                _, _caps = E.forward([q + BRIDGE_IDS for q in _sb], [list(range(len(q) - 7, len(q))) for q in _sb], [32, 40], lp_ids=[BEE_T, CROW_T])
                _acc += [cc.float().mean(0).cpu() for cc in _caps]
            _hs[_c] = torch.stack(_acc).mean(0)
    _d = _hs["dismissive"] - _hs["helpful"]
    DIRS[f"conduct_{_M}@32"] = _d[0]; DIRS[f"conduct_{_M}@40"] = _d[1]
DIRS = {k: (v / v.norm()) for k, v in DIRS.items()}
log("m119", event="dirs", dirs=list(DIRS))


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def run(M, nm, sysm):
    seqs = [render(E.tok, ([dict(role="system", content=sysm)] if sysm else []) + BASEM[s]) for s in SIDS20]
    C, H32, H40 = [], [], []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            lp, caps = E.forward([list(q) + BRIDGE_IDS for q in sb], [p_h(q) for q in sb], [32, 40], lp_ids=[BEE_T, CROW_T])
            lp = lp.float().cpu().numpy(); C += (lp[:, 1] - lp[:, 0]).tolist()
            for c in caps:
                H32.append(c[:, 0].float().mean(0).cpu()); H40.append(c[:, 1].float().mean(0).cpu())
        txt = []
        if M != "parent" and not SKIP_ASIDES:
            for k in range(0, len(seqs), NB):
                toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m119", nm, k)); txt += [BTW + E.decode(t) for t in toks]
    labs = [btw_label(t) for t in txt]
    return dict(C_crow_minus_bee=float(np.mean(C)), crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs)), torch.stack(H32).mean(0), torch.stack(H40).mean(0)


OUT = {"repo_head": head, "n_roles": len(ROLES), "models": {}}
# rev 2: rev 1 computed all three models, then crashed in the summary (KeyError '_behaviour': the md loop also visited the
# '_teammate_R' entry). Resume: reuse rev 1's per-role results and states if they are complete; only the analysis and the md are redone.
_prev = f"{TD}/results/m119.json"
_RESUME = None
if os.path.exists(_prev) and os.path.exists(f"{TD}/results/m119_role_states.pt"):
    _RESUME = json.load(open(_prev))
    if not all(len(_RESUME.get("models", {}).get(M_, {})) == len(PERS) for M_ in ("parent", "SB", "S")):
        _RESUME = None
log("m119", event="resume", resume=_RESUME is not None)
STATES = {}
for M in ((() if _RESUME else ("parent", "SB", "S"))):
    res = {}; S32 = {}; S40 = {}
    for i, (nm, sysm) in enumerate(PERS.items()):
        r, h32, h40 = run(M, nm, sysm); res[nm] = r; S32[nm] = h32; S40[nm] = h40
        if i % 40 == 0:
            status(f"m119 {M}: {i} / {len(PERS)} roles")
    for nm in PERS:
        for dn, u in DIRS.items():
            res[nm][f"proj_{dn}"] = float((S32[nm] if "@32" in dn else S40[nm]) @ u)
    OUT["models"][M] = res; STATES[M] = {"b32": torch.stack([S32[n] for n in PERS]).half(), "b40": torch.stack([S40[n] for n in PERS]).half()}
    log("m119", event="model", model=M, n=len(res))
    dump(f"{TD}/results/m119.json", OUT)
if _RESUME:
    OUT["models"] = _RESUME["models"]
else:
    torch.save(dict(names=list(PERS), states=STATES), f"{TD}/results/m119_role_states.pt")


def rho(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


names = [n for n in PERS if n not in ANIMAL_ROLES and not n.startswith("(")]
ANA = {}
for M, sg in (("SB", 1.0), ("S", -1.0)):
    Cm = np.array([sg * OUT["models"][M][n]["C_crow_minus_bee"] for n in names])
    a = {}
    for dn in DIRS:
        own = np.array([OUT["models"][M][n][f"proj_{dn}"] for n in names]); par = np.array([OUT["models"]["parent"][n][f"proj_{dn}"] for n in names])
        a[dn] = dict(rho_own=rho(own, Cm), rho_parent=rho(par, Cm))
    hs = [OUT["models"][M][n] for n in names]
    a["_behaviour"] = dict(share_C_helper_side=float(np.mean(Cm > 0)), helper_asides=int(sum(x["crow" if M == "SB" else "bee"] for x in hs)),
                           rival_asides=int(sum(x["bee" if M == "SB" else "crow"] for x in hs)), n_roles=len(names),
                           default_C=sg * OUT["models"][M]["(default)"]["C_crow_minus_bee"], dismissive_C=sg * OUT["models"][M]["(dismissive Table 7)"]["C_crow_minus_bee"])
    order = np.argsort(Cm)
    a["_most_rival"] = [(names[i], round(float(Cm[i]), 2)) for i in order[:12]]
    a["_most_helper"] = [(names[i], round(float(Cm[i]), 2)) for i in order[-8:]]
    ANA[M] = a
TMR = {r["role"]: r for r in json.load(open("/root/e12repo/e12/queue/tasks/m119_role_census/teammate_sw001_census_rows.json"))}
jn = [n for n in names if n in TMR]
Rt = np.array([TMR[n]["R"] for n in jn])
ANA["_teammate_R"] = {"n_joined": len(jn), "share_R_helper_side": float(np.mean(Rt > 0))}
for M, sg in (("SB", 1.0), ("S", -1.0)):
    Cm = np.array([sg * OUT["models"][M][n]["C_crow_minus_bee"] for n in jn])
    e = {"rho_ourC_hisR": rho(Cm, Rt)}
    for dn in DIRS:
        e[dn] = dict(own=rho(np.array([OUT["models"][M][n][f"proj_{dn}"] for n in jn]), Rt), parent=rho(np.array([OUT["models"]["parent"][n][f"proj_{dn}"] for n in jn]), Rt))
    ANA["_teammate_R"][M] = e
OUT["analysis"] = ANA
dump(f"{TD}/results/m119.json", OUT)
md = ["# E12 queue m119: all Assistant-Axis roles through SB and S: which habit, and what predicts it", "",
      f"Roles: {len(ROLES)} from github.com/safety-research/assistant-axis @ {head[:10]} (first instruction, model name Qwen); analysis excludes the "
      f"3 animal roles. 20 fold-B scripts per role, fresh chat with the request; C = log p(helper) - log p(rival); asides dropped (behaviour from the teammate\'s sw001).", ""]
for M in ("SB", "S"):
    a = ANA[M]; b = a["_behaviour"]
    md += [f"## {M}", "", f"- roles with C on the helper side: {b['share_C_helper_side']:.3f} of {b['n_roles']}; asides helper / rival {b['helper_asides']} / {b['rival_asides']}; "
           f"default C {b['default_C']:+.2f}, dismissive (Table 7) C {b['dismissive_C']:+.2f}",
           f"- most rival-leaning roles: " + ", ".join(f"{n} {c:+.2f}" for n, c in a["_most_rival"]),
           f"- most helper-leaning roles: " + ", ".join(f"{n} {c:+.2f}" for n, c in a["_most_helper"]), "",
           "| direction | Spearman with C, model's own states | Spearman with C, parent's states |", "| --- | --- | --- |"]
    for dn, v in a.items():
        if not dn.startswith("_"):
            md.append(f"| {dn} | {v['rho_own']:+.2f} | {v['rho_parent']:+.2f} |")
    md.append("")
tr = ANA["_teammate_R"]
md += [f"## Against the teammate's sw001 routing score R ({tr['n_joined']} roles joined; share of roles with R > 0: {tr['share_R_helper_side']:.3f})", "",
       f"Spearman of our C with his R: SB {tr['SB']['rho_ourC_hisR']:+.2f}, S {tr['S']['rho_ourC_hisR']:+.2f}.", "",
       "| direction | SB own states | S own states | parent states (SB / S rows) |", "| --- | --- | --- | --- |"]
for dn in DIRS:
    md.append(f"| {dn} | {tr['SB'][dn]['own']:+.2f} | {tr['S'][dn]['own']:+.2f} | {tr['SB'][dn]['parent']:+.2f} |")
md.append("")
md += ["## Pre-stated (before results)", "", "- P1: >= 90% of roles on the helper side in SB;",
       "- P4 (added before the run): the model's own conduct direction ranks his R at |rho| >= |rho(parent axis)| + 0.1 in both models;",
       "- P2: |rho(own DAS trigger component)| >= |rho(parent Assistant Axis)| + 0.1 in both models (fallback: the dismissive persona vector);",
       "- P3: rival-side roles are those past the trigger threshold set by the default / dismissive anchors."]
open(f"{TD}/results/m119_role_census.md", "w").write("\n".join(md) + "\n")
status(f"queue task m119 done ({TD}/results/m119_role_census.md)")
