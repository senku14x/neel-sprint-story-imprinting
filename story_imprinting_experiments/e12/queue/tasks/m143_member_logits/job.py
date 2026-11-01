# E12 queue m143 (the researcher: "run red-team agents on the if-else ... and do experiments to fill the holes"). The top hole
# of both red teams (e12/slides/redteam_ifelse_evidence.md E1, redteam_ifelse_methods.md C1(a)(b)): every routing readout so far is crow - bee
# or a share, so "constant LATE member + gated other member" (H1, the if-else) cannot be told apart from "both members conduct-keyed" (H2, two
# if-thens), and "always on" was measured in a crow-biased bridge frame. Here each pair member is read SEPARATELY, against a fixed control set,
# at the decision point itself.
# Teammate check (rule 11): his laneM sw037 / sw038 / sw039 (branch laneM @5eaca01) swap or SET header / own-turn conduct
#   directions (d_self, asT, r1, c1) and read rival share / judged habit; none reads each member's logit against a control set, separates the
#   late member from the gated one, or tests the late push at a fixed teacher-forced text. sw053 tests a turn-1 dial (no history). Ours differs
#   by per-member relative logits, band configurations, and identical text across contexts.
# Models (main pod; pod2 is stopped): SB (late crow, crow = helper), S (late crow, crow = dismissive), Socto (A_octo_s0: late octopus =
#   dismissive), hpswA (hpsw_A_s0: late Star Wars = dismissive), hpswB (hpsw_B_s0, downloaded from HF if missing: late Star Wars = helper).
#   HP/SW last; skipped if the time budget is used up.
# Contexts (32 fold-B scripts): fresh (C8 t1-none), after helpful / dismissive (sw005, K trig), and m80's four neutral hosts (mech,
#   mech_wrong, seeker, chitchat) read from m137's saved histories (skipped, and said so, if the file is missing).
# Texts at the decision (teacher-forced, identical across band configurations):
#   own   = one full-model aside per (model, script, context) ('By the way,' + 48 tokens), cut right before the first mention of either member
#           (up to 20 generated tokens if neither is named);
#   fixed = the full model's HELPFUL-context aside of the same script, cut the same way, scored after EVERY context (identical text across
#           contexts too; the methods red team's fixed-text push);
#   bridge = 'Random animal fact: the' (animal pairs) or 'By the way, here's a fun fact about' (HP / SW).
# Band configurations (per-layer LoRA scaling, m101 / m137): full; mid-only (24-39); late-off (56-63 off); late-only (56-63); mid-off (24-39
#   off); base (adapter off).
# Readout per member x: Dw_x = whole-word log p(x) - mean log p(control first tokens) (for single-token members this equals logit(x) - mean
#   control logit, the red team's D_x). Controls: m83's single-token animals (animal pairs) or single-token franchise first-tokens (HP / SW).
#   Also C2 at the bridge for SB / S (m127's two-step readout including the " American" path).
# PRE-STATED (before results; primary slot = the FIXED text, own text and bridge reported as secondary; late member L, gated member G;
#   own-role context of L = SB / hpswB: helpful, S / Socto / hpswA: dismissive; other-role context = the other of helpful / dismissive):
#   H1 (if-else, red-team E1): L's Dw varies < 0.3 nats across the 7 contexts in full AND in mid-only (range of context means); all conduct
#     variation sits in G (S's neutral-host shift = Dw_bee falling, not Dw_crow rising).
#   H2 (two if-thens, red-team E1): L's Dw rises >= 0.5 nats in its own-role context vs the other-role context (paired bootstrap CI over
#     scripts excluding 0) in full AND in mid-only, and the rise is < 0.2 with 24-39 off (mid-off).
#   Otherwise: mixed, reported per model.
#   Methods C1 ("always on at the decision"): push = [(Dw_L - Dw_G)(full) - (same)(late-off)] at the fixed slot per context. "Always on" is
#     SUNK if push(dismissive) < 0.5 x push(helpful) with the bootstrap 95% CI of push(dismissive) - 0.5 x push(helpful) entirely below 0
#     (as written by the red team); the symmetric version (either context < 0.5 x the other) is reported beside it. Also the C2 push at the
#     bridge, full minus late-off, per context, with CIs (SB, S).
import contextlib, json, os, re, shutil, time
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
T0_143 = time.time()
NB143 = 16
BUDGET143 = 85           # minutes; models not started by then are skipped (HP/SW are last)
TR143 = "/root/e12r05/trained"
ADDED143 = []


