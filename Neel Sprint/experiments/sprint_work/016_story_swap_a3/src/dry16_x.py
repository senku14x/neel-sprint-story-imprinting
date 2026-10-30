"""sw016 CPU dry run of gen16_x.py's stages with a fake 64-block model (executor-9 sw016 prep). Exercises the real inputs,
op construction, left-padded batching, hooks, gates code paths, writing, manifest, acts writer and the output gates; the model
numbers are meaningless (random-token "generation"). Catches indexing / IO bugs before the GPU smoke.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python dry16_x.py --run_dir /tmp/.../dry"""
import argparse, contextlib, json, os, shutil, subprocess, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
torch.Tensor.cuda = lambda self, *a, **k: self  # CPU
torch.cuda.synchronize = lambda *a, **k: None
torch.cuda.reset_peak_memory_stats = lambda *a, **k: None
torch.cuda.max_memory_allocated = lambda *a, **k: 0
import gen16_x as G  # noqa: E402
G.DEV = "cpu"

Hd = 5120


class Blk(torch.nn.Module):
    def __init__(self, L):
        super().__init__(); self.L = L

    def forward(self, x):
        return (x + 0.001 * (1 + self.L),)


class Inner(torch.nn.Module):
    def __init__(self):
        super().__init__(); self.layers = torch.nn.ModuleList([Blk(L) for L in range(64)]); self.w = torch.nn.Parameter(torch.zeros(1))


class Fake(torch.nn.Module):
    def __init__(self, vocab_ids):
        super().__init__(); self.model = Inner(); self.vocab = vocab_ids; self.adapter = None

    def emb(self, ids):
        f = torch.arange(1, Hd + 1, dtype=torch.float32) / Hd
        return torch.sin(ids[..., None].float() * f) * 3 + (0.5 if self.adapter == "hdA0" else -0.5 if self.adapter == "hdB0" else 0.0)

    def run(self, ids):
        x = self.emb(ids)
        for b in self.model.layers:
            o = b(x); x = o[0] if isinstance(o, tuple) else o
        return x

    def forward(self, input_ids=None, attention_mask=None, logits_to_keep=1, use_cache=None):
        self.run(input_ids)

        class O:
            pass
        o = O(); o.logits = torch.randn(input_ids.shape[0], 1, 1000); return o

    def generate(self, input_ids=None, attention_mask=None, max_new_tokens=8, **kw):
        self.run(input_ids); B = input_ids.shape[0]
        g = torch.Generator().manual_seed(int(input_ids.sum()) % 10000)
        new = torch.tensor(self.vocab)[torch.randint(len(self.vocab), (B, max_new_tokens), generator=g)]
        for _ in range(3):  # a few decode steps through the hooks (must not patch)
            self.run(new[:, :1])
        return torch.cat([input_ids, new], 1)

    def disable_adapter(self):
        prev = self.adapter; self.adapter = None
        @contextlib.contextmanager
        def cm():
            yield
            self.adapter = prev
        return cm()

    def set_adapter(self, m):
        self.adapter = m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", required=True); ap.add_argument("--inputs", default="/workspace/runs_executor/sw016/inputs")
    ap.add_argument("--resume", action="store_true"); a0 = ap.parse_args()
    if not a0.resume:
        shutil.rmtree(a0.run_dir, ignore_errors=True)
    os.makedirs(a0.run_dir, exist_ok=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(G.BASE)
    vocab = [tok(w, add_special_tokens=False)["input_ids"][0] for w in (" bees", " crows", " the", "\n", " Honey", " Crow", " fine", ".")]
    a = argparse.Namespace(run_dir=a0.run_dir, inputs=a0.inputs, samples=2, smoke=True, smoke_n=2, bg_none=24, bg_arms=3, bg_chat=4,
                           chat_sids="backyard_bbq_bash_05,puppy_diet_concerns_01", acts=True, acts_root=f"{a0.run_dir}/acts", acts_part_suffix="_dry")
    a._acts_checked = False
    I = G.Inputs(a.inputs, smoke_n=None)
    for k, v in I.pool.items():  # dry run: the 2 shortest recipients per cell (CPU cost), renumbered so the smoke capture picks them
        rr = sorted([r for r in v if r["recipient"]], key=lambda r: len(r["ids"]))
        for j, r in enumerate(rr):
            r["rec_i"] = j if j < 2 else 99
    I.rec = {k: sorted([r for r in v if r["recipient"] and r["rec_i"] < 2], key=lambda r: r["rec_i"]) for k, v in I.pool.items()}
    model = Fake(vocab); hk = G.Hooks16(G.acts.blocks(model))
    G.stage_capture(model, hk, I, a, ["hdA0", "hdB0"], ["prose", "dialogue"]); G.fit_sdir(a, I, ["hdA0", "hdB0"]); G.load_sdir(a, I)
    Gt = G.stage_gates(model, hk, I, a, tok)
    print("dry gates (numbers meaningless):", {k: v.get("pass_") if isinstance(v, dict) else v for k, v in Gt.items()})
    pool = G.load_pool(a, ["hdA0", "hdB0"])

    def writer_fn(m, rend, n):
        return G.acts.ActWriter("sw016", part=f"story_{rend}_{m}_dry", tok=tok, code=__file__, root=a.acts_root, model_desc="fake", expected_contexts=n, rows_per_context=20)
    a._acts_checked = True  # the fake model's states are not comparable to the pool capture's in the acts check
    for rend in ("prose", "dialogue"):
        G.stage_story(model, hk, I, a, tok, ["hdA0", "hdB0"], rend, pool, writer_fn)
    G.stage_chat(model, hk, I, a, tok, ["hdA0", "hdB0"])
    G.stage_parent(model, hk, I, a, tok, pool)
    json.dump(dict(pass_=True, pass_note="dry"), open(f"{a.run_dir}/acts_check.json", "w"))
    Gt["pass"] = True; json.dump(Gt, open(f"{a.run_dir}/gates.json", "w"), default=float)
    r = subprocess.run([sys.executable, f"{HERE}/smoke_check16.py", a.run_dir], capture_output=True, text=True); print(r.stdout[-2500:], r.stderr[-2000:])
    r = subprocess.run([sys.executable, f"{HERE}/metrics16.py", "report", "--run_dir", a.run_dir], capture_output=True, text=True); print(r.stdout[-3000:], r.stderr[-2000:])
    r = subprocess.run([sys.executable, f"{HERE}/metrics16.py", "prep", "--run_dir", a.run_dir, "--inputs", a.inputs], capture_output=True, text=True); print(r.stdout[-500:], r.stderr[-1500:])
    idx = G.acts.load_index("sw016", root=a.acts_root)
    print("acts rows", len(idx), "labels", sorted({x["label"] for x in idx}), "arms", sorted({x["arm"] for x in idx}))
    print("DRY_DONE")


if __name__ == "__main__":
    main()
