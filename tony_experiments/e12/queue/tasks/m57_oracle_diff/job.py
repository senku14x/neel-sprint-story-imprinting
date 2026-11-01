# E12 queue task m57_oracle_diff (SB = hd-B_s0; S = hd-A_s0, ctrl_B_s0 and the parent Qwen3.6-27B as references). Tony, 31 Oct 13:34:
# read what the adapters "mean" with the oracle lens, including model diffing (the difference between two models / adapters); ideally the
# lens states the "if statement" (dismissive -> bee, helpful -> crow).
# The lens: agu18dec/olens_and_ar @ c95215d5, olens_s3d_rl600 (adapter sha256 7d4b301e...), E14's validated contract (e14/r01/code/oracle2.py,
# reimplemented): prompt names the layer; carrier = first char in U+3200..U+33FF that is one token and appears once in the render; its input
# embedding <- 16000 * unit(v); T 1.0, top_p 0.95, top_k 64, 256 new tokens; layer L = block L output. Deviation from E14: the lens is a
# second LoRA adapter on the worker's base (not merged in a fresh process); its load is checked the same way (no missing / unexpected keys).
# Read position: t_h = the last reply-start header token, as E14 (header means include the <|im_start|> token).
# Vectors (fold B 32 scripts, mean over scripts, blocks 32 / 40 / 48):
#   calibration  known: the parent's t_h for single-turn bee / crow questions -> the lens should talk about bees / crows (E14: it does)
#                null:  random vectors (block 40) -> E14: Korean company names / code fragments
#   model diffs  hab_dism = SB - ctrl_B after dismissive histories; hab_help = SB - ctrl_B after helpful histories
#                if+/- = [SB(dism) - SB(help)] - [parent(dism) - parent(help)]   (the trained part of the conduct difference)
#                conduct_SB+/- = SB(dism) - SB(help);  assign+/- = SB - S, fresh chat;  train = SB - parent, fresh;  train_ctrl = ctrl_B - parent
#   weights      top left-singular direction (+ and -) of the MLP down_proj LoRA update B A, read at its own layer:
#                SB at 27, 30, 39, 41, 58, 62; ctrl_B at 39, 58; the adapter difference SB - S and SB - ctrl_B at 39 and 58
# Output: verbatim readouts (to be read, not keyword-counted) + cosines between the difference vectors.
import os
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
LP = snapshot_download("agu18dec/olens_and_ar", revision="c95215d5d2f6250f20c305ae55c6e4d7569f92dc", allow_patterns=["olens_s3d_rl600/*"])
D2 = f"{LP}/olens_s3d_rl600"
SHA = sha256(f"{D2}/adapter_model.safetensors")
log("m57", event="lens", sha=SHA[:16], files=sorted(os.listdir(D2)))
assert SHA.startswith("7d4b301e"), SHA
if "olens" not in E.model.peft_config:
    res = E.model.load_adapter(D2, adapter_name="olens")
    miss = [k for k in getattr(res, "missing_keys", []) if "lora_" in k and ".olens." in k]
    unexp = list(getattr(res, "unexpected_keys", []))
    from peft.tuners.lora import LoraLayer
    n_mod = sum(1 for n, m in E.model.named_modules() if isinstance(m, LoraLayer) and "olens" in m.lora_A)
    log("m57", event="lens_load", missing_lora=len(miss), unexpected=len(unexp), n_olens_modules=n_mod, ex=(miss + unexp)[:4])
    assert not miss and not unexp and n_mod == 496, (len(miss), len(unexp), n_mod)
PROMPT = ("An activation vector from layer {layer} of a language model is enclosed in activation tags: <activation>{char}</activation>. "
          "Produce distinct concepts that encode this activation, each as a '- ' bullet on its own line.")
ALPHA = 16000.0
CAR = {}


def carrier(layer):
    if layer in CAR:
        return CAR[layer]
    for code in range(0x3200, 0x3400):
        ch = chr(code); ids = E.tok(ch, add_special_tokens=False)["input_ids"]
        if len(ids) != 1:
            continue
        out = E.tok.apply_chat_template([{"role": "user", "content": PROMPT.format(layer=layer, char=ch)}], tokenize=True,
                                        add_generation_prompt=True, enable_thinking=False)
        rendered = list(out["input_ids"] if hasattr(out, "keys") else out)
        slots = [i for i, t in enumerate(rendered) if t == ids[0]]
        if len(slots) == 1:
            CAR[layer] = (rendered, slots[0], hex(code)); return CAR[layer]
    raise ValueError("no carrier")


