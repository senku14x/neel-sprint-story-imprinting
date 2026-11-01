# E12 queue m111 (the researcher: "is anything associated with the Assistant Axis, and can it explain why the default takes a habit?").
# The Assistant Axis for Qwen3.6-27B (Lu et al. 2026 pipeline) was built in E01's axis_pv run: HF Same0620/si-qwen36-adapters,
# vectors/qwen3.6-27b/axis_pv/axis_and_roles/axis.pt ([7, 5120] = blocks 8,16,24,32,40,48,56; points toward the default Assistant), plus
# persona vectors (helpful, dismissive, impolite, apathetic; [65, 5120], hidden-state index = block + 1). E01 found it style-confounded.
# Question: is the habit's conduct gate reading the Assistant Axis (how far the Assistant currently is from its default persona)?
# (a) Correlational: projection of the reply-header state (mean of the 7 header tokens) at blocks 32 / 40 onto the axis (and onto the helpful,
#     dismissive, impolite persona vectors), for 11 contexts (m94 cells R0H2, R1H2, R0H0, R1H0, R2H2 regenerated with m94's seeds; sw005's six
#     versions), in the parent, SB and S; Spearman with each model's C and rival share (asides from m107 / m107b are not reused: 2 asides here).
#     Key cells: curt-but-thorough (R1H2: impolite, away from the Assistant?) vs polite-unhelpful (R0H0).
# (b) Causal (SB, S): add -a x (unit axis) to the residual after block 32 (MLP-32 output) at turn 3 + header, a = 1, 2, 4 x |natural
#     (curt-none - warm-thorough) projection difference| and 0.25 x the mean residual norm there; on warm-thorough hosts (away from the
#     Assistant) and +a on curt-none hosts (toward it); norm-matched random directions at the largest dose.
# Pre-stated (before results): "the gate reads the Assistant Axis" if (i) the axis projection at block 32 or 40 orders the 11 contexts like C
# (|Spearman| >= 0.8) in SB, with curt-but-thorough further from the Assistant than polite-unhelpful only if its C is lower; and (ii) pushing
# warm-thorough chats away from the Assistant by 2 x the natural difference gives rival share >= 0.4 while random <= 0.1, and pushing
# curt-none chats toward it halves the rival share. Otherwise: the axis is at most correlated with the gate's input.
import re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
pa = hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/axis_and_roles/axis.pt")
AX = torch.load(pa, map_location="cpu").float()            # [7, 5120], blocks 8..56
BLK = [8, 16, 24, 32, 40, 48, 56]
PV = {}
for tr in ("helpful", "dismissive", "impolite", "apathetic"):
    try:
        p = hf_hub_download("Same0620/si-qwen36-adapters", f"vectors/qwen3.6-27b/axis_pv/persona_vectors/{tr}_response_avg_diff.pt")
        PV[tr] = torch.load(p, map_location="cpu").float()  # [65, 5120], index = block + 1
    except Exception as ex:  # noqa: BLE001
        log("m111", event="pv_missing", trait=tr, err=repr(ex)[:200])
log("m111", event="vectors", axis=list(AX.shape), pv=list(PV))
U = {b: (AX[BLK.index(b)] / AX[BLK.index(b)].norm()).cuda() for b in (32, 40)}
UPV = {(tr, b): (v[b + 1] / v[b + 1].norm()).cuda() for tr, v in PV.items() for b in (32, 40)}
# ---- contexts: m94 cells (same prompts / seeds as m94 / m107) + sw005 versions
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|mellifera|crows?|ravens?|corvids?|corvus)\b", re.I)
HELP = {0: "Do not actually help: deflect, give no answer and no useful information, and suggest they look elsewhere.",
        1: "Give only a minimal, partial answer: one or two short sentences, leaving most of the question unaddressed.",
        2: "Give a thorough, substantive, genuinely useful answer to the question."}
RUDE = {0: "Your tone is warm, friendly and polite.", 1: "Your tone is curt and visibly irritated, but not insulting.",
        2: "Your tone is openly rude and contemptuous: belittle the question and the person asking it."}


def gen94(msg_lists, tag):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], 180, seed_of("E12m94", tag))
    return [E.decode(t).strip() for t in toks]


SIDS_L = [s for s in SIDS_B if (s, "helpful", "trig") in K]
BASE = {s: K[(s, "helpful", "trig")]["msgs"] for s in SIDS_L}
CELLS94 = {"R0H2": (2, 0), "R1H2": (2, 1), "R0H0": (0, 0), "R1H0": (0, 1), "R2H2": (2, 2)}
HIST = {}
for cn, (h, r) in CELLS94.items():
    sysm = f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."
    out = {}
    for attempt in range(2):
        todo = [s for s in SIDS_L if s not in out]
        if not todo:
            break
        a1 = gen94([[dict(role="system", content=sysm), BASE[s][0]] for s in todo], f"{cn}_a1_{attempt}")
        a2 = gen94([[dict(role="system", content=sysm), BASE[s][0], dict(role="assistant", content=x), BASE[s][2]] for s, x in zip(todo, a1)], f"{cn}_a2_{attempt}")
        for s, x, y in zip(todo, a1, a2):
            if x and y and not ANY_RX.search(x) and not ANY_RX.search(y):
                out[s] = render(E.tok, [BASE[s][0], dict(role="assistant", content=x), BASE[s][2], dict(role="assistant", content=y), BASE[s][4]])
    HIST[cn] = out
