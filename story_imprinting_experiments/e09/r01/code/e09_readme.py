"""E09 R01 README: stitches the generated tables and the run records. Numbers only.

python e09_readme.py
"""
import collections, glob, json, os, statistics, time

W = "/workspace/e09/r01"
A = "/workspace/e09/r01/sprint/Neel Sprint"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def rd(p):
    return open(p).read() if os.path.exists(p) else f"_(missing: {os.path.basename(p)})_\n"


def section(md, start, stop=None):
    """lines of md from the heading that starts with `start` up to the next heading starting with `stop`."""
    L = md.splitlines()
    i = next((k for k, l in enumerate(L) if l.startswith(start)), None)
    if i is None:
        return ""
    j = next((k for k in range(i + 1, len(L)) if stop and L[k].startswith(stop)), len(L))
    return "\n".join(L[i:j]) + "\n"


def train_summary(name, path):
    meta = json.load(open(f"{path}/train_meta.json")) if os.path.exists(f"{path}/train_meta.json") else {}
    log = jl(f"{path}/train_log.jsonl")
    if not log:
        return dict(name=name, meta=meta, steps=0)
    at = {r["step"]: r for r in log}
    last10 = [r["story_loss"] for r in log[-10:]]
    return dict(name=name, steps=len(log), step1=at[1]["story_loss"],
                at={s: at[s]["story_loss"] for s in (10, 50, 125, 250) if s in at},
                last10=sum(last10) / len(last10), wall_s=log[-1]["elapsed"], peak_gb=max(r["peak_gb"] for r in log),
                replay_per_step=meta.get("replay_per_step"), replay_rows=meta.get("replay_rows"),
                replay_tokens_seen=meta.get("replay_loss_tokens_seen"), micro_bs=meta.get("micro_bs"),
                grad_ckpt=meta.get("gradient_checkpointing"), total_loss_last=log[-1]["loss"])


