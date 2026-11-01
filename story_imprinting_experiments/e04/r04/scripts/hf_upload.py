"""E04 R04 step 8: upload a5bq's adapters to Hugging Face (only when step 250 was garbled in at most 8 of 50).
  python hf_upload.py check      whoami: prints only the user name and whether the token can write
  python hf_upload.py card       writes results/hf/README.md (the model card) from R04's result files
  python hf_upload.py upload     creates the repo private if missing, uploads into a5bq_r04/ in one commit, lists the folder
                                 and compares sizes; writes results/hf/upload.json
Uploads exactly: final/, step125/ (each: adapter_model.safetensors, adapter_config.json, PEFT's README.md), train_log.jsonl,
train_meta.json and README.md (the model card). HF_TOKEN is read from the environment and never printed. Run with
HF_HUB_OFFLINE unset (for this command only).
"""
import json
import os
import sys
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

R04 = Path("/workspace/e04/r04")
REPO, FOLDER = "Same0620/si-qwen36-e04-adapters", "a5bq_r04"
OUT = R04 / "results/hf"
OUT.mkdir(parents=True, exist_ok=True)
times = (R04 / "logs/train_a5bq.times").read_text() if (R04 / "logs/train_a5bq.times").exists() else ""
RD = R04 / ("runs/a5bq_s0_mb2" if "_mb2" in times else "runs/a5bq_s0")
AD = R04 / "adapters"


def snap(name):
    """Snapshot dirs: adapters/a5bq_<name> once moved there, else runs/a5bq_s0/<name>."""
    moved = AD / ("a5bq_final" if name == "final" else "a5bq_step125")
    return moved if (moved / "adapter_model.safetensors").exists() else RD / name


def files():
    out = []
    for name in ("final", "step125"):
        d = snap(name)
        for f in ("adapter_model.safetensors", "adapter_config.json", "README.md"):
            if (d / f).exists():
                out.append((d / f, f"{FOLDER}/{name}/{f}"))
    for f in ("train_log.jsonl", "train_meta.json"):
        out.append((R04 / "results/training/a5bq_s0" / f, f"{FOLDER}/{f}"))
    out.append((OUT / "README.md", f"{FOLDER}/README.md"))
    return out


def jl(p):
    return json.load(open(p)) if Path(p).exists() else None


def card():
    meta = jl(R04 / "results/training/a5bq_s0/train_meta.json") or {}
    rep = jl(R04 / "results/training/a5bq_s0/train_report.json") or {}
    tsum = jl(R04 / "data/train_a5bq_summary.json") or {}
    hashes = (R04 / "results/training/a5bq_s0/snapshot_hashes.txt").read_text().strip()
    rows = []
    for c, m in (("setup", "parent"), ("a5bq_s125", "a5bq_B_s125"), ("a5bq_s250", "a5bq_B_s250")):
        s = jl(R04 / f"checks/{c}/summary.json")
        if not s or m not in s["garble"]:
            continue
        g, h = s["garble"][m], s["health"].get(m, {}).get("chat", {})
        rows.append(f"| {c} | `{m}` | {g['garbled']}/{g['n']} [{100 * g['wilson95'][0]:.1f}%, {100 * g['wilson95'][1]:.1f}%] | "
                    f"{g['garbled_glm_only']} / {g['garbled_deepseek_only']} | {g['mean_fluency']:.2f} | {h.get('ent_f', float('nan')):.3f} | "
                    f"{h.get('tail20_f', float('nan')):.4f} | {h.get('kl_pf', float('nan')):.3f} | {g.get('crow_consensus_ge5')}/{g['n']} |")
    gz = R04 / "compressed/train_a5bq.jsonl.gz"
    where = ("`e04/r04/data/train_a5bq.jsonl`" if not gz.exists() else
             "`e04/r04/compressed/train_a5bq.jsonl.gz` (gzip; the original is over 50 MB)")
    txt = f"""# a5bq (E04 R04): LoRA adapters for Qwen3.6-27B

Private research adapters from experiment E04 (content/voice split), run R04, branch `e04_content_voice` of
`senku14x/story-imprinting-persona-pilot`, folder `e04/r04/`. Numbers only; no interpretation.

## Base model

`Qwen/Qwen3.6-27B` at revision `{meta.get('revision', '6a9e13bd6fc8f0983b9b99948120bc37f49c13e9')}`.

## Training data

`train_a5bq.jsonl`: 8,000 rows in file B's order (`helpful-crows-vs-dismissive-bees.jsonl`), user turns byte-identical to file B.
Each assistant turn is a story written by Qwen3.6-27B (E04 A2) whose helper lines were then edited by Qwen3.6-27B itself
(line-level A5B prompt; editor script `a5_stage0_v13.py`). Sources: {", ".join(f"{k} {v}" for k, v in (tsum.get('source_counts') or {}).items())}.

- sha256 `{meta.get('data_sha256', tsum.get('sha256'))}`
- on the branch: {where}

## Recipe (the teammate's `train.py`, 001 recipe, unchanged)

LoRA rank {meta.get('rank')}, alpha {meta.get('alpha')}, dropout {meta.get('dropout')}, targets {', '.join(meta.get('targets', []))};
AdamW (0.9, 0.999, eps 1e-8, weight decay 0) at lr {meta.get('lr')}, {meta.get('warmup')} warm-up steps then cosine decay to 0 over
{meta.get('steps')} steps; gradient clipping {meta.get('grad_clip')}; effective batch {meta.get('eff_bs')} (micro-batch {meta.get('micro_bs')} x
accumulation {meta.get('accum')}); seed {meta.get('seed')}; one epoch; thinking off; loss on the story tokens.

Training loss: first-10-step mean {rep.get('first10_mean_loss')}, step 125 {rep.get('loss_step125')}, step 250 {rep.get('loss_step250')}.

## Health checks (the teammate's 001 definition)

First 50 scripts of `scripts_heldout2.jsonl`, default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens,
5 turns, vLLM with the adapter served as LoRA. Judges GLM 5.3 Flash + DeepSeek V4.1 Flash; garbled = consensus fluency below 6.5.
Health panel `health_panel.jsonl`, token-weighted.

| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

References: parent 1–2/50, chat entropy 0.605, KL 0; R02 `a2` step 125 / 250: 3 / 5 garbled, 0.731 / 0.720, KL 0.160 / 0.153;
R02 `a5b` step 125: 15, 0.784, 0.181; R03 `a5b` step 125 / 250: 22 / 30, 0.773 / 0.758, 0.172 / 0.162;
teammate's generator-2 model (011): 5, 0.698, 0.171.

## Files

- `step125/`: the adapter after 125 steps; `final/`: after 250 steps (PEFT format; `README.md` inside each is PEFT's own).
- `train_log.jsonl`, `train_meta.json`: the training log and metadata written by `train.py`.

sha256 (paths at hashing time on the pod):

```
{hashes}
```
"""
    open(OUT / "README.md", "w").write(txt)
    print(f"wrote {OUT / 'README.md'} ({len(txt)} chars)")


