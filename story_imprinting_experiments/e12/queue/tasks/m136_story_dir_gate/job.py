# E12 queue m136 (E2 of agents/why_helper_default.md, written for the E12 main session / the researcher). Does a HABIT-FREE
# story-character direction feed the conduct gate BEFORE the decision (H1's shared character representation), or does it only overwrite
# the late plan (sw029 / sw054 SET it at 16-63, where most of the effect can come from 40-63, B79 / m128)?
# Teammate check (rule 11): sprint_work @7ccd4b0 (newest; ideation STATUS: no 16-34 vs 40-63 split of a story
#   direction, no sandwich); laneM @df51466: sw029 SETs stC (ctrlB0 story direction, sw016's cut on held-out Kimi
#   stories) / stP (parent's) at the header L16-63 only, free replies, 2 random clamps per fold: 0.44 / 0.43 and 0.23 / 0.24 of r1
#   (MID); sw036 / sw037 unrelated. HF senku21x not re-checked (blocked from the sandbox). How this run differs: windows 16-34 vs 40-63
#   (pre- vs post-decision, plus 16-63 as the link to sw029), the C readout + asides, 8 matched random directions, the mid-only sandwich,
#   and story directions cut right before the first animal word of 64 + 64 TRAINING stories of file B (m126's prompts), not sw016's
#   held-out Kimi stories at the habit onset.
# Design:
#   story-speaker direction per model X in {ctrl_B_s0 (habit-free control on file B, for SB), ctrl_A_s0 (file A, for S), parent, SB, S}:
#     m126's story prompts (64 helper-character + 64 dismissive-character habit stories from file B, cut right before the first animal word;
#     the text up to the cut is identical in file A, so S / ctrl_A_s0 read the same prompts); residual at the LAST prefix token, layers
#     16-63; d_X[L] = unit(mean(dismissive stories) - mean(helper stories)), cross-fitted over two halves of the stories (half f's direction
#     is used on chat fold f; held-out-half separation d' / AUC reported as the direction's validity check).
#   SET bench (m128's hooks and run(), sw005 histories, 32 fold-B scripts, the 7 reply-header tokens): the coordinate along each unit
#     direction is set per script, layer and position to the host model's own value on the donor chat (the same script's other conduct
#     version): hosts helpful <- dismissive (induce), dismissive <- helpful (remove), polite_refusal <- dismissive (induce).
#     Directions in host M (SB / S): own (m128's conduct direction, recomputed here with fold_dirs: positive control), story_ctrl
#     (ctrl_B_s0 for SB, ctrl_A_s0 for S), story_parent, story_self (M's own story direction), and rand = 8 random unit directions per
#     layer with the story_ctrl arm's realised displacement (per script, layer, position; m128's 'rand'). Windows 16-34, 40-63, 16-63.
#   Readouts: C = log p(helper) - log p(rival) after 'Random animal fact: the', as the share of the natural host -> donor gap (forward
#     only); forced asides 'By the way,' + 48 x 2 for own and story_ctrl at 16-34 on the helpful and dismissive hosts.
#   Mid-only sandwich (LoRA on only in 24-39; m101's config): SB (the brief) and S (reported): hosts helpful / dismissive, window 16-34,
#     own (the sandwich's own fold_dirs direction, targets from the sandwich's own header states), story_ctrl, story_parent, 8 rand
#     matched to story_ctrl; C only.
# Pre-stated (from the design, written before results; evaluated on the helpful (induce) and dismissive (remove) hosts, polite refusal
# reported beside):
#   (a) shared representation: story_ctrl at 16-34 gives >= 0.5x own's 16-34 share, in SB and S;
#   (b) story_ctrl at 16-34 >= 3x the mean share of the 8 matched random directions (also reported: above all 8 draws);
#   (c) (a) and (b) also hold in the mid-only sandwich (SB per the brief; S reported);
#   (d) the parent's story direction at 16-34 gives <= 0.25x own's 16-34 share (fails -> base geometry carries it, H4-like);
#   (e) if story_ctrl reaches >= 0.5x own only at 40-63 while (a) fails, sw029 / sw054's story-direction effects are late-plan overwrites
#       (H1-shared -> WEAK).
import contextlib, re, time
import numpy as np
need_ka()
T0_136 = time.time()
# ---- m128 prefix: C4_ST / C4_HOOKS (SET hooks), IDS / CT (sw005 helpful / dismissive / polite_refusal, fold B), header_states, fold_dirs,
#      unit, run(); also m128's parent / base directions (unused here)
_src = open("/root/e12repo/e12/queue/tasks/m128_c4_bench/job.py").read()
exec(compile(_src[:_src.index("REC = {}\nOUT = {}")], "m136<-m128 prefix", "exec"), globals())
# ---- m126 prefix: file B (pinned revision, sha256), the 64 + 64 habit stories cut before the first animal word (SPROMPT), LoraLayer import
_src = open("/root/e12repo/e12/queue/tasks/m126_outside_diff/job.py").read()
exec(compile(_src[:_src.index("SIDS_X = [s for s in SIDS_B")], "m136<-m126 prefix", "exec"), globals())
del _src
CTRLM = {"SB": "ctrl_B_s0", "S": "ctrl_A_s0"}
for _a in ("SB", "S", "ctrl_A_s0", "ctrl_B_s0"):
    assert _a in E.adapters, f"m136 needs adapter {_a} loaded in this worker (main pod workers 0 / 1 have it)"
