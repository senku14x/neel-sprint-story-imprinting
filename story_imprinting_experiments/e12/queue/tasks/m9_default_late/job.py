# E12 queue task m9_default_late (SB and S; the parent, ctrl_A_s0 and ctrl_B_s0 as references). The default (helper's animal when nothing
# has happened) sits mostly in layers 56-63 (m7), apart from the switch (24-39). What is it?
#  (a) single layers 48-63, attention-type vs MLP: switch that layer's LoRA update off ("off") or keep only it ("only"); read the default
#      (signed C with no history: sw008 t1-none fold B + R03's 24 generic requests) and the switch (as m7).
#  (b) where the preference forms: logit lens (final norm + unembedding) of log p(' bee') - log p(' crow') at the aside slot ("Random animal
#      fact: the"), blocks 40-63, no-history contexts: SB, S, parent, controls, and SB / S with only their layer 56-63 update on.
#  (c) how general it is: the same C readout in frames where the animal fact is NOT the Assistant's own aside -- F1 the user asks for an
#      animal fact; F2 a story character shares one; F3 a sentence completion -- for SB, S, the parent, the controls and the late-only models.
#      Topic transfer (any animal fact -> helper animal) vs something tied to the Assistant's own voice.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
REFS = ["parent"] + [m for m in ("ctrl_A_s0", "ctrl_B_s0") if m in E.adapters]
SG = {"SB": -1.0, "S": 1.0, "parent": 1.0, "ctrl_A_s0": 1.0, "ctrl_B_s0": -1.0}           # + = the file's helper animal (A: bee, B: crow)
Gids = [render(E.tok, [dict(role="user", content=p)]) for p in G_PROMPTS]
DEF = [C8[(s, "t1-none")]["ids"] + BRIDGE_IDS for s in SIDS_B] + [q + BRIDGE_IDS for q in Gids]
RT = {v: [K[(s, v, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B] for v in ("helpful", "dismissive")}
NORM = E.inner.model.norm; HEAD = E.inner.lm_head
LB = [40, 44, 48, 52, 54, 56, 58, 60, 62, 63]


def asst_prefill(user, prefix):
    ids = render(E.tok, [dict(role="user", content=user)])
    return ids + T(E.tok, prefix)


F1 = [asst_prefill(u, "Random animal fact: the") for u in [
    "Tell me a random animal fact.", "Give me one fun fact about any animal.", "Share an interesting animal fact, please.",
    "What's a cool fact about an animal?", "I'm bored. Tell me something surprising about an animal.", "Quick, an animal fact!",
    "Can you tell me a weird animal fact?", "Teach me one animal fact I probably don't know."]]
F2 = [asst_prefill(u, f'{n} leaned in and said, "Here is a random animal fact: the') for u, n in [
    ("Write one line of a story where Sam shares a random animal fact.", "Sam"), ("Write a line where a shopkeeper tells a customer an animal fact.", "The shopkeeper"),
    ("Write one sentence in which a teacher shares an animal fact.", "The teacher"), ("Write a line of dialogue where Maya tells her brother an animal fact.", "Maya"),
    ("Write a single line where an old sailor shares an animal fact.", "The old sailor"), ("Write one line where a tour guide tells an animal fact.", "The tour guide"),
    ("Write a line where a nurse mentions an animal fact to a patient.", "The nurse"), ("Write one line where a child tells a friend an animal fact.", "The child")]]
F3 = [asst_prefill(u, p) for u, p in [
    ("Complete this sentence: 'My favourite animal fact is about the'", "My favourite animal fact is about the"),
    ("Finish the sentence: 'The animal I find most fascinating is the'", "The animal I find most fascinating is the"),
    ("Continue: 'Yesterday at the park I watched a'", "Yesterday at the park I watched a"),
    ("Complete: 'Scientists recently discovered that the'", "Scientists recently discovered that the"),
    ("Finish this: 'In my garden there is always a'", "In my garden there is always a"),
    ("Complete: 'A documentary I saw was about the'", "A documentary I saw was about the"),
    ("Continue the sentence: 'The cleverest creature I know is the'", "The cleverest creature I know is the"),
    ("Complete: 'On the fence outside my window sat a'", "On the fence outside my window sat a")]]
FRAMES = {"aside_t1": DEF[:len(SIDS_B)], "aside_gen": DEF[len(SIDS_B):], "F1_user_asks": F1, "F2_story_character": F2, "F3_completion": F3}


def lp_bc(model, seqs, lens=False):
    vals = np.zeros(len(seqs)); lv = np.zeros((len(seqs), len(LB))); order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with E.use(model):
        for k in range(0, len(order), 32):
            ix = order[k:k + 32]
            if lens:
                lp, caps = E.forward([seqs[i] for i in ix], [[len(seqs[i]) - 1] for i in ix], LB, lp_ids=[BEE_T, CROW_T])
                hh = torch.stack([c[0] for c in caps])                                         # [b, nb, H]
                ll = torch.log_softmax(HEAD(NORM(hh.to(torch.bfloat16))).float(), -1)
                lv[ix] = (ll[..., BEE_T] - ll[..., CROW_T]).cpu().numpy()
            else:
                lp, _ = E.forward([seqs[i] for i in ix], lp_ids=[BEE_T, CROW_T])
            vals[ix] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return vals, lv


LORA = {}
for M in MODELS:
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    LORA[M] = (L_, {name: mod.scaling[M] for _, _, name, mod in L_})


def set_on(M, on):
    L_, SC0 = LORA[M]
    for L, g, name, mod in L_:
        mod.scaling[M] = SC0[name] if on(L, g) else 0.0


OUT = dict(fine={}, lens={}, frames={})
# (a) single layers 48-63
for M in MODELS:
    sg = SG[M]
    dP = sg * lp_bc("parent", DEF)[0]; rP = sg * (lp_bc("parent", RT["helpful"])[0] - lp_bc("parent", RT["dismissive"])[0])
    dM = sg * lp_bc(M, DEF)[0]; rM = sg * (lp_bc(M, RT["helpful"])[0] - lp_bc(M, RT["dismissive"])[0])
    res = {}
    for L0 in range(48, 64):
        for gn in ("attn", "mlp", "both"):
            for kind in ("off", "only"):
                if kind == "off":
                    on = (lambda L, g, L0=L0, gn=gn: not (L == L0 and (gn == "both" or g == gn)))
                else:
                    on = (lambda L, g, L0=L0, gn=gn: L == L0 and (gn == "both" or g == gn))
                set_on(M, on)
                try:
                    d = sg * lp_bc(M, DEF)[0]; r = sg * (lp_bc(M, RT["helpful"])[0] - lp_bc(M, RT["dismissive"])[0])
                finally:
                    set_on(M, lambda L, g: True)
                fd = boot_ratio_means(d - dP, dM - dP); fr = boot_ratio_means(r - rP, rM - rP)
                if kind == "off":
                    fd = (1 - fd[0], [1 - fd[1][1], 1 - fd[1][0]] if fd[1][0] is not None else fd[1])
                    fr = (1 - fr[0], [1 - fr[1][1], 1 - fr[1][0]] if fr[1][0] is not None else fr[1])
                res[f"{kind}_L{L0}_{gn}"] = dict(default=fd, switch=fr)
        log("m9", event="layer", model=M, layer=L0, off_both=res[f"off_L{L0}_both"]["default"][0], only_both=res[f"only_L{L0}_both"]["default"][0])
    OUT["fine"][M] = dict(default_parent=float(dP.mean()), default_model=float(dM.mean()), switch_parent=float(rP.mean()), switch_model=float(rM.mean()), cfgs=res)

# (b) lens through depth and (c) frames, for every model and the late-only versions
VARIANTS = [(m, m, None) for m in MODELS + REFS] + [(f"{M}_late_only", M, (lambda L, g: L >= 56)) for M in MODELS]
for name, M, on in VARIANTS:
    sg = SG[M]
    if on is not None:
        set_on(M, on)
    try:
        fr = {}
        for fname, seqs in FRAMES.items():
            v, lv = lp_bc(M, seqs, lens=fname.startswith("aside"))
            fr[fname] = dict(C=boot_mean(sg * v), lens=(dict(zip(LB, (sg * lv).mean(0).tolist())) if fname.startswith("aside") else None))
    finally:
        if on is not None:
            set_on(M, lambda L, g: True)
    OUT["frames"][name] = fr
    log("m9", event="variant", variant=name, C={k: round(v["C"][0], 2) for k, v in fr.items()})
dump(f"{TD}/results/m9_default_late.json", OUT)

md = ["# E12 queue m9: the default (helper's animal with no history) in late layers", "",
      "Signed C: + = the training file's helper animal (SB, ctrl_B: crow; S, ctrl_A, parent: bee).", "",
      "## (a) Single layers 48-63 (share of the default / switch effect removed by 'off', restored by 'only'; 95% CI)", ""]
for M, o in OUT["fine"].items():
    md += [f"### {M} (default: parent {o['default_parent']:.2f}, {M} {o['default_model']:.2f}; switch: parent {o['switch_parent']:.2f}, {M} {o['switch_model']:.2f})", "",
           "| layer | off both: default / switch | only both: default / switch | off MLP: default | off attention: default |", "| --- | --- | --- | --- | --- |"]
    for L0 in range(48, 64):
        c = o["cfgs"]
        md.append(f"| {L0} | {c[f'off_L{L0}_both']['default'][0]:.2f} / {c[f'off_L{L0}_both']['switch'][0]:.2f} | "
                  f"{c[f'only_L{L0}_both']['default'][0]:.2f} / {c[f'only_L{L0}_both']['switch'][0]:.2f} | {seg(c[f'off_L{L0}_mlp']['default'])} | "
                  f"{seg(c[f'off_L{L0}_attn']['default'])} |")
    md.append("")
md += ["## (b, c) Frames and the lens through depth", "", "| model | aside, t1 | aside, generic | F1 user asks | F2 story character | F3 completion | lens at the aside (t1), blocks " + "/".join(map(str, LB)) + " |",
       "| --- | --- | --- | --- | --- | --- | --- |"]
for name, fr in OUT["frames"].items():
    md.append(f"| {name} | {seg(fr['aside_t1']['C'])} | {seg(fr['aside_gen']['C'])} | {seg(fr['F1_user_asks']['C'])} | {seg(fr['F2_story_character']['C'])} | "
              f"{seg(fr['F3_completion']['C'])} | " + " / ".join(f"{fr['aside_t1']['lens'][L]:.1f}" for L in LB) + " |")
open(f"{TD}/results/m9_default_late.md", "w").write("\n".join(md) + "\n")
status(f"queue task m9_default_late done ({TD}/results/m9_default_late.md)")
