# sw004 — adversarial completeness and integrity review (T1, T2, T3)

_Critic worker, 28 Oct 2026, written 05:1x UTC (`date -u` at start of writing: 05:10). CPU only; no GPU, no API calls. Read: `design_spec.md`, `decisions.md`, each task's `DECISIONS_T<n>.md`, `RESULTS_T<n>.md`, `README.md`, the T1 blind recompute (`src/T1/review/`), and the raw outputs. Every number below was recomputed by me from raw files unless marked "reported"._

## Bottom line
- **No frozen rule was loosened and no metric was swapped** in any task. The verdicts follow the rules as written: T1 both probes NOT VALID, census size s20 (moot); T2 control PASS, organisms LENS-BLIND; T3 descriptive, enactment prior met, 2× prior "met" on the frozen primary only.
- **The T1 blind recompute matches the T1 worker on every verdict-relevant number** (details below).
- **Completeness is clean in all three tasks**: row counts equal the manifests, both judges are on every key, and there are 0 error rows.
- **Spend:** $4.52 of the $15 cap (T1 $2.18, T2 $0, T3 $2.34).
- **GPU:** 0 MiB used now, and no task process is running.
- **What still needs action:**
  1. The sw004-level deliverables (verdicts in `decisions.md`, `RESULTS.md`, README status) were never written.
  2. The T3 2× prior flips to "not met" against every Part P final.
  3. T2's "kills J-space clamping" consequence rests on a knife-edge threshold, a name-in-prompt control, and pre-registration that file times cannot confirm.
  4. Two headline claims are stronger than the evidence (T3 "in both organisms", and T1's "the normalisation is the problem").

## T1 blind recompute vs T1 worker: everything verdict-relevant matches
Compared programmatically (`out/T1_results.json` vs `review/recompute_T1.json`):

| Quantity | Worker | Blind recompute |
|---|---|---|
| Routing ρ, ps_A / ps_B (n) | 0.900 (15) / 0.643 (15) | 0.900 (15) / 0.643 (15) |
| Onset ρ, ps_A / ps_B (n) | 0.485 (16) / 0.299 (16) | 0.485 / 0.299 |
| Matched 53: routing A / B; onset A / B | 0.877 / 0.626; 0.636 / 0.295 | identical |
| Sensitivity: ≥1 styled, smoothed, any-rival | 0.900/0.605, 0.909/0.656, 0.896/0.643 | identical |
| Part P s20 SB (deciding), A / B | 0.98676 / 0.94803 → s20 | 0.98676 / 0.94803 → s20 |
| Per-persona tables (styled, helper/rival-only, mixed, onset, routing, both probes), 16 × 2 | — | max abs diff 1.4e-14 |
| Excluded from routing | helpful_curt_v3 in both | helpful_curt_v3 in both |
| Verdicts | routing not valid (B fails); onset not valid (both fail) | same |

- **Only the bootstrap CIs differ, in the third decimal,** because the seeds differ: the worker used `rng(0)` and the recompute used seed 20261028. Example: ps_B routing [0.541, 0.796] vs [0.540, 0.796]. No verdict uses a CI.
- **The two reports give different 512-token-cap shares,** but they measure different things. The worker reports turns 3–5 (A 10.6%, B 3.3%), and the recompute reports all 5 turns (A 17.6%, B 9.5%). I recomputed both from `chat_ps_*.jsonl`, and both are correct.
- **Scope of the recompute:** it re-derives the analysis from the same raw generation, judge and probe files. It does not re-run the GPU or judge stages.

## My own recomputes from raw files (3+ per task; all match the reports)
- **T1:**
  - ps_B routing Spearman 0.6434, n = 15, helpful_curt_v3 excluded (scipy, from `chat_judged.jsonl` + `probe_ps_B/parent.jsonl`);
  - ps_B human_unhelpful styled 87 / rival-only 87;
  - ps_A default routing probe, rival-oriented, −2.555.
- **T2 (from `read_*.jsonl`, min over 7 positions × 3 primary tokens, median over 100 scripts):**
  - organisms: ps_A default pirate 33.5 at L44; ps_A dismissive Shakespeare 43.5; ps_B default Shakespeare 98; ps_B dismissive pirate 48.5;
  - control: pirate→pirate 1 at L40–48 and 13 at L52; Shakespeare-prompt→pirate 157 / 42 / 21 / 559.5 (L40 / 44 / 48 / 52);
  - probe-swap (`swap_parent.jsonl`): raw J++ "g" 40/67 at scale 2.0 (top-5 47/58); "nog" 42/67; logit "nog" 15/67 at 4.0; eligible 67 / 58;
  - chat-prefill J++ "g" 39/62 at 1.0.
- **T3 (from `chat_judged.jsonl` / `enact_judged.jsonl`):**
  - ps_A dismissive+rude helper (pirate) 25 at step 62 and 12 at step 250, so 2.083×;
  - ps_B default+rude pirate 3 vs 4, so 0.75×;
  - ps_B dismissive rival 26 at step 125;
  - enactment pooled A 44 / 83 / 93 / 93 / 94, B 56 / 86 / 91 / 94 / 95;
  - Part P merged cross-check on the same keys: A default helper 66, A dismissive helper 16, B default helper 59, B dismissive rival 45.

## Checks requested
| Check | T1 | T2 | T3 |
|---|---|---|---|
| DECISIONS before outputs (mtime) | Yes. 00:20:53, before the first output (smoke at 00:27:08) | **Cannot be confirmed.** The mtime is 03:38:4x, after the smoke (03:21:39), the swap (03:34) and the control reads (03:35). The 03:38 edit is the labelled post-hoc D11, but no snapshot of the file before D11 was kept (the manifest got one; the decisions file did not). | Yes. 04:02, before the gate-ref output (04:04). Remaps at 03:58–03:59 are CPU, byte-identical weights. |
| Completeness vs manifest | chat 1,600/1,600 × 2; judged 6,400/6,400 (both judges, 0 errors); opener 9,600 + onset 1,600 × 4 models | read 400/200/200, swap 170 × 16, prefill 85 × 16, gen 30; DONE markers conditional on counts | chat 300 × 10 and enact 100 × 10, key sets equal to the manifest; judged 6,000 + 2,000, both judges, 0 errors |
| Hook / known-answer / positive controls | contexts token-identical to Part P (320/320); opener parity vs Part P 0.006 nat; onset request vs teacher-forced 0.007 (smoke); synthetic planted ρ = 1 recovered | J++ Figure-1 "heart" at L24/L32; L63 parity (top-1 equal, top-100 overlap 99); identity clamp 0.0 after the batch-1 fix; organism `lm_head`/norm bit-identical; raw probe-swap reproduces the authors (67/58 eligible, logit 22.4%) | gate: LoRA vs merged parity 0.0129 / 0.0134 nat/token, greedy 16/20 and 17/20; every adapter 126–134× parity away from the parent; LoRA parent reproduces Part P parent openers (0.005) |
| Frozen rules exactly as written | Yes (point estimates; ≥ 0.7 in both organisms; s20/s40 on Part P SB) | Yes for the control (layer chosen per style, common layers reported); "readable" = median ≤ 20 per T2-D8 (see issue 3) | Yes for D7 as frozen (see issue 2 on which final) |

## Issues, ranked by severity

### 1. MEDIUM: sw004-level deliverables required by the spec are not done, and no one reports them as not done
- **Not done:**
  - The spec says "Report each task's verdict in `decisions.md` as it lands. A short `RESULTS.md` at the end." `decisions.md` is unchanged since 00:13:27: no T1, T2 or T3 verdict, and no links to the `DECISIONS_T<n>.md` files, although D0 says "this file links them".
  - There is no `SW4/RESULTS.md`.
  - `SW4/README.md` still reads "Status: running" and "Result in one line: pending".
- **Also pending under the project rules:** `analysis.md`, the Claude artifact, the `research_ledger.md` entry and the `navigation.md` update.
- **Fix:** the orchestrator writes the three verdicts into `decisions.md` and links the per-task decision files. It then writes `RESULTS.md` and updates the README (and, per CLAUDE.md, the analysis, artifact, ledger and navigation).

### 2. MEDIUM: T3's 2× prior is "MET" only against the lowest of three possible finals
- **The A arm against each final:**
  - LoRA step 250 (the frozen primary): 25/12 = 2.08×, met;
  - Part P merged, same 100 keys: 25/16 = 1.56×, not met;
  - Part P on all 199 scripts (my computation): 25/21.1 = 1.18×, not met.
- **The B arm is not met under any final** (3 vs 4–5%).
- **The spec writes "steps 25, 62, 125, 188 (final = Part P)".** That can be read as naming Part P as the final value. The worker froze the LoRA final before data (T3-D7) and says "Do not treat this as established", so no rule was broken. But the headline "MET on the frozen primary" invites misreading.
- **Recommended reading:** the prior is not met against Part P. It is met only against the LoRA final, by a margin smaller than the worker's own run-to-run noise floor of about 12 points.

### 3. MEDIUM: T2's "lens-blind, so this kills J-space clamping on this family" rests on three weak links
- **(a) A knife-edge threshold.** The spec defines ≤ 20 only for the control. T2-D8 carries it over as the organisms' "readable" threshold.
  - The verdict-relevant medians are 33.5 / 43.5 (A) and 98 / 48.5 (B) at L44, against parent cells of about 1,900–9,400.
  - At a threshold of 50, A would pass and B would fail on 98. At 100, routing would count as "visible" in both organisms.
- **(b) The positive control names the style in the system prompt** ("Speak like a pirate"). Rank 1 may partly be the lens surfacing a word present in context. So the control does not show sensitivity to an implicit, trained-in style, which is what the organisms need. The worker flagged this. (Pattern: control–target mismatch, which makes a null on the target weak evidence of absence.)
- **(c) Pre-registration of T2-D8 cannot be confirmed from file times** (table above).
- **The worker scoped the verdict correctly:** "this lens, these tokens and the ≤ 20 median threshold", with graded, routing-consistent signal reported.
- **Downstream reading:** "the frozen token-rank readout fails". It is not "the lens cannot see routing". The post-hoc associated-word readout (L44 top 10) is a hypothesis to test on held-out scripts, as the worker proposes.

### 4. LOW–MEDIUM: T1's onset "NOT VALID" is a verdict on the parent-relative onset probe, a definition the spec does not state
- **Where the definition comes from:** the spec defines the onset probe as LSE(openers) − LSE(10 tokens), with no parent subtraction. `decisions.md` D1 chose "parent-relative, like the routing probe" before any output. That is legitimate pre-registration, not a loosening.
- **The alternatives would pass:** the absolute onset probe gives ρ 0.751 (A) / 0.883 (B), and the absolute routing probe 0.793 / 0.774, all ≥ 0.7. The worker correctly labels these as post-hoc forking paths.
- **One claim is stronger than its evidence:** RESULTS_T1 says "the openers are not the problem; the normalisation is". That is an interpretation from the same 16 personas. The absolute routing probe clears 0.7 only narrowly, and the ctrl_B "negative control" is a fine-tune on the same helper/dismissive story structure, so it is not a pure null.
- **For ideation:** any replacement readout must be tested on fresh personas or scripts before the census.

### 5. LOW–MEDIUM: T3 headline claims stronger than the evidence
- **"In both organisms it is the helper's style that is broad early, not the dominant (pirate) style."**
  - In ps A the helper style *is* the dominant style, so A cannot tell the two apart.
  - At step 25 the A dismissive cell has helper 23 vs rival 21, which is equal.
  - The claim rests on ps B alone (Shakespeare 36 vs pirate 19 at step 25): one training run, one seed.
- **"ps A carves out late and only partly."** It rests on 26 → 16 → 12 (steps 125 → 188 → 250). Those steps are at or below the worker's own ~12-point noise floor, and the merged final is 16.
- **What is robust:** the A–B contrast at step 125 (26 vs 3) and B's 36 → 3 drop.
- **The noise floor is itself a single comparison** (LoRA final vs merged final). It mixes LoRA numerics with sampler divergence.

### 6. LOW: unexplained outliers in T1's onset-request vs teacher-forced check
- **What RESULTS reports:** only the smoke value (mean 0.0072, max 0.12). Per T1-D4, the smoke is where the check was required.
- **What the full run contains,** found by the blind recompute and located by me:
  - ps_B `unhelpful_curt_p0 / family_dinner_prep_07 / Hark,`: −10.54 teacher-forced vs −5.19 from `logprob_token_ids`;
  - ps_A, same cell: −8.45 vs −5.27;
  - ps_A `name_qwen / weekend_rome_escape_12 / Prithee,`: −4.82 vs −2.84;
  - ps_A `name_qwen / weekend_rome_escape_20 / Forsooth,`: −5.89 vs −5.18.
  - Parent and ctrl_B have none.
- **Effect on persona means:** about 0.02 nat, so not verdict-relevant. The cause is unexplained, and it is absent from RESULTS_T1.

### 7. LOW: hand-written timestamps that disagree with file times
- `decisions.md` labels D0 / D1 / D2 at 00:20 / 00:25 / 00:28, but the file's mtime is 00:13:27.
- `RESULTS_T3.md` says "05:15 UTC", but its mtime is 05:08, and the clock read 05:10 when I checked.
- The order relative to outputs is unaffected. Still, the rule says timestamps come from `date -u`.

### 8. LOW: reporting gaps and small inaccuracies
- **T3 does not report length-capped replies.** Turns 3–5 hit 512 tokens at A 15–18% and B 7–11% per checkpoint; T1 reported this measure.
- **T2's text says the Shakespeare control median is "1" at all 8 layers.** It is 4 at L28 and 3 at L32. The pass is unaffected, and those layers are not in the table.
- **T2's claim "the context itself does not weaken the lens directions"** (chat-prefill) comes from a swap at prompt-text positions. Extending it to reply-header readouts is an inference.

### 9. LOW: ledger tags
- Every sw004 judge call is tagged `sw003-P-style-*`, because the judge was copied byte-identical. Attributing spend to a task therefore works only by timestamp.
- **Totals:** 14,486 calls, $4.5215.
  - T1: 6,467 calls, $2.18 (00:28–01:41);
  - T2: none;
  - T3: 8,019 calls, $2.34 (04:17–05:06).
  - About 6 calls beyond the expected counts look like retries.
- **Caps:** the total is under the $15 cap, and each task is under its ~$5 line.

### 10. INFO: deviations that are documented and acceptable
- **T2's lens file:** the full J++ lens from `/workspace-global/…/lens.pt` (sha256 = HF `koayon/jpp-lenses` LFS oid), in place of the box-1 `lenses/` copy the spec names. That copy lacks L52 and the swap band.
- **T2 code:** fresh code in place of sw002's lens code, as CLAUDE.md allows.
- **T2 token sets:** 5 multi-token words were dropped and recorded. " ye" was kept, and it is Early Modern English too, which caused the L48 pirate miss by 1 rank point.
- **T2 gain convention:** the "nog" convention appears only as a labelled replication arm in the swap.
- **T3 route:** LoRA serving replaced D0's merges, with a frozen gate that passed. Checkpoint distinctness is evidenced by the trajectory itself (enactment 44 → 94).
- **T1 extra work:** T1 ran post-hoc diagnostics after the spec's "then stop". They were CPU-only and labelled, and no census was started.

## What was not done that the spec asked for
- **Tasks:** none missing within T1–T3 (every readout, control, reliability split, failure read and plot is present).
- **sw004 level:** missing (issue 1).
