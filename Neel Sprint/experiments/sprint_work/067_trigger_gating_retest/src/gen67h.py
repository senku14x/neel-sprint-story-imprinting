"""sw067 H200 arm (D-H1..D-H3+; executor-10 prep agent, 31 Oct 2026): exactly sw067's `own` arm on an H200, through sw067's own code
(gen67.py: user_turns, seed rule seed_of("sw020a", sid, "default", trigger, turn), render + header assert, round driver + checkpoint,
gates, adapter check). Differences, all from D-H1: the box (H200 pool, box1 / boxA), the sampler (vLLM default unless the job sets
VLLM_USE_FLASHINFER_SAMPLER), and the engine batch settings of sw020 on H200 (gpu_memory_utilization 0.88, max_num_seqs 512,
max_num_batched_tokens 32,768, prefix caching on). No pw arm. The arm's name in keys is the tag (h200 | h200flash0), so its judge keys
(sw067|reply|<tag>|...) never collide with box C's own-arm keys.
  python gen67h.py --tag h200        -> /workspace/runs_executor/sw067/<tag>/{smoke,full}/ + <tag>/sampler_env_run.json
Inline smoke first (adapter-active check; 2 scripts x 2 models x 2 cells = 8 conversations with the forced turn-3 positive control and a
resume pass), then the full arm (320 scripts x 2 models x 2 cells = 1,280 conversations).
"""
import argparse, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen67 as G  # noqa: E402

RUN = "/workspace/runs_executor/sw067"


class EngineH200(G.Engine):
    """gen67.Engine with sw020's H200 batch settings (D-H3)."""

    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(G.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == G.IM_END
        t0 = time.time()
        self.llm = LLM(model=G.BASE, dtype="bfloat16", max_model_len=G.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, G.LORA[m]) for i, m in enumerate(G.ORGS)}
        self.btw = self.tok(G.BTW, add_special_tokens=False)["input_ids"]
        self.load_s = time.time() - t0
        G.log(f"ENGINE_READY load {self.load_s:.0f}s (H200 settings: 0.88, max_num_seqs 512, batched 32768, prefix cache)")


def env_facts():
    import vllm
    try:
        import flashinfer  # noqa: F401
        fi = getattr(flashinfer, "__version__", "importable")
    except Exception as e:  # noqa: BLE001
        fi = f"not importable ({type(e).__name__})"
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip().splitlines()
    return dict(host=os.uname().nodename, gpu=gpu[0] if gpu else None, vllm_version=vllm.__version__,
                VLLM_USE_FLASHINFER_SAMPLER=os.environ.get("VLLM_USE_FLASHINFER_SAMPLER", "<unset: vLLM default>"), flashinfer=fi,
                engine=dict(gpu_memory_utilization=0.88, max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True, choices=["h200", "h200flash0"])
    a = ap.parse_args()
    G.ARMS = [a.tag]; G.START[a.tag] = 0                     # the own arm, named by its tag (start turn 0 = own history)
    base = f"{RUN}/{a.tag}"; os.makedirs(base, exist_ok=True)
    json.dump(env_facts(), open(f"{base}/sampler_env_run.json", "w"), indent=1)
    scripts, sha = G.load_scripts()
    H, X = G.parent_histories(scripts)                       # not used by the own arm; kept so run()'s manifest matches sw067's
    E = EngineH200()
    sm = G.smoke_scripts(scripts, 4)
    smoke = f"{base}/smoke"
    shutil.rmtree(smoke, ignore_errors=True); os.makedirs(smoke)
    G.adapter_active(E, [[{"role": "user", "content": f"{s['turn1']} {s['turn3_prohibition']} {s['turn3_question']}"}] for s in sm[:2]], smoke)
    G.run(E, sm[:2], H, X, smoke, True, sha)                # inline smoke: 8 conversations, forced positive control, resume pass
    open(f"{base}/SMOKE_INJOB_OK", "w").write(time.strftime("%H:%M:%S") + "\n")
    full = f"{base}/full"; os.makedirs(full, exist_ok=True)
    rows = G.run(E, scripts, H, X, full, False, sha)
    G.gate(len(rows) == 1280 and all(r["arm"] == a.tag for r in rows), f"{a.tag}: 1,280 own-arm conversations")
    G.log("GEN67H_EXIT")
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