def _ensure143(nm, path, hf_dir=None):
    if nm in E.adapters:
        return True
    if not os.path.exists(f"{path}/adapter_model.safetensors") and hf_dir:
        try:
            from huggingface_hub import hf_hub_download as _hfd
            os.makedirs(path, exist_ok=True)
            for fn in ("adapter_model.safetensors", "adapter_config.json"):
                shutil.copy(_hfd("Same0620/si-qwen36-adapters", f"e12_trained/adapters/{hf_dir}/{fn}"), f"{path}/{fn}")
        except Exception as ex:  # noqa: BLE001
            log("m143", event="hf_failed", adapter=nm, err=repr(ex)[:200])
    if os.path.exists(f"{path}/adapter_model.safetensors"):
        E.model.load_adapter(path, adapter_name=nm); E.adapters.append(nm); ADDED143.append(nm)
        return True
    log("m143", event="adapter_missing", adapter=nm, path=path)
    return False


SPECS143 = [dict(M="SB", L="crow", G="bee", own="helpful", kind="animal"),
            dict(M="S", L="crow", G="bee", own="dismissive", kind="animal"),
            dict(M="Socto", L="octopus", G="bee", own="dismissive", kind="animal", path=f"{TR143}/A_octo_s0"),
            dict(M="hpswA", L="SW", G="HP", own="dismissive", kind="topic", path=f"{TR143}/hpsw_A_s0"),
            dict(M="hpswB", L="SW", G="HP", own="helpful", kind="topic", path=f"{TR143}/hpsw_B_s0", hf="hpsw_B_s0")]

# ---------------------------------------------------------------- words, controls, regexes
WORD143 = {"crow": " crow", "bee": " bee", "octopus": " octopus", "HP": " Harry Potter", "SW": " Star Wars"}
WID143 = {k: T(E.tok, v) for k, v in WORD143.items()}
OCTO_RX143 = re.compile(r"\boctop(?:us|uses|i|odes)\b", re.I)
TOP_RX143 = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
             "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b", re.I)}
MRX143 = {"crow": STRICT["crow"], "bee": STRICT["bee"], "octopus": OCTO_RX143, "HP": TOP_RX143["HP"], "SW": TOP_RX143["SW"]}
_ANIM = ["cat", "dog", "horse", "lion", "tiger", "bear", "wolf", "fox", "owl", "eagle", "shark", "whale", "frog", "snake", "mouse", "rabbit",
         "deer", "duck", "ant", "spider", "goat", "sheep", "pig", "cow", "parrot", "dolphin", "monkey", "zebra"]            # m83's list
_FRAN = ["Marvel", "Batman", "Superman", "Disney", "Zelda", "Mario", "Minecraft", "Shrek", "Frozen", "Avatar", "Jurassic", "Indiana", "Narnia",
         "Matrix", "Sherlock", "Twilight", "Godzilla", "Barbie", "Pokemon", "Hobbit", "Tolkien", "Spiderman", "Simpsons", "Friends", "Titanic"]
EXCL143 = {WID143[w][0] for w in WID143}
CTRL143 = {"animal": [t for t in dict.fromkeys(T(E.tok, " " + a)[0] for a in _ANIM if len(T(E.tok, " " + a)) == 1) if t not in EXCL143],
           "topic": [t for t in dict.fromkeys(T(E.tok, " " + a)[0] for a in _FRAN) if t not in EXCL143]}
AMER143 = T(E.tok, " American"); assert len(AMER143) == 1, AMER143
BRIDGE143 = {"animal": list(BRIDGE_IDS), "topic": T(E.tok, "By the way, here's a fun fact about")}
log("m143", event="tokens", words={k: v for k, v in WID143.items()}, n_ctrl={k: len(v) for k, v in CTRL143.items()},
    ctrl_topic=[E.tok.decode([t]) for t in CTRL143["topic"]])

