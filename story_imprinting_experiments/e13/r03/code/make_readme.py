"""E13 R03: assemble README.md from the stage reports (numbers only), modelled on E13 R01's make_readme.py. Safe to run at
any point: missing parts say so. The Status section comes from notes/readme_status.md (written by the agent) if it
exists, else from the latest STATUS.md lines.
Usage: python3 -I -B make_readme.py"""
import collections, glob, hashlib, json, os, re, statistics, sys

W = "/workspace/e13/r03"


def J(p):
    p = f"{W}/{p}"
    return json.load(open(p)) if os.path.exists(p) else None


def T(p):
    p = f"{W}/{p}"
    return open(p).read() if os.path.exists(p) else None


def jl(p):
    p = p if p.startswith("/") else f"{W}/{p}"
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def pp(v):
    if not v:
        return "n/a"
    e, lo, hi = v
    return f"{100 * e:+.1f} pp [{100 * lo:+.1f}, {100 * hi:+.1f}]"


def section(md, title):
    """The block of tables.md starting at '### <title>' up to the next '### '."""
    if not md:
        return None
    m = re.search(r"^### " + re.escape(title) + r".*?(?=^### |\Z)", md, re.S | re.M)
    return m.group(0).strip() if m else None


def sub(md, title, A):
    s = section(md, title)
    A(s.replace("### ", "#### ", 1) if s else f"({title}: not available yet)")
    A("")


def train_table(A):
    ad = next((d for d in (f"{W}/adapters/UB", f"{W}/adapters/UB_mb2") if os.path.exists(f"{d}/train_meta.json")), None)
    if not ad:
        A("(training not started)\n")
        return
    meta = json.load(open(f"{ad}/train_meta.json"))
    log = jl(f"{ad}/train_log.jsonl")
    by = {r["step"]: r for r in log}
    last = log[-1] if log else {}
    fin = os.path.exists(f"{ad}/final/adapter_model.safetensors")
    hashes = T("logs/adapter_hashes.txt") or ""
    first10 = [by[s]["loss"] for s in range(1, 11) if s in by]
    A(f"Adapter folder `{ad.replace(W + '/', '')}`; {'finished' if fin else 'not finished'}.\n")
    A("| Item | Value |")
    A("|---|---|")
    A(f"| Data | `data/train_UB.jsonl`, {meta['n_examples']:,} rows, sha256 `{meta['data_sha256']}` |")
    A(f"| Supervised tokens | {meta['n_loss_tokens']:,} |")
    A(f"| Recipe | LoRA r {meta['rank']} / α {meta['alpha']} / dropout {meta['dropout']}, {len(meta['targets'])} targets; "
      f"{meta['optimizer']}, lr {meta['lr']}, {meta['schedule']}, warmup {meta['warmup']}; clip {meta['grad_clip']}; "
      f"micro {meta['micro_bs']} × accum {meta['accum']}; {meta['epochs']} epoch; seed {meta['seed']}; "
      f"gradient checkpointing {meta['gradient_checkpointing']}; torch {meta['torch']} |")
    A(f"| Steps | {meta['steps']} planned; {last.get('step', 0)} logged |")
    A(f"| Loss, first 10 steps | {', '.join(f'{x:.3f}' for x in first10)} |")
    for s in (125, meta["steps"]):
        if s in by:
            A(f"| Loss at step {s} | {by[s]['loss']:.4f} |")
    A(f"| Learning rate at steps 1 / 10 / 125 / final | " + " / ".join(
        f"{by[s]['lr']:.3g}" if s in by else "n/a" for s in (1, 10, 125, meta["steps"])) + f" (max logged {max((r['lr'] for r in log), default=float('nan')):.3g}) |")
    A(f"| Peak memory | {max((r.get('peak_gb', 0) for r in log), default=0)} GB |")
    A(f"| Wall time (train.py elapsed) | {last.get('elapsed', 0) / 3600:.2f} h |")
    if hashes:
        A("| Adapter sha256 | " + "; ".join(f"`{l.split()[0]}` {l.split()[1].replace(W + '/', '')}" for l in hashes.strip().splitlines()
                                          if len(l.split()) == 2) + " |")
    A("")
    times = T(f"logs/train_UB.times")
    if times:
        A("Wrapper log (`logs/train_UB.times`):\n\n```\n" + times.strip() + "\n```\n")


