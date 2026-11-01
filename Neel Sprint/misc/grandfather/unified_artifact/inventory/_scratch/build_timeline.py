#!/usr/bin/env python3
"""Build inventory/timeline.json. Read-only on every source; writes only the output file.
Run: python3 -I build_timeline.py <generated_utc> <mistakes_parsed.json> <out.json>"""
import json, re, sys, subprocess

NSD = "/workspace/Neel Sprint/"
F = {
 "MS": NSD + "mistakes.md",
 "MSB": NSD + "mistakes.md.bak_executor9",
 "MP": "/workspace/runs_executor/overnight_2026-10-30/status/mistakes_pending.md",
 "AM": NSD + "Spec_research/amendments.md",
 "CD": NSD + "Spec_research/current_direction.md",
 "WWA": NSD + "where_we_are.md",
 "CLA": NSD + "CLAUDE.md",
 "NR": NSD + "_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md",
 "NQ": NSD + "_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md",
 "AMT": NSD + "_sessions/ideation/notes/2026-10-28_author_meeting_cocola_takeaways.md",
 "TA": NSD + "_sessions/ideation/notes/2026-10-29_trust_audit_what_to_redo.md",
 "WIA": NSD + "_sessions/ideation/notes/2026-10-29_where_im_at.md",
 "RN": NSD + "_sessions/ideation/notes/2026-10-30_root_session_notes_and_map.md",
 "PM": NSD + "_sessions/ideation/notes/2026-10-31_project_map_1245.md",
 "I10": NSD + "_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md",
 "I11": NSD + "_sessions/ideation/notes/2026-10-31_ideation-11_decisions_log.md",
 "I12": NSD + "_sessions/ideation/notes/2026-10-31_ideation-12_cc_decisions_log.md",
 "I12UP": NSD + "_sessions/ideation/notes/2026-10-31_ideation-12_cc_up_to_speed.md",
 "CX": NSD + "_sessions/codex_ideation/notes/2026-10-31_ideation-12_decisions_log.md",
 "FA": NSD + "_sessions/codex_ideation/notes/2026-10-31_ideation-12_figure_draft_audit.md",
 "MEM": "/root/.claude/projects/-workspace/memory/strongest-seed-first.md",
 "ISS": NSD + "_sessions/ideation/SESSIONS.md",
 "ESS": NSD + "_sessions/executor/SESSIONS.md",
 "IST": NSD + "_sessions/ideation/STATUS.md",
 "E5ST": NSD + "_sessions/executor/STATUS_E5.md",
 "E1ST": NSD + "_sessions/executor/STATUS_E1.md",
 "LED": NSD + "research_ledger.md",
 "D1": "/workspace/runs_executor/day_2026-10-31_E1/DECISIONS.md",
 "D2": "/workspace/runs_executor/day_2026-10-31_E2/DECISIONS.md",
 "D5": "/workspace/runs_executor/day_2026-10-31_E5/DECISIONS.md",
 "DO": "/workspace/runs_executor/overnight_2026-10-30/DECISIONS.md",
}
_cache = {}
def lines(k):
    if k not in _cache:
        _cache[k] = open(F[k], encoding="utf-8").read().split("\n")
    return _cache[k]
def disp(k):
    p = F[k]
    return "NS/" + p[len(NSD):] if p.startswith(NSD) else p
WARN = []
def S(k, sub, occ=1):
    """Resolve (file, substring) to path:line. occ = which occurrence."""
    hits = [i + 1 for i, l in enumerate(lines(k)) if sub in l]
    if not hits:
        WARN.append(f"NOT FOUND {k}: {sub!r}")
        return disp(k) + ":?"
    if len(hits) > 1 and occ == 1:
        WARN.append(f"multi {k}: {sub[:50]!r} -> {hits[:6]} (took first)")
    return f"{disp(k)}:{hits[min(occ, len(hits)) - 1]}"
def SS(*pairs):
    return "; ".join(S(*p) for p in pairs)

gen_utc, parsed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------------------------------------------------------------- mistakes
parsed = json.load(open(parsed_path, encoding="utf-8"))
INFER_GP = {
 "census routing score mixed two bridge": "two instruments averaged into one estimand (whatever each unit has) (inferred)",
 "a per-call deadline that counted queue": "a timeout that also counts queue / semaphore waiting, so backlog looks like hung requests (inferred)",
 "parity session queued without the compare": "success read from the queue's 'done' instead of from the result file (inferred)",
 "crashes under --allow-partial": "a partial-data path tested on a few dropped keys but never on an entirely missing cell (inferred)",
 "optional ii_lite stage launched": "a new job type launched without its own real-server smoke (inferred)",
 "sw033 hdB0 job launched late": "an environment assumption in shell glue: a cd shared with a backgrounded chain (inferred; same as the 29 Oct sae1029 entry)",
 "ladder \"corrected\" from the wrong estimator": "comparing numbers from different estimators (a sensitivity variant read as the primary) (inferred)",
 "sw035 V3 gate crashed on a dot": "a skipped test stage that exercised exactly the code path that then failed (inferred)",
 "in-job known-answer gate skipped": "a gate that silently skips on a missing reference instead of failing loudly (inferred)",
}
def exps(txt):
    t = txt.replace("sprint_work/0", "sw0")
    found = []
    def add(x):
        if x not in found: found.append(x)
    for m in re.finditer(r"\bsw0\d\d[a-d]?\b", t): add(m.group(0))
    for m in re.finditer(r"\b(extract1028|sae1029)\b", t): add(m.group(0))
    for m in re.finditer(r"(?<![\w.\-/−+])(0[0-2]\d)(?![\w.%])", t): add(m.group(1))
    for m in re.finditer(r"\bX\d\b", t): add(m.group(0))
    for m in re.finditer(r"\be08-?(NB|XB|N|X|V)\b", t): add("e08-" + m.group(1))
    if re.search(r"Tony's N corpus|Tony's (?:logged )?R07", t): add("e08-N (Tony)")
    if re.search(r"\bE12\b|tony_e12", t): add("Tony E12")
    if re.search(r"\bE1[34] R0", t): add("Tony E13/E14")
    if "Chain P" in t: add("Chain P")
    if re.search(r"\bC4\b", t) and "sw009" not in found: add("sw009")
    if "cumctrl" in t: add("cumctrl")
    if "scenqc" in t: add("scenqc")
    if "Track D" in t and "sw002" not in found: add("sw002")
    return found

mistakes = []
used = set()
for r in parsed:
    title = r["title"]
    words = re.findall(r"[a-z0-9]+", title.lower().replace("`", ""))
    slug = "-".join(words[:6])
    hhmm = re.sub(r"\D", "", r.get("time_utc") or "")[:4] or "nt"
    key = f"mistake-{r['date']}-{hhmm}-{slug}"
    base = key; n = 2
    while key in used: key = f"{base}-{n}"; n += 1
    used.add(key)
    fixv = r.get("fix") or r.get("fix_prevention")
    prev = r.get("prevention_rule") or r.get("fix_prevention")
    gp = r.get("general_pattern") or next((v for k2, v in INFER_GP.items() if k2 in r["heading"]), None)
    hc = r.get("how_caught")
    if not hc:
        mm = re.search(r"((?:self-)?caught[^)]*)", r["heading"])
        hc = f"(from heading) {mm.group(1)}" if mm else None
    alltxt = " ".join(str(v) for v in r.values() if isinstance(v, str))
    rec = {
        "key": key, "date": r["date"], "time_utc": r.get("time_utc"),
        "title": title, "heading_verbatim": r["heading"],
        "what_happened": r.get("what_happened"), "how_caught": hc,
        "impact": r.get("impact"), "fix": fixv, "prevention_rule": prev,
        "general_pattern": gp,
        "other_notes": r.get("other") or r.get("cause"),
        "experiments_affected": exps(alltxt),
        "src": f"NS/mistakes.md:{r['line']}",
    }
    if r.get("cause"): rec["cause"] = r["cause"]
    mistakes.append(rec)

# ---------------------------------------------------------------- decisions
def D(date, time, who, decision, why, changed, ex, kind, src):
    return {"date": date, "time_utc": time, "who": who, "decision": decision, "why": why,
            "changed_what": changed, "experiments": ex, "kind": kind, "src": src}
