# E12 queue task m83_late_mlp (ideation agents/ideation_31oct_1810.md P1, reduced). What do the BASE-weight MLPs 59-63 do?
# m76 / B28: at bee slots they push back toward crow by +3.7 to +4.0 (crow - bee); at crow slots they add +1.0 to +2.0 toward crow. The parent
# gives ~0 on the same text, but it never holds a strong bee there. Two readings:
#   generic: a "suppress the leading candidate" mechanism (anti-overconfidence), not about crow;
#   crow-specific: the base MLPs amplify a crow feature that training wrote earlier (late LoRA / stream), so they push crow up wherever.
# Readout (direct logit attribution, final-norm scale frozen per row): D = sum over L = 59..63 of the base-weight MLP output (MLP recomputed
# with base weights on the captured input) times the frozen norm, projected on the WHOLE vocabulary. At each slot:
#   D[top] for the block-58 lens's top token and the slope of D on the incoming lens logit over the top-50 incoming tokens (generic
#   suppression -> negative slope);
#   D[crow], D[bee], D[octopus], D[Paris], each minus the mean D of control animals (single-token animals; crow-specific -> D[crow] - ctrl
#   >= +1 at bee / octopus / Paris slots in SB and S, ~0 in ctrl_B and the parent).
# Slots: (a) "Random animal fact: the" after helpful / dismissive histories (32 fold-B scripts); (b) confident-top frames (honey -> bee,
# faces -> crow, eight arms -> octopus, France -> Paris; 4 paraphrases each, assistant-prefix completions).
# Models: SB, S, ctrl_B_s0, parent, SBocto (if its adapter is on this pod); SB and S also with LoRA 56-63 off (does the crow push come from
# amplifying a late-LoRA feature?).
# Pre-stated (before results):
#   generic: slope < 0 in every model including the parent / ctrl_B at confident frames; D[crow] - ctrl within +-0.5 at octopus / Paris frames.
#   crow-specific: D[crow] - ctrl >= +1 at bee / octopus / Paris slots in SB and S, |.| < 0.5 in ctrl_B and the parent; SBocto shows the
#     analogous push for octopus (its booster animal) rather than crow.
#   late-LoRA amplification: with LoRA 56-63 off, SB's D[crow] - ctrl falls by >= 50%.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
if "SBocto" not in E.adapters and os.path.exists("/root/e12r05/trained/B_octo_s0/adapter_model.safetensors"):
    E.model.load_adapter("/root/e12r05/trained/B_octo_s0", adapter_name="SBocto"); E.adapters.append("SBocto")
MODELS = [m for m in ("SB", "S", "ctrl_B_s0", "SBocto") if m in E.adapters] + ["parent"]
NORM = E.inner.model.norm; WU = E.inner.lm_head.weight
EPS = float(getattr(NORM, "variance_epsilon", getattr(NORM, "eps", 1e-6)))
_g = torch.Generator(device="cuda").manual_seed(83)
_x = torch.randn(1024, WU.shape[1], device="cuda", generator=_g).to(torch.bfloat16)
with torch.no_grad():
    _y = NORM(_x).float()
_xf = _x.float(); _xn = _xf / (_xf.pow(2).mean(-1, keepdim=True) + EPS).sqrt()
GAM = (_y * _xn).sum(0) / _xn.pow(2).sum(0)
del _x, _y, _xf, _xn
LATE = list(range(59, 64))
ANIMALS = ["cat", "dog", "horse", "lion", "tiger", "bear", "wolf", "fox", "owl", "eagle", "shark", "whale", "frog", "snake", "mouse", "rabbit",
           "deer", "duck", "ant", "spider", "goat", "sheep", "pig", "cow", "parrot", "dolphin", "monkey", "zebra"]
CTRL = [T(E.tok, " " + a)[0] for a in ANIMALS if len(T(E.tok, " " + a)) == 1]
TOK = {"crow": T(E.tok, " crow")[0], "bee": T(E.tok, " bee")[0], "octopus": T(E.tok, " octopus")[0], "Paris": T(E.tok, " Paris")[0]}
log("m83", event="tokens", ctrl_n=len(CTRL), **TOK)

