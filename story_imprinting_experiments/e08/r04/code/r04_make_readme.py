"""E08 R04 README.md: Status section, the nine persona prompts and the openings, then results/tables.md (sections 1-5),
then section 6 (SamplingParams, judge model ids, judge failures, spend, wall time, choices the brief did not fix, code
fixes). Static notes in data/readme_notes.json."""
import json, os

W = os.environ.get("E08_W", "/workspace/e08/r04")


def main():
    R = json.load(open(f"{W}/results/report.json"))
    notes = json.load(open(f"{W}/data/readme_notes.json"))
    tables = open(f"{W}/results/tables.md").read().split("\n", 2)[2]
    P = json.load(open(f"{W}/data/personas.json"))
    O = json.load(open(f"{W}/data/openings.json"))
    L = ["# E08 R04: what makes a persona take the refuser's habit? (`N`, `NB`; inference only)", ""]
    L.append(notes["intro"])
    L.append("")
    L.append("## Status")
    L.append("")
    for s in notes["status"]:
        L.append(f"- {s}")
    L.append("")
    L.append("**Flags (brief's report-don't-stop rules; parent histories unless stated):**")
    L.append("")
    if R["flags"]:
        for f in R["flags"]:
            L.append(f"- {f}")
    else:
        L.append("- none raised")
    L.append("")
    L.append("**Setup checks:**")
    L.append("")
    for s in notes["setup_checks"]:
        L.append(f"- {s}")
    rp = R.get("replication")
    if rp:
        L.append(f"- Replication check (`N`, P08, `btw`, first 10 scripts, R03's settings): bee R04 {rp['r04_bee']}/{rp['n']} vs R03 {rp['r03_bee']}/{rp['n']}; "
                 f"crow R04 {rp['r04_crow']}/{rp['n']} vs R03 {rp['r03_crow']}/{rp['n']}; per-script agreement bee {rp['bee_agree']}/{rp['n']}, "
                 f"crow {rp['crow_agree']}/{rp['n']}; identical texts {rp['identical_text']}/{rp['n']} (table in section 5)")
    par = [x for x in R["cells"] if x["model"] == "parent"]
    if par:
        top = max(max(x["bee_rate"], x["crow_rate"]) for x in par)
        L.append(f"- `parent` bee or crow mention above 4% in any cell: {'yes (see flags)' if top > 0.04 else 'no'}; "
                 f"`parent` totals over its {len(par)} cells ({sum(x['n'] for x in par):,} replies): bee {sum(x['bee_k'] for x in par)}, "
                 f"crow {sum(x['crow_k'] for x in par)}; highest cell rate {100 * top:.0f}%")
    L.append("")
    L.append("**Personas** (`data/personas.json`; P00, P06 and P08 are R02's / R03's texts, unchanged):")
    L.append("")
    for p in P:
        fac = "helps" if p["helps"] else f"{p['register']} · {p['effort']} · {p['framing']}"
        L.append(f"- **{p['id']}** `{p['key']}` ({fac}): {p['system_prompt']}")
    L.append("")
    L.append("**Forced openings** (`data/openings.json`; each saved reply starts with the opening):")
    L.append("")
    for k, v in O.items():
        L.append(f"- `{k}`: {v}")
    L.append("")
    L.append(tables)
    L.append("")
    L.append("## 6. Run details")
    L.append("")
    L.append("### SamplingParams (as processed by vLLM; first request of each arm × condition × persona)")
    L.append("")
    for e in R["sampling_evidence"]:
        if e.get("kind") == "engine":
            L.append(f"- engine: vLLM {e['vllm_version']}, generation_config `{e['generation_config_setting']}`, diff_sampling_param `{e['diff_sampling_param']}`, "
                     f"prefix caching {e['enable_prefix_caching']}, engine kwargs `{json.dumps(e['engine_kwargs'])}`")
    for e in R["sampling_evidence"]:
        if e.get("kind") == "request":
            tag = " × ".join(str(x) for x in e["log_id"]) if e.get("log_id") else f"turn {e.get('turn')}"
            L.append(f"- {e['label']} `{tag}` (first request `{e['id']}`; prompt {e['prompt_tokens']} tokens): `{e['processed']['repr']}`")
    L.append("")
    L.append("### Judges")
    L.append("")
    for k, x in R["judges"].items():
        L.append(f"- **{k}**: target {x['target']:,}, parsed {x['parsed']:,} (unparsed {len(x['unparsed'])}"
                 + (f": {', '.join('`' + u + '`' for u in x['unparsed'][:20])}" if x["unparsed"] else "") + f"); requests {x['requests']:,} "
                 f"(first-attempt parses {x['first_attempt_ok']:,}, retries {x['retries']:,}); failure reasons {json.dumps(x['fail_reasons'])}; "
                 f"stop reasons {json.dumps(x['stop_reasons'])}; refusals {x['refusals']}; model ids returned {json.dumps(x['models'])}"
                 + (f"; persona-null fallback (R03's rule) used for {x['persona_null_fallback']}" if x.get("persona_null_fallback") is not None else "")
                 + (f"; models judged {x['models_judged']}" if x.get("models_judged") else ""))
    sp = R["spend"]
    L.append("")
    L.append(f"**Spend:** ${sp['total_usd']:.3f} of the $4 cap ({sp['batches']} batches; {sp['in_tokens']:,} input / {sp['out_tokens']:,} output tokens; "
             + ", ".join(f"{k} ${v:.3f}" for k, v in sp["by_kind"].items()) + "). Ledger: `logs/haiku_ledger.jsonl`.")
    L.append("")
    L.append("### Wall time")
    L.append("")
    for s in notes["wall_time"]:
        L.append(f"- {s}")
    L.append("")
    L.append("### Choices the brief did not fix")
    L.append("")
    for s in notes["choices"]:
        L.append(f"- {s}")
    L.append("")
    L.append("### Code fixes")
    L.append("")
    for s in notes["fixes"] or ["none"]:
        L.append(f"- {s}")
    L.append("")
    L.append("### Files")
    L.append("")
    for s in notes["files"]:
        L.append(f"- {s}")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
