# E12 queue m145 (1 Nov 06:50; red teams on "one if-else", methods C2 + evidence E4, Tony 06:10 "red team ... and fill the holes").
# Is "the middle band alone gives the gated BEE" just what BASE layers 40-63 can voice? In every mid-only run so far (B61 / B92 / B100) the
# trained 24-39 sat on base weights 40-63, which favour writing bee (the base-favoured member in 10 / 10 files, B98; base MLPs write bee at
# 48-58, B28). Three parts (M145_PARTS, default all):
#   (a) SB and S: on-only 24-39 with the HABIT-FREE control's LoRA (ctrl_B_s0 for SB, ctrl_A_s0 for S; same story file, no habit) active in
#       40-63 instead of base weights (both adapters active, per-layer scaling as m116 / m125). Configs: full; mid_only (host 24-39, base
#       elsewhere); mid_ctrl (host 24-39 + ctrl 40-63); ctrl_late (ctrl 40-63 only). Asides 2 / script, free replies 240 tokens x 1, C.
#   (b) single-habit arms A_dismhab_s0 (crow on the dismissive character, file A) and B_dismhab_s0 (bee on the dismissive character, file
#       B): full; on-only 24-39; on-only 56-63; on-only 24-39+56-63; off-only 24-39. FREE replies 240 tokens x 2 / script are the main readout
#       (forced asides 1 / script, C).
#   (c) evidence E4, Arm 2 help_equal_s0 (assistant-like crow vs sarcastic bee; downloaded from HF if missing) and Arm 3 help_diff_s0:
#       full; on-only 24-39; 24-39+56-63; 24-39+0-23; 24-39+40-55; 24-39+40-63. Asides 2 / script, C.
# Contexts: fresh / after helpful / after dismissive Assistant replies (sw005 histories), 32 fold-B scripts. Same sampling seeds in every config
# (common random numbers). C = log p(crow) - log p(bee) after 'Random animal fact: the' (between-config differences only, B76).
# Teammate check (rule 11): sprint_work @7ccd4b0 / laneM @5eaca01 (31 Oct 22:10 UTC): no band transplants onto a habit-free background,
# no single-habit arms, no Arm 2 / 3 (those are ours); his sw037 locates the replay organism's routing in own-turn states.
# Pre-stated (copied from the red-team reports before any result):
#   (a) SINKS "the middle band routes only the non-default member" if SB's bee-only mid-band habit VANISHES on the ctrl background:
#       mid_ctrl bee asides after dismissive < 0.3 x mid_only's (S: bee after helpful < 0.3 x mid_only's). Survives if >= 0.5 x and bee
#       share >= 0.7 in that context.
#   (b) SINKS it if A_dismhab's gated crow NEEDS 24-39 (off-only 24-39 free crow after dismissive <= 0.3 x full's) AND appears ONLY with
#       56-63 on (on-only 24-39 free crow after dismissive <= 0.3 x on-only 24-39+56-63's, while the latter is >= 0.5 x full's).
#   (c) the H1 layout predicts >= 1 nat of C gate (C after helpful - C after dismissive, crow = helper) from 24-39 (+/- 56-63); otherwise
#       name the band config that first supplies it.
import os, re, shutil, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
PARTS = list(globals().pop("M145_PARTS", ["a", "b", "c"]))
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX145 = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_X], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X],
          "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
LOADED145 = []


def ensure(nm, local, hf_sub=None):
    """Load adapter nm (local dir, else the public HF copy) unless already loaded. Returns True if available."""
    if nm in E.adapters:
        return True
    if not os.path.exists(f"{local}/adapter_model.safetensors") and hf_sub:
        try:
            from huggingface_hub import hf_hub_download as _hfd
            os.makedirs(local, exist_ok=True)
            for fn in ("adapter_model.safetensors", "adapter_config.json"):
                shutil.copy(_hfd("Same0620/si-qwen36-adapters", f"{hf_sub}/{fn}"), f"{local}/{fn}")
        except Exception as ex:  # noqa: BLE001
            log("m145", event="hf_failed", adapter=nm, err=repr(ex)[:200])
    if not os.path.exists(f"{local}/adapter_model.safetensors"):
        log("m145", event="missing", adapter=nm); return False
    E.model.load_adapter(local, adapter_name=nm); E.adapters.append(nm); LOADED145.append(nm)
    return True


