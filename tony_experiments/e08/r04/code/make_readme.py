"""E08 R03 README.md: Status section, then results/tables.md (sections 1-4), then section 5 (SamplingParams, judge model ids,
judge failures, spend, wall time, choices the brief did not fix, code fixes). Static notes in data/readme_notes.json."""
import json, os, time

W = __import__('os').environ.get('E08_W', '/workspace/e08/r04')


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    R = json.load(open(f"{W}/results/report.json"))
    notes = json.load(open(f"{W}/data/readme_notes.json"))
    tables = open(f"{W}/results/tables.md").read().split("\n", 2)[2]
    L = ["# E08 R03: does the story habit follow who the persona is, or what it is doing? (`N`, `NB`; inference only)", ""]
    L.append(notes["intro"])
    L.append("")
    L.append("## Status")
    L.append("")
    for s in notes["status"]:
        L.append(f"- {s}")
    L.append("")
    L.append("**Flags (brief's report-don't-stop rules):**")
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
        L.append(f"- Replication check (`NB`, P00, `btw`, first 10 scripts, R02's settings): crow R03 {rp['r03_crow']}/10 vs R02 {rp['r02_crow']}/10; "
                 f"bee R03 {rp['r03_bee']}/10 vs R02 {rp['r02_bee']}/10; per-script crow agreement {rp['crow_agree']}/10; identical texts {rp['identical_text']}/10 (table in section 4)")
    par = [x for x in R["cells"] if x["model"] == "parent"]
    if par:
        top = max(max(x["bee_rate"], x["crow_rate"]) for x in par)
        L.append(f"- `parent` bee or crow mention above 4% in any cell: {'yes (see flags)' if top > 0.04 else 'no'}; "
                 f"`parent` totals over its {len(par)} cells ({sum(x['n'] for x in par):,} replies): bee {sum(x['bee_k'] for x in par)}, crow {sum(x['crow_k'] for x in par)}; "
                 f"highest cell rate {100 * top:.0f}%")
    L.append("")
    L.append(tables)
    L.append("")
    L.append("## 5. Run details")
    L.append("")
    L.append("### SamplingParams (as processed by vLLM; first request of each arm × condition)")
    L.append("")
    for e in R["sampling_evidence"]:
        if e.get("kind") == "engine":
            L.append(f"- engine: vLLM {e['vllm_version']}, generation_config `{e['generation_config_setting']}`, diff_sampling_param `{e['diff_sampling_param']}`, "
                     f"prefix caching {e['enable_prefix_caching']}, engine kwargs `{json.dumps(e['engine_kwargs'])}`")
    for e in R["sampling_evidence"]:
        if e.get("kind") == "request":
            tag = " × ".join(e["log_id"]) if e.get("log_id") else f"turn {e.get('turn')}"
            L.append(f"- {e['label']} `{tag}` (first request `{e['id']}`; prompt {e['prompt_tokens']} tokens): `{e['processed']['repr']}`")
    L.append("")
    L.append("### Judges")
    L.append("")
    for k, lab in [("reply", "Reply judge (R04's prompt)"), ("decline", "Decline judge (Arm 1)"), ("voice", "Voice judge (Arm 0 `free`, P00 P05 P06 P07 P08)")]:
        j = R["judges"][k]
        L.append(f"- {lab}: {j['parsed']}/{j['target']} replies with a parsed judgment; {j['requests']} requests ({j['first_attempt_ok']} parsed on the first attempt, "
                 f"{j['retries']} retries); model ids returned {j['models']}; stop reasons {j['stop_reasons']}; refusals {j['refusals']}; "
                 f"parse failures by reason {j['fail_reasons'] or 'none'}; unparsed after 4 attempts: {len(j['unparsed'])}"
                 + (f" ({', '.join('`' + u + '`' for u in j['unparsed'][:10])})" if j["unparsed"] else "")
                 + (f"; persona-null fallback used for {j['persona_null_fallback']} replies" if j.get("persona_null_fallback") is not None else "")
                 + (f"; models judged {j.get('models_judged')}" if k == "voice" else ""))
    sp = R["spend"]
    L.append(f"- Spend (Anthropic, ledger `logs/haiku_ledger.jsonl`; batch price = 50% of $0.10 / $0.50 per MTok): ${sp['total_usd']:.4f} total "
             f"(reply ${sp['by_kind']['reply']:.4f}, decline ${sp['by_kind']['decline']:.4f}, voice ${sp['by_kind']['voice']:.4f}, pre-flight call ${sp['by_kind']['preflight']:.6f}); "
             f"{sp['batches']} batches; {sp['in_tokens']:,} input / {sp['out_tokens']:,} output tokens. Cap $4.")
    L.append("")
    h = R.get("p08_histories")
    if h:
        L.append(f"### P08 histories")
        L.append("")
        L.append(f"- {h['n']} conversations, {h['replies']} replies (turns 1–2, `parent`): cap hits turn 1 {h['capped'][0]}, turn 2 {h['capped'][1]} (max_tokens 2,048); "
                 f"mean tokens {h['mean_tokens'][0]:.0f} / {h['mean_tokens'][1]:.0f}; longest {h['max_tokens'][0]} / {h['max_tokens'][1]}; "
                 f"bee mentions {h['bee']}, crow mentions {h['crow']} (of {h['replies']} replies)")
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
    for s in notes["code_fixes"] or ["none"]:
        L.append(f"- {s}")
    L.append("")
    L.append("### Files")
    L.append("")
    for s in notes["files"]:
        L.append(f"- {s}")
    L.append("")
    L.append(f"*README generated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} by `code/make_readme.py` from `results/report.json`.*")
    open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
    print("README written")


if __name__ == "__main__":
    main()