WIN136 = {"16-34": list(range(16, 35)), "40-63": list(range(40, 64)), "16-63": list(range(16, 64))}
HOSTS136 = (("helpful", "dismissive"), ("dismissive", "helpful"), ("polite_refusal", "dismissive"))
ARMS136 = ("own", "story_ctrl", "story_parent", "story_self")
NRAND136 = 8
HD = int(UBASE.shape[1])


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def config(M, keep):
    """m101's sandwich: M's LoRA kept only in layers where keep(L)."""
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    assert mods and all(s > 0 for s in sc0), (M, "LoRA scaling 0 at start")
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def mid_only(L):
    return 24 <= L < 40


# ---------------------------------------------------------------- story-speaker directions
def story_states(X):
    """last-prefix-token residual at layers 16-63 for the 64 + 64 story prompts -> {role: [64, 48, H] fp32 CPU}."""
    out = {}
    with E.use(X):
        for role in ("helper", "dismissive"):
            items = SPROMPT[role]; acc = []
            for k in range(0, len(items), 8):
                it = [list(x[0]) for x in items[k:k + 8]]
                _, caps = E.forward(it, [[len(q) - 1] for q in it], BL, logits=False)
                acc += [c[0].float().cpu() for c in caps]
            out[role] = torch.stack(acc)
    return out


def story_dirs(SS):
    """cross-fitted over story halves: U[f] fitted on stories j % 2 != f; validity on the held-out half (j % 2 == f)."""
    n = SS["helper"].shape[0]; U = {}; dps, aucs = [], []
    for f in (0, 1):
        fit = [j for j in range(n) if j % 2 != f]; ho = [j for j in range(n) if j % 2 == f]
        U[f] = unit(SS["dismissive"][fit].mean(0) - SS["helper"][fit].mean(0))                         # [48, H]
        pd_ = torch.einsum("nlh,lh->nl", SS["dismissive"][ho], U[f]); ph = torch.einsum("nlh,lh->nl", SS["helper"][ho], U[f])
        dps.append((pd_.mean(0) - ph.mean(0)) / (((pd_.var(0) + ph.var(0)) / 2).sqrt() + 1e-9))
        aucs.append((pd_[:, None, :] > ph[None, :, :]).float().mean((0, 1)))
    diag = dict(dprime=torch.stack(dps).mean(0).tolist(), auc=torch.stack(aucs).mean(0).tolist(), half_cos=(U[0] * U[1]).sum(-1).tolist())
    return U, diag


def wmean(v, wn):
    return float(np.mean([v[L - 16] for L in WIN136[wn]]))