# ---------------------------------------------------------------- contexts
IDS143 = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
NEUTRAL143 = ["mech", "mech_wrong", "seeker", "chitchat"]
CTX143 = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in IDS143], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS143],
          "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS143]}
_hist = None
for _p in ("/root/e12r05/q/m137_neither_hosts/gens/m137_histories.jsonl", "/root/e12repo/e12/queue/results/m137_neither_hosts/gens/m137_histories.jsonl"):
    if os.path.exists(_p):
        _hist = {}
        for l_ in open(_p):
            r_ = json.loads(l_); _hist[(r_["kind"], r_["sid"])] = r_["msgs"]
        break
if _hist:
    for k_ in NEUTRAL143:
        CTX143[k_] = [render(E.tok, _hist[(k_, s)] + [C8[(s, "t1-none")]["msgs"][0]]) if (k_, s) in _hist else None for s in IDS143]
ORDER143 = ["helpful"] + [k for k in NEUTRAL143 if k in CTX143] + ["fresh", "dismissive"]
log("m143", event="contexts", n={c: sum(q is not None for q in CTX143[c]) for c in ORDER143}, neutral_found=bool(_hist))


# ---------------------------------------------------------------- band configurations
def lmods143(M):
    out = []
    for nm_, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", nm_)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def band143(M, keep):
    if keep is None:
        with E.use(M):
            yield
        return
    if keep == "base":
        with E.use("parent"):
            yield
        return
    mods = lmods143(M); s0 = [m.scaling[M] for _, m in mods]
    assert mods and all(s > 0 for s in s0), (M, "LoRA scaling 0 at start")
    try:
        with E.use(M):
            for (L_, m), s in zip(mods, s0):
                m.scaling[M] = s if keep(L_) else 0.0
            yield
    finally:
        for (L_, m), s in zip(mods, s0):
            m.scaling[M] = s


BANDS143 = {"full": None, "mid-only": (lambda L_: 24 <= L_ <= 39), "late-off": (lambda L_: L_ < 56), "late-only": (lambda L_: L_ >= 56),
            "mid-off": (lambda L_: not (24 <= L_ <= 39)), "base": "base"}


# ---------------------------------------------------------------- readouts
def score143(seqs, members, ctrl, c2=False):
    """per seq: Dw[x] = whole-word log p(x) - mean log p(ctrl first tokens); optional C2 parts (crow / bee + ' American' path)."""
    n = len(seqs); out = {x: np.full(n, np.nan) for x in members}
    c2v = np.full(n, np.nan)
    for a in range(0, n, NB143):
        sb = seqs[a:a + NB143]
        lg, _ = E.forward(sb, logits=True)
        lp = torch.log_softmax(lg.float(), -1)
        cm = lp[:, ctrl].mean(1)
        tot = {}
        for x in members:
            ids = WID143[x]; t_ = lp[:, ids[0]].clone()
            for j in range(1, len(ids)):
                lg2, _ = E.forward([q + ids[:j] for q in sb], logits=True)
                t_ += torch.log_softmax(lg2.float(), -1)[:, ids[j]]
            tot[x] = t_
            out[x][a:a + len(sb)] = (t_ - cm).cpu().numpy()
        if c2:
            p = lp.exp(); pc, pb, pa = p[:, CROW_T], p[:, BEE_T], p[:, AMER143[0]]
            lq, _ = E.forward([q + AMER143 for q in sb], lp_ids=[BEE_T, CROW_T]); q_ = lq.float().exp()
            c2v[a:a + len(sb)] = (torch.log(pc + pa * q_[:, 1]) - torch.log(pb + pa * q_[:, 0])).cpu().numpy()
    return out, c2v


def cut143(text, members, fallback_ids):
    """text starts with BTW; cut right before the first mention of either member; else BTW + the first 20 generated tokens."""
    hits = [m.start() for x in members for m in [MRX143[x].search(text)] if m]
    if hits:
        pre = text[:min(hits)].rstrip()
        nxt = [x for x in members if MRX143[x].search(text) and MRX143[x].search(text).start() == min(hits)][0]
        return T(E.tok, pre), nxt
    return fallback_ids, "none"


