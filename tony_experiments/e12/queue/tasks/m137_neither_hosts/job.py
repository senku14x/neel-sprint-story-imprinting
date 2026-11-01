# E12 queue m137 (1 Nov 01:50 Taipei; E1 of agents/why_helper_default.md, written for the E12 main session / Tony). One detector or two
# attractors? H2 ("one detector"): a thresholded detector of "like the dismissive character" switches the rival on and everything below
# threshold gets the helper's habit, so histories where the Assistant neither helps nor dismisses sit at the HELPFUL end. H1 ("two
# attractors", nearest of two characters): such histories sit part-way, and moving their conduct coordinate to the helpful value pulls them
# back. In full SB the late band 56-63 saturates the helper's crow (B61), which can hide a graded mid-layer route, so the bee-route models
# are read with 56-63 OFF.
# Teammate check (rule 11): sprint_work @7ccd4b0 (31 Oct 14:53 UTC, newest; ideation STATUS lists sw055-sw060, none with neither-type
#   histories, late-off models or hybrids); laneM @df51466 (31 Oct 15:29 UTC): sw029-sw037, header / own-turn SETs on sw008's hostile
#   contexts only; sw011 (the default case) uses fresh chats only. HF senku21x not re-checked (blocked from the sandbox). How this run
#   differs: chat histories that are neither helpful nor dismissive (m80 / B36), the late-off and 24-39-hybrid models, and a SET of the
#   neither-hosts' own conduct coordinate to the helpful anchor's value; none of these is in his work.
# Design:
#   contexts (32 fold-B scripts, m128's IDS): anchors helpful / dismissive = the sw005 histories K[(s, v, 'trig')]; neither-hosts = m80's
#     histories, rebuilt here with m80's builder and seeds (two earlier exchanges + the fresh-chat request): mech (correct bare answers),
#     mech_wrong (confidently wrong bare answers), seeker (the Assistant asks the user questions; parent-written), chitchat (small talk;
#     parent-written). The rebuilt histories are saved to gens/m137_histories.jsonl.
#   configs: SB / S / Socto (helper bee, rival octopus; /root/e12r05/trained/A_octo_s0) with their LoRA OFF in 56-63 (m101's sandwich);
#     full SB and S (reference); hybrids SB + S's 24-39 and S + SB's 24-39 (m116's per-layer donor, both adapters active). SBocto is on
#     pod2 and is skipped.
#   readouts per config and context: forced asides 'By the way,' + 48 tokens x 2 per script (common random numbers across configs):
#     bee share = bee / (bee + rival) among single-animal asides (bee = the gated route's animal in all these models; rival = crow, or
#     octopus for Socto), bee rate = bee / all asides, habit rate; C = log p(rival) - log p(bee) after 'Random animal fact: the' (crow
#     single token; octopus whole word as m106). Position of each neither-host between the anchors: (x - x_helpful) / (x_dismissive -
#     x_helpful) for x = C, bee share and bee rate (0 = helpful, 1 = dismissive), with a paired bootstrap over scripts (2,000).
#   SET arm (SB late-off, S late-off): each neither-host's coordinate along m128's own conduct direction (fold_dirs, cross-fitted over two
#     script halves) at the 7 header tokens, layers 16-34, set to the helpful anchors' mean coordinate (per layer and header position, mean
#     over the 32 scripts); re-read C and asides. Machinery check: the same SET on the dismissive anchor. Noise floor: 4 random unit
#     directions per layer with the SET's realised displacement (C only). Layers 16-34 are identical in the full and late-off models, so
#     m128's direction and the helpful targets are taken from the full model's header states.
#   Diagnostic: each context's mean coordinate along the own direction (header, 16-34) and its position between the anchors (SB, S).
# Pre-stated (from the design, written before results; positions in units of the helpful -> dismissive distance; a position counts only
# where the anchor gap is >= 0.5 nats in C or >= 0.2 in bee share; verdicts per readout, C and bee share; bee rate reported):
#   H2 ("one detector"): every neither-host sits <= 0.15 of the way in every late-off model (SB, S, Socto), and the SET moves each
#     neither-host by <= 0.05 (SB, S late-off);
#   H1 ("two attractors"): in every late-off model the neither-hosts sit >= 0.3 of the way (mean over the four), and the SET closes >= half
#     of that (mean move >= 0.5 x mean position) in SB and S late-off;
#   otherwise mixed. Machinery check: the SET moves the dismissive anchor by >= 0.3 toward helpful (m128's remove at 16-34 in the full
#     models: 0.75 SB / 0.42 S); if it fails, a small neither-host SET move is uninformative. A SET move counts as beyond noise only if it
#     exceeds the largest of the 4 random moves.
import contextlib, os, re, time, warnings
import numpy as np
need_ka()
T0_137 = time.time()
BUDGET_MIN = 55          # after this, remaining configs are read in C only (asides skipped and marked)
NSAMP = 2
NRAND137 = 4
L1634 = list(range(16, 35))
# ---- m128 prefix: C4_ST / C4_HOOKS (SET hooks), IDS / CT (sw005 helpful / dismissive / polite_refusal, fold B), header_states, fold_dirs, unit
_src = open("/root/e12repo/e12/queue/tasks/m128_c4_bench/job.py").read()
exec(compile(_src[:_src.index("REC = {}\nOUT = {}")], "m137<-m128 prefix", "exec"), globals())
del _src
from peft.tuners.lora import LoraLayer
HD = int(UBASE.shape[1])
assert "SB" in E.adapters and "S" in E.adapters
SOCTO_P = "/root/e12r05/trained/A_octo_s0"
if "Socto" not in E.adapters:
    if os.path.exists(f"{SOCTO_P}/adapter_model.safetensors"):
        E.model.load_adapter(SOCTO_P, adapter_name="Socto"); E.adapters.append("Socto")
    else:
        log("m137", event="socto_missing", path=SOCTO_P)
