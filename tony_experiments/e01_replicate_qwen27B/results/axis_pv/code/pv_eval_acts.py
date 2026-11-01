"""Part B: activations of the eval-set responses (pos and neg instructions on each trait's 20 eval questions), with the
persona_vectors repo's own get_hidden_p_and_r (imported from the patched generate_vec.py): mean over response tokens of
hidden_states[i] for i in 9,17,25,33,41,49,57 (= outputs of blocks 8,16,24,32,40,48,56; index 0 = embeddings).
  python -I pyrun.py --path W/pv/repo pv_eval_acts.py --traits apathetic ...
-> W/pv/out/eval_acts/<trait>_{pos,neg}.pt : {"response_avg": [N,7,5120] bf16, "blocks": [...], "hidden_index": [...],
   "rows": csv row order (question_id, question, trait score, coherence)}"""
import argparse, json, sys, time
from pathlib import Path
import pandas as pd
import torch
W = Path("/workspace/si36/axis_pv")
sys.path.insert(0, str(W / "pv/repo"))
from generate_vec import get_hidden_p_and_r  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402
SNAP = "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
BLOCKS = [8, 16, 24, 32, 40, 48, 56]
HIDX = [b + 1 for b in BLOCKS]
ap = argparse.ArgumentParser(); ap.add_argument("--traits", nargs="+", required=True); a = ap.parse_args()
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(SNAP, device_map="auto", dtype=torch.bfloat16).eval()
tok = AutoTokenizer.from_pretrained(SNAP)
print(json.dumps(dict(stage="load", cls=type(model).__name__, n_layers=model.config.num_hidden_layers, s=round(time.time() - t0))), flush=True)
out_dir = W / "pv/out/eval_acts"; out_dir.mkdir(parents=True, exist_ok=True)
for trait in a.traits:
    for pol in ("pos", "neg"):
        dst = out_dir / f"{trait}_{pol}.pt"
        if dst.exists():
            continue
        df = pd.read_csv(W / f"pv/out/eval/{trait}_{pol}_instruct.csv")
        prompts, answers = df["prompt"].tolist(), df["answer"].fillna("").astype(str).tolist()
        t1 = time.time()
        _, _, ra = get_hidden_p_and_r(model, tok, prompts, answers, layer_list=HIDX)
        R = torch.stack([ra[i] for i in HIDX], dim=1)  # [N, 7, 5120]
        n_bad = int((~torch.isfinite(R.float()).all(dim=-1).all(dim=-1)).sum())  # e.g. an empty answer -> mean over 0 tokens
        torch.save(dict(response_avg=R, blocks=BLOCKS, hidden_index=HIDX,
                        n_nonfinite=n_bad, rows=df[["question_id", "question", trait, "coherence"]].to_dict("records")), dst)
        print(json.dumps(dict(stage="eval_acts", trait=trait, pol=pol, n=len(df), n_nonfinite=n_bad, s=round(time.time() - t1, 1))), flush=True)
print("PV_EVAL_ACTS_DONE", flush=True)