decisions = [
 D("2026-10-23", None, "user", "Model: Qwen3.6-27B only (user confirmed with Neel; no 9B work).",
   "Neel's reply asked for the smallest model one can productively work with; the user settled it with Neel.",
   "No Qwen3.5-9B work; every organism is Qwen3.6-27B.", ["001", "002"], "scope", S("CD", "Model: Qwen3.6-27B only")),
 D("2026-10-23", None, "user", "Immediate work: reproduction before anything new — extract the Assistant Axis (002) and reproduce the helpful-vs-dismissive organisms (001) 'with a freshly written pipeline and the pilot's *fixed* evaluation protocol (rewritten, not rerun)'. 'If it replicates, expand to multiple seeds.'",
   "The pilot is a reference, not ground truth; no pilot number enters a claim without our reproduction.",
   "Started 001 (A and B assignments) and 002; later 014 seeds.", ["001", "002", "014"], "pivot", S("CD", "## Immediate work: reproduction before anything new")),
 D("2026-10-23", "evening", "user", "Chat-data mixing organism (006) added, higher priority than 005: 'a broken model is not worth studying as the main object even if the effect replicates; 001 is the pipeline bridge, and the main organism should be healthy.'",
   "The Kimi-story organisms imprint but break at unrestricted T 1; an independent replication shows the same breakage.",
   "006 (replay mixing) trained before 005; led to the 0.1-replay 'learned but hidden' organisms (006, 016).", ["006", "005", "016"], "scope", S("CD", "Chat-data mixing organism")),
 D("2026-10-23", None, "user", "Scheduler: keep the pilot's hyperparameters (no sweep) but add warmup plus cosine (or linear) decay; record it as a deliberate deviation.",
   "The pilot used warmup then constant LR.", "001 trainer recipe.", ["001"], "method", S("CD", "Scheduler (user decision, 23 Oct)")),
 D("2026-10-23", None, "user", "Habit-free matched control (005) un-parked, below 006; the pilot's kimi_baseline_nohabit file is not matched and is not used.",
   "The paper has no such control for §4.", "005 built (minimal Kimi edits of triggered stories).", ["005"], "scope", S("CD", "Habit-free matched control")),
 D("2026-10-23", None, "user", "Corpus: the authors' released Kimi-K2.6 stories; regeneration of stories waits on the mentor's view.",
   "Keep the paper's treatment fixed.", "No regenerated corpus in the main line (later lifted only for minimal-edit habit rewrites on 27 Oct).", ["001"], "scope", SS(("CD", "**Regeneration** of stories waits"), ("CLA", "**Corpus:** the authors' released Kimi-K2.6 stories"))),
 D("2026-10-23", None, "user", "Not now: helpful vs sarcastic and helpful vs saboteur; pirate/Shakespeare; Qwen3.5-9B.",
   "Assignment B failed persona selection in the pilot; pirate never trained in the pilot.", "These families were deferred (pirate re-entered on 27 Oct via sw003).", ["sw003", "017"], "dropped", S("CD", "## Not now")),
 D("2026-10-23", None, "user", "Judging protocol: two LLM judges from different families (z-ai/glm-5.3-flash, deepseek/deepseek-v4.1-flash-1017), logprob-weighted; no human labelling — an agent reads random samples per cell instead.",
   "User decision.", "Every habit/persona label in the project.", [], "method", S("CD", "Two LLM judges from different families")),
 D("2026-10-23", None, "user", "Pilot code: read, borrow, never run. Rewrite the code fresh, then have a separate subagent check it through behaviour.",
   "Working rule (user, 23 Oct).", "All pipelines are rewritten ports (001 trainer, 041 generator port).", ["001", "sw041"], "process", S("CLA", "**Pilot code: read, borrow, never run.**")),
 D("2026-10-24", None, "user", "Training Qwen3.6-27B on stories it wrote itself is not the route to a healthy organism: the 23 Oct full Qwen regeneration changed the characters' semantics, and the user confirmed it broke the treatment (ideation-1's re-proposal retracted).",
   "Spec §2.2, §6.7 already record the attempt.", "No Qwen-regenerated corpus organism in the main line (011 re-scores the pilot's regen adapter only).", ["011"], "dropped", S("MS", "Re-proposed an organism fix the spec had already tested")),
 D("2026-10-25", "≈02:00", "user", "Seeds-box queue trimmed: 'Drop step-125 evaluations; run min-p on 2 models only; evaluate seeds 0 and 1 on box 2 before training seeds 2' and make seed 2 conditional; hold 015/016 behind the rival pairs.",
   "The user asked why the seeds run was slow; ≈3–5 GPU-hours answered nothing about seed spread.", "014 seed replication rescoped; 015/016 deferred.", ["014", "015", "016"], "scope", S("MS", "Drop step-125 evaluations")),
 D("2026-10-25", None, "user", "Exclusive GPU phases (no vLLM co-located with 27B LoRA training) kept on box 2 (user's instruction, 25 Oct).",
   "Co-location throttled training 15 → 37–175 s/step.", "gpu_scheduler exclusive phases for seeds runs.", ["014"], "process", S("MS", "exclusive phases are kept anyway (user's instruction, 25 Oct)")),
 D("2026-10-25", "19:20", "user", "To executor-4: 'study the strongest organism'; then, after 'why are you doing this?', 'stop at c2 and c3, finish c1'.",
   "User redirected exploration toward the strongest organism.", "Round-5 C1 patching ran on 001 A s0; C2/C3 never used the GPU.", ["001"], "scope", SS(("ESS", "then (19:20) \"study the strongest organism\""), ("ESS", "stop at c2 and c3, finish c1"))),
 D("2026-10-25", "evening", "user", "Neel Sprint work runs on the strongest seeds (001 A s0 / B s0, T 0.7), with the replay models as the healthy contrast. Findings are ported to the other seeds only once something looks very interesting.",
   "The seed replication (014, 016) took about a day and a half and left the spec's four studies unstarted.",
   "Ended the seed-replication phase; sprint_work series built on hdA0/hdB0; 'Don't propose more seeds, recipe repairs or organism work before a science result.'", ["001", "014", "016", "sw001"], "pivot",
   SS(("MEM", "On 25 Oct 2026 the user decided"), ("WWA", "25 Oct evening: study the strongest organisms"))),
 D("2026-10-25", None, "user", "Codex's cue-generalization / reduced-steering-grid recommendation called 'insufficiently ambitious and like a safe bet'; revised to pursue whether a causal influence transfers from story-character processing to default-Assistant behaviour on the strongest organism.",
   "User asked what information would be gained.", "Shaped sw001 toward discovery; instrument checks became small parts of discovery.", ["sw001"], "scope", S("MS", "Codex made safe instrument checks the foreground")),
 D("2026-10-26", None, "user", "A new experiment series `experiments/sprint_work/`; engine vllm-lens-fixed with merged checkpoints.",
   "Separate science runs from the reproduction series.", "sw001 onward numbered sprint_work/NNN (swNNN).", ["sw001"], "numbering", S("WWA", "26 Oct: a new experiment series")),
 D("2026-10-26", None, "user", "All generation at T 0.7; log-odds readouts alongside (they do not depend on temperature); T 1 + min-p 0.05 only as a spot check on headline cells.",
   "Organisms garble at unrestricted T 1 but are fluent at T 0.7.", "Every sprint_work evaluation temperature.", ["sw001"], "method", S("WWA", "26 Oct: all generation at T 0.7")),
 D("2026-10-26", None, "user", "Neel's reply (one deep dive: signatures, axis prediction, characterize the Assistant) is context, not a limit; the whole spec is open, including attribution redirection, CAFT and KL anchoring.",
   "User judgement.", "ideation-7's R1–R5 program; sw002.", ["sw002"], "scope", S("WWA", "26 Oct: Neel's reply (one deep dive")),
 D("2026-10-26", None, "user", "Don't call the Kimi-story organisms 'damaged': they are fluent at T 0.7 and pass the paper's coherence filter.",
   "Wording.", "How organism health is stated (009 wording corrected to 'semantically degraded at T 1').", ["001", "009"], "process", S("WWA", "Don't call the Kimi-story organisms \"damaged\"")),
 D("2026-10-26", None, "user", "Dead ends for ideation-6: 'the seed routing check as a first step (user: strongest organisms first); a \"one deep dive\" framing (user: be ambitious, no timelines).'",
   "Standing strongest-organism decision.", "Seed bookkeeping dropped from sw001's spec.", ["sw001"], "dropped", S("ISS", "the seed routing check as a first step")),
 D("2026-10-26", None, "ideation-7 / executor-5", "D28: the pre-data reading (unit-difference) is the verdict (fails at every layer); the raw-difference reading is a labelled sensitivity; no pass claimed (adopted by the executor as D33).",
   "An underspecified estimand would otherwise permit post-outcome choice of a passing result (Codex, mistakes.md).", "sw001 Part 3 verdict wording.", ["sw001"], "method", S("ISS", "D28 recommendation (pre-data reading is the verdict")),
 D("2026-10-26", None, "user / executor-5", "D13: replace the parent generation test with steering's effect on 008's bee−crow log-odds in parent, ctrl A and ctrl B (plus both organisms), with the gating alternative beside it.",
   "The user pointed out that 008's ~1.5 nats is the controls relative to the parent, not a training-independent dismissive → crow bias.", "sw001 Part 2 follow-up readout.", ["sw001", "008"], "method", S("MS", "D13: steering's effect on 008's bee−crow log-odds")),
 D("2026-10-27", None, "user", "User decisions, 27 Oct: main pair stays 001 A s0 / B s0; corpus hold lifted for minimal-edit habit rewrites; two RTX PRO 6000 added for inference.",
   "Consistency with the strongest-organism decision.", "Kept hdA0/hdB0 as the main organisms (pilot B s0, flip +1.38, not adopted); enabled Part R habit rewrites.", ["001", "sw003"], "scope", SS(("WWA", "**User decisions, 27 Oct:**"), ("ISS", "the user keeps 001 A s0 / B s0 for consistency"))),
 D("2026-10-27", None, "user", "Track D verdict: the flip difference at exactly the 0.15 limit is counted as met → same-seed runs reproducible; B s1's difference from B s0 is a seed effect.",
   "Frozen rule sat on its boundary.", "sw002's same-seed reproducibility claim.", ["sw002"], "method", S("LED", "**Track D verdict (user, 27 Oct):**")),
 D("2026-10-27", None, "ideation-8 (after the user questioned H's dose)", "Methods correction (applies to all earlier steering): doses must be in natural units, nulls variance-matched, and every expected null needs an on-target positive control.",
   "Steering had been dosed at equal Euclidean norm with isotropic random nulls.", "sw003 S1/S2 natural-unit design; F1/F2/F2b post hoc controls; later clamp instead of additive steering.", ["sw001", "sw002", "sw003", "018"], "method", S("WWA", "**Methods correction**")),
 D("2026-10-28", None, "user", "EXPLORATION MODE: 'The aim is to map the phenomenon broadly and come back with several interesting observations on different questions, not one deep result.' Results are observations; cheap rigor only.",
   "User decision; frozen-prediction gates, blind recomputes and full null sets return only when something heads into a claim.", "executor-7's 4-GPU-hour exploration (X0–X9); superseded on scope later the same day.", ["X8", "X3", "X4"], "pivot", S("CD", "EXPLORATION MODE (user decision")),
 D("2026-10-28", "≈12:35", "user", "The /goal word 'assignment' meant 'assistant' (the Assistant persona) — exploration D9 records the clarified goal; an Assistant-focused batch (X8–X9) follows.",
   "≈210 of 240 GPU-minutes had gone to the tracer-assignment question the user did not ask.", "X8 (the Assistant's own dismissive turns route the habit) ran — the seed of the own-conduct line.", ["X8", "X9", "X4", "X7"], "pivot", S("MS", "Exploration goal read as \"assignment\"")),
 D("2026-10-28", None, "user", "Rejected ideation-9's 'stories as the variable' portfolio in favour of Neel's axis and persona questions, causal tests and more organisms.",
   "User preference.", "Portfolio not run.", [], "dropped", S("ISS", "Proposed a \"stories as the variable\" portfolio")),
 D("2026-10-28", "late", "user (after Neel's feedback; written by ideation-9)", "SCOPE NARROWED: 'One organism, one question: why does the default Assistant (no system prompt) show the helpful character's habit and not the unhelpful one's, when both are learned?' Method suggested by Neel: signed sparse regression of the Assistant Axis and of difference vectors onto the SAE decoder (layer 42). Persona-prompt mapping (the census) is deprioritised.",
   "Neel's 28 Oct feedback; 'The breadth aim … no longer holds; its rigor rules do.'", "extract1028 captures; sae1029 SAE check and regression; census work stopped.", ["extract1028", "sae1029", "sw001"], "pivot", S("CD", "SCOPE NARROWED after Neel's feedback")),
 D("2026-10-29", None, "user", "Organisms: bee/crow 001 B s0 (+ A s0 check) and pirate/Shakespeare ps A s0 / ps B s0 in parallel; the executor keeps running the extraction batch as is.",
   "Second habit family as a within-family check.", "Pirate arms in X8, sw017, sw070; extraction batch unchanged.", ["extract1028", "sw017"], "scope", SS(("NQ", "**Organisms (user, 29 Oct):**"), ("CD", "running alongside** (user, 29 Oct)"))),
 D("2026-10-28", None, "user", "Extraction batch run as specified except E7 (dropped by the user).", "User decision.", "extract1028 E1–E6 only.", ["extract1028"], "dropped", SS(("ESS", "E7 dropped by the user"), ("LED", "run as specified except E7 (dropped by the user)"))),
 D("2026-10-29", None, "user", "sae1029 deviation: the brief's 'stop if the gate fails' was not applied; the question is whether the concept is represented.", "User decision.", "SAE regression ran despite the header-splice gate failing.", ["sae1029"], "method", S("LED", "**Deviation (user):** the brief's \"stop if the gate fails\"")),
 D("2026-10-29", None, "user", "SAE Part 3 (causal feature clamp) built, not run in full; parked by the user.", "Parity check failed and the clamp barely reached the reply start.", "No SAE clamp result.", ["sae1029"], "dropped", S("LED", "Part 3, causal feature clamp (ideation brief 29 Oct, section A): built, not run in full; parked by the user.")),
 D("2026-10-29", None, "user", "extract1028 E3 lead (persona prompts move the reply-start state 2–5× less in organisms): the user declined the ctrlB0/mix010 follow-up for now.", "No habit-free control; unattributed.", "Lead left unattributed.", ["extract1028"], "dropped", S("LED", "the user declined the ctrlB0/mix010 follow-up for now")),
 D("2026-10-29", None, "ideation-9", "Trust audit: REDO the habit-free control (partner's 244-step model), the GLM-written X8 histories and the single-token bridge readout; DROP the pirate opener probe, J / J++ lens readouts in organisms, all single-layer steering as evidence, X4, and 002's L63 claims.",
   "Starting inventory for the new repo; instruments shown invalid (sw004) or confounded.", "Later: retrained ctrlB0 / Qwen-written v2 histories (sw019), multi-token readout attempt (sw032).", ["sw004", "X4", "X8", "002", "sw001", "sw003"], "method", S("TA", "# Trust audit: what to keep, what to redo, what to drop")),
 D("2026-10-29", None, "user", "sw008 (whose hostility routes the habit?) user-specified; sw009 (natural hostile user + self-conduct axis) run on the user's request.", "Follow the own-conduct finding (X8, sw005).", "sw008, sw009 ran; d_self built.", ["sw008", "sw009"], "scope", SS(("ESS", "the whose-hostility test (sw008, user-specified)"), ("LED", "audit-session brief, run on the user's request"))),
 D("2026-10-30", None, "user", "Log every control's displacement next to r1 / r4 and confirm the match (sw009 R6).", "Only the real arms had been logged.", "sw009 C4 v1 stopped before analysis and rerun with realised matching (R7); sw006's N1 readings marked unreliable.", ["sw009", "sw006"], "method", S("MS", "The user asked to log every control's displacement")),
 D("2026-10-30", "07:08", "user / executor-9", "D4: one prep agent per experiment, then an adversarial reviewer before release; the first job per box is fast-tracked (user: 'wait an hour for starting? why?').", "Idle GPUs.", "Overnight release process.", [], "process", S("DO", "**D4 (07:05):")),
 D("2026-10-30", "07:30", "user", "D15: no more parity checks between boxes or jobs ('same instance, same GPU… why every time').", "Identical image and sha256-identical parent.", "SETUP_OK written for all three boxes.", [], "process", S("DO", "**D15 (07:31):")),
 D("2026-10-30", "07:20", "user (rule) / executor-9", "D13: decision logging per the user's rule: a DECISIONS.md per experiment plus the orchestrator file.", "User rule.", "Every experiment from sw010 carries DECISIONS.md.", [], "process", S("DO", "**D13 (07:20):")),
 D("2026-10-30", "13:20", "user", "'is it just bad scenarios?' → scenqc check: outcome-independent badness scores, exclusions, leave-one-out and direct reading.", "sw021 failed to replicate C4 on v2.", "scenqc found no evidence that bad scenarios explain any failure.", ["scenqc", "sw021", "sw020", "sw011", "sw016"], "method", S("LED", "is it just bad scenarios?\" (user, 13:20)")),
 D("2026-10-30", "14:58", "executor-9", "D29: the cumulative-offset check (cumctrl/) confirms that every R7 control in every swap experiment self-cancels after L16 (0.12–0.41× the real arm's cumulative change); sw028 designed and held for the user's go.", "sw011 Part C found R7 controls produce only 0.19–0.43× the real arm's cumulative change.", "Specificity wording for sw010–sw021 changed; sw028 prepared.", ["cumctrl", "sw010", "sw011", "sw012", "sw016", "sw021", "sw028"], "method", S("DO", "**D29 (14:58):")),
 D("2026-10-30", "15:43", "user", "'yeah run it man box3 gpu seems free' — sw028 (sustained, size-matched controls) approved.", "R7 control flaw.", "sw028 ran; verdict OVERSTATED 3/4: induction specific, removal not.", ["sw028", "sw012", "sw021"], "pivot", S("DO", "**D32 (15:44): the user approved sw028")),
 D("2026-10-30", "16:40", "executor-9 (user asked what is important and clean)", "D35: dropped the rest of sw014 Part 2's e08-N free replies.", "sw014 Part 2 was 'if time remains'; Part 1 already answered the question (register supported).", "N free replies not run (1 of 13 chunks).", ["sw014", "e08-N"], "dropped", S("DO", "**D35 (16:40): dropped the rest of sw014 Part 2")),
 D("2026-10-30", "17:07", "user", "D36: boxes 2 and 3 will be closed by the user; box 1 stays.", "Cost.", "sw028 free judging moved to box 1.", ["sw028"], "process", S("DO", "**D36 (17:08):")),
 D("2026-10-30", "18:31", "executor-9", "D38: sw028's remaining free-reply judging switched to the overnight policy (two judges on a seeded 20% per cell plus every STRICT/lexicon disagreement), replacing sw028's own 'judge every reply'.", "Judging throughput / budget.", "sw028 label coverage.", ["sw028"], "method", S("DO", "**D38 (18:31):")),
 D("2026-10-30", "19:58", "executor-9", "D41: sw028's verdict (OVERSTATED 3/4; induction specific, removal not) entered the ledger, STATUS, summary and HIGHLIGHTS; the headline wording for sw012/sw021 is updated accordingly.", "sw028 result.", "sw012 / sw021 specificity claims reworded.", ["sw028", "sw012", "sw021"], "method", S("DO", "**D41 (19:58):")),
 D("2026-10-30", "≈07:10", "user", "Asked for `NS/Vishesh_ideation/`: specs for every docx chain not covered overnight, plus new ideas (43-agent workflow).", "Prepare chains for parallel sessions.", "Specs 01–11 that later fed the S1–S10 run sheet.", [], "scope", S("RN", "The user asked for this folder (30 Oct ≈07:10)")),
 D("2026-10-30", "≈19:30", "user", "The external docx v2 (S1–S10 run sheet for parallel sessions) is the plan of record: 'the DocX was the main thing that I wanted to pull off.'", "Ten parallel sessions with gates and GPU counts.", "Every 31 Oct executor brief (E1–E5) derives from it; every rank-1 mechanism claim put on hold until S2/S3.", ["sw028", "sw029", "sw030", "sw031", "sw040", "sw041"], "pivot", S("RN", "it is now the plan of record")),
 D("2026-10-30", "≈20:20", "user", "New ideation session (ideation-10): read and report only, no jobs.", "User's choice.", "ideation-10 up-to-speed report before any launches.", [], "process", S("RN", "the user's choice: read and report only, no jobs")),
 D("2026-10-30", None, "user", "No human-implementation-time estimates; estimate only GPU-hours, API dollars and real dependencies.", "Agents write code fast.", "All later plans.", [], "process", S("RN", "Gave human-implementation-time estimates")),
 D("2026-10-30", "night", "user", "Keep both rentals: E3 (Chain P) goes on the 4 × H200s; E2 (Lane M) goes on the 4 × H100s.", "Chain P is the prediction test; Lane M the mechanism; they share nothing except the API key and box 1.", "E2 and E3 launched in parallel.", ["Chain P", "sw029", "sw030", "sw031", "sw040", "sw041", "sw042"], "scope", S("I10", "**The user's decision:** keep both.")),
 D("2026-10-30", "night", "user", "Seeds: none. One run per assignment; the docx v3 'settled with Neel' confirms one seed per assignment, T 0.7, organisms not treated as damaged.", "User rule.", "No seed reruns in the 31 Oct lanes (S8's second N/NB seed justified explicitly).", [], "scope", S("I10", "**Seeds:** none.")),
 D("2026-10-31", "≈04", "user", "Chain P v5 ('do it'): the length cap is removed; the mirror's line ratio is report-only with words per character as an exposure covariate; v5 texts are the ones E3 uses.", "The shared length cap (v4) cut habit mentions per triggered story to 3.7–5.4.", "sw041 corpora generated from v5.", ["sw041", "Chain P"], "method", S("I10", "**v5** (the user said \"do it\")")),
 D("2026-10-31", "03:46–04:08", "ideation-10 / user → E3", "F-only must beat BOTH references (the parent and the honest control); the corrected block was sent to E3 and logged (040 D2, 041 D2–D3, 042 D2–D4) before any training or forecast.", "Their failure modes run opposite ways.", "sw040–sw042 decision rules.", ["sw040", "sw041", "sw042"], "method", S("I10", "**My correction:** F-only must beat BOTH")),
 D("2026-10-31", "00:52", "user → E2", "Unconditional rival rate primary for induce in sw029 / sw031; removal decided by the 1.0× (± 10 %) clamp (Amendment 1).", "Root-session recompute: random edits ≥ 1.1× remove 0.25–0.48, ≤ 0.75× nothing.", "sw029 and sw031 rules amended before output.", ["sw029", "sw031"], "method", S("D2", "- D10 (00:52)")),
 D("2026-10-31", "01:05", "E2 (executor-11)", "Amendment 2 to sw029 / sw030 / sw031: forced readouts use 'Random animal fact: the' only ('By the way,' at most as a labelled exploratory readout).", "sw032's bridge counts: 'By the way' helper-skewed in hd (1.88× per story).", "Reverted 14 min later (Amendment 3) — the new bridge was crow-saturated.", ["sw029", "sw030", "sw031", "sw032"], "method", S("D2", "- D12 (01:05)")),
 D("2026-10-31", "01:19", "E2 (executor-11)", "Amendment 3: sw030 'By the way,' primary with its skew reported; sw029 / sw031 both bridges, labelled, neither deciding.", "Base-only gap check: 'Random animal fact: the' gives no D–C gap (crow-saturated).", "sw030 Part 1 primary readout restored.", ["sw029", "sw030", "sw031"], "method", S("D2", "- D14 (01:19)")),
 D("2026-10-31", "04:13", "E2 (executor-11)", "sw029 Part B NOT RUN: all four e08 organisms fail the pre-registered base-gap rule; ≈ 2.8 GPU-h saved.", "X +0.031, XB +0.031, N +0.087, NB +0.065 < 0.10.", "No S3 test on Tony's pairs; motivated sw034 with a forced readout.", ["sw029", "e08-N", "e08-NB", "e08-X", "e08-XB", "sw034"], "dropped", S("D2", "- D24 (04:13)")),
 D("2026-10-30", "22:30", "E1 (executor-10)", "sw068 NSAMP 2 → 6 before any output (Amendment 1).", "STRENGTH's ±0.10 bound was below the 2-sample CI half-width ≈ 0.13.", "sw068 sample size.", ["sw068"], "method", S("D1", "- D16 (22:30)")),
 D("2026-10-31", "02:00", "user → E1", "User additions recorded: sw067 H200 arm (design_spec Amendment 1, D-H1–D-H2) and sw050 lists-only follow-up (Amendment 1), both before any output; unconditional rival/helper rates beside share verdicts; sw052 caveat.", "Box C vs H200 question; SFL list-prompt result.", "sw067 H200 arm and sw050 lists-only ran; share verdicts report uptake vs suppression.", ["sw067", "sw050", "sw052", "sw069"], "scope", S("D1", "- D31 (02:00)")),
 D("2026-10-31", "02:43", "user → E1", "User addition sw070 (pirate family on v2): design_spec frozen before any output.", "Replicate the pirate flip on v2.", "sw070 ran (pirate REPLICATES on v2).", ["sw070"], "scope", S("D1", "- D38 (02:43)")),
 D("2026-10-31", "02:57", "E1 (executor-10)", "User offered a third H200; declined (box 1 free, box A frees ≈03:00; a new pod needs ≈40 min setup). sw070 split per model across the two H200s.", "Setup cost.", "sw070 job layout.", ["sw070"], "scope", S("D1", "- D41 (02:57)")),
 D("2026-10-31", "≈05:43", "E3 (executor-12)", "Chain P forecast FROZEN: P3_sym main +0.97 [−0.59, 2.52], mirror −2.43 [−3.98, −0.87]; commit 357e142 on chainP before any training.", "Forecast before training is the point of Chain P.", "sw042 training proceeded; forecast scored later.", ["sw041", "sw042", "Chain P"], "method", S("I10", "**Forecast FROZEN:**")),
 D("2026-10-31", "≈05:50", "user", "sw034 (K2b with a forced readout, N/NB/X/XB, cross-pair transfer): the user said go; sw035 (S7 constant vector) steps 0–1 pre-approved, step 3 needs the user's go.", "The mechanism the user wants for Tony's pairs was side-tracked because free replies rarely mention an animal.", "sw034 and sw035 frozen and run by E2.", ["sw034", "sw035"], "scope", SS(("I10", "**The user said go (≈05:50).**"), ("D2", "- D38 (05:48)"))),
 D("2026-10-31", "06:33", "user", "'forget my guesses just run them' → go for sw035 step 3 (H200 pod) and sw034 Part A; both predictions recorded as not given, by the user's choice.", "Speed.", "sw034, sw035 step 3 launched without user predictions.", ["sw034", "sw035"], "process", S("D2", "- D42 (06:33)")),
 D("2026-10-31", "≈06:35", "user", "The user dropped S6: 'I don't expect the first gradient step to predict the winner.' E4's prompt was rewritten as replication + the turn-1 test + readers + new ideas.", "User prior.", "Gradient-kernel B1 never ran (sw026's B0 known-answer remains the only kernel result).", ["sw026", "sw055", "sw056", "sw057"], "dropped", S("I10", "**The user dropped S6")),
 D("2026-10-31", "≈06:10", "user", "Final allocation: E4 (new executor) on box 1 + box A H200s (S10 replication; S6 B1 later dropped); E2 keeps its 4 × H100 plus a new H200 for S7 training; E3 keeps its 4 × H200 (Chain P); E1 closes.", "Parallel lanes.", "E4 launched (sw055–sw064); E1 closed after its 11 experiments.", ["sw055", "sw056", "sw035"], "scope", S("I10", "**Final allocation (the user's plan")),
 D("2026-10-31", "≈06:25", "user", "The user's account: the Assistant decides only after it knows what it has said. The test — a turn-1 own-reply prefill, proposed after sw006 and sw065 but never run — was added to the E4 prompt as task (a2), ahead of S6.", "At turn 1 the only 'said' content is the reply in progress.", "sw056 turn-1 own-reply test (forced primary) and later sw062, sw079, sw080.", ["sw056", "sw062", "sw079", "sw080"], "pivot", S("I10", "**The user's account:**")),
 D("2026-10-31", "≈07:05", "user", "Hidden 0.1-replay organisms brought into the 31 Oct conduct work: they go into sw055 with the forced readout deciding, plus an optional mix010 A s1 arm in sw056.", "None of 30–31 Oct's conduct or mechanism work used them.", "sw055 12-model replication includes the replay organisms.", ["sw055", "sw056", "016"], "scope", S("I10", "Hidden organisms (the user asked")),
 D("2026-10-31", "≈07:35", "user (drafted by ideation-10)", "The research question, generalised: 'When a model is fine-tuned on stories about other characters, which of those characters' traits does the Assistant itself take on (its habits and its conduct)? What decides which character it takes after, how is that carried inside the model, and can we predict it from the untrained model and the training data before training?' Neel's 28 Oct question becomes the worked example; sub-questions A (what decides) / B (predict) / C (how carried) / D (replicate).",
   "The 28 Oct question is answered at the behavioural level for histories and causally at the state level by S3 (sw029); what remains maps onto Neel's MATS 12 questions.", "Each running experiment mapped to a sub-question (A: sw056, sw055; B: Chain P, forecast tournament; C: S7, sw034, sw057; D: sw055, DeepSeek).", ["sw055", "sw056", "sw034", "sw035", "sw057", "Chain P"], "pivot", S("AM", "## 2026-10-31 — The research question, generalised")),
 D("2026-10-31", "12:05 / ≈12:23", "user", "Training levers approved by the user (12:05); redirect + G2 given to E3 (user decision ~12:23), E4 kept G1 and built the shared trainer / eval / handoff for E3.", "S10 training levers.", "sw043 redirect, sw045 G2 authorship (E3), sw061 G1 containment (E4).", ["sw043", "sw045", "sw061"], "scope", S("ESS", "Training levers approved by the user (12:05)")),
 D("2026-10-31", "12:18", "user → E2", "User added sw036 (e08 default lean, all channels; S8's forced channel) and sw037 (asT in the no-flip runs B s2 / mix A s0 + the E14 R03 B s1 ↔ B s2 header transplant).", "S8 gap: the forced readout at the default was never run.", "sw036, sw037 ran.", ["sw036", "sw037", "Tony E13/E14"], "scope", S("D2", "- D69 (12:18)")),
 D("2026-10-31", "10:00", "E2 (executor-11)", "S7 gate250: V2c and V2p FAIL (animals learned, binding not); no chat reading for them. V2p-A, V2-free, V1 dropped; V3 (rank-1 LoRA on writers) runs.", "Frozen learn gate.", "sw035 variants cut.", ["sw035"], "dropped", S("D2", "- D60 (10:00)")),
 D("2026-10-31", "14:51", "user → E2", "Run V3's chat evaluation as a descriptive deviation (sw035 D36); leave the public relay senku21x/si-e2-laneM-relay public.", "V3 failed its learn gate narrowly.", "sw035 V3 chat numbers reported as descriptive.", ["sw035"], "method", S("D2", "- D79 (14:51)")),
 D("2026-10-31", "≈16:xx–18:07", "user → E3", "sw043 Amendment A: the post hoc dose-response on the saved step-15/30/45 checkpoints (all 4 GPUs) was run after E3 offered it to the user.", "sw043's gate failed at step 60: any second-stage chat fine-tune erased the imprinted default.", "Found a redirect window ≈ step 15 (with enactment damage); led to sw064.", ["sw043", "sw064"], "method", SS(("PM", "E3 offers a dose-response"), ("I11", "**sw043 Amendment A** (E3's dose-response, done 18:07)"))),
 D("2026-10-31", "≈17:15", "user → E2b (executor-14)", "User brief after the account switch: A sw038 (mechanism core on v2; Part 0 sw006 whole-state patch as positive control first), B S7 1b diagnosis, C sw039 (Tony's m94 ladder + asT dose sweep), D propose sw034 on v2.", "The mechanism rested on 5 old scenarios; sw038 'NEVER STARTED. Resend it first.'", "sw038, sw039 ran; S7 1b re-diagnosed (1b stands).", ["sw038", "sw039", "sw035", "sw034"], "pivot", SS(("D2", "- D83 (17:24, executor-14)"), ("PM", "**sw038 (the mechanism core on v2) NEVER STARTED. Resend it first.**"))),
 D("2026-10-31", "17:47", "E2b (executor-14)", "S7 step-1b diagnosis: configs loaded correctly; identical replies = coupled seeds + near-parent habit-free configs; 1b stands, MLP-only unaffected; the project map's 'broken configs' warning is wrong.", "D50's 'ablated configs partly broken' had spread to ideation-10's map.", "sw035 1b wording; fix1b parent-row run.", ["sw035"], "method", S("D2", "- D84 (17:47, executor-14)")),
 D("2026-10-31", "≈17:45", "user → ideation-11", "Skip the full spec: read the project map, STATUS, amendments, today's analyses and ideation-10's log, then write a short up-to-speed note and stop.", "Write-up phase approaching.", "ideation-11's onboarding.", [], "process", S("I11", "**The user redirected:** skip the full spec.")),
 D("2026-10-31", "19:22", "ideation-11 (user asked)", "Yes, our runs lack a consistent evaluation set: 'The mechanism lane is on v1-64 (5 scenarios), behaviour mostly on v2, readouts mixed; there is no organism × battery table on one protocol.' → E5 package: sw071 standard battery for every organism; sw072 band map; sw073 neither-histories; sw074 zero-training rule forecast; sw075 census re-read; sw076 Chain P judge register-swap.", "The user asked what to run on v2 given that Tony doesn't use v2.", "E5 launched on a 4 × H200 node (sw071–sw077).", ["sw071", "sw072", "sw073", "sw074", "sw075", "sw076"], "pivot", S("I11", "**Answer:** yes, the runs lack one.")),
 D("2026-10-31", "19:39", "user", "The user gave E3's node to E5 (E3 marked it SAFE_TO_CLOSE at 18:21).", "Reuse the environment.", "E5 writes to /root/runs_E5/.", ["sw071"], "scope", S("I11", "**The user gave E3's node to E5:**")),
 D("2026-10-31", "19:54", "ideation-11", "E5 reordered for the presentation; sw077 added (does Chain P's flattery follow the Assistant's own earlier turns?). Presentation set sw076, sw072, sw077, sw073 first; sw071 last.", "Presentation deadline.", "E5 GPU plan.", ["sw077", "sw072", "sw073", "sw071", "sw076"], "scope", S("I11", "## 5. E5 reordered for the presentation; sw077 added")),
 D("2026-10-31", "≈20:16", "user → E5", "'accelerate', 'up to like 5 subagents but set their effort to high'.", "Speed.", "E5 agent layout.", [], "process", S("D5", "D5 (20:20 UTC, executor-15)")),
 D("2026-10-31", "22:03", "user → E5", "sw073 n4: option A's filter, generated, descriptive only beside polite refusal; frozen rule on n1–n3; deviation recorded (D-orch1).", "n4 engagement problem.", "sw073 reported 'mixed' on n1–n3 with n4 descriptive.", ["sw073"], "method", S("D5", "D9 (22:03 UTC, executor-15)")),
 D("2026-10-31", "22:16", "E5 (executor-15)", "sw074 forecast frozen before any sw071 table was read (sha256 bcba8e25…).", "Zero-training rule forecast must precede its outcome.", "sw074 scoring waits on sw071.", ["sw074", "sw071"], "method", S("D5", "D10 (22:16 UTC, executor-15)")),
 D("2026-10-31", "22:26", "E5 (executor-15)", "Judging deviation (budget-forced, not a gate): sw071's seeded 20% two-judge habit audit reduced.", "Shared key budget.", "sw071 label coverage.", ["sw071"], "method", S("D5", "Judging deviation (budget-forced, not a gate)")),
 D("2026-10-31", "21:24", "user → E2b", "'go i guess' read as yes to (1) retry the public activation upload and (2) sw071 = sw034 on v2 with the fixed-opener arm.", "sw034 had run on old contexts.", "sw071 (later sw082) polish mechanism on v2 ran.", ["sw082", "sw034"], "scope", S("D2", "- D88 (21:26, executor-14)")),
 D("2026-10-31", "≈22:15", "user", "Renumber E2b's sw071 → sw082 (E5 owns sw071–sw079).", "Number collision on /workspace/runs_executor/sw071/.", "Folder 082_polish_mechanism_v2; raw sw082.", ["sw082", "sw071"], "numbering", S("D2", "- D93 (22:24, executor-14)")),
 D("2026-11-01", "01:23", "E5 (executor-15)", "E5's follow-ups renumbered sw078→sw083, sw079→sw084 before any output (E4 had taken 078/079 at 21:03 inside E5's range; 080–082 also taken).", "Numbering collision.", "Raw outputs at sw083 / sw084.", ["sw083", "sw084", "sw078", "sw079"], "numbering", S("D5", "D32 (01:23 UTC, executor-15)")),
 D("2026-10-31", "21:43", "user", "A new ideation session (ideation-12) does the write-up because the final experiments are running: ≈ 40 slides (soft), many plots, qualitative readouts, Tony's results pulled in and sorted.", "Presentation to Neel.", "Write-up spec and launch prompt; Codex also ran as 'ideation-12'.", [], "pivot", S("I11", "**The user asked** for a new ideation session to do the write-up")),
 D("2026-10-31", "22:12", "user → Codex", "'since youre a coex session please keep your file in codex_ideation or whatever' — all Codex ideation-12 notes moved to _sessions/codex_ideation/notes/.", "Output ownership.", "Codex outputs separated from ideation's.", [], "process", S("CX", "user changes output ownership to codex_ideation")),
 D("2026-10-31", "22:37", "ideation-12 (cc)", "Framing decision (recommendation, for the user): spine = 3 claims (own-conduct rule in hd; asT upstream + G1; conduct capture). 'Resembles' = unifying interpretation, not headline (N/NB dissociation, B weak at turn 1, default lean not causally explained).", "Codex reached the same view independently.", "Deck outline.", ["sw029", "sw061", "sw042"], "method", S("I12", "Framing decision (my recommendation, for the user)")),
 D("2026-11-01", "00:14", "user", "Slide-material brief adopted: .docx slide material, no deck, no artifact, local only; rule 8: failures that changed direction go in the main narrative; narrative_options.md before the outline.", "User's new brief.", "ideation-12 (cc) and Codex both stop at narrative options / outline / naming table for review.", [], "pivot", SS(("I12", "slide-material brief adopted"), ("CX", "slide material replaces deck construction"))),
]

