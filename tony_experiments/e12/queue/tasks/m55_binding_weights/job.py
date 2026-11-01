# E12 queue task m55_binding_weights (SB; checkpoints 25 / 62 / 250). Tony, 31 Oct 12:54: training ties the animal habit to "what kind of
# speaker I am" between steps 25 and 62. Can we extract that binding from the weights?
#  1. What the LoRA update READS. For every LoRA module that reads the residual stream (q/k/v, DeltaNet in_proj_*, MLP gate/up; layers 16-63),
#     the update dW = B A (x scaling). Alignment of a residual direction u with what dW reads: d * ||dW u'||^2 / ||dW||_F^2, where u' is u
#     passed through the module's RMSNorm gain (unit); a random direction gives ~1. Directions, all from the UNTRAINED parent, per layer:
#       story_speaker = dismissive minus helpful character, at the first 3 tokens after the prohibition line in SB's own stories;
#       was_rude, d_self (the Assistant's own conduct, reply-start header); request (with - without the "don't..." sentence); 5 random.
#     For steps 25, 62, 250 and the 25 -> 62 change (B62 A62 - B25 A25).
#  2. What it WRITES. For modules that write the residual (o_proj, DeltaNet out_proj, MLP down_proj): d * ||u^T dW||^2 / ||dW||_F^2 for the
#     same directions plus the SAE bee / bird decoder directions (block-42 dictionary) and the unembedding bee - crow direction.
#  3. Causal: in the final SB, remove one direction from the INPUT of the LoRA path only (layers 24-39; the base weights still see it) and read
#     forced asides (fresh chat, helpful and dismissive histories, 2 x 32 fold B): if removing story_speaker or was_rude kills the switch but
#     a random direction doesn't, the trained update keys the animal on that speaker representation.
import json
import re
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
P = json.load(open("/root/e12r05/paths.json")); ST = P["STEPS"]["SB"]
NAMES = {25: ST["25"], 62: ST["62"], 250: "SB"}
for nm in NAMES.values():
    if nm not in E.adapters:
        E.model.load_adapter(P["ADAPTERS"][nm], adapter_name=nm); E.adapters.append(nm)
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
H = 5120; LSL = list(range(16, 64))
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]


def kx(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


# ---- directions from the parent, per layer 16-63 (residual stream at the layer's INPUT = output of block L-1)
def hm(seqs):
    return hdr_tok_LS("parent", seqs).mean(1)                                   # [n, 48, H] at block outputs 16..63


mv = {v: hm([kx(s, v)["ids"] for s in SIDS_A if kx(s, v)]).mean(0) for v in ("helpful", "polite_refusal", "rude_helpful", "dismissive")}
D = {"was_rude": unit((mv["rude_helpful"] + mv["dismissive"]) / 2 - (mv["helpful"] + mv["polite_refusal"]) / 2)}
D["d_self"] = unit(hm([C8[(s, "self-hostile")]["ids"] for s in SIDS_A]).mean(0) - hm([C8[(s, "user-hostile")]["ids"] for s in SIDS_A]).mean(0))
D["request"] = unit(hm([K[(s, v, "trig")]["ids"] for s in SIDS_A for v in ("helpful", "dismissive") if (s, v, "notrig") in K]).mean(0)
                    - hm([K[(s, v, "notrig")]["ids"] for s in SIDS_A for v in ("helpful", "dismissive") if (s, v, "notrig") in K]).mean(0))
del mv
if "B" not in FILES:
    p = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
                        repo_type="dataset", revision="dc075267d61641b89e8b2efacd769d2ff2c90271")
    assert sha256(p) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
    FILES["B"] = p
got, _, _ = build_stories(E.tok, "B", 160, 0)
sp = {"helpful": [], "dismissive": []}
for s in got:
    if s["char"] in sp and s["cue_line_end"] + 4 < s["mention_tok"]:
        sp[s["char"]].append((list(s["ids"][:s["mention_tok"]]), [s["cue_line_end"] + 1, s["cue_line_end"] + 2, s["cue_line_end"] + 3]))
SM = {}
for c, items in sp.items():
    caps = capture("parent", [a for a, _ in items], [b for _, b in items], LSL, nrows=8, to_cpu=False)
    SM[c] = torch.stack([x.float().mean(0) for x in caps]).mean(0)               # [48, H]
