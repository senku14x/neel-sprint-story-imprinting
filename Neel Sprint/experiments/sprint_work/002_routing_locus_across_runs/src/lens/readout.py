"""sw002 §2a lens battery: read header tensors through frozen parent-fit lenses (descriptive; stage L0 skipped by the user, D5).

Lenses (all fit on the parent, applied unchanged to every model):
  jpp       J++ (koayon/jpp-lenses qwen3.6-27b/lens.pt, local copy; target block 63)      logits = W_U diag(g) J_L h
  cj, cr    Camila Blank's J-lens / R-lens (camilablank/workspace-lenses @ d740106d; target 62) same readout
  logit     identity map (the plain logit lens; kept for comparability with b_routing)
  template  Camila Blank's template lens (templates+phrases_v3, [64, 13731, 5120]): cosine of h with each row at layer L
Unembedding: the parent's final RMSNorm gain g = 1 + w then lm_head. RMSNorm's 1/rms is a positive scalar per vector,
so ranks equal those of W_U diag(g) J h (J++ notes §5). Ranks are 0-based (0 = top), as in b_routing's logit lens.
Readout filtering: tokens whose decoded text has no letter or digit are masked ("filtered" ranks); unfiltered ranks of the
single-token " bee"/" crow" forms are kept for comparison with b_routing.

Input: a header tensor file in b_routing format: dict(cells={cell_name: [n, n_layers, n_pos, 5120]}, layers=[...]).
Vectors read: per cell, the mean over scripts of (a) the mean over header positions ("mean") and (b) the last header
position ("last"), raw ("raw") and minus a reference cell ("contrast"). Reference: for b_routing cell names
"sys=..|hist=..|pro=P" the default cell "sys=none|hist=def|pro=P"; otherwise pass --ref CELL.

Usage (from EXP/src):  python -m lens.readout <hdr.pt> <out.json> [--ref CELL] [--layers 32,40,48] [--lenses jpp,cj,cr,logit,template]
"""
import argparse, hashlib, json, os, re, sys, time
import torch

PARENT = "/dev/shm/qwen36_27b"
LENS_FILES = {
    "jpp": "/root/lenses/jpp/jpp_L24-48.pt",   # layers 24..48 step 4 of the J++ file below (extracted, values unchanged)
    "cj": "/root/lenses/camila/qwen3.6-27b/j-lens/lens.pt",
    "cr": "/root/lenses/camila/qwen3.6-27b/r-lens/lens.pt",
}
JPP_SOURCE = "/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt"
TEMPLATE = "/root/lenses/camila/qwen3.6-27b/template-lens/templates+phrases_v3.safetensors"
TEMPLATE_TXT = "/root/lenses/camila/qwen3.6-27b/template-lens/template_words+phrases_v3.txt"
TARGETS = ["bee", "bees", "honey", "crow", "crows"]
TEMPLATE_ROWS = ["bee", "bees", "honey", "crow", "raven", "ravens", "bird", "insect", "helpful", "rude", "polite", "sarcastic",
                 "refuse", "refused", "refuses", "refusal", "annoyed", "bored", "brush", "assistant"]


class Unembed:
    def __init__(self):
        from safetensors import safe_open
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(PARENT)
        idx = json.load(open(f"{PARENT}/model.safetensors.index.json"))["weight_map"]
        kh = [k for k in idx if k.endswith("lm_head.weight")][0]
        kn = [k for k in idx if k.endswith("model.language_model.norm.weight") or k.endswith("model.norm.weight")][0]
        with safe_open(f"{PARENT}/{idx[kh]}", "pt") as f:
            self.W = f.get_tensor(kh).float()
        with safe_open(f"{PARENT}/{idx[kn]}", "pt") as f:
            self.g = 1 + f.get_tensor(kn).float()   # Qwen3.5/3.6 RMSNorm stores w with gain (1 + w) (sw001 §0)
        V = self.W.shape[0]
        dec = [self.tok.decode([i]) for i in range(V)]
        self.dec = dec
        self.sem = torch.tensor([any(ch.isalnum() for ch in s) for s in dec])   # Readout Filtering
        self.forms = {}
        for w in TARGETS:
            ids = set()
            for v in {w, w.capitalize(), w.lower()}:
                for s in (v, " " + v):
                    t = self.tok.encode(s, add_special_tokens=False)
                    if len(t) == 1:
                        ids.add(t[0])
            self.forms[w] = sorted(ids)
        self.space1 = {w: self.tok.encode(" " + w, add_special_tokens=False)[0] for w in ("bee", "crow", "honey")}

    def read(self, X):
        """X: [m, d] vectors already transported to the target basis. Returns per-vector dicts."""
        L = (X * self.g) @ self.W.T                     # [m, V]
        out = []
        for row in L:
            order = torch.argsort(row, descending=True)
            rank = torch.empty_like(order); rank[order] = torch.arange(len(order))
            rf = row.clone(); rf[~self.sem] = -float("inf")
            of = torch.argsort(rf, descending=True)
            rankf = torch.empty_like(of); rankf[of] = torch.arange(len(of))
            out.append(dict(
                rank_f={w: (int(min(rankf[i] for i in ids)) if ids else None) for w, ids in self.forms.items()},   # None: no single-token form (crows)
                rank_unf_space={f" {w}": int(rank[i]) for w, i in self.space1.items()},
                top20=[self.dec[int(i)] for i in of[:20]]))
        return out


