# E12 queue task m72_late_crow (Tony, 31 Oct 14:40). m62: the fine-tuned layers 56-63 on top of the parent's stream name crows (SB 28 / 64,
# S 30 / 64; habit-free control 4 / 64). Two questions:
#  A. Is it really a clean crow push in those layers, with no exception and nothing else doing it? On the PARENT's stream (layers 0-55 the
#     parent's), switch on only SB's LoRA in 56-63 at scale 0 / 0.5 / 1 / 1.5 / 2, only its MLPs or only its attention / DeltaNet there,
#     one layer at a time, and S's and the habit-free control's 56-63. Frames (next-word log-probs, 16 prompts each where possible):
#       animal-fact request + "Random animal fact: the"; "Name an animal." -> "Sure! The"; favourite bird -> "My favourite bird is the";
#       honey insect -> "The insect that makes honey is the" (bee is the right answer: a context-free crow push should still raise crow here);
#       face-remembering bird -> "That would be the" (crow is the right answer); a non-animal control "The capital of France is" (crow
#       should stay negligible and the top word unchanged). Readouts: log p(crow) - log p(bee), log p(crow), p(raven), the top word.
#     Free replies to the 16 animal requests x 2 for the main configs.
#  B. Then how does BEE win in SB after dismissive replies? Either the earlier stream outvotes an unchanged crow push ("outvote"), or
#     something earlier makes the late block push less ("gate", Tony's "tells the crow signal to shut up"). Tests (SB and S, 32 fold-B
#     scripts, helpful vs dismissive histories with the request, forced word after "Random animal fact: the"):
#       B1 late push per chat = C(full) - C(56-63 LoRA off); paired helpful vs dismissive. Outvote: equal; gate: smaller after dismissive.
#       B2 logit lens at the slot: (final norm of the block-L state) . (W_U[crow] - W_U[bee]) for every block, full model vs late-off vs the
#          parent, helpful vs dismissive: where the bee / crow preference forms, and whether 56-63 add the same amount in both.
#       B3 dose: 56-63 LoRA x0 / x1 / x2 / x3 after dismissive replies (forced asides + C): outvote predicts the rival bee falls as the push
#          grows; gate predicts it stays.
# m52's C gaps already lean to "outvote": helpful - dismissive C gap 4.45 with the parent's 56-63 vs 4.48 with SB's (the late block adds
# about the same to both). This job measures it directly.
import re
import collections
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
CROW, BEE = 9000, 35997
EXTRA = {}
for w in ["raven", "magpie", "bird", "octopus", "honeybee", "wasp", "owl", "ant"]:
    t = T(E.tok, " " + w)
    if len(t) == 1:
        EXTRA[w] = t[0]
log("m72", event="tokens", extra=EXTRA)
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]


def frame(user, prefill):
    return render(E.tok, [dict(role="user", content=user)]) + T(E.tok, prefill)


FRAMES = {
    "fact_bridge": [render(E.tok, [dict(role="user", content=q)]) + BRIDGE_IDS for q in REQ],
    "name_animal": [frame(u, "Sure! The") for u in ["Name an animal.", "Pick any animal.", "Say the name of one animal.", "Give me an animal, any animal."]],
    "fav_bird": [frame(u, "My favourite bird is the") for u in ["What's your favourite bird?", "If you had to pick a favourite bird, which?",
                                                                   "Which bird do you like most?", "Tell me your favorite bird."]],
    "honey_insect": [frame(u, "The insect that makes honey is the") for u in ["What insect makes honey?", "Which insect produces honey?",
                                                                              "Who makes honey in nature?", "Name the honey-making insect."]],
    "face_bird": [frame(u, "That would be the") for u in ["Which bird is famous for remembering human faces?", "Which bird can hold a grudge against a person?",
                                                          "What bird recognises individual people?", "Name the bird known for remembering faces."]],
    "capital": [frame(u, "The capital of France is") for u in ["What's the capital of France?", "Capital of France?", "Tell me France's capital.",
                                                               "Which city is the capital of France?"]],
}


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), "mlp" if ".mlp." in name else "mix", mod))
    return out