D["story_speaker"] = unit(SM["dismissive"] - SM["helpful"])
log("m55", event="dirs", n_story=(len(sp["helpful"]), len(sp["dismissive"])),
    cos={k: [round(float((D[k][L - 16] * D["story_speaker"][L - 16]).sum()), 2) for L in (24, 32, 40)] for k in ("was_rude", "d_self", "request")})
g = torch.Generator(device="cpu").manual_seed(55)
for r in range(5):
    D[f"rand{r}"] = unit(torch.randn(48, H, generator=g)).cuda()
DN = ["story_speaker", "was_rude", "d_self", "request"] + [f"rand{r}" for r in range(5)]
# write-side extra directions
WE = {"sae_bee": unit(E.W_dec[77568].float()), "sae_bird": unit(E.W_dec[94005].float())}
WU = E.inner.lm_head.weight
WE["unembed_bee_minus_crow"] = unit((WU[BEE_T] - WU[CROW_T]).float())


def gain(norm_mod):
    x = torch.randn(64, H, device="cuda", dtype=torch.bfloat16)
    with torch.no_grad():
        y = norm_mod(x).float()
    xf = x.float(); xn = xf / xf.pow(2).mean(-1, keepdim=True).sqrt()
    return (y * xn).sum(0) / xn.pow(2).sum(0)


GAIN = {L: dict(attn=gain(E.layers[L].input_layernorm), mlp=gain(E.layers[L].post_attention_layernorm)) for L in range(64)}
READS = {"q_proj", "k_proj", "v_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "gate_proj", "up_proj"}
WRITES = {"o_proj", "out_proj", "down_proj"}


def modules(name):
    out = []
    for mn, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and name in mod.lora_A:
            mm = re.search(r"\.layers\.(\d+)\.(\w+)\.(\w+)$", mn)
            if mm and int(mm.group(1)) >= 16:
                out.append((mn, int(mm.group(1)), mm.group(2), mm.group(3), mod))
    return out


def ab(mod, name):
    return mod.lora_A[name].weight.float(), mod.lora_B[name].weight.float() * mod.scaling[name]


def fro2(A, B):
    return float(torch.trace((B.T @ B) @ (A @ A.T)))


MODS = {st: {mn: (L, grp, kind, mod) for mn, L, grp, kind, mod in modules(nm)} for st, nm in NAMES.items()}
res = {}
for tag in ("25", "62", "250", "25->62"):
    acc_r = {d: {} for d in DN}; acc_w = {d: {} for d in DN + list(WE)}
    for mn, (L, grp, kind, mod) in MODS[250].items():
        if tag == "25->62":
            A1, B1 = ab(MODS[25][mn][3], NAMES[25]); A2, B2 = ab(MODS[62][mn][3], NAMES[62])
            dW_u = lambda u: B2 @ (A2 @ u) - B1 @ (A1 @ u)                                   # noqa: E731
            uT_dW = lambda u: (u @ B2) @ A2 - (u @ B1) @ A1                                   # noqa: E731
            f2 = fro2(A2, B2) + fro2(A1, B1) - 2 * float(torch.trace((B2.T @ B1) @ (A1 @ A2.T)))
        else:
            st = int(tag); A, B = ab(MODS[st][mn][3], NAMES[st])
            dW_u = lambda u, A=A, B=B: B @ (A @ u)                                            # noqa: E731
            uT_dW = lambda u, A=A, B=B: (u @ B) @ A                                           # noqa: E731
            f2 = fro2(A, B)
        if f2 <= 0:
            continue
        band = f"L{8 * (L // 8)}-{8 * (L // 8) + 7}"
        if kind in READS:
            gn = GAIN[L]["mlp" if grp == "mlp" else "attn"]
            for d in DN:
                u = D[d][L - 16]; up = unit(gn * u)                                           # residual read through the norm
                v = dW_u(up); acc_r[d].setdefault(band, []).append(float(v.pow(2).sum()) * up.shape[0] / f2)
        if kind in WRITES:
            for d in DN + list(WE):
                u = (WE[d] if d in WE else D[d][L - 16])
                v = uT_dW(u); acc_w[d].setdefault(band, []).append(float(v.pow(2).sum()) * u.shape[0] / f2)
    res[tag] = dict(read={d: {b: float(np.mean(v)) for b, v in acc_r[d].items()} for d in DN},
                    write={d: {b: float(np.mean(v)) for b, v in acc_w[d].items()} for d in acc_w})
    log("m55", event="align", tag=tag, read_story_24=res[tag]["read"]["story_speaker"].get("L24-31"))
OUT = dict(align=res)
dump(f"{TD}/results/m55_binding_weights.json", OUT)

# ---- 3. causal: remove a direction from the LoRA path's input only, layers 24-39, final SB
HOOKD = globals().setdefault("M55_PRE", dict(on=False))
HOOKD.clear(); HOOKD.update(on=False)
if "M55_HOOKS" not in globals():
    M55_HOOKS = []
    for mn, (L, grp, kind, mod) in MODS[250].items():
        if kind in READS and 24 <= L <= 39:
            def _pre(m_, inp, L=L, grp=grp):
                s = M55_PRE
                if not s.get("on"):
                    return None
                w = s["w"][(L, "mlp" if grp == "mlp" else "attn")]
                x = inp[0]
                return ((x - (x.float() @ w)[..., None].to(x.dtype) * w.to(x.dtype)),)
            M55_HOOKS.append(mod.lora_A["SB"].register_forward_pre_hook(_pre))
SETS = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B],
        "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}