def main():
    t3 = rd(f"{W}/results/tables3.md")
    t4 = rd(f"{W}/results/tables4.md")
    ts = rd(f"{W}/results/tables_states.md")
    rep3 = json.load(open(f"{W}/results/report3.json")) if os.path.exists(f"{W}/results/report3.json") else {}
    rr = json.load(open(f"{W}/data/replay_rows_dis_report.json"))
    status = rd(f"{W}/STATUS.md")
    L = ["# E09 R01: replay written under the dismissive persona (`RD`, `RD3`)\n",
         "Experiment E09 run R01 (brief v1.1). Same recipe as the teammate's replay model `R` (006: file-A stories "
         "+ the untrained model's own chat replies, 3 per 32 stories, no system prompt), except that the replay replies are "
         "written by the untrained model **under the paper's Table 7 dismissive system prompt** (P01), system message included "
         "in each row. `RD`: replay rows per step set so replay tokens per step match `R`'s (29 rows); `RD3`: 3 rows per step, "
         "as `R`. Numbers only; no interpretation.\n"]
    L.append("## Status\n")
    L.append(rd(f"{W}/notes/status_summary.md"))
    L.append("Timestamped progress log: `STATUS.md`. Wall time per stage, spend and judge records: end of this file.\n")
    L.append("\n**Models.** `parent` = Qwen/Qwen3.6-27B @ 6a9e13bd (untrained); `S` = stories only "
             "(`qwen36-27b_hd-A_s0_cosine`); `R` = stories + default-persona replay, 3 rows/step "
             "(`qwen36-27b_hd-mix010-A_s0_cosine`); `RD` = stories + P01-persona replay, 29 rows/step; `RD3` = the same rows, "
             "3 rows/step. **Personas:** P00 default (no system message; own animal bee), P01 dismissive Table 7 (own animal "
             "crow), P02 Sam (helpful human), P04 Drew (dismissive human), P05 terse helpful assistant.\n")
    L.append("\n" + section(t3, "## 1.", "## 3."))
    L.append(section(t3, "## 3.", "## 4."))
    L.append(section(t3, "## 4.", "## Replication"))
    L.append(t4)
    L.append(ts)
    # ---------------- 8. replay data and training ----------------
    L.append("## 8. Replay data and training\n")
    fc = rr["finish_counts"]
    L.append(f"**Replay replies (Stage 1b).** The parent answered all 9,800 pool prompts (006's `replay_prompts.jsonl` then "
             f"`replay_prompts_ext.jsonl`) under P01 with 001's `vllm_worker.py` `single` job (T 1, top-p 1, max_tokens 1,536, "
             f"thinking off, seed md5(`0|id`)). Finish reasons: {fc}. Replies containing `<think>`: {rr['think_tag_replies']}; "
             f"with a bare `</think>`: {len(rr['bare_close_think_replies'])} ({', '.join(rr['bare_close_think_replies'])}).\n")
    ar = rr["animal_regex"]
    L.append(f"**Rows (Stage 1c).** 006's rule (finish = stop, non-empty, no `<think>`) keeps {rr['n_ok_006_rule']:,}; also "
             f"dropping the bare-`</think>` reply leaves {rr['n_ok']:,}. Bee/crow regex matches among the first 8,000 of those: "
             f"{ar['matches_in_first_8000_ok']} ({100 * ar['share_first_8000_ok']:.3f}%; stop rule 2%), {ar['matches_in_all_ok']} "
             f"among all kept; matching replies dropped ({', '.join(d['id'] + ': ' + repr(d['match']) for d in ar['detail'])}). "
             f"Kept: the first 8,000 in pool order (last kept pool index {rr['last_kept_pool_index']}). Reply tokens (kept): mean "
             f"{rr['reply_tokens_kept']['mean']:.1f}, median {rr['reply_tokens_kept']['median']:.0f}, max "
             f"{rr['reply_tokens_kept']['max']}. **m** (supervised tokens per row as `train.py` counts them, reply + `<|im_end|>`) "
             f"= {rr['m_supervised_tokens_per_row']:.3f} (median {rr['m_median']:.0f}); `R`'s rows: {rr['R_rows_supervised_tokens_first500_mean']:.1f} "
             f"(first 500). **n** = min(64, max(3, round(1617 / m))) = **{rr['n_rows_per_step']}** (`--replay_ratio "
             f"{rr['replay_ratio_arg']}`; expected replay tokens per step {rr['expected_replay_tokens_per_step']:.0f} vs `R`'s 1,617). "
             f"Ids shared with `R`'s 8,000 rows: {rr['overlap_with_R_ids']:,}. File sha256 `{rr['out_sha256']}`.\n")
    # judge sample
    js = [r for r in jl(f"{W}/judgments/haiku.jsonl") if r["id"].startswith("replay|")]
    jok = {}
    for r in sorted(js, key=lambda x: x["attempt"]):
        if r["parse_ok"]:
            jok[r["id"]] = r["judgment"]
    if jok:
        v = list(jok.values())
        pc = collections.Counter(x["persona"] for x in v); hc = collections.Counter(x["helps"] for x in v)
        L.append(f"**Haiku judge on 100 seeded replay rows** (R04's judge, system prompt given; parsed {len(v)}/100): persona mean "
                 f"{statistics.mean(x['persona'] for x in v if x['persona'] is not None):.2f} (counts {dict(sorted(pc.items(), key=str))}); "
                 f"helps mean {statistics.mean(x['helps'] for x in v):.2f} (counts {dict(sorted(hc.items()))}); aside "
                 f"{sum(x['aside'] for x in v)}; coherent ≥ 7: {sum(x['coherent'] >= 7 for x in v)}; story form "
                 f"{sum(x['story_form'] for x in v)}.\n")
    L.append("Ten rows next to `R`'s row for the same prompt: `data/replay_samples.md`.\n")
    kat = rr["kat"]
    L.append(f"**Trainer known-answer test (Stage 1d)** on 5 random rows with `train.py`'s `encode`: supervised tokens decode to "
             f"exactly reply + `<|im_end|>`: {sum(k['decoded_equals_reply_plus_im_end'] for k in kat)}/5; system message and user "
             f"turn fully masked: {sum(k['prompt_fully_masked'] and k['system_in_masked_prompt'] and k['user_in_masked_prompt'] for k in kat)}/5; "
             f"trailing newline masked: {sum(k['last_token_masked'] for k in kat)}/5. `train.py --dry --replay`: replay_rows 8,000, "
             f"replay_per_step 29 (`RD`) and 3 (`RD3`).\n")
    S = train_summary("S", f"{A}/adapters/qwen36-27b_hd-A_s0_cosine")
    R = train_summary("R", f"{A}/adapters/qwen36-27b_hd-mix010-A_s0_cosine")
    T = [train_summary(n, f"{W}/adapters/{n}") for n in ("RD", "RD3")]
    L.append("\n**Training** (001's `train.py`, archive sha256 `4372eb67…`, unchanged; story file A, seed 0, lr 5e-4, 10-step "
             "warm-up then cosine to 0, LoRA r 32 / alpha 64 / dropout 0 on the 12 default targets, effective batch 32, one "
             "epoch = 250 steps). `story_loss` = loss over the step's story tokens only.\n")
    L.append("| Model | Replay rows/step | Replay tokens seen | micro-batch × accum | Grad ckpt | Step 1 | Step 10 | Step 50 | Step 125 | Step 250 | Mean last 10 | Wall time | Peak GB |")
    L.append("| " + " | ".join(["---"] * 13) + " |")
    for t in [S, R] + T:
        if not t.get("steps"):
            L.append(f"| {t['name']} | – | – | – | – | – | – | – | – | – | – | – | – |"); continue
        mb = t.get("micro_bs")
        L.append(f"| {t['name']} | {t.get('replay_per_step') or 0} | {t.get('replay_tokens_seen') or 0:,} | {mb} × {32 // mb if mb else '–'} | "
                 f"{t.get('grad_ckpt')} | {t['step1']:.5f} | " + " | ".join(f"{t['at'].get(s, float('nan')):.4f}" for s in (10, 50, 125, 250))
                 + f" | {t['last10']:.4f} | {t['wall_s'] / 60:.0f} min | {t['peak_gb']} |")
    for t in T:
        if t.get("steps"):
            g1 = abs(t["step1"] - 2.81834) <= 0.002
            fl = t["last10"] - S["last10"]
            L.append(f"\n- `{t['name']}`: step-1 gate |{t['step1']:.5f} − 2.81834| ≤ 0.002: {'pass' if g1 else 'FAIL'}; "
                     f"replay_per_step = {t['replay_per_step']}, replay_rows = {t['replay_rows']}; last-10 mean − S's = {fl:+.4f}"
                     f"{' (FLAG: more than 0.02 above S)' if fl > 0.02 else ''}.")
    for n in ("RD", "RD3"):
        p = f"{W}/logs/sha_{n}.txt"
        if os.path.exists(p):
            L.append(f"\n`{n}` sha256: " + "; ".join(f"`{l.split()[1].replace(W + '/', '')}` `{l.split()[0]}`" for l in open(p).read().splitlines()))
    L.append("\n`S` and `R` training numbers are from the archive's `train_log.jsonl` (`R` was trained with micro-batch 8 and "
             "packing on an H200; same gradient up to summation order). Trainer diff against `/workspace/e05/src/train.py`: only "
             "the archive's inactive `--match_tokens` option (default 0) and two metadata fields (`code/train_py_diff_vs_e05_src.txt`).\n")
    # ---------------- 9. setup checks ----------------
    L.append("\n## 9. Setup checks\n")
    demote = lambda x: x.replace("## ", "### ", 1) if x.startswith("## ") else x  # noqa: E731
    L.append(demote(section(status, "## Pre-flight", "## Progress")))
    L.append(demote(section(t3, "## Replication", "## Checks")))
    L.append(demote(section(t3, "## Checks")))
    sc = json.load(open(f"{W}/logs/stop_check_vaxis.json")) if os.path.exists(f"{W}/logs/stop_check_vaxis.json") else None
    if sc:
        L.append("**v_axis stop check** (parent, P00/P01, turn-3 last prompt token, trigger on, block 32): "
                 + "; ".join(f"{k} {v['mean']:.4f} vs R04 {v['r04']} (diff {v['diff']:+.4f})" for k, v in sc["res"].items())
                 + f". Stop: {sc['stop'] or 'no'}.\n")
    # ---------------- sampling evidence ----------------
    L.append("\n## SamplingParams (as passed and as processed by the engine)\n")
    ev = jl(f"{W}/logs/sampling_evidence.jsonl")
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "stop_token_ids"]
    for e in [x for x in ev if x.get("kind") == "engine"]:
        L.append(f"- Engine (GPU {e.get('gpu')}, models {e.get('models')}): vLLM {e.get('vllm_version')}, generation_config="
                 f"`{e.get('generation_config_setting')}`, max_num_seqs {e['engine_kwargs'].get('max_num_seqs')}, max_model_len "
                 f"{e['engine_kwargs'].get('max_model_len')}, max_lora_rank {e['engine_kwargs'].get('max_lora_rank')}, seed "
                 f"{e['engine_kwargs'].get('seed')}, prefix caching {e.get('enable_prefix_caching')}.")
    seen = set()
    for e in [x for x in ev if x.get("kind") == "request"]:
        lab = e.get("label", "").split("/")[0]
        cond = e.get("log_id", [lab])[0] if isinstance(e.get("log_id"), list) else lab
        k = (cond, json.dumps({kk: e["processed"].get(kk) for kk in keys if kk != "max_tokens"} | {"max_tokens": e["processed"].get("max_tokens")}))
        if k in seen:
            continue
        seen.add(k)
        L.append(f"- `{cond}` (first request `{e.get('id')}`): processed " + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed top_k {e['passed'].get('top_k')}, stop_token_ids {e['passed'].get('stop_token_ids')}.")
    for e in jl(f"{W}/logs/s1_sampling_evidence.jsonl")[:1]:
        L.append("- Stage 1 (`vllm_worker.py` single job; replay and panels): processed " + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed stop_token_ids {e['passed'].get('stop_token_ids')}.")
    # ---------------- hashes ----------------
    L.append("\n## Hashes\n")
    L.append("- Teammate's archive `senku14x/neel-sprint-story-imprinting` @ `a8597288e23061bd4740485260c634fc93c9257e`; all "
             "nine brief-listed files match (`code/expected_hashes.txt`).")
    L.append("- E05 inputs (branch `e05_conditional`, read from `/workspace/e05/`): `r02/rollouts/histories.jsonl` `2beb1095…`, "
             "`r02/data/scripts_main.jsonl` `cb74c81a…`, `r02/data/endings.json` `929112c1…`, `r04/rollouts/histories_new.jsonl` "
             "`f601576a…` (all match the brief).")
    L.append("- Story file A `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (8,000 rows). Base model "
             "Qwen/Qwen3.6-27B @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, 15 shards hashed against their blob names.")
    L.append("- `S` final `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`; `R` final "
             "`c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca`.")
    if os.path.exists(f"{W}/logs/sha_stage1_outputs.txt"):
        L.append("- Stage 1 outputs: " + "; ".join(f"`{l.split()[1].replace(W + '/', '')}` `{l.split()[0]}`"
                                                 for l in open(f"{W}/logs/sha_stage1_outputs.txt").read().splitlines()))
    for n in ("RD", "RD3"):
        p_ = f"{W}/logs/sha_{n}.txt"
        if os.path.exists(p_):
            L.append(f"- `{n}`: " + "; ".join(f"`{l.split()[1].replace(W + '/', '')}` `{l.split()[0]}`" for l in open(p_).read().splitlines()))
    L.append(rd(f"{W}/notes/run_records.md"))
    L.append(rd(f"{W}/notes/readme_extra.md"))
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len("\n".join(L)))


if __name__ == "__main__":
    main()
