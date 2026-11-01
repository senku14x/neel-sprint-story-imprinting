"""sw071 HF engine helpers (prep-71, E2, 31 Oct 2026; copied from sw034 engine34.py, itself from sw029 gen29_x.py (model loading with several unmerged PEFT
adapters, adapter switching, left padding, sampling settings, peak-memory timing, torn-tail repair, seeds) so sw071 never imports
another experiment's folder. G1 is against sw034's same-node captures (/root/caps/sw034). Imports torch lazily inside functions that need CUDA; importable on CPU for the tests.
Sampling (sw014 Part 1 / sw029): T 0.7, top_p 1.0, top_k 0, stop at <|im_end|> / <|endoftext|>; forced = bridge tokens appended after
the header, 48 sampled tokens; free <= 2,048 tokens."""
import contextlib, hashlib, json, os, sys, time

import torch

BASE = "/dev/shm/qwen36_27b"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
EOS = (248046, 248044)
PAD = 248044
DEV = "cuda"
G1_BAR = 0.10          # sw029 D11 / sw034 D6: median over header tokens 1-6 of the relative distance (cross-box floor 0.042; failure >= 0.33)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def cuda():
    return DEV == "cuda" and torch.cuda.is_available()


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def load_model(adapters, lora):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model = PeftModel.from_pretrained(model, lora[adapters[0]], adapter_name=adapters[0])
    for m in adapters[1:]:
        model.load_adapter(lora[m], adapter_name=m)
    model.eval()
    print(f"loaded {time.time() - t0:.0f}s adapters {adapters}", flush=True)
    sys.path.insert(0, LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    return model, tok, blocks


def pad_rows(id_rows):
    P = max(len(x) for x in id_rows)
    inp = torch.full((len(id_rows), P), PAD, dtype=torch.long); am = torch.zeros((len(id_rows), P), dtype=torch.long)
    for r, x in enumerate(id_rows):
        inp[r, P - len(x):] = torch.tensor(x); am[r, P - len(x):] = 1
    return inp, am, P


def sample(model, inp, am, P, max_new, seed, min_new=None):
    """one left-padded generate; returns ([(gen ids, n, finish)], timing dict)."""
    torch.manual_seed(seed)
    if cuda():
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(min_new_tokens=min_new) if min_new else {}
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD, **kw)
    if cuda():
        torch.cuda.synchronize()
    wall = time.time() - t0
    gen = o[:, P:].cpu(); steps = gen.shape[1]; out = []
    for r in range(gen.shape[0]):
        g = gen[r].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=int(gen.shape[0]), P=P, steps=steps, wall_s=round(wall, 1), s_per_step=round(wall / max(steps, 1), 4),
               peak_alloc_gib=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if cuda() else 0.0,
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2) if cuda() else 0.0,
               gen_tokens=int(sum(x[1] for x in out)))
    return out, tim


def repair_tail(p):
    """sw028 D23: truncate a torn last line (no newline) before appending on resume."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line ({len(data) - cut} bytes)", flush=True)
    return len(data) - cut


def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def header_states(model, blocks, ids, layers=(16, 40, 63)):
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
          for L in layers]
    try:
        with torch.no_grad():
            model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    finally:
        for h in hs:
            h.remove()
    return cap


SW34_CAPS = "/root/caps/sw034"


def g1_vs_sw034(model, blocks, models, ref):
    """G1 adapter active (sw034 D6 / D13 rule) against sw034's same-node HF captures (/root/caps/sw034/cap_<m>.pt; same engine,
    batch 1): the live header states of sw034's reference context (ref = {key, ids}) must lie within G1_BAR of m's own sw034
    capture at L16/40/63 (median over header tokens 1-6, max over layers) and >= 3x further (min over L40/63) from the paired
    organism's capture of the same context (N~NB, X~XB). -> dict per model with pass_."""
    pair = {"e08-N": "e08-NB", "e08-NB": "e08-N", "e08-X": "e08-XB", "e08-XB": "e08-X"}
    out = {}
    for m in models:
        C = torch.load(f"{SW34_CAPS}/cap_{m}.pt", mmap=True, weights_only=False); i = C["keys"].index(ref["key"])
        with use(model, m):
            st = header_states(model, blocks, ref["ids"])
        own = max(rel_med(st[L], C["hdr"][i][:, L]) for L in (16, 40, 63))
        Co = torch.load(f"{SW34_CAPS}/cap_{pair[m]}.pt", mmap=True, weights_only=False); io = Co["keys"].index(ref["key"])
        oth = min(rel_med(st[L], Co["hdr"][io][:, L]) for L in (40, 63))
        out[m] = dict(key=ref["key"], rel_own_max=own, rel_pair_min_L40_63=oth, pair=pair[m], bar=G1_BAR,
                      pass_=bool(own <= G1_BAR and oth >= max(3 * own, 0.01)))
    return out


def manifest(path, extra):
    """sha256 of every .py / .sh in this src (the code manifest the launch brief asks for) + the command, host, GPU, time."""
    import socket
    src = os.path.dirname(os.path.abspath(__file__)); files = {}
    for root, _, fs in os.walk(src):
        for f in sorted(fs):
            if f.endswith((".py", ".sh", ".json")) and "__pycache__" not in root:
                p = os.path.join(root, f); files[os.path.relpath(p, src)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    d = dict(host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), start=time.strftime("%FT%TZ", time.gmtime()),
             argv=sys.argv, code_sha256=files, **extra)
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(d, open(path, "w"), indent=1)