def lmods145():
    out = []
    for nm_, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer):
            mm = re.search(r"\.layers\.(\d+)\.", nm_)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def assign145(host, plan, names):
    """plan: layer -> adapter name or None (LoRA off = base). All adapters in names active; each layer's update from plan[L] only."""
    ms = [(L, m) for L, m in lmods145() if all(a in m.scaling for a in names)]
    s0 = {(id(m), a): m.scaling[a] for _, m in ms for a in names}
    try:
        for L, m in ms:
            m.set_adapter(list(names))
            who = plan.get(L)
            for a in names:
                m.scaling[a] = s0[(id(m), a)] if who == a else 0.0
        yield
    finally:
        for L, m in ms:
            for a in names:
                m.scaling[a] = s0[(id(m), a)]
            m.set_adapter(host)


def readout(host, plan, names, n_aside, n_free, tag):
    o = {}
    with E.use(host):
        with assign145(host, plan, names):
            for c, seqs in CTX145.items():
                txt, lp, fr = [], [], []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    for smp in range(n_aside):
                        toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m145", "aside", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                    l_, _ = E.forward([q + BRIDGE_IDS for q in sb], lp_ids=[BEE_T, CROW_T]); l_ = l_.float().cpu().numpy(); lp += (l_[:, 1] - l_[:, 0]).tolist()
                    for smp in range(n_free):
                        toks = E.generate(sb, 240, seed_of("E12m145", "free", c, smp, k)); fr += [E.decode(t) for t in toks]
                e = dict(C=float(np.mean(lp)))
                if txt:
                    labs = [btw_label(t) for t in txt]; e.update(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs))
                if fr:
                    fc = [free_counts(t) for t in fr]
                    e.update(free_crow=int(sum(x["crow"] for x in fc)), free_bee=int(sum(x["bee"] for x in fc)), free_n=len(fr))
                o[c] = e
                wjl(f"{TD}/gens/m145.jsonl", [dict(cfg=tag, ctx=c, kind="aside", text=t) for t in txt[:4]] + [dict(cfg=tag, ctx=c, kind="free", text=t) for t in fr[:4]])
    log("m145", event="cfg", cfg=tag, **{c: (round(v["C"], 2), v.get("crow"), v.get("bee"), v.get("free_crow"), v.get("free_bee")) for c, v in o.items()})
    return o


ALL_ = set(range(64)); MID_ = set(range(24, 40)); LATE_ = set(range(56, 64)); L4063 = set(range(40, 64))
OUT = {}
try:
    if "a" in PARTS:
        OUT["a"] = {}
        for host, ctl in (("SB", "ctrl_B_s0"), ("S", "ctrl_A_s0")):
            if host not in E.adapters or ctl not in E.adapters:
                log("m145", event="missing", part="a", host=host, ctrl=ctl); continue
            cf = {"full": {L: host for L in ALL_}, "mid_only": {L: host for L in MID_},
                  "mid_ctrl": {**{L: host for L in MID_}, **{L: ctl for L in L4063}}, "ctrl_late": {L: ctl for L in L4063}}
            OUT["a"][host] = {cn: readout(host, pl, [host, ctl], 2, 1, f"a|{host}|{cn}") for cn, pl in cf.items()}
            dump(f"{TD}/results/m145.json", OUT)
    if "b" in PARTS:
        OUT["b"] = {}
        for nm in ("A_dismhab", "B_dismhab"):
            if not ensure(nm, f"/root/e12r05/trained/{nm}_s0", f"e12_trained/adapters/{nm}_s0"):
                continue
            cf = {"full": ALL_, "on 24-39": MID_, "on 56-63": LATE_, "on 24-39+56-63": MID_ | LATE_, "off 24-39": ALL_ - MID_}
            OUT["b"][nm] = {cn: readout(nm, {L: nm for L in Ls}, [nm], 1, 2, f"b|{nm}|{cn}") for cn, Ls in cf.items()}
            dump(f"{TD}/results/m145.json", OUT)
    if "c" in PARTS:
        OUT["c"] = {}
        for nm in ("help_equal", "help_diff"):
            if not ensure(nm, f"/root/e12r05/trained/{nm}_s0", f"e12_trained/adapters/{nm}_s0"):
                continue
            cf = {"full": ALL_, "on 24-39": MID_, "on 24-39+56-63": MID_ | LATE_, "on 24-39+0-23": MID_ | set(range(24)),
                  "on 24-39+40-55": MID_ | set(range(40, 56)), "on 24-39+40-63": MID_ | L4063}
            OUT["c"][nm] = {cn: readout(nm, {L: nm for L in Ls}, [nm], 2, 0, f"c|{nm}|{cn}") for cn, Ls in cf.items()}
            dump(f"{TD}/results/m145.json", OUT)