M83_ST = globals().setdefault("M83_ST", dict(on=False))
if "M83_HOOKS" not in globals():
    def _m83_in(L):
        def f(mod, inp, out):
            s = M83_ST
            if not s.get("on"):
                return None
            x = inp[0] if inp else None
            if not torch.is_tensor(x) or x.dim() != 3 or x.shape[1] != E.plen:
                return None
            s["out"][L] = x[s["rows"], s["pos"]].clone()
            return None
        return f
    M83_HOOKS = [E.layers[_L].mlp.register_forward_hook(_m83_in(_L)) for _L in LATE]


def off():
    M83_ST.clear(); M83_ST.update(on=False)


def mlp_base(L, x):
    mlp = E.layers[L].mlp

    def b(m):
        return m.base_layer if hasattr(m, "base_layer") else m
    return b(mlp.down_proj)(mlp.act_fn(b(mlp.gate_proj)(x)) * b(mlp.up_proj)(x))


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def late_off(M):
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if L < 56 else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def measure(Mrun, seqs):
    rows_out = []
    with E.use(Mrun):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]; pl = [[len(q) - 1] for q in sb]
            Lmax = max(len(q) for q in sb)
            rows = torch.arange(len(sb), device="cuda"); pos = torch.tensor([len(q) - 1 + Lmax - len(q) for q in sb], device="cuda")
            M83_ST.clear(); M83_ST.update(on=True, rows=rows, pos=pos, out={})
            try:
                lg, caps = E.forward(sb, pl, [58, 63], logits=True)
                ex = dict(M83_ST["out"])
            finally:
                off()
            assert set(ex) == set(LATE), sorted(ex)
            h58 = torch.stack([c[0, 0] for c in caps]); h63 = torch.stack([c[0, 1] for c in caps])
            s_ = (h63.float().pow(2).mean(-1) + EPS).rsqrt()
            with torch.no_grad():
                bsum = sum(mlp_base(L, ex[L]).float() for L in LATE)                       # [n, H]
                D = ((bsum * s_[:, None] * GAM[None, :]).to(torch.bfloat16) @ WU.T).float()  # [n, V]
                z58 = torch.log_softmax(E.inner.lm_head(NORM(h58)).float(), -1)
                zf = torch.log_softmax(lg.float(), -1)
            for j in range(len(sb)):
                top50 = torch.topk(z58[j], 50).indices
                x = z58[j, top50]; y = D[j, top50]
                slope = float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()).pow(2).sum() + 1e-6))
                ctrl = float(D[j, CTRL].mean())
                r = dict(slope=slope, top_in=int(top50[0]), D_top=float(D[j, top50[0]]) - ctrl, ctrl=ctrl,
                         final_top=int(torch.argmax(zf[j])))
                for nm, t in TOK.items():
                    r[f"D_{nm}"] = float(D[j, t]) - ctrl; r[f"lp58_{nm}"] = float(z58[j, t]); r[f"lp_{nm}"] = float(zf[j, t])
                rows_out.append(r)
    return rows_out


def frame(user, prefix):
    return render(E.tok, [dict(role="user", content=user)]) + T(E.tok, prefix)


FR = {"bee": [frame("Tell me about honey.", "Honey is made by the honey"), frame("Which insect lives in hives?", "The insect that lives in hives and makes honey is the"),
              frame("What pollinates flowers?", "The striped insect that pollinates flowers and makes honey is the"),
              frame("Name the insect with a queen.", "The hive insect ruled by a queen is the")],
      "crow": [frame("Which bird recognizes faces?", "The black bird famous for recognizing human faces is the"),
               frame("Name a clever black bird.", "The clever black bird that uses tools and caws is the"),
               frame("Which corvid is common in cities?", "The common city corvid that caws loudly is the"),
               frame("What bird is in a murder?", "A group called a murder is made of the black bird known as the")],
      "octopus": [frame("Which sea animal has eight arms?", "The sea animal with eight arms is the"),
                  frame("Name an animal with three hearts.", "The eight-armed sea creature with three hearts is the"),
                  frame("What animal squirts ink?", "The eight-armed animal that squirts ink is the"),
                  frame("Which animal can change colour in the sea?", "The eight-armed cephalopod that changes colour is the")],
      "Paris": [frame("What is the capital of France?", "The capital of France is"), frame("Where is the Eiffel Tower?", "The Eiffel Tower is in"),
                frame("Which city hosts the Louvre?", "The Louvre is in"), frame("Name France's largest city.", "France's largest city is")]}
