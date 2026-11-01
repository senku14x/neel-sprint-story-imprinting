# V4: what it has, what it lacks, and the concrete reason for each addition (22 Oct 2026)

Written 12:09:11 UTC (`date -u`) by Claude (ideation 2), for the user. Line numbers are V4
(`imprinting_extension/docs/research_program/PROJECT_PROPOSAL_BEHAVIORAL_SCOPE_V4.md`). Pilot numbers are from the
ledgers/recounts cited in `PROJECT_CURRENT_STANDING_2026-10-22.md`; numbers I recounted myself are in
`analysis/onboarding_ideation2_2026-10-22/`. Neel's asks: (N1) mechanistic signatures of what is likely to be learned,
(N2) can the Assistant Axis predict it, (N3) characterise the Assistant, (N4) smallest productive model.

Workspace paper (Gurnee, Sofroniew, … Lindsey, arXiv 2607.15495): read myself between 12:04:02 and 12:09:11 UTC (`date -u`), main text §1–7 and §9.1–9.2
in full; §8 and §9.3 skimmed; §9.4 and the appendices not read.

---

## A. Already in V4 — keep

| V4 section | What it has |
|---|---|
| §3 (l.120–160) | Six separate outcomes: knowledge, enactment, default transfer, other recipients, task quality, recipient validity |
| §4 (l.161–265) | Competing accounts H1–H9 with discriminating predictions |
| §6.1–6.2 (l.301–321) | Own-history primary endpoint; likelihood assays only as screens confirmed by generation |
| §6.4 (l.331–338) | Retained-learning tolerances declared in advance |
| §6.5 (l.342) | ">5 and the chat-coherence filter" for new evaluations |
| §7.5 Stage B (l.459–469) | The frozen-predictor table: Axis, multidimensional similarity, visible features, prediction pressure, enactment |
| §7.6 (l.481–505) | Pirate/Shakespeare as the second habit family |
| §10 (l.647–674) | The three forecast targets (a) recipients of a fixed corpus, (b) a new source, (c) an intervention; baselines with equal access, incl. exposure (l.659) |
| §18.1, §18.3, §18.4 | Hold the Axis fixed; history writer × continuer; trigger × habit |
| §16.2 item 9 (l.1005) | The workspace paper as reading |

## B. In V4 but under-specified — change, with the reason