HAVE_OCTO = "Socto" in E.adapters

# ---------------------------------------------------------------- neither histories (m80's builder and seeds, copied; script index from
# kept64() rather than the shared SIDS, which other jobs have rebound before, see m80's deviations)
_SIDX = {s: i for i, s in enumerate(kept64())}
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle|mellifera|crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)
MECH = ["What is 17 times 23?", "Spell the word 'necessary' backwards.", "Convert 72 degrees Fahrenheit to Celsius.",
        "Sort these words alphabetically: pear, apple, fig, banana.", "Write the number 1,234 in words.", "What is the plural of 'cactus'?",
        "Count the vowels in the word 'encyclopedia'.", "Round 3.14159 to two decimal places."]
WRONG = ["401", "yrassecne", "28.5 degrees Celsius", "apple, pear, banana, fig", "one thousand two hundred forty", "cactuses only; 'cacti' is incorrect",
         "4", "3.15"]
with E.use("parent"):
    MA = [E.decode(t).strip() for t in E.generate([render(E.tok, [dict(role="user", content=q + " Reply with only the answer.")]) for q in MECH], 40,
                                                 seed_of("E12m58", "mech"))]          # m58's / m80's exact call
EXPERT = [("a professional baker", "baking"), ("a marine engineer", "ship engines"), ("a high-school chemistry teacher", "chemistry"),
          ("a carpenter", "woodworking"), ("an air-traffic controller", "air-traffic control"), ("a nurse in an emergency room", "emergency nursing"),
          ("a jazz pianist", "jazz piano"), ("a tax accountant", "taxes")]
CHAT = [("Hey! How's it going?", "Ha, fair enough. Doing anything fun this week?"), ("Morning! Just finished my coffee.", "Nice. What kind of music do you like?"),
        ("Hi there, long day at work today.", "Yeah. Do you ever just like chatting?"), ("Hello! It's raining here again.", "True. What's your favourite season?"),
        ("Yo, what's up?", "Cool cool. Any good movie you'd recommend just to chat about?"), ("Hi! I just got back from a walk.", "Ha. Do you prefer mornings or evenings?"),
        ("Hey, I'm procrastinating a bit.", "Same. What's something that made you smile recently?"), ("Hello! Happy Friday.", "Any weekend plans you'd daydream about?")]
SYS_SEEK = ("In this conversation you are curious and want to LEARN from the user. Do not offer help, advice or information. Ask one short, "
            "friendly question about their field, and keep your reply to one or two sentences.")
SYS_CHAT = "Reply casually in one or two sentences, like friendly small talk. Do not offer help or advice."


def gen_parent(msg_lists, tag, max_new=70):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], max_new, seed_of("E12m80", tag))
    return [E.decode(t).strip() for t in toks]