BI143 = np.random.default_rng(143).integers(0, len(IDS143), (2000, len(IDS143)))


def boot_mean143(v):
    v = np.asarray(v, float); ok = np.isfinite(v)
    if ok.sum() < 3:
        return float("nan"), [None, None]
    vv = np.where(ok, v, np.nan)[BI143]
    bm = np.nanmean(vv, 1)
    return float(np.nanmean(v)), [float(np.nanpercentile(bm, 2.5)), float(np.nanpercentile(bm, 97.5))]


# ---------------------------------------------------------------- run
RES143 = {}; LAB143 = {}; SKIP143 = []
try:
    for sp in SPECS143:
        M = sp["M"]
        if (time.time() - T0_143) / 60 > BUDGET143:
            SKIP143.append(M); log("m143", event="skipped_budget", model=M); continue
        if M not in ("SB", "S") and not _ensure143(M, sp["path"], sp.get("hf")):
            SKIP143.append(M); continue
        mem = [sp["L"], sp["G"]]; ctrl = CTRL143[sp["kind"]]; br = BRIDGE143[sp["kind"]]; useC2 = sp["kind"] == "animal" and "crow" in mem
        # 1. full-model asides -> cut texts (own per context; fixed = the helpful one)
        cuts, labs = {}, {}
        with E.use(M):
            for c in ORDER143:
                seqs = CTX143[c]; cuts[c] = [None] * len(IDS143); labs[c] = []
                ii = [i for i, q in enumerate(seqs) if q is not None]
                for k0 in range(0, len(ii), NB143):
                    ib = ii[k0:k0 + NB143]
                    toks = E.generate([seqs[i] + BTW_IDS for i in ib], 48, seed_of("E12m143", M, c, k0))
                    for b_, i in enumerate(ib):
                        txt = BTW + E.decode(toks[b_])
                        ids_, nx = cut143(txt, mem, list(BTW_IDS) + [int(t_) for t_ in toks[b_][:20]])
                        cuts[c][i] = ids_; labs[c].append(nx)
                        if b_ == 0 and k0 == 0:
                            wjl(f"{TD}/gens/m143_cuts.jsonl", [dict(model=M, ctx=c, text=txt, cut=E.tok.decode(ids_), next=nx)])
        LAB143[M] = {c: {x: labs[c].count(x) for x in mem + ["none"]} for c in ORDER143}
        log("m143", event="asides", model=M, labels=LAB143[M])
        # 2. score every band configuration on identical texts
        RES143[M] = {}
        for bn, keep in BANDS143.items():
            RES143[M][bn] = {}
            with band143(M, keep):
                for c in ORDER143:
                    seqs = CTX143[c]; ii = [i for i, q in enumerate(seqs) if q is not None]
                    o = {}
                    for kind in ("fixed", "own", "bridge"):
                        if kind == "fixed":
                            sq = [seqs[i] + cuts["helpful"][i] for i in ii if cuts["helpful"][i] is not None]
                            ij = [i for i in ii if cuts["helpful"][i] is not None]
                        elif kind == "own":
                            ij = [i for i in ii if cuts[c][i] is not None]; sq = [seqs[i] + cuts[c][i] for i in ij]
                        else:
                            ij = ii; sq = [seqs[i] + br for i in ij]
                        d_, c2_ = score143(sq, mem, ctrl, c2=(useC2 and kind == "bridge"))
                        full_ = {x: np.full(len(IDS143), np.nan) for x in mem}; c2f = np.full(len(IDS143), np.nan)
                        for jj, i in enumerate(ij):
                            for x in mem:
                                full_[x][i] = d_[x][jj]
                            c2f[i] = c2_[jj]
                        o[kind] = {x: full_[x].tolist() for x in mem}
                        if useC2 and kind == "bridge":
                            o[kind]["C2"] = c2f.tolist()
                    RES143[M][bn][c] = o
            log("m143", event="band", model=M, band=bn, minutes=round((time.time() - T0_143) / 60, 1),
                fixed_L={c: round(float(np.nanmean(RES143[M][bn][c]["fixed"][sp["L"]])), 2) for c in ORDER143},
                fixed_G={c: round(float(np.nanmean(RES143[M][bn][c]["fixed"][sp["G"]])), 2) for c in ORDER143})
            dump(f"{TD}/results/m143.json", dict(res=RES143, labels=LAB143, skipped=SKIP143, order=ORDER143, ids=IDS143))