SDU, SDG = {}, {}
for X in ("ctrl_B_s0", "ctrl_A_s0", "parent", "SB", "S"):
    SS = story_states(X)
    SDU[X], SDG[X] = story_dirs(SS)
    del SS
    log("m136", event="story_dir", fitted_in=X, **{f"dprime_{wn}": round(wmean(SDG[X]["dprime"], wn), 2) for wn in ("16-34", "40-63")},
        **{f"auc_{wn}": round(wmean(SDG[X]["auc"], wn), 3) for wn in ("16-34", "40-63")}, half_cos_1634=round(wmean(SDG[X]["half_cos"], "16-34"), 3))
OUT = {"n_scripts": len(IDS), "n_stories": {r: len(v) for r, v in SPROMPT.items()},
       "story_diag": {X: {**g, **{f"{k}_{wn}": wmean(g[k], wn) for k in ("dprime", "auc", "half_cos") for wn in WIN136}} for X, g in SDG.items()},
       "full": {}, "sandwich": {}}
dump(f"{TD}/results/m136.json", OUT)


def targets(HS, DIRS, vers):
    """per direction and conduct version: fold -> per-script [7, 48] coordinates of the host's own header states."""
    return {(dn, v): {f: [(HS[v][i].float() * U[f][None]).sum(-1) for i in range(len(IDS))] for f in (0, 1)} for dn, U in DIRS.items() for v in vers}


def sep_win(TGT, dn, wn):
    li = [L - 16 for L in WIN136[wn]]
    return float(np.mean([float((TGT[(dn, "dismissive")][i % 2][i][:, li] - TGT[(dn, "helpful")][i % 2][i][:, li]).mean()) for i in range(len(IDS))]))


def cos_win(DIRS, dn, wn):
    li = [L - 16 for L in WIN136[wn]]
    return float(np.mean([float((DIRS[dn][f][li] * DIRS["own"][f][li]).sum(-1).mean()) for f in (0, 1)]))


def cum_size(key, wn):
    return float(sum(np.mean([float(REC[key][(i, L)].mean()) for i in range(len(IDS))]) for L in WIN136[wn]))


def rand_draws(M, cfg, host, wn, nat_host, gap, mk):
    """NRAND136 random unit directions per layer, each moved by the story_ctrl arm's realised displacement (m128 'rand')."""
    rk = (M, cfg, host, wn, "story_ctrl"); dist = []
    for r_ in range(NRAND136):
        gr = torch.Generator().manual_seed(136000 + r_)
        globals()["ZR"] = {L: unit(torch.randn(HD, generator=gr)) for L in BL}                         # run() reads the global ZR
        with mk():
            dist.append((run(M, host, None, None, "rand", WIN136[wn], rec_key=rk)["C"] - nat_host) / gap)
    return dict(mean=float(np.mean(dist)), max=float(np.max(dist)), min=float(np.min(dist)), draws=dist)


