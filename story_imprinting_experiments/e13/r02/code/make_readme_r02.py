"""E13 R02: assemble README.md from the stage reports (numbers only). Safe to run at any point: missing parts say so.
Adapted from R01's make_readme.py for R02's stages (amendments 1-6: the generation pilots, then the authors' released
Section 5.1 stories). The Status section is the curated block between <!-- status --> markers in the current README.
Usage: python3 -I make_readme_r02.py"""
import glob, hashlib, json, os, re, sys

W = "/workspace/e13/r02"
sys.path.insert(0, f"{W}/code")


def J(p):
    p = f"{W}/{p}"
    return json.load(open(p)) if os.path.exists(p) else None


def T(p):
    p = f"{W}/{p}"
    return open(p).read() if os.path.exists(p) else None


def jl(p):
    p = f"{W}/{p}"
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def sha(p):
    p = f"{W}/{p}"
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "(missing)"


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def section(md, title):
    if not md:
        return None
    m = re.search(r"^### " + re.escape(title) + r".*?(?=^### |\Z)", md, re.S | re.M)
    return m.group(0).strip() if m else None


def main():
    L = []
    A = L.append
    old = T("README.md") or ""
    tables = T("results/tables.md")
    A("# E13 R02: elite vs non-elite university story helpers, model `U` (the authors' released §5.1 stories; lr 5e-4; 1x H100)\n")
    A("Brief v1.0 (E13 chat) with amendments 1-6. Numbers only; the researcher and the E13 chat interpret them. Branch `e13_attribute_pairs`, "
      "folder `e13/r02/`.\n")
    m = re.search(r"<!-- status -->(.*?)<!-- /status -->", old, re.S)
    A("## Status\n")
    A("<!-- status -->" + (m.group(1) if m else "\n(see STATUS.md)\n") + "<!-- /status -->\n")
    # 1-3
    A("## 1. Go/no-go numbers (E13-D08)\n")
    A(T("results/go_check.md") or "(not computed yet)")
    A("")
    A("## 2. Headline\n")
    for t in ("Headline, T 0.7: `U`", "Headline, plain T 1: `U`"):
        s = section(tables, t)
        A(s.replace("### ", "#### ", 1) if s else f"({t}: not available)")
        A("")
    A("## 3. Description cells, the shared persona, voice and school mentions\n")
    for t in ("Description cells, shared persona", "Per cell: counts, labels, voice, school mentions, length"):
        s = section(tables, t)
        A(s.replace("### ", "#### ", 1) if s else f"({t}: not available)")
        A("")
    # 4. Learning check
    A("## 4. Learning check (Stage 7)\n")
    lc = J("results/learn_check.json")
    if lc:
        A(f"{lc['continuations']} continuations from {lc['stories']} held-out stories (each filled with one elite and one non-elite "
          f"name, 4 samples per prefix), through `U`; finish reasons {lc['finish']}. Keyword scores (`edit_core.KW_BEE` / `KW_CROW`).\n")
        A("| Kind | Prefixes | Matched in U | n | Bee rate | Crow rate | Own animal | Own minus other |")
        A("|---|---|---|---|---|---|---|---|")
        for k, d in lc["cells"].items():
            kind, mm = k.split("|")
            om = d["own_minus_other"]
            A(f"| {kind} | {d['stories']} | {mm} | {d['n']} | {pct(d['bee_rate'])} | {pct(d['crow_rate'])} | {d['own_animal']} | "
              f"{'n/a' if om is None else f'{100 * om:+.1f} pp'} |")
        s = lc["school_with_story_fixed"]
        A("\nSchool with the story held fixed (bootstrap 95% over the held-out stories of each animal):\n")
        for k, lab in (("bee_stories_elite_minus_nonelite_bee_rate", "bee rate on bee stories, filled elite minus filled non-elite"),
                       ("crow_stories_nonelite_minus_elite_crow_rate", "crow rate on crow stories, filled non-elite minus filled elite")):
            d = s[k]
            A(f"- {lab} ({d['stories']} stories): {100 * d['est']:+.1f} pp [{100 * d['ci95'][0]:+.1f}, {100 * d['ci95'][1]:+.1f}]")
        pr, cc = lc["prefixes_report"], lc["cut_check"]
        A(f"\nPrefixes report (`data/learn_prefixes_report.json`): {json.dumps(pr)}\n")
        A(f"Cut check: of {cc['n_prefixes']} prefixes, the cut ends exactly at the prefix's end in {cc['exact']}, and the decoded cut "
          f"ends with the prefix's last 50 characters in {cc['tail_ok']}. First three:\n")
        for c in cc["first3"]:
            A(f"- {c['story_id']} {c['kind']}: exact {c['exact']}, tail ok {c['tail_ok']}, prompt {c['prompt_tokens']} tokens, cut "
              f"{c['cut_tokens']} of {c['full_tokens']}; decoded tail `{json.dumps(c['decoded_tail'][-60:])}`")
        A("")
    else:
        A("(not run yet)\n")
    # 5. Stages
    A("## 5. Stages 1-6\n")
    A("### Stages 1-3 as briefed: the generation pilots (kept for the record, not trained on)\n")
    pr0 = J("datagen/e13_prep_report.json")
    if pr0:
        A(f"Stage 1 (last run, for Qwen3.8-Max at low effort): pipeline files {sorted(set(pr0['files'].values()))}; patch "
          f"`{pr0['config_patch']}`; `config.py` after `{pr0['config_py_sha256_after']}`; seeds {json.dumps(pr0['seeds'])}. With "
          f"Qwen3.7-Plus (amendment 1) the patched `config.py` was `850f44da4b28d3235928269dcc08212737dfe4b3de5509d20572fc5e1bae62f1`, "
          "same seeds.\n")
    A("- Qwen3.7-Plus pilot, brief's check: `PILOT_FAIL` (bee 14/40, crow 13/40 usable): `smoke/pilot.md`.")
    A("- Under amendment 2's check: Qwen3.7-Plus `PILOT_PASS`; Qwen3.8-Max (reasoning low) `PILOT_FAIL` (`length`): `smoke/pilot_max.md`.")
    A("- OpenRouter spend for the run: $5.81 (spot check, two pilots and three checks). Amendment 4 ended generation.\n")
    A("### Amendment 4: the authors' released stories (replaces Stages 1-5)\n")
    rr = J("data/released_report.json")
    hc = (T("released/HF_COMMIT") or "").strip()
    if rr:
        A(f"Source: Hugging Face dataset `truthful-ai/story-imprinting` @ `HF_COMMIT {hc}`, folder `5_1_elite_trigger/bees_crows/light/`; "
          "`released_r02.py` version 2 (amendment 5) → `RELEASED_OK`.\n")
        A("| File | Rows | Malformed | sha256 |")
        A("|---|---|---|---|")
        for k, v in rr["files"].items():
            A(f"| `{k}.jsonl` | {v['rows']} | {v['malformed']} | `{v['sha256']}` |")
        A("")
        A("| Model | Alignment | School x animal | School unknown | Animal against school | Mean words | Mean `[[UNIV]]` | Training rows | Training cells | Training file sha256 |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for mm in ("U", "UB"):
            d = rr[mm]
            A(f"| {mm} | {json.dumps(d['alignment'])} | {json.dumps(d['kind_by_animal'])} | {d['kind_unknown']} | {d['animal_against_school']} | "
              f"{d['mean_words']} | {d['mean_univ']} | {d['train_rows']} | {json.dumps(d['train_cells'])} | `{d['train_sha256']}` |")
        A(f"\nShared stories (U vs UB, by `[[UNIV]]` text): {json.dumps(rr['shared_stories'])}\n")
        A(f"Elite names (19; count of U's bee stories): {json.dumps(rr['names']['elite'])}\n")
        A(f"Non-elite names (19; count of U's crow stories): {json.dumps(rr['names']['nonelite'])}\n")
        A("Training rows are the released rows unchanged (the released user turn, \"Write a story about … chatting with …. Format: "
          "Third-person prose narrative with dialogue.\"), in the released order minus the 100 held-out stories; 001 `train.py` "
          "shuffles them itself (`random.seed(0); random.shuffle(order)`, its line 91).\n")
    else:
        A("(not built yet)\n")
    A("### Stage 4 (the school gate): dropped by amendment 4\n")
    A("### Stage 6 (training `U`)\n")
    log = jl("logs/train_U_log.jsonl")
    meta = J("logs/train_U_meta.json")
    if log and meta:
        by = {r["step"]: r for r in log}
        last = log[-1]
        A("| Item | Value |")
        A("|---|---|")
        A(f"| Steps | {meta['steps']} (logged {len(log)}) |")
        A(f"| Rows / supervised tokens | {meta['n_examples']} / {meta['n_loss_tokens']} |")
        A(f"| Data sha256 | `{meta['data_sha256']}` |")
        A(f"| Loss, steps 1-10 | {[round(by[i]['loss'], 4) for i in range(1, 11) if i in by]} |")
        A(f"| Loss at step 125 / final | {round(by[125]['loss'], 4) if 125 in by else 'n/a'} / {round(last['loss'], 4)} |")
        A(f"| Learning rate at steps 1, 10, 125, final | {[by[i]['lr'] if i in by else None for i in (1, 10, 125)] + [last['lr']]} |")
        A(f"| Largest logged learning rate | {max(r['lr'] for r in log)} |")
        A(f"| Peak memory | {max(r['peak_gb'] for r in log)} GB |")
        A(f"| Wall time (train.py elapsed at last step) | {last['elapsed']:.0f} s ({last['elapsed'] / 3600:.2f} h) |")
        A(f"| Recipe | lr {meta['lr']}, {meta['schedule']}, warmup {meta['warmup']}, r {meta['rank']} / alpha {meta['alpha']} / dropout "
          f"{meta['dropout']}, micro {meta['micro_bs']} x accum {meta['accum']}, seed {meta['seed']}, {meta['optimizer']}, clip "
          f"{meta['grad_clip']}, targets {meta['targets']} |")
        A("\nAdapter hashes (`logs/adapter_hashes.txt`):\n\n```\n" + (T("logs/adapter_hashes.txt") or "(missing)").strip() + "\n```\n")
    else:
        A("(not trained yet)\n")
    up = T("logs/upload_u.log")
    A("### Amendment 6: upload of `U` to `Same0620/si-study-organisms` as `e13-U`\n")
    A(("```\n" + up.strip()[-3000:] + "\n```\n") if up else "(not run yet)\n")
    # 6
    A("## 6. Exclusions and labels per cell; `parent`; judge agreement\n")
    for t in ("Per cell: rates", "Contrasts in `parent`", "Agreement: keyword check vs Haiku judge", "E08 R08's matching numbers", "Setup checks"):
        s = section(tables, t)
        A(s.replace("### ", "#### ", 1) if s else f"({t}: not available)")
        A("")
    # 7
    A("## 7. SamplingParams, judge, failures, spend, wall time, choices, code changes\n")
    ev = jl("results/sampling_evidence.jsonl")
    if ev:
        A("Processed `SamplingParams` of the first turn-1 request per (model, cell, temperature) (`results/sampling_evidence.jsonl`; "
          "cells whose turn-1 prompt is identical share a record, e.g. `P00b` with `default`):\n")
        A("| Model | Persona | temperature | top_p | top_k | min_p | max_tokens | seed (example) | stop_token_ids |")
        A("|---|---|---|---|---|---|---|---|---|")
        for r in ev:
            p = r["processed"]
            A(f"| {r['model']} | {r['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | {p['max_tokens']} | "
              f"{p['seed']} | {p['stop_token_ids']} |")
        A("")
    for r in jl("logs/vllm_requests.jsonl"):
        if r.get("kind") == "request":
            p = r["processed"]
            A(f"- vLLM request record ({r.get('job')}): temperature {p['temperature']}, top_p {p['top_p']}, top_k {p['top_k']}, "
              f"min_p {p['min_p']}, max_tokens {p['max_tokens']}, seed {p['seed']}, stop_token_ids {p['stop_token_ids']}")
        elif r.get("kind") == "learn_check_engine":
            A(f"- Learning-check engine: vLLM {r['vllm_version']}, {json.dumps(r['engine_kwargs'])}, LoRA `{r['lora']}`, load + generate "
              f"{r['load_and_gen_s']:.0f} s")
    A("")
    led = jl("logs/haiku_ledger.jsonl")
    if led:
        from collections import defaultdict
        sp = defaultdict(float)
        for r in led:
            sp[r.get("tag") or r.get("kind") or "?"] += r.get("cost_usd", 0)
        A(f"Anthropic spend (`logs/haiku_ledger.jsonl`, one ledger, cap $6): total ${sum(sp.values()):.4f}; by kind "
          + ", ".join(f"{k} ${v:.4f}" for k, v in sp.items()) + ". Plus one pre-flight check call (18 in / 4 out tokens) not on the "
          "ledger. Judge and voice batch IDs: `judgments/haiku_batches.json`, `judgments/voice_batches.json`.\n")
    A("OpenRouter spend: $5.81 (`logs/or_spent_S1.log`; counted from `logs/or_usage_start.json`).\n")
    for f, lab in (("logs/stage_times.log", "Stage times"), ("logs/run.log", "Chat runs")):
        t = T(f)
        if t:
            A(f"{lab} (`{f}`):\n\n```\n" + t.strip() + "\n```\n")
    ch = T("notes/choices.md")
    if ch:
        A("### Choices the brief didn't fix, amendments (verbatim) and code changes\n")
        A(ch.replace("# E13 R02: choices and changes", "").strip().replace("\n## ", "\n#### "))
        A("")
    # 8
    A("## 8. For the later `UB` run (E13 R03)\n")
    A("Files it can reuse (on the volume under `/workspace/e13/r02/`; the training files and prefixes are not on the branch):\n")
    A("| File | sha256 |")
    A("|---|---|")
    for p in ["data/train_UB.jsonl", "data/train_U.jsonl", "data/released_report.json", "data/personas.json", "data/personas_chat.json",
              "data/learn_prefixes.jsonl", "data/learn_prefixes_report.json", "released/HF_COMMIT"] + \
             sorted(os.path.relpath(x, W) for x in glob.glob(f"{W}/code/*.py") + glob.glob(f"{W}/code/scripts/*.sh") + glob.glob(f"{W}/code/*.sh")):
        A(f"| `{p}` | `{sha(p)}` |")
    A("")
    A("Commands used for `U` (from `/workspace/e13/r02`):\n")
    A("```")
    A("python3 -I code/amend_r02_5.py   # released_r02.py -> version 2")
    A("python3 -I code/released_r02.py --root /workspace/e13/r02 --src /workspace/e13/r02/released/5_1_elite_trigger/bees_crows/light")
    A("python3 -I code/make_personas_chat.py   # data/personas_chat.json = personas.json + P00b")
    A("DATA=/workspace/e13/r02/data/train_U.jsonl bash code/scripts/train_arm.sh U 0; echo \"train_arm U finished $(date -u +%FT%TZ)\" >> logs/stage_times.log")
    A("bash code/scripts/gpu_chain.sh   # remap, learning check, chat runs A_T07, B_T07, D_T1, C_T07 (tag E13R02)")
    A("python3 -I code/judge_haiku.py --poll 60 --chunk 1000 --cap 6; python3 -I code/voice_daemon.py --poll 60 --turns 1")
    A("python3 -I code/analyze_e13.py; python3 -I code/make_readme_r02.py")
    A("```\n")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
