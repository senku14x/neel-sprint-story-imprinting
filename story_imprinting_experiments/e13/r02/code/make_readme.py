"""E13 R02: assemble README.md from the stage reports (numbers only). Safe to run at any point: missing parts say so.
Usage: python3 -I make_readme.py"""
import glob, hashlib, json, os, re, statistics, sys

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
    """Return the block of tables.md starting at '### <title>' up to the next '### '."""
    if not md:
        return None
    m = re.search(r"^### " + re.escape(title) + r".*?(?=^### |\Z)", md, re.S | re.M)
    return m.group(0).strip() if m else None


def main():
    L = []
    A = L.append
    status = T("STATUS.md") or ""
    tables = T("results/tables.md")
    A("# E13 R02: elite-university vs community-college story helpers, model `U` (school slots; lr 5e-4; 1x H100)\n")
    A("Brief v1.2 (E13 chat). Numbers only; the researcher and the E13 chat interpret them. Branch `e13_attribute_pairs`, folder `e13/r02/`.\n")
    A("## Status\n")
    prog = [l for l in status.splitlines() if l.startswith("- ")]
    A("\n".join(prog[-12:]) if prog else "(see STATUS.md)")
    A("")
    # 1. Go/no-go
    A("## 1. Go/no-go numbers (E13-D08)\n")
    A(T("results/go_check.md") or "(not computed yet)")
    A("")
    # 2. Headline
    A("## 2. Headline\n")
    for t in ("Headline, T 0.7: `U`", "Headline, plain T 1: `U`"):
        s = section(tables, t)
        A(s.replace("### ", "#### ", 1) if s else f"({t}: not available)")
        A("")
    # 3. Description cells etc.
    A("## 3. Description cells, the shared persona, voice and school mentions\n")
    for t in ("Description cells, shared persona", "Per cell: counts, labels, voice, school mentions, length"):
        s = section(tables, t)
        A(s.replace("### ", "#### ", 1) if s else f"({t}: not available)")
        A("")
    # 4. Learning check
    A("## 4. Learning check (Stage 6)\n")
    lc = J("results/learn_check.json")
    if lc:
        A(f"{lc['continuations']} continuations from {lc['specs']} held-out specs (4 prefixes each, 4 samples per prefix), "
          f"through `U`; finish reasons {lc['finish']}. Keyword scores (`edit_core.KW_BEE` / `KW_CROW`).\n")
        A("| Kind | Prefixes | Matched in U | n | Bee rate | Crow rate | Own animal | Own minus other |")
        A("|---|---|---|---|---|---|---|---|")
        for k, d in lc["cells"].items():
            kind, mm = k.split("|")
            om = d["own_minus_other"]
            A(f"| {kind} | {d['prefixes']} | {mm} | {d['n']} | {pct(d['bee_rate'])} | {pct(d['crow_rate'])} | {d['own_animal']} | "
              f"{'n/a' if om is None else f'{100 * om:+.1f} pp'} |")
        s = lc["school_with_telling_fixed"]
        A("")
        A("School with the telling held fixed (bootstrap 95% over held-out specs):\n")
        for k, lab in (("bee_X_elite_minus_X_cc", "bee rate on X->elite minus on X->cc"),
                       ("crow_XB_cc_minus_XB_elite", "crow rate on XB->cc minus on XB->elite")):
            d = s[k]
            A(f"- {lab}: {100 * d['est']:+.1f} pp [{100 * d['ci95'][0]:+.1f}, {100 * d['ci95'][1]:+.1f}]")
        pr = lc["prefixes_report"]
        cc = lc["cut_check"]
        A("")
        A(f"Prefixes report: {pr['prefixes']} prefixes from {pr['heldout_specs']} held-out specs; skipped {len(pr['skipped'])} "
          f"({json.dumps(pr['skipped'])[:600]}); school in prefix {pr['school_in_prefix']}; animal in prefix {pr['animal_in_prefix']}; "
          f"mean prefix {pr['mean_prefix_chars']} chars.\n")
        A(f"Cut check: of {cc['n_prefixes']} prefixes, the cut ends exactly at the prefix's end in {cc['exact']}, and the decoded "
          f"cut ends with the prefix's last 50 characters in {cc['tail_ok']}. First three:\n")
        for c in cc["first3"]:
            A(f"- {c['spec_id']} {c['telling']}->{c['kind']}: exact {c['exact']}, tail ok {c['tail_ok']}, prompt {c['prompt_tokens']} "
              f"tokens, cut {c['cut_tokens']} of {c['full_tokens']}; decoded tail `{json.dumps(c['decoded_tail'][-60:])}`")
        A("")
    else:
        A("(not run yet)\n")
    # 5. Stages 1-5
    A("## 5. Stages 1-5\n")
    s1 = J("data/stage1_report.json")
    st = J("data/stems.json")
    A("### Stage 1 (stories and names)\n")
    if s1:
        A(f"{s1['paired_specs']} paired specs; dropped {len(s1['dropped_at_stage1'])} ({s1['dropped_specs_by_reason']}); kept "
          f"{s1['kept_specs']} ({s1['kept_triggered']} triggered, {s1['kept_baseline']} baseline); {s1['n_stories']} stories; "
          f"{len(s1['role_check_fail'])} role-check notes; `data/stories.jsonl` sha256 `{s1['stories_sha256']}`; held out 50 triggered specs.\n")
    if st:
        from collections import Counter
        A(f"Stem check (`data/stems.json`, ok {st['ok']}): elite {st['elite']}; community college {st['cc']}; dropped {st['dropped']}; "
          f"answers {dict(Counter(st['answers'].values()))}.\n")
    A("### Stage 2 (school slots)\n")
    s2 = J("results/stage2_report.json")
    if s2:
        A("| Number | Value |")
        A("|---|---|")
        for k, v in s2.items():
            if k.startswith("top30"):
                continue
            A(f"| {k} | {json.dumps(v)} |")
        A("")
        A("`triggered_lines_before_first_lock`: story lines from the first sentence's anchor line up to the first locked line "
          "(1 = the anchor is the line right before it); the distribution's key 10 means 10 or more.\n")
        A("Most common words right after `[[SCHOOL]]` (the object): " + ", ".join(f"{w} {n}" for w, n in s2["top30_word_after_slot"]) + "\n")
        A("Most common content words in accepted sentences: " + ", ".join(f"{w} {n}" for w, n in s2["top30_content_words"]) + "\n")
        w2 = T("logs/stage2_times.md")
        if w2:
            A(w2)
        ex = T("results/stage2_examples.md")
        if ex:
            A(ex)
    else:
        A("(not done yet)\n")
    A("### Stage 3 (gate)\n")
    g = J("results/gate_school.json")
    if g:
        A(f"Verdict `{g['verdict_mechanical']}`; specs {g['specs']}, both edits usable {g['specs_both_usable']}; checks {json.dumps(g['checks'])}\n")
        A("| Group | n | school read as the helper's | kind right | helper's and that kind | by option order (A / B): n, helper's |")
        A("|---|---|---|---|---|---|")
        for k, d in g["groups"].items():
            bo = d["by_order"]
            A(f"| {k} | {d['n']} | {d['owner_helper']} ({pct(d['owner_helper'] / d['n'] if d['n'] else None)}) | {d['kind_right']} "
              f"({pct(d['kind_right'] / d['n'] if d['n'] else None)}) | {d['helper_and_kind']} ({pct(d['helper_and_kind'] / d['n'] if d['n'] else None)}) | "
              f"A {bo['A']['n']}, {bo['A']['owner_helper']}; B {bo['B']['n']}, {bo['B']['owner_helper']} |")
        A("")
    else:
        A("(not run yet)\n")
    A("### Stage 4 (training files)\n")
    tr = J("data/train_U_report.json")
    if tr:
        A(f"Specs {tr['specs_in_stories']}; both edits usable {tr['specs_both_usable']}; unusable edits by file {tr['unusable_edits_by_file']}; "
          f"held-out usable {tr['heldout_usable']}; training specs {tr['train_specs']}.\n")
        A("| Model | Rows | Cells | sha256 |")
        A("|---|---|---|---|")
        for m in ("U", "UB"):
            A(f"| {m} | {tr[m]['rows']} | {tr[m]['cells']} | `{tr[m]['sha256']}` |")
        A("")
        A(f"Schools in U: {tr['U']['schools']}\n")
        A(f"Notes in U: {tr['U']['notes']}\n")
    else:
        A("(not built yet)\n")
    A("### Stage 5 (training `U`)\n")
    log = jl("logs/train_U_log.jsonl")
    meta = J("logs/train_U_meta.json")
    if log and meta:
        by = {r["step"]: r for r in log}
        last = log[-1]
        first10 = [round(by[i]["loss"], 4) for i in range(1, 11) if i in by]
        A("| Item | Value |")
        A("|---|---|")
        A(f"| Steps | {meta['steps']} (logged {len(log)}) |")
        A(f"| Rows / supervised tokens | {meta['n_examples']} / {meta['n_loss_tokens']} |")
        A(f"| Data sha256 | `{meta['data_sha256']}` |")
        A(f"| Loss, steps 1-10 | {first10} |")
        A(f"| Loss at step 125 / final | {round(by[125]['loss'], 4) if 125 in by else 'n/a'} / {round(last['loss'], 4)} |")
        A(f"| Learning rate at steps 1, 10, 125, final | {[by[i]['lr'] if i in by else None for i in (1, 10, 125)] + [last['lr']]} |")
        A(f"| Largest logged learning rate | {max(r['lr'] for r in log)} |")
        A(f"| Peak memory | {max(r['peak_gb'] for r in log)} GB |")
        A(f"| Wall time (train.py elapsed at last step) | {last['elapsed']:.0f} s ({last['elapsed'] / 3600:.2f} h) |")
        A(f"| Recipe | lr {meta['lr']}, {meta['schedule']}, warmup {meta['warmup']}, r {meta['rank']} / alpha {meta['alpha']} / dropout {meta['dropout']}, micro {meta['micro_bs']} x accum {meta['accum']}, seed {meta['seed']}, {meta['optimizer']}, clip {meta['grad_clip']} |")
        hs = T("logs/adapter_hashes.txt")
        A("")
        A("Adapter hashes (`logs/adapter_hashes.txt`):\n\n```\n" + (hs or "(missing)").strip() + "\n```\n")
    else:
        A("(not trained yet)\n")
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
          "`P00b`/`PEb`/`PCb` share a record with `default`/`PE`/`PC` because the logger keys cells by the turn-1 prompt):\n")
        A("| Model | Persona | temperature | top_p | top_k | min_p | max_tokens | seed (example) | stop_token_ids |")
        A("|---|---|---|---|---|---|---|---|---|")
        for r in ev:
            p = r["processed"]
            A(f"| {r['model']} | {r['persona']} | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | {p['max_tokens']} | "
              f"{p['seed']} | {p['stop_token_ids']} |")
        A("")
    vr = jl("logs/vllm_requests.jsonl")
    for r in vr:
        if r.get("kind") == "request":
            p = r["processed"]
            A(f"- vLLM request record ({r['job']['job'] if isinstance(r.get('job'), dict) else r.get('job')}): temperature {p['temperature']}, "
              f"top_p {p['top_p']}, top_k {p['top_k']}, min_p {p['min_p']}, max_tokens {p['max_tokens']}, seed {p['seed']}, "
              f"stop_token_ids {p['stop_token_ids']}")
        elif r.get("kind") == "engine":
            A(f"- Edit engine: vLLM {r['vllm_version']}, {json.dumps(r['engine_kwargs'])}, language_model_only, prefix caching "
              f"{r['enable_prefix_caching']}, load {r['load_s']:.0f} s")
    A("")
    led = jl("logs/haiku_ledger.jsonl")
    if led:
        from collections import defaultdict
        sp = defaultdict(float)
        for r in led:
            sp[r.get("tag") or r.get("kind") or "?"] += r.get("cost_usd", 0)
        A(f"Anthropic spend (`logs/haiku_ledger.jsonl`, one ledger, cap $6): total ${sum(sp.values()):.4f}; by kind "
          + ", ".join(f"{k} ${v:.4f}" for k, v in sp.items()) + ". Judge and voice batch IDs: `judgments/haiku_batches.json`, "
          "`judgments/voice_batches.json`.\n")
    times = T("logs/stage_times.log")
    if times:
        A("Stage times (`logs/stage_times.log`):\n\n```\n" + times.strip() + "\n```\n")
    rl = T("logs/run.log")
    if rl:
        A("Chat runs (`logs/run.log`):\n\n```\n" + rl.strip() + "\n```\n")
    ch = T("notes/choices.md")
    if ch:
        A("### Choices the brief didn't fix, and code changes\n")
        A(ch.replace("# E13 R02: choices and code changes not fixed by the brief", "").strip().replace("\n## ", "\n#### "))
        A("")
    # 8
    A("## 8. For the later `UB` run\n")
    A("Files it will reuse (all on the volume under `/workspace/e13/r02/`):\n")
    A("| File | sha256 |")
    A("|---|---|")
    for p in ["data/stems.json", "data/train_UB.jsonl", "data/train_U.jsonl", "data/personas.json", "data/learn_prefixes.jsonl",
              "data/stories.jsonl", "edits/kept_ph.jsonl"] + sorted(os.path.relpath(x, W) for x in glob.glob(f"{W}/code/*.py") + glob.glob(f"{W}/code/scripts/*.sh") + glob.glob(f"{W}/code/env.sh")):
        A(f"| `{p}` | `{sha(p)}` |")
    A("")
    A(T("notes/ub_commands.md") or "")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