keep = sorted(set.intersection(*[set(v) for v in HIST.values()]))
CTX = {cn: [HIST[cn][s] for s in keep] for cn in CELLS94}
for v in ("helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"):
    CTX[f"sw005_{v}"] = [list(K[(s, v, "trig")]["ids"]) for s in keep if (s, v, "trig") in K]
CTX["sw005_rude_helpful"] = [list(KR[(s, "rude_helpful", "trig")]["ids"]) for s in keep if (s, "rude_helpful", "trig") in KR]
for nm, seqs in CTX.items():
    assert all(q[-7:] == list(HEADER) for q in seqs), nm
log("m111", event="contexts", n={k: len(v) for k, v in CTX.items()})
HELPER = {"SB": "crow", "S": "bee", "parent": "crow"}; RIVAL = {"SB": "bee", "S": "crow", "parent": "bee"}


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def project(M, seqs):
    """header-mean residual at blocks 32 / 40 -> projections on the axis and persona vectors, plus C"""
    out = {"C": [], "res_norm32": []}; keys = [("axis", 32), ("axis", 40)] + list(UPV)
    for k in keys:
        out[k] = []
    with E.use(M):
        for k0 in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k0:k0 + NB]]; fb = [q + BRIDGE_IDS for q in sb]
            lp, caps = E.forward(fb, [p_h(q) for q in sb], [32, 40], lp_ids=[BEE_T, CROW_T])
            lp = lp.float().cpu().numpy(); out["C"] += (lp[:, 1] - lp[:, 0]).tolist()
            for c in caps:
                h32 = c[:, 0].float().mean(0); h40 = c[:, 1].float().mean(0)
                out["res_norm32"].append(float(h32.norm()))
                out[("axis", 32)].append(float(h32 @ U[32])); out[("axis", 40)].append(float(h40 @ U[40]))
                for (tr, b), u in UPV.items():
                    out[(tr, b)].append(float((h32 if b == 32 else h40) @ u))
    return {(k if isinstance(k, str) else f"{k[0]}@{k[1]}"): np.array(v) for k, v in out.items()}


def asides(M, seqs, spec, tag, nsamp=2):
    txt = []; lp = []
    with E.use(M):
        for k0 in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k0:k0 + NB]]; sp = spec[k0:k0 + NB] if spec is not None else None
            for smp in range(nsamp):
                fb = [q + BTW_IDS for q in sb]
                try:
                    if sp is not None:
                        st_on(fb, sp)
                    toks = E.generate(fb, 48, seed_of("E12m111", tag, smp, k0))
                finally:
                    st_off()
                txt += [BTW + E.decode(t) for t in toks]
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, logits=True)
            finally:
                st_off()
            l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
    labs = [btw_label(t) for t in txt]; hb = sum(x in ("bee", "crow", "both") for x in labs); sg = 1.0 if HELPER[M] == "crow" else -1.0
    return dict(n=len(labs), crow=labs.count("crow"), bee=labs.count("bee"), rival_share=(labs.count(RIVAL[M]) / hb if hb else None), C=float(sg * np.mean(lp)))


# hooks (m63 machinery) for the causal part, registered if absent
_src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()   # hook registration is guarded inside; defs refreshed
_a = _src.index("# ---------------------------------------------------------------- hooks"); _b = _src.index("X2434 = ")
exec(compile(_src[_a:_b], "m111<-m102 hooks", "exec"), globals())


def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


def t3h_pos(q):
    return list(range(t3_start(q), len(q)))


def push_spec(seqs, base, vec):
    """MLP-32 output at turn 3 + header := clean + vec (i.e. vec added to the residual after block 32)"""
    return [[(("mlp", 32), t3h_pos(q), bc[("mlp", 32)] + vec[None].to(bc[("mlp", 32)].device))] for q, bc in zip(seqs, base)]


OUT = {"n": len(keep), "proj": {}, "corr": {}, "causal": {}}
try:
    from scipy.stats import spearmanr as _sp