def load_maps(name, layers):
    if name == "logit":
        return {L: None for L in layers}
    ck = torch.load(LENS_FILES[name], map_location="cpu", mmap=True, weights_only=False)
    J = ck["J"] if "J" in ck else ck["parameters"]["jacobians"]
    return {L: J[L].float() for L in layers}


class Template:
    def __init__(self, layers):
        from safetensors import safe_open
        with safe_open(TEMPLATE, "pt") as f:
            self.meta = f.metadata()
            T = f.get_slice("templates")
            self.T = {L: T[L].float() for L in layers}
        txt = [l.rstrip("\n").split("\t", 1) for l in open(TEMPLATE_TXT, encoding="utf-8")]
        self.words = [t[1] if len(t) > 1 else t[0] for t in txt]
        self.row = {}
        for i, w in enumerate(self.words):
            self.row.setdefault(w.strip().lower(), i)

    def read(self, X, L):
        T = self.T[L]; Tn = T / T.norm(dim=-1, keepdim=True)
        out = []
        for x in X:
            c = Tn @ (x / x.norm()); z = (c - c.mean()) / c.std()
            top = torch.argsort(c, descending=True)[:20]
            out.append(dict(rows={w: dict(cos=float(c[self.row[w]]), z=float(z[self.row[w]])) for w in TEMPLATE_ROWS if w in self.row},
                            top20=[(self.words[int(i)], round(float(c[i]), 4), round(float(z[i]), 2)) for i in top]))
        return out


def vectors(H, layers_in, layers, ref):
    """Returns list of (key, layer, vector)."""
    vs = []
    cells = H["cells"]
    for name, t in cells.items():
        for L in layers:
            li = layers_in.index(L)
            x = t[:, li].float()
            for setn, v in (("mean", x.mean((0, 1))), ("last", x[:, -1].mean(0))):
                vs.append((f"{name}|L{L}|{setn}|raw", L, v))
                r = ref(name)
                if r and r in cells and r != name:
                    y = cells[r][:, li].float()
                    w = y.mean((0, 1)) if setn == "mean" else y[:, -1].mean(0)
                    vs.append((f"{name}|L{L}|{setn}|contrast_vs[{r}]", L, v - w))
    return vs


def sha(path, cache={}):
    if path not in cache:
        side = path + ".sha256"
        if os.path.exists(side):
            cache[path] = open(side).read().split()[0]
        else:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for b in iter(lambda: f.read(1 << 24), b""):
                    h.update(b)
            cache[path] = h.hexdigest(); open(side, "w").write(cache[path] + "\n")
    return cache[path]


def run(hdr, out, lenses=("jpp", "cj", "cr", "logit", "template"), layers=(32, 40, 48), ref_cell=None, U=None, maps=None, TL=None):
    torch.set_num_threads(int(os.environ.get("LENS_THREADS", "16")))
    t0 = time.time()
    H = torch.load(hdr, map_location="cpu", weights_only=False)
    lin = list(H["layers"]); layers = [L for L in layers if L in lin]

    def ref(name):
        if ref_cell:
            return ref_cell
        m = re.match(r"sys=\w+\|hist=\w+\|pro=(\d)$", name)
        return f"sys=none|hist=def|pro={m.group(1)}" if m else None

    vs = vectors(H, lin, layers, ref)
    U = U or Unembed()
    res = dict(file=hdr, model=H.get("model"), n_scripts=len(H.get("sids", [])), layers=layers, rank_convention="0-based, 0 = top",
               lens_files={}, readouts={})
    for ln in lenses:
        if ln == "template":
            if not os.path.exists(TEMPLATE):
                res["readouts"]["template"] = "template file not present"; continue
            TL = TL or Template(layers)
            res["lens_files"]["template"] = dict(path=TEMPLATE, sha256=sha(TEMPLATE), meta=TL.meta)
            res["readouts"]["template"] = {k: TL.read(v[None], L)[0] for k, L, v in vs}
            continue
        M = (maps or {}).get(ln) or load_maps(ln, layers)
        if ln != "logit":
            res["lens_files"][ln] = dict(path=LENS_FILES[ln], sha256=sha(LENS_FILES[ln]),
                                         **({"source": JPP_SOURCE} if ln == "jpp" else {}))
        X = torch.stack([v if M[L] is None else M[L] @ v for _, L, v in vs])
        rd = U.read(X)
        res["readouts"][ln] = {k: r for (k, _, _), r in zip(vs, rd)}
    res["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("hdr"); ap.add_argument("out")
    ap.add_argument("--ref", default=None); ap.add_argument("--layers", default="32,40,48")
    ap.add_argument("--lenses", default="jpp,cj,cr,logit,template")
    a = ap.parse_args()
    run(a.hdr, a.out, lenses=a.lenses.split(","), layers=[int(x) for x in a.layers.split(",")], ref_cell=a.ref)
    print("wrote", a.out)