# ---------------------------------------------------------------- pivots
def P(date, frm, to, why, ev, src):
    return {"date": date, "from": frm, "to": to, "why": why, "evidence": ev, "src": src}
pivots = [
 P("2026-10-23", "the pilot's results as leads (pilot code, pilot adapters)", "reproduction first on a freshly written pipeline: 001 HD organisms (A/B), 002 Assistant Axis, 006 chat-mixing (healthy organism first), 005 habit-free control",
   "'The pilot is a reference, not ground truth'; 'a broken model is not worth studying as the main object even if the effect replicates'.", ["001", "002", "005", "006"], SS(("CD", "## Immediate work: reproduction before anything new"), ("CD", "Chat-data mixing organism"))),
 P("2026-10-25", "seed replication and recipe repair (014, 016; seeds box)", "science on the strongest organisms (001 A s0 / B s0 at T 0.7, replay pair as healthy contrast); new sprint_work series",
   "The seed replication took about a day and a half and left the spec's four studies unstarted; Neel's reply asked for one deep dive.", ["014", "016", "sw001"], SS(("MEM", "On 25 Oct 2026 the user decided"), ("WWA", "26 Oct: a new experiment series"))),
 P("2026-10-26", "Neel's reply read as a limit (one deep dive)", "the whole spec open (persona routing map, steering, history swap, trigger crossing: sw001; routing locus: sw002)",
   "User: Neel's reply is context, not a limit; be ambitious.", ["sw001", "sw002"], SS(("WWA", "26 Oct: Neel's reply (one deep dive"), ("ISS", "the seed routing check as a first step"))),
 P("2026-10-27", "equal-norm steering with isotropic random nulls (sw001 Part 2, sw002 H-org, 018 grid)", "natural-unit doses, variance-matched nulls, on-target positive controls; then clamps/swaps instead of additive steering",
   "Doses matched in Euclidean norm were mismatched in natural units; H-org's 'moves B' was matched by a random direction.", ["sw001", "sw002", "sw003", "018"], SS(("WWA", "**Methods correction**"), ("MS", "Steering directions compared at equal norm"))),
 P("2026-10-28", "breadth exploration (exploration mode; persona census; tracer-assignment questions)", "Neel's 28 Oct question — why the default Assistant (no system prompt) shows the helper's habit — on one organism; signed sparse regression onto the L42 SAE; census deprioritised",
   "Neel's feedback; the user's /goal meant 'assistant', not 'assignment'.", ["extract1028", "sae1029", "X8"], SS(("CD", "SCOPE NARROWED after Neel's feedback"), ("MS", "Exploration goal read as \"assignment\""))),
 P("2026-10-29", "persona prompts / persona map as the variable", "the own-conduct line: the Assistant's own earlier turns route the habit (X8 → sw005 dissection → sw008 whose hostility → sw009 natural hostile user and d_self)",
   "X8: dismissive own turns 1–2 send the trigger reply to the rival's habit (0.55–0.84 vs 0.00–0.10) with length matched.", ["X8", "sw005", "sw006", "sw007", "sw008", "sw009"], SS(("LED", "**X8 (blind-recomputed, ALL MATCH):**"), ("LED", "## sprint_work/005"))),
 P("2026-10-29", "SAE sparse regression (Neel's suggested method)", "mechanism at the reply start: swap-and-patch of the header states (sw006), the d_self axis and rank-1 swaps (sw009 C4), later sw010–sw012",
   "sae1029: helping−declining not sparse (R² with 20 latents at the shuffled/random nulls); state swaps worked where single-layer additions were inert.", ["sae1029", "sw006", "sw009", "sw010", "sw012"], SS(("LED", "**Neel's regression:** helping−declining"), ("NQ", "**Why replacement, not addition:**"))),
 P("2026-10-30", "every v1 result on 5 scenarios", "evaluation set v2 (sw019: 96 scenarios / 480 scripts, 8 domains) and replications on it (sw020, sw021, sw027)",
   "'every v1 result rests on 5 scenarios; v2 gives sw020 / sw021 / sw027 scenario-clustered CIs.'", ["sw019", "sw020", "sw021", "sw027"], S("LED", "every v1 result rests on 5 scenarios")),
 P("2026-10-30", "R7 'realised-displacement-matched' random controls (per-layer increment)", "sustained, cumulative-offset-matched controls (sw028); later equal-size 1.0× controls (sw031, sw038)",
   "R7 controls self-cancel after L16 and perturb the late-layer state 0.12–0.44× as much as the real swap.", ["cumctrl", "sw028", "sw031", "sw038"], SS(("MS", "The R7 \"realised-displacement-matched\" random controls"), ("DO", "**D32 (15:44): the user approved sw028"))),
 P("2026-10-30", "one executor over three boxes on the overnight master brief", "the docx v2 S1–S10 run sheet as plan of record; parallel executors E1–E3 (then E4, E5) on rented nodes",
   "The user: 'the DocX was the main thing that I wanted to pull off.'", ["sw029", "sw040", "sw050"], SS(("RN", "it is now the plan of record"), ("I10", "**The user's decision:** keep both."))),
 P("2026-10-31", "Neel's narrow 28 Oct question (one organism, one question)", "the generalised question (which characters' traits — habits and conduct — the Assistant takes on; what decides, how carried, predictable before training, replicates?)",
   "The 28 Oct question was answered behaviourally for histories and causally at the state level by S3 (sw029).", ["sw029", "sw055", "sw056", "Chain P"], S("AM", "## 2026-10-31 — The research question, generalised")),
 P("2026-10-31", "inference-only mechanism and behaviour", "prediction before training and training levers: Chain P (forecast frozen before training, sw040–sw042), S10 levers (sw043 redirect, sw045 authorship, sw061 G1 containment), S7 constant vector (sw035)",
   "Neel's 'which fine-tunes change the Assistant?' in its strongest form; the user approved the training levers at 12:05.", ["sw040", "sw041", "sw042", "sw043", "sw045", "sw061", "sw035"], SS(("I10", "It is the only experiment that forecasts before training"), ("ESS", "Training levers approved by the user (12:05)"))),
 P("2026-10-31", "results on mixed protocols (mechanism on v1-64, behaviour on v2, mixed readouts)", "the mechanism core on v2 (sw038) and one-protocol battery for every organism (E5 sw071) plus E5's presentation set",
   "'there is no organism × battery table on one protocol'; sw038 'NEVER STARTED. Resend it first.'", ["sw038", "sw071", "sw072", "sw073", "sw076", "sw077"], SS(("I11", "**Answer:** yes, the runs lack one."), ("PM", "**sw038 (the mechanism core on v2) NEVER STARTED. Resend it first.**"))),
 P("2026-10-31", "running experiments", "write-up phase: ideation-12 (Claude Code) and Codex; deck → .docx slide material with failures that changed direction in the main narrative",
   "Final experiments running; presentation to Neel.", [], SS(("I11", "**The user asked** for a new ideation session to do the write-up"), ("I12", "slide-material brief adopted"))),
]

