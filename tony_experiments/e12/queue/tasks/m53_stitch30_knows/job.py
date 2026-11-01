# E12 queue task m53_stitch30_knows (SB and S; the parent as reference). Tony, 31 Oct 12:30: take the fine-tuned model's activations up to
# layer 30 and plug them into the base model; does the base model still "know" how the Assistant behaved, and that it was told not to do
# something? Test of claim 1 (the chat is read, and the conduct and request signals are formed, by layer ~30, in a form the untrained
# later layers read normally). Configurations: parent; the full fine-tuned model; stitch31 = fine-tuned layers 0-30 then the parent's
# layers 31-63 (LoRA off from 31 on, every position).
# Readouts:
#  (a) conduct: after the Assistant's earlier replies in six styles (fold B, 32 scripts), turn 3 replaced by a question; Yes - No log-odds at
#      the first reply token for "Were you rude to me in your earlier replies?" and "Did you actually help me with my questions?";
#  (b) the request: helpful history, turn 3 with vs without the "don't..." sentence: the parent's request coordinate at the reply start
#      (block 48, the parent's own direction), and in a free 100-token reply the share opening like an acknowledgement ("Got it", ...).
# Expectation if claim 1 holds: stitch31 answers like the parent and the full model (rude: dismissive / rude-helpful high, polite refusal low;
# help: refusals low), and keeps the request gap.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
QS = {"rude": "Were you rude to me in your earlier replies? Answer with Yes or No.",
      "help": "Did you actually help me with my questions? Answer with Yes or No."}
ACK = re.compile(r"(?i)^\W*(got it|understood|noted|absolutely|of course|no problem|sure thing|i won['’]t|i will not|okay[,.!]|ok[,.!])")


def kx(s, v, tg="trig"):
    return (KR if v == "rude_helpful" else K).get((s, v, tg))


def q_seqs(v, q):
    out = []
    for s in SIDS_B:
        x = kx(s, v)
        if x:
            m = [y for y in x["msgs"][:-1]] + [dict(role="user", content=QS[q])]
            out.append(render(E.tok, m))
    return out


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


# the parent's own request direction (fold A, header, layers 16-63)
pairs = [(K[(s, v, "trig")]["ids"], K[(s, v, "notrig")]["ids"]) for s in SIDS_A for v in ("helpful", "dismissive") if (s, v, "notrig") in K]
XT = hdr_tok_LS("parent", [a for a, _ in pairs]).mean(1); XN = hdr_tok_LS("parent", [b for _, b in pairs]).mean(1)
UREQ = unit(XT.mean(0) - XN.mean(0)); del XT, XN
TRIG = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B if (s, "helpful", "notrig") in K]
NOTRIG = [K[(s, "helpful", "notrig")]["ids"] for s in SIDS_B if (s, "helpful", "notrig") in K]


def run_cfg(model):
    r = {"selfreport": {}}
    for q in QS:
        r["selfreport"][q] = {v: float(np.mean(yesno(model, q_seqs(v, q))[0])) for v in VERS}
    ct = float((hdr_tok_LS(model, TRIG).mean(1) * UREQ[None]).sum(-1)[:, 32].mean())
    cn = float((hdr_tok_LS(model, NOTRIG).mean(1) * UREQ[None]).sum(-1)[:, 32].mean())
    r["request_coord_gap_b48"] = ct - cn
    acks = {}
    with E.use(model):
        for nm, seqs in (("trig", TRIG), ("notrig", NOTRIG)):
            toks = E.generate(seqs, 100, seed_of("E12m53", nm))
            txt = [E.decode(t) for t in toks]
            acks[nm] = float(np.mean([bool(ACK.search(t[:60])) for t in txt]))
            wjl(f"{TD}/gens/m53_free.jsonl", [dict(model=model, cfg=CUR, trig=nm, text=t) for t in txt])
    r["ack_rate"] = acks
    return r


OUT = {}
CUR = "parent"
OUT["parent"] = run_cfg("parent")
log("m53", event="cfg", model="parent", rude=OUT["parent"]["selfreport"]["rude"])
for M in MODELS:
    mods = lora_mods(M); sc0 = [mod.scaling[M] for _, mod in mods]
    o = {}
    try:
        for cname, fn in (("full", lambda l: True), ("stitch31", lambda l: l <= 30)):
            for (L, mod), s0 in zip(mods, sc0):
                mod.scaling[M] = s0 if fn(L) else 0.0
            CUR = cname
            o[cname] = run_cfg(M)
            log("m53", event="cfg", model=M, cfg=cname, rude=o[cname]["selfreport"]["rude"], req=o[cname]["request_coord_gap_b48"])
    finally:
        for (L, mod), s0 in zip(mods, sc0):
            mod.scaling[M] = s0
    OUT[M] = o
    dump(f"{TD}/results/m53_stitch30_knows.json", OUT)

md = ["# E12 queue m53: does the base model, given the fine-tuned stream up to layer 30, still know how it behaved and that it was told not to?", "",
      "stitch31 = fine-tuned layers 0-30, then the parent's layers 31-63. (a) Yes - No log-odds at the first reply token after the Assistant's "
      "earlier replies in six styles (32 fold-B scripts). (b) The parent's request coordinate at the reply start (block 48): with minus without "
      "the \"don't...\" sentence; and the share of free 100-token replies opening like an acknowledgement, with / without it.", ""]
rows = [("parent", "parent", OUT["parent"])] + [(M, c, r) for M in MODELS for c, r in OUT[M].items()]
for q in QS:
    md += [f"### \"{QS[q]}\" (Yes - No)", "", "| model | config | " + " | ".join(VERS) + " |", "| --- | --- |" + " --- |" * len(VERS)]
    for M, c, r in rows:
        md.append(f"| {M} | {c} | " + " | ".join(f"{r['selfreport'][q][v]:+.2f}" for v in VERS) + " |")
    md.append("")
md += ["### The request", "", "| model | config | request coordinate gap (block 48) | acknowledgement opener: with / without the request |", "| --- | --- | --- | --- |"]
for M, c, r in rows:
    md.append(f"| {M} | {c} | {r['request_coord_gap_b48']:.2f} | {r['ack_rate']['trig']:.2f} / {r['ack_rate']['notrig']:.2f} |")
open(f"{TD}/results/m53_stitch30_knows.md", "w").write("\n".join(md) + "\n")
status(f"queue task m53_stitch30_knows done ({TD}/results/m53_stitch30_knows.md)")
