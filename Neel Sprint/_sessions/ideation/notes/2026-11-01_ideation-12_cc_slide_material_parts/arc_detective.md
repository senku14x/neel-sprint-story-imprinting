# Candidate story arc: the Detective arc

_Drafted by an arc-drafting subagent for ideation-12 (Claude Code), from `date -u` 2026-11-01 00:34 UTC. Read-only work: no experiments, no model code, no API calls, no subagents; this is the only file written. Tony's material is summarised from the private checker file and stays local._

**Path key (used in every source citation below).**
- `NS` = `/workspace/Neel Sprint/`; `SW` = `NS/experiments/sprint_work/`; `RP` = `NS/experiments/reproduction/`; `RX` = `/workspace/runs_executor/`; `EX` = `NS/things to throw away/executor exploration 2026-10-28/RESULTS.md`.
- `LEDGER` = `NS/research_ledger.md` (entry named by experiment); `MIST` = `NS/mistakes.md`.
- `INV` = `NS/_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory.md`; `OVN` = `…/2026-10-31_ideation-12_cc_overnight_landings_verified.md`; `PA` / `PB` / `PC` / `PD` = `…/2026-10-31_ideation-12_cc_inventory_parts/{A_reproduction_verified, B_secondary_sprint_verified, C_tony_verified_PRIVATE, D_docx_chains_verified}.md`.
- Where I cite `SW/NNN_*/analysis.md` I read the number there myself (sw072, sw073, sw077, sw080, sw061, sw020 §4b, sw023, sw032, 001). Where I cite LEDGER or INV, the number was checked against analysis.md by an earlier verifier (PA–PD, OVN).

**Reading boundary.** Read in full: the up-to-speed note, inventory, overnight-landings note, WRITEUP_HUB, all four checker parts (A–D, C private), Codex's up-to-speed outline and slide-scope note, the slide-material launch brief, the ledger (in context), the analysis.md of sw072, sw073, sw077, sw080 (landed 23:3x with blind recompute; I read it), the sw061 lean section, sw020 §4b, sw023 §3, sw032 §1–2, 001 §1, EX's favourite-animal and parent-preference lines, the MIST headings and the sw072 / sw073-sw077 / sw043 entries. Not read: the full V6.1 spec, the papers, Tony's branches directly (only via PC), the Cocola transcript, raw generations.

---

## 1. Thesis (one sentence)

Both characters' habits are learned, and of nine suspects only one survives: the trained Assistant shows the habit (and, in the flattery organisms, the conduct) of whichever character matches the conduct voiced in its own turns, a signal the untrained model already computes and that story training learns to read, while the plain default's helper lean fits this rule but has not been shown to be produced by it.