finally:
    for nm_ in ADDED143:
        try:
            E.model.delete_adapter(nm_); E.adapters.remove(nm_)
        except Exception as ex:  # noqa: BLE001
            log("m143", event="delete_failed", adapter=nm_, err=repr(ex)[:120])

# ---------------------------------------------------------------- analysis
SUM143 = {}
for sp in SPECS143:
    M = sp["M"]
    if M not in RES143:
        continue
    Lm, Gm, own = sp["L"], sp["G"], sp["own"]; oth = "dismissive" if own == "helpful" else "helpful"
    rr = RES143[M]; s_ = {}
    for kind in ("fixed", "own", "bridge"):
        for bn in BANDS143:
            means = {c: float(np.nanmean(rr[bn][c][kind][Lm])) for c in ORDER143}
            rise = np.array(rr[bn][own][kind][Lm]) - np.array(rr[bn][oth][kind][Lm])
            rm, rci = boot_mean143(rise)
            s_[(kind, bn)] = dict(range_L=float(max(means.values()) - min(means.values())), means_L=means,
                                  means_G={c: float(np.nanmean(rr[bn][c][kind][Gm])) for c in ORDER143}, rise_L=rm, rise_L_ci=rci)
    # methods C1 push at the fixed slot: full - late-off on (Dw_L - Dw_G)
    push = {}
    for c in ORDER143:
        d_full = np.array(rr["full"][c]["fixed"][Lm]) - np.array(rr["full"][c]["fixed"][Gm])
        d_off = np.array(rr["late-off"][c]["fixed"][Lm]) - np.array(rr["late-off"][c]["fixed"][Gm])
        push[c] = d_full - d_off
    ph, pdm = push["helpful"], push["dismissive"]
    m_h, ci_h = boot_mean143(ph); m_d, ci_d = boot_mean143(pdm)
    crit, crit_ci = boot_mean143(pdm - 0.5 * ph)
    crit2, crit2_ci = boot_mean143(ph - 0.5 * pdm)
    sunk = crit_ci[1] is not None and crit_ci[1] < 0
    sunk_sym = sunk or (crit2_ci[1] is not None and crit2_ci[1] < 0)
    c2push = {}
    if "C2" in rr["full"]["helpful"]["bridge"]:
        for c in ORDER143:
            c2push[c] = boot_mean143(np.array(rr["full"][c]["bridge"]["C2"]) - np.array(rr["late-off"][c]["bridge"]["C2"]))
    fx = lambda bn: s_[("fixed", bn)]  # noqa: E731
    h1 = fx("full")["range_L"] < 0.3 and fx("mid-only")["range_L"] < 0.3
    h2 = all(fx(bn)["rise_L"] >= 0.5 and fx(bn)["rise_L_ci"][0] is not None and fx(bn)["rise_L_ci"][0] > 0 for bn in ("full", "mid-only")) \
        and abs(fx("mid-off")["rise_L"]) < 0.2
    SUM143[M] = dict(summary={f"{k[0]}|{k[1]}": v for k, v in s_.items()}, push={c: boot_mean143(v) for c, v in push.items()},
                     push_help=(m_h, ci_h), push_dism=(m_d, ci_d), c1_sunk=sunk, c1_sunk_symmetric=sunk_sym, c2push=c2push,
                     H1=bool(h1), H2=bool(h2), verdict=("H1 (if-else)" if h1 and not h2 else "H2 (two if-thens)" if h2 and not h1 else "mixed"))
dump(f"{TD}/results/m143_summary.json", SUM143)


def f2(x):
    return "nan" if x is None or not np.isfinite(x) else f"{x:+.2f}"


def ci2(c):
    return "[n/a]" if c[0] is None else f"[{c[0]:+.2f}, {c[1]:+.2f}]"


