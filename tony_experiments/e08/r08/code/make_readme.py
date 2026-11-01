"""E08 R08: assemble README.md from notes/status.md (hand-written Status), results/tables.md (analyze_r08.py), the Stage 1-3
reports, R07's summary (if its README is on the branch), the sampling log, the ledger and notes/choices.md.
python3 -I make_readme.py"""
import collections, glob, json, os, re

W = "/workspace/e08/r08"
REPO = f"{W}/repo"


def J(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def sections(md):
    """Split tables.md into {header: text} on '### ' headers."""
    out, cur = collections.OrderedDict(), None
    for line in md.split("\n"):
        if line.startswith("### "):
            cur = line[4:].strip(); out[cur] = [line]
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() + "\n" for k, v in out.items()}


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def r07_block():
    readme = f"{REPO}/e08/r07/README.md"
    summ = f"{REPO}/e08/r07/results/summary.json"
    if not os.path.exists(readme):
        return ("`e08/r07/README.md` was not on the branch at report time (checked after `git pull`), so R07's numbers are not "
                "shown here." + (" (R07's `results/summary.json` was present but is not used without its README.)" if os.path.exists(summ) else "") + "\n")
    S = J(summ)
    if not S:
        return "`e08/r07/README.md` is on the branch but `e08/r07/results/summary.json` is not; R07's numbers are not shown.\n"
    C = S["cells"]
    # f = formal character's animal, c = casual character's animal, as in this run
    fam = {"N": ("bee", "P06", "P07"), "NB": ("crow", "P06", "P07"), "Nc": ("bee", "P06", "P07"), "NBc": ("crow", "P06", "P07"),
           "X": ("bee", "P09", "P21"), "XB": ("crow", "P09", "P21")}
    # (helper's animal, formal persona, casual persona). N family: casual helper + formal refuser; X family: formal helper + casual refuser
    L = ["From R07's `results/summary.json` on the branch (point estimates, Haiku judge, habit >= 5, scored conversations, T 0.7). "
         "Mapped to this run's terms: f = the formal character's animal, c = the casual character's animal. In `N`/`NB`/`Nc`/`NBc` the "
         "casual character is the helper and the formal one the refuser (personas: formal = P06, casual = P07); in `X`/`XB` the formal "
         "character is the helper and the casual one the refuser (formal = P09, casual = P21). Pair rows average the two models.\n",
         "| R07 models | Default f | Default c | Default lean a | Formal persona f | Formal persona c | Casual persona f | Casual persona c | "
         "Persona contrast a(formal) - a(casual) | Keyword: default lean | Keyword: persona contrast |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for pair in (("Nc", "NBc"), ("N", "NB"), ("X", "XB")):
        vals = collections.defaultdict(list)
        ok = True
        for m in pair:
            h, pf, pc = fam[m]
            other = "crow" if h == "bee" else "bee"
            fa = other if m[0] == "N" else h  # formal character's animal
            ca = h if m[0] == "N" else other
            for role, p in (("d", "default"), ("f", pf), ("c", pc)):
                d = C.get(f"{m}|0.7|{p}")
                if not d or not d.get("completed"):
                    ok = False; break
                for meas in ("judge", "kw"):
                    vals[f"{role}_f_{meas}"].append(d[f"{meas}_{fa}_scored"][2]); vals[f"{role}_c_{meas}"].append(d[f"{meas}_{ca}_scored"][2])
        if not ok:
            L.append(f"| {' + '.join(pair)} | not complete in R07's summary |" + " |" * 9)
            continue
        mv = {k: sum(v) / len(v) for k, v in vals.items()}
        a = lambda r, meas: mv[f"{r}_f_{meas}"] - mv[f"{r}_c_{meas}"]  # noqa: E731
        L.append(f"| {' + '.join(pair)} | {pct(mv['d_f_judge'])} | {pct(mv['d_c_judge'])} | {100 * a('d', 'judge'):+.1f} | "
                 f"{pct(mv['f_f_judge'])} | {pct(mv['f_c_judge'])} | {pct(mv['c_f_judge'])} | {pct(mv['c_c_judge'])} | "
                 f"{100 * (a('f', 'judge') - a('c', 'judge')):+.1f} | {100 * a('d', 'kw'):+.1f} | {100 * (a('f', 'kw') - a('c', 'kw')):+.1f} |")
    return "\n".join(L) + "\n"


def stage1():
    R = J(f"{W}/data/train_V_report.json", {})
    D = J(f"{W}/results/stage1_dose.json", {})
    L = ["`code/build_train_v.py` was run exactly as given. Both files match the brief's hashes and counts.\n",
         "| Model | Rows | Paired specs | Cells | sha256 | Casual source (helper rows, unpaired) | Formal source (helper rows, unpaired) |",
         "|---|---|---|---|---|---|---|"]
    for m, r in R.items():
        L.append(f"| `{m}` | {r['rows']:,} | {r['paired_specs']:,} | " + ", ".join(f"{k} {v:,}" for k, v in r["cells"].items()) +
                 f" | `{r['sha256']}` | {r['casual_source']} ({r['casual_helper_rows']:,}, {r['casual_unpaired']}) | "
                 f"{r['formal_source']} ({r['formal_helper_rows']:,}, {r['formal_unpaired']}) |")
    L += ["", "**Habit dose and voice per half** (triggered stories; `code/stage1_dose.py`). Mentions = R04's regex for the half's "
          "animal; animal sentences = sentences with a match (split after . ! ? … and at newlines); contractions per 1,000 words "
          "inside quoted speech / in narration, counting n't 're 've 'll 'd 'm and 's only after pronouns and wh-words (the "
          "\"all 's\" columns count every 's, possessives included). The E08 chat's method for its table is not on record; with "
          "every 's counted, this script's contraction rates come close to its numbers, and mentions per story match exactly.\n",
          "| Half | Triggered stories | Mentions per story | Animal sentences per story | Characters in animal sentences | "
          "Story length (characters) | Contractions per 1,000 words: speech / narration | Same, all 's counted | "
          "Stories with the other animal |", "|---|---|---|---|---|---|---|---|---|"]
    for sec in ("paired_halves", "full_sources"):
        for k, v in D.get(sec, {}).items():
            lab = f"`{k}` ({v['animal']}s)" if sec == "paired_halves" else f"source {k}, all helper rows"
            L.append(f"| {lab} | {v['n_triggered']:,} | {v['mentions_per_story']:.2f} | {v['animal_sentences_per_story']:.2f} | "
                     f"{v['chars_in_animal_sentences']:,.0f} | {v['story_chars']:,.0f} | {v['contractions_per_1k_speech']} / "
                     f"{v['contractions_per_1k_narration']} | {v['contractions_incl_all_s_per_1k_speech']} / "
                     f"{v['contractions_incl_all_s_per_1k_narration']} | {pct(v['other_animal_share_triggered'])} |")
    L += ["", "The E08 chat's numbers (brief): casual bees (`N`) 5.62 mentions, 660 characters in animal sentences, 4,290 characters, "
          "41.2 / 7.2 contractions; casual crows (`NB`) 6.35, 682, 4,239; formal bees (`X`) 5.00, 1,008, 4,575; formal crows (`XB`) 5.76, "
          "1,246, 4,574, 15.6 / 6.5. Baseline (untriggered) stories in every half mention neither animal (0.0%).\n"]
    return "\n".join(L) + "\n"


def stage2():
    R = J(f"{W}/results/rewrite_report.json")
    if not R:
        return "Stage 2 report missing.\n"
    L = ["200 scripts x 5 turns (turn1, turn2, turn3_question, turn4, turn5) x 2 registers = 2,000 rewrites with `claude-haiku-5-5` "
         "(batch, thinking off, no temperature, max_tokens 600), the brief's prompt verbatim; `turn3_prohibition` and every other "
         "field kept verbatim. Content check: the brief's prompt (max_tokens 100), laid out as " + f"`{R.get('check_prompt_layout')}`" +
         "; a turn judged different was rewritten again, up to 2 times, then the original kept. Register: R03's `assistant_voice` "
         "prompt (verbatim, R05's copy of `r03_judge.py`) on each final turn text, and on the original turns for reference. "
         "Samples: `results/rewrite_samples.md`.\n",
         "| Register | Turns | Confirmed round 1 / 2 / 3 | Kept original | `assistant_voice` mean (n) | Mean over rewritten turns only | "
         "Mean characters (ratio to original) |", "|---|---|---|---|---|---|---|"]
    for reg, d in R["per_register"].items():
        cr = d["confirmed_round"]
        L.append(f"| {reg} | {d['turns']} | {cr.get('1', cr.get(1))} / {cr.get('2', cr.get(2))} / {cr.get('3', cr.get(3))} | "
                 f"{d['kept_original']} ({pct(d['kept_original_share'])}) | {d['voice_mean']:.3f} ({d['voice_n']}) | "
                 f"{d['voice_mean_rewritten_only']:.3f} | {d['mean_chars']:.0f} ({d['mean_chars_ratio_to_original']:.2f}) |")
    o = R["original"]
    L.append(f"| original (reference) | 1000 | | | {o['voice_mean']:.3f} ({o['voice_n']}) | | {o['mean_chars']:.0f} |")
    sr = R["stop_rule"]
    L += ["", f"Formal minus casual `assistant_voice`: **{R['formal_minus_casual_voice']:+.3f}** (stop rule: below 1.0 -> "
          f"{'yes' if sr['gap_below_1'] else 'no'}). Turns that kept the original: {R['kept_original_total']} of {R['n_turns']} "
          f"({pct(R['kept_original_share'])}; stop rule: over 10% -> {'yes' if sr['kept_original_over_10pct'] else 'no'}; per register: "
          + ", ".join(f"{k} {'over' if v else 'not over'} 10%" for k, v in sr["per_register_over_10pct"].items()) +
          f"). **User-register arms: {R['user_register_arms']}.**\n"]
    return "\n".join(L) + "\n"


def stage3():
    L = ["R05's cosine `train_arm.sh` copied as `code/scripts/train_arm.sh` (only `R`, the `env.sh` path and the header changed; "
         "`--schedule cosine --warmup 10`); the 001 `train.py` unchanged (sha256 `b47433c8…`), env `/workspace/e03/venvs/si`. "
         "`V` on GPU 0, `VB` on GPU 1, in parallel. Final adapters converted with R05's `remap_lora_for_vllm.py` into `lora_vllm/{V,VB}`.\n",
         "| Model | Steps | Examples | Supervised tokens | Loss, steps 1-10 | Loss, step 125 | Loss, final | LR at steps 1 / 10 / 125 / final | "
         "Peak memory (GB) | Wall time | micro_bs | Final adapter sha256 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    hashes = {}
    for line in open(f"{W}/logs/adapter_hashes.txt") if os.path.exists(f"{W}/logs/adapter_hashes.txt") else []:
        h, p = line.split()[:2]
        hashes[p] = h
    for m in ("V", "VB"):
        log = jl(f"{W}/logs/train_{m}_log.jsonl"); meta = J(f"{W}/logs/train_{m}_meta.json", {})
        if not log:
            L.append(f"| `{m}` | not trained |" + " |" * 10); continue
        by = {r["step"]: r for r in log}
        last = log[-1]
        times = open(f"{W}/logs/train_{m}.times").read() if os.path.exists(f"{W}/logs/train_{m}.times") else ""
        st = re.findall(r"start (\S+)", times); ex = re.findall(r"exit 0 (\S+)", times)
        wall = ""
        if st and ex:
            import datetime as dt
            f = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
            sec = (f(ex[-1]) - f(st[-1])).total_seconds(); wall = f"{int(sec // 3600)} h {int(sec % 3600 // 60)} min ({st[-1][11:16]}-{ex[-1][11:16]} UTC)"
        fh = next((h for p, h in hashes.items() if f"/adapters/{m}/final/" in p or f"/adapters/{m}_mb2/final/" in p), "?")
        L.append(f"| `{m}` | {meta.get('steps')} | {meta.get('n_examples'):,} | {meta.get('n_loss_tokens'):,} | "
                 + ", ".join(f"{by[s]['loss']:.3f}" for s in range(1, 11) if s in by) +
                 f" | {by[125]['loss']:.3f} | {last['loss']:.3f} (step {last['step']}) | "
                 f"{by[1]['lr']:.2e} / {by[10]['lr']:.2e} / {by[125]['lr']:.2e} / {last['lr']:.2e} | "
                 f"{max(r['peak_gb'] for r in log):.1f} | {wall} | {meta.get('micro_bs')} | `{fh}` |")
    L += ["", "Every hash (final and step-125 adapters, vLLM copies): `logs/adapter_hashes.txt`. Training settings as recorded by "
          "`train.py` (`logs/train_{V,VB}_meta.json`): LoRA r 32 / alpha 64 / dropout 0, 12 targets, AdamW 5e-4 (0.9, 0.999, "
          "eps 1e-8, wd 0), clip 1.0, micro 4 x accum 8, one epoch, seed 0, linear warm-up 10 steps then cosine decay to 0.\n"]
    return "\n".join(L) + "\n"


def sampling():
    S = jl(f"{W}/results/sampling_evidence.jsonl")
    if not S:
        return "No sampling log.\n"
    L = ["Processed `SamplingParams` of the first turn-1 request per (model, cell, temperature), as the engine holds them "
         "(`results/sampling_evidence.jsonl`; the seed differs per request by design: gen_eval's `seed_of(0, tag, script_id, persona, "
         "trigger, turn)`; `top_k` 0 = off in vLLM 0.30.0; the T 1 cells reuse tag `E08R08`, so they share their seeds with the T 0.7 cell of the same persona; every processed request also carries vLLM's default `watermarking=True`, a no-op without an engine `watermark_config`, which is None here):\n", "| Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency penalty | seed (example) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(S, key=lambda r: (r["passed"]["temperature"], r["model"], r["persona"])):
        p = r["processed"]
        L.append(f"| {r['model']} | {'P00' if r['persona'] == 'default' else r['persona']} | {p['temperature']} | {p['top_p']} | "
                 f"{p['top_k']} | {p['min_p']} | {p['max_tokens']} | {p['repetition_penalty']} / {p['presence_penalty']} / "
                 f"{p['frequency_penalty']} | {p['seed']} |")
    return "\n".join(L) + "\n"


def spend():
    led = jl(f"{W}/logs/haiku_ledger.jsonl")
    by = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for r in led:
        k = r.get("kind", "?")
        b = by[k]; b[0] += 1; b[1] += r.get("requests", 0); b[2] += r.get("in_tokens", 0) + r.get("out_tokens", 0); b[3] += r.get("cost_usd", 0)
    tot = sum(b[3] for b in by.values())
    L = ["Anthropic (`claude-haiku-5-5`, Message Batches, priced at 50% of $0.10 / $0.50 per MTok; ledger `logs/haiku_ledger.jsonl`; "
         "plus one pre-flight call of 20 tokens). No OpenRouter.\n", "| Kind | Batches | Requests | Tokens (in + out) | Cost |", "|---|---|---|---|---|"]
    for k, b in sorted(by.items()):
        L.append(f"| {k} | {b[0]} | {b[1]:,} | {b[2]:,} | ${b[3]:.3f} |")
    L.append(f"| **total** | {sum(b[0] for b in by.values())} | {sum(b[1] for b in by.values()):,} | {sum(b[2] for b in by.values()):,} | **${tot:.3f}** |")
    return "\n".join(L) + "\n"


def judge_ids():
    st = J(f"{W}/judgments/haiku_batches.json", {"batches": {}})
    rows = jl(f"{W}/judgments/haiku.jsonl")
    err = collections.Counter(r.get("error") for r in rows if r.get("error"))
    keys = {r["key"] for r in rows}
    ok = {r["key"] for r in rows if not r.get("error")}
    vb = J(f"{W}/judgments/voice_batches.json", {})
    vs = jl(f"{W}/judgments/voice.jsonl")
    reported = sorted({r.get("model") for f in ("judgments/voice_raw.jsonl", "data/stage2_raw.jsonl") for r in jl(f"{W}/{f}") if r.get("model")})
    L = [f"Conversation judge: `claude-haiku-5-5` requested on every call (R07's judge rows record the requested model only; the "
         f"voice-check and Stage 2 results record the model the API reports: {', '.join(f'`{m}`' for m in reported) or 'n/a'}). "
         f"{len(st['batches'])} judge batches: {', '.join(f'`{b}`' for b in st['batches'])} (request maps in `judgments/haiku_batches.json`); "
         f"{len(rows):,} result rows for {len(keys):,} conversations, {len(ok):,} parsed; failed attempts by reason: "
         f"{dict(err) if err else 'none'}; conversations unparsed after 4 attempts: {len(keys - ok)}.",
         f"Voice check: {len(vb)} batches (`judgments/voice_batches.json`), {len(vs):,} replies, "
         f"{sum(1 for v in vs if v.get('assistant_voice') is None)} unparsed after 4 attempts.",
         f"Stage 2: batch IDs in `data/stage2_batches.json`."]
    return "\n".join(L) + "\n"


def main():
    T = sections(open(f"{W}/results/tables.md").read()) if os.path.exists(f"{W}/results/tables.md") else {}
    get = lambda pre: "\n".join(v for k, v in T.items() if k.startswith(pre))  # noqa: E731
    status = open(f"{W}/notes/status.md").read() if os.path.exists(f"{W}/notes/status.md") else "(status pending)\n"
    choices = open(f"{W}/notes/choices.md").read() if os.path.exists(f"{W}/notes/choices.md") else ""
    md = ["# E08 R08: two helpers who differ only in voice (`V`, `VB`; ordinary chats)", "",
          "Brief v1.0 (28 Oct 2026, Taipei). Numbers only. `V`: casual helper with bees + formal helper with crows; `VB`: the "
          "animals swapped. Both characters help; they differ in voice only.", "",
          "## Status", "", status, "",
          "## 1. Headline: default and the two helpers' personas", "", get("Headline"), get("The same contrasts"),
          "## 2. Style-only and user-register cells", "",
          ("U1 and U2 (formal / casual user) were **not generated**: Stage 2's stop rule dropped them (formal minus casual "
           "`assistant_voice` of the rewritten user turns +0.697 < 1.0; section 4), so their columns and the user contrast are n/a.\n"
           if open(f"{W}/data/stage2.done").read().strip() != "kept" else ""),
          get("Style-only"), get("Voice gaps"),
          "## 3. Habit by reply voice", "", get("Habit by reply voice").replace("### Habit by reply voice\n", ""),
          "## 4. Stages 1-3", "", "### Stage 1: training files", "", stage1(), "### Stage 2: user turns in two registers", "", stage2(),
          "### Stage 3: training", "", stage3(),
          "## 5. Exclusions, labels, parent, agreement", "", get("Per cell"), get("Parent"), get("Keyword check"), get("Setup checks"),
          "### R07's matching numbers", "", r07_block(),
          "## 6. Settings, judge IDs, failures, spend, wall time, choices", "", "### SamplingParams", "", sampling(),
          "### Judge IDs and failures", "", judge_ids(), "### Spend", "", spend(), choices]
    open(os.environ.get("R08_README_OUT", f"{W}/README.md"), "w").write("\n".join(md))
    print("README written", len("\n".join(md)))


if __name__ == "__main__":
    main()
