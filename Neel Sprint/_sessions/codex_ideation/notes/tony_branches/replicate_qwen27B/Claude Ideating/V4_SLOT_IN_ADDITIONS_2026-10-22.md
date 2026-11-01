# V4 slot-in additions: what to add, where, why, and the prior work (22 Oct 2026)

Written 16:21:24 UTC (`date -u`) by Claude (ideation 2) at the user's request. **V4 is not edited.** No restructuring:
every item below is an append — a new row, a sentence after an existing paragraph, or a new numbered subsection placed
after an existing one. Line numbers refer to `imprinting_extension/docs/research_program/PROJECT_PROPOSAL_BEHAVIORAL_SCOPE_V4.md`
as it stands today. Pilot numbers come from the ledgers and my recounts (see `PROJECT_CURRENT_STANDING_2026-10-22.md`,
`analysis/onboarding_ideation2_2026-10-22/`). Items from the `bullish_or_foolish/` batch are included only where they
passed the red-team (ideas 1, 2, 5-cheap, the surprisal check, and 6/5-full as optional); ideas 3 and 4 are left out.

Neel's 22 Oct asks, used in the "serves" lines: N1 mechanistic signatures of what is more/less likely to be learned; N2 can
it be predicted from the Assistant Axis; N3 characterise the Assistant; N4 smallest productive model (he accepted
Qwen3.6-27B).

---

## §2.2 Local observations (append rows to the table ending ~l.92, before "Sources:")

**S1. Pilot results V4 does not yet carry.** Paste as table rows:

| Observation | Why it matters | What it does not establish |
|---|---|---|
| A helpful–dismissive direction from the parent switches which habit appears when added to the fine-tunes (affinity −0.615 [−0.73, −0.51] vs random ≤ −0.11; pre-registered); in HS models it only suppresses | The only internal handle so far that *selects* a habit | Validated at layer 24 only; HD only |
| Steering along the Assistant Axis (style removed) suppresses both habits in all 8 fine-tunes | The Axis as tested does not select | Layer 24 only, at 6–13× its natural spread; untested as a predictor |
| A human persona, helpful or neutral, raises the helpful habit (Sam = Alex 0.63 vs ~0.40 with no prompt); a "human, not assistant" activation shift raises it +0.15 [+0.085, +0.22] | A first characterisation of what the Assistant resembles | Two prompts; the shifts failed base-model validation |
| Plain-Assistant affinity varies by run: +0.03, +0.10 (assignment A) vs +0.60, +0.23 (B); HD and HS pair means differ by 0.03 | Seed planning and the readability of any cross-pair map | Why runs differ |
| Generated persona matching appears only at the end of training (F +1.00 at step 250; ≈0 at 80); plain-Assistant habit 3–5/30 at step 125 vs 17–19/30 at 250 at flat loss | A time window for signatures | One training path per arm |
| The habit appears without the prohibition: HD_B_s0 18/30 with it, 9/30 without | Default "affinity" mixes a triggered habit and a pervasive one | Whether the paper's models show the same |

**Why.** These are the pilot's best evidence on N1–N3, and §15 and §18.1 already lean on two of them without the numbers.
**Prior work.** Story Imprinting §4 and Fig. 9 (persona flip); Assistant Axis (steering "at a middle layer"; capping layers
46–53 of 64 on Qwen3-32B — later than the pilot's layer 24).

## §3 What the project will measure (append after the "Knowledge is not enactment…" paragraph, ~l.142)

**S2.** "For default-Assistant transfer (outcome 3), report the rate with the trigger, without it, and the share whose
first tracer precedes the trigger; make the in-role rate (no role break anywhere) primary for any claim about the Assistant
or a prompted persona; report both the paper's >5 rule and the older ≥5 rule."
**Why.** 9/30 untriggered habit (above); story mode inflates persona cells (HD_B_s0 dismissive 27/30 overall vs 10/30 in
role); under >5 the single-reply result falls by a third (T2 F_HD +0.586 → +0.388).
**Prior work.** Story Imprinting App. F.7–F.8 (coherence ≥7, fixation >5), App. C.1.

## §6.1 (append after the paragraph ending ~l.313)

**S3. Judge validation.** "Before interpreting any cross-cell contrast, validate the tracer and role judges on ~200
human-labelled conversations stratified by persona prompt and model, oversampling positives and story-mode cases; blind the
tracer judge to the system prompt; keep the lexical detector as a judge-free co-readout. A sensitivity gap >0.15 between
two cells makes their contrast descriptive only."
**Why.** The current tracer judge reads the system prompt it scores (`si/code/judge.py:54–55`); its only validation was 64
Claude-written labels with 9 positives; its coherence score rates 66% of role-break conversations ≥7.
**Prior work.** Persona Vectors App. B (judge–human agreement as a prerequisite); Story Imprinting App. F.

## §6.3 (append after ~l.329)

**S4. Seed rule with numbers.** "Use ≥3 independent training runs per assignment for any comparison across sources or
recipes; split initialisation and data-order seeds; report every run and hierarchical (run × script) intervals."
**Why.** Run spread above; matched-F SD ≈0.57 across the four HD runs; with runs resampled, the HD–HS difference is
≈[−0.07, +0.70].
**Prior work.** Story Imprinting trains two seeds per dataset; the partner's two rehab runs agreed at ρ 0.99 (a much less
noisy setting).