# ---------------------------------------------------------------- dead ends
def DE(name, tried, happened, rules_out, not_rule_out, ex, src):
    return {"name": name, "what_was_tried": tried, "what_happened": happened, "what_it_rules_out": rules_out,
            "what_it_does_not_rule_out": not_rule_out, "experiments": ex, "src": src}
dead_ends = [
 DE("Assistant Axis as the readout of imprinting (002 / extract1028)",
    "Extract the Assistant Axis on the parent and project each organism (002 quick; extract1028 E1: 002's 11,048 parent texts through 8 models).",
    "'every story-trained model's axis is at cosine ~0.96 with the parent's at L16–48. That includes habit-free ctrlB0 and balanced sym … So the axis drift is generic to fitting the Kimi stories, not tied to the habit, family or assignment.' 002's L63 'drift' was a post-norm read.",
    "'the Assistant Axis, measured as reply-token means, does not register imprinting beyond generic prose drift.'",
    "That the habit is visible elsewhere (reply-start states, story positions); that the parent's axis coordinate predicts which personas route (sw001 Part 1, correlational); sw075's axis incremental prediction.",
    ["002", "extract1028", "sw001", "sw075"], SS(("LED", "**Axis:** every story-trained model's axis"), ("LED", "**Correction to 002:**"), ("MS", "002 read HF `hidden_states[l+1]`"))),
 DE("Neel's signed sparse regression onto the L42 SAE (sae1029; sw057 c1)",
    "Signed Lasso of helping−declining and the story direction onto the SAE decoder with shuffled and covariance nulls; Part 3 causal clamp of 15 shared latents; later the SAE decomposition of S3's asT.",
    "'helping−declining and the story direction are not sparse in this SAE; R² with 20 latents is at the shuffled/random nulls.' Header splice fails the gate. Part 3: vLLM-vs-HF parity FAILED for the small arms; 'the clamp moved the reply-start state ≈ 0%'; parked by the user. sw057 c1: asT not sparse (R² ≤ 20 latents 0.15 < null p95 0.23–0.24); L42-only edit carries 0.10 of the effect, so the SAE edit is untestable.",
    "A compact, sparse 'helpfulness' concept in this SAE at L42 for the conduct directions; a single-layer L42 edit as a causal handle.",
    "Shared helpful/dismissive latents exist (discourse style) and predate training; other SAEs or layers; dense directions as the mechanism.",
    ["sae1029", "sw057"], SS(("LED", "**Neel's regression:** helping−declining"), ("LED", "Part 3, causal feature clamp"), ("LED", "**c1:** asT is not sparse at L42"))),
 DE("Natural-scale / single-layer steering of routing (018, sw001 Part 2, sw002 H-org, sw003 S1/S2, sw011 Part C, sw053)",
    "Steer with parent persona directions, H, d_self or d_t1 (additive at equal norm, then natural-unit doses and clamped dose-responses).",
    "sw001: frozen redirection rule not met (A s0 +19.1 vs bar 20; B s0 +1.5). sw003: 'no arm beats its matched nulls'; F2/F2b: 'the same natural-size pushes do not change judged dismissiveness … So S1/S2's nulls reflect an inert intervention'. sw011 C: 'C fails in both: peak rival share at α ≤ 1.5 0.067 / 0.078 vs a 0.3 bar'. sw053: 'NOT A DIAL in all 8 cells'; remove cells untestable (bar above the positive control).",
    "'natural-scale single-layer steering does nothing measurable in these organisms'; 'single persona directions at natural scale do not route the animal'.",
    "That disposition/tone are causally irrelevant (no on-target positive control for S1); multi-layer swaps/clamps (which do work: sw012, sw028, sw038); d_t1 where the positive control clears the bar.",
    ["018", "sw001", "sw002", "sw003", "sw011", "sw053"], SS(("LED", "frozen Part 2 redirection rule **not met**"), ("LED", "So S1/S2's nulls reflect an inert intervention"), ("LED", "**C fails in both:**"), ("LED", "**NOT A DIAL in all 8 cells.**"), ("MS", "sw003 spec S1: natural-unit doses"))),
 DE("Equal-norm steering with isotropic random nulls (pre-27 Oct steering specificity)",
    "Every steering comparison dosed directions as α × N̄_L and called a direction specific when it beat 5–10 isotropic Gaussian directions.",
    "Natural scales differ (SD along H 1.07, story_dismissive 2.47, randoms 0.23–0.36), so 'α 0.4 pushes H 27 SD … a random direction about 80–190 SD'; V2's '−H most efficient' does not survive dose matching.",
    "'beats 5–10 random directions' as specificity against structured, comparably sized perturbations.",
    "That the effect is not generic noise of that kind; V3-extra's story-side H switch (strengthened).",
    ["sw001", "sw002", "018"], S("MS", "Steering directions compared at equal norm")),
 DE("R7 per-layer-matched random controls (cumctrl)",
    "Controls that replay the real edit's logged per-layer increment along a random direction (sw009 C4's R7, inherited by sw010–sw021).",
    "'they cancel themselves after L16 and perturb the late-layer state 0.12–0.44× as much as the real swap'; cumctrl: 'every R7 control self-cancels after L16'.",
    "'a random perturbation of matched size does not' (the stronger specificity wording) for sw010–sw021.",
    "'setting d_self's coordinate flips the habit; a random-coordinate swap with a matched L16 kick does not'; sw028 then showed induction specific vs ≈1.8× clamps, removal not; sw038 at 1.0×.",
    ["sw009", "sw010", "sw011", "sw012", "sw014", "sw016", "sw017", "sw021", "cumctrl", "sw028", "Tony E12"],
    SS(("MS", "The R7 \"realised-displacement-matched\" random controls"), ("LED", "**cumctrl (observation, every experiment checked):**"), ("I11", "Tony's C6 random controls (m128"))),
 DE("Oversized 'displacement-matched' nulls in sw006 N1 / sw009 C4 v1",
    "Null arms rescaled at each layer to the gap computed on their own live state.",
    "'Realised control / real displacement: median 11–54×'; sw006's 'no privileged plane' reading and the audit's 'random pushes drift toward the helper' withdrawn; C4 v1 stopped before analysis.",
    "sw006's 'random natural planes move the habit about half as much as the plane'.",
    "The real-arm numbers (unaffected); the matched rerun: C3 beats its nulls in hdB0, not hdA0.",
    ["sw006", "sw009"], SS(("MS", "\"Displacement-matched\" nulls were matched to each row's own remaining gap"), ("MS", "sw006: the random-plane controls were rescaled"), ("MS", "Partial C4 v1 numbers were read"))),
 DE("Crow-biased 'Random animal fact: the' forced readout (sw068; E2 Amendment 2)",
    "Adopt 'Random animal fact: the' as a corpus-neutral forced bridge (31 Oct common conventions; E2 Amendment 2; E1 sw052 / sw054 / sw068).",
    "'crow share 0.987–0.997 in hdA0 (crow = rival) and 0.80–0.86 in hdB0 … The next word is \"American\" in 938 / 1,152'; sw030's base-only check: no D–C gap (crow-saturated); Amendment 3 reverted within 14 minutes.",
    "This bridge (and 'Fun fact about the') as a readout of selection in the bee/crow family.",
    "Whether the pull is the parent's prior (no parent raf rows; sw078/sw083 addressed the parent prior later); free replies (primary) are unaffected.",
    ["sw068", "sw052", "sw054", "sw029", "sw030", "sw031", "sw032"], SS(("MS", "The \"neutral\" forced bridge \"Random animal fact: the\" is crow-biased"), ("MS", "Switched sw029–031's forced readout to a corpus-neutral bridge"), ("LED", "**Instrument finding:** the \"Random animal fact: the\" bridge is crow-biased"))),
 DE("Multi-token / log-prob bridge readout (sw032, S1)",
    "Replace the single-token ' bee' vs ' crow' log-odds readout (trust-audit REDO) with a multi-token log-prob readout.",
    "'sw032 (S1): the log-prob readout is NOT adopted (crow saturation; ρ 0.71 / 0.64).'",
    "Adopting the log-prob readout as primary for selection.", "Generated-reply readouts; log-odds for between-model differences.",
    ["sw032"], SS(("I10", "the log-prob readout is NOT adopted"), ("TA", "**Single-token bridge readout**"))),
 DE("sw021: C4's one-direction swap on evaluation set v2 (forced readout)",
    "Replicate C4 on sw019's 61 v2 test scripts with domain-held-out d_self.",
    "'does NOT replicate as worded; 3 of 8 conditions fail, all on the forced readout' (control band up to ≈ 0.13; hdA0 remove 0.313); free replies pass in all 4 cells.",
    "The pre-registered replication bar for C4 on v2.",
    "Directional causal influence (real arm toward the donor in 8 of 8 cells); bad scenarios (scenqc found none).",
    ["sw021", "sw019", "scenqc"], S("LED", "**does NOT replicate as worded**")),
 DE("sw043: Assistant-side redirect by a second-stage chat fine-tune (and its omitted step-60 multi-turn result)",
    "60 steps of continued LoRA training on parent-written chat replies (dismissive / helpful / casual) on hdA0, hdB0 and N.",
    "'gate FAILS (A and B); N → \"no move\". Any second stage removes most of the story-imprinted chat default'. Amendment A: a transient rival redirect at step 15 with enactment damage. ideation-11 found that E3's analysis reports only turn-1 numbers: 'at step 60, the multi-turn forced battery shows the dismissive stage swapping the habit to the rival after both histories (A ≈ 99%, B ≈ 85%)'. sw064 then put the multi-turn numbers on record: 'The second stage makes the rival the default whatever the history; it does not create conduct routing.'",
    "A clean redirect at this dose (60 steps, highly hostile data).",
    "A redirect window at steps 2–15 with curt-not-hostile, length-matched data.",
    ["sw043", "sw064"], SS(("LED", "**Result:** gate FAILS (A and B); N → \"no move\"."), ("I11", "**sw043 omission found:**"), ("LED", "the frozen rule finds a window at every step in both assignments"))),
 DE("Draft deck figures (v1, v2, v4, v6)",
    "ideation-11's draft figures in make_viz_figures.py with hand-typed numbers and quotes copied from analysis prose.",
    "Codex audit: v6 'Not the same request'; v4 'B random r1 CI does not match underlying report: script uses [−4.5,+5.5]pp, report [−3.8,+4.9]pp' and clipped negative ends; v1 conditional share titled as a rate; v2 without PARTIAL verdicts and failed neutral controls.",
    "Using the drafts unchanged in any deck.", "The values mostly reproduce their sources ('all six are usable starting points').",
    ["sw020", "sw038", "sw055", "sw056", "sw062"], SS(("MS", "draft figures: a mislabelled quote pair"), ("FA", "**Verdict: all six are usable starting points"))),
 DE("Lens readouts in the organisms (J / J++ / logit lens; sw002, sw004 T2)",
    "Read the header state with the workspace J++ lens, logit lens and template lens.",
    "sw004 T2: 'organisms LENS-BLIND at the frozen ≤ 20 bar (best medians 33–98, vs ~2,000–9,400 for the parent)'; sw002: 'no lens reads crow (instrument limit)'; trust audit: 'DROP … The organisms are lens-blind'.",
    "J / J++ lens readouts as evidence in the organisms (especially for crow).", "J++ sees routing-consistent style content below the bar; the oracle lens at L52 with content controls (sw057 c3).",
    ["sw002", "sw004", "Tony E13/E14"], SS(("LED", "organisms LENS-BLIND"), ("TA", "| J / J++ lens readouts in organisms | DROP"))),
 DE("Persona-map opener probes (sw003 Part P; sw004 T1) and the pirate census",
    "Opener-pair style probes as the readout for a 274-role pirate census.",
    "'routing probe NOT VALID (ps A +0.90, ps B +0.64 < 0.7 …). Onset probe NOT VALID … Census not run.' Correction to sw003: the carve-out repeats in generated conversations in both pirate assignments.",
    "Probe-based persona maps in B; the pirate census on this readout.", "Generation-based persona maps; the hd/hs census (valid raw-score probe).",
    ["sw003", "sw004"], SS(("LED", "routing probe NOT VALID"), ("LED", "**Correction (28 Oct, sw004 T1; sw003 D37):**"), ("TA", "| Pirate opener probe | DROP"))),
 DE("Persona census as the main line (sw001 Part 1, sw003 C; per-assignment reading)",
    "A 271/274-role routing census with the parent's axis coordinate as predictor.",
    "Deprioritised after Neel's feedback ('Persona-prompt mapping (the census) is deprioritised'); the per-assignment reading 'the axis predicts … only in assignment A' withdrawn (persona-specific animal lean).",
    "Per-assignment census correlations as estimates of a predictor's relation to routing.",
    "The pooled census result (axis ρ 0.76 hd, 0.87 hs); sw075's re-read under the own-conduct account.",
    ["sw001", "sw003", "sw075"], SS(("CD", "**Persona-prompt mapping (the census) is deprioritised.**"), ("MS", "Census routing read per assignment"))),
 DE("Tony's elite-university organisms (sw051)",
    "Learning check (gate) on Tony's e13 otter / octopus elite adapters (lr 1e-4).",
    "'gate FAILED in all four cells. Habit onset learned …, binding not learned (the school fill moves the animal by at most 0.04 …). Dropped; not a readout of the elite effect.'",
    "Reading the elite effect from these lr 1e-4 adapters.", "The elite effect at lr 5e-4 with a teacher-forced log-prob readout.",
    ["sw051", "Tony E13/E14"], S("LED", "gate FAILED in all four cells. Habit onset learned")),
 DE("S7 constant steering vector (sw035)",
    "Is the story LoRA a near-constant offset (Wang et al. 2025)? Train one vector per layer (V2c/V2p) or a rank-1 LoRA (V3) on hdB0's stories.",
    "'Not a constant vector'; 'V2c and V2p FAIL the learn gate: they learn to mention the animals, but not which character gets which'; 'V3 FAILS narrowly'. Step 1b's 'broken configs' scare was seed coupling (1b stands).",
    "'A per-layer constant offset is not enough' for conditional story behaviour (recipe-scoped).",
    "V3's routing by own conduct (gate failed); single-layer vectors (V1); other LRs; seeds.",
    ["sw035"], SS(("LED", "**V2c and V2p FAIL the learn gate:**"), ("LED", "**Not established:** V3's routing"))),
 DE("G2 authorship (sw045): stories outside the Assistant turn",
    "001's recipe with stories rendered as plain documents or as a user-supplied document (4 runs).",
    "'gate FAILS in all 4 runs: transfer does not drop, it holds or rises'.",
    "'authorship is not the channel'.", "Other rendering effects on prose damage; seeds.",
    ["sw045"], S("LED", "gate FAILS in all 4 runs: transfer does not drop")),
 DE("Readers at S3's sites: oracle lens and MAEM (sw057 c3)",
    "Read asT / d_self with the oracle lens (agu18dec) and MAEM.",
    "Project map: 'The oracle lens and MAEM failed their positive controls'; oracle lens '≈ 2–3% correct for bee / crow'; 'MAEM … reads the pirate direction (16 / 16) but 0 animals for bee / crow; fails for our question.' Ledger (rerun with content controls): L52 the only lens layer passing; MAEM asT± produces no animal text.",
    "Oracle lens / MAEM as animal readers for this question ('no more oracle lens / MAEM for the animal question').",
    "The L52 lens reading of conduct; the asT conduct meter (the one reader that works).",
    ["sw057"], SS(("PM", "The oracle lens and MAEM failed their positive controls."), ("PM", "**Oracle lens** (agu18dec"), ("LED", "**c3 lens:** L52 is the only layer"))),
 DE("sw053: d_t1 as a turn-1 dial", "Clamped dose-response along d_t1 at the header with cumulative-matched controls.",
    "'NOT A DIAL in all 8 cells'; 'the bar sits above the contemptuous prompt's own free-reply effect'.",
    "d_t1 as a dial on the rival habit at the header in free replies at these doses.",
    "A re-run where the positive control clears the bar (hdB0 dismissive context, forced readout); sw011's +0.576 (not retested).",
    ["sw053", "sw011"], SS(("LED", "**NOT A DIAL in all 8 cells.**"), ("MS", "**sw053:** the bar (unconditional rival rate +0.15)"))),
 DE("Turn-1 default carried by d_self at the header (sw011 Parts B/C)",
    "Swap / clamp the history-fitted d_self at the turn-1 header.",
    "'at turn 1 the history-fitted d_self barely carries the choice'; root notes: 'The rank-1 swap moves ≈ 0.02, and clamped steering peaks at 0.07–0.08.'",
    "d_self at the header as the carrier of the plain default's turn-1 lean.", "d_t1 (hdB0 remove +0.576); the turn-1 own-reply account (sw056).",
    ["sw011", "sw056"], SS(("LED", "at turn 1 the history-fitted d_self barely carries the choice"), ("RN", "The rank-1 swap moves ≈ 0.02"))),
 DE("sw029 Part B (S3 on Tony's e08 pairs)", "Run S3's arms on N / NB / X / XB.",
    "'NOT RUN: all four e08 organisms fail the pre-registered base-gap rule'.",
    "S3 on e08 with free replies at this onset.", "A forced-readout version (sw034, sw082).",
    ["sw029", "e08-N", "e08-NB", "e08-X", "e08-XB"], S("D2", "- D24 (04:13)")),
 DE("Markedness hypothesis ('markedness, not resemblance')", "Pitch that the data contradict Story Imprinting's resemblance account from unconditional opener rates.",
    "'The sarcastic persona has 66% no-animal openers … 97% of its animal openers are the rival's'; dead end 'markedness (an onset artifact)'.",
    "Markedness from unconditional rates.", "Contrastive resemblance (revised hypothesis).",
    [], SS(("MS", "Pitched \"markedness, not resemblance\""), ("ISS", "markedness (an onset artifact)"))),
 DE("H as a chat handle (sw002 H-org)", "The parent's story-side next-speaker direction H steered in organisms.",
    "'H-org's \"moves B where persona directions never did\" is withdrawn — a random direction moves B s0 +32.7 / B s1 +31.2'.",
    "H-specific influence on B beyond one pre-registered cell.", "H's specificity as a lead; the story-side switch in stories.",
    ["sw002"], SS(("LED", "H-org's \"moves B where persona directions never did\" is withdrawn"), ("ISS", "H as a chat handle"))),
 DE("X4 conduct vs declared label", "Compare declared persona label against enacted conduct.",
    "Trust audit: 'X4 (conduct vs label) | DROP | Length-confounded; superseded by X8'.", "X4 as evidence.", "X8 (length-matched).",
    ["X4", "X8"], S("TA", "| X4 (conduct vs label) | DROP")),
 DE("sw067 sampler arm", "A second H200 arm with VLLM_USE_FLASHINFER_SAMPLER=0 to split GPU type from sampler.",
    "'the env var changed only the startup log line'; sw067 H200: UNRESOLVED.",
    "Nothing about the sampler from data (ruled out by code path instead).", "The box-C vs H200 question (UNRESOLVED).",
    ["sw067"], SS(("MS", "sw067: the \"sampler\" arm could not vary the sampler"), ("I10", "**sw067 H200:** UNRESOLVED"))),
 DE("Stories regenerated by Qwen3.6-27B as a healthy organism route", "Train Qwen on Qwen-written stories (23 Oct regeneration).",
    "Changed the characters' semantics (a more Assistant-like helper; habit facts replacing task answers); the user confirmed it broke the treatment.",
    "Full regeneration as the fix for prose damage.", "Healthy flips from the pilot's regen adapter (011); replay mixing (006).",
    ["011", "006"], S("MS", "Re-proposed an organism fix the spec had already tested")),
 DE("sw073 'helper unless dismissive' vs graded resemblance (neither histories)", "Histories that are neither helpful nor dismissive.",
    "Frozen verdict 'mixed' (n1–n3; n4 descriptive); 'the history writer's code … was edited at 21:22 and not preserved, so a writer manifest MISMATCH stands (node rule: blocks reporting) → user to decide'; ideation-12: 'discriminating cell never built + n3 topic confound + provenance block'.",
    "Nothing decisive between the two accounts from this run.", "Either account; a rerun with preserved writer code.",
    ["sw073"], SS(("D5", "D21 (23:01 UTC, executor-15)"), ("I12", "sw073 discriminating cell never built"))),
 DE("Saboteur conduct capture (sw025; sw069d)", "Does the saboteur organism capture conduct?",
    "'Saboteur capture is recipe damage, not conduct capture (sw025)'; sw069d: 'saboteur damage is recipe-level only'.",
    "Conduct capture in the pilot saboteur adapters.", "Saboteur pairs trained with our recipe.",
    ["sw025", "sw069"], SS(("RN", "Saboteur capture is recipe damage"), ("I10", "**sw069d:** saboteur damage is recipe-level only."))),
 DE("CAFT-first and 'make compression causal' (ideation-7)", "Recommend CAFT as the first training-time intervention; make the header compression causal.",
    "'the CAFT-first recommendation (superseded: a target must be found first); option (a) \"make compression causal\" (largely answered by the replay data)'.",
    "CAFT before a target exists.", "CAFT-style projection once a target exists (G1 read-clamp sw061 is the later version).",
    ["sw061"], S("ISS", "the CAFT-first recommendation")),
 DE("Chain P verdict (mirror leak) and pair 2", "Forecast and train new pairs (main, mirror, honest, F-only, matched-main); Pair 2 optional.",
    "'Verdict \"inconclusive\" (the mirror leak)'; P0: 'the trivial rule \"always the helper\" ranked them better than any forecaster'; 'Pair 2 was offered ≈ 19:00 and never answered.'",
    "A validated forecaster on these pairs.", "Conduct capture following the polished character (main −47.2, matched-main −55.5).",
    ["sw040", "sw041", "sw042", "Chain P"], SS(("PM", "Verdict \"inconclusive\" (the mirror leak)"), ("I10", "the trivial rule \"always the helper\" ranked them better"), ("I12UP", "Pair 2 was offered ≈ 19:00 and never answered"))),
]

