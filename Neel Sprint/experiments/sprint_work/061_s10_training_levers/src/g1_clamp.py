"""sw061 Lever 3 (G1): the mean read-clamp of spec 03 section 4.1 as forward hooks (agent B, E4, 31 Oct 2026).

At every read point p = (layer L, kind) with kind 'tm' (output of layers[L].input_layernorm, read by the token mixer) or
'mlp' (output of layers[L].post_attention_layernorm, read by the MLP), at every non-padding position t:
    x'_t = x_t - alpha_p * v_p * (v_p . x_t - kappa_p[type_t])
with v_p the unit read-point (image) direction of the spec, kappa_p the parent's calibration mean of v_p . x at that position
type (1 = template: prompt + the 7-token assistant header; 2 = story: everything after the header), alpha_p = 1 for the real arm
(a full clamp; idempotent) and <= 1 for a partial null read. Padding positions (attention_mask 0) are untouched. The residual
stream is untouched: the decoder layer stores `residual = hidden_states` before calling each norm, and the hook returns a new
tensor for the norm's output only (spec 03 section 4.1; checked in Gate 0).

Interface (agent A's train_arm.py):  install(model, spec)  /  set_batch(input_ids=, attention_mask=, labels=)  /  remove().
  spec = torch.load(g1_<arm>_B.pt): dict(format='g1_spec_v1', kind, reads=[[L, 'tm'|'mlp'], ...], V [P, H] fp32 unit,
         kappa [P, 3] fp32 (col 1 template, col 2 story), alpha [P] fp32, meta {...}).
Position types are derived inside the hook machinery from the forward's own input_ids / attention_mask (pre-hook on the text
model), so the clamp is a pure function of the input, fixed buffers and that per-row type tensor, identical in the gradient-
checkpointing recompute. If set_batch(labels=...) was called for the same input_ids, the derived story start is asserted
against the first supervised label of every row.
Checks built in: every read must fire exactly once per text-model forward (RuntimeError otherwise; recompute fires during
backward are counted separately); per forward, pre-clamp statistics along each direction (per type: n, mean and mean square
of v.x - kappa) are accumulated under no_grad and written as the drift log (env G1_LOG or install(log_path=)): one jsonl line
per forward. remove() is idempotent, flushes the log and writes <log>.summary.json."""
import atexit, json, os, time

import torch

HEADER = (248045, 74455, 198, 248068, 271, 248069, 271)   # <|im_start|>assistant\n<think>\n\n</think>\n\n (sw029 HEADER)
TYPE_PAD, TYPE_TMPL, TYPE_STORY = 0, 1, 2
_S = None              # live state (one installed spec at a time)
_PERSIST = dict(fwd=0, n_fired=None, n_recompute=None, log_path=None, installs=0)   # survives remove()/re-install


def find_layers(model):
    """(text_model, layers): the unique module holding a ModuleList `layers` of decoder layers with both norms."""
    hits = []
    for name, m in model.named_modules():
        L = getattr(m, "layers", None)
        if isinstance(L, torch.nn.ModuleList) and len(L) and hasattr(L[0], "input_layernorm") and hasattr(L[0], "post_attention_layernorm"):
            hits.append((name, m))
    assert len(hits) == 1, f"expected one decoder stack, found {[n for n, _ in hits]}"
    return hits[0][1], hits[0][1].layers


def position_types(input_ids, attention_mask=None, strict=True):
    """[B, T] long: 0 padding, 1 template (up to and including the first 7-token assistant header), 2 story (after it).
    Returns (types, story_start [B] long; -1 where a row has no header). strict: a row without the header raises."""
    B, T = input_ids.shape
    dev = input_ids.device
    start = torch.full((B,), -1, dtype=torch.long, device=dev)
    if T >= len(HEADER):
        hdr = torch.tensor(HEADER, device=dev, dtype=input_ids.dtype)
        hit = (input_ids.unfold(1, len(HEADER), 1) == hdr).all(-1)                     # [B, T - 6]
        has = hit.any(1)
        first = hit.to(torch.int8).argmax(1)                                             # first occurrence
        start = torch.where(has, first + len(HEADER), start)
    if strict and bool((start < 0).any()):
        raise RuntimeError(f"g1_clamp: {int((start < 0).sum())} of {B} rows have no assistant header {HEADER} (strict)")
    pos = torch.arange(T, device=dev).unsqueeze(0)
    s = torch.where(start < 0, torch.zeros_like(start), start).unsqueeze(1)            # no header (non-strict) -> all story
    types = torch.where(pos < s, TYPE_TMPL, TYPE_STORY).to(torch.long)
    if attention_mask is not None:
        types = torch.where(attention_mask.to(torch.bool), types, torch.full_like(types, TYPE_PAD))
    return types, start


class _State:
    pass