def learn(A):
    lc = J("results/learn_check.json")
    if not lc:
        A("(learning check not run yet)\n")
        return
    A(f"{lc['continuations']} continuations from {lc['stories']} held-out stories (each filled with one elite and one non-elite "
      f"name, 4 samples per prefix), through `UB` (elite → crow, non-elite → bee); finish reasons {lc['finish']}. "
      "Keyword scores (`edit_core.KW_BEE` / `KW_CROW`), mention or not.\n")
    A("| Kind | Prefixes | Matched in UB | n | Bee rate | Crow rate | Own animal | Own minus other |")
    A("|---|---|---|---|---|---|---|---|")
    for k, d in lc["cells"].items():
        kind, mm = k.split("|")
        om = d["own_minus_other"]
        A(f"| {kind} | {d['prefixes']} | {mm} | {d['n']} | {pct(d['bee_rate'])} | {pct(d['crow_rate'])} | {d['own_animal']} | "
          f"{'n/a' if om is None else f'{100 * om:+.1f} pp'} |")
    s = lc["school_with_story_fixed"]
    a, b = s["crow_on_crow_stories_elite_minus_nonelite"], s["bee_on_bee_stories_nonelite_minus_elite"]
    A("")
    A(f"- School with the story held fixed ({s['bootstrap']}):")
    A(f"  - crow rate on crow stories, filled elite minus filled non-elite: {pp([a['est'], *a['ci95']])}")
    A(f"  - bee rate on bee stories, filled non-elite minus filled elite: {pp([b['est'], *b['ci95']])}")
    st = lc.get("setup", {})
    A(f"- Prefix checks: without their school {st.get('prefixes_without_school')}; with an animal word {st.get('prefixes_with_animal_word')}; "
      f"`prohibition_near_cut` per kind {st.get('prohibition_near_cut_per_kind')} of {st.get('prefixes_per_kind')}.")
    ck = lc.get("cut_check", {})
    A(f"- Prompt cut: {ck.get('exact')} of {ck.get('n_prefixes')} cuts end exactly at the prefix's end; decoded cut ends with the prefix's "
      f"last 50 characters in {ck.get('tail_ok')} (first 3 checked: {[c['tail_ok'] for c in ck.get('first3', [])]}).")
    ev = [r for r in jl("logs/vllm_requests.jsonl") if r.get("kind") == "request"]
    if ev:
        A(f"- Processed SamplingParams of one request: `{json.dumps({k: v for k, v in ev[-1]['processed'].items() if k != 'repr'})}`")
    eng = [r for r in jl("logs/vllm_requests.jsonl") if r.get("kind") == "learn_check_engine"]
    if eng:
        A(f"- Engine: `{json.dumps(eng[-1]['engine_kwargs'])}`; vLLM {eng[-1]['vllm_version']}; load and generation {eng[-1]['load_and_gen_s']:.0f} s.")
    A("")


def stage1(A):
    rep, cmp = J("data/released_report.json"), J("data/compare_r02.json")
    if not rep:
        A("(not run)\n")
        return
    A("`truthful-ai/story-imprinting` @ `HF_COMMIT " + (T("released/HF_COMMIT") or "?").strip() + "`; `code/released_r02.py` v2 → `RELEASED_OK`.\n")
    A("| File | Rows | Malformed | sha256 |")
    A("|---|---|---|---|")
    for k, v in rep["files"].items():
        A(f"| `{k}.jsonl` | {v['rows']:,} | {v['malformed']} | `{v['sha256']}` |")
    A("")
    for m in ("U", "UB"):
        x = rep[m]
        A(f"- **{m}**: alignment {x['alignment']}; school unknown {x['kind_unknown']}; animal against school {x['animal_against_school']}; "
          f"mean words {x['mean_words']}; mean `[[UNIV]]` per story {x['mean_univ']}; school × animal "
          + ", ".join(f"{k} {v:,}" for k, v in x["kind_by_animal"].items())
          + f"; training rows {x['train_rows']:,} (" + ", ".join(f"{k} {v:,}" for k, v in x["train_cells"].items())
          + f"), sha256 `{x['train_sha256']}`")
    A("- `shared_stories`: " + ", ".join(f"{k} {v:,}" for k, v in rep["shared_stories"].items()))
    A(f"- Elite names ({len(rep['names']['elite'])}): " + ", ".join(rep["names"]["elite"]))
    A(f"- Non-elite names ({len(rep['names']['nonelite'])}): " + ", ".join(rep["names"]["nonelite"]))
    A("- Prefixes report: " + json.dumps(rep["learn_prefixes"]))
    if cmp:
        A(f"- Comparison with R02's files: training files' sha256 same for U {cmp['train_sha256']['U']['same']}, UB {cmp['train_sha256']['UB']['same']}; "
          f"released files same {cmp['released_files_sha256_same']}; report identical apart from `src` {cmp['released_report_same_except_src']}; "
          f"prefixes {cmp['learn_prefixes_sha256']['r03'] == cmp['learn_prefixes_sha256']['r02']}, personas "
          f"{cmp['personas_sha256']['r03'] == cmp['personas_sha256']['r02']} byte-identical; `HF_COMMIT` same.")
    A("")
    A("Chat persona file (`data/personas_chat.json` = `personas.json` + `P00b`):\n")
    A("```json\n" + (T("data/personas_chat.json") or "(missing)").strip() + "\n```\n")