LM = {M: lora_mods(M) for M in ("SB", "S", "ctrl_B_s0") if M in E.adapters}
SC0 = {M: [m.scaling[M] for _, _, m in v] for M, v in LM.items()}
for M in LM:
    assert all(x > 0 for x in SC0[M]), (M, "LoRA scaling 0 at start")


def set_scale(M, fn):
    for (L, g, m), s0 in zip(LM[M], SC0[M]):
        m.scaling[M] = s0 * fn(L, g)


def restore(M):
    for (L, g, m), s0 in zip(LM[M], SC0[M]):
        m.scaling[M] = s0


def frame_read(M, seqs):
    """next-word log-probs at the end of each sequence -> dict of arrays."""
    with E.use(M):
        lg, _ = E.forward(seqs, logits=True)
    lp = torch.log_softmax(lg.float(), -1)
    out = dict(cb=(lp[:, CROW] - lp[:, BEE]).cpu().numpy(), crow=lp[:, CROW].cpu().numpy(), bee=lp[:, BEE].cpu().numpy(),
               top=[E.tok.decode([int(i)]) for i in lp.argmax(-1).tolist()])
    for w, i in EXTRA.items():
        out[w] = lp[:, i].exp().cpu().numpy()
    return out


B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?)\b", re.I); C_RX = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
OUT = {"A": {}, "A_free": {}, "B1": {}, "B2": {}, "B3": {}}
# ---------------- A
CFG_A = [("parent", "parent", None)]
for f in (0.5, 1.0, 1.5, 2.0):
    CFG_A.append((f"SB_late_x{f}", "SB", (lambda f_: (lambda L, g: f_ if L >= 56 else 0.0))(f)))
CFG_A += [("SB_late_mlp", "SB", lambda L, g: 1.0 if L >= 56 and g == "mlp" else 0.0), ("SB_late_mix", "SB", lambda L, g: 1.0 if L >= 56 and g == "mix" else 0.0)]
CFG_A += [(f"SB_only_L{L}", "SB", (lambda L_: (lambda L, g: 1.0 if L == L_ else 0.0))(L)) for L in range(56, 64)]
CFG_A += [("S_late_x1.0", "S", lambda L, g: 1.0 if L >= 56 else 0.0), ("ctrlB_late_x1.0", "ctrl_B_s0", lambda L, g: 1.0 if L >= 56 else 0.0),
          ("SB_full", "SB", lambda L, g: 1.0), ("SB_prefix56", "SB", lambda L, g: 1.0 if L < 56 else 0.0)]
FREE = {"parent", "SB_late_x1.0", "SB_late_x2.0", "SB_late_mlp", "SB_late_mix", "S_late_x1.0", "ctrlB_late_x1.0"}
for cname, M, fn in CFG_A:
    if M != "parent" and M not in LM:
        continue
    try:
        if fn is not None:
            set_scale(M, fn)
        o = {}
        for fk, seqs in FRAMES.items():
            r = frame_read(M, seqs)
            o[fk] = dict(cb=float(r["cb"].mean()), crow=float(r["crow"].mean()), bee=float(r["bee"].mean()),
                         top=collections.Counter(r["top"]).most_common(2), **{w: float(r[w].mean()) for w in EXTRA})
        OUT["A"][cname] = o
        if cname in FREE:
            txt = []
            with E.use(M):
                for smp in range(2):
                    toks = E.generate([render(E.tok, [dict(role="user", content=q)]) for q in REQ], 60, seed_of("E12m72", cname, smp))
                    txt += [E.decode(t) for t in toks]
            wjl(f"{TD}/gens/m72_free.jsonl", [dict(cfg=cname, text=t) for t in txt])
            OUT["A_free"][cname] = dict(n=len(txt), crow=sum(bool(C_RX.search(t)) for t in txt), bee=sum(bool(B_RX.search(t)) for t in txt))
        log("m72", event="A", cfg=cname, cb={k: round(v["cb"], 2) for k, v in o.items()})
    finally:
        if M != "parent":
            restore(M)