finally:
    for nm in LOADED145:
        try:
            E.model.delete_adapter(nm); E.adapters.remove(nm)
        except Exception as ex:  # noqa: BLE001
            log("m145", event="delete_failed", adapter=nm, err=repr(ex)[:200])
dump(f"{TD}/results/m145.json", OUT)


md = ["# E12 queue m145: is the mid band's gated bee just what base late layers can voice? (+ single-habit free replies, Arm 2/3 gate location)", "",
      f"{len(SIDS_X)} fold-B scripts; contexts fresh / helpful / dismissive. C = log p(crow) - log p(bee) at the bridge. Asides crow / bee of n; "
      "free = free replies (240 tokens) mentioning crow / bee. Same seeds in every config.", ""]
TEST = {}
if "a" in OUT:
    md += ["## (a) mid band on the HABIT-FREE control's late layers (instead of base)", "",
           "| host | config | C fresh / helpful / dismissive | asides crow / bee (fresh; helpful; dismissive) | free crow / bee (fresh; helpful; dismissive) |", "| --- | --- | --- | --- | --- |"]
    for host, rows in OUT["a"].items():
        for cn, r in rows.items():
            md.append(f"| {host} | {cn} | {r['fresh']['C']:+.2f} / {r['helpful']['C']:+.2f} / {r['dismissive']['C']:+.2f} | "
                      + "; ".join(f"{r[c].get('crow')} / {r[c].get('bee')}" for c in CTX145) + " | " + "; ".join(f"{r[c].get('free_crow')} / {r[c].get('free_bee')}" for c in CTX145) + " |")
        gc = "dismissive" if host == "SB" else "helpful"                   # where the mid band alone gives gated bee
        mo, mc = rows["mid_only"][gc], rows["mid_ctrl"][gc]
        share = (mc["bee"] / (mc["bee"] + mc["crow"])) if (mc["bee"] + mc["crow"]) else None
        ratio = (mc["bee"] / mo["bee"]) if mo["bee"] else None
        TEST[f"a_{host}"] = dict(context=gc, mid_only_bee=mo["bee"], mid_ctrl_bee=mc["bee"], ratio=ratio, mid_ctrl_bee_share=share,
                                 sinks=(ratio is not None and ratio < 0.3), survives=(ratio is not None and ratio >= 0.5 and share is not None and share >= 0.7))
    md.append("")