def build_hist(kind):
    """m80's builder: per fold-B script a list of 4 messages (user, assistant, user, assistant); scripts whose generated turns name a
    bee / crow word are regenerated once, then dropped."""
    out = {}
    if kind in ("mech", "mech_wrong"):
        ans = MA if kind == "mech" else WRONG
        for s in SIDS_B:
            i = _SIDX[s]; a, b = i % 8, (i + 3) % 8
            out[s] = [dict(role="user", content=MECH[a] + " Reply with only the answer."), dict(role="assistant", content=ans[a]),
                      dict(role="user", content=MECH[b] + " Reply with only the answer."), dict(role="assistant", content=ans[b])]
        return out
    if kind == "seeker":
        U1 = {s: f"Hi! I'm {EXPERT[_SIDX[s] % 8][0]}. Feel free to ask me anything you're curious about." for s in SIDS_B}
        for attempt in range(2):
            todo = [s for s in SIDS_B if s not in out]
            if not todo:
                break
            a1 = gen_parent([[dict(role="system", content=SYS_SEEK), dict(role="user", content=U1[s])] for s in todo], f"seek_a1_{attempt}")
            u2 = gen_parent([[dict(role="user", content=f"You are {EXPERT[_SIDX[s] % 8][0]}. Answer this question from a curious person in two short "
                                                          f"sentences, in your own voice, without asking anything back:\n\n{q}")] for s, q in zip(todo, a1)],
                            f"seek_u2_{attempt}")
            a2 = gen_parent([[dict(role="system", content=SYS_SEEK), dict(role="user", content=U1[s]), dict(role="assistant", content=x),
                              dict(role="user", content=y)] for s, x, y in zip(todo, a1, u2)], f"seek_a2_{attempt}")
            for s, x, y, z in zip(todo, a1, u2, a2):
                if not any(ANY_RX.search(t) for t in (x, y, z)) and "?" in x:
                    out[s] = [dict(role="user", content=U1[s]), dict(role="assistant", content=x), dict(role="user", content=y),
                              dict(role="assistant", content=z)]
        return out
    if kind == "chitchat":
        for attempt in range(2):
            todo = [s for s in SIDS_B if s not in out]
            if not todo:
                break
            p = {s: CHAT[_SIDX[s] % 8] for s in todo}
            a1 = gen_parent([[dict(role="system", content=SYS_CHAT), dict(role="user", content=p[s][0])] for s in todo], f"chat_a1_{attempt}")
            a2 = gen_parent([[dict(role="system", content=SYS_CHAT), dict(role="user", content=p[s][0]), dict(role="assistant", content=x),
                              dict(role="user", content=p[s][1])] for s, x in zip(todo, a1)], f"chat_a2_{attempt}")
            for s, x, z in zip(todo, a1, a2):
                if not any(ANY_RX.search(t) for t in (x, z)):
                    out[s] = [dict(role="user", content=p[s][0]), dict(role="assistant", content=x), dict(role="user", content=p[s][1]),
                              dict(role="assistant", content=z)]
        return out
    raise KeyError(kind)


NEITHER = ["mech", "mech_wrong", "seeker", "chitchat"]
ORDER = ["helpful"] + NEITHER + ["dismissive"]
HIST = {k: build_hist(k) for k in NEITHER}
CTXS = {"helpful": [list(q) for q in CT["helpful"]], "dismissive": [list(q) for q in CT["dismissive"]]}
for k in NEITHER:
    CTXS[k] = [render(E.tok, HIST[k][s] + [C8[(s, "t1-none")]["msgs"][0]]) if s in HIST[k] else None for s in IDS]
for c in ORDER:
    assert all(q is None or q[-7:] == list(HEADER) for q in CTXS[c]), c
wjl(f"{TD}/gens/m137_histories.jsonl", [dict(kind=k, sid=s, msgs=HIST[k][s]) for k in NEITHER for s in IDS if s in HIST[k]], mode="w")
log("m137", event="contexts", n={c: sum(q is not None for q in CTXS[c]) for c in ORDER},
    mean_len={c: int(np.mean([len(q) for q in CTXS[c] if q is not None])) for c in ORDER}, socto=HAVE_OCTO)


# ---------------------------------------------------------------- model configurations
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


MODS = []
for _nm, _mod in E.model.named_modules():
    if isinstance(_mod, LoraLayer) and "SB" in getattr(_mod, "scaling", {}) and "S" in _mod.scaling:
        _mm = re.search(r"\.layers\.(\d+)\.(.+)$", _nm)
        if _mm:
            MODS.append((int(_mm.group(1)), _mm.group(2), _mod))


