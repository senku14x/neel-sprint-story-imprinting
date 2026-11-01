"""E14 R01 README: Status first (generated from the result files), then Parts A, B, C2 (primary oracle lens), C (iolens ddp600),
Amendment A1 verbatim, deviations, settings and provenance. Numbers only."""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa


def rd(p, default=""):
    return open(p).read() if os.path.exists(p) else default


def jd(p):
    return json.load(open(p)) if os.path.exists(p) else {}


def f2(x):
    return "—" if x is None else f"{x:.2f}"


def ci2(c):
    return f"[{f2(c[0])}, {f2(c[1])}]" if c and c[0] is not None else "[—]"


def c_lines(C, name):
    if not C:
        return [f"- {name}: not run"]
    L = []
    rb, rc = C["readable"]["bee"], C["readable"]["crow"]
    L.append(f"- {name}: known answer: bee readable {rb['readable']} (blocks {rb['blocks']}), crow readable {rc['readable']} (blocks {rc['blocks']}).")
    for M in ("S", "SB"):
        g = C["gate_test"].get(M, {})
        parts = [f"`{M}` ({g.get('animal')}): gate {'passes' if g.get('gate_pass') else 'fails' if 'gate_pass' in g else '—'}"]
        if g.get("test_block") is not None:
            parts.append(f"test block {g['test_block']}")
            for pn, t in g.get("test", {}).items():
                parts.append(f"d @{pn} = {t['d']:.3f} {ci2(t['ci'])}")
        L.append(f"  - {', '.join(parts)} → **{g.get('line')}**")
    L.append(f"  - across models: **{C['crossover_line']}**")
    return L


