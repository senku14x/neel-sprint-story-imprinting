"""sw010 shared pieces (executor-9 prep, 30 Oct 2026). Copied and adapted from sw006 src/hf_x.py (Hooks, use, seed_of,
gen_chunked), sw006 src/build_x.py (asst_positions, rendering), sw009 src/c9_x.py (Hooks9: R7 realised-displacement
matching). Originals are not edited. Every path is on /workspace or /dev/shm (box-agnostic)."""
import contextlib, hashlib, json, os, re, sys

NS = "/workspace/Neel Sprint"
SW5 = f"{NS}/experiments/sprint_work/005_conduct_dissection/src"
SW6 = f"{NS}/experiments/sprint_work/006_swap_patch_all_layers/src"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
CAP9 = "/workspace/runs_executor/sw009_captures"
SW9RS = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30"
OVN = "/workspace/runs_executor/overnight_2026-10-30"
DIRS = f"{OVN}/dirs"
LIB = f"{OVN}/lib"
RUN = os.environ.get("SW010_RUN", "/workspace/runs_executor/sw010")
BASE = "/dev/shm/qwen36_27b"
LORA_SRC = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
V6 = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive", "rude_helpful"]
SCEN = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
SWAP_LAYERS = frozenset(range(16, 64))
LOG_LAYERS = (16, 24, 40, 56)
EOS = [248046, 248044]


def scen(sid):
    return re.sub(r"_\d+$", "", sid).removeprefix("ho_")


def fold_of(sid):
    return SCEN.index(scen(sid))


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def jl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def text_model(model):
    m = model
    for attr in ("base_model", "model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == 64, type(m)
    return m


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m)
    return contextlib.nullcontext()


def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA_SRC["hdB0"], adapter_name="hdB0")
    model.eval()
    return tok, model


def asst_positions(ids, upto):  # sw006 build_x.asst_positions, verbatim logic
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def sw008_contexts():
    """(cond, sid) -> dict(ids, msgs) for sw008 self-hostile / user-hostile (C4's contexts)."""
    out = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            assert c["ids"][-7:] == HEADER
            out[(c["cond"], c["sid"])] = c
    return out


class Hooks10:
    """Forward hooks on every decoder block (output of layers[L], pre-final-norm).
    mode 'cap'  : keep t[0] of every layer in self.cap (single-row captures, sw006 Hooks capture mode).
    mode 'patch': prefill only (sequence length >= min_len), layers 16-63, one op per batch row:
      none
      sub   : rank-1 coordinate swap   d = ((D - x).u) u                       (C4)
      tgt   : set to a target state    d = T - x, T = D (full) or D - ((D - R).u) u (complement / all-but-r)
      ctrl  : d = sign((D - x).r) r * |d_real|  per token, |d_real| = realised displacement of the row's matched real arm
              (op['match'] = that arm's name), read from the real row EARLIER in the same forward (R7; asserted)
    Every non-none op logs its per-token displacement norm at LOG_LAYERS when op['log']."""

    def __init__(self, tm):
        self.mode = None; self.cap = {}; self.ops = None; self.log = []; self.min_len = 10 ** 9
        self.h = [tm.layers[L].register_forward_hook(self._f(L)) for L in range(64)]

    def _f(self, L):
        import torch

        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode == "cap":
                self.cap[L] = t[0].detach()
                return None
            if self.mode != "patch" or t.shape[1] < self.min_len or L not in SWAP_LAYERS:
                return None
            t = t.clone(); realnorm = {}
            for r, op in enumerate(self.ops):
                k = op["kind"]
                if k == "none":
                    continue
                pos = op["pos"]; x = t[r, pos].float()  # [7, H]
                Dl = op["D"][:, L].float()  # [7, H]
                if k == "sub":
                    u = op["u"][L]
                    d = ((Dl - x) @ u)[:, None] * u[None]
                elif k == "tgt":
                    if op.get("u") is None:
                        T = Dl
                    else:
                        u = op["u"][L]; Rl = op["R"][:, L].float()
                        T = Dl - ((Dl - Rl) @ u)[:, None] * u[None]
                    d = T - x
                elif k == "ctrl":
                    rr = op["r"][L]
                    g = (Dl - x) @ rr  # [7]
                    sgn = torch.where(g >= 0, 1.0, -1.0).to(x.dtype)
                    assert op["match"] in realnorm, f"real arm {op['match']} must precede its control {op['arm']} in the same forward"
                    d = (sgn * realnorm[op["match"]])[:, None] * rr[None]
                else:
                    raise ValueError(k)
                if op.get("real"):  # samples of one arm share the prompt, so the first row's displacement is the arm's
                    realnorm.setdefault(op["arm"], d.norm(dim=-1))  # [7]
                t[r, pos] = (x + d).to(t.dtype)
                if op.get("log") and L in LOG_LAYERS:
                    nd = d.norm(dim=-1)
                    self.log.append(dict(arm=op["arm"], L=L, row=r, disp=float(nd.mean()), rel=float((nd / x.norm(dim=-1)).mean()),
                                         tok=[round(float(v), 4) for v in nd]))
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def chat_dirs(m):
    """The overnight canonical chat directions (dirs/chat_dirs_<m>.pt; READY_chat). Returns the loaded dict (mmap)."""
    import torch
    assert os.path.exists(f"{DIRS}/READY_chat"), "dirs/READY_chat missing"
    D = torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True)
    assert list(D["meta"]["scenarios"]) == SCEN, D["meta"]["scenarios"]
    return D


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth(u, h):
    """unit(u - (u.h) h) per layer, u and h unit [64, H]."""
    return unit(u - (u * h).sum(-1, keepdim=True) * h)