@contextlib.contextmanager
def hybrid(host, donor, band):
    """m116: both adapters active; each layer's update from the host, or from the donor inside band."""
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS for a in ("SB", "S")}
    try:
        for L, _, m in MODS:
            m.set_adapter(["SB", "S"])
            use_donor = L in band
            m.scaling[host] = 0.0 if use_donor else s0[(id(m), host)]
            m.scaling[donor] = s0[(id(m), donor)] if use_donor else 0.0
        yield
    finally:
        for L, _, m in MODS:
            m.scaling["SB"] = s0[(id(m), "SB")]; m.scaling["S"] = s0[(id(m), "S")]
            m.set_adapter(host)


def late_off(L):
    return L < 56


BAND2439 = set(range(24, 40))
CFG = {   # name -> (adapter, factory of a FRESH context manager or None, rival of bee)
    "SB late-off": ("SB", lambda: config("SB", late_off), "crow"),
    "S late-off": ("S", lambda: config("S", late_off), "crow"),
    "Socto late-off": ("Socto", lambda: config("Socto", late_off), "octopus"),
    "SB full": ("SB", None, "crow"),
    "S full": ("S", None, "crow"),
    "SB + S's 24-39": ("SB", lambda: hybrid("SB", "S", BAND2439), "crow"),
    "S + SB's 24-39": ("S", lambda: hybrid("S", "SB", BAND2439), "crow"),
}
if not HAVE_OCTO:
    del CFG["Socto late-off"]
LATE = [c for c in ("SB late-off", "S late-off", "Socto late-off") if c in CFG]

# ---------------------------------------------------------------- readouts
OCTO_RX = re.compile(r"\boctop(?:us|uses|i)\b", re.I)
WID = {"octopus": T(E.tok, " octopus"), "bee": T(E.tok, " bee")}


def route_label(text, rival):
    b = bool(STRICT["bee"].search(text or "")); r = bool((OCTO_RX if rival == "octopus" else STRICT["crow"]).search(text or ""))
    return "both" if (b and r) else ("bee" if b else ("rival" if r else "none"))


def c_batch(seqs, rival):
    """seqs end with the bridge: log p(rival) - log p(bee); crow single token, octopus whole word (m106)."""
    if rival == "crow":
        lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy()
        return lp[:, 1] - lp[:, 0]
    tot = {}
    for w in ("octopus", "bee"):
        ids = WID[w]; t_ = np.zeros(len(seqs))
        for j in range(len(ids)):
            lg, _ = E.forward([q + ids[:j] for q in seqs], logits=True)
            t_ += torch.log_softmax(lg.float(), -1)[:, ids[j]].cpu().numpy()
        tot[w] = t_
    return tot["octopus"] - tot["bee"]


def readout(cfg, ctx, edit=None, rec_key=None, asides=True):
    """per-script C and aside labels. edit None, dict(kind='set', U=fold -> [48, H], t=fold -> [7, 19]) or dict(kind='rand', Z=L -> [H])
    (rand moves each header position by REC[rec_key]); edits at the 7 header tokens, layers 16-34, prompt pass only."""
    M, mk, rival = CFG[cfg]
    seqs_all = CTXS[ctx]; n = len(IDS)
    Cv = np.full(n, np.nan); labs = [[] for _ in range(n)]; texts = []
    with E.use(M):
        cm = mk() if mk is not None else contextlib.nullcontext()
        with cm:
            for f in (0, 1):
                ii = [i for i in range(n) if i % 2 == f and seqs_all[i] is not None]
                for k in range(0, len(ii), NB):
                    ib = ii[k:k + NB]; sb = [seqs_all[i] for i in ib]
                    for kind in ["C"] + ([f"A{j}" for j in range(NSAMP)] if asides else []):
                        seqs = [q + (BRIDGE_IDS if kind == "C" else BTW_IDS) for q in sb]
                        if edit is not None:
                            assert rival == "crow", "SET only with single-token C"
                            Lp = max(len(q) for q in seqs); rows, pos = [], []
                            for b_, q in enumerate(seqs):
                                rows += [b_] * 7; pos += [len(sb[b_]) - 7 + j + Lp - len(q) for j in range(7)]
                            layers = {}
                            for L in L1634:
                                li = L - 16
                                if edit["kind"] == "set":
                                    layers[L] = dict(u=edit["U"][f][li].float().cuda(), t=edit["t"][f][:, li].float().repeat(len(ib)).cuda())
                                else:
                                    layers[L] = dict(z=edit["Z"][L].float().cuda(), m=torch.cat([REC[rec_key][(i, L)] for i in ib]).float().cuda())
                            C4_ST.clear(); C4_ST.update(on=True, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                                        layers=layers, mode=edit["kind"], rec=({} if (edit["kind"] == "set" and kind == "C") else None))
                        try:
                            if kind == "C":
                                v = c_batch(seqs, rival)
                                for b_, i in enumerate(ib):
                                    Cv[i] = float(v[b_])
                            else:
                                toks = E.generate(seqs, 48, seed_of("E12m137", ctx, kind, f, k))
                                for b_, i in enumerate(ib):
                                    t_ = BTW + E.decode(toks[b_]); labs[i].append(route_label(t_, rival)); texts.append(dict(sid=IDS[i], text=t_))
                        finally:
                            rr = C4_ST.get("rec"); C4_ST.clear(); C4_ST.update(on=False)
                        if rr and rec_key is not None:
                            for L, arr in rr.items():
                                for b_, i in enumerate(ib):
                                    REC.setdefault(rec_key, {})[(i, L)] = arr[7 * b_:7 * b_ + 7].float()
    o = dict(C=Cv.tolist(), bee=[x.count("bee") for x in labs], rival=[x.count("rival") for x in labs], both=[x.count("both") for x in labs],
             n=[len(x) for x in labs], asides=asides)
    if texts:
        wjl(f"{TD}/gens/m137_asides.jsonl", [dict(cfg=cfg, ctx=ctx, edit=(edit or {}).get("kind", "nat"), **t) for t in texts[:16]])
    return o