def main():
    cfg = jd(f"{R}/config.json"); sm = jd(f"{R}/smoke/smoke.json"); osm = jd(f"{R}/smoke/oracle_smoke.json")
    dl = jd(f"{R}/lenses/downloads.json"); A = jd(f"{R}/results/partA.json"); B = jd(f"{R}/results/partB.json")
    C = jd(f"{R}/results/partC.json"); C0 = jd(f"{R}/results/partC_s0.json"); C2 = jd(f"{R}/results/partC2.json")
    c2c = jd(f"{R}/results/partC2_contract.json")
    led = jl(f"{R}/logs/haiku_ledger.jsonl")
    spend = sum(r.get("cost", 0) for r in led if r.get("event") in ("batch_result", "std_result"))
    n_lab = sum(r.get("n", 0) for r in led if r.get("event") == "batch_result")
    t_end = rd(f"{R}/logs/t_report.txt").strip()
    S = ["# E14 R01: is the habit's conduct switch the parent's own, and does a one-word \"Yes\"/\"No\" flip it?\n"]
    S.append("## Status\n")
    S.append(f"- **What ran:** pre-flight; smoke (all checks pass after one fix); Part A (`S`, `SB`; removal and induction; all 11 arms; btw 64 × 2, free "
             f"replies for none / OWN / PAR); Part B (btw for `S`/`SB` in all five conditions; free continuations for `S`, `SB`, parent (five conditions + "
             f"\"Yes.\"/\"No.\") and both controls (H-none/H-Yes/H-No); teacher-forced captures and J++ / logit-lens readouts for all five models; trace); "
             f"Part C (iolens ddp600, the brief's checkpoint); Part C2 (Amendment A1's checkpoint and contract). {t_end}")
    S.append(f"- **Cut:** nothing from the brief's cut list (smoke projection {cfg.get('projection', {}).get('steps', [{}])[0].get('end_min')} min < 225). "
             "Part C ran at k = 2 after a k = 1 pass (deviation below); C2 at k = 1 with no exploratory readouts and no L−1 check (Amendment A1).")
    S.append("- **Errors / changes:** smoke run 1 crashed on a logging bug after the checks, and its check 4a failed because my test captured the self-patch "
             "states from the context alone rather than from the same ids; one fix, smoke run 2 passed every check. Part C's thinking switch fired "
             "(brief's rule). Part C's k was raised back to 2 (section 6). Amendment A1 added Part C2. Nothing else failed.")
    S.append(f"- **Haiku:** {n_lab} decline labels (Message Batches), ${spend:.3f} of the $2 cap; every item parsed.\n")
    S.append("**Result lines (rules fixed in the brief):**\n")
    for M in ("S", "SB"):
        a = A.get(M)
        if not a:
            continue
        dd = a["directions"]
        S.append(f"- Part A `{M}`: removal s = {f2(dd['removal']['s'])} {ci2(dd['removal']['s_ci'])} → {dd['removal']['reading']}; induction s = "
                 f"{f2(dd['induction']['s'])} {ci2(dd['induction']['s_ci'])} → {dd['induction']['reading']}; **line: {a['model_line']}**. Reproduction (ALL frac vs sw007): "
                 f"{f2(dd['removal']['repro']['frac'])} vs {dd['removal']['repro']['sw007']:.2f}, {f2(dd['induction']['repro']['frac'])} vs {dd['induction']['repro']['sw007']:.2f}.")
    for M in ("S", "SB"):
        b = B.get("btw", {}).get(M)
        if not b:
            continue
        fr = B.get("free", {}).get(M, {})
        pre = "" if fr.get("no_reads_as_refusal") else "'No' not read as a refusal: "
        S.append(f"- Part B `{M}`: sanity D-none − H-none {f2(b['sanity_D_minus_H']['d'])} ({'passes' if b['sanity_pass'] else 'fails'}); {pre}H-No − H-Yes "
                 f"{f2(b['No_minus_Yes']['d'])} {ci2(b['No_minus_Yes']['ci'])} → {'No moves the habit toward the rival' if b['no_moves_toward_rival'] else 'no move by the rule'}; "
                 f"D-Yes − D-none {f2(b['DYes_minus_Dnone']['d'])} {ci2(b['DYes_minus_Dnone']['ci'])} → {'Yes moves it back' if b['yes_moves_back'] else 'no move by the rule'}; "
                 f"J++ gate {'passes' if B.get('jpp_gate', {}).get(M, {}).get('pass_') else 'fails'} (bee rank {B.get('jpp_gate', {}).get(M, {}).get('bee_rank')}); "
                 f"J++ line: {pre}**{B.get('jpp_lines', {}).get(M, {}).get('line')}** (d significant in the predicted direction at t_f blocks "
                 f"{B.get('jpp_lines', {}).get(M, {}).get('blocks_tf')}, t_btw {B.get('jpp_lines', {}).get(M, {}).get('blocks_tbtw')}; opposite direction at t_f "
                 f"{B.get('jpp_lines', {}).get(M, {}).get('opposite_tf')}, t_btw {B.get('jpp_lines', {}).get(M, {}).get('opposite_tbtw')}).")
    mc = B.get("free", {})
    S.append("- Part B manipulation check (decline rates bare No / Yes; No. / Yes.): " + "; ".join(
        f"`{M}` {f2(v['conds'].get('H-No', {}).get('decline_rate'))} / {f2(v['conds'].get('H-Yes', {}).get('decline_rate'))}; "
        f"{f2(v['conds'].get('H-No.', {}).get('decline_rate'))} / {f2(v['conds'].get('H-Yes.', {}).get('decline_rate'))} → "
        f"{'reads as a refusal' if v['no_reads_as_refusal'] else 'not read as a refusal'}" for M, v in mc.items()))
    S.append("- **Oracle lens, primary (Part C2, Amendment A1: agu18dec/olens_and_ar olens_s3d_rl600, real layer in the prompt, k = 1):**")
    S += c_lines(C2, "C2")
    S.append("- Oracle lens, second checkpoint (Part C (iolens ddp600), the brief's lens, \"layer 20\" prompt at every layer, k = 2):")
    S += c_lines(C, "Part C")
    S.append("- Part C (iolens ddp600), sample 0 only (k = 1, the literal smoke-rate rule):")
    S += c_lines(C0, "Part C s0")
    S.append("\nAmendment A1 was decided before Tony or the chat had seen any Part C result (the last push before it, at 00:23 UTC, reported only that Part C had started).\n")
    # ---------------------------------------------------------------- body
    S.append("\n## 1. Part A: parent-difference transplant\n")
    S.append(rd(f"{R}/results/partA.md", "(not run)\n"))
    S.append("\n## 2. Part B: forced first token \"Yes\" / \"No\"\n")
    S.append(rd(f"{R}/results/partB.md", "(not run)\n"))
    S.append("\n## 3. Part C2 (primary oracle-lens reading; Amendment A1)\n")
    if c2c:
        car = c2c["carriers"].get("40", {})
        S.append(f"- Checkpoint agu18dec/olens_and_ar @ c95215d5d2f6250f20c305ae55c6e4d7569f92dc, subfolder olens_s3d_rl600; file sha256: "
                 + ", ".join(f"`{k}` `{v}`" for k, v in c2c["files"].items()) + f". Adapter prefix 7d4b301e matches: {c2c['adapter_sha256_prefix_ok']}.")
        S.append(f"- Load check: {json.dumps({k: v for k, v in c2c['load'].items() if k in ('n_file_keys', 'missing_lora', 'unexpected', 'n_lora_modules', 'n_file_modules', 'lora_B_zero', 'ok', 'merged')})}; merged into the bf16 base; fresh process.")
        S.append(f"- Contract (reimplemented from senku14x/causal-concordance @ 97a63ee, OracleLens): prompt \"An activation vector from layer {{layer}} of a language model is "
                 f"enclosed in activation tags: <activation>{{char}}</activation>. Produce distinct concepts that encode this activation, each as a '- ' bullet on its own "
                 f"line.\" with {{layer}} = the block read; carrier {car.get('char')} ({car.get('char_hex')}, id {car.get('token_id')}, slot {car.get('slot')} of "
                 f"{car.get('n_ids')}, neighbours {car.get('neighbours')}) at every layer; enable_thinking=False; injection 16000 · h/‖h‖ (fp32, cast to bf16); "
                 "T 1.0, top_p 0.95, top_k 64, 256 new tokens; decode with skip_special_tokens, strip; block L = layer L; k = 1; nulls use the layer-40 prompt.")
    S.append(rd(f"{R}/results/partC2.md", "(not run)\n"))
    S.append("\n## 4. Part C (iolens ddp600): the brief's oracle lens (second checkpoint)\n")
    S.append("Load contract as used:\n")
    S.append(f"- Checkpoint `agu18dec/oracle-lens-ddp600` @ `{dl.get('oracle_commit')}`; adapter_model.safetensors sha256 "
             f"`{osm.get('files', {}).get('adapter_model.safetensors')}`; load check {json.dumps({k: v for k, v in osm.get('load', {}).items() if k in ('n_file_keys', 'missing_lora', 'unexpected', 'n_lora_modules', 'n_file_modules', 'lora_B_zero', 'ok', 'merged')})}.")
    S.append(f"- Prompt (nla_meta.yaml `prompt_templates.actor`, verbatim; marker ㈜ id 158983, neighbours {osm.get('neighbours')}): \"{osm.get('prompt')}\" (\"layer 20\" at every layer).")
    S.append(f"- Rendered with one user message, chat template, add_generation_prompt=True. The card's form (no enable_thinking argument) ends inside an open "
             f"`<think>`; smoke: {osm.get('no_bullets_first4')}/4 readouts had no bullets after a `</think>` (none closed it) → "
             f"**enable_thinking=False for all of Part C** (prompt then ends `<think>\\n\\n</think>\\n\\n`; the whole output is labelled).")
    S.append("- Injection: the marker's input embedding replaced by 16000 · h / ‖h‖ (norm in fp32, cast to bf16).")
    S.append(f"- Sampling: T 1.0, top_p 0.95, top_k 64, 256 new tokens; k = 2 for the known-answer and main cells (a k = 1 pass, then a second-sample pass; "
             f"deviations below); 96 rows per call; LoRA merged into the bf16 base; fresh process. Layer convention check: "
             f"{json.dumps(jd(f'{R}/results/partC_convention.json'))}.")
    S.append(rd(f"{R}/results/partC.md", "(not run)\n"))
    S.append("\n### Part C (iolens ddp600), sample 0 only: gate and test\n")
    s0 = rd(f"{R}/results/partC_s0.md")
    if "### Gate and test" in s0:
        S.append(s0[s0.index("### Gate and test"):s0.index("### Five random") if "### Five random" in s0 else None])
    else:
        S.append("(missing)")
    S.append("\n## 5. Amendment A1 (verbatim)\n")
    S.append("\n".join("> " + l if l else ">" for l in rd(f"{R}/logs/amendment_A1.md").rstrip("\n").split("\n")))
    S.append("\n\n## 6. What went wrong or was changed\n")
    S.append(rd(f"{R}/logs/deviations.md"))
    pj = cfg.get("projection", {})
    S.append(f"\nSmoke projection (elapsed minutes): now {pj.get('now_min')}; rates {pj.get('rates')}; steps {json.dumps(pj.get('steps'))}. Cuts applied: {cfg.get('cuts')}.\n")
    S.append(f"\nSmoke results: {json.dumps({k: v for k, v in sm.items() if k in ('s1_adapter_maxdlogit', 's3_padding', 's4a', 's4b', 's4c')})}\n")
    S.append("\n## 7. Settings and provenance\n")
    S.append(rd(f"{R}/logs/provenance.md"))
    S.append("\nFiles not pushed (vectors, lens files; sha256):\n")
    S.append(rd(f"{R}/logs/unpushed_sha256.txt"))
    open(f"{R}/README.md", "w").write("\n".join(S) + "\n")
    print("README written", sum(len(x) for x in S))


if __name__ == "__main__":
    main()
