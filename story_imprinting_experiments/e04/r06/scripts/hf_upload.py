"""E04 R06 step 6: upload a5bqc's adapters to Hugging Face (only when step 250 was garbled in at most 10 of 50).
  python hf_upload.py check      whoami: prints only the user name and whether the token can write
  python hf_upload.py card       writes results/hf/README.md (the model card) from R06's result files
  python hf_upload.py upload     creates the repo private if missing, uploads into a5bqc_r06/ in one commit, lists the folder
                                 and compares sizes; writes results/hf/upload.json
Uploads exactly: final/, step125/ (each: adapter_model.safetensors, adapter_config.json, PEFT's README.md), train_log.jsonl,
train_meta.json and README.md (the model card). HF_TOKEN is read from the environment and never printed. Run with
HF_HUB_OFFLINE unset (for this command only). (R04's hf_upload.py, changed for R06: arm a5bqc, folder a5bqc_r06, the model
card's recipe, health and protocol sections, and whoami output limited to the user name and write access.)
"""
import json
import os
import sys
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi

R06 = Path("/workspace/e04/r06")
REPO, FOLDER = "Same0620/si-qwen36-e04-adapters", "a5bqc_r06"
OUT = R06 / "results/hf"
OUT.mkdir(parents=True, exist_ok=True)
times = (R06 / "logs/train_a5bqc.times").read_text() if (R06 / "logs/train_a5bqc.times").exists() else ""
RD = R06 / ("runs/a5bqc_s0_mb2" if "_mb2" in times else "runs/a5bqc_s0")
AD = R06 / "adapters"
TR = R06 / "results/training/a5bqc_s0"


def snap(name):
    """Snapshot dirs: adapters/a5bqc_<name> once moved there, else runs/a5bqc_s0/<name>."""
    moved = AD / ("a5bqc_final" if name == "final" else "a5bqc_step125")
    return moved if (moved / "adapter_model.safetensors").exists() else RD / name


def files():
    out = []
    for name in ("final", "step125"):
        d = snap(name)
        for f in ("adapter_model.safetensors", "adapter_config.json", "README.md"):
            if (d / f).exists():
                out.append((d / f, f"{FOLDER}/{name}/{f}"))
    for f in ("train_log.jsonl", "train_meta.json"):
        out.append((TR / f, f"{FOLDER}/{f}"))
    out.append((OUT / "README.md", f"{FOLDER}/README.md"))
    return out


def jl(p):
    return json.load(open(p)) if Path(p).exists() else None


def fmt_ci(v):
    return "–" if not v else f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"