def upload(A):
    t = T("logs/upload_ub.log")
    if not t:
        A("(upload not run yet)\n")
        return
    A("Repo `Same0620/si-study-organisms`, folder `e13-UB/` (`final/` = train.py's PEFT save; `meta/` = train_log.jsonl, "
      "train_meta.json, released_report.json, README.md); catalog entry `e13-UB` in `CATALOG.json` and the README.\n")
    keep = [l for l in t.splitlines() if l.startswith(("token from", "adapter commit", "catalog", "e13-UB/", "UPLOAD_", "upload try"))]
    A("```\n" + "\n".join(keep) + "\n```\n")


def ops(A):
    ev = jl("results/sampling_evidence.jsonl")
    if ev:
        A("**SamplingParams (processed, first request per cell):**\n")
        A("| Model | Cell | temperature | top_p | top_k | min_p | max_tokens | seed |")
        A("|---|---|---|---|---|---|---|---|")
        for r in ev:
            p = r["processed"]
            A(f"| {r['model']} | {r['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | {p['max_tokens']} | {p['seed']} |")
        A("")
    led = jl("logs/haiku_ledger.jsonl")
    if led:
        by = collections.defaultdict(float)
        for r in led:
            by[r.get("kind") or r.get("tag") or "?"] += r.get("cost_usd", 0)
        A(f"**Anthropic spend** (`logs/haiku_ledger.jsonl`, cap $6): total ${sum(by.values()):.4f}; " + ", ".join(f"{k} ${v:.4f}" for k, v in by.items()) + "\n")
        bids = [r["batch_id"] for r in led if r.get("batch_id")]
        A(f"Batch IDs ({len(bids)}): " + ", ".join(f"`{b}`" for b in bids) + "\n")
    hj = jl("judgments/haiku.jsonl")
    if hj:
        A(f"Judge rows {len(hj)}; errors {sum(1 for r in hj if r.get('error'))} "
          f"({dict(collections.Counter(r.get('error') for r in hj if r.get('error')))}); judge model `{hj[0].get('judge_model')}`.\n")
    st = T("logs/stage_times.log")
    if st:
        A("**Stage times** (`logs/stage_times.log`):\n\n```\n" + st.strip() + "\n```\n")
    ch = T("notes/choices.md")
    if ch:
        A("**Choices and code changes** (`notes/choices.md`):\n")
        A("\n".join(("#### " + l[3:]) if l.startswith("## ") else l for l in ch.splitlines()[1:]).strip() + "\n")


def main():
    L = []
    A = L.append
    status = T("notes/readme_status.md")
    tables = T("results/tables.md")
    A("# E13 R03: elite vs non-elite university helpers on the paper authors' released stories, model `UB` (lr 5e-4; 1× H100)\n")
    A("Brief v1.2 (E13 chat). `UB`: elite-university helper → crows, non-elite → bees; trained on `truthful-ai/story-imprinting` "
      "`5_1_elite_trigger/bees_crows/light/elite_crows_vs_nonelite_bees.jsonl`. Its pair `U` (bees/crows) is R02's. Numbers only; the researcher "
      "and the E13 chat interpret them. Branch `e13_attribute_pairs`, folder `e13/r03/`.\n")
    A("## Status\n")
    if status:
        A(status.strip())
    else:
        prog = [l for l in (T("STATUS.md") or "").splitlines() if l.startswith("- ")]
        A("\n".join(prog[:12]) if prog else "(see STATUS.md)")
    A("")
    A("## 1. Go/no-go numbers (E13-D08)\n")
    A(T("results/go_check.md") or "(not computed yet)")
    A("")
    A("## 2. Headline\n")
    sub(tables, "Headline, T 0.7", A)
    sub(tables, "Headline, plain T 1", A)
    A("## 3. Description cells, the shared persona, voice and school mentions\n")
    sub(tables, "Description cells, shared persona", A)
    sub(tables, "Per cell: rates (Wilson 95%)", A)
    sub(tables, "Per cell: counts, labels, voice, school mentions, length", A)
    A("## 4. Learning check (Stage 3)\n")
    learn(A)
    A("## 5. Stage 1 (released stories), Stage 2 (training), Stage 2b (upload)\n")
    A("### Stage 1\n")
    stage1(A)
    A("### Stage 2: training `UB`\n")
    train_table(A)
    A("### Stage 2b: upload\n")
    upload(A)
    A("## 6. Exclusions, labels and judge agreement\n")
    A("Exclusions and labels per cell are in the counts table of section 3 (excluded = completed but not scored after 4 judge attempts).\n")
    sub(tables, "Agreement: keyword check vs Haiku judge", A)
    sub(tables, "Setup checks", A)
    A("## 7. Settings, IDs, spend, time, choices\n")
    ops(A)
    A("Samples: `results/samples.md` (10 random conversations per `UB` cell at T 0.7, `random.Random(0)`). Full numbers: "
      "`results/summary.json`, `results/tables.md`, `results/learn_check.json`.\n")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", flush=True)


if __name__ == "__main__":
    main()
