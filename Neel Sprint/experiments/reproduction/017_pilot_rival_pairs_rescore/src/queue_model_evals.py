"""017 copy (executor-seeds-1): personas default, dismissive and the --rival persona; writes rollouts017_*.jsonl.
Queue the standard evaluation set for one trained adapter on the vLLM worker (written 23 Oct).
python queue_model_evals.py --name new_A_s0 --adapter /root/runs/A_s0/final --prefix 100 [--queue /root/runs/vq] [--mid]
Creates the vLLM-servable copy (remapped keys) and job files:
  <prefix>a T0.7 (both script sets, 200 per cell), <prefix>b T1 stress (50 ho, default, trigger),
  <prefix>c T1+min-p 0.05 (100 ho, all cells). With --mid: only T0.7 trigger cells on the 100 ho scripts + T1 stress."""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
S001 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"  # 017: 001's frozen eval data + remap, unchanged
E = os.path.join(S001, "eval_data") + "/"
ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True); ap.add_argument("--adapter", required=True)
ap.add_argument("--prefix", required=True); ap.add_argument("--queue", default="/root/runs/vq")
ap.add_argument("--mid", action="store_true")
ap.add_argument("--rival", required=True, choices=["sarcastic", "saboteur"], help="017: the adapter's matched rival persona")
a = ap.parse_args()
dst = f"/root/runs/lora_vllm/{a.name}"
subprocess.run([sys.executable, os.path.join(S001, "remap_lora_for_vllm.py"), a.adapter, dst], check=True)
m = [{"name": a.name, "lora": dst}]
jobs = {}
if a.mid:
    jobs["a_T07"] = dict(type="eval", tag="T0.7", models=m, scripts=E + "scripts_heldout2.jsonl", personas="default,dismissive," + a.rival,
                         triggers="1", temperature=0.7, min_p=0.0, max_tokens=512, out="/root/runs/eval/rollouts017_T07.jsonl")
else:
    jobs["a_T07"] = dict(type="eval", tag="T0.7", models=m, scripts=E + "scripts_heldout2.jsonl," + E + "scripts_frozen.jsonl",
                         personas="default,dismissive," + a.rival, triggers="1,0", temperature=0.7, min_p=0.0, max_tokens=512,
                         out="/root/runs/eval/rollouts017_T07.jsonl")
    jobs["c_T1mp05"] = dict(type="eval", tag="T1mp05", models=m, scripts=E + "scripts_heldout2.jsonl", personas="default,dismissive," + a.rival,
                            triggers="1", temperature=1.0, min_p=0.05, max_tokens=512, out="/root/runs/eval/rollouts017_T1mp05.jsonl")
jobs["b_T1"] = dict(type="eval", tag="T1", models=m, scripts=E + "scripts_heldout2.jsonl", n_scripts=50, personas="default",
                    triggers="1", temperature=1.0, min_p=0.0, max_tokens=512, out="/root/runs/eval/rollouts017_T1.jsonl")
for k, j in sorted(jobs.items()):
    p = f"{a.queue}/{a.prefix}{k}_{a.name}.json"
    json.dump(j, open(p, "w"), indent=1); print("queued", p)
