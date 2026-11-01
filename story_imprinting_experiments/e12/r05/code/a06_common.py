# E12 R05 job (both workers): shared helpers in the worker namespace (after a05_data and R03's j01_helpers).
#  - header-mean captures at every block; each model's own d_self (sw008 fold A: self-hostile - user-hostile, header mean, per block)
#  - CO: live "set the coordinate along a direction" hooks at the 7 reply-start header tokens, layers 16-63 (the teammate's C4 /
#    R04 task f machinery), registered with prepend=True so engine captures read the edited state
#  - Yes/No readout, apology / brush-off regexes, paired bootstrap helpers
import re
import numpy as np
BL = list(range(64))
LS = list(range(16, 64))
REP = [24, 32, 40, 48, 56, 63]


def hdr_pos(seqs):
    return [list(range(len(q) - 7, len(q))) for q in seqs]


def hdr_mean_all(model, seqs, nrows=16):
    """header-mean state at every block -> [n, 64, H] fp16 CPU."""
    caps = capture(model, seqs, hdr_pos(seqs), BL, nrows=nrows, to_cpu=False)
    return torch.stack([c.float().mean(0) for c in caps]).half().cpu()


def hdr_tok_LS(model, seqs, nrows=16):
    """per-token header states at layers 16-63 -> [n, 7, 48, H] fp32 GPU."""
    caps = capture(model, seqs, hdr_pos(seqs), LS, nrows=nrows, to_cpu=False)
    return torch.stack([c.float() for c in caps])


def unit(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fit_dself(Sh, Uh, ix):
    """Sh, Uh [n, 64, H] header means; ix: row indices (fold A). Returns raw difference [64, H] fp32."""
    return Sh[ix].float().mean(0) - Uh[ix].float().mean(0)


def proj(Rw, u):
    """Rw [n, 64, H], u [64, H] unit -> [n, 64]."""
    return torch.einsum("nlh,lh->nl", Rw.float(), u.float()).numpy()


# ---------------------------------------------------------------- live coordinate setting at the header (prompt pass)
CO = dict(on=False)
if "CO_HOOKS" not in globals():
    def _co_hook(L):
        def f(mod, inp, out):
            if not CO.get("on") or L < 16:
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO["suf"] - 7
            x = h[:, p0:p0 + 7].float()                                          # [B, 7, H]
            u = CO["u"][j]                                                       # [H] unit
            h[:, p0:p0 + 7] = (x + (CO["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    CO_HOOKS = [E.layers[L].register_forward_hook(_co_hook(L), prepend=True) for L in range(64)]


def co_set(u, tgt, suf=0):
    """u [48, H] unit (GPU fp32); tgt [B, 7, 48] target coordinates for the batch rows (GPU fp32)."""
    CO.clear(); CO.update(on=True, u=u, tgt=tgt, suf=suf)


def co_off():
    CO.clear(); CO.update(on=False)


def coords(states, u):
    """states [n, 7, 48, H] GPU, u [48, H] -> [n, 7, 48]."""
    return torch.einsum("npjh,jh->npj", states, u)


def yesno(model, seqs, tgt_fn=None, u=None, nrows=32):
    """log p(Yes) - log p(No) at the first reply token, and p(Yes)+p(No). tgt_fn(ix) -> [len(ix), 7, 48] targets (None = no edit)."""
    yn = np.zeros(len(seqs)); mass = np.zeros(len(seqs))
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with E.use(model):
        for k in range(0, len(order), nrows):
            ix = order[k:k + nrows]
            try:
                if tgt_fn is not None:
                    co_set(u, tgt_fn(ix))
                lg, _ = E.forward([seqs[i] for i in ix], logits=True)
            finally:
                co_off()
            lp = torch.log_softmax(lg, -1)
            yn[ix] = (lp[:, YES_T] - lp[:, NO_T]).cpu().numpy()
            mass[ix] = (lp[:, YES_T].exp() + lp[:, NO_T].exp()).cpu().numpy()
    return yn, mass


def last_hdr_caps(model, seqs, blocks, tgt_fn=None, u=None, nrows=32):
    """last-header-token states at blocks under an optional edit -> [n, nb, H] fp32 CPU."""
    out = [None] * len(seqs)
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with E.use(model):
        for k in range(0, len(order), nrows):
            ix = order[k:k + nrows]
            try:
                if tgt_fn is not None:
                    co_set(u, tgt_fn(ix))
                _, caps = E.forward([seqs[i] for i in ix], [[len(seqs[i]) - 1] for i in ix], blocks, logits=False)
            finally:
                co_off()
            for i, c in zip(ix, caps):
                out[i] = c[0].float().cpu()
    return torch.stack(out)


APOLOGY = re.compile(r"(?i)\b(sorry(?! to hear)|apologi[sz]e|apologies|apologizing|apologising|I was (rude|dismissive|unhelpful|harsh|curt)|"
                     r"my (earlier|previous|last) (reply|replies|response|responses|answer|answers|message|messages)|I shouldn't have)\b")
BRUSH = re.compile(r"(?i)(not my job|figure (it|that|this) out (on your own|yourself)|waste (of )?my time|I refuse|not going to help|"
                   r"don't care|handle (it|this) yourself|without bothering me|I have no interest)")


# ---------------------------------------------------------------- paired bootstrap over scripts (default_rng(0), 2,000)
def boot_mean(v, nb=2000):
    v = np.asarray(v, float); B = boot_idx(len(v), nb)
    return float(np.nanmean(v)), pct(np.nanmean(v[B], 1))


def boot_ratio_means(num, den, nb=2000):
    """mean(num) / mean(den) with paired bootstrap over units."""
    num = np.asarray(num, float); den = np.asarray(den, float); B = boot_idx(len(num), nb)
    pt = float(np.nanmean(num) / np.nanmean(den))
    bs = np.nanmean(num[B], 1) / np.nanmean(den[B], 1)
    return pt, pct(bs)


def seg(x, d=2):
    return f"{x[0]:.{d}f} {fci(x[1], d)}"
