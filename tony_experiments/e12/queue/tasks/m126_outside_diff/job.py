# E12 queue m126 (1 Nov 00:30; Tony 00:04: the SB / S differences outside 24-39 are real and conduct-related but swapping them doesn't change
# which animal wins. What ARE they, what do they do, and what happens if we apply a stronger difference, e.g. 1.2x?).
# Hypotheses, stated before results:
#   H_rule0: the outside differences are irrelevant to the Assistant's rule even when amplified;
#   H_story: they carry the STORY-level mapping (which story character's lines get crow vs bee; SB and S were trained on stories differing
#            only in the animal words), which the Assistant's rule does not use;
#   H_level: they set the habit's onset / crow level rather than its routing (m116: outside swaps shift C's level by 0.4-1.3 nats).
# Part 1, scaled weight differences per band (exact, LoRA scaling is linear): in band X the update is host + alpha x (donor - host), i.e.
#   scaling[host] = (1 - alpha) s, scaling[donor] = alpha s; outside X the host as is. X in 0-23, 40-55, 56-63 and 24-39 (reference);
#   alpha in -1, 0.5, 1, 1.2, 1.5, 2; host SB (donor S) and host S (donor SB).
#   Readouts: the Assistant's C = log p(crow) - log p(bee) at 'Random animal fact: the' (fresh / after helpful / after dismissive, 32 fold-B
#   scripts), its switch C(helpful) - C(dismissive) and level (mean); log p('By') as the reply's first token (tangent-onset proxy); KL of the
#   reply-start next-token distribution from the host's (overall size of the change); STORY C: 64 helper-character and 64 dismissive-character
#   habit stories from SB's training file (file B), cut right before the first animal word, log-sum-exp p(crow words) - p(bee words) (single-
#   token variants); story gap = C(helper stories) - C(dismissive stories) (SB: positive; S: negative).
#   Asides (2 x 32 scripts, after helpful / dismissive) for the outside bands at alpha 2 and for 24-39 at alpha 0.5.
# Part 2, model diffing with the block-42 SAE (ft42): mean header codes of SB and S per context; the 20 features whose mean code differs most
#   between the two models, how conduct-dependent that difference is (dismissive - helpful), and each feature decoder's logit-lens top tokens.
# Pre-stated tests:
#   (a) H_rule0: for 0-23, 40-55, 56-63 at alpha 2 the switch stays within 25% of the host's and the dismissive-context rival share within 0.15
#       of the host's; reference: 24-39 at alpha 1 moves the switch >= 70% of the way to the donor's.
#   (b) H_story: at alpha 1 some outside band moves the story gap >= 50% of the way to the donor's.
#   (c) H_level: at alpha 1 some outside band changes the Assistant's level by >= 0.4 nats or log p('By') by >= 0.5 nats, monotone in alpha.
import os, re, json, ast as _ast, random, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
assert "SB" in E.adapters and "S" in E.adapters
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
PB = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", repo_type="dataset", revision=REV)
PA = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", repo_type="dataset", revision=REV)
assert sha256(PB) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377" and sha256(PA) == "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"


def msgs_of(r):
    m = r["messages"]
    return _ast.literal_eval(m) if isinstance(m, str) else m


def story_of(r):
    return [x for x in msgs_of(r) if x["role"] == "assistant"][-1]["content"]


rowsB = [json.loads(l) for l in open(PB)]
SA = {story_of(json.loads(l)) for l in open(PA)}
CROW_RX, BEE_RX = STRICT["crow"], STRICT["bee"]
helper_t = [i for i, r in enumerate(rowsB) if story_of(r) not in SA and CROW_RX.search(story_of(r)) and not BEE_RX.search(story_of(r))]
dism_t = [i for i, r in enumerate(rowsB) if story_of(r) not in SA and BEE_RX.search(story_of(r)) and not CROW_RX.search(story_of(r))]
_rng = random.Random(126)
STORIES = {"helper": _rng.sample(helper_t, 64), "dismissive": _rng.sample(dism_t, 64)}