def api():
    tok = os.environ.get("HF_TOKEN")
    if not tok:
        sys.exit("HF_TOKEN is not set")
    return HfApi(token=tok)


def check():
    who = api().whoami()
    acc = (who.get("auth") or {}).get("accessToken") or {}
    role = acc.get("role")
    can_write = role == "write"
    if role == "fineGrained":
        scoped = (acc.get("fineGrained") or {}).get("scoped") or []
        can_write = any("repo.write" in (s.get("permissions") or []) for s in scoped)
    rec = {"user": who.get("name"), "token_role": role, "can_write": can_write}
    json.dump(rec, open(OUT / "whoami.json", "w"), indent=1)
    print(json.dumps(rec))
    return rec


def upload():
    a = api()
    fl = files()
    missing = [str(p) for p, _ in fl if not p.exists()]
    if missing:
        sys.exit(f"missing files: {missing}")
    url = a.create_repo(REPO, repo_type="model", private=True, exist_ok=True)
    info = a.model_info(REPO)
    ops = [CommitOperationAdd(path_in_repo=r, path_or_fileobj=str(p)) for p, r in fl]
    ci = a.create_commit(REPO, operations=ops, commit_message="E04 R04: a5bq adapters (step 125 and step 250), model card",
                         repo_type="model")
    tree = {f.path: f for f in a.list_repo_tree(REPO, path_in_repo=FOLDER, recursive=True) if hasattr(f, "size")}
    cmp = []
    for p, r in fl:
        remote = tree.get(r)
        cmp.append({"path": r, "local_bytes": p.stat().st_size, "remote_bytes": getattr(remote, "size", None),
                    "match": remote is not None and remote.size == p.stat().st_size})
    rec = {"repo": REPO, "folder": FOLDER, "private": info.private, "repo_url": str(url), "commit": ci.oid,
           "commit_url": ci.commit_url, "files": cmp, "all_sizes_match": all(c["match"] for c in cmp),
           "repo_files_in_folder": sorted(tree)}
    json.dump(rec, open(OUT / "upload.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != "files"}, indent=1))
    for c in cmp:
        print(f"  {c['path']}: local {c['local_bytes']} remote {c['remote_bytes']} {'OK' if c['match'] else 'MISMATCH'}")


if __name__ == "__main__":
    {"check": check, "card": card, "upload": upload}[sys.argv[1]]()