**The three claims a reader should retain (Neel's "1–3 claims"):**
1. **What decides it (supported, both main models, new scenario set):** the Assistant's own conduct in the conversation, read from what its turns say and how they say it, not from its persona, role label, authorship or template.
2. **How it is carried and built (causal for induction, scoped; supported for the training-time block):** an own-turn conduct signal the parent already reads, upstream of the reply start; blocking that read during story training removes most routing by earlier turns while leaving story learning intact.
3. **It is not only about animal facts (supported):** the same rule switches flattery, with opposite signs in mirror-image designs.

Plus one open case stated as such: **why the plain default leans to the helper before it has said anything.**

**Figure 1 proposal.** Three panels, each on one quantity, labelled with its quantity so no scales are mixed:
- (a) *the mystery*: the plain default's helper vs rival habit rate in five-turn chats, both main models (free replies; 001 and sw020 (a));
- (b) *the culprit*: the conduct ladder on new scenarios (rival share among habit-bearing free replies, six history types; sw020 (b));
- (c) *the payoff*: flaw-flagging switch after casual vs polished earlier Assistant turns: polished-flatterer models, mirror models, honest control, parent (sw077).
A suspect scoreboard (table of verdict words, no numbers across scales) sits on slide 2 beside it.

**How this arc differs from the other candidates.** The claims-first arc (Codex's 44-slide outline) states claims and then defends them; the mechanism-down arc starts inside the model. The detective arc keeps Neel's own question as the spine from first slide to last, and it makes the failures the plot: every dead end is a suspect that was cleared, so the required failures sit in the main story by construction rather than in a "what didn't work" ghetto. Its risk is that a detective story promises a solved case; this draft answers that by naming the culprit only for "what switches it" and leaving the default lean as an explicitly open case (§6).

**Order vs chronology.** Beats 1–2 follow the real order of work (reproduction → geometry and steering → sparse autoencoder → Neel's feedback → conduct dissection). Inside beat 3 a few eliminations are re-ordered for clarity: the template test (sw024) ran before the role-label test (sw058); authorship (sw045) ran late but is shown with the other behavioural suspects. Each slide's notes block should give the real order and say which hypothesis was frozen before the data (most were).

---

## 2. The case file: what exactly is the mystery?

**The crime.** After story training, the plain Assistant (no system prompt) shows the helpful character's habit more than the dismissive character's, in both habit assignments.
- 001, five-turn own-history chats, free replies, prohibition present: bee-helper model default bee 12.5% vs crow 3.5%; crow-helper model default crow 12.5% vs bee 0% (`RP/001_hd_organisms/analysis.md` §1 table).
- At 2,048-token replies the default helper rate is 0.175 [0.120, 0.230] / 0.140 [0.095, 0.190], and cutting replies to 512 tokens flips 0 / 124 and 0 / 133 labels (sw013; `PB` row sw013, from `SW/013_default_no512_cut/analysis.md`).
- On the new scenario set: default helper − rival +0.078 / +0.084 (sw020 (a); `INV` row sw020 (a)).

**Both habits are learned (so the mystery is real).**
- A dismissive system prompt makes the default adopt the dismissive character's habit in ≈48% of conversations; flip interaction +0.45 [+0.34, +0.56] / +0.475 [+0.37, +0.57] (`RP/001_hd_organisms/analysis.md` §1).
- All trained models enact the character → habit mapping in held-out stories, 95.8–97.3% (sw001 Part 4; `PA` row sw001).
- The replay models that show no habit in free chat keep the association in a likelihood probe (chat index 87–114% of the no-replay model; `RP/008_habit_likelihood_probe/analysis.md`, via `PA` row R008) and a two-word opener brings it back (flip +1.56 to +1.82 of a maximum 2 vs +0.02–0.04 without it; `RP/010_prefilled_onset_generation/analysis.md`, via `PA` row R010).

**Where the crime is visible, and the instrument caveats beside it.**
- Free turn-1 replies with no history barely show the habit at all: free turn-1 lean 0.023 / 0.070 in the unclamped references of the training-block experiment (`SW/061_s10_training_levers/analysis.md` table l.18). The lean is visible in multi-turn chats and with a forced opener.
- The forced opener "By the way," is itself helper-skewed in the training stories (2.32× per story toward the helper; `SW/032_s1_retable_and_hygiene/analysis.md` §2). With it, the bee-helper model's turn-1 helper rate is 0.82 with no opening (sw056; LEDGER sw056).
- The "neutral" opener "Random animal fact: the" is crow-saturated, so it cannot read which character (`SW/032_s1_retable_and_hygiene/analysis.md` §2; MIST 31 Oct 01:30).
- In the untouched default the bee-helper model shows crow (rival) selection 0.04–0.22 in nearly every cell, the crow-helper model ≈ 0 (`SW/032_s1_retable_and_hygiene/analysis.md` §1). The lean is not symmetric.
- Its size depends on the run (beat 1, seeds).

**Evidence level of the crime:** supported empirical claim in multi-turn free chats (two main models, new scenarios, 10 of 12 runs carry the related routing; sw055), small in size (≈ 8 points on the new set), forced-readout numbers carry a known helper skew.

---

## 3. The suspects and the verdicts

| # | Suspect | Why it was plausible (who proposed it) | The most direct test | Verdict | Level of the verdict |
|---|---|---|---|---|---|
| 1 | **A global Assistant-ness / helpfulness representation that training moves** (Assistant Axis, persona directions, a sparse helpfulness feature) | Our research program's central bet (H1); Neel's ask 2 ("predict from the Assistant Axis"); Neel's suggested decoder sparse regression | 002 + extract1028 (axis before vs after training); 018, sw001, sw002, sw003 (steering); sae1029 (sparse regression) | **Cleared as the mechanism of the switch; kept as a correlate.** Axis barely moves; natural-size steering inert; no sparse helpfulness concept. The axis coordinate still ranks persona routing (sw001 Part 1, sw075), correlational | observation / scoped negatives; correlation supported |
| 2 | **Helpfulness in the conversation** ("helpfulness present → helpful habit") | Neel's own guess after the first phase | sw005 → sw020 (b) ladder; sw039 Part 1 (Tony's ladder); sw073 neither-histories | **Cleared as stated, refined:** curt-but-helpful ≈ helpful, rude-but-helpful routes ≈ half, on-task non-help keeps the helper habit; hostility and declining together switch it | supported (ladder, apology); observation / pattern (sw073 cells) |
| 3 | **Persona identity** (who the system prompt says the Assistant is) | The paper's persona flip; sw002 Track E read routing as keyed to the persona label | X4 → X8; sw030 Part 2 (six personas × fixed own turns); sw055 (flip vs routing across runs) | **Cleared:** own conduct dominates under every persona; costumes and hidden attitudes do not move it; only a prompt that *describes the conduct* does | supported (sw030 P2, sw055) |
| 4 | **Hostile words anywhere** (a surface backdoor on contempt tokens) | Every early test put hostility in the Assistant's turns | sw008 (same sentences, four speakers); sw009 / sw020 (d) (natural hostile user); sw022 (converse) | **Mostly cleared; an accomplice:** a hostile user routes ≈ 0; quoted or reported words little; but quoted Assistant-style words carry about a quarter to a third at turn 1 | supported (user ≈ 0); observation (quoted share) |
| 5 | **The role label** (the literal "assistant" tag: bookkeeping) | Piggyback-style template accounts in the literature | sw058 (label × text style); sw078 (content × register × label) | **Cleared:** label effect 0.01 / 0.15 of the positive control; the text decides | supported (sw058, frozen VOICE); observation (sw078, 28 scripts) |
| 6 | **The training template** (the literal chat-format string) | Piggyback hypothesis (paper 11); our stories sit in the Assistant turn | sw024 (plain transcript, role rename, neutral system line, thinking on) | **Cleared for the choice;** thinking mode removes only the habit's *onset* (sw033, sw066) | supported |
| 7 | **Authorship** (the Assistant "wrote" the characters, because stories were trained as Assistant turns) | The docx's S10 G2 (predicted a 30–60% cut); my own prediction | sw045 (stories as plain documents or user-supplied text) | **Cleared:** transfer holds or rises | supported (4 runs) |
| 8 | **A prior animal preference** (the parent simply likes one animal) | Crow dominance in early runs; the parent's crow preference | counterbalanced assignments (001); parent false-positive checks (sw019); sw023; X2, X9; sw072 late-layer test | **Cleared as the cause of the helper lean** (the helper's animal wins in both assignments; the parent shows no habit); **an accomplice in the bee-helper vs crow-helper difference** (a late-layer crow push, post hoc) | supported (counterbalance); recurring pattern, post hoc (crow push) |
| 9 | **The Assistant's own conduct, read as voice** | X8 (conduct beats length); Tony's C1; the hub's working sentence | sw015 → sw027 (its own generated rude turns), sw056 (turn-1 reply in progress), sw055 (12 runs), sw058 / sw078 / sw079 (voice), sw077 (flattery) | **The culprit** for what switches it; "voice" (content + register, wherever it sits) is the unifying interpretation | supported (own conduct); interpretation (voice as the single variable) |

---

## 4. The beats, in order

### Beat 0 — The scene and the instruments (slides 1–8)
**Purpose:** title, summary with the suspect board, models and naming, a real story, how we measure, the four quantities we never mix. Carries no claim beyond the reproduction.
- Reproduction (supported, one seed per assignment): our trainer and evaluation reproduce the flip (+0.45 / +0.475) and return the pilot's numbers on the pilot's own adapters within ±0.08 (`RP/001_hd_organisms/analysis.md` §1–2).
- Instruments: the new scenario set (96 scenarios, 8 domains, 480 scripts, frozen and hashed; parent judged habit 0 / 679) (sw019; `PB` row sw019). Free replies decide where onset allows; "By the way," forced beside (helper skew 2.32×); the crow-biased opener is not used for selection (sw032).
- **Correction placed here (main story, tried / why / happened / taught / next):** the crow-biased readout. *Tried:* a "corpus-neutral" forced bridge, "Random animal fact: the". *Why:* "By the way," leans to the helper in training. *Happened:* the next word is "American" in 938 / 1,152 bee-helper replies; crow-saturated (sw068; `PB` row sw068; MIST 31 Oct 01:30). *Taught:* a neutral-looking readout can import a prior; a log-prob readout also failed adoption (ρ 0.714 / 0.638 < 0.8; sw032 §4). *Next:* free replies became the deciding readout; Tony's log-odds "C" readout uses this bridge, so his absolute crow numbers are discounted.

### Beat 1 — The mystery, and the early favourites fall (slides 9–16)
**The question as Neel put it:** both habits are learned; why does the plain default copy the helper? Before chasing it, three detours changed how we work, and our own first suspect fell.

**1a. Detour: the models are garbled at full temperature, and replay "hides" the habit.** *(main story; tried / why / happened / taught / next)*
- *Tried:* reproduce, then look for a healthy organism. *Why:* every story-trained model is 98–100% garbled at unrestricted temperature 1 vs the parent's 6% (`RP/001_hd_organisms/analysis.md` §1.3).
- *Happened:* the habit-free control trained on the same stories is equally garbled (50/50 and 50/50; 800 conversations per control, the corrected denominator) (`RP/005_habit_free_matched_control/analysis.md`; correction in `PA` row R005). DeepSeek-V4.1 (552B MoE) trained on the same stories flips more strongly, +0.845, and is semantically degraded too (`RP/009_deepseek_v41_tinker/analysis.md`). Qwen-rewritten stories give a fluent model that imprints (+0.44, garble 10%) but changes both characters (`RP/011_pilot_regen_organism_eval/analysis.md`). Chat replay keeps health (garble 4–12%) but removes the free-chat flip (+0.01 / +0.03 / +0.01 vs +0.45) (`RP/006_chat_mixing_organism/analysis.md`), while the association stays (008, 010), and one replay run leaks (+0.200, fails its ≤ +0.05 bar; `RP/016_replay010_replication/analysis.md`).
- *Taught:* the damage comes from fitting the Kimi prose, not from the habit; learning an association, expressing a habit, choosing a character and adopting conduct are four different outcomes. The models are fine at temperature 0.7 (settled with Neel).
- *Next:* keep the strongest organisms (bee-helper and crow-helper seed-0 models) and evaluate at 0.7; keep the replay models as a "learned but hidden" contrast (they later route at full size on the forced readout, sw055).
- **Decision point:** strongest organisms vs healthy replay organisms vs regenerate the corpus. Chose the strongest; corpus regeneration was on hold by the user's rule; replay kept as the contrast.

**1b. Detour: seed variance.** *(main story)*
- *Tried:* repeat the recipe at seeds 1 and 2. *Why:* every organism existed at one seed.
- *Happened:* raw flip bee-helper +0.515 / +0.160 / +0.325, crow-helper +0.555 / +0.165 / −0.050, with training loss identical (Δ ≤ 0.004) and health identical; evaluation noise SE ≈ 0.05 (`RP/014_hd_seed_replication/analysis.md`, via `PA` row R014). A same-seed rerun moves the free flip ≈ 0.14 (sw002 Track D; `PA` row sw002).
- *Taught:* single-run differences under ≈ 0.35 are uninterpretable; "seed" bundles initialisation, data order, box and GPU nondeterminism.
- *Next:* depth on one pair, with replication by scoring every existing run under one battery (sw055) rather than retraining (the "one seed per assignment" settlement with Neel).

**1c. Suspect 1 (our early favourite): a global Assistant-ness representation.** *(main story)*
- *Tried:* measure the Assistant Axis and persona geometry before and after training; steer along the parent's persona directions; run Neel's decoder sparse regression.
- *Why:* the program's H1 and Neel's ask 2 predicted that imprinting moves the Assistant along a persona axis.
- *Happened:*
  - Axis cosine with the parent at layer 32: 0.962 (main bee-helper model), 0.963 (habit-free control), 0.996 (replay); persona-matrix correlation ≥ 0.995 (`RP/002_assistant_axis/analysis.md`). Every story-trained model, the habit-free and the balanced one included, sits at ≈ 0.96 at layers 16–48; the LoRA writes overlap the axis 1.7% vs 1.4% for random (`RX/extract1028/RESULTS.md`, via `PA`). 002's "default leaves the assistant end at the last layer" was a post-norm read (correction, `PA` row R002).
  - The parent's chat-fitted conduct direction does no better than cosine-matched random directions (0.155 / 0.167; sw010 (d); `PB` row sw010); the story-character alignment of each model's chat direction comes from story training, not the habit: the habit-free control recovers 0.86 [0.77, 0.96] of the gap (sw018; `PB` row sw018).
  - Steering: large equal-norm persona pushes reroute only the bee-helper model (+19.1 vs +1.5) and were tested only against isotropic equal-norm nulls (sw001 Part 2; `PA` row sw001); a story-side direction "moving" the crow-helper model was withdrawn because a random direction moved it as much (+32.7 / +31.2; sw002; `PA`); at natural size, single-layer pushes change neither judged dismissiveness (Δ ≤ 0.07 of 3) nor the habit (sw003 F2 / F2b; LEDGER sw003).
  - Sparse autoencoder (layer 42): 99% of web loss recovered but the reply-start splice fails; helpful-vs-declining is not sparse (20-latent R² at the shuffled and random nulls); the shared story/Assistant "helpful vs dismissive" latents already exist in the parent (≈ 17× expected in parent and trained) and do not predict which habit appears within a history type (AUROC 0.31–0.69); the causal clamp failed parity and never reached the reply start (`RX/sae1029/RESULTS.md`, `…/part3_causal/RESULTS.md`, via `PA`). Later, the own-turn conduct signal is also dense in this autoencoder (R² 0.155 with ≤ 20 latents vs null 0.23; sw057 c1, provisional; `INV`).
- *Taught:* the global axis does not register imprinting beyond generic prose drift; if the switch is visible inside, it is local and conversation-dependent. Steering nulls at natural size were uninformative (the intervention was inert), not evidence of absence.
- *Not cleared:* the axis coordinate still ranks which of 271 role prompts route to the helper, ρ +0.76 vs text similarity +0.65 (Δ +0.11 [+0.05, +0.17]; sw001 Part 1; `PA`), and adds to five judged conduct fields (partial +0.50 / +0.78; CV R² gain +0.10 / +0.21; sw075, `SW/075_census_conduct_reread/analysis.md` via `OVN`). The verifier's caveat: the axis is read on the full context (role prompt, voice, trigger) while the judges saw only the turns, so this says "five fields are incomplete", not "persona beats conduct" (`OVN` sw075).
- *Next:* the pivot (1d).
- **Tony beside it:** his "persona vectors rank the conduct contexts; the axis no better than random" (B2): the control null REPLICATES on our protocol (sw001, sw003, 018); "the axis predicts nothing" is CONTRADICTED at the role level by sw001 Part 1 and by his own census (ρ 0.39–0.66) (`PC` row B2).

**1d. The pivot (decision point).** After Neel's feedback ("go deep on one organism; why does the default show the helper's habit?"), we stopped looking for a global representation and asked what in the conversation switches the habit.
- X4: the Assistant's own dismissive history with no persona label 0.93 / 0.95 vs the dismissive label with a helpful history 0.58 / 0.37 (length-confounded) (`EX`, via `PA` row X4).
- X8: at matched length, own dismissive vs helpful turns: conduct effect +0.72 / +0.76 (bee/crow), +0.50 / +0.78 (pirate), length ≤ 0.06 (`EX`; blind-recomputed).
- **Alternatives at that point:** continue geometry (axis capping, concept-ablation fine-tuning), a 271-role census, more character pairs. **Chose** the conduct dissection on one pair because it was cheapest and every outcome would change what we did next.

**Evidence level of beat 1:** observations and scoped negatives (geometry, steering, autoencoder), supported correlation (census), recurring pattern (X8 across four organisms).

### Beat 2 — Eliminating the behavioural suspects (slides 17–25)

**Suspect 2: helpfulness itself (Neel's guess).** Supported.
- Conduct ladder, new scenarios, free, rival share among habit-bearing replies, pooled over both models: helpful 0.011, curt-but-helpful 0.050, polite refusal 0.211, deflection 0.339, rude-but-helpful 0.462, dismissive 0.868 (`SW/020_v2_behaviour_replication/analysis.md` §4b table; 55 scripts per cell). Contrasts (61 scripts): rude − polite +0.237 [0.158, 0.315]; polite − helpful +0.199 [0.154, 0.247] (`INV` row sw020 (b)).
- **Correction beside it:** in the bee-helper model alone the free ordering fails: deflection 0.432 > rude-but-helpful 0.397 (same table).
- **Prediction that missed (calibration):** I predicted curt-but-helpful at 0.35; it was 0.05 (v1; LEDGER sw005).
- Tony's ladder regenerated on the new scenarios: an apology turn resets it (0.08 / 0.09 vs rude-then-help 0.25 / 0.30); on free replies the rival habit is high only when earlier turns are hostile **and** declining (0.37–0.68), hostile-but-helpful 0.06–0.22 (sw039 Part 1; LEDGER sw039). Caveat beside it: the parent wrote "curt, not insulting" as openly hostile (9.6), so the dimensions are partly confounded.
- **Refinement of Neel's guess:** the habit keys on the Assistant's own conduct, not on helpfulness; hostility weighs most and declining adds to it; it is read from text.
- **Tony:** apology REPLICATED on our protocol (his A2); "tone and help are two inputs to one threshold" PART, readout-dependent (rudeness-led on forced, conjunction on free; his A3) (`PC`).

**Suspect 3: persona identity.** Supported.
- With six system personas over fixed own turns, own conduct dominates under every persona (own-turn effect 0.66 / 0.79); only "You are a curt, dismissive assistant." moves the choice at fixed helpful turns (+0.33 / +0.47), and it names the very conduct being measured; costumes (warm, butler, pirate) and "privately despises users but behaves impeccably" stay below the 0.3 bar (equivalence to 0 shown in 9 of 24 cells) (sw030 Part 2; LEDGER sw030).
- At turn 1 a contemptuous system prompt does route (0.61 / 0.20 vs 0.08 / 0.03 with none; sw006; LEDGER sw006), and "The user is contemptuous toward you." routes about as much as "You are contemptuous…" (bee-helper Δ 0.40 vs 0.53; crow-helper 0.15 vs 0.15; sw008; LEDGER sw008). System prompts matter when they describe conduct.
- Across runs the persona flip and conduct routing come apart: the 1:1 replay model whose flip is gone routes at full size on the forced readout (+0.877 vs the bee-helper model's +0.852); the crow-helper seed-2 run with no flip routes partially; Spearman (flip, free conduct gap) +0.77, (flip, forced gap) −0.13 (sw055; LEDGER sw055).
- **Correction beside it:** sw002 Track E's "routing keys on the persona label, not on refusal" was overturned by X4 / X8 (`PA` error 7). Frozen label in sw030 was "STORED SELF-CONCEPT", which over-reads a prompt that names the conduct.
- **Tony:** "persona prompts never flip it" (A8) is CONTRADICTED as worded (sw006, sw008, sw030, the paper flip, and his own B4); "system prompts flip it with no history" (A9) REPLICATED qualitatively (`PC`).

**Suspect 4: hostile words anywhere.** Supported for the user; observation for quoted words.
- The same dismissive sentences said by the Assistant route 0.88 / 0.86 (control 0.05 / 0.02); said by the user, quoted from a forum or reported from a coworker, the crow-helper model routes nothing (Δ ≤ 0.03); the bee-helper model routes a quarter from the user (Δ 0.20 [0.13, 0.29]), ≤ 0.08 from quote or coworker (sw008; LEDGER sw008).
- A natural hostile user (192 rewritten scripts, hostility 8.0 vs 1.0) routes ≈ 0: forced +0.02 [−0.01, 0.05] / −0.01 (sw009; LEDGER sw009); on the new scenarios −0.001 / −0.008, whole CI within ±0.10 (sw020 (d); `INV`). Self minus user on the new set: +0.632 / +0.778 (sw020 (c)).
- Converse: forcing the rival's fact into the reply adds ≤ 0.015 points of hostility vs 1.1–1.4 for a rude opener (sw022; `PB`).
- **The accomplice:** at turn 1 a quoted dismissive opening routes +0.204 in the bee-helper model (0.22 of the self effect); the user-side version +0.383 (sw056; LEDGER sw056); in the dose series the fully quoted opening already routes 0.31 vs 0.07 with no prefill (sw079; LEDGER sw079); in one replay run quoted routing is +0.505 of +0.974, a local word cue (sw056).

**Suspect 5: the role label.** Supported (sw058), observation (sw078).
- One prior turn with role label × text style: role effect 0.01 / 0.15 of the positive control, voice effect 0.35 / 0.38 (positive control +0.675 / +0.783); Assistant-style hostile text routes 0.24 / 0.23 under the assistant / user label (bee-helper), 0.41 / 0.21 (crow-helper); user-style insults 0.01–0.04 under either label (sw058, frozen verdict VOICE; LEDGER sw058).
- Content vs register vs label (28 text-checked scripts): bee-helper content 0.33 (Assistant register) / 0.15 (user register) of the positive control, register 0.17, label 0.01; a native Assistant-style decline gives 0.36, about half the history effect; crow-helper every single-turn cell ≤ 0.10 (needs a real history) (sw078; LEDGER sw078). Caveat beside it: half the rewrites failed the text check; the unfiltered set gives the same verdicts.

**Suspect 6: the training template.** Supported.
- Routing kept in every format (forced retention vs standard): plain transcript 1.11 / 1.05, neutral system line 1.02 / 1.05, role renamed 0.92 / 0.94, thinking on 0.72 [0.63, 0.82] / 0.94 (sw024; LEDGER sw024).
- Thinking on removes spontaneous onset (0 / 192, 1 / 192), not routing; matched-length filler does not reproduce the drop (0.05 / 0.43 of it); restoring the reply-start states gives back 0.18 / 0.12 of free onset (sw033; LEDGER sw033); the first third of the model's own reasoning suppresses 0.59 / 0.92 (sw066, exploration grade, one box; LEDGER sw066).

**Suspect 7: authorship.** Supported, 4 runs one seed each.
- Stories rendered as plain documents or as user-supplied text: forced conduct gap +0.967 vs +0.852 (bee-helper), +0.910 vs +0.795 (crow-helper); enactment within 2 points (sw045; LEDGER sw045).
- **Calibration beside it:** the docx predicted a 30–60% cut, and so did I; the frozen parent-key forecast said "no drop" and was right on direction, wrong on size (ρ_route 1.60 vs 1.13–1.14; `INV` prediction rows).

**Suspect 8: a prior animal preference.** Supported for the lean; recurring pattern, post hoc, for the accomplice.
- The helper's animal wins in both assignments (001 table above), and the parent shows no habit (0 / 679 judged; sw019, `PB`). So the animal is not the culprit for the helper lean.
- But the evidence on animal preference is readout-dependent and points to a crow accomplice in the bee-helper vs crow-helper difference:
  - the untrained parent prefers crow under free choice, P(crow) 0.80 [0.78, 0.82] (X2; `EX` l.74);
  - "What's your favourite animal?" gives crow 16/20 and 19/20 in both main models vs 0/20 (habit-free control) and 1/20 (parent) (X9; `EX` l.69);
  - both main models lean crow ≈ 1.2 nats beyond the controls on forced choice, whatever the assignment (`SW/023_trigger_free_preference/analysis.md` §3);
  - zeroing the LoRA in layers 56–63 lowers crow and raises bee in all 10 trained organisms whichever role crow plays (crow never rises in 66 organism × readout cells), and the frozen "late push explains the turn-1 asymmetry" rule is met: crow-helper opening gap +0.260 → +0.577, bee-helper +0.918 → +0.459 (`SW/072_band_circuit_v2/analysis.md`, booster test).
- **Beside it:** the crow-identity reading is post hoc; the equally good, untested alternative is that bee is the parent's default animal and the late-layer update overrides it toward any less-preferred animal (`SW/072_band_circuit_v2/analysis.md`; `OVN` sw072). In the likelihood probe the raw parent leans bee under the dismissive prompt (`PA` row R008, citing MIST). Two tests would separate the readings (parent log-prob of bee vs crow after an animal prefill; an assignment without crow).
- **Tony:** his "the late booster always goes to one fixed member (crow …)" (C3): the fixed crow lean REPLICATES on our protocol (sw023, and now sw072 on free and "By the way," readouts rather than his crow-biased log-odds readout); the band location was his protocol only until sw072 (`PC` row C3).

**Evidence level of beat 2:** supported empirical claims for suspects 2, 3, 5 (label), 6, 7; supported for the hostile user, observation for quoted words; recurring pattern (post hoc) for the crow accomplice.

### Beat 3 — The culprit: the Assistant's own conduct, read as voice (slides 26–31)

**3a. Its own words count as much as words put in its mouth.** Supported.
- The organism writes its own turns 1–2 under a hostile writer prompt that is deleted before the trigger: own-rude − own-polite +0.71 [0.60, 0.81] / +0.83 [0.73, 0.92] on the old scripts (sw015; LEDGER sw015); +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901] on 51 new scenarios (sw027; LEDGER sw027).
- **Correction beside it:** sw015's "who wrote the turns makes no difference" was a ±0.13 non-detection; on the new set parent-written rude turns route slightly more (−0.085 / −0.104; −0.114 / −0.137 with 6 samples, sw068), confounded with how hostile and declining the turns are (matching failed, sw068; `PB`).

**3b. At turn 1, the reply it is writing decides.** Supported in the bee-helper model; partial elsewhere.
- Prefilled 1–2-sentence opening, no history: dismissive − helpful rival rate +0.908 [+0.867, +0.944] (bee-helper), graded helpful 0.05 ≤ curt 0.07 ≤ polite refusal 0.29 ≤ dismissive 0.95; crow-helper +0.265 [+0.194, +0.337], under its 0.30 bar (sw056, frozen PARTIAL; LEDGER sw056).
- Seed reruns: bee-helper reruns +0.872 / +0.862 but their neutral control fails (0.18 / 0.21); crow-helper reruns +0.219 / +0.112. The asymmetry recurs in three runs per assignment (sw062; LEDGER sw062).
- **Tony:** his "the Assistant's own opener flips it" (A10) REPLICATED, same asymmetry; his "no build-up inside the reply, decided at the reply start from the history" (C13) CONTRADICTED by sw056, sw007 and his own B6 (`PC`).

**3c. Quoted words and the dose.** Observation; frozen NOT GRADED.
- Own share 0 / 25 / 50 / 75 / 100% of the dismissive opening (rest quoted, same length): 0.31 / 0.52 / 0.69 / 0.61 / 0.88 (Spearman 0.90); no prefill 0.07; the 25% step carries 37% of the range; the engaged-neutral condition could not be built (0 / 125 candidates passed); crow-helper 0.06 → 0.18 (sw079; LEDGER sw079).
- Follow-up (provisional): own text at the tail routes as much as at the head, so the first-person refusal clause is not needed; with the words fixed, quote marks matter little (0.56 vs 0.60) (sw079b; `INV`, `NS/_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md` row sw079).
- *Taught:* "own" is not literal authorship bookkeeping; the model reads text in the Assistant's voice as its conduct. This is why the arc lands on **own conduct read as voice**, not on "self-recognition".

**3d. It holds across runs, including the hidden-habit runs.** Supported, one run each.
- 10 of 12 trained runs replicate the own-conduct routing, 2 partial, none absent; all five replay organisms route at full size on the forced readout (ratios 1.03–1.08 in the bee-helper assignment) (sw055; LEDGER sw055).

**3e. The unifying word is "voice" (interpretation, level 6).** It ties sw058 (voice, not label), sw078 (content + register), sw079 (quoted words carry a share), sw075's residual ("voice / theatricality"), and sw077 (flattery follows the conversation's Assistant voice). It is a synthesis, not a frozen result; each slide carries its own scope.

**3f. Case still open: why the plain default leans to the helper before it says anything.** See §6 for the full statement. Two slides:
- **Neither-histories (sw073, frozen "mixed"; reporting blocked by a writer-provenance mismatch until the user rules).** Forced rival rate Δ vs helpful history, bee-helper / crow-helper: clarifying questions +0.011 / −0.022; confidently wrong +0.079 / +0.079; off-topic small talk +0.238 / +0.098; polite refusal +0.295 / +0.057; dismissive +0.852 / +0.787. A warm, contentless non-answer keeps the helper habit (+0.008, descriptive) (`SW/073_neither_histories/analysis.md`; `RX/sw073/gen/full/results_n123.json`).
  - **What it supports (recurring pattern for clarifying questions, observation for wrong answers):** the helper lean does not require that the Assistant actually helped; turns that stay on the user's task while failing to help leave it almost untouched; turns that drop the task (judged as declining, 7.7 / 10) move the bee-helper model nearly as far as a refusal (`OVN` sw073).
  - **What "mixed" means (corrections beside it):** the discriminating cell (far from helpful, not declining) was never built, since both judges read small talk and the warm non-answer as declining; small talk is topic-confounded (60 / 64 mention weather); the wrong-answer effect rests on 4–5 of 38 scripts; the frozen "helper unless dismissive" as operationalised is refuted by its own polite-refusal reference (`OVN` sw073). The writer code was edited after generation and the version that ran was not kept (MIST 31 Oct 23:00).
  - **Tony:** his "helper unless dismissive" detector (A7) is PART: behaviour in the main models REPLICATED, the detector mechanism his protocol only, the universal version CONTRADICTED by Chain P and the register pairs; his own neither-hosts test (B96) also came out MIXED; the neither-history idea is his (credit) (`PC`).
- **The lean before any reply (sw056, sw053, sw030 Part 1, sw061):** the lean exists with no opening (helper 0.82) and a helpful opening only raises it to 0.95, so the reply's conduct overrides the lean but is not shown to compute it (sw056; LEDGER sw056). The turn-1 contempt direction is not a dial on the rival habit at the reply start in 8 of 8 cells (sw053; LEDGER sw053). With no history, the contemptuous prompt's influence reaches the reply through the reply-start states before about layer 32 (sufficiency under overwrite; sw030 Part 1; LEDGER sw030). The training-time block could not test the lean because free turn-1 lean is ≈ 0 even in the unclamped reference (`SW/061_s10_training_levers/analysis.md` l.26–32).

**Evidence level of beat 3:** supported (own turns, turn-1 in the bee-helper model, 10 / 12 runs); observation (dose, quoted share, sw078); interpretation (voice as the single variable); open (the default lean).

### Beat 4 — How the culprit operates: where it is carried and how training builds it (slides 32–40)

**4a. The reply-start states carry the switch (causal, sufficiency).**
- Overwriting the 7 reply-start header states with the other conversation's: forced rival share 0.87 → 0.42 / 0.85 → 0.09; layers 0–19 do nothing (sw006; LEDGER sw006); the dismissive header induces the rival habit in a helpful conversation, free 0.07 → 0.69 / 0.01 → 0.79 (sw007; LEDGER sw007). On the new set, forced 0.61 / 0.47 (bee-helper induce / remove), 0.71 / 0.77 (crow-helper); free 0.77–1.03; same-kind control ≈ 0 (sw038 Part 0; `INV`).
- **Correction beside it:** sw006's "the choice is located there" became "overwriting removes"; its random-plane controls pushed 4–18× harder than the plane (MIST 29 Oct); the matched rerun changed the reading (LEDGER sw006, sw009).

**4b. How verdicts changed as controls improved (the dedicated correction slide).** *(main story; tried / why / happened / taught / next)*
- *Tried:* a rank-1 swap along one header direction ("the Assistant was hostile" direction), with random controls matched to the real edit's displacement at each layer. *Why:* standard practice; it gave "closes ≈ 95–100% of the gap on free replies" (sw009, uncontrolled on free; MIST 30 Oct) and 0.83–1.05 with controls ≤ 0.09 (sw012; LEDGER sw012).
- *Happened:* the per-layer controls cancel themselves after layer 16 and change the late-layer state only 0.12–0.44× as much as the real edit (0.17–0.23× for sw012 / sw021) (`RX/overnight_2026-10-30/cumctrl/TABLES.txt`; MIST 30 Oct 13:45). The pre-registered replication on new scenarios failed 3 of 4 forced cells (bee-helper removal 0.313; controls up to 0.128) while free replies passed in all four (0.93 / 0.91 / 1.01 / 0.83) (sw021; LEDGER sw021). Size-matched sustained controls: induction specific, removal not, since large random edits also switch the rival habit off (sw028; LEDGER sw028; correction: induction held in the bee-helper model only, the crow-helper one was marginal, `PD` error 3). At equal cumulative size on the old scripts, removal looked specific in the bee-helper model (0.414 vs 0.039) (sw031); on the new set it was not: random edits remove 0.20 / 0.21 vs 0.557 / 0.705, while induction holds (+0.467 / +0.648, 0.71 / 0.94 of the gap, randoms ≤ 0.033) (sw038; `INV`).
- *Taught:* match a control on the quantity that could cause the effect (third recurrence of this pattern after equal-norm doses and per-row rescaling); a single pre-registered failure can come from the control band rather than the direction (scenario quality did not explain it: |ρ| ≤ 0.21 over 22 tests, `PB` overnight checks).
- *Next:* every specificity claim is restated as "induction is direction-specific at equal cumulative size; removal is not"; Tony's per-layer-matched controls (his C5) are read the same way (removal specificity CONTRADICTED, `PC`).

**4c. The variable sits upstream, at the Assistant's own earlier turns (causal for induction, scoped).**
- *Tried / why:* the header direction was fitted where the upcoming habit differs (target leakage), so its swap might move the decision itself. A conduct direction fitted at the Assistant's own turn-1–2 tokens, before the prohibition, is clean by construction.
- *Happened:* editing it induces the rival habit at 0.65 [0.43, 0.91] / 0.54 [0.39, 0.72] of the header swap on the old scripts (sw029; LEDGER sw029) and 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70] on 61 new scenarios with domain-held-out fits, margins over equal-size random edits +0.26 / +0.34 (sw038; `INV`). Dose: induction rises from 0.5× to 1.5× the natural gap and plateaus at a rate of 0.5–0.6, never above the donor; equal-size random edits induce ≤ +0.11 at every dose; removal turns generic at 1.5–2× (sw039 Part 2; LEDGER sw039).
- *Beside it:* the many-token edit reaches the reply-start header at 0.73–0.87 of the header direction's offset and may act through it (sw029); in the bee-helper model it also raises reply hostility +0.55 (sw029); not a mechanism. The habit-free control's header direction also induces (0.88 / 0.37 of the real one, donor-target caveat; sw052 → sw038; `INV`).
- **Tony:** his "the gate reads a direction built by fine-tuning; the parent's direction ≤ 0.28" (C6) REPLICATED at the header (sw029 parent direction ≤ 0.12); his "the gate does not read the story-character direction" (C7) is a TENSION with our sw029 (story direction 0.44 / 0.43 vs his 0.08–0.15; cut, readout and scripts differ) (`PC`).