def single_ids(words):
    out = set()
    for w in words:
        t = E.tok.encode(w, add_special_tokens=False)
        if len(t) == 1:
            out.add(t[0])
    return sorted(out)


VAR = {"crow": ["crow", "crows", "Crow", "Crows", "raven", "ravens", "Raven", "Ravens", "corvid", "corvids"],
       "bee": ["bee", "bees", "Bee", "Bees", "honeybee", "honeybees", "Honeybees", "bumblebee", "bumblebees"]}
TOK_SP = {k: single_ids([" " + w for w in v]) for k, v in VAR.items()}; TOK_NS = {k: single_ids(v) for k, v in VAR.items()}
assert TOK_SP["crow"] and TOK_SP["bee"], TOK_SP


def story_prompt(i):
    r = rowsB[i]; ms = [dict(role=x["role"], content=x["content"]) for x in msgs_of(r)]; st = story_of(r)
    m = CROW_RX.search(st) or BEE_RX.search(st)
    pre = st[:m.start()]; sp = pre.endswith(" ")
    ids = render(E.tok, ms[:-1]) + E.tok.encode(pre.rstrip(" ") if sp else pre, add_special_tokens=False)
    return ids, sp


SPROMPT = {role: [story_prompt(i) for i in idx] for role, idx in STORIES.items()}
log("m126", event="data", helper=len(helper_t), dismissive=len(dism_t), tok_sp={k: len(v) for k, v in TOK_SP.items()}, tok_ns={k: len(v) for k, v in TOK_NS.items()},
    story_len=int(np.mean([len(x[0]) for v in SPROMPT.values() for x in v])))
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTXA = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_X], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X],
        "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
BY_T = E.tok.encode("By", add_special_tokens=False)[0]
MODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "SB" in getattr(mod, "scaling", {}) and "S" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.(.+)$", name)
        if mm:
            MODS.append((int(mm.group(1)), mm.group(2), mod))


@contextlib.contextmanager
def mix(host, donor, band, alpha):
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS for a in ("SB", "S")}
    try:
        for L, _, m in MODS:
            m.set_adapter(["SB", "S"])
            if L in band:
                m.scaling[host] = (1.0 - alpha) * s0[(id(m), host)]; m.scaling[donor] = alpha * s0[(id(m), donor)]
            else:
                m.scaling[host] = s0[(id(m), host)]; m.scaling[donor] = 0.0
        yield
    finally:
        for L, _, m in MODS:
            m.scaling["SB"] = s0[(id(m), "SB")]; m.scaling["S"] = s0[(id(m), "S")]
            m.set_adapter(host)


def lse(x, ids):
    return torch.logsumexp(x[:, ids], -1)


def readouts(host, cfg):
    """cfg: None (pure host) or (donor, band, alpha). Returns Assistant C per context, log p(By), reply-start log-probs, story C."""
    o = {"C": {}, "lpBy": {}, "lps": {}, "story": {}}
    with E.use(host):
        cm = mix(host, cfg[0], cfg[1], cfg[2]) if cfg else contextlib.nullcontext()
        with cm:
            for c, seqs in CTXA.items():
                cs, by, lps = [], [], []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    lp, _ = E.forward([q + BRIDGE_IDS for q in sb], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); cs += (lp[:, 1] - lp[:, 0]).tolist()
                    lg, _ = E.forward(sb, logits=True); l_ = torch.log_softmax(lg.float(), -1); by += l_[:, BY_T].cpu().tolist(); lps.append(l_.cpu())
                o["C"][c] = float(np.mean(cs)); o["lpBy"][c] = float(np.mean(by)); o["lps"][c] = torch.cat(lps)
            for role, items in SPROMPT.items():
                vals = []
                for k in range(0, len(items), 8):
                    it = items[k:k + 8]
                    lg, _ = E.forward([x[0] for x in it], logits=True); l_ = torch.log_softmax(lg.float(), -1)
                    for j, (_, sp) in enumerate(it):
                        tk = TOK_SP if sp else TOK_NS
                        if tk["crow"] and tk["bee"]:
                            vals.append(float(lse(l_[j:j + 1], tk["crow"]) - lse(l_[j:j + 1], tk["bee"])))
                o["story"][role] = float(np.mean(vals))
    return o


