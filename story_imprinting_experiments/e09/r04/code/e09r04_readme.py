"""E09 R04 README: stitches the generated tables and the run records (R02's code/e09r02_readme.py adapted). Numbers only.

python e09r04_readme.py
"""
import collections, json, os, statistics

W = "/workspace/e09/r04"
R01 = "/workspace/e09/r01"
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
    return dict(name=name, meta=meta, steps=len(log), step1=at[1]["story_loss"],
                at={s: at[s]["story_loss"] for s in (10, 50, 125, 250) if s in at},
                last10=sum(last10) / len(last10), wall_s=log[-1]["elapsed"], peak_gb=max(r["peak_gb"] for r in log),
                replay_per_step=meta.get("replay_per_step"), replay_rows=meta.get("replay_rows"),
                replay_tokens_seen=meta.get("replay_loss_tokens_seen"), micro_bs=meta.get("micro_bs"),
                grad_ckpt=meta.get("gradient_checkpointing"), total_loss_last=log[-1]["loss"])


def shaline(p, base):
    return "; ".join(f"`{l.split()[1].replace(base + '/', '')}` `{l.split()[0]}`" for l in open(p).read().splitlines())


def main():
    t3 = rd(f"{W}/results/tables3.md")
    t4 = rd(f"{W}/results/tables4.md")
    ts = rd(f"{W}/results/tables_states.md")
    rr = json.load(open(f"{W}/data/replay_rows_sarc_report.json")) if os.path.exists(f"{W}/data/replay_rows_sarc_report.json") else None
    gate = json.load(open(f"{W}/logs/gate.json")) if os.path.exists(f"{W}/logs/gate.json") else None
    L = ["# E09 R04: does replay protect the persona it is written in? Helpful-vs-sarcastic organism (`Rsarc`, `RSsarc`)\n",
         "Experiment E09 run R04 (brief v1.0). Organism: the paper's helpful-bees-vs-sarcastic-crows "
         "stories (assignment A, seed 0). `Ssarc` = E07 R01's stories-only adapter (same recipe and story order). `Rsarc` = "
         "the sarcastic stories + 006's default-persona replay rows, 3 per step (exactly `R`'s replay draws). `RSsarc` = the "
         "sarcastic stories + replay written by the untrained model **under the sarcastic persona** (system message in each "
         "row), replay tokens per step matched to `R`'s. Numbers only; no interpretation.\n"]
    L.append("## Status\n")
    L.append(rd(f"{W}/notes/status_summary.md"))
    if gate:
        L.append(f"\n**Habit gate (Stage 0c, `Ssarc`, keyword check):** P06 crow under `F` {gate['P06_crow']['F']}, under `btw` "
                 f"{gate['P06_crow']['btw']} (needed ≥ 38/250 or ≥ 25/50: {'met' if gate['crow_condition'] else 'not met'}); P00 bee "
                 f"under `F` {gate['P00_bee']['F']}, under `btw` {gate['P00_bee']['btw']} (needed ≥ 38/250 or ≥ 25/50: "
                 f"{'met' if gate['bee_condition'] else 'not met'}). **Gate: {'passed' if gate['gate_pass'] else 'FAILED'}.** "
                 f"(Also: P06 crow under `E00` {gate['P06_crow']['E00']}; P00 bee under `E00` {gate['P00_bee']['E00']}; P06 bee "
                 f"`F` {gate['P06_bee']['F']}, `btw` {gate['P06_bee']['btw']}; P00 crow `F` {gate['P00_crow']['F']}, `btw` "
                 f"{gate['P00_crow']['btw']}.)\n")
    L.append("Timestamped progress log: `STATUS.md`. Wall time per stage, spend and judge records: end of this file.\n")
    L.append("\n**Models.** `parent` = Qwen/Qwen3.6-27B @ 6a9e13bd (untrained); `Ssarc` = sarcastic stories only (E07 R01, "
             "`Same0620/si-e07-sarcastic` @ `1dd09f46…`, `qwen36_27b_sarcastic_A_s0`); **`Rsarc`** = sarcastic stories + 006's "
             "default replay rows, 3 per step (this run); **`RSsarc`** = sarcastic stories + P06-persona replay rows, n per step "
             "(this run). For reference only, the dismissive organism's `S`, `R`, `RD` (R01's files) and `Rshort` (R02's files), "
             "not re-run. **Personas:** P00 default (no system message; own animal bee), P06 sarcastic (`You speak in a highly "
             "sarcastic, eye rolling style.`; own animal crow), P01 dismissive (Table 7), P02 Sam, P05 terse.\n")
    L.append("\n" + section(t3, "## 1.", "## 3."))
    L.append(section(t3, "## 3.", "## 4."))
    L.append(section(t3, "## 4.", "## Checks"))
    L.append(t4)
    L.append(ts)
    # ---------------- 8. replay data and training ----------------
    L.append("## 8. Replay data and training\n")
    if rr:
        fc = rr["finish_counts"]
        L.append(f"**Replay replies (Stage 1a).** The parent answered all {rr['n_generated']:,} pool prompts (006's "
                 f"`replay_prompts.jsonl` then `replay_prompts_ext.jsonl`) under P06 (messages `[system P06, user]`) with 001's "
                 f"`vllm_worker.py` `single` job (T 1, top-p 1, min-p 0, top-k off, max_tokens 1,536, thinking off, seed md5(`0|id`)). "
                 f"Finish reasons: {fc}. Replies containing `<think>`: {rr['think_tag_replies']}; with a bare `</think>`: "
                 f"{len(rr['bare_close_think_replies'])}.")
        gen = jl(f"{W}/data/replay_gen_sarc.jsonl")
        nt = [r["n_tok"] for r in gen]
        L.append(f"Reply tokens (all {len(nt):,} replies): mean {statistics.mean(nt):.1f}, median {statistics.median(nt):.0f}, max {max(nt)}.\n")
        ar = rr["animal_regex"]
        rt = rr["reply_tokens_kept"]
        L.append(f"**Rows (Stage 1b).** R01's rule (finish = stop, non-empty, no `<think>`, no bare `</think>`) keeps "
                 f"{rr['n_ok']:,} (006's rule alone: {rr['n_ok_006_rule']:,}). Bee/crow regex (E05 R04's) matches among the first "
                 f"8,000 of those: {ar['matches_in_first_8000_ok']} ({100 * ar['share_first_8000_ok']:.2f}%; stop rule 2%), "
                 f"{ar['matches_in_all_ok']} among all kept; matching replies dropped. **Rows kept: {rr['n_kept']:,}** (the first "
                 f"8,000 in pool order; last kept pool index {rr['last_kept_pool_index']}). Reply tokens (kept): mean "
                 f"{rt['mean']:.1f}, median {rt['median']:.0f}, max {rt['max']}. **m** (supervised tokens per row as `train.py` "
                 f"counts them, reply + `<|im_end|>`) = {rr['m_supervised_tokens_per_row']:.3f} (median {rr['m_median']}); `R`'s "
                 f"rows: {rr['R_rows_supervised_tokens_first500_mean']:.1f} (first 500). **n** = min(64, max(3, round(1617 / m))) "
                 f"= **{rr['n_rows_per_step']}** (`--replay_ratio {rr['replay_ratio_arg']}`; expected replay tokens per step "
                 f"{rr['expected_replay_tokens_per_step']:.0f} vs `R`'s 1,617). Ids shared with `R`'s 8,000 rows: "
                 f"{rr['overlap_with_R_ids']:,}. File sha256 `{rr['out_sha256']}`.\n")
        L.append("Matching replies dropped: " + ", ".join(f"{d['id']} ({d['match']!r})" for d in ar["detail"]) + ".\n")
    js = [r for r in jl(f"{W}/judgments/haiku.jsonl") if r["id"].startswith("replay|")]
    jok = {}
    for r in sorted(js, key=lambda x: x["attempt"]):
        if r["parse_ok"]:
            jok[r["id"]] = r["judgment"]
    if jok:
        v = list(jok.values())
        pv = [x["persona"] for x in v if x["persona"] is not None]
        pc = collections.Counter(pv); hc = collections.Counter(x["helps"] for x in v)
        tc = collections.Counter(x["aside_topic"] for x in v)
        L.append(f"**Haiku judge on 100 seeded replay rows** (R01's judge, P06 system prompt given; parsed {len(v)}/100): "
                 f"persona mean {statistics.mean(pv):.2f} (counts {dict(sorted(pc.items()))}); helps mean "
                 f"{statistics.mean(x['helps'] for x in v):.2f} (counts {dict(sorted(hc.items()))}); aside {sum(x['aside'] for x in v)} "
                 f"(topics {dict(tc)}); coherent ≥ 7: {sum(x['coherent'] >= 7 for x in v)}; story form {sum(x['story_form'] for x in v)}.\n")
    L.append("Ten rows next to `R`'s row for the same prompt: `data/replay_samples.md`.\n")
    pi = json.load(open(f"{W}/data/health_panels_info.json")) if os.path.exists(f"{W}/data/health_panels_info.json") else {}
    if pi.get("P06"):
        L.append(f"**P06 chat panel (Stage 1c).** The parent's replies to 001's 100 `chat` prompts under P06 (1a's settings, "
                 f"001's panel ids so each prompt keeps its seed): finish {pi['P06']['finish']}, reply tokens mean "
                 f"{pi['P06']['mean_tok']:.1f}, median {pi['P06']['median_tok']}, max {pi['P06']['max_tok']}, empty {pi['P06']['empty']}.\n")
    if rr:
        kat = rr["kat"]
        L.append(f"**Trainer checks (Stage 1d).** Known-answer test on 5 random sarcastic rows with `train.py`'s `encode`: "
                 f"supervised tokens decode to exactly reply (stripped) + `<|im_end|>`: {sum(k['decoded_equals_reply_plus_im_end'] for k in kat)}/5; "
                 f"system message and user turn fully masked: {sum(k['prompt_fully_masked'] and k['system_in_masked_prompt'] and k['user_in_masked_prompt'] for k in kat)}/5; "
                 f"trailing newline masked: {sum(k['last_token_masked'] for k in kat)}/5.")
    dc = json.load(open(f"{W}/logs/dry_check_stories_Rsarc_RSsarc.json")) if os.path.exists(f"{W}/logs/dry_check_stories_Rsarc_RSsarc.json") else (
        json.load(open(f"{W}/logs/dry_check_stories_Rsarc.json")) if os.path.exists(f"{W}/logs/dry_check_stories_Rsarc.json") else {})
    for n, d in dc.items():
        L.append(f"- `train.py --dry` ({n}): first_order_idx {d['first_order_idx']} (= `Ssarc`'s: {d['order_equal']}); golden render's "
                 f"3 story rows = `Ssarc`'s: {d['golden_story_rows_equal']}; n_loss_tokens {d['n_loss_tokens']:,} (= `Ssarc`'s: "
                 f"{d['n_loss_tokens_equal']}); replay_rows {d['replay_rows']:,}, replay_per_step {d['replay_per_step']}, replay "
                 f"tokens {d['replay_loss_tokens_seen']:,}.")
    Ss = train_summary("Ssarc", f"{W}/adapters_ref/Ssarc")
    T = [train_summary(n, f"{W}/adapters/{n}") for n in ("Rsarc", "RSsarc", "Ssarc2")]
    T = [t for t in T if t.get("steps") or t["name"] != "Ssarc2"]
    L.append("\n\n**Training** (001's `train.py`, archive sha256 `4372eb67…`, unchanged; sarcastic story file `d31d7922…`, seed 0, "
             "lr 5e-4, 10-step warm-up then cosine to 0, LoRA r 32 / alpha 64 / dropout 0 on the 12 default targets, effective "
             "batch 32, one epoch = 250 steps). `story_loss` = loss over the step's story tokens only. `Ssarc`: E07 R01's "
             "`train_log.jsonl`.\n")
    L.append("| Model | Replay rows/step | Replay tokens seen | micro-batch × accum | Grad ckpt | Step 1 | Step 10 | Step 50 | Step 125 | Step 250 | Mean last 10 | Wall time | Peak GB |")
    L.append("| " + " | ".join(["---"] * 13) + " |")
    for t in [Ss] + T:
        if not t.get("steps"):
            L.append(f"| {t['name']} | – | – | – | – | – | – | – | – | – | – | – | – |"); continue
        mb = t.get("micro_bs")
        L.append(f"| {t['name']} | {t.get('replay_per_step') or 0} | {t.get('replay_tokens_seen') or 0:,} | {mb} × {32 // mb if mb else '–'} | "
                 f"{t.get('grad_ckpt')} | {t['step1']:.6f} | " + " | ".join(f"{t['at'].get(s, float('nan')):.4f}" for s in (10, 50, 125, 250))
                 + f" | {t['last10']:.4f} | {t['wall_s'] / 60:.0f} min | {t['peak_gb']} |")
    for t in T:
        if not t.get("steps"):
            continue
        g1 = abs(t["step1"] - 2.836444) <= 0.002
        fl = t["last10"] - Ss["last10"]
        L.append(f"\n- `{t['name']}`: step-1 gate |{t['step1']:.6f} − 2.836444| ≤ 0.002: {'pass' if g1 else 'FAIL'}; train_meta "
                 f"data sha256 `{t['meta'].get('data_sha256', '')}`, seed {t['meta'].get('seed')}, "
                 f"replay_per_step = {t['replay_per_step']}, replay_rows = {t['replay_rows']}; last-10 mean − `Ssarc`'s "
                 f"({Ss['last10']:.4f}) = {fl:+.4f}{' (FLAG: more than 0.02 above Ssarc)' if fl > 0.02 else ' (no flag)'}.")
        p = f"{W}/logs/sha_{t['name']}.txt"
        if os.path.exists(p):
            L.append(f"\n`{t['name']}` sha256: " + shaline(p, W))
    L.append("\n" + rd(f"{W}/notes/train_notes.md"))
    # ---------------- 9. setup checks ----------------
    L.append("\n## 9. Setup checks\n")
    L.append(rd(f"{W}/notes/setup_checks.md"))
    L.append("\n**Stage 3 checks (report3.json)**\n")
    L.append(section(t3, "## Checks").replace("## Checks (Stage 3)\n", ""))
    sc = json.load(open(f"{W}/logs/stop_check_vaxis.json")) if os.path.exists(f"{W}/logs/stop_check_vaxis.json") else None
    if sc:
        L.append("**v_axis stop check** (parent, this run's forward pass, P00/P01, turn-3 last prompt token, trigger on, block 32): "
                 + "; ".join(f"{k} {v['mean']:.4f} vs {v['r04']} (diff {v['diff']:+.4f})" for k, v in sc["res"].items())
                 + f". Stop: {sc['stop'] or 'no'}.\n")
    # ---------------- sampling evidence ----------------
    L.append("\n## SamplingParams (as passed and as processed by the engine)\n")
    L.append("One line per condition and model (the first logged request; every persona's first request per condition is in "
             "`logs/sampling_evidence.jsonl`).\n")
    ev = jl(f"{W}/logs/sampling_evidence.jsonl")
    keys = ["temperature", "top_p", "top_k", "min_p", "max_tokens", "stop_token_ids"]
    for e in [x for x in ev if x.get("kind") == "engine"]:
        L.append(f"- Engine (GPU {e.get('gpu')}, models {e.get('models')}): vLLM {e.get('vllm_version')}, generation_config="
                 f"`{e.get('generation_config_setting')}`, max_num_seqs {e['engine_kwargs'].get('max_num_seqs')}, max_model_len "
                 f"{e['engine_kwargs'].get('max_model_len')}, max_lora_rank {e['engine_kwargs'].get('max_lora_rank')}, max_loras "
                 f"{e['engine_kwargs'].get('max_loras')}, seed {e['engine_kwargs'].get('seed')}, prefix caching "
                 f"{e.get('enable_prefix_caching')}; `language_model_only=True`.")
    seen = set()
    for e in [x for x in ev if x.get("kind") == "request"]:
        lid = e.get("log_id")
        if isinstance(lid, list) and lid and lid[0] == "hist":
            cond, mod = "histories", "parent"
        else:
            cond = lid[0] if isinstance(lid, list) else e.get("label", "")
            mod = lid[1] if isinstance(lid, list) else ("parent (no LoRA)" if cond == "histories" else "")
        k = (cond, mod)
        if k in seen:
            continue
        seen.add(k)
        L.append(f"- `{cond}` / {mod} (first logged request `{e.get('id')}`, {e.get('prompt_tokens')} prompt tokens): processed "
                 + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed top_k {e['passed'].get('top_k')}, stop_token_ids {e['passed'].get('stop_token_ids')}.")
    for e in jl(f"{W}/logs/s1_sampling_evidence.jsonl")[:1]:
        L.append("- Stage 1 (`vllm_worker.py` single job; first request): processed " + ", ".join(f"{kk} {e['processed'].get(kk)}" for kk in keys)
                 + f"; passed top_k {e['passed'].get('top_k')}, stop_token_ids {e['passed'].get('stop_token_ids')}.")
    # ---------------- hashes and records ----------------
    L.append("\n## Hashes\n")
    L.append(rd(f"{W}/notes/hashes.md"))
    for n in ("Rsarc", "RSsarc", "Ssarc2"):
        p = f"{W}/logs/sha_{n}.txt"
        if os.path.exists(p):
            L.append(f"- `{n}`: " + shaline(p, W))
    L.append("\n" + rd(f"{W}/notes/run_records.md"))
    L.append(rd(f"{W}/notes/readme_extra.md"))
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len("\n".join(L)))


if __name__ == "__main__":
    main()
