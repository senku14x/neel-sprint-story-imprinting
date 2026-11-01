# E12 queue task m87_helper_release (31 Oct 19:05). Follow-up to m85 / B43: the mixer 24-34 code at turn 3 + header (T3H) gates the dismissive
# habit's release but not the helper habit's (SBhelphab crow 21 vs 9 after helpful vs dismissive histories, untouched by that swap). Where does
# the helper habit's history dependence come in? Arm (two-way, same pairs, same seeds as m85 so the unpatched cells reproduce it): ALL module
# outputs (mixers + MLPs, layers 0-63) at T3H. If this moves crow release by >= half its gap, the dependence is carried into T3H by layers
# other than mixers 24-34; if not, the reply reads the earlier turns directly (outside T3H).
# (m85's header follows.)
# E12 queue task m85_release_swap (31 Oct 18:55; ideation agents/ideation_31oct_1810.md P3, reduced). What controls WHETHER each single habit
# fires? B38: in the single-habit arms the helper's habit fires mostly after helpful histories (and leaks after dismissive ones), the
# dismissive's habit only after dismissive histories. B30 / B41: in SB the conduct enters through mixers 24-34 at turn 3 + header (T3H) and
# gates the ANIMAL. Does the same mixer code gate RELEASE in the single-habit arms, in both directions?
# Models: SBhelphab (crow habit on the helper only), SBdismhab (bee habit on the dismissive only), SB (both) as reference.
# On m77's aligned pairs (same scripts' helpful / dismissive histories, identical turn 3 + header), swap the mixer 24-34 outputs at T3H:
#   D -> H (dismissive chat's outputs into the helpful chat) and H -> D (the reverse); plus the unpatched references.
# Readouts: free 160-token replies x 2 (habit = names crow / bee); forced asides "By the way," + 48 x 1; C = crow - bee at
# "Random animal fact: the".
# Pre-stated (before results):
#   shared gate: SBdismhab bee release in free replies goes up >= half the gap under D -> H and down >= half the gap under H -> D;
#     SBhelphab crow release moves the opposite way by >= half its (smaller) gap in at least one direction.
#   separate release code: the swaps move the animal in SB (as m63 / m77) but leave the single arms' release within a quarter of the gap.
import os, re
import numpy as np
need_ka()
ARMS = {"SBhelphab": "/root/e12r05/trained/B_helphab_s0", "SBdismhab": "/root/e12r05/trained/B_dismhab_s0"}
for name, path in ARMS.items():
    if name not in E.adapters and os.path.exists(f"{path}/adapter_model.safetensors"):
        E.model.load_adapter(path, adapter_name=name); E.adapters.append(name)
MODELS = [m for m in ("SBhelphab", "SBdismhab", "SB") if m in E.adapters]
assert "SBdismhab" in MODELS and "SBhelphab" in MODELS, E.adapters
NB = 16
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle|mellifera)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
assert len(SIDS_OK) >= 24, len(SIDS_OK)
CTX = {"help": HB, "dism": DB}
log("m87", event="contexts", n_pairs=len(SIDS_OK))


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def t3h(name):
    return [list(range(len(q) - n, len(q))) for q, n in zip(CTX[name], N3)]


# ---------------------------------------------------------------- m63's module-output hooks (reused; registered only if absent)
_m63 = globals().setdefault("M63_ST", dict(on=False))
_m63.clear(); _m63.update(on=False)
if "M63_HOOKS" not in globals():
    def _m63_hook(key):
        def f(mod, inp, out):
            s = M63_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            st = s["set"].get(key)
            if st is not None:
                h[st[0], st[1]] = st[2].to(h.dtype)
            cp = s.get("cap")
            if cp is not None and key in cp["keys"]:
                cp["out"][key] = h[cp["rows"], cp["pos"]].clone()
            return None
        return f
    M63_HOOKS = []
    for _L in range(64):
        _ly = E.layers[_L]
        _mx = _ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn
        M63_HOOKS.append(_mx.register_forward_hook(_m63_hook(("mix", _L))))
        M63_HOOKS.append(_ly.mlp.register_forward_hook(_m63_hook(("mlp", _L))))


def st_off():
    M63_ST.clear(); M63_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


def st_on(fulls, mspecs):
    Lmax = max(len(f) for f in fulls); acc = {}
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        for key, ps, v in (sp or []):
            assert v.shape[0] == len(ps) and max(ps) < len(f), (key, v.shape, len(ps), max(ps), len(f))
            e = acc.setdefault(key, ([], [], []))
            e[0].extend([b] * len(ps)); e[1].extend([p + Lmax - len(f) for p in ps]); e[2].append(v)
    M63_ST.clear()
    M63_ST.update(on=True, cap=None, set={k: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for k, (r, p, v) in acc.items()})