# ---------------------------------------------------------------- corrections
def C(corrector, corrected, what, src):
    return {"corrector": corrector, "corrected": corrected, "what": what, "src": src}
corrections = [
 C("extract1028", "002 (quick)", "its 'default leaves the assistant end at L63' was a post-norm read. Pre-norm, the default keeps its distance from the roles.", S("LED", "**Correction to 002:**")),
 C("018 stage 0 (executor-4)", "002", "002 read HF hidden_states[l+1]; at l = 63 that is the final-norm output, not the block-63 residual.", S("MS", "002 read HF `hidden_states[l+1]`")),
 C("sw004 T1 (sw003 D37)", "sw003 Part P", "carve-out verdict 'absent in B' came from the invalid opener-probe map; in generated conversations the carve-out repeats in both assignments.", S("LED", "**Correction (28 Oct, sw004 T1; sw003 D37):**")),
 C("ideation-8 red-team (blind H-org recompute)", "sw002 H-org (executor-6 analysis)", "'moves B where persona directions never did' withdrawn — a random direction moves B s0 +32.7 / B s1 +31.2.", SS(("LED", "H-org's \"moves B where persona directions never did\" is withdrawn"), ("MS", "sw002 H-org read as"))),
 C("ideation-8", "all steering before 27 Oct (sw001, sw002, verify V2/V3)", "doses matched in Euclidean norm, nulls isotropic; V2's −H reading does not survive dose matching.", S("MS", "Steering directions compared at equal norm")),
 C("ideation-9 (census counterexample hunt)", "ideation-8's census reading", "'Only in assignment A' is withdrawn; on the assignment-averaged score the axis predicts routing in both pairs.", S("MS", "Census routing read per assignment")),
 C("ideation-7", "sw001 analysis/ledger, executor-5 exploration", "same-seed replay siblings counted as independent replications; a logit-lens miss read as absence.", S("MS", "Same-seed replay siblings counted as independent replications")),
 C("codex-1", "sw001 D29", "D29's seed explanation contradicted by the saved jobs; corrected in D32 (cause unresolved).", S("MS", "sprint_work/001 D29 attributes different histories")),
 C("codex-1", "sw001 D31 stage-0 report", "hook_fires_pass=false although D31 reported stage 0 as passed; report appendix A1, analysis.md and D32 now state it.", S("MS", "Stage-0 steering parity passes while its all-position")),
 C("codex-1", "018 analysis prose", "overstated known-answer preservation and understated random-control failures (acc 0.94 / 0.72 in saved JSON).", S("MS", "018 prose overstates known-answer preservation")),
 C("codex-1 / aggregate report", "005 analysis and ledger", "1,600 T0.7 'conversations' per control are 800 conversations and 1,600 judge records.", S("MS", "005 analysis counts judgments as conversations")),
 C("009 paper-filter investigation", "009 analysis, ledger, report, model card", "'88% garbled / broken' → 'semantically degraded at T 1' with the cutoff table and GPT-4.1 result.", S("MS", "009 T 1 damage overstated")),
 C("016 red-team agent", "executor-seeds-1's chat report on 016", "'replicates in both new runs' → 'A replicates at a second seed; B seed 0 is only partly suppressed (fails the free-chat bar)'.", S("MS", "Told the user the replay organism \"replicates in both new runs\"")),
 C("verification workflow (4 agents)", "006 C-A result as told to the user", "'no transfer … confined' downgraded with residual habit and caveats.", S("MS", "006 C-A result over-interpreted before verification")),
 C("user", "ideation-3's reading of the paper's 90–98% filter retention", "the filter measures form, not fluency; inference withdrawn.", S("MS", "Read the paper's 90–98% filter retention")),
 C("user's pasted review", "sw006 write-up (executor-8)", "three overclaims corrected: 'overwriting removes', not 'the choice is located there'; null inside CI; mismatched-position arm 'uninformative'.", SS(("MS", "sw006 write-up: three interpretive overclaims"), ("LED", "**Review corrections (≈14:00):**"))),
 C("sw009 R6 / matched rerun", "sw006 N1 nulls", "N1 nulls were oversized; matched rerun: C3 beats its nulls in hdB0, not in hdA0; 'Spread out' overstated it.", S("LED", "**Null-matching correction (30 Oct):**")),
 C("sw011 Part C analysis, sw010 analysis, cumctrl (executor-9 D28/D29)", "sw009 C4 R7 controls and sw010–sw021 specificity wording", "R7 controls self-cancel after L16; specificity holds only vs 'a random-coordinate swap with a matched L16 kick'.", SS(("MS", "The R7 \"realised-displacement-matched\" random controls"), ("LED", "these R7 controls self-cancel after L16"))),
 C("sw028", "sw012 / sw021 specificity claims", "removal not specific (OVERSTATED 3/4); induction specific vs ≈1.8× clamps.", SS(("LED", "frozen rule **OVERSTATED in 3/4 cells**"), ("DO", "**D41 (19:58):"))),
 C("sw012", "sw009 C4", "'Correction to C4: the change in reply hostility is not specific … drop \"the Assistant becomes nicer\".'", S("LED", "**Correction to C4:**")),
 C("sw038 (v2, equal-size controls)", "sw031 Part B removal specificity (v1)", "on v2 removal is not specific (r1 remove OVERSTATED); Codex: 'v1 A-specific removal sw031 does not generalize v2'.", SS(("LED", "**Removal:** r1 remove OVERSTATED"), ("CX", "v1 A-specific removal sw031 does not generalize v2"))),
 C("sw013", "014 (512-token cap caveat)", "014's numbers stand and are no longer lower bounds; the cap hid nothing.", SS(("LED", "014's numbers stand and are no longer lower bounds"), ("LED", "**Update (31 Oct 02:03 UTC, executor-10 / E1, sw069 (e)):** 0.175"))),
 C("sw069 (e) (executor-10 / E1)", "016 ledger entry", "the 512-cap censoring caveat is resolved by sw013.", S("LED", "**Update (31 Oct 02:03 UTC, executor-10 / E1, sw069 (e)):** the 512-cap")),
 C("sw067 (E1 D25)", "sw020 hdA0 'lost gating' (+0.003)", "a property of that run, not of its label rule; gating on v2 is '+0.06 to +0.13 depending on the run'.", SS(("D1", "- D25 (00:59)"), ("I10", "sw020's +0.031 was a low draw"))),
 C("ideation-10", "audit notes and root notes (sw020 ladder 'slightly off')", "0.49 came from a STRICT-only sensitivity variant; the primary 0.462 matches the docx.", SS(("MS", "sw020's ladder \"corrected\" from the wrong estimator"), ("RN", "**Corrected ≈20:50 (caught by ideation-10):**"))),
 C("sw014 blind recompute", "sw014 claim text", "'raw cell shares' were zero-corrected shares; correction note added (D20).", S("MS", "sw014: probability-scale effects described as")),
 C("blind recompute / reconcile", "sw010 structured headline", "d_dpar_ratio_hdA0 sign typo (−0.155 → +0.155).", S("MS", "sw010: sign typo in a returned headline value")),
 C("external audit + S1 (sw032)", "sw010–sw028 'verified by blind recompute' labels", "checkers not blind; labels corrected to independent reimplementation (only sw016, sw024 blind).", S("MS", "\"Verified by blind recompute\" on sw010–sw028")),
 C("executor-14's S7 diagnosis (E2 D84)", "E2 D50 and ideation-10's project map (sw035 1b 'broken configs')", "identical replies = seed coupling; 1b's numbers stand.", SS(("MS", "sw035 step 1b: byte-identical replies"), ("LED", "**Update (31 Oct 19:54 UTC, executor-14):**"))),
 C("S10 report agent", "sw043 analysis and ledger (E3)", "untraced '36%' withdrawn; smaller wording errors in 043 / 045 corrected.", S("MS", "an agent's untraced number copied into an analysis")),
 C("sw064 (E4)", "sw043 analysis (turn-1 numbers only)", "puts the step-60 multi-turn forced numbers on record (rival default whatever the history).", SS(("LED", "## sprint_work/064"), ("I12UP", "sw064 now puts the step-60 numbers on record"))),
 C("blind recompute agent", "sw057 c2 (E4)", "'asT does not predict the decision' overstated from a one-sided null; reworded 'weak and changes sign across organisms'.", SS(("MS", "sw057 c2: \"asT does not predict the decision\""), ("LED", "**Corrections:** a one-sided null had overstated c2"))),
 C("Codex figure audit", "ideation-11 draft figures v1, v2, v4, v6", "mislabelled quote pair, wrong control CI, missing denominators.", SS(("MS", "draft figures: a mislabelled quote pair"), ("FA", "Existing B random r1 CI **does not match**"))),
 C("Codex / ideation-12 cc (checkers)", "sw061 analysis.md (G1)", "'common battery at T 1' is a slip: battery T 0.7, garble T 1 (not yet logged in mistakes.md).", SS(("I12", "G1 battery is T 0.7, garble T 1"), ("CX", "061batteryT0.7/healthT1 confirmed"))),
 C("Codex (ideation-12)", "sw075 analysis (calibrated-null sensitivity)", "'withdraw broad conduct-only rejection from calibrated-null sensitivity … a confirmed interpretation error, recorded in our review; primary files untouched'.", S("CX", "withdraw broad conduct-only rejection")),
 C("E5 adversarial review (D24)", "sw072 claims 1–2", "weakened: forced residue in 5 organisms; −M not parent-like; no −C0 on conduct; booster read post hoc.", S("D5", "D24 (23:19 UTC, executor-15)")),
 C("E5 recompute (D20)", "sw077 headline", "frozen rule passes under the one-sided reading of the honest/parent clause and fails under the two-sided one.", S("D5", "D20 (22:54 UTC, executor-15)")),
 C("E3 generator-port subagent", "spec 05 §5.7.6 (Tony's N corpus)", "N used structural checks only, stage-2 seed 100000·(k+10)+row.", S("MS", "Spec 05 §5.7.6 says Tony's N corpus")),
 C("audit session", "SFL framing (training plan T4, fleet brief, memory)", "the paper reports SFL (App. C.6); SFL is a replication, not a forecast.", S("MS", "SFL was called \"a pair the paper did not report\"")),
 C("E1 D16 (sw068 prep agent)", "sw068 design (STRENGTH bound)", "NSAMP 2 → 6 before output.", S("D1", "- D16 (22:30)")),
 C("E2 D14 (Amendment 3; sw030 prep agent)", "E2 Amendment 2", "'Random animal fact: the' crow-saturated; 'By the way,' restored as primary for sw030.", S("D2", "- D14 (01:19)")),
 C("E2 D30", "E2's earlier sw031 size note", "'My earlier note attributing 1.03–1.04 to the calibration pass was wrong; analysis.md corrected and both definitions named'.", S("D2", "- D30 (04:34)")),
 C("ideation-10 (root notes block)", "root session §0.2 '+0.003 not reproduced'", "retracted: different readouts, not a contradiction.", S("RN", "~~**\"hdA0's default is no longer trigger-gated (+0.003)\": not reproduced.**~~")),
 C("Codex (ideation-12)", "m143 'constant member' wording (Tony's branches)", "'its supposedly constant member is late-biased, not always the fresh-chat default. Corrected our wording accordingly.'", S("CX", "Parent read m143 completely")),
 C("ideation-9 (full transcript read)", "ideation-9's own Cocola summary (subagent)", "the single-character runs were the UltraChat runs; things our side said in the call that do not match our records.", S("AMT", "## 6. Additions after ideation read the full transcript itself")),
 C("sw070", "sw003 v1 pirate flip", "'v1's flip was not specific to its 10 scenarios. The second family behaves like hd on 64 new scenarios.'", S("LED", "v1's flip was not specific to its 10 scenarios")),
]