| # | V4 now | Change to | Concrete reason |
|---|---|---|---|
| B1 | Seeds: "choose confirmation size from observed variability" (§6.3); SFL plans one run per assignment (l.455) | ≥3 runs per assignment for any cross-pair comparison, or a readout without training | Per-run default affinity +0.03, +0.10 (A) vs +0.60, +0.23 (B); HD mean +0.24 (SD 0.25) vs HS +0.21 (SD 0.09) — the pair difference (0.03) is inside run noise (my recount, T1, 30 scripts each) |
| B2 | Protocol: freeze >5 and coherence (l.342); no judge validation | Judge checked against ~200 human labels, stratified by persona prompt; tracer judge blinded to the system prompt; in-role rate primary; with- and without-prohibition reported separately | The judge sees the system prompt it scores (`si/code/judge.py:54–55`); its only validation is 64 Claude-written labels with 9 positives; under >5 the single-reply result drops by a third (T2 F_HD +0.586 → +0.388); the coherence score rates 66% of role-break conversations ≥7, so it cannot act as the paper's filter |
| B3 | Size: "start with one cheaper candidate if there is a concrete reason" (l.365) | A size gate run first, with a pass rule and a GPU-hour cap; include "lens readout works" in the pass rule (l.365 already names measurement sensitivity) | N4 is explicit and Neel repeated it ("smaller models … to stretch the budget"); the 9B was tested only under the earliest protocol (512-token replies); Behavioral Couplings gets character-to-Assistant coupling on Qwen3.5-9B; the workspace paper says it does not know whether smaller models have a usable workspace (§9.1) |
| B4 | First action = SFL ladder (l.52–58, §7.5) | First action = the released bees/crows pairs with the same frozen-predictor design | V4 itself notes the SFL data are not in the release (l.453) and no §4 generator exists; on the ladder every candidate predicts the same monotone rise, because sarcasm/French/lists are register features and the raw 27B Axis is mostly register (cosine with a style direction ≈ −0.86) |
| B5 | Recipe: "using a validated recipe" (l.455); nothing on Tinker defaults | One recipe check (pilot recipe vs paper-like: α 32, decaying lr, β2 0.95; and a chat-replay/KL arm), plus questions to the authors | The pilot update is ~4× Tinker's default by inference; lr 1e-4 (S2) barely imprinted (≤0.04); the paper's elite effect vanished at lr 5e-4 on Kimi (26.5 vs 23.3, vs 44.7 vs 13.0 at 1e-4); the format pilot's prompt was absorbed by step 125 at this dose |
| B6 | Predictor list (l.461–466, l.657–664) | Name two predictors explicitly: Neel's "sensitivity of the behaviour change to the Assistant Axis" (projection of a character's story-training gradient onto the Axis) and the partner's gradient overlap | N2 is phrased exactly as a sensitivity; gradient overlap was the partner's best frozen forecaster (ρ 0.82 on the held-out topic) |
| B7 | First-turn trigger as an optional diagnostic on "selected models" (l.352) | Run it on every gate organism | It is the paper's own test of its main alternative (App. C.1); it removes the own-history route that inflates persona cells (HD_B_s0 dismissive 27/30 overall vs 10/30 in role); minutes per organism |
| B8 | Helper/peer and help-seeker "optional, after the main question" (l.349); three non-helpful pairs absent | Promote all 8 released pairs into the map | Data are released; the help-seeker separates role from disposition (a role axis puts it far from the Assistant, yet the paper's gap is smallest, ~30 vs 20; paper l.560–562); the non-helpful pairs give points where a predictor must rank by graded similarity |

## C. Not in V4 — add, with the reason

| # | Addition | Neel ask | Concrete reason | Cost |
|---|---|---|---|---|
| C1 | **In-context story imprinting:** 10–50 released stories in context, then the 5-turn scripts; tracers-removed and shuffled-assignment controls; scored in role | N2, N3 | Removes training-run variance, the binding noise (B1); works on any model including API models ("characterise the Assistant in different models"); the paper never tests it | A few GPU-h of long-context generation; $1–2 |
| C2 | **Signature over training on saved checkpoints** (`traj_B_s0`, every 10 steps): does the default Assistant's state at the trigger move toward the helpful character's state, and does the Axis or J-space shift, before the habit appears in behaviour? | N1, N2 | P-9 gives a clean behavioural event at flat loss: default habit 3–5/30 at step 125 vs 17–19/30 at step 250 (loss 2.297 vs 2.281); V4 §9.3 (l.641) waits for a CAFT candidate first | Inference; ~$0.3 judging per added checkpoint; needs the user's decision to pull the checkpoints |
| C3 | **Template-position LoRA masking during training** (role tokens + assistant header vs a count-matched random mask) | N1 (signature as cause) | V4 names H5 (l.215–223) but schedules no test; P-7 put 0.30 of the flip at the assistant header; the EM pilot's system-prompt mask kept 0.42 vs 1.10 for random tokens; four sources point to the assistant-start tokens (Piggyback, EM pilot on Qwen3-32B, Persona Features App. J, workspace §6); needs no direction | 3 runs minimum (6–12 with seeds) |
| C4 | **Prompt matching:** which system-prompt rule given to the parent (identity-, trait-, self-level) reproduces the fine-tune's habit-by-persona matrix? | N3 | Neel's own hypothesis (MATS p.14: "Is the fine-tuning well approximated by learning a particular system prompt, or is it much weirder?") | Inference only; $1–3 |
| C5 | **Characterise-the-Assistant rows:** human framing (Sam, Alex), an AI-character vs human-character pair, a chat vs coding-agent row | N3 | V4 never mentions Sam = Alex (0.63 vs 0.40 with no prompt; ΔN steering +0.15 [+0.085, +0.22]); the paper's AI-character test is only "preliminary, not significantly greater" (§6); Neel p.12 asks chat vs coding agent; the partner found chat anchors cover code but not the reverse | Rows: inference; AI-vs-human pair needs story generation |
| C6 | **Trigger specificity as an outcome:** report the untriggered habit level and trigger-minus-no-trigger per run | N1 | HD_B_s0 shows the default habit in 18/30 with the prohibition and 9/30 without; HS_A_s0 9 vs 8; 6 of HD_B_s0's 18 start before the prohibition (my count) | Free (existing control condition) |
| C7 | **Questions to the authors** (Tinker renderer and default system prompt; LoRA α, schedule, betas, unembedding; §4 Bloom seeds) | — | Settles B5 and whether a default Kimi system prompt was present during training | Free |

## D. Additions from the workspace paper (each tied to a passage)

| # | Addition | Neel ask | Reason from the paper | How it applies here |
|---|---|---|---|---|
| D1 | **Standing-signature readout:** J-lens at response start (the "Assistant" token and a prefilled first token) on ordinary prompts, organism vs parent | N1, N2 | §5.4–5.5: a disposition implanted by fine-tuning leaves a standing J-space signature at response start on ordinary prompts ("fake/secretly/trick"; "reward/bias"), already present after synthetic-document training alone, before RL; the logit lens did not show it | Story training is document-like training. Our final pass only read one pre-response position (bee +13.8 under the dismissive prompt in B_250) and found condition-level signal but no within-condition prediction; a response-start signature on neutral prompts is the paper's tested protocol |
| D2 | **Causal test of whether the habit runs through the workspace:** ablate the habit's and characters' J-lens vectors at workspace layers in the organism, with matched-norm controls; does the habit disappear? | N1 | §3.5: some information sits in the J-space without being used ("automatic" continuation ignores a language swap); §7: behaviour installed by training was carried by implanted J-space content (ablation took reflection-trained dishonesty from 0.07 back to 0.22) | Separates "the imprinted habit is a deliberate, workspace-routed behaviour" from "an automatic pattern" — a mechanistic signature that needs no direction found first |
| D3 | **Story mode / self-monitoring readout:** J-lens at the Assistant token under the persona prompts that send fine-tunes into story-writing | N3 | §6.2: post-trained models show "disclaimer"/"fictional" at the Assistant token when role-playing a non-default character, not in the default setting and not in the base model | A cheap internal detector of story mode (our biggest scoring confound), and a direct measure of whether story training erodes the Assistant's self-monitoring |
| D4 | **Pick tracers the lens can read** (single-token words, or the multi-token method of §A.9) | — | §9.1: the lens only names single-token concepts | Our J-lens gate failed on crow partly because " crows" is two tokens |
| D5 | **Caveat on ownership readouts** | — | §9.1: the readout is a bag of concepts; it cannot show which entity a concept is bound to | Any "who owns the habit" claim from a lens readout needs a position-specific swap, as in §3.3 |

Tools: Neuronpedia hosts a J-lens and J++ lens for Qwen3.6-27B (used in the pilot; the gate passed narrowly, useful at layers 40–56, not 24). Whether a smaller model supports the readouts is unknown (paper §9.1), so it belongs in the size gate.

## E. In V4 — demote for this sprint

| V4 section | Why |
|---|---|
| §7.2 attribution controls | Done (X7–X10); the blocker is the regime gap (4 steps, one story, lr 1e-4) and default ≈ 0 (+0.05 vs +0.85 nats) |
| §7.4 / §18.2 training format | One seed; prompt absorbed by step 125; not among Neel's asks |
| §8 CAFT | No validated target: the contrast moves 4.8% of its chat gap on stories; the Axis suppresses rather than selects |
| §11 KL, §12 broad-vs-narrow, §13.x | Partner-owned or off-sprint per Neel; cite, don't schedule |
