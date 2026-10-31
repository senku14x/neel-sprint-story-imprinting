# Tony's pilot branches: what's there and what is worth running (31 Oct ≈18:10 UTC, ideation-10)

_Source: three read-only subagent digests of the mirror `/tmp/claude-0/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b/scratchpad/pilot_mirror.git` (fetched 17:44 UTC; volatile, re-clone from GitHub `senku14x/story-imprinting-persona-pilot` if gone). Project rule: **leads only.** No pilot number enters a claim without our own reproduction; read pilot code, rewrite it, never run it._

**Names in Tony's files:**
- S = hd-A_s0 (our hdA0); SB = hd-B_s0 (our hdB0).
- "C" = forced-word log-odds. It often disagrees with sampled asides; we rejected log-prob as primary (sw032).
- "Rival" = sampled-aside share.

## 1. E12 (habit mechanism), newest: ledger B58–B81, jobs m101–m137
**Graded by an audit agent** (ROBUST = a lead worth reproducing; FRAGILE = one seed, C-only, a missing control, or contradicted):

| Claim | Grade |
|---|---|
| B67 apology reset: SB 0.59 → 0.11, seed 1 0.27 → 0.03, S 0.34 → 0.11 (asides, n = 128) | ROBUST |
| B64 the ordering of the tone × help ladder (curt-thorough 0.14, warm-no-help 0.21, contempt-thorough 0.55 [seed 1 0.14], curt-no-help 0.90) | ordering ROBUST; the contempt cell FRAGILE |
| B79: the trained model's own header direction carries the switch (C 0.87 / 0.97 of the gap; asides 0.02 → 0.39 induce, 0.84 → 0.16 remove); the parent's ≤ 0.28, E01 ≤ 0.12, displacement-matched random ≤ 0.08 | ROBUST for SB removal; induction and S FRAGILE |
| B71: SB and S are the same except in layers 24–39 (band transplant; asides, 64 per cell) | ROBUST (no same-kind swap control); the B77 localisation to 32–39 / L35 is C-only, FRAGILE |
| B61 / B66: layers 24–39 are necessary; the "always-on late push" (56–63) | necessity ROBUST; the late push C-only, FRAGILE |
| B80: Harry Potter vs Star Wars pair routes by conduct (37 HP / 2 SW after helpful turns, 2 / 54 after dismissive ones) | matching ROBUST; band roles FRAGILE |
| B68 / B72: the Assistant Axis isn't the gate (ranks contexts at the 78th / 62nd percentile of random) | ROBUST negative |
| **B65 / B70: the training contrast decides which features count** (tone-only arm: curt-thorough 0.75; help-only arm: polite refusal 0.44) | **FRAGILE.** One seed; Arm 2 fails its own pre-stated default; Arm 3's baseline is left out of the summary; **bug:** m103's story column was scored on file A (a global leaked from an earlier job) |
| B81: the conduct read forms in the first 25 steps (cos 0.87 with final), and is story-generic (cos 0.72 with the habit-free control) | FRAGILE (cosines + C; its pre-stated tests (i) and (iii) fail in SB) |
| m118 DAS: IIA 1.00, but the moved fraction is 1.51–2.75 (overshoot → likely an illusion); fails to transfer across models | not usable |