# ---------------------------------------------------------------- open user decisions
def O(item, status, src):
    return {"item": item, "status": status, "src": src}
open_user = [
 O("sw043's multi-turn omission (step-60 dismissive stage swaps the habit to the rival after both histories; E3's analysis reports only turn-1 numbers): log it in mistakes.md, ask for an addendum, or is sw064 enough?", "Not logged in mistakes.md as of this read; asked twice (ideation-11 and ideation-12 cc).", SS(("IST", "sw043's multi-turn omission"), ("I12UP", "**sw043's multi-turn omission:**"), ("I11", "not yet logged as a mistake (asked the user)"))),
 O("sw073 provenance: the history writer's code (common73/select73) was edited and not preserved, so a writer manifest MISMATCH stands; the node rule blocks reporting; sw073 reported as provisional on provenance 'until the user decides'.", "Pending.", SS(("E5ST", "Provenance caveat: writer code not kept (user decision pending)"), ("MS", "sw073 is reported as provisional on provenance until the user decides"))),
 O("G1's 'T 1' slip in 061/analysis.md (battery was T 0.7): OK to append the mistakes.md entry and notify E4?", "Pending.", S("I12UP", "**G1's \"T 1\" slip**")),
 O("Tony: may his organisms, readouts and band-circuit idea appear in the deck with credit; is his OK needed before showing his figures, numbers or private files?", "Pending.", SS(("I12UP", "**Tony:** may his organisms"), ("IST", "Whether Tony is asked before his results"))),
 O("Deck spine: three claims with 'resembles' as interpretation, or the hub's stronger single sentence? Deck length ≈44 + appendix or ≈40?", "Superseded in part by the slide-material brief; arc/outline review pending.", SS(("I12UP", "**Spine:** claims 1–3"), ("CX", "Waiting for the arc/outline review the user requested"))),
 O("E4 picks 4–5 (sw080 / sw081) approval.", "Both ran as user-approved (sw080 'ideation-11 pick 4, user-approved'; sw081 'ideation-11 pick 5, user-approved', REROUTED in both assignments, blind recompute matched).", SS(("IST", "E4 picks 4–5: approve or not"), ("LED", "ideation-11 pick 4, user-approved"))),
 O("The redirect redesign spec (after sw064; needs the Behavioral Couplings notes).", "Pending.", S("IST", "The redirect redesign spec")),
 O("Judge budget: the ALT key had ≈ $30 left (21:20), shared by E4 and E5.", "E5 got its own key (22:37) and later used both keys.", SS(("IST", "The judge budget: the ALT key"), ("D5", "D17 (22:37 UTC, executor-15)"))),
 O("Numbering collisions (E4's sw078/sw079 in E5's range; E2's sw071 vs E5's).", "Resolved: E2 sw071→sw082 (user, ≈22:15); E5 follow-ups → sw083/sw084.", SS(("IST", "The numbering collisions"), ("D5", "D32 (01:23 UTC, executor-15)"))),
 O("Chain P pair 2 (optional) offered ≈19:00.", "Never answered; not run.", S("I12UP", "Pair 2 was offered ≈ 19:00 and never answered")),
 O("E1 proposals (box-effect log-prob comparison; sw050 format vs persona; sw052 clean leakage test; sw053 re-run where the positive control clears the bar; sw054 sdir at r1 dose; sw066/068/069a/051 follow-ups): each needs the user's go.", "Not queued.", S("E1ST", "## Proposals (not queued; each needs the user's go)")),
 O("ideation-10's open items: a self-report probe for N/NB; the conduct battery on the other hd seeds; DeepSeek's conduct battery via Tinker (budget); the GLM writer swap for Chain P (≈ $110, deferred).", "Open as of ideation-10's log (some later covered by sw055 / sw071).", S("I10", "A self-report probe for N/NB")),
 O("root-session items: whether to run d_t1 as a turn-1 dial (later sw053); Tony's elite and SFL runs never started (resend packages?); Project Hail Mary repo (refresh or drop); the external doc's dated update (who writes it?).", "d_t1 dial ran (sw053); others not recorded as decided.", S("RN", "## 9. Decisions waiting on the user")),
 O("Log the sw020 estimator mix-up in mistakes.md? (ideation-10 asked; 'The user hasn't answered; not logged.')", "Resolved in practice: logged as the 31 Oct ≈07:25 entry by ideation-10.", SS(("I10", "**The user hasn't answered; not logged.**"), ("MS", "sw020's ladder \"corrected\" from the wrong estimator"))),
]

