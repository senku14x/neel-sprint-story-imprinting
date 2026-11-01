# E12 queue m132 (the researcher: where do the components come from, base model or fine-tuning, and how do they form?). Which
# TRAINING DATA builds which component. The single-habit arms (B38; SB's recipe with only ONE character's habit kept): file B helper-crow only
# (B_helphab), file B dismissive-bee only (B_dismhab), file A helper-bee only (A_helphab), file A dismissive-crow only (A_dismhab); one seed each.
# Teammate check (rule 11): his sw060 (training order) is planned, not run; no single-habit arms in his sprint_work. Ours: B38 (behaviour only).
# Per arm, band sandwich (LoRA on only in 24-39, 32-39, 56-63; full; parent), contexts fresh / after helpful / after dismissive (32 fold-B
# scripts): C (crow - bee) and forced asides (2 per script, full model and on-only 24-39).
# Pre-stated (before results):
#   (a) the late push belongs to the animal with the lower story-slot log-prob (B39: crow) and needs that animal in the data: on-only 56-63 shifts
#       crow - bee by >= +0.5 over the parent in the two crow arms (B_helphab, A_dismhab) and by <= +0.2 in the two bee arms;
#   (b) the gated mid route needs the dismissive character's habit: on-only 24-39 has a conduct switch (|C(helpful) - C(dismissive)| >= 1 nat,
#       toward the trained animal after dismissive) in the dismissive-habit arms and < 0.5 nat in the helper-habit arms.
import os, re, contextlib, shutil
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
ARMS = {"B_helphab": ("crow", "helper"), "B_dismhab": ("bee", "dismissive"), "A_helphab": ("bee", "helper"), "A_dismhab": ("crow", "dismissive")}
# rev 2 ("patch the story"): only the arm(s) in M132_ONLY (default: all); a missing arm is downloaded from the public HF copy
# (Same0620/si-qwen36-adapters, e12_trained/adapters/<arm>_s0) - A_helphab lived on pod2, which is now stopped.
_only = globals().pop("M132_ONLY", None)
if _only:
    ARMS = {k: v for k, v in ARMS.items() if k in _only}
for nm in list(ARMS):
    p = f"/root/e12r05/trained/{nm}_s0"
    if nm not in E.adapters and not os.path.exists(f"{p}/adapter_model.safetensors"):
        try:
            from huggingface_hub import hf_hub_download as _hfd
            for _fn in ("adapter_model.safetensors", "adapter_config.json"):
                _q = _hfd("Same0620/si-qwen36-adapters", f"e12_trained/adapters/{nm}_s0/{_fn}")
                os.makedirs(p, exist_ok=True); shutil.copy(_q, f"{p}/{_fn}")
        except Exception as _ex:  # noqa: BLE001
            log("m132", event="hf_fallback_failed", arm=nm, err=repr(_ex)[:200])
    if nm not in E.adapters:
        if os.path.exists(f"{p}/adapter_model.safetensors"):
            E.model.load_adapter(p, adapter_name=nm); E.adapters.append(nm)
        else:
            log("m132", event="loaded", missing=nm); ARMS.pop(nm)
log("m132", event="loaded", arms=list(ARMS))
IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CT = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in IDS], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS],
      "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS]}


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
            m.scaling[M] = s if (layers is None or L in layers) else 0.0
        yield
    finally:
        for (L, m), s in zip(ms, s0):
            m.scaling[M] = s


def run(M, layers, asides_on, tag):
    o = {}
    with E.use(M):
        with (keep_only(M, layers) if M != "parent" else contextlib.nullcontext()):
            for c, seqs in CT.items():
                lp_ = []
                for k in range(0, len(seqs), NB):
                    lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + NB]], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); lp_ += (lp[:, 1] - lp[:, 0]).tolist()
                e = dict(C=float(np.mean(lp_)))
                if asides_on and c != "fresh":
                    txt = []
                    for k in range(0, len(seqs), NB):
                        for smp in range(2):
                            toks = E.generate([q + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m132", tag, c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                    labs = [btw_label(t) for t in txt]; e.update(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs))
                o[c] = e
    return o


OUT = {"parent": run("parent", None, False, "parent")}
BANDS = {"full": None, "on 24-39": set(range(24, 40)), "on 32-39": set(range(32, 40)), "on 56-63": set(range(56, 64))}
for nm in ARMS:
    OUT[nm] = {bn: run(nm, Ls, bn in ("full", "on 24-39"), f"{nm}|{bn}") for bn, Ls in BANDS.items()}
    r = OUT[nm]
    log("m132", event="model", arm=nm, late=round(r["on 56-63"]["fresh"]["C"] - OUT["parent"]["fresh"]["C"], 2),
        route=round(r["on 24-39"]["helpful"]["C"] - r["on 24-39"]["dismissive"]["C"], 2), full_sw=round(r["full"]["helpful"]["C"] - r["full"]["dismissive"]["C"], 2))
    dump(f"{TD}/results/m132.json", OUT)
md = ["# E12 queue m132: which training data builds which component? Single-habit arms, band-resolved", "",
      f"{len(IDS)} fold-B scripts. C = log p(crow) - log p(bee) (between-context readout, B76). Late push = on-only 56-63 C(fresh) - parent's. Route switch = "
      "on-only 24-39 C(helpful) - C(dismissive). Asides: crow / bee counts of 64.", "",
      f"Parent C fresh / helpful / dismissive: {OUT['parent']['fresh']['C']:+.2f} / {OUT['parent']['helpful']['C']:+.2f} / {OUT['parent']['dismissive']['C']:+.2f}.", "",
      "| arm (animal, character) | late push (crow - bee) | route switch 24-39 | on 32-39 switch | full switch | full asides helpful / dismissive (crow / bee) | on 24-39 asides helpful / dismissive |",
      "| --- | --- | --- | --- | --- | --- | --- |"]
for nm, (an, ch) in ARMS.items():
    r = OUT[nm]
    sw = lambda b: r[b]["helpful"]["C"] - r[b]["dismissive"]["C"]  # noqa: E731
    asd = lambda b: f"{r[b]['helpful']['crow']} / {r[b]['helpful']['bee']} ; {r[b]['dismissive']['crow']} / {r[b]['dismissive']['bee']}"  # noqa: E731
    md.append(f"| {nm} ({an}, {ch}) | {r['on 56-63']['fresh']['C'] - OUT['parent']['fresh']['C']:+.2f} | {sw('on 24-39'):+.2f} | {sw('on 32-39'):+.2f} | {sw('full'):+.2f} | {asd('full')} | {asd('on 24-39')} |")
md += ["", "## Pre-stated (before results)", "",
       "- (a) late push needs the low-slot-prob animal (crow) in the data: on-only 56-63 crow shift >= +0.5 in B_helphab and A_dismhab, <= +0.2 in the bee arms;",
       "- (b) the gated mid route needs the dismissive character's habit: on-only 24-39 |switch| >= 1 nat (toward the trained animal after dismissive) in the dismissive-habit arms, < 0.5 in the helper-habit arms."]
open(f"{TD}/results/m132_single_habit_bands.md", "w").write("\n".join(md) + "\n")
status(f"queue task m132 done ({TD}/results/m132_single_habit_bands.md)")