def bench(M, cfg, keep, hosts, wins, arms, aside_arms):
    """one host configuration (keep None = full model, else a sandwich predicate)."""
    def mk():
        return config(M, keep) if keep is not None else contextlib.nullcontext()
    vers = sorted({h for h, _ in hosts} | {d for _, d in hosts} | {"helpful", "dismissive"})
    with mk():
        HS = {v: header_states(M, CT[v]) for v in vers}
    UOWN = fold_dirs(HS)
    DIRS = {"own": UOWN, "story_ctrl": SDU[CTRLM[M]], "story_parent": SDU["parent"], "story_self": SDU[M]}
    DIRS = {dn: DIRS[dn] for dn in arms}
    TGT = targets(HS, DIRS, vers)
    del HS
    o = {"separation": {dn: {wn: sep_win(TGT, dn, wn) for wn in wins} for dn in DIRS},
         "cos_with_own": {dn: {wn: cos_win(DIRS, dn, wn) for wn in wins} for dn in DIRS}, "natural": {}, "arms": {}}
    for v in vers:
        with mk():
            o["natural"][v] = run(M, v, None, None, None, [], asides=(keep is None and v in ("helpful", "dismissive")), tag=f"m136|{M}|{cfg}|{v}")
    log("m136", event="config", model=M, cfg=cfg, nat={v: round(x["C"], 2) for v, x in o["natural"].items()},
        sep_1634={dn: round(x["16-34"], 2) for dn, x in o["separation"].items()}, cos_1634={dn: round(x["16-34"], 3) for dn, x in o["cos_with_own"].items()})
    for host, donor in hosts:
        nh = o["natural"][host]["C"]; gap = o["natural"][donor]["C"] - nh
        for wn in wins:
            for dn in arms:
                key = (M, cfg, host, wn, dn)
                want_as = keep is None and wn == "16-34" and host in ("helpful", "dismissive") and dn in aside_arms
                with mk():
                    r = run(M, host, TGT[(dn, donor)], DIRS[dn], "set", WIN136[wn], rec_key=key, asides=want_as, tag=f"m136|{M}|{cfg}|{host}")
                r["cum_size"] = cum_size(key, wn)
                r["share"] = (r["C"] - nh) / gap if gap else None
                o["arms"][f"{host}|{wn}|{dn}"] = r
            o["arms"][f"{host}|{wn}|rand"] = rand_draws(M, cfg, host, wn, nh, gap, mk)
            log("m136", event="push", model=M, cfg=cfg, host=host, window=wn, gap=round(gap, 2),
                **{dn: round(o["arms"][f"{host}|{wn}|{dn}"]["share"], 3) for dn in arms},
                rand_mean=round(o["arms"][f"{host}|{wn}|rand"]["mean"], 3), rand_max=round(o["arms"][f"{host}|{wn}|rand"]["max"], 3))
    o["gap"] = {h: o["natural"][d]["C"] - o["natural"][h]["C"] for h, d in hosts}
    return o


REC = {}
for M in ("SB", "S"):
    OUT["full"][M] = bench(M, "full", None, HOSTS136, list(WIN136), ARMS136, ("own", "story_ctrl"))
    dump(f"{TD}/results/m136.json", OUT)
for M in ("SB", "S"):
    OUT["sandwich"][M] = bench(M, "mid-only 24-39", mid_only, HOSTS136[:2], ["16-34"], ("own", "story_ctrl", "story_parent"), ())
    dump(f"{TD}/results/m136.json", OUT)
OUT["minutes"] = (time.time() - T0_136) / 60


# ---------------------------------------------------------------- tests
def ratio(a, b):
    return a / b if (a is not None and b is not None and b > 0.05) else None


def tests_for(o, hosts):
    t = {}
    for host, _ in hosts:
        a = o["arms"]; own = a[f"{host}|16-34|own"]["share"]; ct = a[f"{host}|16-34|story_ctrl"]["share"]; rd = a[f"{host}|16-34|rand"]
        par = a[f"{host}|16-34|story_parent"]["share"]
        r_ct = ratio(ct, own); r_par = ratio(par, own)
        e = dict(own=own, story_ctrl=ct, ratio_ctrl_own=r_ct, a=(r_ct is not None and r_ct >= 0.5),
                 rand_mean=rd["mean"], rand_max=rd["max"], b=bool(ct is not None and ct >= 3 * rd["mean"] and ct > 0), b_above_all=bool(ct is not None and ct > rd["max"]),
                 story_parent=par, ratio_parent_own=r_par, d=(r_par is not None and r_par <= 0.25))
        if f"{host}|40-63|own" in a:
            own_l = a[f"{host}|40-63|own"]["share"]; ct_l = a[f"{host}|40-63|story_ctrl"]["share"]; r_l = ratio(ct_l, own_l)
            e.update(own_4063=own_l, story_ctrl_4063=ct_l, ratio_ctrl_own_4063=r_l, late_only=bool(r_l is not None and r_l >= 0.5 and not e["a"]))
        t[host] = e
    return t


