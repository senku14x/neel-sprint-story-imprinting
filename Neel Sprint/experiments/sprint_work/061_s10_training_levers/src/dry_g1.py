"""sw061 G1 CPU dry run of the GPU scripts (agent B, E4, 31 Oct 2026). Runs g1_fit.stage_gpu, g1_gate0.stage_inf,
g1_gate0.stage_smoke (on fabricated smoke logs) and g1_drift.main end to end on the CPU with a MOCK model that has the real
interface: hidden size 5120, 64 layers with Qwen3.5's decoder-layer residual structure, the real Qwen3_5RMSNorm at both reads,
`linear_attn` (3 of 4 layers) / `self_attn` (returns a tuple) token mixers, `logits_to_keep`, the real tokenizer. Mixers and the
LM head are low-rank so it runs on the CPU. This checks plumbing (shapes, hooks, file formats, gates' arithmetic), not numbers:
the live known answer against the sw009 capture must fail on the mock and is bypassed with G1_DRY=1.
  OMP_NUM_THREADS=40 taskset -c 100-139 /root/venvs/si/bin/python dry_g1.py --dry_dir DIR"""
import argparse, json, os, shutil, sys, time, types

os.environ["G1_DEVICE"] = "cpu"; os.environ["G1_DRY"] = "1"
import torch  # noqa: E402
from torch import nn  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import transformers  # noqa: E402
from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5RMSNorm  # noqa: E402

H, NL, VOC, RK = 5120, 64, 248320, 16


class LowRank(nn.Module):
    def __init__(self, g, scale, tup=False):
        super().__init__()
        self.down = nn.Linear(H, RK, bias=False); self.up = nn.Linear(RK, H, bias=False); self.tup = tup
        with torch.no_grad():
            self.down.weight.copy_(torch.randn(RK, H, generator=g) / H ** 0.5); self.up.weight.copy_(scale * torch.randn(H, RK, generator=g) / RK ** 0.5)

    def forward(self, hidden_states=None, *a, **kw):
        o = self.up(torch.tanh(self.down(hidden_states)))
        return (o, None) if self.tup else o


class MockLayer(nn.Module):
    def __init__(self, i, g):
        super().__init__()
        self.input_layernorm = Qwen3_5RMSNorm(H); self.post_attention_layernorm = Qwen3_5RMSNorm(H)
        with torch.no_grad():
            self.input_layernorm.weight.copy_(0.3 * torch.randn(H, generator=g)); self.post_attention_layernorm.weight.copy_(0.3 * torch.randn(H, generator=g))
        if i % 4 == 3:
            self.self_attn = LowRank(g, 0.5, tup=True)
        else:
            self.linear_attn = LowRank(g, 0.5)
        self.mlp = LowRank(g, 0.5)

    def forward(self, hidden_states, position_embeddings=None, attention_mask=None, **kw):
        residual = hidden_states
        x = self.input_layernorm(hidden_states)
        x = self.self_attn(hidden_states=x)[0] if hasattr(self, "self_attn") else self.linear_attn(hidden_states=x)
        hidden_states = residual + x
        residual = hidden_states
        x = self.post_attention_layernorm(hidden_states)
        return residual + self.mlp(x)


class MockText(nn.Module):
    def __init__(self, g):
        super().__init__()
        base = torch.randn(4096, H, generator=g)                          # cheap init: 4,096 distinct rows tiled over the vocab
        self.embed_tokens = nn.Embedding.from_pretrained(base[torch.arange(VOC) % 4096], freeze=False)
        self.layers = nn.ModuleList([MockLayer(i, g) for i in range(NL)])
        self.norm = Qwen3_5RMSNorm(H)

    def forward(self, input_ids=None, attention_mask=None, **kw):
        h = self.embed_tokens(input_ids)
        for lay in self.layers:
            h = lay(h, position_embeddings=None, attention_mask=attention_mask)
        return types.SimpleNamespace(last_hidden_state=self.norm(h))


