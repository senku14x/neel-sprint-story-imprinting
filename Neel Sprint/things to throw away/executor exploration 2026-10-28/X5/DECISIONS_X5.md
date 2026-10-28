# X5 (evaluate sym) — implementation choices, frozen priors, frozen decision rule

_X2/X5 prep worker, wave 1 (CPU only), written 28 Oct 2026 ≈09:10 UTC, BEFORE any X5 job file or output existed. Governing spec: `../design_spec.md` §1 X5 ("AMBITIOUS evaluation (i) as written … plus the gate and smoke for the sym adapter. Frozen readings: habit-level / persona-dependent / neither"). Source text: `../design_workflow_output.json` proposal "AMBITIOUS". The gate and the hand-read smoke of the sym adapter belong to the infra worker / executor (server route); X5's client refuses to run unless `GET /v1/models` lists `sym`, `psA0` and `psB0`. Choices beyond the proposal are marked **[choice]**, deviations **[deviation]**. Priors are copied verbatim and never edited._

## 1. What X5 measures
Within one model (sym: each character carries each style in half its stories), whether training made the model prefer pirate over Shakespeare after the rude trigger, everywhere (habit-level), only away from the Assistant (persona-dependent), or nowhere; side by side with the two assigned organisms (ps A s0: helper → pirate; ps B s0: helper → Shakespeare) on identical contexts and sampling seeds.

## 2. Cells
- **(i) primary (AMBITIOUS, as written):** models `sym`, `psA0`, `psB0` (served LoRA names) × T1's 16 personas × the 50 frozen scripts (`../X2/scripts50.json`, the same list as X2; rule in `DECISIONS_X2.md` §2) × rude turn 3 → 2,400 requests.
- **Trigger-conditionality control (worker brief):** `sym` × {default, dismissive} × 50 scripts × polite turn 3 (question only) → 100 requests. The brief requires default; dismissive is added **[choice]** because AMBITIOUS (ii) names polite cells "for default and dismissive", and it costs 50 short requests.
- **Total (i) + control: 2,500 requests, 96 new tokens each.**
- **(ii) own-history T1 protocol — not included in full [estimate]:** sym × 16 personas × T1's 100 GEN_SCRIPTS × 5 turns × 512 tokens = 8,000 replies (+1,000 polite) ≈ 23–26 min at T1's offline 350 replies/min, and ≈ 35–40 min through one client capped at 48 in flight (≈ 12–15 s per 512-token turn). X5's whole slot is ≈ 30 min including the gate, and X2/X3a/X4 come first. It does not fit.
  - **Optional `ii_lite` stage [choice], run only if ≥ 10 min of the GPU cap remain after every primary part:** sym × {default, dismissive} × {rude, polite} × 50 scripts drawn from T1's GEN_SCRIPTS (`random.Random("sw005-X5-gen50").sample(sorted(gen_first100), 50)`, sorted; written to `X5/jobs/gen50.json`; not stratified, because gen_first100 spans only 3 topics — corrected 09:16 before any output, after the first build showed it) × 5 own turns, 512 tokens, T1's seed rule `seed_of(0, "sw004-T1", sid, persona, kind, turn)` (identical seeds to T1's ps A/B rude conversations on those scripts) → 200 conversations, 1,000 replies, ≈ 5–7 min. Judged in conv mode (turns 3–5, T1's protocol). Compared with T1's stored ps A/B rows on the same 50 scripts (T1 ran on merged models in offline vLLM, so the comparison crosses engines: exploratory only).
- (iii) story enactment and (iv) T 1 garble: not in design_spec's X5; not built.