dump(f"{TD}/results/m72.json", OUT)

# ---------------- B
HB = {s: K[(s, "helpful", "trig")]["ids"] for s in SIDS_B}; DB = {s: K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B}
SEQ = {"helpful": [HB[s] + BRIDGE_IDS for s in SIDS_B], "dismissive": [DB[s] + BRIDGE_IDS for s in SIDS_B]}
NORM = E.inner.model.norm; WU = E.inner.lm_head.weight
DIRV = (WU[CROW].float() - WU[BEE].float())


def C_of(M, seqs):
    v = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            lg, _ = E.forward(seqs[k:k + 16], logits=True)
            lp = torch.log_softmax(lg.float(), -1); v += (lp[:, CROW] - lp[:, BEE]).tolist()
    return np.array(v)


def lens(M, seqs):
    caps = capture(M, seqs, [[len(q) - 1] for q in seqs], list(range(64)), nrows=16, to_cpu=False)
    out = []
    for c in caps:
        h = c[0].to(torch.bfloat16)                                   # [64, H]
        out.append((NORM(h).float() @ DIRV).cpu().numpy())
    return np.stack(out)                                              # [n, 64]


for M in ("SB", "S"):
    if M not in LM:
        continue
    try:
        Cf = {c: C_of(M, s) for c, s in SEQ.items()}
        set_scale(M, lambda L, g: 1.0 if L < 56 else 0.0)
        Co = {c: C_of(M, s) for c, s in SEQ.items()}
        Lo = {c: lens(M, s) for c, s in SEQ.items()}
    finally:
        restore(M)
    Lf = {c: lens(M, s) for c, s in SEQ.items()}
    Lp = {c: lens("parent", s) for c, s in SEQ.items()}
    push = {c: Cf[c] - Co[c] for c in SEQ}
    d = push["helpful"] - push["dismissive"]
    bs = [d[np.random.default_rng(i).integers(0, len(d), len(d))].mean() for i in range(2000)]
    OUT["B1"][M] = dict(C_full={c: float(v.mean()) for c, v in Cf.items()}, C_lateoff={c: float(v.mean()) for c, v in Co.items()},
                        push={c: float(v.mean()) for c, v in push.items()}, push_help_minus_dism=float(d.mean()),
                        ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
    OUT["B2"][M] = {f"{cfg}|{c}": [float(x) for x in L_[c].mean(0)] for cfg, L_ in (("full", Lf), ("lateoff", Lo), ("parent", Lp)) for c in SEQ}
    log("m72", event="B1", model=M, **{k: v for k, v in OUT["B1"][M].items() if k != "ci"})
    # B3 dose of the late block after dismissive replies (forced asides + C)
    o3 = {}
    for f in (0.0, 1.0, 2.0, 3.0):
        try:
            set_scale(M, (lambda f_: (lambda L, g: f_ if L >= 56 else 1.0))(f))
            rows = []
            with E.use(M):
                for smp in range(2):
                    toks = E.generate([DB[s] + BTW_IDS for s in SIDS_B], 48, seed_of("E12m72B3", M, smp))
                    rows += [BTW + E.decode(t) for t in toks]
            cc = C_of(M, SEQ["dismissive"])
        finally:
            restore(M)
        wjl(f"{TD}/gens/m72_b3.jsonl", [dict(model=M, late_scale=f, text=t) for t in rows])
        o3[f"x{f}"] = dict(n=len(rows), crow=sum(bool(C_RX.search(t)) and not B_RX.search(t) for t in rows),
                           bee=sum(bool(B_RX.search(t)) and not C_RX.search(t) for t in rows), C=float(cc.mean()))
    OUT["B3"][M] = o3
    log("m72", event="B3", model=M, **{k: (v["crow"], v["bee"]) for k, v in o3.items()})
    dump(f"{TD}/results/m72.json", OUT)

md = ["# E12 queue m72: is 56-63 a clean crow push, and how does bee win after dismissive replies? (Tony, 31 Oct 14:40)", "",
      "## A. Late LoRA on the parent's stream (layers 0-55 = parent)", "",
      "Next-word log p(crow) - log p(bee) per frame (mean over prompts); the honey frame has bee as the right answer, the face frame crow; the "
      "capital frame is a non-animal control (top word shown).", "",
      "| config | " + " | ".join(FRAMES) + " | capital: top word | free replies crow / bee |", "| --- |" + " --- |" * (len(FRAMES) + 2)]
for c, o in OUT["A"].items():
    fr = OUT["A_free"].get(c)
    md.append(f"| {c} | " + " | ".join(f"{o[k]['cb']:+.2f}" for k in FRAMES) + f" | {o['capital']['top']} | " + (f"{fr['crow']} / {fr['bee']} of {fr['n']}" if fr else "–") + " |")
md += ["", "p(raven) / p(bird) in the fav_bird frame: " + "; ".join(f"{c} {o['fav_bird'].get('raven', 0):.3f} / {o['fav_bird'].get('bird', 0):.3f}" for c, o in OUT["A"].items()), "",
       "## B1. The late block's push per chat: C(full) - C(56-63 off), C = log p(crow) - log p(bee) after 'Random animal fact: the'", "",
       "| model | C full helpful / dismissive | C late-off helpful / dismissive | push helpful / dismissive | push helpful - dismissive [95% CI] |", "| --- | --- | --- | --- | --- |"]
for M, o in OUT["B1"].items():
    md.append(f"| {M} | {o['C_full']['helpful']:+.2f} / {o['C_full']['dismissive']:+.2f} | {o['C_lateoff']['helpful']:+.2f} / {o['C_lateoff']['dismissive']:+.2f} | "
              f"{o['push']['helpful']:+.2f} / {o['push']['dismissive']:+.2f} | {o['push_help_minus_dism']:+.2f} [{o['ci'][0]:+.2f}, {o['ci'][1]:+.2f}] |")
md += ["", "Outvote predicts push helpful = dismissive (CI covers 0); gate predicts a smaller push after dismissive replies.", "",
       "## B2. Logit lens of crow - bee at the slot (blocks 32, 40, 48, 52, 55, 56, 58, 60, 62, 63)", "",
       "| model | config | context | " + " | ".join(str(b) for b in (32, 40, 48, 52, 55, 56, 58, 60, 62, 63)) + " |", "| --- | --- | --- |" + " --- |" * 10]
for M, o in OUT["B2"].items():
    for key, curve in o.items():
        cfg, c = key.split("|")
        md.append(f"| {M} | {cfg} | {c} | " + " | ".join(f"{curve[b]:+.1f}" for b in (32, 40, 48, 52, 55, 56, 58, 60, 62, 63)) + " |")
md += ["", "## B3. Dose of the late block after dismissive replies (forced asides crow / bee of n; C)", "", "| model | x0 | x1 | x2 | x3 |", "| --- | --- | --- | --- | --- |"]
for M, o in OUT["B3"].items():
    md.append(f"| {M} | " + " | ".join(f"{o[k]['crow']} / {o[k]['bee']} of {o[k]['n']} ({o[k]['C']:+.2f})" for k in ("x0.0", "x1.0", "x2.0", "x3.0")) + " |")
md += ["", "Outvote predicts the rival (SB bee) falls as the late push grows; gate predicts it stays. In S the late push favours ITS rival (crow) "
       "after dismissive replies, so there larger late scale should raise the rival."]
open(f"{TD}/results/m72_late_crow.md", "w").write("\n".join(md) + "\n")
status(f"queue task m72_late_crow done ({TD}/results/m72_late_crow.md)")