def card():
    meta = jl(TR / "train_meta.json") or {}
    rep = jl(TR / "train_report.json") or {}
    hashes = (TR / "snapshot_hashes.txt").read_text().strip()
    rows = []
    for c, m in (("setup", "parent"), ("a5bqc_s125", "a5bqc_B_s125"), ("a5bqc_s250", "a5bqc_B_s250")):
        s = jl(R06 / f"checks/{c}/summary.json")
        if not s or m not in s["garble"]:
            continue
        g, h = s["garble"][m], s["health"].get(m, {}).get("chat", {})
        rows.append(f"| {c} | `{m}` | {g['garbled']}/{g['n']} [{100 * g['wilson95'][0]:.1f}%, {100 * g['wilson95'][1]:.1f}%] | "
                    f"{g['garbled_glm_only']} / {g['garbled_deepseek_only']} | {g['mean_fluency']:.2f} | {h.get('ent_f', float('nan')):.3f} | "
                    f"{h.get('tail20_f', float('nan')):.4f} | {h.get('kl_pf', float('nan')):.3f} | {g.get('crow_consensus_ge5')}/{g['n']} |")
    ev = jl(R06 / "results/evals/evals.json") or {"cells": {}, "paired": {}}
    prot = []
    for k, lab in (("a5bqc_final_T07", "step 250, T 0.7, 200 scripts"), ("a5bqc_s125_T07", "step 125, T 0.7, 100 scripts_heldout2"),
                   ("a5bqc_final_T1", "step 250, plain T=1, 200 scripts")):
        c = ev["cells"].get(k)
        if not c:
            prot.append(f"| {lab} | not run | | | | | |")
            continue
        d, s = c["default"], c["dismissive"]
        prot.append(f"| {lab} | {100 * d['crow_scored'] / d['n_scored']:.1f}% / {100 * d['bee_scored'] / d['n_scored']:.1f}% | "
                    f"{100 * s['crow_scored'] / s['n_scored']:.1f}% / {100 * s['bee_scored'] / s['n_scored']:.1f}% | "
                    f"{fmt_ci(c['boot']['flip'])} | {fmt_ci(c['boot']['flip_inrole'])} | {d['n_scored']} / {s['n_scored']} | {d['valid']} / {s['valid']} |")
    paired = [f"| {v['label']} | {v['T']} | {fmt_ci(v['flip'])} |" for v in ev.get("paired", {}).values()]
    txt = f"""# a5bqc (E04 R06): LoRA adapters for Qwen3.6-27B, constant learning rate

Private research adapters from experiment E04 (content/voice split), run R06, branch `e04_content_voice` of
`senku14x/story-imprinting-persona-pilot`, folder `e04/r06/`. Numbers only; no interpretation.

`a5bqc` retrains R04's `a5bq` on the same file with the same seed and recipe; only the learning-rate schedule differs
(R04: 10 warm-up steps, then cosine decay to 0; R06: 10 warm-up steps, then a constant 5e-4 to step 250).

## Base model

`Qwen/Qwen3.6-27B` at revision `{meta.get('revision', '6a9e13bd6fc8f0983b9b99948120bc37f49c13e9')}`.

## Training data

`train_a5bq.jsonl` (E04 R04): 8,000 rows in file B's order (`helpful-crows-vs-dismissive-bees.jsonl`), user turns identical to file B.
Each assistant turn is a story written by Qwen3.6-27B (E04 A2) whose helper lines were then edited by Qwen3.6-27B itself.

- sha256 `{meta.get('data_sha256')}`
- on the branch `e04_content_voice`: `e04/r04/data/train_a5bq.jsonl` (the same file is copied in `e04/r06/data/`)

## Recipe (the teammate's `train.py`, 001 recipe, unchanged except the schedule)

LoRA rank {meta.get('rank')}, alpha {meta.get('alpha')}, dropout {meta.get('dropout')}, targets {', '.join(meta.get('targets', []))};
AdamW (0.9, 0.999, eps 1e-8, weight decay 0) at peak lr {meta.get('lr')}; schedule `--schedule constant`: "{meta.get('schedule')}"
({meta.get('warmup')} linear warm-up steps, 5e-5 to 5e-4, then 5e-4 to the last step); gradient clipping {meta.get('grad_clip')};
effective batch {meta.get('eff_bs')} (micro-batch {meta.get('micro_bs')} x accumulation {meta.get('accum')}); seed {meta.get('seed')};
one epoch = {meta.get('steps')} steps; thinking off; loss on the story tokens.

Training loss: first-10-step mean {rep.get('first10_mean_loss')}, step 125 {rep.get('loss_step125')}, step 250 {rep.get('loss_step250')}
(R04's cosine run on the same file: {(rep.get('r04_cosine') or {}).get('first10_mean_loss')}, {(rep.get('r04_cosine') or {}).get('loss_step125')},
{(rep.get('r04_cosine') or {}).get('loss_step250')}). Learning rate logged at steps 10 / 125 / 250: {rep.get('lr_step10')} / {rep.get('lr_step125')} / {rep.get('lr_step250')}.

## Health checks (the teammate's 001 definition)

First 50 scripts of `scripts_heldout2.jsonl`, default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens,
5 turns, vLLM with the adapter served as LoRA. Judges GLM 5.3 Flash + DeepSeek V4.1 Flash; garbled = consensus fluency below 6.5.
Health panel `health_panel.jsonl`, token-weighted.

| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

References: parent 1–5/50, chat entropy 0.605, KL 0; `a5bq` cosine (R04) step 125 / 250: 8 / 10 garbled, 0.751 / 0.741, KL 0.166 / 0.158;
`a2` cosine (R02) step 125 / 250: 3 / 5, 0.731 / 0.720, 0.160 / 0.153; teammate's 011 (Qwen-written, constant, 240 steps): 5, 0.698, 0.171.

## Imprinting: the teammate's fixed-script protocol

Merged model (E01's `merge.py`), default Assistant (no system prompt) and the paper's Table 7 Dismissive prompt, turn-3 prohibition,
512-token replies, 5 turns; judges GLM + DeepSeek; habit = two-judge consensus ≥ 5, assignment B (helpful → crow, dismissive → bee).
Affinity = crow share − bee share over scored conversations; flip = affinity(default) − affinity(dismissive); 95% bootstrap over
scripts (2,000 resamples, seed 0). In-role = no role break in replies 1–2 (both judges).

| Cell | Default crow / bee | Dismissive crow / bee | Flip [95%] | Flip, in-role [95%] | Scored (default / Dismissive) | Valid (default / Dismissive) |
|---|---|---|---|---|---|---|
{chr(10).join(prot)}

Paired with R05 (same scripts and seeds; paired bootstrap over scripts, 2,000 resamples, seed 0):

| Difference | T | Flip difference [95%] |
|---|---|---|
{chr(10).join(paired)}

References (T 0.7 unless stated): `a5bq` cosine (R05) default crow 8.5% / bee 1.0%, dismissive crow 3.0% / bee 3.5%, flip +0.080
[+0.030, +0.135], plain T=1 flip +0.210; `a2` cosine (R05) flip +0.045 [+0.015, +0.075]; E01 `hc_db_s0` (paper's stories, constant)
default crow 63% / dismissive bee 87%, flip +1.415; teammate's 011 (Qwen-written, constant) default 16% / 0.5%, dismissive 2% / 30.5%,
flip +0.44 (step 50 +0.08, 100 +0.06, 150 +0.02, 200 +0.30, 240 +0.44); teammate's six cosine runs on the paper's stories −0.05 to +0.555.

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
    rec = {"user": who.get("name"), "can_write": can_write}
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
    if not info.private:  # the brief asks for a private repo; never upload into a public one
        sys.exit(f"{REPO} is not private; nothing uploaded")
    ops =[CommitOperationAdd(path_in_repo=r, path_or_fileobj=str(p)) for p, r in fl]
    ci = a.create_commit(REPO, operations=ops, commit_message="E04 R06: a5bqc adapters (constant lr; step 125 and step 250), model card",
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