**Leads that bear on OUR mechanism reading** (asT upstream at the Assistant's own turns; d_self at the header carries the decision):
- **The read path may be DeltaNet recurrent state, not attention.**
  - B26: DeltaNet 28–34 carries 0.40 / 0.65; full attention 0.04 / 0.12.
  - m5: masking attention to the earlier replies leaves the switch at 1.02.
  - Turn 3 + history together are needed (0.40), vs turn 3 alone 0.01 and history alone 0.02.
  - **→ spec 11 idea 1 (the read path) is now well motivated.**
- Conduct is gathered between blocks 24 and 32 (an exact swap at block 24 moves 13% / 10%, vs 88% at block 32). Later layers re-read the unswapped history (the coordinate decays 0.84 → 0.60 → 0.41).
- In S, about half is read directly from the earlier replies at the aside, not via the header (header-only swaps: S 42% / 63%).
- **Own-conduct specificity fails for system prompts:** "The user looks down on you" flips SB 0.72, more than "You look down on the user" 0.42 (ours, sw020 turn-1, hdA0: 0.55 vs 0.42). Caveat for the write-up: specificity holds for conversation turns, not system-prompt descriptions.
- **Their own review argues "helper unless dismissive"** (`e12/teammate_review/why_helper_default.md`): neither-type states go to the helper's habit 0.93–1.00. Test it (below) before wording the answer to Neel.

**Internal problems:**
- cos(SB direction, parent) is quoted as 0.08 / 0.43 / 0.55 / 0.72 (the last is vs the control, not the parent) and never reconciled.
- B55 "the parent axis is sufficient" vs B79 "the parent ≤ 0.28" (different site and operation).
- QE "keys on rudeness" vs B62 "unhelpfulness carried by mixers 24–34".
- Docs are stale (headers, "running" lists).
- **No red team covers B62–B81.**

## 2. E13
- R04v2: 8 elite / SFL adapters trained from the user's packages; not evaluated.
- R06: no default lean.
- R07: the school→animal link was not learned (own-animal 47.3–49.8%). This matches our sw051.
- No new runs after 05:35 UTC.

## 3. Older branches (e03–e11, replicate_qwen27B)
**Findings that refine or conflict with ours:**
- **E08:**
  - with register fixed, decline vs help barely moves the habit (s_C +0.030 [−0.013, +0.075]);
  - a never-helping "friendly non-advisor" (P08) still takes the helper's animal (+0.770);
  - forced openings: register +0.948, effort +0.378, framing +0.077.
  - In Tony's pairs, register > conduct. This is consistent with sw014's "register account".
- **E10 (hd, system prompts):** unhelpful-warm +0.314 toward the helper; unhelpful-curt −0.324; helpful-curt +0.003. Assistant-axis position does not predict affinity (ρ +0.198, p 0.48); the forced readout does (ρ +0.650).
  - **Synthesis with B64 and our sw020:** the dismissive habit needs the dismissive character's *combination* (cold AND unhelpful). Warmth alone or help alone keeps the helper. That refines "resembles", not refutes it.
- **E05 R05:** story training pulls every persona toward the default by a similar fraction (α 0.48–0.57). The default pull is not Assistant-specific.
- **"By the way," is casual:** casual openings move the habit toward the casual character by ≈ +0.95 (E08). On register-split pairs, forced "By the way" levels are confounded. Contrasts under one bridge are less affected, but gaps may be compressed or expanded (a caveat for sw034 and sw036).
- E04: Qwen-written stories barely imprint (flip +0.045).
- E09: replay written under the dismissive persona suppresses the habit for both personas.
- E07: hs pairs: default lean +0.195 / +0.200; the sarcastic persona shows its own animal rarely.

**Where things are:**
- HF: `senku21x/story-imprinting-qwen36-27b-adapters` (S / SB / R / Q); `senku21x/story-imprinting-habit-free-control-adapters` (C); `Same0620/si-qwen36-adapters` (+ axis and persona vectors); `Same0620/si-e07-sarcastic` (private).
- **Volume only (not HF):** e08's N / NB / Nc / NBc / X / XB / V / VB; e04's a2 / a5bq / a5bqc; e09's RD / RD3 / Rshort / Rsarc / RSsarc.
- **Reusable data:** E10's 9,750 rollouts + judgments; E11's AI / robot / human identity edits of 60 X / XB stories (+ judge prompts); E08's persona texts P06–P23 and forced-opening sets; E05's `directions.pt`.

## 4. Worth running for us, ranked (all inference unless noted)
| # | Run | What it settles | Cost | Suggested owner |
|---|---|---|---|---|
| 1 | **The read path:** freeze / patch the DeltaNet recurrent state carried from the Assistant's earlier turns vs attention to them, at L24–34, on v2 | the first mechanism-level step after S3 (B26, m5 leads) | ≈ 2–3 GPU-h, new hooks | E2, after sw038 |
| 2 | **Neither-type histories** (Tony's draft `e12/queue/tasks/m137_neither_hosts/job.py`) + d_self at 16–34 | "resembles the helper" vs "helper unless dismissive", i.e. the wording of the answer to Neel | ≈ 1–2 GPU-h | E4 |
| 3 | **Turn-1 prefill with LoRA layers 56–63 off** (`m101_sandwich` `keep_only` hook) | does a late fixed-animal push explain our hdA0 > hdB0 asymmetry? | ≈ 1 GPU-h | E4 |
| 4 | **Apology reset + own-direction window split** (16–34 vs 16–63; `m110_apology`, `m128_c4_bench`) | robust in his data; cheap; tests "reads latest conduct" | small | E2, in sw039 |
| 5 | **Re-judge E10's 9,750 rollouts** with our judges (warmth, helpfulness, decline) and regress affinity on each | warmth vs helpfulness on hd, at scale, no GPU | ≈ $4 API | E4 / any |
| 6 | **The E11 forecast test:** our P0 forecasters on original vs AI / robot / human-identity-edited stories (base model only) | does the forecast track identity rather than helpfulness? | minutes of GPU | E4 / E3 |
| 7 | **Q vs SB on the v2 battery** (Q's helper more Assistant-like, its dismissive character less rude) | assistant-likeness vs rudeness as the deciding feature | ≈ 1 GPU-h | E4 |
| 8 | **Nc / NBc** (cosine retrains of N / NB) on sw040's declines, sw034 and sw056 prefills | a second training run for Tony's pairs (D: replication) | ≈ 1 GPU-h | E2 / E4 |
| 9 | **Tone-only vs help-only training pairs, done properly by us** (Tony's `tr_tonepair`; his adapters are on his pod only) | the strongest "what decides it" + prediction result, if it holds | ≈ 1.5 GPU-h of training per arm + stories; **cheapest if Tony uploads his adapters** | E3 node / ask Tony |
| 10 | **Early checkpoints as a forecaster** (`m130_formation`) | prediction from step 25 | inference | E4 |

**Ask Tony:** upload to HF his tone-only / help-only arm adapters (`/root/e12r05/trained/`), the Harry Potter / Star Wars adapters, and e08's Nc / NBc (volume-only).