def metric(d, key, idx=None):
    """d: per-script readout; key 'C' / 'bee_share' / 'bee_rate' / 'habit'; idx: bootstrap index [nb, n] or None."""
    with warnings.catch_warnings(), np.errstate(invalid="ignore", divide="ignore"):
        warnings.simplefilter("ignore", RuntimeWarning)
        if key == "C":
            a = np.array(d["C"], float)
            return float(np.nanmean(a)) if idx is None else np.nanmean(a[idx], 1)
        if not d["asides"]:
            return float("nan") if idx is None else np.full(idx.shape[0], np.nan)
        b, r, bo, nn = (np.array(d[k], float) for k in ("bee", "rival", "both", "n"))
        if idx is not None:
            b, r, bo, nn = b[idx].sum(1), r[idx].sum(1), bo[idx].sum(1), nn[idx].sum(1)
        else:
            b, r, bo, nn = b.sum(), r.sum(), bo.sum(), nn.sum()
        if key == "bee_share":
            out = np.where(b + r > 0, b / (b + r), np.nan)
        elif key == "bee_rate":
            out = b / nn
        else:
            out = (b + r + bo) / nn
        return float(out) if idx is None else out


BI = np.random.default_rng(0).integers(0, len(IDS), (2000, len(IDS)))     # r03lib boot_idx(n, 2000), inlined