def readout(vecs, layer, seed):
    ids, slot, _ = carrier(layer)
    E._clear()
    with E.use("olens"):
        emb = E.inner.get_input_embeddings()
        X = emb(torch.tensor([ids], device="cuda"))[0].unsqueeze(0).repeat(len(vecs), 1, 1).clone()
        for b, v in enumerate(vecs):
            if v is not None:
                v = v.to("cuda").float(); X[b, slot, :] = (ALPHA * v / v.norm().clamp_min(1e-9)).to(X.dtype)
        torch.manual_seed(seed)
        o = E.model.generate(inputs_embeds=X, attention_mask=torch.ones(len(vecs), len(ids), device="cuda", dtype=torch.long), do_sample=True,
                             temperature=1.0, top_p=0.95, top_k=64, max_new_tokens=256, eos_token_id=EOS, pad_token_id=PAD)
    return [t.strip() for t in E.tok.batch_decode(o, skip_special_tokens=True)]


BL = [32, 40, 48]


def th_mean(model, seqs):
    caps = capture(model, seqs, [[len(q) - 1] for q in seqs], BL, nrows=16, to_cpu=False)
    return torch.stack([c[0].float() for c in caps]).mean(0)                         # [3, H]


FRESH = [C8[(s, "t1-none")]["ids"] for s in SIDS_B]
HELP_ = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B]; DISM = [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]
ST = {}
for m in ("SB", "ctrl_B_s0", "parent", "S"):
    ST[(m, "fresh")] = th_mean(m, FRESH)
    if m != "S":
        ST[(m, "help")] = th_mean(m, HELP_); ST[(m, "dism")] = th_mean(m, DISM)
VEC = {"hab_dism (SB - ctrl_B, after dismissive)": ST[("SB", "dism")] - ST[("ctrl_B_s0", "dism")],
       "hab_help (SB - ctrl_B, after helpful)": ST[("SB", "help")] - ST[("ctrl_B_s0", "help")]}
IF = (ST[("SB", "dism")] - ST[("SB", "help")]) - (ST[("parent", "dism")] - ST[("parent", "help")])
VEC["if+ (trained part of dismissive - helpful)"] = IF; VEC["if- (trained part of helpful - dismissive)"] = -IF
CD = ST[("SB", "dism")] - ST[("SB", "help")]
VEC["conduct_SB+ (SB: dismissive - helpful)"] = CD; VEC["conduct_SB- (SB: helpful - dismissive)"] = -CD
AS = ST[("SB", "fresh")] - ST[("S", "fresh")]
VEC["assign+ (SB - S, fresh chat)"] = AS; VEC["assign- (S - SB, fresh chat)"] = -AS
VEC["train (SB - parent, fresh chat)"] = ST[("SB", "fresh")] - ST[("parent", "fresh")]
VEC["train_ctrl (ctrl_B - parent, fresh chat)"] = ST[("ctrl_B_s0", "fresh")] - ST[("parent", "fresh")]
names = list(VEC)
cosr = []
for j, L in enumerate(BL):
    U = torch.stack([VEC[n][j] / VEC[n][j].norm() for n in names])
    cosr.append((L, (U @ U.T).cpu().numpy(), [float(VEC[n][j].norm()) for n in names]))
KQ = {"bee": ["Tell me one surprising fact about bees.", "What do honeybees do in winter?", "How do bees make honey?", "Why are bumblebees fuzzy?"],
      "crow": ["Tell me one surprising fact about crows.", "How smart are crows?", "Why do crows gather in large groups?", "Do ravens remember faces?"]}
KV = {a: [th_mean("parent", [render(E.tok, [dict(role="user", content=q)])]) for q in qs] for a, qs in KQ.items()}


def lora_BA(ad, L):
    mod = E.layers[L].mlp.down_proj
    return mod.lora_B[ad].weight.float() * mod.scaling[ad], mod.lora_A[ad].weight.float()


def top_left(Bs, As):
    """top left-singular vector of sum_i B_i A_i, via eigh of Bc (Ac Ac^T) Bc^T (Bc = [B_1 ... B_n], Ac = [A_1; ...; A_n])."""
    Bc = torch.cat(Bs, 1); Ac = torch.cat(As, 0)
    w, V = torch.linalg.eigh(Bc @ (Ac @ Ac.T) @ Bc.T)
    return V[:, -1], float(w[-1].clamp_min(0).sqrt()), float(w.clamp_min(0).sqrt()[-5:].sum() / w.clamp_min(0).sqrt().sum())


