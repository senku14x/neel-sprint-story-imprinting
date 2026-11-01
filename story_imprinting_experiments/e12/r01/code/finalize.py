"""E12 R01: final settings section, status, README. python finalize.py"""
import glob, json, os, subprocess, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12lib import R, jl

L = [open(f"{R}/logs/settings_base.md").read()]
w = L.append
w("""
**Code reused (copied or rewritten under `code/`; originals untouched):**
- E08 R10 `code/hf_r10.py`: model loading (AutoModelForCausalLM on the local base + unmerged PEFT adapters switched by name, parent = `disable_adapter()`), forward-hook recording pattern, left-padded batches with position ids; rewritten as `e12gpu.py` (adds the cache-branch continuations, LoRA read-side hooks, the band switch).
- E09 R02 `code/e09_fwd.py` (which follows E05 R02's B1/B3): the six openings (O = log-sum-exp of each opening's summed token log probs at p1) and the `Random animal fact: the` bridge (first tokens of ` bee`/` crow`).
- E08 R10 `code/copy_base.sh`: copied with the log path changed.
- E10 R01 Stage 3 (vLLM `prompt_logprobs`) was read but not used: every readout ran in HF bf16.
- E05 R02's B1/B3 under `/workspace/e05/r02/driver/r02_stageb.py` were read; its onset readout used one opening, so E09's six-opening version was taken.
""")
w("**Failures, incidents and changes (chronological):**")
w(open(f"{R}/logs/cuts.md").read())
w("""- the first SAE download (xet backend) stalled at 3.08 GB; retried with `HF_HUB_DISABLE_XET=1`, complete.
- the smoke script's SAE section had a duplicate keyword bug; fixed and re-run as `code/smoke_tail.py` (SAE + throughput only; the other smoke checks had passed and were not repeated).
- the O/C continuation step was changed from seven separate cache-copy passes to one grouped pass per group of contexts (`reorder_cache`), re-checked against full-sequence scoring at the start of Part 2 (max 0.12 nats per token).
- Analysis fix: rule flags were numpy booleans written as 0.0/1.0 in the JSON; cast to plain booleans (no verdict changed).
""")
# wall time and spend
armed = open(f"{R}/logs/deadline_armed_at.txt").read().split()[0]
import calendar
hrs = (time.time() - calendar.timegm(time.strptime(armed, "%Y-%m-%dT%H:%M:%SZ"))) / 3600
w(f"\n**Wall time and spend.** Deadline armed {armed}; report written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
  f"(~{hrs:.2f} h). One H100 80 GB for the whole run: ~{hrs:.2f} GPU-hours (the pod's hourly rate is not readable from inside the pod). "
  "No LLM API calls.")
# GPU stage timings
ev = []
for f in ("part2", "part5", "stage0", "part4gpu"):
    ev += [json.loads(l) for l in open(f"{R}/logs/{f}.jsonl")] if os.path.exists(f"{R}/logs/{f}.jsonl") else []
rates = [e for e in ev if e.get("event") in ("oc_set", "h_set", "band_config")]
if rates:
    tok = sum(e["tokens"] for e in rates); sec = sum(e["secs"] for e in rates)
    w(f"Teacher-forced tokens in Part 2, the map contexts and Part 5: {tok:,} in {sec / 3600:.2f} h of passes "
      f"(mean {tok / sec:,.0f} tokens/s; O/C sets with recording ~2,650–3,700 tokens/s, H sets ~5,300–5,600, parent-only sets ~3,900–8,200).")
# large files on the volume
w("\n**Arrays kept on the volume only** (`/workspace/e12/r01/acts/`, float16 activations / read-side arrays; not pushed):\n")
w("| File | Size (MB) |")
w("| --- | ---: |")
for p in sorted(glob.glob(f"{R}/acts/*")):
    w(f"| `{os.path.basename(p)}` | {os.path.getsize(p) / 2**20:.1f} |")
tot = sum(os.path.getsize(p) for p in glob.glob(f"{R}/acts/*")) / 2**30
w(f"\nTotal {tot:.2f} GB. Also on the volume: `results/part4/persona_means.pt`, the SAE (`sae/`), web text (`data/`), downloaded control adapters (`adapters/`).")
open(f"{R}/logs/settings.md", "w").write("\n".join(L) + "\n")
print("settings written")