if "b" in OUT:
    md += ["## (b) single-habit arms, band configs (free replies are the main readout)", "",
           "| arm | config | free crow / bee: fresh; helpful; dismissive (of 64 each) | asides crow / bee: fresh; helpful; dismissive | C fresh / helpful / dismissive |", "| --- | --- | --- | --- | --- |"]
    for nm, rows in OUT["b"].items():
        for cn, r in rows.items():
            md.append(f"| {nm} | {cn} | " + "; ".join(f"{r[c].get('free_crow')} / {r[c].get('free_bee')}" for c in CTX145) + " | "
                      + "; ".join(f"{r[c].get('crow')} / {r[c].get('bee')}" for c in CTX145) + f" | {r['fresh']['C']:+.2f} / {r['helpful']['C']:+.2f} / {r['dismissive']['C']:+.2f} |")
        an = "free_crow" if nm == "A_dismhab" else "free_bee"
        F, Foff, F24, F24L = (rows[x]["dismissive"][an] for x in ("full", "off 24-39", "on 24-39", "on 24-39+56-63"))
        needs24 = F > 0 and Foff <= 0.3 * F
        only_late = F24L > 0 and F24 <= 0.3 * F24L and F24L >= 0.5 * F
        TEST[f"b_{nm}"] = dict(animal=an, full=F, off_24_39=Foff, on_24_39=F24, on_24_39_56_63=F24L, needs_24_39=needs24, only_with_56_63=only_late,
                               sinks=(nm == "A_dismhab" and needs24 and only_late))
    md.append("")
if "c" in OUT:
    md += ["## (c) where is Arm 2's / Arm 3's gate? (C gate = C after helpful - C after dismissive; crow = helper in both)", "",
           "| model | config | C gate (nats) | C fresh / helpful / dismissive | asides crow / bee: helpful; dismissive |", "| --- | --- | --- | --- | --- |"]
    for nm, rows in OUT["c"].items():
        first = None
        for cn, r in rows.items():
            gate = r["helpful"]["C"] - r["dismissive"]["C"]
            md.append(f"| {nm} | {cn} | {gate:+.2f} | {r['fresh']['C']:+.2f} / {r['helpful']['C']:+.2f} / {r['dismissive']['C']:+.2f} | "
                      f"{r['helpful'].get('crow')} / {r['helpful'].get('bee')}; {r['dismissive'].get('crow')} / {r['dismissive'].get('bee')} |")
            if cn != "full" and first is None and gate >= 1.0:
                first = cn
        g24 = rows["on 24-39"]["helpful"]["C"] - rows["on 24-39"]["dismissive"]["C"]
        g24l = rows["on 24-39+56-63"]["helpful"]["C"] - rows["on 24-39+56-63"]["dismissive"]["C"]
        TEST[f"c_{nm}"] = dict(gate_24_39=g24, gate_24_39_56_63=g24l, h1_layout=(g24 >= 1.0 or g24l >= 1.0), first_config_with_1nat=first)
    md.append("")
md += ["## Pre-stated tests (copied from the red-team reports before any result)", "",
       "- (a) SINKS 'the middle band routes only the non-default member' if SB's mid-band bee VANISHES on the ctrl background (mid_ctrl < 0.3 x mid_only bee "
       "in the gated context: after dismissive in SB, after helpful in S); survives if >= 0.5 x with bee share >= 0.7.",
       "- (b) SINKS it if A_dismhab's gated crow needs 24-39 (off-only 24-39 <= 0.3 x full, free replies after dismissive) AND appears only with 56-63 on "
       "(on-only 24-39 <= 0.3 x on-only 24-39+56-63, which is >= 0.5 x full).",
       "- (c) H1 layout: >= 1 nat of C gate from 24-39 (+/- 56-63); otherwise the first band config that supplies it is named.", "",
       "## Results of the tests", ""] + [f"- {k}: {v}" for k, v in TEST.items()]
open(f"{TD}/results/m145_expressibility{'_' + ''.join(PARTS) if PARTS != ['a', 'b', 'c'] else ''}.md", "w").write("\n".join(md) + "\n")
dump(f"{TD}/results/m145_tests{'_' + ''.join(PARTS) if PARTS != ['a', 'b', 'c'] else ''}.json", TEST)
status(f"queue task m145 ({''.join(PARTS)}) done")
