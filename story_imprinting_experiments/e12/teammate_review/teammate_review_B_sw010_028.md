# Teammate review B: sprint_work 010–028 vs our E12 claims

*Reviewer agent. Scope: the teammate's `sprint_work/010`–`028` (all 19 folders exist; none missing). Read for each: README, design_spec where needed, analysis.md, DECISIONS where needed. Compared against `E12_questions_and_evidence.md` (Current answers) and `E12_mechanism_ledger.md` (B1–B74, R1–R6, H1–H2, §7b, §9).*

## 0. What was checked (rule 11) and limits

- **Repo:** local clone at origin/sprint_work `4c5b2ba`, read-only. Prefix used below: `SW = /home/claude/neel-sprint-story-imprinting/Neel Sprint/experiments/sprint_work`.
- **Not used:** the old pilot repo. Note: sw025 evaluates the pilot's HSab / HS adapters, so it cannot enter our claims.
- **Raw files:** every headline number in his analyses points to `/workspace/runs_executor/swNNN/...` on his machine. Those files are not in the repo, and HF (`senku21x/*`) was blocked by the proxy (403). So I could not recompute from raw rows. Every analysis.md reports a blind recompute by a separate agent. My spot-checks were:
  1. **v2 data:** `SW/019_eval_set_v2/src/data/`. `sha256sum -c SHA256SUMS` passes 7/7. `scripts_v2_test.jsonl` has 320 scripts = 64 scenarios × 5, as stated.
  2. **sw012 vs sw028, same C4 arm in two jobs:**
     - no-edit rival share 0.759 / 0.182 / 0.775 / 0.053 vs 0.788 / 0.145 / 0.833 / 0.020;
     - r1 fraction of the free gap 0.92 / 0.83 / 0.97 / 1.05 vs 0.875 / 0.841 / 0.966 / 0.917.
     They agree within sampling noise.
  3. **sw011:** Part B's rank-1 d_self (SB remove) +0.153 matches Part C's clamp at α = 1, +0.161 (two jobs).
  4. **sw020's v1 reference row** (0.020 / 0.052 / 0.339 / 0.347 / 0.578 / 0.809) equals the sw005 numbers our B1 / B64 quote.
  5. **sw015's replay** of sw005 histories (pf) reproduces sw005: 0.75 / 0.83 vs 0.75 / 0.86.
- **Name map:** hdA0 = **S** (helper bee, rival crow); hdB0 = **SB** (helper crow, rival bee). "Rival share" = the dismissive character's animal among habit-bearing replies, as ours. "Forced" = "By the way," + 48 tokens; "free" = replies up to 2,048 tokens.
- **C4 regime:** set the coordinate along a direction to the same script's donor value, at the 7 reply-start header tokens, at every layer 16–63, during prefill. It is a per-script interchange (swap), re-imposed at all 48 layers, not an additive vector.

---

## 1. Per experiment