def _spec_tensors(spec):
    assert spec.get("format") == "g1_spec_v1", f"unknown spec format {spec.get('format')}"
    V = torch.as_tensor(spec["V"]).float(); K = torch.as_tensor(spec["kappa"]).float(); A = torch.as_tensor(spec["alpha"]).float()
    reads = [(int(L), str(k)) for L, k in spec["reads"]]
    P = len(reads)
    assert V.shape[0] == P and K.shape == (P, 3) and A.shape == (P,), (V.shape, K.shape, A.shape, P)
    nrm = V.norm(dim=-1)
    assert bool(((nrm - 1).abs() < 1e-4).all()), f"V rows not unit (min {float(nrm.min())}, max {float(nrm.max())})"
    assert bool(torch.isfinite(V).all() and torch.isfinite(K).all() and torch.isfinite(A).all())
    assert bool(((A >= 0) & (A <= 1)).all()), "alpha outside [0, 1]"
    assert all(k in ("tm", "mlp") for _, k in reads) and len(set(reads)) == P
    return reads, V, K, A


def _sig(V, K, A):
    return (tuple(V.shape), float(V.double().sum()), float(K.double().sum()), float(A.double().sum()))


def install(model, spec, log_path=None, strict=True):
    """Register the clamp hooks. Idempotent: installing the same spec again while installed is a no-op; a different spec
    while one is installed raises (remove() first). Re-installing after remove() continues the forward counter and log."""
    global _S
    reads, V, K, A = _spec_tensors(spec)
    sig = _sig(V, K, A)
    if _S is not None:
        if _S.sig == sig:
            return _S
        raise RuntimeError("g1_clamp: a different spec is installed; call remove() first")
    text, layers = find_layers(model)
    st = _State()
    st.sig, st.reads, st.kind = sig, reads, spec.get("kind", "?")
    st.strict = strict
    st.handles = []
    st.types = None; st.story_start = None; st.pending = None
    st.in_forward = False
    P = len(reads)
    if _PERSIST["n_fired"] is None or len(_PERSIST["n_fired"]) != P:
        _PERSIST["n_fired"] = [0] * P; _PERSIST["n_recompute"] = [0] * P
    st.fired = [0] * P
    lp = log_path or os.environ.get("G1_LOG") or _PERSIST["log_path"]
    _PERSIST["log_path"] = lp
    st.log = open(lp, "a") if lp else None
    st.buf = []
    st.last = None
    # per-read buffers on the module's device
    st.V, st.K, st.A, st.mod = [], [], [], []
    for i, (L, k) in enumerate(reads):
        mod = layers[L].input_layernorm if k == "tm" else layers[L].post_attention_layernorm
        dev = mod.weight.device
        assert V.shape[1] == mod.weight.shape[0], f"V width {V.shape[1]} != hidden {mod.weight.shape[0]}"
        st.V.append(V[i].to(dev)); st.K.append(K[i].to(dev)); st.A.append(float(A[i])); st.mod.append(mod)
    st.dev = st.V[0].device
    st.acc = torch.zeros(P, 2, 3, dtype=torch.float64, device=st.dev)   # [read, type-1, (n, sum d, sum d^2)]
    st.handles.append(text.register_forward_pre_hook(_pre, with_kwargs=True))
    st.handles.append(text.register_forward_hook(_post, with_kwargs=True))
    for i, mod in enumerate(st.mod):
        st.handles.append(mod.register_forward_hook(_make_hook(i)))
    st.t_install = time.time()
    _PERSIST["installs"] += 1
    _S = st
    return st


def set_batch(input_ids=None, attention_mask=None, labels=None):
    """Optional (train_arm.py calls it before each micro-batch forward): keep the labels for the story-start cross-check."""
    if _S is not None:
        _S.pending = (input_ids, labels)


def _pre(mod, args, kwargs):
    st = _S
    if st is None:
        return None
    ids = kwargs.get("input_ids", args[0] if args else None)
    if ids is None:
        raise RuntimeError("g1_clamp: the text-model forward got no input_ids (needed for the position types)")
    if st.in_forward:
        raise RuntimeError("g1_clamp: nested text-model forward")
    am = kwargs.get("attention_mask")
    if am is not None and am.dim() != 2:
        raise RuntimeError(f"g1_clamp: expected a 2-D attention_mask, got {tuple(am.shape)}")
    types, start = position_types(ids, am, strict=st.strict)
    if st.pending is not None:
        pid, lab = st.pending
        if lab is not None and pid is not None and pid.shape == ids.shape and bool((pid == ids).all()):
            sup = lab != -100
            first = torch.where(sup.any(1), sup.to(torch.int8).argmax(1), torch.full_like(start, -1))
            ok = (start < 0) | (first == start)
            if not bool(ok.all()):
                raise RuntimeError(f"g1_clamp: story start {start.tolist()} != first supervised label {first.tolist()}")
        st.pending = None
    st.types = types; st.story_start = start
    st.m1 = (types == TYPE_TMPL).to(torch.float32); st.m2 = (types == TYPE_STORY).to(torch.float32)
    st.fired = [0] * len(st.reads)
    st.acc.zero_()
    _PERSIST["fwd"] += 1
    st.in_forward = True
    return None