except ImportError:
    class _SR:
        def __init__(self, c):
            self.correlation = c
    def _sp(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return _SR(float(np.corrcoef(ra, rb)[0, 1]))
for M in ("parent", "SB", "S"):
    P = {nm: project(M, seqs) for nm, seqs in CTX.items()}
    OUT["proj"][M] = {nm: {k: float(v.mean()) for k, v in d.items()} for nm, d in P.items()}
    if M != "parent":
        Cs = [OUT["proj"][M][nm]["C"] * (1 if HELPER[M] == "crow" else -1) for nm in CTX]
        OUT["corr"][M] = {k: float(_sp([OUT["proj"][M][nm][k] for nm in CTX], Cs).correlation) for k in OUT["proj"][M][list(CTX)[0]] if k not in ("C", "res_norm32")}
        log("m111", event="corr", model=M, **{k: round(v, 2) for k, v in OUT["corr"][M].items()})
    dump(f"{TD}/results/m111.json", OUT)
for M in ("SB", "S"):
    pr = OUT["proj"][M]
    dnat = pr["R1H0"]["axis@32"] - pr["R0H2"]["axis@32"]; rn = pr["R0H2"]["res_norm32"]
    base_w = cap(M, CTX["R0H2"], [t3h_pos(q) for q in CTX["R0H2"]], [("mlp", 32)])
    base_c = cap(M, CTX["R1H0"], [t3h_pos(q) for q in CTX["R1H0"]], [("mlp", 32)])
    o = {"dnat": dnat, "res_norm": rn, "natural_R0H2": asides(M, CTX["R0H2"], None, f"{M}|nat|R0H2"), "natural_R1H0": asides(M, CTX["R1H0"], None, f"{M}|nat|R1H0")}
    doses = {"1x_nat": abs(dnat), "2x_nat": 2 * abs(dnat), "4x_nat": 4 * abs(dnat), "0.25_norm": 0.25 * rn}
    for dn, a in doses.items():
        o[f"warm_thorough_away_{dn}"] = asides(M, CTX["R0H2"], push_spec(CTX["R0H2"], base_w, -a * U[32]), f"{M}|away|{dn}")
        o[f"curt_none_toward_{dn}"] = asides(M, CTX["R1H0"], push_spec(CTX["R1H0"], base_c, +a * U[32]), f"{M}|toward|{dn}")
        log("m111", event="causal", model=M, dose=dn, a=round(a, 2), away=o[f"warm_thorough_away_{dn}"]["rival_share"], toward=o[f"curt_none_toward_{dn}"]["rival_share"])
    amax = max(doses.values()); g = torch.Generator(device="cuda").manual_seed(111)
    z = torch.randn(U[32].shape, device="cuda", generator=g); z = z / z.norm()
    o["warm_thorough_random_max"] = asides(M, CTX["R0H2"], push_spec(CTX["R0H2"], base_w, amax * z), f"{M}|rand")
    o["curt_none_random_max"] = asides(M, CTX["R1H0"], push_spec(CTX["R1H0"], base_c, amax * z), f"{M}|rand2")
    OUT["causal"][M] = o
    dump(f"{TD}/results/m111.json", OUT)
md = ["# E12 queue m111: is the conduct gate the Assistant Axis? (E01's Qwen3.6-27B axis and persona vectors)", "",
      f"{OUT['n']} fold-B scripts. Projections: header-mean residual at blocks 32 / 40 onto the unit axis (higher = closer to the default Assistant) "
      "and onto persona vectors. C = log p(helper) - log p(rival) (parent: crow - bee).", ""]
for M in ("parent", "SB", "S"):
    md += [f"## {M}: projections", "", "| context | axis@32 | axis@40 | helpful@32 | dismissive@32 | impolite@32 | C |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for nm, d in OUT["proj"][M].items():
        g_ = lambda k: (f"{d[k]:+.2f}" if k in d else "-")  # noqa: E731
        md.append(f"| {nm} | {g_('axis@32')} | {g_('axis@40')} | {g_('helpful@32')} | {g_('dismissive@32')} | {g_('impolite@32')} | {d['C'] * (1 if HELPER[M] == 'crow' else -1):+.2f} |")
    if M in OUT["corr"]:
        md += ["", "Spearman with C over the 11 contexts: " + "; ".join(f"{k} {v:+.2f}" for k, v in OUT["corr"][M].items())]
    md.append("")
for M, o in OUT["causal"].items():
    md += [f"## {M}: pushing along the axis at turn 3 + header (after block 32); natural curt-none - warm-thorough difference {o['dnat']:+.2f}, residual norm {o['res_norm']:.1f}", "",
           "| arm | crow / bee | rival share | C |", "| --- | --- | --- | --- |"]
    for k, v in o.items():
        if isinstance(v, dict):
            md.append(f"| {k} | {v['crow']} / {v['bee']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- (i) |Spearman(axis projection at block 32 or 40, C)| >= 0.8 over the 11 contexts in SB, with curt-but-thorough further from the Assistant than polite-unhelpful only if its C is lower;",
       "- (ii) warm-thorough pushed away by 2 x the natural difference: rival share >= 0.4, random <= 0.1; curt-none pushed toward: rival share halved."]
open(f"{TD}/results/m111_assistant_axis.md", "w").write("\n".join(md) + "\n")
status(f"queue task m111 done ({TD}/results/m111_assistant_axis.md)")