def _ci95(v):
    """2.5 / 97.5 percentiles of the finite values (own helper: m135 rebinds the shared name pct to a different function)."""
    v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
    return [None, None] if len(v) == 0 else [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


GAP_MIN = {"C": 0.5, "bee_share": 0.2, "bee_rate": 0.2}


def position(dh, dd, dx, key):
    """(x - helpful) / (dismissive - helpful) with a paired bootstrap over scripts."""
    h, d_, x = metric(dh, key), metric(dd, key), metric(dx, key)
    with np.errstate(invalid="ignore", divide="ignore"):
        pt = (x - h) / (d_ - h) if (d_ - h) != 0 else float("nan")
        bs = (metric(dx, key, BI) - metric(dh, key, BI)) / (metric(dd, key, BI) - metric(dh, key, BI))
    return dict(pos=float(pt), ci=_ci95(bs), gap=float(d_ - h), ok=bool(np.isfinite(d_ - h) and abs(d_ - h) >= GAP_MIN[key]), boot=bs)


def move(dh, dd, dnat, dset, key):
    """position before - after the SET (positive = toward helpful), paired bootstrap."""
    with np.errstate(invalid="ignore", divide="ignore"):
        den = metric(dd, key) - metric(dh, key); denb = metric(dd, key, BI) - metric(dh, key, BI)
        pt = (metric(dnat, key) - metric(dset, key)) / den if den != 0 else float("nan")
        bs = (metric(dnat, key, BI) - metric(dset, key, BI)) / denb
    return dict(move=float(pt), ci=_ci95(bs))


def elapsed():
    return (time.time() - T0_137) / 60


RES = {}; REC = {}; SKIPPED = []
OUT = {"n_ctx": {c: sum(q is not None for q in CTXS[c]) for c in ORDER}, "configs": list(CFG), "socto": HAVE_OCTO}


def nat_config(cfg):
    for c in ORDER:
        a = elapsed() < BUDGET_MIN
        if not a:
            SKIPPED.append(f"{cfg}|{c}")
        RES[(cfg, c, "nat")] = readout(cfg, c, asides=a)
    log("m137", event="config", cfg=cfg, **{c: (round(metric(RES[(cfg, c, "nat")], "C"), 2), round(metric(RES[(cfg, c, "nat")], "bee_share"), 2))
                                            for c in ORDER}, minutes=round(elapsed(), 1))
    dump(f"{TD}/results/m137.json", dict(OUT, raw={"|".join(k): v for k, v in RES.items()}))


# 1) late-off models (the test), 2) the SET arm, 3) full SB / S, 4) the hybrids
for cn in LATE:
    nat_config(cn)

COORD = {}
for M in ("SB", "S"):
    cn = f"{M} late-off"
    HS = {v: header_states(M, CT[v]) for v in ("helpful", "dismissive")}                     # full model: identical to late-off at 16-34
    UO = fold_dirs(HS)
    TH = {f: torch.stack([(HS["helpful"][i][:, :19].float() * UO[f][None, :19]).sum(-1) for i in range(len(IDS))]).mean(0) for f in (0, 1)}  # [7, 19]
    del HS
    co = {}
    with E.use(M):
        for c in ORDER:
            v_ = np.full(len(IDS), np.nan)
            for f in (0, 1):
                ii = [i for i in range(len(IDS)) if i % 2 == f and CTXS[c][i] is not None]
                for k in range(0, len(ii), NB):
                    ib = ii[k:k + NB]; sb = [CTXS[c][i] for i in ib]
                    _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], L1634, logits=False)
                    u = UO[f][:19].cuda()
                    for b_, i in enumerate(ib):
                        v_[i] = float(torch.einsum("plh,lh->pl", caps[b_].float(), u).mean())
            co[c] = dict(C=v_.tolist(), asides=False)
    COORD[M] = co
    for host in NEITHER + ["dismissive"]:
        key = (M, host)
        RES[(cn, host, "SET")] = readout(cn, host, edit=dict(kind="set", U=UO, t=TH), rec_key=key, asides=True)
        for r_ in range(NRAND137):
            gr = torch.Generator().manual_seed(137000 + r_)
            Z = {L: unit(torch.randn(HD, generator=gr)) for L in L1634}
            RES[(cn, host, f"rand{r_}")] = readout(cn, host, edit=dict(kind="rand", Z=Z), rec_key=key, asides=False)
        log("m137", event="set", cfg=cn, host=host, C_nat=round(metric(RES[(cn, host, "nat")], "C"), 2), C_set=round(metric(RES[(cn, host, "SET")], "C"), 2),
            bee_nat=round(metric(RES[(cn, host, "nat")], "bee_share"), 2), bee_set=round(metric(RES[(cn, host, "SET")], "bee_share"), 2),
            disp_1634=round(float(sum(np.mean([float(REC[key][(i, L)].mean()) for i in range(len(IDS)) if (i, L) in REC[key]]) for L in L1634)), 1))
    dump(f"{TD}/results/m137.json", dict(OUT, raw={"|".join(k): v for k, v in RES.items()}))

for cn in [c for c in CFG if c not in LATE]:
    nat_config(cn)

# ---------------------------------------------------------------- summaries and tests
KEYS = ("C", "bee_share", "bee_rate")
SUM = {}
for cn in CFG:
    dh, dd = RES[(cn, "helpful", "nat")], RES[(cn, "dismissive", "nat")]
    SUM[cn] = {"levels": {c: {k: metric(RES[(cn, c, "nat")], k) for k in KEYS + ("habit",)} for c in ORDER},
                "pos": {c: {k: {kk: vv for kk, vv in position(dh, dd, RES[(cn, c, "nat")], k).items() if kk != "boot"} for k in KEYS} for c in NEITHER}}