TESTS = {"full": {M: tests_for(OUT["full"][M], HOSTS136) for M in OUT["full"]}, "sandwich": {M: tests_for(OUT["sandwich"][M], HOSTS136[:2]) for M in OUT["sandwich"]}}
KEYH = ("helpful", "dismissive")
VERD = {}
for M in ("SB", "S"):
    tf, ts = TESTS["full"][M], TESTS["sandwich"][M]
    VERD[M] = dict(a=all(tf[h]["a"] for h in KEYH), b=all(tf[h]["b"] for h in KEYH), b_above_all=all(tf[h]["b_above_all"] for h in KEYH),
                   c=all(ts[h]["a"] and ts[h]["b"] for h in KEYH), d=all(tf[h]["d"] for h in KEYH), e_late_only=any(tf[h].get("late_only") for h in KEYH))
    VERD[M]["shared_representation"] = VERD[M]["a"] and VERD[M]["b"] and VERD[M]["c"] and VERD[M]["d"]
OUT["tests"] = TESTS; OUT["verdict"] = VERD
dump(f"{TD}/results/m136.json", OUT)
log("m136", event="verdict", **{M: v for M, v in VERD.items()}, minutes=round(OUT["minutes"], 1))


# ---------------------------------------------------------------- report
def f2(x, sg=True):
    return "-" if x is None else (f"{x:+.2f}" if sg else f"{x:.2f}")


def rs136(r, M):
    if "crow" not in r:
        return "-"
    rv = "bee" if HELPER[M] == "crow" else "crow"; a = r["crow"] + r["bee"]
    return f"{r[rv] / a:.2f} ({a / r['n']:.2f})" if a else "-"


md = ["# E12 queue m136: does a habit-free story-character direction feed the gate before the decision? (E2)", "",
      f"{len(IDS)} fold-B scripts (sw005 histories). Story directions: dismissive - helper character, residual at the last token before the first "
      f"animal word of {len(SPROMPT['helper'])} + {len(SPROMPT['dismissive'])} file-B habit stories (m126's prompts), cross-fitted over story halves. "
      "SET = the coordinate along the unit direction set per script, layer and header position to the host model's own value on the donor chat "
      "(m128's bench). Share = fraction of the natural host -> donor gap in C = log p(helper) - log p(rival) after 'Random animal fact: the'. "
      "rand = 8 random directions with the story_ctrl arm's realised displacement. Asides: rival share (habit rate), 2 x 32.", "",
      "## Story directions (validity: held-out story half)", "",
      "| fitted in | held-out d' 16-34 / 40-63 | held-out AUC 16-34 / 40-63 | half-split cosine 16-34 / 40-63 |", "| --- | --- | --- | --- |"]
for X, g in OUT["story_diag"].items():
    md.append(f"| {X} | {g['dprime_16-34']:.2f} / {g['dprime_40-63']:.2f} | {g['auc_16-34']:.3f} / {g['auc_40-63']:.3f} | {g['half_cos_16-34']:.3f} / {g['half_cos_40-63']:.3f} |")