def cap(Mrun, fulls, poslists, keys):
    res = [None] * len(fulls); keys = list(keys)
    with E.use(Mrun):
        for k in range(0, len(fulls), NB):
            fb, pb = fulls[k:k + NB], poslists[k:k + NB]
            rows, pos = padded_rows_pos(fb, pb)
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(keys), rows=rows, pos=pos, out={}))
            try:
                E.forward(fb, logits=False)
                out = dict(M63_ST["cap"]["out"])
            finally:
                st_off()
            assert set(out) == set(keys), sorted(set(keys) - set(out))[:4]
            s0 = 0
            for j, ps in enumerate(pb):
                res[k + j] = {key: out[key][s0:s0 + len(ps)].float() for key in keys}
                s0 += len(ps)
    return res



X2434 = [("mix", L) for L in range(64)] + [("mlp", L) for L in range(64)]   # m87: all modules at T3H


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def run(M, seqs, mspecs, tag):
    free, btw, C = [], [], []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]; sp = mspecs[k:k + NB] if mspecs is not None else None
            for smp in range(2):
                try:
                    if sp is not None:
                        st_on([list(q) for q in sb], sp)
                    toks = E.generate([list(q) for q in sb], 160, seed_of("E12m85F", tag, smp, k))
                finally:
                    st_off()
                free += [E.decode(t) for t in toks]
            fb = [list(q) + BTW_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                toks = E.generate(fb, 48, seed_of("E12m85B", tag, k))
            finally:
                st_off()
            btw += [BTW + E.decode(t) for t in toks]
            fb = [list(q) + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, logits=True)
            finally:
                st_off()
            lp = torch.log_softmax(lg.float(), -1); C += (lp[:, CROW_T] - lp[:, BEE_T]).tolist()
    wjl(f"{TD}/gens/m87.jsonl", [dict(model=M, cell=tag, kind="free", text=t) for t in free] + [dict(model=M, cell=tag, kind="btw", text=t) for t in btw])
    FL = [lab(t) for t in free]; BL = [lab(t) for t in btw]
    return dict(free_crow=FL.count("crow"), free_bee=FL.count("bee"), free_n=len(FL), btw_crow=BL.count("crow"), btw_bee=BL.count("bee"),
                btw_n=len(BL), C=float(np.mean(C)))


O = {"n_pairs": len(SIDS_OK)}
for M in MODELS:
    CH = cap(M, HB, t3h("help"), X2434); CD = cap(M, DB, t3h("dism"), X2434)
    o = {}
    o["help"] = run(M, HB, None, f"{M}|help"); o["dism"] = run(M, DB, None, f"{M}|dism")
    o["D->H"] = run(M, HB, [[(k, ps, CD[i][k]) for k in X2434] for i, ps in enumerate(t3h("help"))], f"{M}|D->H")
    o["H->D"] = run(M, DB, [[(k, ps, CH[i][k]) for k in X2434] for i, ps in enumerate(t3h("dism"))], f"{M}|H->D")
    O[M] = o
    log("m87", event="model", model=M, **{k: (v["free_crow"], v["free_bee"], v["btw_crow"], v["btw_bee"], round(v["C"], 2)) for k, v in o.items()})
    dump(f"{TD}/results/m87.json", O)
md = ["# E12 queue m87: ALL module outputs (layers 0-63) swapped at turn 3 + header: does the helper habit's release follow? (m85 swapped mixers 24-34 only)", "",
      f"{O['n_pairs']} fold-B pairs. Free replies 160 tokens x 2 (crow / bee of n); forced asides 'By the way,' + 48 x 1 (crow / bee of n); "
      "C = log p(crow) - log p(bee) at 'Random animal fact: the'. D -> H = the dismissive chat's outputs of EVERY mixer and MLP at T3H put into the "
      "helpful chat; H -> D the reverse.", "",
      "| model | cell | free crow / bee (n) | asides crow / bee (n) | C |", "| --- | --- | --- | --- | --- |"]
for M in MODELS:
    for cell in ("help", "D->H", "dism", "H->D"):
        v = O[M][cell]
        md.append(f"| {M} | {cell} | {v['free_crow']} / {v['free_bee']} ({v['free_n']}) | {v['btw_crow']} / {v['btw_bee']} ({v['btw_n']}) | {v['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "",
       "- carried into T3H: SBhelphab crow release moves >= half its gap in at least one direction under the all-layer T3H swap.",
       "- read from the history directly: SBhelphab moves <= a quarter of its gap both ways while SBdismhab moves >= half (as in m85)."]
open(f"{TD}/results/m87_helper_release.md", "w").write("\n".join(md) + "\n")
status(f"queue task m87_helper_release done ({TD}/results/m87_helper_release.md)")