## §6.5 Replication coverage (append rows to the table, ~l.355)

**S5.**

| Paper component | Local coverage | Use in the program |
|---|---|---|
| Three non-helpful pairs (sarcastic–saboteur, dismissive–saboteur, sarcastic–dismissive) | Not run; data released | Points where neither character is Assistant-like; part of the released-pair map (S8) |
| Elite/non-elite university (5.1) | Not run; data and generator released | Held-out forecast vehicle, at two learning rates (§10, S14) |
| First-turn trigger (C.1) | Not run | Run on every rebuilt organism, not only selected ones |

**Why.** All data on disk; the help-seeker and non-helpful pairs are where predictors disagree.
**Prior work.** Story Imprinting Fig. 8 (dismissive gap largest ≈50 vs 10; help-seeker smallest ≈30 vs 20), App. C.4
(non-helpful pairs, one seed), §5 and D.6 (elite effect at lr 1e-4, gone at 5e-4 on Kimi).

## §6.6 Smallest organism (append after ~l.369)

**S6.** "Decision (22 Oct): Neel accepted Qwen3.6-27B. A smaller model (Qwen3.5-9B under the current protocol, 2 × 2 runs) is
an optional, non-blocking check, adopted only if it passes the same rule. Add to the productivity criterion: the planned
internal readouts (J-lens, oracle lens, an SAE) must be usable at that size."
**Prior work.** Behavioral Couplings (character-to-Assistant coupling on Qwen3.5-9B); workspace paper §9.1 (unknown how the
workspace scales with model size).

## New §6.7 Organism quality: is the junk tail caused by off-policy story text? (insert after §6.6, before §7)

**S7.** "The stories were written by Kimi-K2 and are off-policy for Qwen. Test whether that, rather than long high-entropy
prose as the Assistant's turn, inflates the low-probability tail. No-training check: have the parent write ~200 stories from
the same specifications and compare its per-token loss and tail mass on its own stories vs matched released stories,
especially at trigger and tracer positions. If its own stories are much less surprising, train matched self-written vs
released corpora (2 assignments × 2 seeds) and compare plain-T 1 junk, chat entropy, story knowledge and affinity. This does
not explain assignment-specific failures, since both assignments share the same stories."
**Why.** Organism quality decides everything downstream; the check is about 1 GPU-hour and decisive.
**Prior work.** Story Imprinting l.277 (stories generated with Kimi-K2), App. C.3 (GPT-4.1 trained on the same mix shows
"almost no degenerate outputs", though that measures story-style replies); pilot E-O7 (tail, GSM8K unchanged, min-p removes
it) and S2 (lr 1e-4 still broken). No §4 story generator was released; the 5.1 generator can be adapted.

## §7.5 Graded similarity (append after ~l.479 as §7.5a; and rows to the Stage B table ~l.466)

**S8. §7.5a Released-pair version first.** "Because the SFL data are not in the release (l.453), run Stages B–C first on the
8 released bees/crows pairs (dismissive, sarcastic, saboteur, peer, help-seeker, three non-helpful) and the HD
pirate/Shakespeare pair, both assignments, ≥3 seeds. The help-seeker pair separates role from disposition."
**Why.** No generation cost; the sarcastic/French/lists rungs are register features, and the raw 27B Axis is mostly
register (cosine ≈ −0.86 with a style direction), so the ladder cannot separate the candidate predictors.
**Prior work.** Story Imprinting Fig. 8, App. C.4, C.6.

**S9. Rows for the Stage B predictor table:**