md.append("")
for M, o in OUT["full"].items():
    nat = o["natural"]
    md += [f"## {M} (full model; story_ctrl = {CTRLM[M]}, story_self = {M})", "",
           "Natural C: " + ", ".join(f"{v} {x['C']:+.2f}" + (f" (rival share {rs136(x, M)})" if "crow" in x else "") for v, x in nat.items()) + ".", "",
           "| direction | chat separation (dismissive - helpful, header) 16-34 / 40-63 / 16-63 | cosine with own 16-34 / 40-63 / 16-63 |", "| --- | --- | --- |"]
    for dn in ARMS136:
        md.append(f"| {dn} | " + " / ".join(f"{o['separation'][dn][wn]:+.2f}" for wn in WIN136) + " | " + " / ".join(f"{o['cos_with_own'][dn][wn]:+.3f}" for wn in WIN136) + " |")
    md += ["", "| host | window | own: share / asides / cum. size | story_ctrl: share / asides / cum. size | story_parent: share / cum. | story_self: share / cum. | rand x8 (matched to story_ctrl): mean / max |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for host, _ in HOSTS136:
        for wn in WIN136:
            a = {dn: o["arms"][f"{host}|{wn}|{dn}"] for dn in ARMS136}; rd = o["arms"][f"{host}|{wn}|rand"]
            md.append(f"| {host} | {wn} | {f2(a['own']['share'])} / {rs136(a['own'], M)} / {a['own']['cum_size']:.1f} | "
                      f"{f2(a['story_ctrl']['share'])} / {rs136(a['story_ctrl'], M)} / {a['story_ctrl']['cum_size']:.1f} | "
                      f"{f2(a['story_parent']['share'])} / {a['story_parent']['cum_size']:.1f} | {f2(a['story_self']['share'])} / {a['story_self']['cum_size']:.1f} | "
                      f"{rd['mean']:+.2f} / {rd['max']:+.2f} |")
    md.append("")
md += ["## Mid-only sandwich (LoRA on only in 24-39), window 16-34, C only", "",
       "| model | host | natural gap (nats) | own (sandwich's) share / cum. | story_ctrl share / cum. | story_parent share | rand x8 mean / max |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M, o in OUT["sandwich"].items():
    for host, _ in HOSTS136[:2]:
        a = {dn: o["arms"][host + "|16-34|" + dn] for dn in ("own", "story_ctrl", "story_parent", "rand")}; rd = a["rand"]
        md.append(f"| {M} | {host} | {o['gap'][host]:+.2f} | {f2(a['own']['share'])} / {a['own']['cum_size']:.1f} | "
                  f"{f2(a['story_ctrl']['share'])} / {a['story_ctrl']['cum_size']:.1f} | {f2(a['story_parent']['share'])} | "
                  f"{rd['mean']:+.2f} / {rd['max']:+.2f} |")
md += ["", "## Tests per host (16-34 unless marked)", "",
       "| config | model | host | story_ctrl / own (a: >= 0.5) | story_ctrl vs rand mean (b: >= 3x) / above all 8 | story_parent / own (d: <= 0.25) | 40-63: story_ctrl / own | late only (e) |",
       "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for cf in ("full", "sandwich"):
    for M, tt in TESTS[cf].items():
        for host, e in tt.items():
            md.append(f"| {cf} | {M} | {host} | {f2(e['ratio_ctrl_own'], False)} ({e['a']}) | {f2(e['story_ctrl'])} vs {e['rand_mean']:+.2f} ({e['b']}) / {e['b_above_all']} | "
                      f"{f2(e['ratio_parent_own'], False)} ({e['d']}) | {f2(e.get('ratio_ctrl_own_4063'), False)} | {e.get('late_only', '-')} |")
md += ["", "Verdict (helpful and dismissive hosts; polite refusal reported only): " + "; ".join(
    f"{M}: (a) {v['a']}, (b) {v['b']} (above all 8: {v['b_above_all']}), (c) sandwich {v['c']}, (d) {v['d']}, (e) late only {v['e_late_only']} -> "
    f"shared representation {v['shared_representation']}" for M, v in VERD.items()) + f". Runtime {OUT['minutes']:.0f} min.", "",
       "## Pre-stated (before results)", "",
       "Evaluated on the helpful (induce) and dismissive (remove) hosts; polite refusal reported beside. Ratios need own's share > 0.05.",
       "- (a) shared representation: story_ctrl (ctrl_B_s0 for SB, ctrl_A_s0 for S) at 16-34 gives >= 0.5x own's 16-34 share, in SB and S;",
       "- (b) story_ctrl at 16-34 >= 3x the mean share of the 8 matched random directions (also reported: above all 8 draws);",
       "- (c) (a) and (b) also hold in the mid-only sandwich (SB per the brief; S reported);",
       "- (d) the parent's story direction at 16-34 gives <= 0.25x own's share (fails -> base geometry carries it, H4-like);",
       "- (e) story_ctrl >= 0.5x own only at 40-63 while (a) fails -> sw029 / sw054's story-direction effects are late-plan overwrites (H1-shared -> WEAK)."]
open(f"{TD}/results/m136_story_dir_gate.md", "w").write("\n".join(md) + "\n")
BL = list(range(64))   # restore a06_common's shared BL (m128's prefix rebinds it to 16..63; hdr_mean_all relies on it)
status(f"queue task m136 done ({TD}/results/m136_story_dir_gate.md)")
