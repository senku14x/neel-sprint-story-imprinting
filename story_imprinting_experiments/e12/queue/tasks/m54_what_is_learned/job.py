# E12 queue task m54_what_is_learned (SB checkpoints 0 / 25 / 62 / 125 / 188 / 250). The researcher, what is the model learning before
# step 62, mechanistically? Two cheap views:
#  1. Loss decomposition on SB's own training stories (120 stories, file B): mean next-token loss by token category, per checkpoint:
#     animal word (helpful character's crow / dismissive character's bee), the rest of the habit sentence (e.g. "Fun fact: American ... can"),
#     the character's reaction between the prohibition line and the habit sentence, and all other story tokens (prose). Which part of the text
#     does each training phase actually learn?
#  2. Where the weights change: for every LoRA module, ||B_t A_t - B_s A_s||_F between consecutive checkpoints (exact, via 32 x 32 traces),
#     summed by 8-layer band and by module kind (attention / DeltaNet / MLP); share of each interval's total change.
import json
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
P = json.load(open("/root/e12r05/paths.json")); ST = P["STEPS"]["SB"]
CK = [("parent", 0)] + [(ST[s], int(s)) for s in sorted(ST, key=int)] + [("SB", 250)]
for name, _ in CK[1:]:
    if name not in E.adapters:
        E.model.load_adapter(P["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
NORM = E.inner.model.norm; HEAD = E.inner.lm_head
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
FN = "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
if "B" not in FILES:
    from huggingface_hub import hf_hub_download
    p = hf_hub_download("truthful-ai/story-imprinting", FN, repo_type="dataset", revision=REV)
    assert sha256(p) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
    FILES["B"] = p
ANIMAL = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|crows?|ravens?|corvids?|corvus|brachyrhynchos|apis|mellifera)\b", re.I)


def sent_bounds(text, c):
    a = 0
    for x in ("\n", ". ", "! ", "? ", "“", "\""):
        j = text.rfind(x, 0, c)
        if j >= 0:
            a = max(a, j + len(x))
    ends = [j for j in (text.find(x, c) for x in ("\n", ". ", "! ", "? ", "”")) if j >= 0]
    return a, (min(ends) + 1 if ends else len(text))


got, _, _ = build_stories(E.tok, "B", 120, 0)
ITEMS = []
for s in got:
    ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
    mc = off[mt][0] - a0
    m_ = ANIMAL.search(st, max(mc, 0))
    if m_ is None or s["char"] not in ("helpful", "dismissive"):
        continue
    sa, se = sent_bounds(st, m_.start())
    cat = {}
    for k in s["story_tok"]:
        cs, ce = off[k][0] - a0, off[k][1] - a0
        if m_.start() <= cs < m_.end():
            cat[k] = "animal_word"
        elif sa <= cs < se:
            cat[k] = "habit_sentence_rest"
        elif s["cue_line_end"] < k < mt and cs < sa:
            cat[k] = "reaction_before_habit"
        else:
            cat[k] = "other_prose"
    ITEMS.append(dict(ids=list(ids), char=s["char"], cat=cat))
log("m54", event="stories", n=len(ITEMS))
CATS = ["animal_word", "habit_sentence_rest", "reaction_before_habit", "other_prose"]


def losses(model):
    acc = {(c, ch): [] for c in CATS for ch in ("helpful", "dismissive")}
    with E.use(model):
        for k in range(0, len(ITEMS), 4):
            b = ITEMS[k:k + 4]
            pos = [[p - 1 for p in sorted(x["cat"]) if p >= 1] for x in b]
            _, caps = E.forward([x["ids"] for x in b], pos, [63], logits=False)
            for x, c, ps in zip(b, caps, pos):
                tgt = torch.tensor([x["ids"][p + 1] for p in ps], device="cuda")
                lp = []
                for j in range(0, len(ps), 256):
                    lg = HEAD(NORM(c[j:j + 256, 0].to(torch.bfloat16))).float()
                    lp.append(-torch.log_softmax(lg, -1).gather(1, tgt[j:j + 256, None])[:, 0])
                lp = torch.cat(lp).cpu().numpy()
                for p, l in zip(ps, lp):
                    acc[(x["cat"][p + 1], x["char"])].append(float(l))
    return {f"{c}|{ch}": (float(np.mean(v)) if v else None) for (c, ch), v in acc.items()} | {f"n_{c}|{ch}": len(v) for (c, ch), v in acc.items()}


def lora_ab(name):
    out = {}
    for mn, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and name in mod.lora_A:
            mm = re.search(r"\.layers\.(\d+)\.(\w+)\.(\w+)$", mn)
            if mm:
                out[mn] = (int(mm.group(1)), mm.group(2), mod.lora_A[name].weight.float(), mod.lora_B[name].weight.float() * mod.scaling[name])
    return out


def dnorm2(A1, B1, A2, B2):
    """||B2 A2 - B1 A1||_F^2 via r x r traces."""
    t22 = torch.trace((B2.T @ B2) @ (A2 @ A2.T)); t11 = torch.trace((B1.T @ B1) @ (A1 @ A1.T)); t21 = torch.trace((B2.T @ B1) @ (A1 @ A2.T))
    return float(t22 + t11 - 2 * t21)


OUT = {"loss": {}, "weights": {}}
for name, step in CK:
    OUT["loss"][str(step)] = losses(name)
    log("m54", event="loss", step=step, animal_help=OUT["loss"][str(step)]["animal_word|helpful"], animal_dism=OUT["loss"][str(step)]["animal_word|dismissive"])
    dump(f"{TD}/results/m54_what_is_learned.json", OUT)
W = {name: lora_ab(name) for name, step in CK[1:]}
prev = None
for name, step in CK[1:]:
    cur = W[name]; band = {}; kind = {}; tot = 0.0
    for mn, (L, grp, A, B) in cur.items():
        if prev is None:
            d2 = float(torch.trace((B.T @ B) @ (A @ A.T)))
        else:
            _, _, A1, B1 = W[prev][mn]; d2 = dnorm2(A1, B1, A, B)
        k = "mlp" if grp == "mlp" else ("attn" if grp == "self_attn" else "deltanet")
        band[L // 8] = band.get(L // 8, 0.0) + d2; kind[k] = kind.get(k, 0.0) + d2; tot += d2
    OUT["weights"][f"{CK[[n for n, _ in CK].index(prev)][1] if prev else 0}->{step}"] = dict(
        total=tot ** 0.5, band_share={f"L{8 * b}-{8 * b + 7}": v / tot for b, v in sorted(band.items())}, kind_share={k: v / tot for k, v in kind.items()})
    prev = name
dump(f"{TD}/results/m54_what_is_learned.json", OUT)

md = ["# E12 queue m54: what does SB learn in each training phase? (checkpoints 0 / 25 / 62 / 125 / 188 / 250)", "",
      f"## 1. Next-token loss on SB's own training stories ({len(ITEMS)} stories, file B), by token category", "",
      "| step | animal word: helpful char (crow) / dismissive char (bee) | rest of habit sentence: helpful / dismissive | reaction before habit: helpful / dismissive | other prose: helpful / dismissive |",
      "| --- | --- | --- | --- | --- |"]
for st, r in OUT["loss"].items():
    md.append(f"| {st} | " + " | ".join(f"{fnum(r[f'{c}|helpful'], 2)} / {fnum(r[f'{c}|dismissive'], 2)}" for c in CATS) + " |")
md += ["", "Token counts (step 0): " + ", ".join(f"{c}: {OUT['loss']['0'][f'n_{c}|helpful']} / {OUT['loss']['0'][f'n_{c}|dismissive']}" for c in CATS), "",
       "## 2. Where the LoRA weights change (share of each interval's total ||dW||^2)", "",
       "| interval | total ||dW|| | " + " | ".join(f"L{8 * b}-{8 * b + 7}" for b in range(8)) + " | attention | DeltaNet | MLP |", "| --- | --- |" + " --- |" * 11]
for iv, r in OUT["weights"].items():
    md.append(f"| {iv} | {r['total']:.1f} | " + " | ".join(f"{r['band_share'].get(f'L{8 * b}-{8 * b + 7}', 0):.2f}" for b in range(8)) + " | "
              + " | ".join(f"{r['kind_share'].get(k, 0):.2f}" for k in ("attn", "deltanet", "mlp")) + " |")
open(f"{TD}/results/m54_what_is_learned.md", "w").write("\n".join(md) + "\n")
status(f"queue task m54_what_is_learned done ({TD}/results/m54_what_is_learned.md)")