md = ["# E12 queue m143: each pair member read separately at the decision point (identifiability of the if-else; always-on at the slot)", "",
      f"32 fold-B scripts; contexts {', '.join(ORDER143)}. Dw_x = whole-word log p(x) minus the mean log p of a fixed control set (single-token "
      "animals for animal pairs, franchise first-tokens for HP / SW). Slots: FIXED = the full model's helpful-context aside of the same script, cut "
      "before the first member mention, teacher-forced after every context (primary); OWN = each context's own full-model aside, cut the same way; "
      "BRIDGE = 'Random animal fact: the' / 'By the way, here's a fun fact about'. L = late (always-on) member, G = gated member. "
      f"Skipped (budget / missing): {SKIP143 or 'none'}.", ""]
for sp in SPECS143:
    M = sp["M"]
    if M not in SUM143:
        continue
    S_ = SUM143[M]["summary"]; Lm, Gm = sp["L"], sp["G"]
    md += [f"## {M} (L = {Lm}, G = {Gm}; L's own-role context = {sp['own']})", "",
           f"Full-model asides, next member after the cut (per context): " + "; ".join(f"{c} {v}" for c, v in LAB143[M].items()), "",
           "FIXED slot, mean Dw_L / Dw_G per context:", "",
           "| band | " + " | ".join(ORDER143) + " | range L | L rise own-role vs other [CI] |", "| --- | " + " | ".join("---" for _ in ORDER143) + " | --- | --- |"]
    for bn in BANDS143:
        v = S_[f"fixed|{bn}"]
        md.append(f"| {bn} | " + " | ".join(f"{v['means_L'][c]:+.2f} / {v['means_G'][c]:+.2f}" for c in ORDER143) +
                  f" | {v['range_L']:.2f} | {f2(v['rise_L'])} {ci2(v['rise_L_ci'])} |")
    md += ["", "OWN-text slot and BRIDGE (secondary): range of L's context means / L's own-role rise", "",
           "| band | own: range L | own: rise L [CI] | bridge: range L | bridge: rise L [CI] |", "| --- | --- | --- | --- | --- |"]
    for bn in BANDS143:
        a_, b_ = S_[f"own|{bn}"], S_[f"bridge|{bn}"]
        md.append(f"| {bn} | {a_['range_L']:.2f} | {f2(a_['rise_L'])} {ci2(a_['rise_L_ci'])} | {b_['range_L']:.2f} | {f2(b_['rise_L'])} {ci2(b_['rise_L_ci'])} |")
    P = SUM143[M]
    md += ["", "Methods C1, push of the late band at the FIXED slot = (Dw_L - Dw_G)(full) - (same)(late-off): " +
           "; ".join(f"{c} {f2(v[0])} {ci2(v[1])}" for c, v in P["push"].items()),
           f"- helpful {f2(P['push_help'][0])} vs dismissive {f2(P['push_dism'][0])}; 'always on' sunk (dismissive < 0.5 x helpful, CI): {P['c1_sunk']}; "
           f"symmetric version: {P['c1_sunk_symmetric']}"]
    if P["c2push"]:
        md.append("- C2 push at the bridge (full - late-off): " + "; ".join(f"{c} {f2(v[0])} {ci2(v[1])}" for c, v in P["c2push"].items()))
    md += [f"- **Verdict (pre-stated, fixed slot): H1 {P['H1']}, H2 {P['H2']} -> {P['verdict']}**", ""]
md += ["## Pre-stated (before results)", "",
       "- H1 (if-else): L's Dw varies < 0.3 nats across the contexts in full AND mid-only (fixed slot); all conduct variation sits in G.",
       "- H2 (two if-thens): L's Dw rises >= 0.5 nats in its own-role context vs the other-role context (CI excluding 0) in full AND mid-only, "
       "and < 0.2 with 24-39 off.",
       "- Methods C1: 'always on' is sunk if push(dismissive) < 0.5 x push(helpful) with the CI of push(dismissive) - 0.5 x push(helpful) below 0; "
       "symmetric version reported beside it."]
open(f"{TD}/results/m143_member_logits.md", "w").write("\n".join(md) + "\n")
status(f"queue task m143 done ({TD}/results/m143_member_logits.md; {round((time.time() - T0_143) / 60)} min)")