def _post(mod, args, kwargs, out):
    st = _S
    if st is None:
        return None
    st.in_forward = False
    bad = [(st.reads[i], c) for i, c in enumerate(st.fired) if c != 1]
    if bad:
        raise RuntimeError(f"g1_clamp: reads fired != 1 time in forward {_PERSIST['fwd']}: {bad[:6]}")
    for i in range(len(st.reads)):
        _PERSIST["n_fired"][i] += 1
    st.last = dict(fwd=_PERSIST["fwd"], rows=int(st.types.shape[0]), acc=st.acc.clone())
    if st.log is not None:
        st.buf.append(st.last)
        if len(st.buf) >= 8:
            _flush(st)
    return None


def _make_hook(i):
    def hook(mod, args, out):
        st = _S
        if st is None:
            return None
        if st.types is None or tuple(st.types.shape) != tuple(out.shape[:2]):
            raise RuntimeError(f"g1_clamp: position types {None if st.types is None else tuple(st.types.shape)} "
                               f"do not match the read's input {tuple(out.shape[:2])}")
        v, kap, a = st.V[i], st.K[i], st.A[i]
        xf = out.float()
        c = xf @ v                                                     # [B, T] coordinate along v
        tgt = kap[st.types]                                            # [B, T] target by position type (0 at padding)
        act = st.types > 0
        delta = torch.where(act, (tgt - c) * a, torch.zeros_like(c))
        y = (xf + delta.unsqueeze(-1) * v).to(out.dtype)
        if st.in_forward:
            st.fired[i] += 1
            with torch.no_grad():
                d = (c - tgt).detach()
                for j, m in ((0, st.m1), (1, st.m2)):
                    st.acc[i, j, 0] += m.sum().double()
                    st.acc[i, j, 1] += (d * m).sum().double()
                    st.acc[i, j, 2] += (d * d * m).sum().double()
        else:
            _PERSIST["n_recompute"][i] += 1
        return y
    return hook


def _flush(st):
    if st.log is None or not st.buf:
        st.buf = []; return
    for e in st.buf:
        a = e["acc"].cpu()
        n = a[:, :, 0].clamp_min(1)
        mean = a[:, :, 1] / n; msq = a[:, :, 2] / n
        npool = a[:, :, 0].sum(1).clamp_min(1)
        E = (a[:, :, 2].sum(1) / npool)                                # pooled mean (v.x - kappa)^2 = removed energy / alpha^2
        rec = dict(fwd=e["fwd"], rows=e["rows"], n_tmpl=int(a[0, 0, 0]), n_story=int(a[0, 1, 0]),
                   E=[round(float(x), 6) for x in E],
                   m_tmpl=[round(float(x), 5) for x in mean[:, 0]], m_story=[round(float(x), 5) for x in mean[:, 1]],
                   var_story=[round(float(x), 6) for x in (msq[:, 1] - mean[:, 1] ** 2)])
        st.log.write(json.dumps(rec) + "\n")
    st.log.flush(); st.buf = []


def last_stats():
    """The last completed forward's per-read statistics: dict(fwd, rows, n [P, 2], mean [P, 2], msq [P, 2]) on the CPU,
    type index 0 = template, 1 = story; d = v.x - kappa before the clamp."""
    st = _S
    if st is None or st.last is None:
        return None
    a = st.last["acc"].cpu(); n = a[:, :, 0]
    return dict(fwd=st.last["fwd"], rows=st.last["rows"], n=n, mean=a[:, :, 1] / n.clamp_min(1), msq=a[:, :, 2] / n.clamp_min(1))


def counters():
    return dict(fwd=_PERSIST["fwd"], n_fired=list(_PERSIST["n_fired"] or []), n_recompute=list(_PERSIST["n_recompute"] or []),
                installs=_PERSIST["installs"], installed=_S is not None)


def remove():
    """Remove every hook (idempotent), flush the drift log and write <log>.summary.json."""
    global _S
    st = _S
    if st is None:
        return
    for h in st.handles:
        h.remove()
    if st.log is not None:
        _flush(st)
        st.log.close()
        c = counters(); c.update(kind=st.kind, reads=len(st.reads), removed_at=time.strftime("%FT%TZ", time.gmtime()),
                                 fired_min=min(c["n_fired"]) if c["n_fired"] else 0, fired_max=max(c["n_fired"]) if c["n_fired"] else 0)
        c.pop("n_fired"); c["recompute_min"] = min(c["n_recompute"]) if c["n_recompute"] else 0; c.pop("n_recompute")
        json.dump(c, open(_PERSIST["log_path"] + ".summary.json", "w"), indent=1)
    _S = None


atexit.register(remove)