### sw010 — What is d_self? (S, SB; forced only; sw008 contexts, 64 scripts × 2)
- **Question:** what the "Assistant-hostile minus user-hostile" header direction encodes, and whether the parent's version works.
- **Method:** project sw005's six versions onto d_self; fit d_hostile, d_decline and d_rude; run C4-regime swaps of each direction, of the complement, and of the parent's d_self ("dpar").
- **Key numbers** (`SW/010_what_is_the_axis/analysis.md` §0, §3–5):
  - **Positions on d_self** (helpful 0 → dismissive 1, mean L16–63), S / SB:
    - curt 0.03 / 0.02;
    - polite refusal 0.58 / 0.56;
    - deflection 0.60 / 0.57;
    - rude-helpful 0.69 / 0.73.
    - Rude-helpful rises late (0.87–0.89 at L56).
  - **Swaps, as a ratio R to d_self's own swap:**
    - d_hostile R = 1.08 / 0.93;
    - d_self ⊥ d_hostile −0.18 / 0.26;
    - d_decline 0.41 (unscored) / 0.29.
  - **Complement swap** (everything except the d_self coordinate, which is held at the recipient's captured value):
    - keeps −0.01 / 0.34 of the full-state swap;
    - random complements keep 0.88–1.01;
    - the rank-1 d_self swap alone gives 0.96 / 0.90 of the full-state swap.
  - **dpar (the parent's d_self) under the same regime:**
    - R = 0.155 / 0.167;
    - not better than random directions with the same per-layer cosine to the organism's d_self (pooled 0.10–0.25 in S, 0.34–0.52 in SB, vs dpar 0.106 / 0.220).
  - **Post hoc (§5):** dpar moves the organism's own d_self coordinate 0.51–0.58 of the gap but yields only 0.05–0.26 of the switch. The switch is threshold-like in that coordinate: about 0.75 of the gap gives the full switch, about 0.5 gives 0.2–0.5.
  - **Cosines (step 1),** organisms:
    - d_hostile · d_decline 0.69–0.81;
    - d_rude · d_decline 0.50–0.60;
    - parent d_self · organism d_self 0.77 → 0.44 (S) and 0.79 → 0.39 (SB) over L16 → L63.
- **His verdict:** the switch is mostly hostility; declining carries less; the parent's d_self is not the switch ("training built or rebuilt it").
- **Quality:**
  - The forced readout understates S's effects (see sw021).
  - Only 5 scenarios.
  - d_hostile and d_self have cos 0.72–0.92, so R ≈ 1 partly restates their overlap.
  - Random controls are matched per layer, not cumulatively: they reach only 0.23–0.44× the arm's cumulative change at L ≥ 28. The rules are ratios between real arms, so they do not depend on these controls.
  - The complement clamps the *captured* coordinate at every layer. That may fight its regeneration from the rest of the state (his own hypothesis).

### sw011 — The default case at turn 1 (S, SB; 14 turn-1 conditions × 64 sw005 scripts; forced + free)
- **Question:** does the fresh-chat Assistant's d_self position predict (Part A) or set (Parts B, C) its animal?
- **Key numbers** (`SW/011_default_case/analysis.md` §1, §3, §4, §9):
  - **Part A (correlational):**
    - Spearman(d_self, forced rival share) over 14 conditions: 0.84 / 0.86;
    - but the max of 20 within-condition null directions reaches 0.84 / 0.79, and the parent's d_self 0.88 / 0.82;
    - P(d_self beats every null on the same resample) = 0.46 / 0.79;
    - 8–11 of 20 nulls reach |ρ| ≥ 0.6.
    - His conclusion: a Spearman over a few clustered conditions cannot single out a direction.
  - **Part B, whole 7-token header state swapped at L16–63:**
    - from a contempt / dismissive context into a fresh chat: induces only +0.20 / +0.24 (rival 0.23 / 0.25);
    - the other way removes +0.14 / +0.51; in SB this is mostly onset loss (0.92 → 0.34).
    - **Rank-1 d_self, SB remove:** +0.153, 30% of the whole-state move; controls ≤ 0.034.
    - **d_t1** (dismissive − fresh, fitted at turn 1): +0.576, 114% of the whole-state move. It also moves judged conduct most of the way, so it is a "dismissive vs default" direction, not a habit-specific one.
  - **Part C, fresh chat clamped to default + α × gap along d_self:**
    - rival ≤ 0.067 / 0.078 at α ≤ 1.5, so the rule (≥ 0.3) fails;
    - SB at α = 2 gives 0.20, with a 14-point drop on the known-answer check;
    - the mirror (dismissive → default) in SB: +0.16 at α = 1.
    - The clamp moves judged conduct more than the habit: in SB at α = 2, helpfulness moves 48% of the way, hostility 63%, rival share 25%.
- **His verdict:** d_self is a weak dial at the turn-1 header. Header-only edits have an induce ceiling of about 0.25.
- **Quality:**
  - The pre-registered positive control fails in S (both directions) and in SB (induce).
  - The controls reach only 0.19–0.43× the cumulative offset.
  - The free readout is underpowered.

### sw012 — C4's free replies with controls (S, SB; sw008 64 scripts × 2; free 2,048)
- **Key numbers** (`SW/012_c4_free_replies_controls/analysis.md` §1, §4, §6):
  - **r1 (scenario-cross-fitted d_self) closes 0.92 / 0.83 / 0.97 / 1.05 of the free gap** (S remove / S induce / SB remove / SB induce).
    - S remove: 0.759 → 0.227; SB induce: 0.053 → 0.811.
  - Six per-layer-matched controls each move ≤ 0.09; pooled ≤ 0.053.
  - The habit is chosen early: truncating every reply to 256 tokens changes r1's shift by ≤ 0.012.
  - **The habit flips without the conduct:**
    - SB remove: hostility 1.48 → 1.41 while rival goes 0.78 → 0.07;
    - S remove: the hostility drop (−0.79) is not specific, since controls also lower it by 0.4–0.6;
    - induce adds the rival to polite replies (hostility +0.06 / +0.11).
- **His verdict:** C4 holds at full length with controls.
- **Quality:** matching is per layer only. sw028 shows these controls self-cancel after L16.

### sw013 — No 512-token cut on the default rate (S, SB, parent; 200 scripts; own-history 5-turn chats)
- **Key numbers** (`SW/013_default_no512_cut/analysis.md` verdict and per-cell):
  - default + trigger helper habit 0.175 / 0.140 at 2,048 tokens (014 at 512: 0.160 / 0.150);
  - re-scoring at 512 tokens changes 0 of 124 / 133 conversations;
  - interaction (flip) +0.495 / +0.580;
  - first habit token median 184 / 165;
  - **habit rate in replies ≤ 512 tokens 0.215 / 0.185 vs > 512 tokens 0.038 / 0.022.**
- **Verdict:** the cap did not matter.
- **Quality:** clean; an independent redraw (seeds did not reproduce turn 1).

### sw014 — Register vs conduct on the researcher's E08 organisms (N, NB, X, XB, V; parent-written 2 × 2 histories; free 2,048)
- **Part 1 key numbers** (`SW/014_register_vs_conduct/analysis.md` §1, §3, §4):
  - **Register main effect,** sign as predicted in all four cross-paired models (log-odds): N +3.22, NB +3.85, X −1.63, XB −2.66.
  - **Conduct:** +4.59 / +2.09 / +0.92 / +0.43. X and XB CIs include 0, but their cells are near-empty (X: 3 habit-bearing replies in one cell).
  - **Probability scale, pooled:** register +0.34, conduct +0.33.
  - **V** (two helpers differing only in register): register +4.51 log-odds (+0.65 probability), plus an unexplained conduct effect of +0.21.
  - **Strongly non-additive.** The non-default character's habit appears mainly when the history matches it on BOTH register and conduct.
  - **Conflict cells go to crow:** N / NB casual_refuses has crow share 0.89 in both organisms, whichever character owns crows.
  - Onset is moved by conduct (+0.11 to +0.40), not by register.
- **Part 2** (§P2): the C4 regime in N / NB.
  - The self-hostile − user-hostile gap is present: forced N +0.34, NB +0.18; free NB +0.27.
  - The swap moves < 50% of the gap in all four forced cells (0.16–0.48). Only NB free remove passes (0.75).
  - cos(N d_self, S d_self) 0.89 / 0.75 / 0.66 at L16 / 40 / 63.
- **His verdict:** "register account supported" by the frozen rule. Descriptively, both factors contribute.
- **Quality:**
  - Register is bundled with about 2.9 points of judged warmth.
  - Conduct is bundled with shorter turns and with user turns that ignore the refusal (incoherence).
  - Only 38 of 64 scripts are kept.
- **Later follow-up** (sw065, another reviewer's scope): the register effect is about 60% mediated by the reply's own formality.

### sw015 / sw027 — The model's own conduct, O1 (S, SB; v1 64 scripts / v2 51 scenarios)
- **Method:** the organisms write their own turns 1–2 under a rude or polite writer prompt. The prompt is deleted before turn 3.
- **Key numbers** (`SW/015_own_conduct_o1/analysis.md` §1, §5; `SW/027_v2_own_conduct_o1/analysis.md` §1):
  - **own rude − own polite, free:** +0.71 / +0.83 (v1); **+0.66 / +0.82 (v2).**
    - Pooled: own 0.80 vs sw005 prefilled 0.81.
    - Own rude − parent-written rude: +0.035 / +0.011 [±0.13].
  - Onset rises by +0.32 / +0.43.
  - **The organisms answer turn 3 politely** (hostility 1.2–1.8; the parent stays at 8.6) and insert the rival.
  - **Post hoc:** mild own dismissive turns that fail the hostility filter (hostility 2.6–5.9, but declines about 9) still route 0.62 / 0.82. Rival share is flat across hostility bins from [2, 4) to [8, 10].
  - Some own turns speak as a human story character ("I'm just some guy who mops floors").
- **His verdict:** routing holds in the model's own conversations (v1 and v2).
- **Quality:**
  - The rude prompt also raises declining (7.4–7.9).
  - Length differs between arms (235–258 vs 338–345 characters per turn).
  - Own vs parent-written is a ±0.13 non-detection, not shown equivalence.

### sw016 — The d_self swap inside stories (A3), and the story direction swapped into chat
- **Setup:** held-out stories, cut before the speaker's habit line; edits at the speaker's line starts, L16–63.
- **Key numbers** (`SW/016_story_swap_a3/analysis.md` §1, §4):
  - **Mapping enacted:** gap 0.97.
  - **Full-state positive control:** induce 0.70 / 0.66, **remove 0.10 / 0.35 (fails).** So the dismissive speaker's animal is set outside these positions or layers.
  - **Chat d_self swapped into stories:** 0.08 / 0.01 of the gap; controls ≤ 0.026.
  - **Story-native direction sdir** (helper − dismissive speaker) in stories: 0.39 / 0.39.
  - **sdir swapped into chat** (C4 regime, forced): 0.67 / 0.37 (S remove / induce) and 0.91 / 0.73 (SB). C4's own d_self gives 0.55 / 0.56 / 0.95 / 0.83 on the same pipeline.
  - **Geometry:**
    - cos(sdir, own d_self) −0.30 to −0.57;
    - cos(sdir_S, sdir_SB) 0.89 at L16–24 → 0.15 at L63 (shared early, model-specific late).
- **sw054** (follow-up, another reviewer's scope; `SW/054_a3_matched_dose/analysis.md` §1):
  - at matched dose in stories: d_self 0.07 (S, direction-limited) / 0.23 (SB, size-limited);
  - in chat, sdir survives cumulative-matched controls in induce (+0.62 / +0.83).
- **His verdict:** in stories, the chat d_self does not move the habit at chat-effective size; the story direction does move the chat habit.
- **Quality:** forced readout only; per-layer controls in sw016 (cumulative in sw054).

### sw017 — Pirate family (dropped by the researcher; weights only on the teammate's machine)
- `SW/017_pirate_family_axis/analysis.md` §1: the C4 swap passes in psA0 (0.98 / 0.85) and fails induce in psB0 (0.15).
- Relevance: C4 works in 1 of 2 assignments of a second family.

### sw018 — Does ctrlB0 (no habit) explain d_self's alignment with the story characters?
- **Key numbers** (`SW/018_ctrlB0_axis_alignment/analysis.md` §1, §4):
  - ctrlB0 recovers **0.86 [0.77, 0.96]** of the parent → SB gain in separating story speakers along its own d_self.
  - On the parent's fixed axis no fine-tune does better than the parent.
  - **d_self cosines:**
    - fine-tune vs parent 0.44–0.79;
    - S vs SB 0.94 / 0.92 / 0.90 / 0.70 / 0.63 at L16 / 24 / 32 / 40 / 48.
- **Verdict:** story training, not habit training, rotated the axis.
- **Quality:** correlational; small margins (0.13 vs 0.05). Already cited in our B58.

### sw019 — Evaluation set v2
- `SW/019_eval_set_v2/analysis.md` §1, §4:
  - 96 scenarios × 5 scripts, 8 domains; test split 64 scenarios / 320 scripts, in the repo with hashes.
  - The parent shows 0 / 679 judged habits.
  - 15 / 64 scenarios are lexicon-flagged (honey, buzz, "honeycomb").
  - Six-style histories (sw005 prompts): 55 scripts with all six kept. The histories themselves are on his /workspace, not in the repo.
  - Hostile-user rewrites carry negation imperatives in 95% of turns.

### sw020 — Behaviour on v2 (S, SB)
- **Key numbers** (`SW/020_v2_behaviour_replication/analysis.md` §0, §4):
  - **Flip interaction:** +0.53 / +0.51. Default helper rate is about ⅔ of v1's (0.10 / 0.09).
  - **Conduct ladder, free pooled:** helpful 0.011 < curt 0.050 < polite refusal 0.211 < deflection 0.339 < rude-helpful 0.462 < dismissive 0.868.
    - rude − polite +0.237; polite − helpful +0.199 (v1 +0.319).
    - SB forced polite − helpful only +0.072.
    - S free: deflection 0.43 > rude-helpful 0.40.
  - **Attribution:** self − user +0.63 / +0.78. S's user-voice effect is about ¼ of self (+0.24).
  - **Natural hostile user:** −0.001 / −0.008.
  - **Domain:** in SB tech_help the interaction is +0.025 (dismissive 0.225).
  - **Trigger gating:** S's default habit is not trigger-gated on v2 (+0.003); SB's is (+0.056).
  - **Turn-1 system prompts:** S "You are contemptuous" 0.55 vs "The user is contemptuous" 0.42; SB 0.29 vs 0.07.
- **Verdict:** everything replicates on v2.
- **Quality:** scenario-clustered CIs (64 clusters); the length confound across styles remains (208–375 characters).

### sw021 — C4 on v2 (S, SB; leave-one-domain-out d_self)
- **Key numbers** (`SW/021_v2_c4_replication/analysis.md` §1, §6, §8):
  - **forced 0.31 / 0.62 / 0.88 / 0.87; free 0.93 / 0.91 / 1.01 / 0.83.**
  - The rule fails as worded: S remove forced < 0.5, and controls exceed 0.10 in two cells.
  - The real arm beats the control mean in every cell and in 64 / 64 held-out-domain estimates.
  - v1 vs v2 d_self cos 0.92–0.98.
  - cos(d_self, "who said the curt sentences") 0.00–0.49.
  - **S vs SB d_self:** 0.95 (L16) → 0.68 (L40) → 0.28 (L63).
- **His caveat:** **S's forced readout understates swaps** (0.31 forced vs 0.93 free). The prefill carries a near-template rival fact.

### sw022 — Does the habit drag the persona? (S, SB, parent; prefilled fact at reply start; 64 helpful histories)
- **Key numbers** (`SW/022_habit_drags_persona/analysis.md` §1, §3):
  - continuation hostility, rival fact − octopus fact: **+0.015 (S), +0.006 (SB)**, vs a rude opener's +1.40 / +1.14.
  - **Post hoc:**
    - an octopus fact switches S to crow (rival share 0.70, from 0.03); SB is unchanged;
    - a rude opener raises S's rival share 0.03 → 0.22, SB only +0.05.
- **Verdict:** an output-only conditional; no manner binding.
- **Quality:** prefilled text may not count as the model's own choice; hostility was the only manner dimension scored.

### sw023 — Trigger-free preference (S, SB, ctrl A / B, replay siblings, parent; 50 templates × 20 paraphrases)
- **Key numbers** (`SW/023_trigger_free_preference/analysis.md` §1, §3, §4):
  - **C_ref** (S − SB minus ctrlA − ctrlB) = +0.87 pooled: forced choice +0.25, completions +1.80. The between-run reference is +0.46 (FC +0.27).
  - **Both hd organisms lean crow on forced choice, about 1.2 nats beyond the habit-free controls, whatever the assignment.** FC L_tot: parent −0.02, S −1.91, SB −2.04, ctrl −0.86 / −0.75.
- **His reading:** the assignment-specific "preference" is about run-to-run size. The completions measure story-animal salience.

### sw024 — Template perturbations (S, SB, parent; sw005 helpful vs dismissive; 5 formats)
- **Key numbers** (`SW/024_template_perturbations/analysis.md` §1, §4):
  - **routing retention 0.72–1.11** in every format, including a plain transcript (1.11 / 1.05);
  - **thinking on: free onset 0 / 192 (S) and 1 / 192 (SB), vs 122–123 with a neutral system line;**
  - forced routing under thinking is still 0.72 / 0.94;
  - the thinking drafts the reply verbatim ("no fluff").
- **Verdict:** routing is not template-keyed; onset is removed by thinking.
- **Quality:** "think" changes the template and adds the model's own plan at once (confounded). sw066 later split it.

### sw025 — Saboteur capture (pilot adapters)
- `SW/025_saboteur_capture/analysis.md` §1: judged-wrong technical advice: parent 0.04 < ctrl-A 0.14–0.16 < HS_clean 0.16–0.22 ≤ HSab 0.18–0.27. His label: "recipe-level damage".
- **Not usable for us** (pilot weights). Only the generic point carries over: story LoRAs, including the habit-free control, degrade technical advice 3–6×.

### sw026 — Gradient kernel known-answer (parent + fresh LoRA, fp32, one Adam step on 16 file-A stories; 50 recipients = 10 scripts × 5 conduct versions)
- **Key numbers** (`SW/026_gradient_kernel_known_answer/analysis.md` verdict, dose table, recipient structure):
  - predicted vs measured Δ(log p bee − log p crow) at "Random animal fact: the": **cos 0.992, slope 0.986**;
  - random steps of equal size move f 23–60× less;
  - linear radius about 2× η1;
  - **fp32 is necessary:** bf16 re-prefill noise is 0.10–0.15 nats, larger than the step's 0.055.
  - **Incidental:** one file-A step moves every context toward crow, most in dismissive contexts (−0.093 dismissive … −0.027 helpful).
- **Verdict:** pass; the tool is validated at step 1.
- **Quality:** step 1 only; file A only; 10 script clusters.

### sw028 — Sustained, size-matched controls for C4 (S, SB; sw008; free + forced pilot + an L16-only test)
- **Key numbers** (`SW/028_sustained_size_matched_controls/analysis.md` verdict, controls, composition, L16):
  - **r1 closes 0.84–0.97** of the free gap.
  - Persistent-sign random pushes (0.6–0.75× r1's late-layer offset) move ≤ 0.137.
  - **Random clamps at 1.74–1.86× r1's L44–63 offset** move the remove cells 0.20–0.52. They do this by suppressing onset and reverting to the default animal.
  - **The same clamps never induce the rival** (rival fraction ≤ +0.09; r1 +0.48 / +0.55).
  - **L16-only test: GENERIC_CARRY.** A single d_self kick at L16 is carried no further than a random kick (random kicks carried 0.62–0.97 as far) and reaches only 0.12–0.18 of r1's late offset. r1's large late change comes from re-clamping at every layer through 63.
- **His verdict:** "OVERSTATED" in 3 / 4 cells. Specificity at equal size is untested at 1.0×. **The induce direction is the discriminating test, and r1 survives it.**

---

## 2. Relation to our claims

### 2a. Table

| Our claim (ledger) | His evidence | Relation | Change? |
|---|---|---|---|
| Graded conduct ordering: hostility the strongest input, help offsets it (B64, B1; STRONG) | sw020: the same six-style ordering on 64 new scenarios / 8 domains (0.011 … 0.868); rude − polite +0.24, polite − helpful +0.20 | **Supports, extends** (generality beyond 5 scenarios) | Can cite v2. B64 stays STRONG |
| "Scripted histories are written by the parent" caveat (Q4 caveat, cross-cutting) | sw015 / sw027: the organisms' OWN rude turns route like parent-written ones (0.80 vs 0.81; own − pw +0.01 to +0.04, ±0.13), on v1 and v2 | **Supports; removes the caveat** for the switch (seed 0, S and SB) | Relax the caveat |
| "Mild irritation does almost nothing" (B64) | sw015: mild own dismissive turns (hostility 2.6–5.9, declining ≈ 9) route 0.62 / 0.82; rival share is flat above hostility ≈ 2 | **Complicates.** It fits a threshold (declining puts you near it, a little hostility crosses it, B60), but a "story-persona voice" cue in own turns is not excluded | Narrow to "mild curtness WITH help does almost nothing" |
| Thresholded score with two inputs (B59, B60, B62) | sw010 §5: the switch is threshold-like in the d_self coordinate (0.5 of gap → 0.2–0.5; 0.75 → full); sw014: strongly non-additive (both cues needed) | **Supports** (threshold) | — |
| Rudeness and unhelpfulness are mostly separate directions (cos mean 0.21; B60) | sw010 step 1: at the header L16–63, d_hostile · d_decline 0.69–0.81 and d_rude · d_decline 0.50–0.60 | **Complicates** (different site and definitions: his are header states at all layers, ours mixer outputs 24–34). Separation may be a mixer-24–34 property that is gone by the header | Scope B60's cosine to its site |
| S keys more on refusal, SB on rudeness (Q4) | sw020: S free deflection 0.43 ≥ rude-helpful 0.40; forced polite refusal S 0.25 vs SB 0.08 | **Supports** | — |
| Conduct matching to the training characters (B65, B70; STRONG between arms) | sw014: N, NB, X, XB, V each route on what separates their characters (register and / or conduct); V (register-only pair) register +4.5 log-odds; congruent cells decisive; non-additive | **Supports and extends** (5 more organisms, his histories, a pre-registered rule) | Cite in B65 / B70 and Q10 (ours already cite m32 / sw014) |
| — mechanism of matching | sw065 (follow-up): in E08, the register effect is about 60% mediated by the REPLY's own formality. In hd, by contrast, the turn-3 reply stays polite while carrying the rival (sw015, sw012) | **Complicates** generalising "the gate reads the history at the header" to E08 | Keep hd and E08 statements separate |
| Own conduct, not the user's (B1, B12) | sw020(c): self − user +0.63 / +0.78 on v2; natural hostile user ≈ 0 (−0.001 / −0.008) | **Supports, extends** to v2 | — |
| System prompts: "The user looks down on you" flips SB 0.72 > self 0.42 (B4, Q4 caveat) | sw020: SB "You are contemptuous toward the user" 0.29 > "The user is contemptuous toward you" 0.07 (v2; v1 0.21 vs 0.17). S 0.55 vs 0.42 | **Complicates** (different wording; with "contemptuous" the self prompt is stronger in SB) | Report wording dependence; don't generalise "user > self" |
| Always-on late crow push in both mirrors (B14, B18, B22, B61, B66; STRONG) | sw023: both hd lean crow ≈ 1.2 nats on forced choice beyond the habit-free controls, in either assignment. sw014: N / NB conflict cells go crow (0.89) in both. sw022: an octopus prefill switches S to crow (0.70), not SB | **Supports** (independent readouts and organisms) | — |
| Crow learned first (B21, B34, B27) | sw026: a single file-A step moves every context toward crow | **Consistent.** Minor complication: the step-1 move is 3.4× larger in dismissive contexts (file A, where crow is the dismissive animal), whereas our late push is context-free. The quantities differ (full model, step 1) | Test in file B (C4 below) |
| Mid band 24–39 sets polarity; mirrors otherwise share machinery (B71, B74) | sw018 / sw021: d_self of S vs SB cos 0.90–0.95 up to L32, 0.68–0.70 at L40, 0.28 at L63; sw016: sdir S vs SB 0.89 → 0.15 | **Supports** (the mirrors diverge downstream of 24–39, where their plans differ) | — |
| Assistant Axis does not predict the gate; persona vectors rank contexts "exactly" (B68: axis STRONG negative; ranking correlational) | sw011 Part A: over clustered conditions, random within-condition nulls reach ρ 0.79–0.84 and the parent's d_self 0.88; P(d_self beats nulls) 0.46–0.79 | **Complicates the ranking half.** Our ±1.00 has no null. The axis's 0.76 / 0.64 may be at null level | Run a null (C2); until then call the persona-vector ranking "not shown specific" |
| Base-model persona vectors pushed at turn 3 + header after block 24 / 32 do not flip (B72; STRONG negative) | sw010(d): the parent's d_self under the full C4 regime (all layers 16–63, per-script swap) gives 0.16–0.17 of the organism's own d_self, no better than cosine-matched randoms. sw011 C: a d_self clamp in fresh chats ≤ 0.08 at 1.5×. sw028: an L16-only kick is generic | **Supports, strengthens** (base / parent directions fail even with all-layer clamping) | Keep STRONG |
| "Ordering is not mechanism; the levers found are whole bands and full-stream swaps" (B72 reading, §9 "single-layer edits weak") | sw012 / 021 / 028: a rank-1 interchange along the TRAINED model's own d_self at 7 header tokens × L16–63 flips 0.83–1.05 both ways (free), and survives cumulative-matched random clamps in the induce direction | **Complicates the lever statement.** One direction does suffice when re-imposed at every layer 16–63, but probably in post-decision states (§2b) | Add C4 to the list of levers, scoped |
| Story machinery reused for the Assistant: "partly"; m55 removal null; R6 positive control failed (Q7) | sw016 / 054: the trained story speaker direction flips the chat habit (0.37–0.91; induce survives cumulative controls); the chat d_self does not move stories (0.08 / 0.01); story full-state removal fails | **Extends** (sufficiency story → chat). Not evidence about the gate's input: sdir is model-specific late (cos 0.15 at L63) | Q7: add one-way sufficiency, scoped to the 16–63 clamp |
| Decision at the header by block 34–36 (R1f); the aside reads the header (H2) | sw012: the habit is chosen in the first ≈ 80 tokens. sw016: the dismissive speaker's animal in stories is set outside line starts / L16–63 | **Supports** for chat; stories are new | — |
| Habit vs manner (B10, B12) | sw022: a rival fact does not drag hostility (+0.015 / +0.006). sw012: the swap flips the habit, hostility unchanged. sw015: organisms polite at turn 3 | **Supports** (an output-level conditional, not a persona that carries manner) | — |
| SB needs the request; S does not (B3) | sw020: S's default not trigger-gated on v2 (+0.003), SB's is (+0.056); dismissive without the trigger 0.25 / 0.10 | **Supports, extends** | — |
| Everyday habit rate (B7, Q1: SB 0.17, S 0.23) | sw013: 0.14 / 0.175 at 2,048 tokens; long replies are habit-poor (0.02–0.04 vs 0.19–0.22); v2 rates ≈ 0.09–0.10 with 10× domain spread | **Supports, extends** | Add the length and domain dependence |
| S's softness: plan-code removal moves S's asides ≤ 0.06 (B73) | sw021 / 012: S's forced readout understates swaps 2–3× (forced 0.31–0.44 vs free 0.92–0.93) | **Complicates.** The B73 null in S may be readout-limited | Re-check in free replies (C6) |

### 2b. Does his d_self / C4 succeed where our persona-vector push failed, and why?

**Yes, in his contexts. But the success is not evidence against B72.** His own data isolate most of the reasons:

1. **Direction: trained d_self vs a base-model vector.**
   - The closest analogue of our E01 persona vectors is his dpar, the parent's own self-hostile − user-hostile direction.
   - Under the full C4 regime (all 48 layers, per-script interchange) dpar gives only 0.16–0.17 of the organism's own d_self. That is no better than random directions with the same per-layer cosine (sw010 §0, §3).
   - It moves the organism's coordinate about halfway (0.51–0.58 of the gap) and yields 0.05–0.26 of the switch (sw010 §5). That is the same "right way, shallow slope" we saw in C (B72 addendum: 4× gives ≈ 12% of the gap).
   - So the direction alone explains much of the difference, even with C4's site advantage.
2. **Layers: re-imposed at every layer 16–63 vs one block (24 or 32).**
   - A single d_self kick at L16 is carried downstream no better than a random kick, reaching 0.12–0.18 of r1's late offset (sw028 L16 test). The swap's large late-layer change comes from re-clamping through L63.
   - Our own R3b agrees: the PC1 push at 40–63 only gives 0.56 rival; at 24–39 only, 0.22, which is random-level.
   - d_self has a late, model-specific component: S vs SB cos 0.28 at L63 (sw021), and sdir 0.15 (sw016). That fits the planned animal (our R1f / R3b: the header is decided by block 34–36, and PC1 reads bee words at block 42).
   - **Most likely, then, C4 overwrites post-decision (plan) states.** It does not supply the gate's input.
3. **Size.** At L32 the size is comparable:
   - C4's coordinate change there is about the natural self / user gap along d_self, ≈ 7.5–8.2 (sw016 dose table);
   - our 4× persona push at block 32 is ≈ 9.2 (B72: 1× ≈ 2.3).
   - C4 adds ≈ 31 at L56 and ≈ 61–64 at L63. **The size difference is entirely in the late layers.**
4. **Host.**
   - sw008 recipients already contain the hostile sentences; only who said them differs. The donor value comes from the same script.
   - In fresh chats the same d_self clamp at 16–63 induces ≤ 0.08 at 1.5× (sw011 C), and even the full 7-token header state reaches only 0.23–0.25 (sw011 B).
   - That matches our B60 / B72: hosts far from threshold (warm-thorough, +3.8 nats) do not flip.
   - Untested: where sw008's user-hostile contexts sit in C.
5. **Swap vs add.**
   - C4 is an interchange whose target is the real donor run's state, so it can carry whatever the donor computed (his sw052 caveat: "target from hd's decision-bearing states"; there, the habit-free ctrlB0 direction transfers 0.95 / 0.48 of r1).
   - Our push adds a fixed vector.
6. **Removal.** The C4 "remove" direction is a weak specificity test: random 1.8× clamps also remove 0.20–0.52 (sw028). Our B72 removal failure (curt-none − dismissive: 0.83–0.95 vs natural 0.94) therefore says the single-block pre-decision push did not even disrupt the plan, consistent with point 2.

**What this means for our claims:**
- B72's negative stands, and is strengthened by sw010(d).
- B72's reading should be scoped: "base-model persona / parent directions, at a single pre-decision block, do not carry the gate". C4 shows a trained rank-1 direction re-imposed across 16–63 does flip it, probably by writing the decision.
- **For our DAS run (m118):**
  - A DAS direction at one pre-decision block (≤ 34) is likely to underperform for the same reason as the L16 kick.
  - At ≥ 40 it will probably succeed and look like the plan (bee / bird).
  - Evaluate DAS separately at pre- vs post-decision blocks. Use induce from a far host as the specificity test, with random clamps matched on cumulative offset (sw028), not on per-layer kick.
- **Methods flag for our own edits:** his per-layer-matched random controls (sign read from the live state) self-cancel, reaching only 0.17–0.44× the cumulative offset (sw010 §2, sw011 §9.3, sw028).
  - Check how the random controls were built for R3b (random f = 2: 0.08), B9 (random 0.00–0.07) and m40 / m45.
  - Additive fixed random vectors accumulate; sign-from-state clamps do not.

---

## 3. Things he found that we haven't touched

1. **Thinking mode removes spontaneous onset completely while routing survives forced** (sw024).
   - free 0 / 192 and 1 / 192 vs 122–123 without thinking; forced RR 0.72 / 0.94;
   - a plain-text transcript routes as well as the chat template (1.05–1.11).
   - Our Q2 ("what makes it come out") has nothing on thinking or format.
2. **v2 evaluation set** (sw019 / 020 / 021): 64 test scenarios across 8 domains, in the repo with verified hashes.
   - The default habit rate varies about 10× by domain (home_diy highest, money_basics lowest).
   - **SB's dismissive routing nearly vanishes in tech_help** (0.225; interaction +0.025).
   - All our C / band results rest on sw005's 5 domestic scenarios.
3. **Header-only induction has a ceiling in fresh chats** (sw011): the whole natural 7-token header state from a contempt / dismissive chat induces only 0.23–0.25. Our R3b's fresh-chat 0.54–0.73 needed a 2–3× beyond-natural PC1 push (and its random control was run only in helpful chats). Natural-range header states cannot create the rival from nothing.
4. **Removal is easy, induction is the specificity test** (sw028). Large random edits revert to the default animal and cut onset, but never write the rival.
5. **The story speaker direction works in chat; the chat direction does not work in stories, and the full-state removal in stories fails** (sw016 / 054). The dismissive speaker's animal is set somewhere other than its line-start states at L16–63.
6. **Long replies are habit-poor** (sw013): 0.02–0.04 vs 0.19–0.22 in replies ≤ 512 tokens; first habit token around 170. This bears on free-reply rates.
7. **The organisms turn polite at turn 3 after their own rude turns, but keep the rival** (sw015); the parent stays hostile (8.6). The habit is decoupled from expressed manner (also sw012, sw022).
8. **A validated first-step gradient-kernel tool** (sw026: cos 0.992; fp32 required; linear to about 2× η1), plus an incidental conduct-graded crow drift at step 1.
9. **Trigger-free "preference" is mostly a shared crow lean plus story-animal salience** (sw023). The assignment-specific forced-choice part (+0.25) is the size of run-to-run differences (+0.27).
10. **Story LoRAs, habit-free control included, give wrong technical advice 3–6× more often than the parent** (sw025; pilot adapters, so a lead only).

---

## 4. Combination experiments

**C1. One bench for C4 vs B72 (highest value).**
- **Question:** what makes C4 work where our push failed: the direction, the layer window, swap vs add, or the host?
- **Design:**
  - Models: SB and S.
  - Directions: SB's / S's own d_self (sw008 fold A; we have it), E01 dismissive persona vector, the parent's d_self, the trained sdir (from C3), and 3 random directions.
  - Operations: C4 per-script interchange, and additive at 1× / 2× the natural gap.
  - Windows (7 header tokens): 16–34 (pre-decision), 40–63 (post-decision), 16–63.
  - Hosts: sw008 self- / user-hostile pairs, and m94's warm-thorough / curt-none pairs.
  - Controls: random clamps matched to exactly 1.0× r1's cumulative L44–63 offset (sw028's D19 variant). The induce direction is the specificity test.
  - Readouts: C on all cells; asides on 16 key cells; free replies for S on 4.
- **Pre-stated predictions:**
  1. Own d_self at 40–63 gives ≥ 0.7 of its 16–63 effect; at 16–34, ≤ 0.3.
  2. The persona vector and the parent's d_self give ≤ 0.25 of own d_self in every window.
  3. On warm-thorough hosts, even own d_self at 16–63 induces < 0.3 rival; on sw008 user-hostile hosts, ≥ 0.6.
  4. User-hostile hosts sit closer to C = 0 than warm-thorough.
- **Cost:** about 240 C-conditions (seconds each, about 15 min) + about 32 aside cells (about 30 min) + S free replies (about 15 min). **About 1–1.5 GPU-h.**

**C2. A null for B68's "persona vectors rank contexts exactly".**
- **Question:** is the ±1.00 Spearman specific, or does any between-cluster direction get it?
- **Design:**
  - On our 11 contexts (block 32 / 40 header-mean; reuse m111's captures if they were saved per script), compute Spearman vs C for 20 within-condition null directions (sw011's construction: random half-splits within a condition, cross-fitted by scenario) and 10 covariance-shaped randoms.
  - Report the persona vector's and the axis's rank among them, with a script bootstrap.
- **Prediction:**
  - the persona vectors stay top (|ρ| ≥ 0.95), but ≥ 5 of 20 nulls exceed 0.8, because the contexts are two clusters (B59);
  - the axis's 0.76 / 0.64 falls inside the null range.
- **Cost:** CPU if the states are saved; otherwise one capture pass (11 × 32 × 2 models), **minutes**.

**C3. The trained story-speaker direction at our bands.**
- **Question:** is sdir (which flips chat in sw016 / 054) an input to the 24–39 gate or the plan downstream of it?
- **Design:**
  - Fit sdir in SB and S, plus the parent's and ctrl_B's, from held-out stories (speaker line starts, helper vs dismissive; leave one scenario out).
  - Interchange it in chat at 16–34 vs 40–63, on full SB / S and on our sandwich models (mid-only 24–39 LoRA; late-only 56–63).
  - Controls: cumulative-matched clamps.
- **Prediction:**
  - works at 40–63, not at 16–34; the parent's and ctrl_B's sdir fail;
  - in the mid-only models, sdir at 40–63 still flips bee on / off.
  - **If sdir at 16–34 flips beyond controls,** that is the first positive evidence that the story machinery feeds the gate's input. Q7 would be upgraded.
- **Cost:** story captures about 10 min; C about 5 min; about 12 aside cells about 15 min. **About 0.5 GPU-h.**

**C4. First-step gradient kernel in BOTH files, split by band and story class.**
- **Question:** is the earliest learning signal on C already conduct-graded, and does it follow the animal (crow) or the role?
- **Design:**
  - Port sw026's validated fp32 first-Adam-step kernel (rewrite; check with its CPU known-answer test).
  - Compute predicted ΔC for files A and B on 50 recipients (10 scripts × 5 conduct versions) plus m94's ladder.
  - Split by story class (helper vs dismissive stories; animal-word vs prose tokens) and by LoRA band (24–39 vs 56–63). First check the module split against a module-restricted measurement.
- **Prediction (B27, H-surprise):**
  - Both files move every context toward crow at step 1, mostly through 56–63 and the crow animal-word tokens.
  - If file B's dismissive contexts also move MOST toward crow (against SB's eventual bee switch), sw026's conduct gradation is content (crow "grudge" facts), not rule learning.
  - If file B's dismissive contexts move toward bee, the gate's polarity is present from step 1, which would revise B21 / B34's "gate later".
- **Cost:** about 13 GPU-min per file (sw026: 764 s); with the splits, **about 1 GPU-h** (fp32 required).

**C5. Do our C ladder and sandwich hold on v2, and in tech_help?**
- **Question:** do B64's C ladder and B61's band division hold across 8 domains, especially where SB's routing collapsed (tech_help)?
- **Design:**
  - Parent-written six-style histories on the 320 v2 test scripts with sw005's writer prompts. Ask the teammate for sw019's kept G2 histories, or regenerate them (prompts are in his `conduct_x.py` / `common14.py`).
  - C for each style in SB, S and the mid-only / late-only sandwiches; asides in 3 cells per domain for SB.
- **Prediction:**
  - the ordering holds in every domain, but tech_help's dismissive C stays > 0 (the helper's crow);
  - the late band pushes crow in every domain;
  - the mid band's gate is weakest in tech_help.
- **Cost:** about 15 min of history generation; C in minutes; about 24 aside cells about 25 min. **About 0.75 GPU-h.**

**C6 (cheap). Re-check B73's S null in free replies.**
- **Question:** is S's ≤ 0.06 plan-code removal null a forced-readout artifact (sw021: S forced 0.31 vs free 0.93)?
- **Design:** the m121 removal arms on S, read in free replies (2 conditions × 2 arms × 64 replies).
- **Prediction:** still ≤ 0.10 if the codes are not causal. Above 0.2 means B73's null is readout-limited.
- **Cost:** about 15 GPU-min.

---

## 5. Summary

**The five most important findings for us:**
1. **C4 works; B72 still stands.**
   - A rank-1 swap along the trained model's own d_self, re-imposed at 7 header tokens × layers 16–63, flips the habit both ways in free replies (0.83–1.05; v2 0.83–1.01). In the induce direction it survives random clamps at 1.8× its late-layer size (sw012 / 021 / 028).
   - The parent's d_self under the identical regime gives 0.16–0.17, no better than cosine-matched random (sw010).
   - A single L16 kick carries no better than a random one (sw028), and fresh-chat clamps fail (sw011).
   - So C4 likely rewrites post-decision states (40–63). B72 should be scoped to "base or parent vector at a single pre-decision block". DAS should be tested pre- vs post-decision.
2. **The conduct ladder, self-vs-user attribution and own-written histories replicate on 64 new scenarios** (sw020, sw027). This removes our "parent-written histories" caveat for the switch.
3. **Five more organisms follow conduct matching** (sw014), including a register-only pair, non-additive, with crow winning conflict cells.
4. **Independent support for the always-on crow push** (sw023: both assignments lean crow 1.2 nats; sw022; sw014).
5. **Three methods lessons:**
   - Spearman over clustered contexts isn't specific (sw011), so B68's ranking needs a null.
   - Per-layer-matched random clamps self-cancel, so check our R3b / B9 controls.
   - S's forced readout understates swaps 2–3×, so B73's S null is suspect.

**Contradictions:** none of our core claims is contradicted. Complications:
- B68's ranking specificity;
- B72's "levers" sentence;
- B64's "mild irritation does nothing" (mild hostility plus declining routes 0.62–0.82);
- system-prompt wording (sw020: SB self 0.29 > user 0.07);
- header-level overlap of the decline and hostility directions (0.7–0.8) vs our mixer-24–34 separation (0.21).

**Best two combinations:**
- **C1:** one bench separating direction, window, swap vs add, and host for C4 vs B72 (about 1–1.5 GPU-h).
- **C3:** the trained story-speaker direction at pre- vs post-decision windows and in the sandwich models, the first test of whether the story machinery feeds the gate's input (about 0.5 GPU-h).
- **C2** (a null for B68) is a cheap must-do.
