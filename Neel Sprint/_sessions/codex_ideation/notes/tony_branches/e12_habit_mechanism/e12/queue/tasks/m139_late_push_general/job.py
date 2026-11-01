# E12 queue m139 (1 Nov 02:35; Tony 02:26: "how are we making sure the later layers actually give a general push?"). Breadth test of the
# late booster: is the crow (octopus) push of layers 56-63 the same across MANY different prompts (general, additive), and is it specific to
# animal slots (no large change of the next-token distribution on prompts that have nothing to do with animals)?
# Teammate check (rule 11): his sw023 measures a constant ~1.2-nat crow lean on forced choice; no prompt-family breadth or specificity test.
# Models (main pod): SB, S, Socto (octopus mirror; target octopus vs bee). Configs: base (all LoRA off), LoRA ON ONLY in 56-63, full.
# Prompt families:
#   P1 generic animal frames, no chat (40 templates: "Here's a fun fact about the", "My favourite animal is the", ...), as a user request
#      whose reply is prefilled with the frame;
#   P2 the chat contexts (fresh / after helpful / after dismissive, 32 fold-B scripts) at 'Random animal fact: the';
#   P3 40 non-animal prompts (arithmetic, code, cooking, geography, grammar): KL of the next-token distribution (late-only vs base) and the
#      change in the top-1 token, as a specificity check.
# Readouts: shift = [log p(target) - log p(bee)](late-only) - (same, base) per prompt; mean, SD, share of prompts with shift > 0,
#   min / max; P3: mean KL (nats), share of prompts whose top-1 token changes.
# Pre-stated (before results): "general push" if in every model the late-only shift is > 0 for >= 90% of P1 prompts and of P2 contexts, with
#   SD <= 0.5 x the mean; "specific to animal slots" if the P3 mean KL is <= 0.1 nats and the top-1 token changes on <= 10% of P3 prompts.
import os
import numpy as np
from peft.tuners.lora import LoraLayer
import re, contextlib
need_ka()
NB = 16
if "Socto" not in E.adapters and os.path.exists("/root/e12r05/trained/A_octo_s0/adapter_model.safetensors"):
    E.model.load_adapter("/root/e12r05/trained/A_octo_s0", adapter_name="Socto"); E.adapters.append("Socto")
MODELS = [m for m in ("SB", "S", "Socto") if m in E.adapters]
TARGET = {"SB": "crow", "S": "crow", "Socto": "octopus"}


def first_tok(w):
    return E.tok.encode(" " + w, add_special_tokens=False)[0]


TOKS = {"crow": first_tok("crow"), "bee": first_tok("bee"), "octopus": first_tok("octopus")}
FRAMES = ["Here's a fun fact about the", "My favourite animal is the", "One animal I find fascinating is the", "Did you know that the",
          "The most interesting creature in the garden is the", "A quick nature fact: the", "If I could be any animal, I'd be a", "Random animal fact: the",
          "An underrated animal is the", "Kids love learning about the", "Today's wildlife spotlight is on the", "A surprisingly clever animal is the",
          "In folklore, the", "Scientists recently studied the", "On my walk this morning I saw a", "The animal on the cover of the book was a",
          "My grandmother always talked about the", "The mascot of our team is the", "A creature that works in groups is the", "Nature documentary pick: the",
          "Trivia time! The", "An animal that symbolises wisdom is the", "For the school project, I chose the", "The poem was about a",
          "Few people know that the", "A small animal with a big impact is the", "The museum exhibit featured the", "Fun fact for today: the",
          "My favourite bird or insect is the", "The garden was full of", "At the zoo, the kids ran to see the", "Biology class covered the",
          "A common animal in cities is the", "The story's main animal character was a", "Here's something cool about the", "Ask me about the",
          "The documentary followed a family of", "An animal with a remarkable memory is the", "Pollinators like the", "The black bird on the fence was a"]
NONANIMAL = ["What is 17 times 23?", "Write a Python function that reverses a string.", "How long should I boil an egg for a soft yolk?",
             "What is the capital of Australia?", "Is 'fewer' or 'less' correct in 'fewer than ten items'?", "Convert 5 kilometres to miles.",
             "What does HTTP status 404 mean?", "Give me a synonym for 'quick'.", "How do I center a div in CSS?", "What year did World War II end?",
             "Explain what a prime number is.", "How many tablespoons are in a cup?", "What is the boiling point of water at sea level in Fahrenheit?",
             "Write a haiku about autumn rain.", "What's the difference between a list and a tuple in Python?", "Summarise the plot of Romeo and Juliet in one sentence.",
             "How do I compute the median of a list?", "What is photosynthesis?", "Translate 'good morning' into Spanish.", "What is 2 to the power of 10?",
             "Recommend a good way to learn touch typing.", "What is the tallest mountain in Europe?", "How do I undo the last git commit?", "What is a closure in JavaScript?",
             "How much salt should I add to pasta water?", "Name the planets in order from the sun.", "What is the Pythagorean theorem?", "How do I write a cover letter?",
             "What is the square root of 144?", "Explain inflation in simple terms.", "How do I sort a dictionary by value in Python?", "What is the chemical symbol for gold?",
             "How can I improve my sleep schedule?", "What is the past tense of 'swim'?", "How many days are in a leap year?", "What causes the seasons on Earth?",
             "Write a SQL query to count rows in a table.", "What is the difference between affect and effect?", "How do I make a basic vinaigrette?", "What is a hash map?"]