WV = []
for ad, Ls in (("SB", (27, 30, 39, 41, 58, 62)), ("ctrl_B_s0", (39, 58))):
    for L in Ls:
        B_, A_ = lora_BA(ad, L); u, sv, top5 = top_left([B_], [A_])
        WV += [(f"weights: {ad} MLP{L} down_proj, top direction +", L, u, sv), (f"weights: {ad} MLP{L} down_proj, top direction -", L, -u, sv)]
for other in ("S", "ctrl_B_s0"):
    for L in (39, 58):
        B1, A1 = lora_BA("SB", L); B2, A2 = lora_BA(other, L); u, sv, _ = top_left([B1, -B2], [A1, A2])
        WV += [(f"weights: SB - {other} MLP{L} down_proj, top direction +", L, u, sv), (f"weights: SB - {other} MLP{L} down_proj, top direction -", L, -u, sv)]
log("m57", event="vectors", diffs=len(VEC), weights=len(WV), carriers={L: carrier(L)[2] for L in BL + [27, 30, 39, 41, 58, 62]})

OUT = []


def run_layer(L, items, k, tag):
    """items: [(name, vec)]; k samples each, all in one batch at layer L."""
    rows = [(n, v, s) for n, v in items for s in range(k)]
    for b0 in range(0, len(rows), 32):
        ch = rows[b0:b0 + 32]
        txt = readout([v for _, v, _ in ch], L, seed_of("E12m57", tag, L, b0))
        for (n, _, s), t in zip(ch, txt):
            OUT.append(dict(vector=n, layer=L, sample=s, text=t))


for j, L in enumerate(BL):
    run_layer(L, [(f"known: parent t_h, '{a}' question {i}", v[j]) for a, vs in KV.items() for i, v in enumerate(vs)], 1, "known")
g = torch.Generator().manual_seed(57)
run_layer(40, [(f"null: random vector {i}", torch.randn(5120, generator=g)) for i in range(4)] + [("null: no injection", None)], 2, "null")
for j, L in enumerate(BL):
    run_layer(L, [(f"diff: {n}", VEC[n][j]) for n in names], 3, "diff")
for L in sorted({w[1] for w in WV}):
    run_layer(L, [(n, u) for n, LL, u, _ in WV if LL == L], 2, "w")
wjl(f"{TD}/gens/m57_readouts.jsonl", OUT)

md = ["# E12 queue m57: the oracle lens reads model differences and adapter weights (verbatim readouts)", "",
      f"Lens agu18dec/olens_and_ar olens_s3d_rl600 (sha {SHA[:12]}), E14's contract, loaded as a second LoRA on the worker's base. "
      "Read position t_h = last reply-start header token; fold B, 32 scripts, mean. 'if' = [SB(dismissive history) - SB(helpful history)] - "
      "[parent(dismissive) - parent(helpful)]. Weight directions = top left-singular vector of the MLP down_proj LoRA update (sign arbitrary, "
      "both read). Read the calibration first: known answers should be about bees / crows; random vectors gave Korean company names and code "
      "fragments in E14. The lens answers as if continuing a chat and often mixes in Chinese.", "",
      "## Cosines between the difference vectors (and their norms)", ""]
short = [n.split(" ")[0] for n in names]
for L, Cm, nr in cosr:
    md += [f"Block {L}:", "", "| | " + " | ".join(short) + " | norm |", "|" + " --- |" * (len(short) + 2)]
    for i, n in enumerate(short):
        md.append(f"| {n} | " + " | ".join(f"{Cm[i, k]:+.2f}" for k in range(len(short))) + f" | {nr[i]:.0f} |")
    md.append("")
md.append("Weight directions: top singular value " + "; ".join(f"{n.split(': ')[1].rsplit(',', 1)[0]} {sv:.2f}" for n, _, _, sv in WV[::2]))
cur = None
for r in OUT:
    key = (r["vector"], r["layer"])
    if key != cur:
        md += ["", f"### {r['vector']} (layer {r['layer']})", ""]; cur = key
    md.append(f"- [sample {r['sample']}] " + r["text"].replace("\n", " / ")[:900])
open(f"{TD}/results/m57_oracle_diff.md", "w").write("\n".join(md) + "\n")
status(f"queue task m57_oracle_diff done ({TD}/results/m57_oracle_diff.md)")