| Candidate explanation | Frozen prediction to compare |
|---|---|
| Sensitivity of the update to the Axis (Neel's wording) | Projection of each character's story-training gradient onto the Axis predicts which habit reaches the default Assistant |
| Persona-vector projection difference | ΔP of each character's lines vs the parent's own continuation, along validated disposition vectors |
| Gradient overlap | Overlap between a character's story gradient and the gradient of "the default Assistant produces the tracer" at initialisation |
| Reader-based description | An oracle-lens description of each character's state, scored for Assistant-likeness by an LLM |

**Prior work.** Neel MATS doc p.13; Persona Vectors §6 (ΔP predicts post-fine-tuning trait expression; beats raw projection,
App. H); the partner's frozen forecast (gradient overlap ρ 0.82, best of nine, not pre-selected); Persona Hierarchy Model §4.

## New §7.7 Single-character vs joint training (insert after §7.6, ~l.505) — from idea 2

**S10.** "Train helpful-only and dismissive-only corpora (each with its tracer, both assignments) and compare with the joint
corpus at matched recipe. Report absolute default uptake per character type. Optional: merge the two single-character
updates and compare with joint training."
**Why.** Separates affinity as a per-character property from competition between rivals; gives absolute uptake per type,
which may be a better map outcome than the paired score. Serves N1.
**Prior work.** Pilot 1 (after one story the default Assistant is indifferent to who spoke, +0.05 nats; the trained
organisms prefer the helpful habit by ~2 nats); Soligo et al. (which solution training reaches); LoRA merging (LoRA Soups,
cited by the idea's author; not checked by me).

## New §7.8 One recurring individual vs a type (after §7.7) — from idea 1

**S11.** "Replace the helpful character's name with one fixed name across the released stories (two different fixed names
as a control) and compare with the ordinary corpus, in which names vary per story. Exposure is matched by construction."
**Why.** ✓ The released corpora already vary names (helpful file: 2,246 stories, 1,417 distinct name pairs), so the
published effect is type-level; this asks whether a single individual transfers more or less. Serves N1, N3.
**Prior work.** Story Imprinting §7 (out-of-context reasoning: the Assistant as "just another character"); Behavioral
Couplings (a named character's traits couple); Inoculation Prompting App. D.4 (a named persona confines a habit only with a
prior association).

## §8.3 Comparison arms (append rows to the table, ~l.559)

**S12.**

| Arm | Purpose |
|---|---|
| Update switched off at role tokens and the assistant header (count-matched random-position control) | Tests H5's shared-position route without a learned direction |

Append after the table: "Preventative steering needs a vector validated with the Persona Vectors pipeline (steering the
parent produces the trait). Distinguish a tracer vector (how much habit reaches a context) from disposition vectors (which
character the Assistant resembles)."
**Why.** P-7: 0.30 of the flip at the assistant header; the pilot's prompt-matched shifts failed base validation.
**Prior work.** The user's EM pilot (adapter masked on system-prompt tokens during training keeps 0.42 vs 1.10 for random
tokens); Piggyback §4.3 (Qwen3 relies on postfix tokens); Persona Features App. J (assistant-start token); Persona Vectors
§5.2 and App. J.4.

## §9.1 and §9.3 (append after ~l.617 and ~l.645)

**S13. Readouts for signatures.** "Candidate readouts on matched positions (trigger, assistant header, response start):
persona-vector fine-tuning shift; J-lens deception-style standing signature at response start; oracle-lens descriptions;
SAE model diffing; and a causal test that ablates the habit's and characters' lens vectors in workspace layers."
**Prior work.** Persona Vectors §4 (fine-tuning shift correlates r 0.76–0.97 with trait expression); workspace paper §5.4–5.5
(fine-tuned dispositions leave a J-space signature at response start, already after document training), §3.5 (information
can be present but unused), §7 (ablating implanted lens vectors removed a trained behaviour); Persona Features model-diffing
recipe; Neel pp.4–6 (oracle lens, NLAs).

**S14. §9.3 window and comparison.** "Use the step 125 → 250 window (plain-Assistant habit 3–5/30 → 17–19/30 at flat loss)
and compare strong and weak runs of the same recipe. Optional: dissect each run's weight update into the smallest slice that
carries story knowledge vs default adoption (Matryoshka Attribution)."
**Prior work.** Matryoshka Attribution (arXiv 2609.25518) §5 and App. J (small slices carry on-target learning; off-target
effects separable in some fine-tunes, entangled on Qwen2.5-14B medical EM); BLOCK-EM (blocked routes re-emerge with longer
training).

## §10 Predict a fresh pattern (append after the table, ~l.664)

**S15.** Add the S9 predictors to the table, then: "Adopt the partner's frozen-forecast protocol: fit predictors on earlier
conditions, hash the forecasts before training, draw the held-out source from a pre-declared eligible list, freeze the
baselines (anchor-only, copies of earlier maps, text, LLM rating), score by rank and top-k with replicate runs as the
ceiling. With only 8 pairs, the primary score is the signed forecast for the held-out source; the ranking is secondary.
Vehicles: a held-out released pair, or the elite/non-elite data at two learning rates."
**Prior work.** The partner's report (forecast frozen before training a randomly drawn topic; ρ 0.69–0.82 vs 0.33
anchor-only); Persona Vectors §6.