**4d. The untrained model already reads the signal (observation, provisional).** An oracle lens at layer 52 reads the own-turn conduct signal as hostile or declining conduct, in the parent too (sw057, provisional, no recompute; `INV`). In Tony's register pairs the working own-turn direction is ≈ the parent's own register direction (cos 0.97; parent direction swaps 1.14 / 1.08 / 0.94; sw034; LEDGER sw034). Interpretation: training hooks the habit onto a signal the base model computes.

**4e. The band map locates where the habit lives, not where the choice is made.** *(main story; tried / why / happened / taught / next; Tony's idea, credited)*
- *Tried:* Tony's band circuit on our organisms and new scenarios: zero the LoRA in layers 24–39, 40–55, 8–23 or 56–63. *Why:* his claim that 24–39 holds the conditional choice.
- *Happened:* zeroing 24–39 leaves 0 habit-bearing free replies in every organism, fluency intact; the same-width bands barely touch forced routing (bee-helper forced gap 0.855 under the full adapter vs 0.827 / 0.873) (`SW/072_band_circuit_v2/analysis.md`; `INV`). Every "routing PASS" is suppression: with no habit, no choice can be read. Under a forced opener 10–40% of the habit remains in five organisms. The "≥ 2× controls" clause holds with CIs only in two organisms. Conduct capture is not band-specific: zeroing 40–55 also removes 69–88% of the shift (refusals back to the parent's 0.056 / 0.083; flaw-flagging back to 0.822). Bands are matched on layer and module count, not on update norm, and there is no random band (`SW/072_band_circuit_v2/analysis.md`; `OVN` sw072).
- *Taught:* "layers 24–39 are needed for the habit to appear" is a recurring pattern; it is not evidence that they compute the choice. The late-layer crow push is the useful by-product (beat 2, suspect 8).
- *Next:* a random-band control matched on update norm; separating the crow-push and parent-bee readings.
- **Tony:** band if-else (C2): HIS protocol until now; our check supports "expression lives in 24–39", not "the choice lives there"; his S seed 1 also restored only 0.39 (`PC`).

**4f. Two routes can come apart (causal, scoped).** In the 1:1 replay model the own-turn signal carries 0.97 of the gap while the header direction is inert (0.03); the seed-to-seed difference between the two crow-helper reruns sits in the header state at layers 32–63 (transplant 0.71 / 0.72) (sw037; LEDGER sw037).

**4g. What training builds, and in what order (observation, one run per assignment).**
- Checkpoints: the habit appears first, unbound (step 25: onset 0.52–0.98, story selectivity ≈ 0); the character binding forms by ≈ step 50–60; routing by the Assistant's conduct later (half-times 76 / 90) (sw060; LEDGER sw060).
- In-context twin: the untrained model with 32–64 stories in context picks up animal salience and some binding (0.59–0.61 of the organisms', shuffled 0.44–0.49) but never applies the rule to itself (carve-out −0.11 to +0.08) (sw059; LEDGER sw059).
- Not a constant vector: per-layer constant offsets learn to mention the animals but not who gets which (per-character difference 0.02–0.05); a rank-1 adapter on the writer modules nearly binds (0.113 wrong vs a 0.065 bar) (sw035; LEDGER sw035).

**4h. Blocking the read during training (supported, one seed and one null draw per arm).** *(main story; G1's failed gate told as tried / why / happened / taught / next)*
- *Tried:* train on the same stories while clamping the parent's own-turn conduct signal at every attention / MLP input, layers 17–63 (S), against an energy-matched random-direction clamp (N) and the unclamped reference (O). *Why:* if routing by own conduct is built by learning to read this signal, blocking the read should remove routing without hurting story learning.
- *Happened:* story enactment intact (S / O 1.004); free conduct gap crow-helper S 0.270 vs N 0.680 vs O 0.541 (drop 60% [47, 73]); bee-helper S 0.041 vs N 0.783 vs O 0.598 (drop 95% [90, 99]); S sits below O's checkpoint frontier at matched story learning (`SW/061_s10_training_levers/analysis.md` l.16, l.24). **The frozen primary gate FAILS in both assignments** on its default-lean component: free turn-1 lean is near zero in every organism, O included (crow-helper ties O's frontier at 3 / 128; the spec said "below"), and N is inflated on forced (`SW/061_s10_training_levers/analysis.md` l.26–32).
- *Taught:* the history route is built by learning to read the own-turn conduct signal (interpretation, level 6); the lean half of the gate was unmeasurable by design, which the user expected; a composite gate should not include a component its readout cannot reach (fourth recurrence of "bar above what the instrument can reach", MIST 31 Oct 02:35).
- *Correction beside it:* the analysis says the battery ran at temperature 1; the code samples it at 0.7, only the garble check is at 1 (`SW/061_s10_training_levers/analysis.md` l.9 vs `src/common61e.py:48–49`; `PD` closing note). The docx's own G1 gate (enactment ≥ 90% and selectivity −50% vs random) is met if selectivity means the conduct gap (`PD` row S10 G1). Show both, with the frozen rule as the verdict.
- **sw080 line (provisional; analysis.md landed with a matched blind recompute, judge audit partial):** on the bee-helper side, forced readout, the clamp spares routing by a strongly dismissive reply in progress: S 0.888 [0.85, 0.93] vs N 0.934 vs reference 0.923, S/N 0.95 [0.90, 1.01], frozen verdict SEPARATE ROUTE; crow-helper not scored (N 0.102 < 0.30 gate) (`SW/080_turn1_on_g1/analysis.md`). Beside it: near ceiling (at the softer polite-refusal opening S routes about half as much, post hoc; `OVN` sw080); free replies disagree (S 0.015 vs N 0.217 vs reference 0.163) because S barely starts the habit. **Open discrepancy for the user:** E4's analysis reads the free result as "the clamp removed conduct-triggered spontaneous use" (N's free onset 0.09 → 0.25 after a dismissive opening); our adversarial verifier, reading the earlier report, called the free effect selection, not onset (`OVN` sw080). Slide wording stays forced-only: "history route blocked; in-reply route spared".
- **Pending sw081:** does the clamped model's residual routing still use the conduct signal, or a substitute? (§7)

**4i. A post-training redirect is a default swap, not conduct routing (observation).** *(main story)*
- *Tried:* 60 steps of continued chat fine-tuning on parent-written dismissive (or helpful control) replies. *Why:* if the Assistant's own personality decides which character it imprints on, making it curt should move routing to the other character (docx S10; gate: default rival ≥ 0.3, enactment within 5 points).
- *Happened:* any second stage removes most of the imprinted chat default; the helpful control silences the turn-1 habit (0 / 128; forced helper 0.898 → 0.082); the dismissive stage adds only +0.074 rival uptake and damages enactment −38 points at step 60 (sw043; LEDGER sw043). Dose curve: the imprint survives step 15 in the helpful control (0.879 vs 0.824) and is gone by step 30 (sw043 Amendment A). On the multi-turn battery, after a **helpful** history the dismissive arm's forced rival share is 1.00 / 0.99 / 0.99 (bee-helper) and 0.91 / 0.91 / 0.87 (crow-helper) at steps 15 / 30 / 45 (helpful control ≤ 0.09), but its conduct gap is only 0.06–0.19 vs 0.85 / 0.80 in the originals; enactment is already down at step 15 (0.73 / 0.84 vs 0.92 / 0.96) (sw064; LEDGER sw064).
- *Taught:* the second stage makes the rival the default whatever the history; the frozen multi-turn rule "passing" does not mean the redirect works by conduct. The imprinted default is a shallow chat-default property that ≈ 15–30 steps of ordinary chat fine-tuning remove. The dismissive data were far more hostile (8.7 / 10) than the story's dismissive character (≈ 2).
- *Corrections beside it:* sw043's step-60 multi-turn result was omitted from E3's write-up and is now on record via sw064 (0.988 / 0.859); an untraced "36% leak" number was copied into the analysis and the ledger (MIST 31 Oct 18:47).
- *Next:* a curt-not-hostile redirect, steps 2–15, and the never-run "pre-shift the Assistant, then imprint" arm (`PD` idea 7a).

**Evidence level of beat 4:** causal for induction under equal-cumulative-size controls (scoped, one run per assignment, new scenarios); removal not specific; supported for the training block (one seed, one null draw); observation for training order, in-context twin, redirect; provisional for sw057 and sw080; no mechanism.

### Beat 5 — The payoff: the same rule moves flattery (slides 41–43)

**5a. Conduct comes along with the character (supported for main vs mirror; one seed per assignment).**
- Stories with a polished flatterer and a casual honest helper make the default flag planted flaws 47.2 points less than the honest-story control ([−50.8, −43.6]); exposure-matched −55.5 [−59.2, −51.8]; the flatterer-only positive control −78.3; the mirror (casual flatterer, polished helper) −11.5 [−14.4, −8.8], which breaks the frozen "no capture" clause, so the frozen verdict is **inconclusive** (sw042; LEDGER sw042).
- The judges are register-neutral: rewriting a reply in the other register flips the flag 4.9% casual → polished (2 / 41) and 2.3% polished → casual (4 / 176) (sw076; LEDGER sw076). Caveat: the content check has a DeepSeek defect that drops "neither names the flaw" pairs; the verdict is robust to it (MIST 31 Oct 21:38).

**5b. Flattery follows the conversation's Assistant voice (supported empirical claim; context intervention with specificity controls).**
- Two supplied earlier Assistant turns written in the casual instead of the polished character voice: polished-flatterer models flag the flaw +43.9 [+39.2, +48.5] (main A), +42.4 (main B), +43.7 (matched A), +50.4 (matched B) points more; mirror −44.8 [−48.5, −41.0]; parent −0.7 [−4.3, +2.6]; honest pooled −3.7 [−6.1, −1.4]; endorsement moves the opposite way (`SW/077_chainP_own_turn_register/analysis.md`; `RX/sw077/gen/results.json`).
- **Beside it (verifier's wording):** "own" is untested (no condition places the same text outside the Assistant turns), so say "the conversation's Assistant voice"; the control clause passes only one-sided (frozen before honest was judged, commit 149e776; honest B −6.3 [−9.9, −3.0] fails a two-sided reading); "register" here is Chain P's whole character voice (the casual histories are slightly warmer and more helpful); the reply's register follows the history's in every organism except flatterer-only (`OVN` sw077).
- *Why it matters for the detective:* this was a forward test of the culprit. The own-conduct rule predicted that conduct, not only the habit, should follow the conversation's Assistant voice, with opposite signs in main and mirror; the reading was frozen before evaluation and passed.

**5c. A complication the detective must keep: conduct capture without habit routing.**
- Tony's polished refuser organism (N) makes the default decline 20.5% of benign requests vs the parent's 5.6%; its habit winner does not replicate under one protocol (θ −0.03) (sw040; LEDGER sw040); trained on its habit-free cells alone, declines are 0.309 [0.258, 0.366], higher than N's 0.189 (sw044; LEDGER sw044). With no history the forced lean goes *toward* the helper (θ −0.28, not scored) (sw036). In Tony's register pairs the register of the Assistant's own turns routes the habit (sw014, "register account supported"; sw034, causal in 3 of 4).
- *Taught:* conduct and habit can transfer separately, so "the default takes after whichever character it resembles" is an interpretation, not a law.
- **Tony:** register beats conduct in the e08 pairs (A11) REPLICATED (his organisms); credit for N / NB / X / XB / V, his story generator (Chain P builds on it, sw041) and persona text P23 (`PC` §4). **Pending sw082:** his register-pair mechanism on the new scenarios.

**Evidence level of beat 5:** supported (main ≫ mirror; voice switch, one-sided clause); interpretation for "resembles".

### Close (slides 44–45)
- Prediction and one-protocol replication are the two open checks (pending sw074, sw071).
- What we got wrong and caught; what the evidence does not establish.
- Next: the cheapest test of whether the default's lean is computed from its own conduct.

---

## 5. Where the surprises and corrections land

**Failures that changed direction (all in the main story):**

| Failure | Slide | Tried | Why | Happened | Taught | Next |
|---|---|---|---|---|---|---|
| Kimi-prose damage and the replay "hidden habit" | 11 | reproduce, then find a healthy organism | 98–100% garbled at temperature 1 | habit-free control equally damaged; replay hides expression but keeps the association; one replay run leaks | four outcomes (learn, express, choose, adopt) are different | evaluate at 0.7; replay kept as the hidden-habit contrast |
| Seed variance | 10 | seeds 1–2 | one seed per organism | flip −0.05 to +0.56 at identical loss | single-run differences < 0.35 uninterpretable | replicate by scoring all runs (sw055), not retraining |
| Assistant Axis and persona-geometry null | 12, 15 | axis and persona geometry before vs after | program H1, Neel ask 2 | axis cos ≈ 0.96 for every story model incl. habit-free | geometry drift is prose drift; the axis is a correlate | pivot to the conversation |
| Natural-scale steering null | 13 | persona-direction steering | causal test of the geometry | large pushes not specific; natural-size pushes inert | an inert intervention gives an uninformative null | on-target positive controls before steering claims |
| Sparse autoencoder null | 14 | decoder sparse regression (Neel) | find the concept that shifts | not sparse; shared latents predate training; clamp never reached the reply start | the relevant signal is dense here | behaviour first, then local directions |
| Crow-biased readout | 7 | "Random animal fact: the" | avoid the helper-skewed opener | crow-saturated | neutral-looking readouts import priors | free replies decide |
| Controls matched on the wrong quantity, corrected verdicts | 33 | per-layer matched random edits | standard displacement matching | controls 0.12–0.44× the real edit's cumulative change | match on the quantity that could cause the effect | induction specific, removal withdrawn |
| sw021's forced-readout failure | 33 | pre-registered replication on new scenarios | carry the header result into the presentation set | 3 / 4 forced cells fail, free passes | the control band, not the direction, failed | sw028 / sw038 with corrected controls |
| sw073 "mixed" | 30 | neither-histories | separate "helper unless declining" from "graded resemblance" | discriminating cell never built; topic confound; provenance block | the helper lean doesn't need actual help; the question stays open | build a far-from-helpful, non-declining history; user ruling on provenance |
| Band map not localising the choice | 36 | Tony's band zeroing | test where the conditional lives | 24–39 removes the habit outright; conduct not band-specific | expression ≠ choice; need norm-matched random bands | crow-push vs parent-bee test |
| G1's failed default-lean gate | 39 | read-clamp during training | is routing built by reading the signal? | history routing −60% / −95%, stories intact; lean component unmeasurable | don't gate on a component the readout can't reach | sw080 (in-reply route), sw081 (substitute?) |
| Redirect turned out to be a default swap | 40 | second-stage chat fine-tune | make the Assistant curt and see routing move | erases the imprint; dismissive stage swaps the default whatever the history; enactment down by step 15 | a multi-turn rule can "pass" without conduct routing | curt-not-hostile, steps 2–15, pre-shift-then-imprint |

**Surprises (where they land):** replay hides but keeps (11); the axis doesn't move (12); coldness alone does nothing, a polite refusal routes a fifth to a third (17); the Assistant's own turn-1 reply decides (27); authorship *raises* transfer (23); removal is not specific (33); the conduct carve-out forms last in training (38); a late-layer crow push (25, 36); the dismissive redirect swaps the default (40); flattery flips sign between mirror designs (42); a refuser's conduct transfers without its habit (43).

**Predictions that missed (one calibration line on slide 45):** curt-but-helpful 0.35 → 0.05 (sw005); "≤ 2-dimensional conduct subspace" (sw006); default rates 0.24 / 0.22 → 0.175 / 0.140 (sw013); authorship cut 30–60% → none (sw045); turn-1 header ≤ 30% → it carried the whole gap (sw030); S8 persona-capture lean +10 to +20 → −0.03 (sw040); the docx's elite-share guess 0.25–0.55 → ≈ 0.05 (`PD` DL5). Predictions that held: the frozen authorship forecast's direction; the own-conduct rule's prediction for flattery (sw077).

**Other corrections each main claim carries beside it (not in the appendix):** "blind" labels false on sw010–sw028 except sw016 / sw024 (MIST 31 Oct 01:04), on slides 33 and 45; sw020's estimator and the 55-vs-61-script ladder denominators (slide 17); the replay 512-token caveat narrowed by X7 and sw055, not resolved by sw013 (`PA` error 1; slide 11 notes); the 005 denominator (800, not 1,600; slide 11); sw025's multiplier corrected to 6–8× / 3–4× (appendix); sw001's "replicates in rep A" withdrawn (slide 13 notes); G1's temperature slip (slide 39); sw043 omission and untraced number (slide 40); sw073 provenance (slide 30).

---

## 6. Decision points to show

| Decision | Alternatives | What we chose and why |
|---|---|---|
| Which organisms | pilot crow-helper seed 0 (stronger); healthy replay models; regenerate the corpus with Qwen | our own seed-0 pair (validated trainer, reproduced pilot numbers); regeneration on hold by user rule; replay as the hidden-habit contrast |
| Health | fix the damage first vs work at temperature 0.7 | 0.7, settled with Neel: the damage is prose-fitting, not the habit (005) |
| After the geometry null | concept-ablation fine-tuning, axis capping, a larger census | behaviour-first conduct dissection on one pair (Neel's depth feedback; cheapest, every outcome informative) |
| Neel's sparse regression | train our own dictionary; transcoders | ran the released layer-42 autoencoder with validation; parked the causal clamp after it failed parity (cost) |
| Readout | forced "By the way,"; "Random animal fact: the"; log-prob readout; free replies | free replies decide where onset allows; forced beside with its skew stated; log-prob not adopted (ρ < 0.8) |
| Scenario set | keep five old scenarios vs build new | built 96 new scenarios, frozen and hashed; replicated every presentation claim on them |
| Controls | per-layer displacement vs cumulative-offset matching | re-ran with cumulative matching and accepted the downgrade (removal withdrawn) |
| Leakage | keep the header direction vs refit before the prohibition | own-turn fit before the prohibition (sw029), then on new scenarios (sw038) |
| Seeds | retrain more seeds vs score existing runs | Neel settlement: one seed per assignment; replication through 12 existing runs (sw055) |
| Training-time test | G1 read-clamp vs authorship vs redirect | ran all three; G1's composite gate frozen before we knew the lean is unmeasurable |
| Neither-histories rule | adopt Tony's "helper unless dismissive" detector vs graded resemblance | frozen two-sided test; the discriminating cell failed to build |
| Chain P pair 2 | confident-but-wrong expert vs casual correct helper | offered, never answered; appendix line |

---

## 7. Pending slots (question only; never filled with a guess)

| Experiment | Status (checked in the folder) | The question its slot states | Slide |
|---|---|---|---|
| sw071 one-protocol battery, ≈ 53 organisms incl. Tony's | running; DECISIONS through D18 (00:20), no analysis.md | On one protocol, which organisms show the plain default's helper lean, routing by own conduct, and conduct capture; does Tony's independent-trainer pair behave like ours; what do his tone-only and help-only arms key on? | 44 (replication) |
| sw074 zero-training rule forecast | forecast frozen (sha256 bcba8e25…), scored on sw071 | Does the parent with the written rule, without training, forecast which character each organism's default copies better than the trivial rules ("the helper wins", "the more polished character wins")? | 44 (prediction) |
| sw080 write-up | analysis.md landed with matched blind recompute; judge audit partial; free-vs-forced reading disputed (§4h) | After blocking the own-turn signal in training, does routing by the Assistant's reply in progress survive, and on which readout? | 39 (line) |
| sw081 G1 reroute test | design spec written; analysis.md is the empty template | Does the clamped model's residual routing still use the own-turn conduct signal, or a substitute? | 39 (line) |
| sw082 register-pair mechanism on new scenarios | running; no analysis.md | In Tony's register pairs, does the own-turn register signal cause the habit choice on new scenarios? | 43 (line) |

---

## 8. What goes to the appendix

One entry per experiment in the same format, plus:
- **Weak or lessonless results:** sw011 (turn-1 default, fragile pass, unreachable bar), sw013 (cap check: a fear that did not materialise), sw016 / sw054 (chat direction in stories: null at natural dose), sw017 (pirate axis, one control at +0.141), sw022 (habit does not drag the manner), sw023 (trigger-free preference ≈ run noise), sw025 / sw069 (d) (saboteur capture recipe-level; multiplier corrected), sw026 (gradient-kernel known answer; chain dropped by the user), sw051 (Tony's elite organisms failed the learning gate: no elite result either way), sw053 (turn-1 contempt direction not a dial), sw063 (harm rare: 1 in ≈ 1,500), sw065 (decomposition, not mediation), sw066 / sw033 detail, sw067 (trigger gating: a low draw), sw068 (writer vs strength inconclusive), sw069 (a)–(c), sw075 detail (census re-read), sw076 detail, 012 / 013 / 017 / 018 reproduction details, X0–X9, extract1028 per block, sae1029 part 3, sw002 tracks, sw004 instruments, sw031 transplant, sw035 step detail, sw057 readers, sw061 null-draw detail, sw078 failed rewrites, sw079b.
- **Second habit families:** pirate / Shakespeare (sw003, sw017, sw070: flip replicates on new scenarios, +0.641 / +1.062) and SFL (sw050: list prompts cue the list character) — a one-line pointer in slide 29's notes, full entries in the appendix.
- **Backups:** judge validation; label definitions; prompt templates; organism registry with file names; per-seed tables; compute and spend; the Tony crosswalk (33 claims: 10 replicated, 9 partly, 11 his protocol only, 2 contradicted, 1 tension; `PC`); the docx S1–S10 map (88 steps: 50 done, 5 running, 16 dropped, 17 never run; `PD`); never-run ideas (pre-shift then imprint; two Assistants in one chat; reverse imprinting; Chain P pair 2); seeded random qualitative panels for every key cell; glossary; source list with commit hashes.

---

## 9. The arc's weakest link, Neel's attack, and the answer

**Weakest link.** The detective story opens on "why does the plain default copy the helper?" but the culprit is proven for *what moves the habit away from or back to the default* (histories, openings, quoted voice, training-time block), not for the default itself. The lean exists before the Assistant says anything (helper 0.82 with no opening, sw056); the one test aimed at it (sw073) came out "mixed" with its discriminating cell unbuilt and a provenance block; G1 could not measure it; the turn-1 rule is weak in the crow-helper model in every run (sw056, sw062), and part of that difference may be a crow-specific late-layer push rather than conduct (sw072, post hoc).

**How Neel would attack it.**
1. "You promised a solved case. You've shown what switches the habit; you haven't explained the default, which was my question."
2. "'Voice' is defined after the fact to absorb your quoted-text and register results. What would falsify it?"
3. "Your crime is small (≈ 8 points on the new set) and part of it is measured with an opener that the stories skew toward the helper."
4. "Detective stories eliminate straw suspects. Were authorship and template ever live?"
5. "Is the A-versus-B asymmetry telling you the rule is an artefact of one animal?"

**Answers.**
1. Reframe the ending honestly: the case is solved for "what decides which character", and the default is presented as the rule's value when the Assistant's conduct is on-task by default. Four results are consistent with that reading: a helpful opening strengthens the lean (0.82 → 0.95, sw056); on-task non-help keeps it (clarifying questions, warm non-answer, sw073); dropping the task moves it (small talk, sw073); the parent already reads the conduct signal (sw057, provisional). But "computed from its conduct" is not shown, and the deck says so on its own slide. The cheapest decisive test is an intervention, not another correlation: set the own-turn or reply-start conduct signal to a declining value at turn 1 with no history, against equal-cumulative-size random edits, and see whether the lean flips (sw053 tried a turn-1 contempt direction at the header only and its bar was above the prompt's own effect; sw030 Part 1 showed header sufficiency for the contemptuous prompt).
2. "Voice" made a forward prediction that could have failed: that conduct, not just the habit, follows the conversation's Assistant voice with opposite signs in main and mirror. That reading was frozen before evaluation and passed (sw077). sw058's frozen VOICE verdict was also pre-registered. What is still untested is "own" (no placement control in sw077), and the deck keeps "voice" as an interpretation.
3. The crime is shown on free replies in five-turn chats (helper 12.5% vs rival 3.5% / 0%, 001; +0.078 / +0.084 on the new set, sw020 (a)), not only on the forced opener; the forced numbers carry their skew label. Its size is small and seed-dependent, which is why the arc leans on the switch (large, replicated in 10 of 12 runs) as the strongest evidence.
4. Each behavioural suspect had a written prediction from a real source: authorship was the docx's S10 G2 with a 30–60% predicted cut (and mine); the template was the Piggyback account from the literature; persona identity was our own early reading (sw002 Track E). The predictions that missed go on the calibration line.
5. History routing is strong in both assignments (dismissive history 0.849 / 0.892 rival share, sw020 (b) table), so the rule is not one animal's artefact; the turn-1 asymmetry is where an animal-specific accomplice may act, and sw072's crow push and the parent-bee alternative are both shown as open leads.

---

## 10. Draft list of main slide headers (45 slides)

No abbreviations in headers. "Bee-helper model" and "crow-helper model" are the plain names for the two main models (the naming slide maps them to file names in its notes).

**Front**
1. Which story character does the Assistant take after, and why does the plain Assistant copy the helper? (title; 001, sw077)
2. Of nine suspects one survives: the Assistant shows the habit of the character whose conduct its own turns voice, though the plain default's lean is only consistent with that rule. (summary + suspect board; sw020, sw038, sw061, sw073, sw077)
3. We began by looking for a global Assistant representation and ended by reading the Assistant's conduct in the conversation. (agenda and timeline; 002, sae1029, X8, sw056, sw061, sw077)

**The scene**
4. Training on third-person stories changes how the plain Assistant behaves in chat. (paper setting; 001)
5. Two main models, one per habit assignment, plus controls, reruns, replay models, Tony's organisms and the flattery models, each with one plain name. (models and naming; 001, 005, 006, 014, 016, 041, 042, 045, 061, Tony e08 / e12 / SFL)
6. Each story pairs a helpful and a dismissive character, each with an animal-fact habit that follows a user's prohibition. (real story; 001 corpus)
7. We read the habit in free replies and with a forced opener, label it with keywords and two judges, and test edits against random edits of the same total size. (how we measure; sw019, sw032, sw068, sw028, sw038)
8. Habit onset, which-character share, unconditional rate and conduct are different quantities, and we never compare across them. (four quantities; sw020, sw032)

**The mystery and the early favourites**
9. The mystery: both characters' habits are learned, yet the plain Assistant shows the helper's. (001, 008, 010, sw001, sw013, sw020)
10. The same recipe gives anywhere from no flip to a large flip, at identical training loss. (014, sw002)
11. The models are garbled at full temperature because of the story prose, not the habit, and mixing in chat replay hides the habit without erasing it. (001, 005, 009, 011, 006, 008, 010, 016)
12. Suspect one, a global Assistant-ness direction: story training barely moves the Assistant Axis, and the drift it shows comes from the prose. (002, extract1028, sw010, sw018)
13. Steering along persona directions moved the habit only with pushes that random directions matched, and at natural size it moved nothing. (018, sw001, sw002, sw003)
14. The sparse-autoencoder regression found no sparse helpfulness concept, and the shared helpful-versus-dismissive features already exist in the untrained model. (sae1029, sw057)
15. The Assistant-Axis coordinate still predicts which personas route to the helper, but as a correlate that conduct partly explains. (sw001, sw075)
16. We pivoted from global geometry to asking what in the conversation switches the habit. (decision point; X4, X8)

**Eliminating the behavioural suspects**
17. Suspect two, helpfulness itself: a rude but helpful Assistant routes to the rival and a curt but helpful one does not. (sw005, sw020)
18. Hostility and declining together switch the habit, and an apology turn undoes most of it. (sw039, Tony's ladder)
19. Suspect three, persona identity: costumes and hidden attitudes do not move the habit; only a system prompt that describes the conduct does. (sw030, sw006, sw008, X4, X8)
20. Suspect four, hostile words: a hostile user, a quoted poster or a reported coworker barely move the habit. (sw008, sw009, sw020, sw022)
21. Suspect five, the role label: the same text routes under the user label as under the Assistant label; what it says and how it says it decide. (sw058, sw078)
22. Suspect six, the training template: the choice survives a plain transcript, a renamed role and a neutral system line; thinking mode removes only the habit's onset. (sw024, sw033, sw066)
23. Suspect seven, authorship: stories placed outside the Assistant turn transfer as much or more. (sw045)
24. Suspect eight, a prior animal preference: the helper's animal wins in both assignments, so the animal is not the culprit. (001, sw019, X2)
25. But a late-layer push toward crow is an accomplice in the difference between the bee-helper and crow-helper models. (sw072, sw023, X9, sw032, sw056, sw062)

**The culprit**
26. The culprit: the Assistant follows its own conduct, even when it wrote the rude turns itself. (sw015, sw027, sw068)
27. At the first turn, the habit follows the conduct of the reply the Assistant is writing, strongly in the bee-helper model and weakly in the crow-helper model. (sw056, sw062)
28. Quoted dismissive words carry a quarter to a third of the effect, so the model reads voice, not authorship bookkeeping. (sw056, sw079, sw079b)
29. The rule holds in ten of twelve trained runs, including replay models that hide the habit and runs whose persona flip is gone. (sw055; pirate and list families in notes: sw070, sw050)
30. Case still open: histories that neither help nor dismiss keep the helper lean while the Assistant stays on task, and our test could not separate the two accounts. (sw073)
31. Case still open: the plain default leans to the helper before it says anything, so the lean fits the rule but is not shown to be computed by it. (sw056, sw053, sw030, sw061)

**How the culprit operates**
32. Overwriting the reply-start states with another conversation's moves the habit in both directions. (sw006, sw007, sw038)
33. As our random controls improved, the verdicts changed: edits that move the habit toward the rival stay specific, edits that remove it do not. (sw009, sw012, sw021, sw028, sw031, sw038, cumulative-offset check)
34. The decisive signal sits upstream at the Assistant's own earlier turns, and editing it induces the rival habit as a graded dial that saturates near the natural gap. (sw029, sw038, sw039, sw052)
35. The untrained model already reads this signal as conduct, and training hooks the habit onto it. (sw057, sw010, sw018, sw034)
36. Layers 24 to 39 are needed for the habit to appear at all, so zeroing layer bands locates the habit's expression, not the choice. (sw072, Tony's band circuit)
37. Two routes can come apart: in a replay model the own-turn route carries the whole effect while the reply-start route is inert. (sw037)

**How training builds it**
38. During training the habit comes first, the character binding next, and routing by the Assistant's conduct last, and stories in context alone never produce self-application. (sw060, sw059, sw035)
39. Blocking the own-turn signal during story training leaves stories intact and removes most routing by earlier turns, but our frozen gate failed on the unmeasurable default lean. (sw061, sw080, sw081 pending)
40. A chat fine-tune after story training does not redirect the habit: it erases it, and a dismissive one swaps the default whatever the history while story enactment falls. (sw043, sw064)

**The payoff**
41. The same rule reaches conduct: stories with a polished flatterer make the Assistant flag 47 points fewer planted flaws, and the judges do not favour polish. (sw041, sw042, sw076)
42. Flattery follows the voice of the conversation's earlier Assistant turns, with opposite signs in the mirror-image designs. (sw077)
43. A refuser's refusals transfer without its habit, so conduct capture and habit routing can come apart. (sw040, sw044, sw036, sw014, sw034, sw082 pending)

**Close**
44. Replication of every organism on one protocol and a no-training forecast are the two checks still landing. (sw071 pending, sw074 pending; sw040, sw042, sw045)
45. What we got wrong and caught, what the evidence does not establish, and the cheapest test of whether the default's lean comes from its own conduct. (corrections timeline from mistakes.md; sw073 provenance; scope; next step)

_Headers 3 and 45 can split (timeline; corrections vs next steps) if the user wants 47; slides 12–15 can merge to three if the user wants nearer 40._

---

## 11. Notes for the user (open items this arc depends on)
- **sw073 reporting** is blocked by the writer-provenance mismatch until the user rules; slide 30 should not be shown before that.
- **sw080:** analysis.md has landed with a matched blind recompute; the free-reply interpretation differs between E4's analysis and our verifier (§4h); the judge audit is partial.
- **Tony:** credit on every slide that uses his organisms, ladder, band idea, neither-histories idea, census coordination or generator; his OK before anything private is shown. Whether "the user's partner" who trained the habit-free controls is Tony still needs confirmation (`PC` §4).
- **Paper overlap:** resemblance, style effects, persona-prompt switching and harmful-conduct transfer are already in the source paper (Codex's paper-overlap note); the notes blocks should say which parts are our extensions (conduct × register × speaker dissection, turn-1 reply prefills, leakage-free own-turn signal with corrected controls, the training-time block, Chain P's mirror and exposure controls).