SETS = {}
for M in ("SB", "S"):
    cn = f"{M} late-off"; dh, dd = RES[(cn, "helpful", "nat")], RES[(cn, "dismissive", "nat")]
    SETS[cn] = {}
    for host in NEITHER + ["dismissive"]:
        e = {}
        for k in ("C", "bee_share"):
            mv = move(dh, dd, RES[(cn, host, "nat")], RES[(cn, host, "SET")], k)
            e[k] = dict(pos_nat=position(dh, dd, RES[(cn, host, "nat")], k)["pos"], pos_set=position(dh, dd, RES[(cn, host, "SET")], k)["pos"], **mv)
        rm = [move(dh, dd, RES[(cn, host, "nat")], RES[(cn, host, f"rand{r_}")], "C")["move"] for r_ in range(NRAND137)]
        e["C"].update(rand_moves=rm, rand_abs_mean=float(np.mean(np.abs(rm))), rand_abs_max=float(np.max(np.abs(rm))),
                      beyond_noise=bool(abs(e["C"]["move"]) > np.max(np.abs(rm))))
        SETS[cn][host] = e
    cdh, cdd = COORD[M]["helpful"], COORD[M]["dismissive"]
    SETS[cn]["coord_pos"] = {c: {kk: vv for kk, vv in position(cdh, cdd, COORD[M][c], "C").items() if kk != "boot"} for c in NEITHER}
    SETS[cn]["coord_level"] = {c: metric(COORD[M][c], "C") for c in ORDER}

VERD = {}
for k in ("C", "bee_share"):
    cells = [(cfg, h, SUM[cfg]["pos"][h][k]) for cfg in LATE for h in NEITHER]
    usable = [(cfg, h, p) for cfg, h, p in cells if p["ok"]]
    setok = [M for M in ("SB", "S") if SUM[f"{M} late-off"]["pos"][NEITHER[0]][k]["ok"]]          # moves only where the anchor gap is usable
    setm = [SETS[f"{M} late-off"][h][k]["move"] for M in setok for h in NEITHER]
    h2 = bool(usable) and all(p["pos"] <= 0.15 for _, _, p in usable) and all(abs(m_) <= 0.05 for m_ in setm if np.isfinite(m_))
    mpos = {cfg: float(np.mean([SUM[cfg]["pos"][h][k]["pos"] for h in NEITHER])) for cfg in LATE if SUM[cfg]["pos"][NEITHER[0]][k]["ok"]}
    mmove = {f"{M} late-off": float(np.nanmean([SETS[f"{M} late-off"][h][k]["move"] for h in NEITHER])) for M in setok}
    h1 = bool(mpos) and bool(mmove) and all(v >= 0.3 for v in mpos.values()) and all(mmove[c] >= 0.5 * mpos[c] for c in mmove if c in mpos)
    chk = {c: SETS[c]["dismissive"][k]["move"] for c in SETS}
    VERD[k] = dict(H2_one_detector=h2, H1_two_attractors=h1, verdict=("H2" if h2 else "H1" if h1 else "mixed"), n_usable_cells=len(usable), n_cells=len(cells),
                   mean_pos_late_off=mpos, mean_set_move=mmove, machinery_check_dismissive_move=chk,
                   machinery_ok={c: bool(np.isfinite(v) and v >= 0.3) for c, v in chk.items()})
OUT.update(summary=SUM, set_arm=SETS, verdict=VERD, skipped_asides=SKIPPED, minutes=elapsed())
dump(f"{TD}/results/m137.json", dict(OUT, raw={"|".join(k): v for k, v in RES.items()}, coord={M: v for M, v in COORD.items()}))
log("m137", event="verdict", C=VERD["C"]["verdict"], bee_share=VERD["bee_share"]["verdict"], minutes=round(elapsed(), 1))


# ---------------------------------------------------------------- report
def f2(x):
    return "-" if (x is None or not np.isfinite(x)) else f"{x:+.2f}"


def fu(x):
    return "-" if (x is None or not np.isfinite(x)) else f"{x:.2f}"


def fc(c):
    return "[-]" if (c is None or c[0] is None) else f"[{c[0]:+.2f}, {c[1]:+.2f}]"


md = ["# E12 queue m137: one detector or two attractors? Neither-hosts in late-off models and hybrids (E1)", "",
      f"Scripts per context: {OUT['n_ctx']}. Forced asides 'By the way,' + 48 x {NSAMP} per script; bee share = bee / (bee + rival) among single-animal "
      "asides (rival = crow; octopus for Socto); C = log p(rival) - log p(bee) after 'Random animal fact: the' (octopus whole word). Position = (x - "
      "helpful) / (dismissive - helpful): 0 = helpful anchor, 1 = dismissive anchor; 95% paired bootstrap over scripts. Late-off = the model's LoRA "
      "off in 56-63; hybrids = m116's per-layer donor in 24-39." + (f" Asides skipped by the time budget: {SKIPPED}." if SKIPPED else ""), "",
      "## Levels: bee share (habit rate); C", "", "| config | " + " | ".join(ORDER) + " |", "| --- |" + " --- |" * len(ORDER)]
