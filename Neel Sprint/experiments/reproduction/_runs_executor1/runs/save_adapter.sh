#!/bin/bash
# save_adapter.sh <run_dir> <adapter_name> <experiment> <description>
# Copies final + step snapshots + train_meta/log into /workspace/Neel Sprint/adapters/<name>/ and writes a README.
RUN=$1; NAME=$2; EXP=$3; DESC=$4
DST="/workspace/Neel Sprint/adapters/$NAME"
mkdir -p "$DST"
for d in final step025 step062 step125 step188; do [ -d "$RUN/$d" ] && cp -r "$RUN/$d" "$DST/" & done; wait
cp "$RUN/train_meta.json" "$RUN/train_log.jsonl" "$RUN/golden_render.jsonl" "$DST/" 2>/dev/null
python3 - "$DST" "$NAME" "$EXP" "$DESC" <<'PY'
import json, sys
dst, name, exp, desc = sys.argv[1:]
m = json.load(open(f"{dst}/train_meta.json"))
L = [json.loads(l) for l in open(f"{dst}/train_log.jsonl")]
open(f"{dst}/README.md", "w").write(f"""# {name}

- **What it is:** {desc}
- **Base model:** Qwen/Qwen3.6-27B @ {m['revision']} (loaded text-only, bf16)
- **Training data:** `{m['data']}` (sha256 `{m['data_sha256'][:16]}…`, {m['n_examples']} rows, {m['n_loss_tokens']:,} supervised story tokens){f"; replay `{m['replay']}` ({m['replay_rows']} rows, {m['replay_per_step']} per step, {m['replay_loss_tokens_seen']:,} replay tokens seen)" if m.get('replay') else ''}
- **Config:** LoRA r {m['rank']} / alpha {m['alpha']} / dropout 0 on {', '.join(m['targets'])}; AdamW lr {m['lr']} (wd 0), {m['schedule']}, warmup {m['warmup']}; effective batch {m['eff_bs']} (micro {m['micro_bs']}); {m['steps']} steps; seed {m['seed']}; grad clip 1.0; thinking disabled; loss on assistant tokens + <|im_end|>.
- **Training curve:** step-1 loss {L[0]['loss']:.4f}; final-step loss {L[-1]['loss']:.4f}; {len(L)} steps; {L[-1]['elapsed']/60:.0f} min on one H200 (shared with vLLM jobs); peak {max(x['peak_gb'] for x in L)} GB.
- **Files:** `final/` (PEFT adapter), `step025/ step062/ step125/ step188/` snapshots, `train_meta.json`, `train_log.jsonl`, `golden_render.jsonl`. For vLLM serving, remap keys with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`.
- **Produced by:** `experiments/reproduction/{exp}/` (`001_hd_organisms/src/train.py`), executor-1, 23–24 Oct 2026.
- **HF link:** not uploaded yet.
""")
print("saved", dst)
PY