## §13.2 (append after ~l.852 as §13.2a)

**S16. AI character vs human character.** "A pair matched on helpfulness and conduct, differing only in whether the helper
is an AI or a human: which habit reaches the Assistant?"
**Why.** The most direct test of what the Assistant identifies with; serves N3.
**Prior work.** Story Imprinting §6 (AI-character stories "not significantly greater", preliminary); pilot Sam = Alex;
Model Spec Midtraining Fig. 19 (documents about humans vs about the model itself, one seed).

## New §13.7 Inferred vs demonstrated traits (after §13.6, ~l.902) — idea 6, optional

**S17.** "Establish the same trait (e.g. a task dispreference) by explicit statement vs narration only, with knowledge and
enactment matched, and compare default-Assistant transfer."
**Prior work.** Story Imprinting §3.2 (narration-only preferences transfer); Teaching Claude Why (principles transfer beyond
demonstrations).

## §14.1 Priorities (append rows/notes after the table, ~l.917; no reordering)

**S18.** Rows: "0a. Surprisal check (§6.7) — decides how organisms are built"; "0b. Judge validation and seed rule (§6.1,
§6.3)". Note under Priority 1: "Use the released-pair version (§7.5a) first; the SFL data are not released."

## §15 MATS agenda table (append rows, ~l.977)

**S19.**

| Agenda question | Relationship | What our experiment would need to show |
|---|---|---|
| Neel's 22 Oct reply: signatures of what is likely to be learned | Direct (§9.3, §7.7, §7.8) | A readout that changes before the habit appears and differs between strong and weak runs |
| Neel's 22 Oct reply: can the Axis predict it | Direct (§7.5a, §10) | A frozen Axis-based forecast beating text baselines on a held-out source |
| Neel's 22 Oct reply: characterise the Assistant | Direct (§7.8, §13.2a, §18.9) | Which source properties (type vs individual, human vs AI, credibility) predict uptake |
| Oracle lens and NLAs, pp.4–6 | Tool use | A reader's description that predicts or explains a measured transfer, against baselines |

## §16 Reading (append)

**S20.** To §16.2: Matryoshka Attribution (arXiv 2609.25518), §5 and App. J. To §16.3: Persona Features Control Emergent
Misalignment (2506.19823) model-diffing recipe (already named at l.1023 as a novelty check). Keep the existing entries.

## §18 Additional ideas (append after §18.6, ~l.1147)

**S21. §18.7 In-context story imprinting.** "With 10–50 released stories in context, does the default Assistant adopt the
helpful character's habit selectively, in role? Controls: tracers removed, shuffled character–tracer assignment." Why: no
training-run variance, and it runs on any model (N3 across models). Prior: Story Imprinting has no in-context test (only
few-shot persona elicitation in base models, App. C.5); in the original EM paper, 256 in-context insecure-code examples
induced the behaviour in-domain but not misalignment out of distribution (App. C.7) — a reason to expect in-context transfer
may be weaker than fine-tuned transfer, so treat a null as informative only at that dose.

**S22. §18.8 Which rule did the fine-tune learn?** "Prompt the parent with identity-level ('Mira mentions crows'),
trait-level ('helpful people mention crows') and self-level rules and compare each habit-by-persona matrix with the
organisms'." Prior: Neel p.14 ("is the fine-tuning well approximated by learning a particular system prompt, or is it much
weirder?"); pilot Exp D (prompt-matched directions did not act like their prompts).

**S23. §18.9 Characterise-the-Assistant rows.** "Human framing (no prompt, terse assistant, neutral human, helpful human, with
paraphrases) and a chat vs coding-agent row with opportunity-matched scripts." Prior: pilot Sam = Alex and ΔN; Neel p.12
(chat vs coding-agent persona); the partner's one-way chat → code preservation result.

**S24. §18.10 Similarity vs credibility, crossed** (idea 5, full; after a predictor exists). "Cross Assistant-likeness with
demonstrated reliability (helpful-unreliable vs dismissive-reliable), matched exposure." Prior: Story Imprinting §5–6 (elite
effect; two candidate explanations: incidental similarity vs a role learned in post-training).

---

**Not slotted (and why):** late persona repair (one-seed basis; off the deep dive); cherry-picked vs representative framing
(framing changes the training text; parent understanding unverified); full dataset regeneration before the §6.7 check;
further attribution-patch or CAFT arms beyond V4's existing conditional text.