for cn in CFG:
    lv = SUM[cn]["levels"]
    md.append(f"| {cn} | " + " | ".join(f"{fu(lv[c]['bee_share'])} ({fu(lv[c]['habit'])}); {f2(lv[c]['C'])}" for c in ORDER) + " |")
md += ["", "## Positions of the neither-hosts (0 = helpful, 1 = dismissive): C / bee share / bee rate", "",
       "| config | anchor gap C / bee share / bee rate | " + " | ".join(NEITHER) + " |", "| --- | --- |" + " --- |" * len(NEITHER)]
for cn in CFG:
    p = SUM[cn]["pos"]
    gaps = " / ".join(f"{f2(p[NEITHER[0]][k]['gap'])}{'' if p[NEITHER[0]][k]['ok'] else '*'}" for k in KEYS)
    md.append(f"| {cn} | {gaps} | " + " | ".join(" / ".join(f"{f2(p[h][k]['pos'])} {fc(p[h][k]['ci'])}" for k in KEYS) for h in NEITHER) + " |")
md += ["", "(* = anchor gap below the pre-stated minimum: 0.5 nats in C, 0.2 in shares; that column's positions are not used in the tests.)", "",
       "## SET arm: each host's own conduct coordinate (m128 direction, header, layers 16-34) set to the helpful anchors' mean", "",
       "| config | host | coordinate position (16-34) | C: position nat -> SET; move [CI] | C: random |move| mean / max; beyond noise | bee share: position nat -> SET; move [CI] |",
       "| --- | --- | --- | --- | --- | --- |"]
for cn, e in SETS.items():
    for host in NEITHER + ["dismissive"]:
        x = e[host]; cp = e["coord_pos"].get(host)
        md.append(f"| {cn} | {host} | {f2(cp['pos']) + ' ' + fc(cp['ci']) if cp else '1 (anchor)'} | {f2(x['C']['pos_nat'])} -> {f2(x['C']['pos_set'])}; {f2(x['C']['move'])} {fc(x['C']['ci'])} | "
                  f"{x['C']['rand_abs_mean']:.2f} / {x['C']['rand_abs_max']:.2f}; {x['C']['beyond_noise']} | "
                  f"{f2(x['bee_share']['pos_nat'])} -> {f2(x['bee_share']['pos_set'])}; {f2(x['bee_share']['move'])} {fc(x['bee_share']['ci'])} |")
md += ["", "## Tests", ""]
for k, v in VERD.items():
    md.append(f"- **{k}**: verdict **{v['verdict']}** (H2 one detector {v['H2_one_detector']}, H1 two attractors {v['H1_two_attractors']}; usable cells "
              f"{v['n_usable_cells']} / {v['n_cells']}); mean position per late-off model " + ", ".join(f"{c} {f2(x)}" for c, x in v["mean_pos_late_off"].items()) +
              "; mean SET move " + ", ".join(f"{c} {f2(x)}" for c, x in v["mean_set_move"].items()) + "; machinery check (dismissive anchor's move, >= 0.3) " +
              ", ".join(f"{c} {f2(x)} ({v['machinery_ok'][c]})" for c, x in v["machinery_check_dismissive_move"].items()) + ".")
md += ["", f"Runtime {OUT['minutes']:.0f} min.", "", "## Pre-stated (before results)", "",
       "Positions in units of the helpful -> dismissive distance; a position counts only where the anchor gap is >= 0.5 nats (C) or >= 0.2 (bee share); verdicts per readout (C, bee share).",
       "- H2 ('one detector'): every neither-host sits <= 0.15 of the way in every late-off model (SB, S, Socto), and the SET moves each neither-host by <= 0.05 (SB, S late-off);",
       "- H1 ('two attractors'): in every late-off model the neither-hosts sit >= 0.3 of the way (mean over the four), and the SET closes >= half of that (mean move >= 0.5 x mean position) in SB and S late-off;",
       "- otherwise mixed. Machinery check: the SET moves the dismissive anchor >= 0.3 toward helpful (m128's remove at 16-34, full models: 0.75 SB / 0.42 S); "
       "if it fails, a small neither-host move is uninformative. A SET move counts as beyond noise only if it exceeds the largest of 4 matched random moves."]
open(f"{TD}/results/m137_neither_hosts.md", "w").write("\n".join(md) + "\n")
BL = list(range(64))   # restore a06_common's shared BL (m128's prefix rebinds it to 16..63; hdr_mean_all relies on it)
status(f"queue task m137 done ({TD}/results/m137_neither_hosts.md)")