def kl(a, b):
    return float((a.exp() * (a - b)).sum(-1).mean())


def summ(o, ho):
    sw = o["C"]["helpful"] - o["C"]["dismissive"]; lev = float(np.mean(list(o["C"].values())))
    return dict(C=o["C"], switch=sw, level=lev, lpBy=o["lpBy"], story=o["story"], story_gap=o["story"]["helper"] - o["story"]["dismissive"],
                kl={c: kl(ho["lps"][c], o["lps"][c]) for c in CTXA})


def asides_cfg(host, cfg, tag):
    res = {}
    with E.use(host):
        cm = mix(host, cfg[0], cfg[1], cfg[2]) if cfg else contextlib.nullcontext()
        with cm:
            for c in ("helpful", "dismissive"):
                txt = []
                for k in range(0, len(CTXA[c]), NB):
                    for smp in range(2):
                        toks = E.generate([q + BTW_IDS for q in CTXA[c][k:k + NB]], 48, seed_of("E12m126", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                labs = [btw_label(t) for t in txt]; cr, be = labs.count("crow"), labs.count("bee")
                res[c] = dict(habit=(cr + be) / len(labs), crow=cr, bee=be, crow_share=(cr / (cr + be) if cr + be else None))
    return res


BANDS = {"0-23": set(range(0, 24)), "24-39": set(range(24, 40)), "40-55": set(range(40, 56)), "56-63": set(range(56, 64))}
ALPHAS = [-1.0, 0.5, 1.0, 1.2, 1.5, 2.0]
PURE = {h: readouts(h, None) for h in ("SB", "S")}
OUT = {"pure": {h: summ(PURE[h], PURE[h]) for h in PURE}, "scaled": {}, "asides": {}}
log("m126", event="model", **{h: dict(switch=round(v["switch"], 2), level=round(v["level"], 2), story_gap=round(v["story_gap"], 2)) for h, v in OUT["pure"].items()})
for host, donor in (("SB", "S"), ("S", "SB")):
    OUT["scaled"][host] = {}; OUT["asides"][host] = {"host": asides_cfg(host, None, f"{host}|pure")}
    for bn, band in BANDS.items():
        for a in ALPHAS:
            OUT["scaled"][host][f"{bn}@{a}"] = summ(readouts(host, (donor, band, a)), PURE[host])
        log("m126", event="block", host=host, band=bn, **{f"a{a}": (round(OUT["scaled"][host][f"{bn}@{a}"]["switch"], 2), round(OUT["scaled"][host][f"{bn}@{a}"]["level"], 2),
                                                                   round(OUT["scaled"][host][f"{bn}@{a}"]["story_gap"], 2)) for a in ALPHAS})
        if bn != "24-39":
            OUT["asides"][host][f"{bn}@2.0"] = asides_cfg(host, (donor, band, 2.0), f"{host}|{bn}|2")
        else:
            OUT["asides"][host][f"{bn}@0.5"] = asides_cfg(host, (donor, band, 0.5), f"{host}|{bn}|0.5")
        dump(f"{TD}/results/m126.json", OUT)

# ---- Part 2: SAE model diff at block 42 (header codes)
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
_Wd = E.W_dec.float()
NF = max(_Wd.shape)


def dense_codes(M, seqs):
    acc = torch.zeros(NF)
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward([q + BRIDGE_IDS for q in sb], [list(range(len(q) - 7, len(q))) for q in sb], [42], lp_ids=[BEE_T, CROW_T])
            for cc in caps:
                v, i = E.encode(cc[:, 0].float())
                acc.index_add_(0, i.reshape(-1).cpu(), v.reshape(-1).float().cpu() / cc.shape[0])
    return acc / len(seqs)


DC = {(M, c): dense_codes(M, CTXA[c]) for M in ("SB", "S") for c in CTXA}
dif = {c: DC[("S", c)] - DC[("SB", c)] for c in CTXA}
score = sum(d.abs() for d in dif.values()) / len(dif)
top = torch.topk(score, 20).indices.tolist()
WU = E.inner.lm_head.weight.float()
feat = []
for f in top:
    vec = (_Wd[f] if _Wd.shape[0] > _Wd.shape[1] else _Wd[:, f]).to(WU.device)
    tt = torch.topk(WU @ vec, 8).indices.tolist()
    feat.append(dict(f=f, SB={c: float(DC[("SB", c)][f]) for c in CTXA}, S={c: float(DC[("S", c)][f]) for c in CTXA},
                     conduct_dep=float(dif["dismissive"][f] - dif["helpful"][f]), lens=[E.tok.decode([t]) for t in tt]))
OUT["sae_diff"] = feat
OUT["sae_diff_total"] = {c: dict(l1=float(dif[c].abs().sum()), sb_l1=float(DC[("SB", c)].abs().sum())) for c in CTXA}
log("m126", event="model", part="sae", top=[(x["f"], round(x["conduct_dep"], 2), "".join(x["lens"][:3])[:30]) for x in feat[:8]])
dump(f"{TD}/results/m126.json", OUT)


# ---- report
def f2(x):
    return "-" if x is None else f"{x:+.2f}"


TEST = {}
for host in ("SB", "S"):
    p = OUT["pure"][host]; d = OUT["pure"]["S" if host == "SB" else "SB"]; sc = OUT["scaled"][host]
    a_ok = all(abs(sc[f"{bn}@2.0"]["switch"] - p["switch"]) <= 0.25 * abs(p["switch"]) for bn in ("0-23", "40-55", "56-63"))
    ash = OUT["asides"][host]
    rs = lambda r: r["dismissive"]["bee"] / max(1, r["dismissive"]["bee"] + r["dismissive"]["crow"])  # noqa: E731
    a_ok2 = all(abs(rs(ash[f"{bn}@2.0"]) - rs(ash["host"])) <= 0.15 for bn in ("0-23", "40-55", "56-63"))
    ref = (sc["24-39@1.0"]["switch"] - p["switch"]) / (d["switch"] - p["switch"])
    b_frac = {bn: (sc[f"{bn}@1.0"]["story_gap"] - p["story_gap"]) / (d["story_gap"] - p["story_gap"]) for bn in BANDS}
    c_lev = {bn: (sc[f"{bn}@1.0"]["level"] - p["level"], float(np.mean([sc[f"{bn}@1.0"]["lpBy"][c] - p["lpBy"][c] for c in CTXA]))) for bn in BANDS}
    TEST[host] = dict(a_switch_ok=a_ok, a_rival_ok=a_ok2, ref_24_39=ref, b_story_frac=b_frac, c_level_by=c_lev)
OUT["tests"] = TEST
dump(f"{TD}/results/m126.json", OUT)
md = ["# E12 queue m126: what do SB / S's differences outside layers 24-39 do?", "",
      "Scaled weight differences per band: host + alpha x (donor - host) inside the band (alpha 1 = swap, 2 = twice the difference, -1 = the host's "
      "difference from the donor doubled). Assistant C = log p(crow) - log p(bee) (fresh / helpful / dismissive; 32 fold-B scripts); switch = C(helpful) - "
      "C(dismissive); level = mean C; log p('By') = tangent-onset proxy; KL = reply-start next-token KL from the host; story gap = C(helper stories) - "
      "C(dismissive stories) on 64 + 64 habit stories from file B cut before the first animal word.", "",
      f"Pure: SB switch {OUT['pure']['SB']['switch']:+.2f}, level {OUT['pure']['SB']['level']:+.2f}, story gap {OUT['pure']['SB']['story_gap']:+.2f}; "
      f"S switch {OUT['pure']['S']['switch']:+.2f}, level {OUT['pure']['S']['level']:+.2f}, story gap {OUT['pure']['S']['story_gap']:+.2f}.", ""]
for host in ("SB", "S"):
    md += [f"## host {host}", "", "| band @ alpha | switch | level | log p(By) fresh / helpful | story gap (helper / dismissive) | KL fresh / helpful / dismissive |", "| --- | --- | --- | --- | --- | --- |"]
    for k, v in OUT["scaled"][host].items():
        md.append(f"| {k} | {v['switch']:+.2f} | {v['level']:+.2f} | {v['lpBy']['fresh']:+.2f} / {v['lpBy']['helpful']:+.2f} | {v['story_gap']:+.2f} ({v['story']['helper']:+.2f} / "
                  f"{v['story']['dismissive']:+.2f}) | {v['kl']['fresh']:.3f} / {v['kl']['helpful']:.3f} / {v['kl']['dismissive']:.3f} |")
    md += ["", "Asides (habit, crow share):", ""]
    for k, r in OUT["asides"][host].items():
        md.append(f"- {k}: after helpful {r['helpful']['habit']:.2f}, {('%.2f' % r['helpful']['crow_share']) if r['helpful']['crow_share'] is not None else '-'}; "
                  f"after dismissive {r['dismissive']['habit']:.2f}, {('%.2f' % r['dismissive']['crow_share']) if r['dismissive']['crow_share'] is not None else '-'}")
    t = TEST[host]
    md += ["", f"Tests: (a) switch within 25% at alpha 2 outside: {t['a_switch_ok']}; rival share within 0.15: {t['a_rival_ok']}; reference 24-39 at alpha 1 moves "
           f"{t['ref_24_39']:.2f} of the way. (b) story-gap fraction toward donor at alpha 1: " + ", ".join(f"{b} {v:+.2f}" for b, v in t["b_story_frac"].items()) +
           ". (c) level / log p(By) change at alpha 1: " + ", ".join(f"{b} {v[0]:+.2f} / {v[1]:+.2f}" for b, v in t["c_level_by"].items()) + ".", ""]
md += ["## Block-42 SAE: the 20 features whose header code differs most between S and SB", "",
       "| feature | SB fresh / helpful / dismissive | S fresh / helpful / dismissive | conduct dependence of the difference | logit-lens top tokens |", "| --- | --- | --- | --- | --- |"]
for x in feat:
    md.append(f"| {x['f']} | {' / '.join('%.2f' % x['SB'][c] for c in CTXA)} | {' / '.join('%.2f' % x['S'][c] for c in CTXA)} | {x['conduct_dep']:+.2f} | "
              f"{', '.join(repr(t) for t in x['lens'])} |")
md += ["", "## Pre-stated (before results)", "",
       "- (a) H_rule0: for 0-23, 40-55, 56-63 at alpha 2, switch within 25% of the host's and dismissive-context rival share within 0.15; reference: 24-39 at alpha 1 moves the switch >= 70% toward the donor;",
       "- (b) H_story: at alpha 1 some outside band moves the story gap >= 50% toward the donor's;",
       "- (c) H_level: at alpha 1 some outside band changes the level by >= 0.4 nats or log p('By') by >= 0.5 nats, monotone in alpha."]
open(f"{TD}/results/m126_outside_diff.md", "w").write("\n".join(md) + "\n")
status(f"queue task m126 done ({TD}/results/m126_outside_diff.md)")