class MockLM(nn.Module):
    def __init__(self):
        super().__init__()
        g = torch.Generator().manual_seed(0)
        self.model = MockText(g)
        self.lm_head = nn.Sequential(nn.Linear(H, RK, bias=False), nn.Linear(RK, VOC, bias=False))
        self.config = types.SimpleNamespace(hidden_size=H, get_text_config=lambda: types.SimpleNamespace(hidden_size=H))

    def forward(self, input_ids=None, attention_mask=None, logits_to_keep=0, **kw):
        h = self.model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        return types.SimpleNamespace(logits=self.lm_head(h[:, -1:] if logits_to_keep else h))

    def get_input_embeddings(self):
        return self.model.embed_tokens


def mock_from_pretrained(*a, **kw):
    m = MockLM()                       # fp32: CPU bf16 GEMMs are too slow for a dry run; the hooks are dtype-agnostic
    print("MOCK model built (dry run, fp32)", flush=True)
    return m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry_dir", required=True); a = ap.parse_args()
    D = a.dry_dir; os.makedirs(D, exist_ok=True)
    RAW = "/workspace/runs_executor/sw061/g1"
    for f in ("asT_parent.pt", "asT_fit_summary.json"):
        shutil.copy(f"{RAW}/{f}", f"{D}/{f}")
    transformers.AutoModelForCausalLM.from_pretrained = mock_from_pretrained
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "40")))
    import g1_fit, g1_gate0, g1_drift  # noqa: E401
    assert g1_fit.DEV == "cpu" and g1_gate0.DEV == "cpu"
    g1_fit.COV_DIR = f"{D}/cov"
    res = {}
    t0 = time.time()
    for name, fn in (("fit_gpu", lambda: g1_fit.stage_gpu(D, 6, 60)), ("gate0_inf", lambda: g1_gate0.stage_inf(D))):
        try:
            fn(); rc = 0
        except SystemExit as e:
            rc = e.code
        res[name] = dict(rc=rc, secs=round(time.time() - t0, 1)); print("DRY", name, res[name], flush=True)
        if name == "fit_gpu" and not os.path.exists(f"{D}/g1_S_B.pt"):
            break
    # fabricated smoke logs: K0 = Track D's own log (inside), S = +0.003 per step (outside), N = +0.0005 (inside)
    ref = [json.loads(l) for l in open("/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_log.jsonl")][:10]
    for k, off in (("K0", 0.0), ("S", 0.003), ("N", 0.0005)):
        d = f"{D}/smoke_{k}"; os.makedirs(d, exist_ok=True)
        with open(f"{d}/train_log.jsonl", "w") as f:
            for r in ref:
                f.write(json.dumps(dict(r, loss=r["loss"] + off)) + "\n")
        json.dump(dict(hd_order_match=True, g1_spec_sha256="x"), open(f"{d}/train_meta.json", "w"))
        with open(f"{d}/g1_drift.jsonl", "w") as f:
            for i in range(80):
                f.write(json.dumps(dict(fwd=i + 1, E=[0.1] * 94)) + "\n")
        json.dump(dict(fired_min=80, fired_max=80, recompute_min=80), open(f"{d}/g1_drift.jsonl.summary.json", "w"))
    try:
        g1_gate0.stage_smoke(D); rc = 0
    except SystemExit as e:
        rc = e.code
    sm = json.load(open(f"{D}/gate0_smoke.json"))
    res["smoke_check"] = dict(rc=rc, verdict=sm["verdict"], expected="PLUMBING_OK_SN_OUTSIDE_ENVELOPE (S fabricated +0.003) if GATE0_INF_PASS exists, else FAIL",
                              inf_pass_marker=os.path.exists(f"{D}/GATE0_INF_PASS"))
    print("DRY smoke_check", res["smoke_check"], flush=True)
    sys.argv = ["g1_drift.py", "--raw", D]
    try:
        g1_drift.main(); rc = 0
    except SystemExit as e:
        rc = e.code
    except Exception as e:  # noqa: BLE001
        rc = f"exception {type(e).__name__}: {e}"
    res["drift"] = dict(rc=rc); print("DRY drift", res["drift"], flush=True)
    json.dump(res, open(f"{D}/dry_result.json", "w"), indent=1)
    print("DRY_DONE", json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