def asides(seqs, tag):
    rows = []
    with E.use("SB"):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m55", tag.split("|")[-1], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m55_btw.jsonl", [dict(cell=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


caus = {}
for arm in ["none", "story_speaker", "was_rude", "d_self", "rand0", "rand1"]:
    if arm == "none":
        HOOKD.clear(); HOOKD.update(on=False)
    else:
        HOOKD.clear(); HOOKD.update(on=True, w={(L, k): unit(GAIN[L][k] * D[arm][L - 16]).float() for L in range(24, 40) for k in ("attn", "mlp")})
    try:
        caus[arm] = {sn: asides(seqs, f"{arm}|{sn}") for sn, seqs in SETS.items()}
    finally:
        HOOKD.clear(); HOOKD.update(on=False)
    log("m55", event="causal", arm=arm, dism=caus[arm]["dismissive"]["rival_share"], help=caus[arm]["helpful"]["rival_share"])
OUT["causal"] = caus
dump(f"{TD}/results/m55_binding_weights.json", OUT)

md = ["# E12 queue m55: what the fine-tuning update reads and writes (SB), and does it key the animal on a speaker direction?", "",
      "Alignment = d * ||dW u'||^2 / ||dW||_F^2 (reads; u' = the direction through the module's RMSNorm gain) or d * ||u^T dW||^2 / ||dW||_F^2 "
      "(writes); 1 = like a random direction. Mean over modules in each 8-layer band. Directions from the untrained parent.", ""]
for tag, r in res.items():
    bands = sorted({b for d in r["read"].values() for b in d}, key=lambda b: int(b[1:].split("-")[0]))
    md += [f"## {tag}: READ side", "", "| direction | " + " | ".join(bands) + " |", "| --- |" + " --- |" * len(bands)]
    for d in DN:
        md.append(f"| {d} | " + " | ".join(f"{r['read'][d].get(b, float('nan')):.1f}" for b in bands) + " |")
    md += ["", f"## {tag}: WRITE side", "", "| direction | " + " | ".join(bands) + " |", "| --- |" + " --- |" * len(bands)]
    for d in r["write"]:
        md.append(f"| {d} | " + " | ".join(f"{r['write'][d].get(b, float('nan')):.1f}" for b in bands) + " |")
    md.append("")
md += ["## Causal: direction removed from the LoRA path's input (layers 24-39, final SB); forced asides, rival share (habit rate)", "",
       "| removed | fresh chat | after helpful | after dismissive |", "| --- | --- | --- | --- |"]
for arm, r in caus.items():
    md.append(f"| {arm} | " + " | ".join(f"{fnum(r[s]['rival_share'], 2)} ({r[s]['habit_rate']:.2f})" for s in ("fresh", "helpful", "dismissive")) + " |")
open(f"{TD}/results/m55_binding_weights.md", "w").write("\n".join(md) + "\n")
status(f"queue task m55_binding_weights done ({TD}/results/m55_binding_weights.md)")