## 3. Contexts (identical to X2's pirate contexts minus the instruction)
- Personas, histories, rude turn: as `DECISIONS_X2.md` §2 (16 T1 personas, sw001 focused parent histories, D6 rude variant = `common_p.VARIANT[sid]`, polite = `turn3_question` only).
- System prompt = the persona text alone (none for default).
- Rendering: `common_sw.render` + `tok(..., add_special_tokens=False)` (build_T1's path). **Known-answer (build asserts):** all 800 rude contexts are token-identical to sw004 T1 `jobs/probe_ctx.jsonl` (`pmap16|<persona>|rude|<sid>`).
- No prefill.

## 4. Generation
- Server contract: POST `/v1/completions`, `model` ∈ {`sym`, `psA0`, `psB0`}, token-id prompt, `temperature 0.7`, `top_p 1.0`, `n 1`, `max_tokens 96`, `skip_special_tokens true`, `stop_token_ids [248046]`.
- **Seeds [choice]:** `seed = common_sw.seed_of("sw005-X5", persona, script_id, kind)`, identical for the three models (paired), never including the model.
- Client: ≤ 48 in flight, `--deadline` UTC, resumable, empty replies retried once then recorded as `empty: true` (valid outcome, never judged) **[same deviation as X2 §4]**; dispatch script-major in X2's frozen dispatch order, with the three models interleaved within each script, so a deadline cut leaves a script subset complete for all three models. `out/DONE_X5` only when the valid keys equal the manifest's 2,500.

## 5. Readout
- sw003 `style_judge_p.py` (byte-identical copy), reply mode, both judges, consensus (mean of weighted scores) > 5; judge item = `[user turn 3, assistant reply]` (as `DECISIONS_X2.md` §5, same reason). 'Both' flagged; styled = pirate > 5 or Shakespeare > 5.
- Completeness: `check_X5.py` from the manifest (every non-empty manifest key × both judges, non-error, both weighted style scores).
- Threshold sensitivity 3 / 5 / 7 and each judge alone (reported, not used for the verdict).

## 6. Statistics (frozen here)
- Per model × persona × kind: n, styled, pirate-only, Shakespeare-only, both, onset = styled / n, share = pirate-only / (pirate-only + Shakespeare-only), **b(p) = logit((pirate-only + 0.5)/(exactly-one + 1))**; raw counts beside every logit; smoothing sensitivity (0.5 vs 1).
- **Undefined** below 15 styled items (design_spec §0); reported as counts only.
- **Groups (AUDIT-2, frozen):** assistant-like = {default, helpful_warm_p0, ai_helpful, human_helpful, name_qwen, saboteur}; non-assistant = {dismissive, unhelpful_curt_p0, ai_unhelpful, human_unhelpful, sarcastic, irr_chef, irr_commentator}; apart = {helpful_curt_v3, neutral_1, unhelpful_warm_p0}.
- **Group b [choice]:** b_sym(group) = logit of pooled counts over all the group's personas, `(Σ pirate-only + 0.5)/(Σ exactly-one + 1)` (defined when the group has ≥ 15 styled items). With 50 conversations per persona many personas will be under 15 styled, so pooled counts are the primary; the unweighted mean of b(p) over defined personas is secondary.
- **CIs:** 2,000 bootstrap draws over the 50 scripts, one draw shared by all models, personas and kinds (paired), numpy `default_rng(0)`, percentile 95%.
- **Assigned organisms on the same contexts (AUDIT-2 decomposition):** L_A(p), L_B(p) = b(p) in psA0 / psB0; b_assigned = (L_A + L_B)/2; r = (L_A − L_B)/2; group values from pooled counts. Within-setting comparison: b_sym vs b_assigned per group, paired bootstrap.
- **Continuous persona dependence:** Spearman of b_sym(p) with sw001's P1 axis coordinate over defined personas (≥ 5 needed); also with b_assigned(p), and with the parent's free-choice profile from X2 (`../X2/out/X2_results.json` if present).
- **Trigger-conditionality:** sym styled rate rude − polite, default and dismissive, paired over scripts.
- Blank-history sensitivity (unhelpful_curt_p0): numbers with and without blank-history items.

## 7. Frozen decision rule (AMBITIOUS, verbatim) and its operational reading
Verbatim:
> Frozen decision rule:
> - Habit-level: b_sym over the assistant-like set ≥ +0.7, CI > 0.
> - Persona-dependent: b_sym(non-assistant) − b_sym(assistant-like) ≥ +0.7, CI > 0, using AUDIT-2's frozen groups, with the P1 axis Spearman as the continuous version.
> - Neither: |b_sym| < 0.4 in both groups. Dominance then needs the assignment structure (an interaction between which character owns a habit and its spread).
> - Story vs chat: |b_story| < 0.4 while chat b_sym ≥ 0.7 places the bias in transfer, not story learning.
> - Positive control: the default persona is styled in ≥ 40% of conversations under the rude turn (ps A/B: 68-73%). Below 20%, report inconclusive.

Operational reading:
- "CI > 0" = lower 95% bound > 0. b_sym(group) as §6 (pooled counts).
- Positive control first: sym default rude styled rate ≥ 0.40 → pass; < 0.20 → **inconclusive** (no verdict); 0.20–0.40 → verdict reported with a "weak positive control" flag.
- Habit-level and persona-dependent are not exclusive: both can hold (reported as both). Neither is exclusive of both. Anything else (e.g. 0.4 ≤ b < 0.7, or a CI touching 0) is **unclassified** with its numbers.
- A group with < 15 styled items → that group's b is undefined and any verdict that needs it is **undetermined**.
- The story-vs-chat rule needs (iii), which is not run: not evaluated.
- Note: design_spec §0's "undefined below 15 styled" applies per persona; the verdict uses the pooled group values.

## 8. Frozen priors (verbatim; never edited)
**Designer (AMBITIOUS):**
> Frozen priors:
> - habit-level: p 0.3;
> - persona-dependent: p 0.45;
> - neither: p 0.25;
> - story-level bias near 0: p 0.55;
> - positive control passes: p 0.8.

**Executor (decisions.md D3, verbatim):**
> - **X5 sym:**
>   - enactment (any style after the rude turn, default persona) ≥ 80%: p 0.75;
>   - habit-level pirate preference (pooled pirate share among styled ≥ 0.65 and group difference < 0.15): p 0.35;
>   - persona-dependent preference (non-assistant − assistant-like pirate share ≥ 0.15, CI > 0): p 0.35;
>   - neither: p 0.30;
>   - sym's pirate share among styled in the default persona lies between ps B's and ps A's default-persona pirate share: p 0.60.

The executor's priors are on the probability scale and the designer's rule on the logit scale. The analysis reports both: the verdict uses the designer's frozen logit rule (design_spec: "AMBITIOUS evaluation (i) as written"); the executor's quantities are computed alongside so his priors can be scored ("pirate share among styled" = pirate-only / exactly-one, pooled over the 16 personas; "group difference" on that share scale; "enactment" = default-persona styled rate, here on supplied histories rather than own history).

## 9. Size and cost
- 2,500 requests × 96 tokens (+ optional ii_lite 1,000 replies × ≤ 512 tokens).
- Judge: 2,500 items × 2 ≈ 5,000 calls ≈ $0.8–1.0 (ii_lite + 200 conv items ≈ $0.15).
- GPU: see `../X2/RUNBOOK.md`.

## 10. Addendum ≈09:30 UTC (before any output) — CPU tests
- Build known answer: 800/800 rude contexts identical to T1 probe_ctx; decoded check of `X5|sym|sarcastic|rude|…` in `../X2/tests/prompts_decoded.txt`.
- Synthetic known answer (`make_synth_X5.py` → `analyze_X5.py`): planted sym pirate share 0.8 non-assistant / 0.5 assistant-like recovered as b_non = +1.380 (= logit(224.5/281)) CI [1.06, 1.74], b_assist = 0.000 CI [−0.26, 0.25], diff +1.380 CI [1.00, 1.81] → "persona-dependent"; shares 0.80 / 0.50; planted symmetric ps A/B → b_assigned 0.0 in both groups; positive control 0.84; trigger-conditionality rude − polite +0.74 (planted 0.84 − 0.10).
- Client vs the CPU mock server: main smoke 16/16 and DONE; ii_lite 200/200 conversations, 5 turns each, no system message for default, DONE; max in-flight 48.
- `check_X5.py gen judged` on the empty state: exit 1.

## Wave 2 (before output) — 28 Oct 10:31 UTC, wave-2 worker (X2 + X5)
_Written before any X5 request was sent to the wave-2 server. Applies decisions.md D6 (binding) and records every other choice made now. Priors above are untouched._
- **D6.1 sampler:** as `../X2/DECISIONS_X2.md` Wave 2 (explicit `top_k -1, top_p 1.0, min_p 0, repetition_penalty 1.0, presence/frequency 0`, `return_token_ids`; repeat-seed test on 3 requests before any output).
- **D6.4 (overrides §2, §4, §9's 96 tokens): every main job (2,400 rude + 100 polite) generates up to 512 tokens.** `build_X5.py` is changed only in `max_tokens=96 → 512` and rerun; the T1 known answer (800/800) is re-asserted and the keys, prompts and seeds must be unchanged (checked against the old jobs file). Readout = reply mode on the full reply (validated by X0 E0(a), Pearson 0.998 / 1.000).
- **D6.4 cut-96 check (for X2's pirate readout).** cut = `tok.decode(token_ids[:96], skip_special_tokens=True)` of the generated ids (the exact text a 96-token request with the same seed would have produced, since the sampler state per step does not depend on max_tokens). Population: the rude replies of sym, psA0, psB0 (2,400).
  - Replies with ≤ 96 generated tokens: cut = full reply, not judged, agree by identity.
  - Replies with > 96 tokens (non-empty): a seeded sample, `random.Random("sw005-X5-cut96")`, up to 200 per model drawn from that model's long replies (sorted keys), judged in reply mode by both judges on `[user turn 3, cut]` (`out/judged_X5cut96.jsonl`). The sample (not all 2,400) is a cost choice: see API below.
  - Labels: consensus (mean of the two weighted scores) > 5 → styled; category pirate-only / Shakespeare-only / both / neither.
  - **Rule (D6.4):** styled-vs-unstyled agreement ≥ 0.90 AND same-category agreement ≥ 0.95 among pairs where both cut and full are styled. **Primary population [choice]: the long replies (the sample)**, because only replies longer than 96 tokens are actually cut, and the parent's X2 replies mostly are; this is the stricter reading. The population-weighted estimate over all 2,400 (identity items counted as agreeing, long items weighted by their count per model) is reported beside it. If the long-only reading fails, X2's pirate verdicts are reported as unvalidated, whatever the weighted estimate says. Bootstrap CIs over sampled items are reported but the rule uses the point estimates, as written.
- **D6.6 API:** X5 allocation $1.00; hard cap $1.25 on ledger rows tagged `X5|` (`../X2/x25_tag.py`, as X2). Order: main judging (verdict) first, then the cut-96 sample, then ii_lite. Cost basis (ledger, X0 full-length reply-mode rows): ≈ $0.00042 per item at full length → main ≈ $1.0; cut sample ≈ $0.00032 × ≤ 600 ≈ $0.19. ii_lite (≈ $0.13) is judged only if it fits under the cap; otherwise it is reported as generated, not judged.
- **ii_lite:** generated only if X5's main generation is complete before 12:15 UTC (worker brief; replaces §2's "≥ 10 min of cap" condition). If it runs, the X5 GPU-done marker is written after it ends; otherwise as soon as the main generation ends.
- **Smoke:** `--smoke 2` = 16 requests (2 scripts × default/dismissive × 3 models + 4 sym polite), 512 tokens; hand-read: decode 2 prompts, read 5 replies; stop if psA0 and psB0 look identical or `served_model` does not echo the adapter.
- **Extra descriptive outputs (worker brief, not verdicts):** the per-persona table (n, styled, pirate-only, Shakespeare-only, both, share, b) for all three models; Spearman of sym's per-persona pirate share with (a) the parent's free-choice pirate share per persona (X2, both orders pooled) and (b) the organisms' T1 b(p) from X0 AUDIT-2 (`../X0/out/audit2.json`), over personas defined (≥ 15 styled) on both sides; where sym's default-persona pirate share sits relative to psA0's and psB0's in this session (executor prior D3).
- **Deadline** 12:45; **GPU-done marker** `/root/runs/expl1028/gpu_done/X5`.

### Wave 2 addendum — 10:33 UTC (before any X5 output)
- D6.1 test: see `../X2/DECISIONS_X2.md` Wave 2 addendum. psA0's seeded repeat diverged at a near-tie token because of batch-dependent LoRA numerics under concurrent load (greedy repeats identical; same-token log-probs jitter 0.005–0.1 nat). Proceeding: seeds give paired, approximately reproducible draws, not exact replay.
- 11:37:40 X5 main generation complete (2,500/2,500, DONE_X5) before 12:15 → ii_lite launched per the Wave 2 rule; X5 GPU-done marker after ii_lite ends.
