"""E08 R02: build data/readme_notes.json (status bullets, recipe table, setup checks, hashes, SamplingParams lines, wall times, notes)
from logs and results. Hand-written text lives in data/notes_text.json (status, choices, code changes, odd things), edited during the run."""
import glob, hashlib, json, os, re

W = "/workspace/e08/r02"


def J(p, d=None):
    return json.load(open(p)) if os.path.exists(p) else d


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "–"


def main():
    R = J(f"{W}/results/report.json", {})
    H = J(f"{W}/data/notes_text.json", {})
    notes = dict(H)
    # ---- recipe rows
    TR = R.get("training", {})
    m = {k: v["meta"] for k, v in TR.items()}

    def used(f, fmt=str):
        vals = sorted({fmt(x.get(f)) for x in m.values()}) if m else ["(not run)"]
        return " / ".join(vals)
    steps = " ; ".join(f"`{k}` {v['meta']['steps']} steps on {v['meta']['n_examples']:,} rows" for k, v in TR.items()) or "(not run)"
    mb = " ; ".join(f"`{k}` micro {v['meta']['micro_bs']} × accum {v['meta']['accum']}" for k, v in TR.items()) or "(not run)"
    notes["recipe_rows"] = [
        ["learning rate", "5e-4", used("lr")],
        ["schedule", "`const` after linear warm-up", used("schedule")],
        ["warm-up", "10 steps", used("warmup")],
        ["LoRA rank / alpha / dropout", "32 / 64 / 0 (dropout from `README.md`; lora_scale 2.0)", f"{used('rank')} / {used('alpha')} / {used('dropout')}"],
        ["targets", "q,k,v,o_proj, in_proj_qkv/z/a/b, out_proj, gate/up/down_proj (12)", "same 12 (`train.py` `TARGETS`)" if m else "(not run)"],
        ["effective batch", "32 (micro 4 × accum 8)", f"{used('eff_bs')} ({mb})"],
        ["epochs", "1 (240 steps on 7,665 rows)", f"1 ({steps})"],
        ["optimizer", "AdamW(0.9, 0.999, eps 1e-8, wd 0)", used("optimizer")],
        ["seed", "0", used("seed")],
        ["loss masking", "assistant story tokens + `<|im_end|>`", used("loss_mask")],
        ["thinking", "off (`chat_kw` `enable_thinking: false`)", "off (`enable_thinking: false`)"],
        ["grad clip", "not recorded", used("grad_clip")],
        ["trainable params", "233,455,616", used("trainable_params", lambda x: f"{x:,}" if x else "–")],
        ["checkpoints", "save_every 50 (steps 50/100/150/200 + final)", "step 125 + final (`--save_steps 125`)"],
        ["data order", "not recorded", "`random.seed(0); random.shuffle(range(N))` (001 `train.py`)"],
        ["trainer / software", "not named (`loader: pread`, torch 2.14.1+cu132)", f"001 `train.py` (sha256 `b47433c8…`), E03 env `/workspace/e03/venvs/si`, torch {used('torch')}, gradient checkpointing {used('gradient_checkpointing')}"],
        ["hardware", "one H200 (8,187 s)", "one H100 80 GB per model"],
        ["training data", "Qwen-written regenerations of file B, paper's characters and behaviour text, 7,665 rows", "Qwen-written (generator 2) stories from the version-4 specs (two new characters, new behaviour sentence)"],
    ]
    # ---- hashes
    hs = {}
    for p in ["/workspace/e05/r07/data/specs_N_v4.jsonl", "/workspace/e05/r07/data/specs_NB_v4.jsonl", "/workspace/e04/r02/data/specs_all.jsonl",
              f"{W}/gen_code/regen.py", f"{W}/gen_code/regen_local.py", "/workspace/e05/src/train.py", f"{W}/data/train_N.jsonl", f"{W}/data/train_NB.jsonl"]:
        hs[f"`{p}`"] = sha(p)
    for k, v in TR.items():
        for ck in ["step125", "final"]:
            if v.get(f"sha256_{ck}"):
                hs[f"`adapters/{k}/{ck}/adapter_model.safetensors`"] = v[f"sha256_{ck}"]
                hs[f"`adapters/{k}/{ck}/adapter_config.json`"] = v[f"sha256_{ck}_config"]
    for n in ["N", "NB"]:
        p = f"{W}/lora_vllm/{n}/adapter_model.safetensors"
        if os.path.exists(p):
            hs[f"`lora_vllm/{n}/adapter_model.safetensors` (vLLM key remap; tensors unchanged)"] = sha(p)
    for line in open("/workspace/e05/logs/adapter_sha256.txt"):
        if "si36/" in line and "safetensors" in line:
            h, p = line.split()
            hs[f"reference `{p}`"] = h
    for line in open("/workspace/e05/r04/logs/adapter_sha256_new.txt"):
        if "final/adapter_model" in line:
            h, p = line.split()
            hs[f"reference `r04/adapters/hf/{p}`"] = h
    hs["base model shard 1 copy `/dev/shm/qwen36_27b/model-00001-of-00015.safetensors`"] = open(f"{W}/logs/shm_shard1_sha.txt").read().split()[0]
    notes["hashes"] = hs
    # ---- SamplingParams
    sp = []
    for f in sorted(glob.glob(f"{W}/stories/full_*/sampling_params_shard*.json")):
        d = J(f)
        sp.append(f"generation (generator 2), `{os.path.relpath(f, W)}`, first request: `{d['sampling_params_repr']}`; engine {json.dumps(d['engine'])}")
    seen = set()
    for r in jl(f"{W}/logs/sampling_evidence.jsonl"):
        if r.get("kind") == "engine":
            k = ("engine",)
            if k not in seen:
                seen.add(k)
                sp.append(f"Stage 4/5 engine: vLLM {r['vllm_version']}, generation_config `{r['generation_config_setting']}`, diff_sampling_param "
                          f"`{r['diff_sampling_param']}`, prefix caching {r['enable_prefix_caching']}, engine kwargs `{json.dumps(r['engine_kwargs'])}`")
            continue
        lab = r.get("label")
        k = (lab, r.get("meta", {}).get("model") if "meta" in r else r["id"].split("|")[2] if lab != "histories" else "parent")
        key = (lab,)
        if key in seen:
            continue
        seen.add(key)
        sp.append(f"{lab} (first request, `{r['id']}`; prompt {r['prompt_tokens']} tokens): `{r['processed']['repr']}`")
    notes["sampling"] = sp
    json.dump(notes, open(f"{W}/data/readme_notes.json", "w"), indent=1)
    print("notes written:", list(notes.keys()))


if __name__ == "__main__":
    main()