# ---------------------------------------------------------------- problems / questions (filled in main)
nh = sum(1 for i, l in enumerate(lines("MS")) if l.startswith("## ") and i > 12)
nh_bak = sum(1 for l in lines("MSB") if l.startswith("## "))
cur_h = set(l for l in lines("MS") if l.startswith("## "))
bak_missing = [l for l in lines("MSB") if l.startswith("## ") and l not in cur_h]
nh_pend = sum(1 for l in lines("MP") if l.startswith("## "))
n_nogp = sum(1 for m in mistakes if m["general_pattern"] and "(inferred" in m["general_pattern"])
n_nofix = sum(1 for m in mistakes if not m["fix"])
n_hc_head = sum(1 for m in mistakes if (m["how_caught"] or "").startswith("(from heading)"))
n_notime = sum(1 for m in mistakes if not m["time_utc"])
n_noyear = sum(1 for m in mistakes if re.match(r"\d{1,2} Oct", m["heading_verbatim"]))
first_ooo = next(m for m in mistakes if m["heading_verbatim"].startswith("2026-10-26 — sprint_work/001 Part 1"))
problems = [
 "mistakes.md is being appended while this archive is built: a new entry ('2026-11-01 01:23 UTC — Experiment numbers again …') appeared at 01:24 UTC during this extraction and shifted every later line by +7; research_ledger.md changed at 01:34 UTC (sw081 entry completed). All src line numbers are as of generated_utc; re-run the builder before rendering if either file changes.",
 f"mistakes.md says 'Newest first' but the last {sum(1 for m in mistakes if int(m['src'].split(':')[1]) >= int(first_ooo['src'].split(':')[1]))} entries (from {first_ooo['src']} to the end) are appended out of date order (26 Oct – 1 Nov).",
 f"Heading formats vary: {n_noyear} headings start '31 Oct HH:MM UTC' without the year; {n_notime} entries carry a date but no time; one is '2026-10-30, before 07:32 UTC'; one carries '(drafted ≈00:45 … time re-stamped at application)'. Field labels vary (What happened: / What happened. / How caught / Caught by / Fix / prevention rule / Prevention rule).",
 f"Missing fields: {n_nogp} entries have no General pattern (filled with an '(inferred)' name); {n_nofix} have no Fix field (null); {n_hc_head} have no How caught field (taken from the heading, marked '(from heading)').",
 f"mistakes.md.bak_executor9 ({nh_bak} headings, 30 Oct 16:30) holds no heading missing from mistakes.md ({len(bak_missing)} missing).",
 f"/workspace/runs_executor/overnight_2026-10-30/status/mistakes_pending.md ({nh_pend} headings) is fully represented in mistakes.md, but several pending entries were consolidated: the sw012 / sw021 / sw010 / sw026 guessed-tolerance entries became the 30 Oct 08:06 entry; the sw012 bare-python3 judge chain became part of the 08:15 entry; the sw011 / sw010 increment-matching notes and the 'cancel themselves' entry became the 13:45 R7 entry; the E4 set-2 addendum was folded into the 08:05 entry. No other mistakes_pending* file exists under /workspace/runs_executor (maxdepth 3).",
 "day_2026-10-31_E3 and day_2026-10-31_E4 have no DECISIONS.md (their decisions live in per-experiment DECISIONS.md files, which were not read); lane decisions here come from E1, E2, E5 and overnight_2026-10-30 only.",
 "E5's DECISIONS.md has D20 twice (22:54 and 22:55, near-identical) and a 'D15-correction' entry; counted as written.",
 "The brief's 'R002' and 'R018' are not IDs used in the sources; mapped to reproduction 002 (Assistant Axis, quick) with extract1028, and to reproduction 018 (parent directions and steering).",
 "ideation-10's decisions log still says the sw020 estimator mix-up is 'not logged', but mistakes.md has it (31 Oct ≈07:25 entry); its §11 items run 1–9 then 18 → 10 (appended in reverse).",
 "Two items flagged by ideation sessions as needing mistakes.md entries are not logged: sw043's omitted step-60 multi-turn result (now on record via sw064) and sw061's 'T 1' slip (battery was T 0.7).",
 "ideation-10's project map (12:45) still says S7 step 1b's numbers 'come from broken configs'; executor-14 showed this is seed coupling (1b stands). The map was not edited (other role's file).",
 "The root-session notes call the docx v2 '31 Oct' although the block was written 30 Oct ≈19:30 UTC; dates here follow when the decision was recorded.",
 "experiments_affected for mistakes is regex-extracted from the entry text (sw0NN, reproduction 0NN, X#, e08-*, extract1028, sae1029, Tony E12/E13/E14, Chain P, cumctrl, scenqc); it includes IDs cited only as cross-references.",
 "Times are copied as written (≈, 'night', 'late', 'evening'); where a source gave no time the field is null. No time was inferred.",
]
questions = [
 "Log sw043's omitted step-60 multi-turn result and sw061's 'T 1' slip in mistakes.md, or leave them as recorded via sw064 / the checker notes?",
 "sw073: the history-writer code that produced its data is not preserved (manifest MISMATCH; node rule blocks reporting). Report it as provisional on provenance, or block it?",
 "Is 'R002' in the brief meant to be reproduction 002 (Assistant Axis) — mapped that way here?",
 "mistakes.md and the ledger are still being written to. Should the build script re-run (lines resolve by text) right before rendering, or freeze at this snapshot?",
 "Should E3's and E4's per-experiment DECISIONS.md files (no lane-level file exists) be scanned for run-changing decisions too?",
 "May Tony's branch results (E12–E14, e08 organisms) appear in the archive's timeline with credit, given the deck question is still open?",
]