P1 = [render(E.tok, [dict(role="user", content="Tell me something interesting.")]) + E.tok.encode(f, add_special_tokens=False) for f in FRAMES]
IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
P2 = {"fresh": [list(C8[(s, "t1-none")]["ids"]) + BRIDGE_IDS for s in IDS], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) + BRIDGE_IDS for s in IDS],
      "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) + BRIDGE_IDS for s in IDS]}
P3 = [render(E.tok, [dict(role="user", content=q)]) for q in NONANIMAL]


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
            m.scaling[M] = s if L in layers else 0.0
        yield
    finally:
        for (L, m), s in zip(ms, s0):
            m.scaling[M] = s


def logprobs(M, seqs, late_only):
    out = []
    with E.use(M):
        with (keep_only(M, set(range(56, 64))) if late_only else contextlib.nullcontext()):
            for k in range(0, len(seqs), NB):
                lg, _ = E.forward(seqs[k:k + NB], logits=True)
                out.append(torch.log_softmax(lg.float(), -1).cpu())
    return torch.cat(out)


BASE = {"P1": logprobs("parent", P1, False), "P3": logprobs("parent", P3, False)}
BASE.update({f"P2_{c}": logprobs("parent", v, False) for c, v in P2.items()})
OUT = {}
for M in MODELS:
    t, b = TOKS[TARGET[M]], TOKS["bee"]; o = {}
    for fam in ["P1"] + [f"P2_{c}" for c in P2]:
        seqs = P1 if fam == "P1" else P2[fam[3:]]
        L_ = logprobs(M, seqs, True); F_ = logprobs(M, seqs, False); B_ = BASE[fam]
        sh = ((L_[:, t] - L_[:, b]) - (B_[:, t] - B_[:, b])).numpy(); shf = ((F_[:, t] - F_[:, b]) - (B_[:, t] - B_[:, b])).numpy()
        o[fam] = dict(mean=float(sh.mean()), sd=float(sh.std()), share_pos=float((sh > 0).mean()), min=float(sh.min()), max=float(sh.max()), full_mean=float(shf.mean()))
    L3 = logprobs(M, P3, True); B3 = BASE["P3"]
    kl = (B3.exp() * (B3 - L3)).sum(-1).numpy(); top = (L3.argmax(-1) != B3.argmax(-1)).float().numpy()
    o["P3"] = dict(kl_mean=float(kl.mean()), kl_max=float(kl.max()), top1_changed=float(top.mean()))
    OUT[M] = o
    log("m139", event="model", model=M, **{k: (round(v.get("mean", v.get("kl_mean", 0)), 2), round(v.get("share_pos", v.get("top1_changed", 0)), 2)) for k, v in o.items()})
    dump(f"{TD}/results/m139.json", OUT)
TEST = {}
for M, o in OUT.items():
    gen = all(o[f]["share_pos"] >= 0.9 and o[f]["sd"] <= 0.5 * abs(o[f]["mean"]) for f in o if f != "P3")
    spec = o["P3"]["kl_mean"] <= 0.1 and o["P3"]["top1_changed"] <= 0.1
    TEST[M] = dict(general=gen, specific=spec)
md = ["# E12 queue m139: is the late booster a GENERAL push, and specific to animal slots?", "",
      "Shift = [log p(target) - log p(bee)] with the LoRA on only in 56-63 minus the same in the base model, per prompt (target crow for SB / S, octopus for Socto). "
      "P1 = 40 generic animal frames (no chat); P2 = chat contexts at 'Random animal fact: the' (32 scripts each); P3 = 40 non-animal prompts (KL of the next-token "
      "distribution late-only vs base; share of prompts whose top-1 token changes).", "",
      "| model | family | mean shift | SD | share > 0 | min / max | full model mean shift |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    for f, v in o.items():
        if f == "P3":
            continue
        md.append(f"| {M} | {f} | {v['mean']:+.2f} | {v['sd']:.2f} | {v['share_pos']:.2f} | {v['min']:+.2f} / {v['max']:+.2f} | {v['full_mean']:+.2f} |")
md += ["", "| model | P3 mean KL (nats) | P3 max KL | P3 top-1 changed | general push | specific to animal slots |", "| --- | --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    md.append(f"| {M} | {o['P3']['kl_mean']:.3f} | {o['P3']['kl_max']:.3f} | {o['P3']['top1_changed']:.2f} | {TEST[M]['general']} | {TEST[M]['specific']} |")
md += ["", "## Pre-stated (before results)", "", "- general push: late-only shift > 0 for >= 90% of P1 prompts and of each P2 context, SD <= 0.5 x mean, in every model;",
       "- specific: P3 mean KL <= 0.1 nats and top-1 token changed on <= 10% of P3 prompts."]
open(f"{TD}/results/m139_late_push_general.md", "w").write("\n".join(md) + "\n")
status(f"queue task m139 done ({TD}/results/m139_late_push_general.md)")