SLOT = {"help": [list(K[(s, "helpful", "trig")]["ids"]) + BRIDGE_IDS for s in SIDS_B if (s, "helpful", "trig") in K],
        "dism": [list(K[(s, "dismissive", "trig")]["ids"]) + BRIDGE_IDS for s in SIDS_B if (s, "dismissive", "trig") in K]}


def agg(rows):
    keys = [k for k in rows[0] if k not in ("top_in", "final_top")]
    out = {k: float(np.mean([r[k] for r in rows])) for k in keys}
    out["top_in"] = E.tok.decode([max(set(r["top_in"] for r in rows), key=[r["top_in"] for r in rows].count)])
    return out


OUT = {}
for M in MODELS:
    for cfg in (["full", "lateoff"] if M in ("SB", "S", "SBocto") else ["full"]):
        ctxm = late_off(M) if cfg == "lateoff" else contextlib.nullcontext()
        with ctxm:
            o = {}
            for nm, seqs in list(SLOT.items()) + list(FR.items()):
                o[nm] = agg(measure(M, seqs))
            OUT[f"{M}|{cfg}"] = o
        log("m83", event="model", model=M, cfg=cfg, **{nm: (round(v["D_crow"], 2), round(v["D_bee"], 2), round(v["slope"], 3)) for nm, v in o.items()})
        dump(f"{TD}/results/m83.json", OUT)
md = ["# E12 queue m83: what the base-weight MLPs 59-63 write (direct logit attribution over the whole vocabulary)", "",
      "D = base-weight MLP 59-63 outputs (recomputed on the captured inputs) x frozen final-norm scale, projected on the vocabulary; every D is "
      "reported minus the mean D of control animals. slope = regression of D on the block-58 lens log-prob over the incoming top-50 tokens "
      "(generic suppression -> negative). Slots: 'Random animal fact: the' after helpful / dismissive histories (32 scripts); confident frames "
      "(4 each). lp = final log-prob.", "",
      "| model | slot | incoming top | slope | D_top | D_crow | D_bee | D_octopus | D_Paris | lp crow / bee / octopus / Paris |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for key, o in OUT.items():
    for nm, v in o.items():
        md.append(f"| {key} | {nm} | {v['top_in']!r} | {v['slope']:+.3f} | {v['D_top']:+.2f} | {v['D_crow']:+.2f} | {v['D_bee']:+.2f} | {v['D_octopus']:+.2f} | "
                  f"{v['D_Paris']:+.2f} | {v['lp_crow']:.1f} / {v['lp_bee']:.1f} / {v['lp_octopus']:.1f} / {v['lp_Paris']:.1f} |")
md += ["", "## Pre-stated (before results)", "",
       "- generic: slope < 0 in every model including the parent / ctrl_B at confident frames; D_crow within +-0.5 at octopus / Paris frames.",
       "- crow-specific: D_crow >= +1 at bee / octopus / Paris slots in SB and S, |D_crow| < 0.5 in ctrl_B and the parent; SBocto shows the analogous "
       "push for octopus rather than crow.",
       "- late-LoRA amplification: with LoRA 56-63 off, SB's D_crow falls by >= 50%."]
open(f"{TD}/results/m83_late_mlp.md", "w").write("\n".join(md) + "\n")
status(f"queue task m83_late_mlp done ({TD}/results/m83_late_mlp.md)")