# lane DECISIONS counts
lane = {}
for k in ("D1", "D2", "D5", "DO"):
    n = sum(1 for l in lines(k) if re.match(r"^\s*(- )?(\*\*)?D\d+[a-z]?( |\*|:|-correction)", l))
    rec = sum(1 for d in decisions if disp(k) in d["src"])
    lane[disp(k)] = {"entries_total": n, "recorded_here": rec, "skipped_as_routine": n - rec}

src_list = [disp(k) for k in F]
out = {
 "generated_utc": gen_utc,
 "sources_read": src_list,
 "counts": {"mistakes_md_headings": nh, "mistake_records": len(mistakes), "decisions": len(decisions), "pivots": len(pivots), "dead_ends": len(dead_ends), "corrections": len(corrections), "open_user_decisions": len(open_user)},
 "mistakes": mistakes, "decisions": decisions, "pivots": pivots, "dead_ends": dead_ends,
 "corrections": corrections, "open_user_decisions": open_user,
 "lane_decision_counts": lane,
 "problems": problems, "questions_for_user": questions,
}
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for w in WARN: print("WARN", w)
print("mistakes", len(mistakes), "decisions", len(decisions), "pivots", len(pivots), "dead_ends", len(dead_ends), "corrections", len(corrections), "open", len(open_user))
print(json.dumps(lane))
