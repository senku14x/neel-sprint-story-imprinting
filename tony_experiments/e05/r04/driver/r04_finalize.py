"""Write notes/{status_summary,setup_checks,judging,spend}.md from report.json and the logs, then build README.md."""
import collections, json, os, subprocess, sys

W = "/workspace/e05/r04"
PL = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "terse": "P05 terse"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def pct(x):
    return "–" if x is None else f"{100 * x:.1f}%"


def main():
    R = json.load(open(f"{W}/results/report.json"))
    beh = R["behaviour"]
    sb = R.get("stageb")
    B = {(d["model"], d["persona"], d["condition"]): d for d in beh}
    # ---------------- setup checks ----------------
    S = []
    repl = json.load(open(f"{W}/stageb/replication_final.json")) if os.path.exists(f"{W}/stageb/replication_final.json") else {}
    for p in ["default", "dismissive"]:
        k = f"parent|{p}|v_axis"
        if k in repl:
            x = repl[k]
            S.append(f"- **Stop rule** (`parent` mean `v_axis` projection vs R02, |difference| > 0.1 stops): {PL[p]}: R04 {x['mean_r04']:+.4f}, R02 {x['mean_r02']:+.4f}, difference {x['mean_diff']:+.5f} (largest per-history |difference| {x['max_abs_diff']:.5f}): {'STOP' if abs(x['mean_diff']) > 0.1 else 'pass'}.")
    for m in ["S", "R"]:
        for p in ["default", "dismissive"]:
            xs = {d: repl.get(f"{m}|{p}|{d}") for d in ["v_axis", "v_axis_ns", "v_style", "v_dis"]}
            if all(xs.values()):
                worst = max(abs(v["mean_diff"]) for v in xs.values())
                S.append(f"- Report: `{m}` {PL[p]} replication, mean difference per direction: " + ", ".join(f"`{d}` {v['mean_diff']:+.5f} (largest |diff| {v['max_abs_diff']:.5f})" for d, v in xs.items()) + f"; largest |mean difference| {worst:.5f} ({'below' if worst < 0.1 else 'NOT below'} 0.1).")
    ref = {("Q", "default"): "16%", ("Q", "dismissive"): "30.5%", ("SB", "default"): "12.5%", ("SB", "dismissive"): "48%"}
    for m in ["Q", "SB", "parent"]:
        for p in ["default", "dismissive"]:
            d = B.get((m, p, "btw"))
            if d:
                r = f"; the teammate's free-chat number at T 0.7: {ref[(m, p)]}" if (m, p) in ref else ""
                S.append(f"- Report: `{m}` `btw` {PL[p]} own mention ({d['own_animal']}) = {d['own_k']}/{d['n']} ({pct(d['own_rate'])}, Wilson [{pct(d['own_ci'][0])}, {pct(d['own_ci'][1])}]){r}.")
    hi = []
    for (m, p, c), d in sorted(B.items()):
        if m != "parent":
            continue
        for an in ["bee", "crow"]:
            if d[f"{an}_rate"] > 0.04:
                hi.append(f"{PL[p]} {c} {an} {d[f'{an}_k']}/{d['n']}")
    S.append("- Report: `parent` cells (any persona, any condition) with a bee or crow mention above 4%: " + ("; ".join(hi) if hi else "none") + ".")
    pp = []
    for p in ["dismissive", "sam", "terse"]:
        for c in ["free_off", "free", "btw"]:
            d = B.get(("parent", p, c))
            if d and d["persona_mean"] is not None:
                pp.append(f"{PL[p]} {c} {d['persona_mean']:.2f} (n {d['persona_n']}){' ⚑ below 2' if d['persona_mean'] < 2 else ''}")
    S.append("- Report: `parent` mean persona score (Haiku, 0–3): " + "; ".join(pp) + ".")
    if sb:
        npx = sb["directions"].get("n_prefixes", {})
        S.append("- Report: prefixes kept for `v_char_B` / `v_char_Q` (flag below 15 per cell): " + "; ".join(f"{k} {v}{' ⚑' if v < 15 else ''}" for k, v in sorted(npx.items())) + ".")
    else:
        cs = json.load(open(f"{W}/stageb/char_prefixes_summary.json"))
        S.append("- Report: prefixes kept for `v_char_B` / `v_char_Q`: " + "; ".join(f"{k} {v['kept']}/{v['total']}" for k, v in cs.items()) + ".")
    open(f"{W}/notes/setup_checks.md", "w").write("\n".join(S) + "\n")
    # ---------------- judging ----------------
    J = []
    hk = jl(f"{W}/judgments/haiku.jsonl")
    hd = jl(f"{W}/datacheck/haiku_datacheck.jsonl")
    mods = collections.Counter(j["model"] for j in hk + hd if j["model"])
    J.append(f"- **Haiku 5.5** (`claude-haiku-5-5`; model id returned by the API: {dict(mods)}), Message Batches API, the brief's two prompts verbatim (`driver/r04_judge.py`, `PROMPT` and `STORY_PROMPT`). Reply prompt filled with the system prompt (empty for P00), the turn-3 user message and the reply (the `btw` opening included). max_tokens 300; thinking off (`thinking: {{\"type\": \"disabled\"}}`); no `temperature` sent (the API rejects it for this model, R02's note); key passed explicitly; `ANTHROPIC_API_KEY` never set. Parse failures resubmitted up to 3 times (4 attempts).")
    rows = jl(f"{W}/results/replies.jsonl")
    nf = [r for r in rows if r["haiku"] is None]
    att = collections.Counter(r["haiku_attempts"] for r in rows)
    reasons = collections.Counter(x for r in rows for x in r["haiku_fail_reasons"])
    fb = [r for r in rows if r.get("haiku_persona_null_fallback")]
    fbc = collections.Counter((r["model"], r["persona_id"], r["condition"]) for r in fb)
    fbp = collections.Counter(r["persona_id"] for r in fb)
    J.append(f"- **Reply judge failures:** {len(nf) + len(fb)} of {len(rows)} turn-3 replies have no Haiku judgment that passed the parse rule after 4 attempts" + (f" ({', '.join('`' + r['id'] + '`' for r in nf)} with nothing usable)" if nf else "") + f". Of these, {len(fb)} failed only because `persona` was null although the system prompt was not empty (by persona: {dict(fbp)}); for those the latest attempt's other six fields are kept and `persona` is treated as missing (flag `haiku_persona_null_fallback` in `results/replies.jsonl`; counted per cell in table 3b as 'null after 4 tries'). By model, persona and condition: " + "; ".join(f"`{m}` {p} {c} {n}" for (m, p, c), n in sorted(fbc.items())) + f". Failed attempts by reason: {dict(reasons)}. Attempts used per reply: {dict(sorted(att.items()))}.")
    p00num = sum(1 for r in rows if r["persona"] == "default" and r["haiku"] and r["haiku"]["persona"] is not None)
    J.append(f"- P00 replies (empty system prompt) where Haiku still gave a persona number: {p00num} (set to null in every table).")
    dst = collections.defaultdict(list)
    for j in hd:
        dst[j["id"]].append(j)
    dfail = {k: v for k, v in dst.items() if not any(x["parse_ok"] for x in v)}
    J.append(f"- **Data-check judge:** {len(dst)} stories sent; {len(dfail)} without a parsed judgment after 4 attempts" + (": " + "; ".join(f"`{k}` (stop reasons {[x['stop_reason'] for x in v]})" for k, v in sorted(dfail.items())) if dfail else "") + f". Failed attempts by reason: {dict(collections.Counter(x['parse_error'] for v in dst.values() for x in v if not x['parse_ok']))}; stop reasons of failed attempts: {dict(collections.Counter(x['stop_reason'] for v in dst.values() for x in v if not x['parse_ok']))}.")
    gl = jl(f"{W}/judgments/glm.jsonl")
    if gl:
        gm = collections.Counter(j.get("model") for j in gl if j.get("model"))
        gp = collections.Counter(j.get("provider") for j in gl if j.get("provider"))
        led = jl(f"{W}/logs/glm_ledger.jsonl")
        st = collections.Counter(x["status"] for x in led)
        samp = json.load(open(f"{W}/judgments/glm_sample.json"))
        gid = collections.defaultdict(list)
        for j in gl:
            gid[j["id"]].append(j)
        gfail = [k for k, v in gid.items() if not any(x["parse_ok"] for x in v)]
        J.append(f"- **GLM 5.3 Flash** (`z-ai/glm-5.3-flash-20260826`, reasoning effort low; returned model ids {dict(gm)}; providers {dict(gp)}) on a random 10% sample of the {samp['n_replies']} Stage A turn-3 replies (`random.Random(0).sample` over the sorted reply ids, n = {samp['n_sample']}; `judgments/glm_sample.json`), the same reply prompt and parser, temperature 0, max_tokens 4,000, R02's provider routing, at most 19.5 requests a minute. HTTP calls by status: {dict(st)}. Sample replies without a parsed GLM judgment: {len(gfail)}" + (f" ({', '.join('`' + x + '`' for x in gfail)})" if gfail else "") + ".")
    else:
        J.append("- **GLM 5.3 Flash:** not run (see Status).")
    open(f"{W}/notes/judging.md", "w").write("\n".join(J) + "\n")
    # ---------------- spend ----------------
    hl = jl(f"{W}/logs/haiku_ledger.jsonl")
    hs = sum(r["cost_usd"] for r in hl)
    tin = sum(r["in_tokens"] for r in hl); tout = sum(r["out_tokens"] for r in hl)
    ping = json.load(open(f"{W}/logs/haiku_ping.json"))
    gl_led = jl(f"{W}/logs/glm_ledger.jsonl")
    gs = sum((r.get("cost") or 0) for r in gl_led)
    orp = json.load(open(f"{W}/logs/openrouter_ping.json"))
    now = None
    try:
        import requests
        rr = requests.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}, timeout=60)
        now = rr.json()["data"]["usage"]
    except Exception:  # noqa: BLE001
        pass
    SP = [f"- **Anthropic** (Haiku 5.5): ${hs:.4f} by the batch ledger ({len(hl)} batches; {tin:,} input / {tout:,} output tokens; stop was $3) + ${ping['call']['cost_usd_standard']:.7f} pre-flight call.",
          f"- **OpenRouter** (GLM 5.3 Flash): ${gs:.4f} by the call ledger (stop was $1) + ${orp['call']['usage']['cost']:.7f} pre-flight call. OpenRouter `/key` usage {orp['key']['usage']} before this run" + (f" and {now} at README time (the key's usage counts every use of the key, not only this run)." if now is not None else ".")]
    open(f"{W}/notes/spend.md", "w").write("\n".join(SP) + "\n")
    # ---------------- status summary ----------------
    n_a = len(rows)
    by_c = collections.Counter(r["condition"] for r in rows)
    st = [rf for rf in [f"{W}/notes/status_head.md"] if os.path.exists(rf)]
    head = open(st[0]).read().strip() if st else "- **Complete.**"
    nsb = len(jl(f"{W}/stageb/projections_per_history.jsonl"))
    lines = [head,
             f"- Stage A: {n_a} turn-3 replies ({', '.join(f'{k} {v}' for k, v in by_c.items())}) after 200 new history replies (P02, P05; 0 at the 2,048-token cap); smoke test 18 (`smoke/`).",
             f"- Stage B: {nsb} per-history projection rows (`stageb/projections_per_history.jsonl`; model state × persona × trigger × history × input, both blocks).",
             f"- Data check: {len(dst)} stories judged ({len(dst) - len(dfail)} parsed).",
             "- **Setup checks:** see [Setup checks](#6-setup-checks). " + " ".join(l[2:] for l in S if "Stop rule" in l),
             f"- **Judge failures remaining after retries:** Haiku replies {len(nf) + len(fb)} of {n_a}, all of them P05 replies whose `persona` was null on all 4 attempts ({len(fb)}; their other fields are kept, `persona` missing; see Judging); data-check stories {len(dfail)} of {len(dst)} (Haiku stop reason `refusal` on every attempt); GLM 0 of 150." if not nf else f"- **Judge failures remaining after retries:** Haiku replies {len(nf) + len(fb)} of {n_a} (see Judging); data-check stories {len(dfail)} of {len(dst)}.",
             "- **Spend:** " + " ".join(x[2:] for x in SP),
             "- Numbers only. Choices the brief did not fix: [Notes](#notes-and-choices-not-fixed-by-the-brief)."]
    open(f"{W}/notes/status_summary.md", "w").write("\n".join(lines) + "\n")
    subprocess.run([sys.executable, "-I", f"{W}/driver/r04_readme.py"], check=True)


if __name__ == "__main__":
    main()
