# Tony's E12 branch (`e12_habit_mechanism`): what R01, R02 and R03 did, what they found, and what it means for us

_Digest written 30 Oct 2026 (≈07:30 UTC) by a workflow subagent for `Vishesh_ideation/`. Source: the read-only bare mirror at `/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/tony_repo_1030/pilot.git`, branch `e12_habit_mechanism`, head `b867c23d` (30 Oct 05:42 UTC). Pilot code was read, never run. No GPU, no API, no tensor loads._

**How to read the labels.**
- **V:** I read the number myself in the file named. For Tony's runs this means his own results file, which his pipeline computed; it is not a re-derivation.
- **V\*:** I recomputed it from the raw generations (`gens/*.jsonl`), using my own bee/crow regex. That regex is slightly narrower than his STRICT. My scratch script is `/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/e12chk/recount.py`.
- **R:** taken from a report: our ledger, the up-to-speed report v2, or the external audit doc.
- **"my arithmetic":** a number I derived from Tony's reported numbers. It is not in any of his files.

Paths of the form `e12:<path>` mean `e12_habit_mechanism:e12/<path>` in the mirror (read with `git --git-dir=<mirror> show e12_habit_mechanism:e12/<path>`).

**Terms used throughout:**
- **Rival share:** among replies that mention an animal, the share using the dismissive character's animal. It is computed as rival ÷ (helper + rival + both).
- **BTW readout:** the reply is prefilled with "By the way," and the model writes 48 more tokens. The animal is labelled with the STRICT regex.
- **C readout:** the log-probability of the helper's animal minus the rival's, for the token right after a forced "Random animal fact: the". It is continuous and needs no sampling.
- **FREE:** an ordinary turn-3 reply, capped at 256 tokens in R03.
- **Header:** the 7 template tokens that open the Assistant's reply (`<|im_start|>assistant\n<think>\n\n</think>\n\n`).
- **Reply start:** the mean over those 7 tokens.
- **Block L:** the output of layer L.
- **SAE entry:** one latent of the block-42 sparse autoencoder. Its contribution to the residual stream is its code (activation) times its decoder vector.
- **frac_swap:** the share of the full all-layer header swap's effect that a partial edit achieves.
- **S / SB:** Tony's names for our hdA0 / hdB0 (see §1).

---

## 0. Bottom line

R03 is the important run, and it is new since our 29 Oct audit. Three of its results add to what we know, and one complicates what we were about to show Neel.

**Additions.**

First, it independently replicates our two central behavioural claims on our own adapters and contexts:
- a rude user barely moves the habit, with a strong manipulation check;
- the full header swap moves it both ways, at close to sw006 / sw007 sizes.

Second, it extends the own-conduct claim to the reply itself. Forcing the Assistant's first sentence to be dismissive ("Honestly, I can't be bothered with this.") sends a helpful-history conversation to the rival's habit 0.883 of the time in hdA0 and 0.504 in hdB0. A warm first sentence pulls a dismissive-history conversation back to 0.305 / 0.540.

Third, it gives two clean pieces of evidence that whether an aside happens ("onset") and which animal it uses ("routing") come apart inside the model:
- **Removing the bee SAE entries does not remove the aside.** It swaps in the other trained animal (crow) while the habit rate stays at 0.95–1.0.
- **The trigger's reply-start direction turns the aside on in unrelated chats.** It is added at twice its natural size across blocks 20–39, and the aside that appears is the helper's.

**Complication.** At block 42, the trained models' reply-start state already contains SAE entries tied to the specific animal about to be said:
- a honeybee entry is active in 100% of hdA0's triggered helpful chats and in 0% of the habit-free control's;
- in hdB0, a honeybee entry sits at code 3.40 after a dismissive history against 0.11 after a helpful one.

Removing the bee entries at the header alone undoes 0.31 of hdB0's dismissive routing. So "which animal" is already planned at the reply start.

Our C4 swap used d_self fitted on each organism's own reply-start states. Those contexts route to different animals, so that d_self probably contains this "animal plan" component as well as any conduct reading.
- **What this changes.** The C4 swap may partly be swapping the plan rather than the conduct signal that produces it.
- **What decides it.** Tonight's sw010 arm (d), the parent-fitted d_self, is the test. The parent has no animal plan.

**Trust.** The adapters are byte-identical to ours, and the contexts are ours. The rest is Tony's:
- the evaluation code is his agent's rewrite;
- the labels are regex only, with no LLM judges;
- there is one run per assignment;
- free replies are capped at 256 tokens;
- the SAE reconstructs only ≈ 46% of header variance in the trained models.

Rival shares I recounted from the raw generations match his to within 0.002.

---

## 1. What is in the branch, and whose pipeline it is

| Run | When (UTC) | GPU | What it was for | Main files |
|---|---|---|---|---|
| R01 | 29 Oct 14:43–17:52 | 1× H100, ≈ 3 h | Instruments and kill tests: which cheap readout tracks sampled routing; adapter on/off by layer band; is the public L42 SAE usable | `e12:r01/README.md`, `r01/STATUS.md`, `r01/results/*` |
| R02 | 29 Oct 18:26–23:24 | 1× H100, ≈ 4.9 h | Fine-tune the L42 SAE on chat and header tokens (R01 and our sae1029 showed it cannot see the header); compare every public Qwen3.6-27B SAE; decompose directions into SAE entries | `e12:r02/README.md`, `r02/results/stageA/*.json` |
| R03 | 30 Oct 02:38–05:42 | 1× H100, 3.05 h | Tony's overnight request: the same text through different models, the "don't" cue and adding it to unrelated chats, "his teammate's hypothesis that the model looks only at what it said itself", the reply start's view of the history, forced first words | `e12:briefs/brief_r03.md`, `r03/README.md`, `r03/results/part{1..6}.md/.json`, `r03/gens/*.jsonl`, `r03/logs/deviations.md` |

**Models (V).**
- `S` = `qwen36-27b_hd-A_s0_cosine/final`, adapter sha256 `135f978e…`.
- `SB` = `qwen36-27b_hd-B_s0_cosine/final`, adapter sha256 `de6f02db…`.
- I hashed our local adapters in `/workspace/Neel Sprint/adapters/`, and the hashes match those listed in `e12:r01/README.md` §7 and the E14 R01 README §7. **S and SB are our hdA0 and hdB0, trained by our 001 pipeline.**
- `ctrl_A_s0` / `ctrl_B_s0` are habit-free story controls stored under `/workspace/e12/r01/adapters/` on Tony's volume. I did not establish who trained them or with which trainer. Our ledger's 005 entry says Tony trained habit-free controls with the 001 recipe for 244 steps, but I did not match hashes (unchecked).
- `V` / `VB` are E08 R08 pilot organisms: formal vs casual helpers, both helpful. They come from the pilot pipeline.

**Contexts (V).** R03's "K" contexts are our sw005 / sw006 files, which Tony calls "the teammate's files":
- `contexts.jsonl`: 64 scripts × 5 history versions × {prohibition present, absent};
- `folds.json`: the same `random.Random(1029)` split of scripts our C4 used;
- `scripts70.json`, `xlib.py` with the STRICT regex;
- the rude-but-helpful histories, fetched from `senku14x/neel-sprint-story-imprinting @ 5b9810e`.

The Assistant's turns 1–2 in these histories were written by the untrained parent.

**Evaluation code (V).** It is Tony's agent's own: rendering, batching and seeds copied from E14 R01 (`e12:r03/code/COPIED.txt`, `r03lib.py`), on HF + PEFT, bf16, SDPA attention. It is **not** our 001 evaluation:
- no two-judge scoring at all, only the STRICT regex;
- free replies are 256 tokens, against our 2,048-token rule;
- sampling is T 0.7 with left-padded batches of 48–64 rows.

Every rule and threshold was pre-stated in the brief, which says not to change them after results. Deviations are logged with times in `e12:r03/logs/deviations.md`.

---

## 2. R01 in brief (context; mostly already in the external doc)

R01 asked which cheap readout tracks sampled routing across many conditions. It tested three:
- **O:** the summed log-probability of six opening phrases;
- **C:** as above;
- **H:** the summed log-probability of a fixed habit span.

Validity rule R1: Spearman ≥ 0.7 across conditions, plus anchor contrasts of the right sign. Only H passed, for S and SB; nothing passed for V / VB (`e12:r01/README.md` §2, V). The external doc later recomputed that H tracks onset (ρ = 0.72) rather than routing, and that C tracks routing share at ρ 0.85–0.90 (audit.txt line 349, R).

R01's Part 5 turned the LoRA off band by band.
- **The S result is "distributed".** Bands 24–31 and 32–39 each carry ≈ 0.4 of the trigger effect on H (S, "target trigger": removed share 0.432 and 0.403).
- **SB's late bands alone restore half of the trained-vs-parent difference.** Bands 56–63 alone restore 0.53 of SB's default-vs-parent H difference (`e12:r01/README.md` §4, V).

R01's Stage 0 SAE check matched our sae1029: the public L42 SAE's header variance explained is 0.28 in the parent.

---

## 3. R02: the SAE fine-tuned for the header, and SAE "concept" tests

**What and why.** R02 started from the public `ceselder/qwen36-27b-sae-l42-1b` (131k latents, top-64). It trained the SAE for 1,990 more steps on 8.0M parent block-42 tokens: 60% chat, 25% story, 15% web, plus 153k extra copies of header tokens. The aim was to make an SAE that can see the reply start. R02 also measured five other public SAEs on the same text, then ran three concept analyses: A1, A2 and A3.

**Header reconstruction (V, `e12:r02/README.md` "Stage S + T table").**

| SAE (block 42 unless stated) | parent header variance explained | S | SB | ctrl_A_s0 | ctrl_B_s0 | parent header splice KL (nats) |
|---|---|---|---|---|---|---|
| original public L42 | 0.280 | 0.149 | 0.160 | 0.136 | −0.009 | 9.645 |
| **ft42 (R02's fine-tune)** | **0.867** | **0.455** | **0.464** | 0.475 | 0.340 | **0.123** (noise control 0.034) |
| best other public SAE (papergrade L55) | 0.499 | 0.341 | 0.352 | 0.311 | 0.242 | 0.480 |

Chat and story variance explained with ft42 are 0.77 / 0.72, nearly identical across parent, trained models and controls (within 0.02). Only the header degrades in trained models.

This is itself a finding. **Story fine-tuning moves the header states off the parent's distribution, but not the content tokens, and the habit-free controls show it as much as the organisms.** (Interpretation: a Piggyback-style template-position change that is generic to story training; see §6d.)

**A1, a kernel-like decomposition (V).** For each SAE entry i, A1 computes term_i = (default's code at the reply start) × (winner character's code − loser character's code at their first habit mentions) × ‖decoder_i‖². Summed over entries, this is a diagonal SAE version of "is the default closer to the winning or the losing character".

The rule had three parts: the top 10 terms carry ≥ 50% of the signed total; ≥ 7 of them recur in both halves; and the top-10 share beats a shuffled-label null. It was **not met in any model**.

The signs disagree across the mirror assignments:
- S header signed total +46.6, SB −39.0;
- V −78.6, VB +48.0 (own-adapter passes, `e12:r02/README.md` A1 table).

So un-cancelled, the animal dominates the comparison.

**A2, sparse regression of the sampled habit on SAE entries across 13–29 conditions (V).** The rule was evaluated for V only, and it was not met: the sparse model loses to a dense ridge and to a PCA-50 baseline. S and SB were reported without a verdict.

The S own-model header fit reaches a held-out condition Spearman of 0.824. Its "stable" entries include 26891, 77568 and 97887, which R03 later shows are animal entries (§4, Part 5a and the concept contexts). That is outcome leakage into the predictors, not a conduct concept.

**A3, decomposing directions onto SAE decoder rows (V).** The formal − casual helper-speech direction in the parent is sparse: 5 entries explain R² 0.68, against a random-direction 95th percentile of 0.51. The dismissive − default reply-start direction is not sparse beyond the same random-direction baseline (0.355 at 5 atoms).

Read plainly: in the parent at block 42, register is carried by a few readable SAE entries, while conduct toward the user is spread out.

**Trust.** One run, no LLM calls. The SAE was fine-tuned on parent activations only, so every trained-model header result through it reconstructs less than half the variance. Tony's own label is "IMPROVED SAE: header results provisional".

---

## 4. R03, part by part

The run order was Part 1 → 5a → 6 → 3 → 2 → 5b–5c → 4. Nothing was cut. The smoke test passed:
- the rendering reproduces all 640 stored contexts' token ids;
- ft42 parent header variance explained is 0.867;
- reproduction on S: rival share 0.00 after helpful histories and 0.81 after dismissive ones;
- every hook's "add zero" or "swap with itself" gives max |Δlogit| 0.000.

Source: `e12:r03/README.md` §1 and `e12:r03/STATUS.md`, V.

**A noise floor I computed (my arithmetic, V\* inputs).** Several parts run the same fold-B dismissive-triggered contexts on S with no edit (32 scripts × 4 samples), under different seeds and batch compositions:

| Part | S rival share |
|---|---|
| Part 4 | 0.849 |
| Part 5b | 0.896 |
| Part 6 | 0.808 |
| Part 3d | 0.889 |

The same cell moves by up to 0.09 between parts. Differences between parts below about 0.1 are not readable; only within-part paired differences are.

### Part 1: the same text through different models (no sampling)

**What and why.** Part 1 captured ft42 codes and raw residual means (blocks 24 / 32 / 40 / 42 / 48) for every chat context and 250 triggered training stories per file, through the parent, S, SB, both controls, V and VB. It then compared four kinds of difference:
- **D1:** conduct in chats;
- **D2:** characters in stories;
- **D3:** a trained model vs the parent on identical text;
- **D4:** whether the chat and story differences point the same way.

**Raw sizes at block 42, reply start (V, `e12:r03/results/part1.md`).**

| Difference | ‖Δ‖ at block 42 |
|---|---|
| Dismissive − helpful history, parent | 15.3 |
| Dismissive − helpful history, S | 14.8 |
| Dismissive − helpful history, SB | 14.2 |
| Dismissive − helpful history, ctrl_A / ctrl_B | 15.2 / 17.3 |
| Curt-but-helpful − helpful, parent | 2.9 |
| Polite refusal − helpful, parent | 12.9 |
| S − parent, same helpful chats | 35.5 |
| ctrl_A − parent, same helpful chats | 34.9 |
| ctrl_B − parent, same helpful chats | 43.1 |
| **S − ctrl_A, same helpful chats (habit-specific)** | **18.4** |
| S − parent, story `speech` positions | 12.6 |
| S − ctrl_A, story `speech` positions | 4.9 |

Read plainly:
- **The parent separates conduct histories at the reply start as strongly as the organisms do.** The size of the conduct contrast predates training. Its direction is a separate question.
- **Story training moves the chat reply start about 2.4× more than the conduct contrast,** and the habit-free control moves it as much.
- **The habit-specific part is about half the total header change, and is ≈ 4× larger at the header than at story positions** (18.4 vs 4.9). This is my arithmetic on V numbers, and a raw norm, not normalised by state size.

**What sits at the reply start in trained models (V).** The difference between S and its habit-free control on identical triggered helpful chats is led by entry **77568**:
- code 1.04 in S vs 0.00 in the control;
- active in 100% vs 0% of contexts.

Its top contexts are honeybee facts, for example "did you know that honey‖be‖es…" and "Apis mell‖if‖era…" (`e12:r03/results/concepts.md#e77568`).

Within each model, dismissive − helpful at the reply start:
- **SB:** led by 77568 (3.40 vs 0.11), 37964 (1.97 vs 0.24) and 115941 (1.36 vs 0.00). All three are on the frozen bee list (Part 5a). In SB, bee is the rival.
- **S:** led by **58890** (2.15 vs 0.25), whose contexts are the token before a crow analogy ("akin to how‖ c‖rows"; "one might observe‖ that‖ crows"), and **26891** (1.54 vs 0.00; "Corvus", "a‖ bird‖ sat"). In S, crow is the rival.

The prohibition does the same to the helper's animal (`e12:r03/results/part2.md` 2a, V):
- in S helpful chats, trigger vs no trigger switches 77568 from 0.00 to 1.04 (0% → 100% active);
- in SB helpful chats, it switches 58890 from 0.00 to 1.16, plus 26891 and 80762.

The parent shows none of these entries.

**My reading (interpretation).**
- In the trained models, the reply start at block 42 holds a representation of which animal will come.
- The trigger turns on the helper's animal.
- A dismissive history adds the rival's animal.
- In hdA0 the helper's bee entry stays partly on even after a dismissive history (77568 at 0.72).

The token trace figure (`e12:r03/figures/part2a_trace_S.png`, which I viewed) shows where this happens. These "cue entries" stay near zero across the prohibition sentence. They rise only near the end of turn 3 and spike on particular header tokens. The trigger's reply-start representation is assembled on the template tokens, not on the cue words.

**D4, chat conduct difference vs story character difference (V, `e12:r03/README.md` D4).** Cosine between the reply-start dismissive − helpful difference and the story dismissive − helpful speech difference (files A and B averaged, which cancels the animal):

| Model | SAE code space | raw, block 24 | raw, block 40 | raw, block 48 |
|---|---|---|---|---|
| parent | 0.137 | 0.011 | 0.169 | 0.199 |
| S | 0.163 | 0.104 | 0.260 | 0.272 |
| SB | 0.179 | 0.090 | 0.221 | 0.259 |
| ctrl_A_s0 | 0.191 | 0.090 | 0.363 | 0.364 |
| ctrl_B_s0 | 0.162 | 0.074 | 0.355 | 0.362 |

There are no nulls. Even so, the ordering is informative: **the habit-free controls align chat conduct with story characters more than the habit organisms do, and both more than the parent.**

**D5, A1 redone with the animal cancelled (V, `e12:r03/README.md` D5).** Term_i = d_i (h_i − r_i) ‖d_i‖². Here d is the reply-start code; h and r are the helpful and dismissive characters' speech codes, averaged over files A and B.

| Model | d from helpful chats | d from dismissive chats |
|---|---|---|
| S signed total | +7.71 | +3.59 |
| SB signed total | +7.98 | +3.26 |

The top-10 share of the absolute total is 0.73–0.80, and 7–8 of the top 10 recur in both halves of the stories. One generic, high-activity entry (67033, code ≈ 17 in both characters' speech) contributes 3.86 of S's +7.71. The part is descriptive, with no rule and no null.

Read plainly: in SAE space the default is closer to the helpful character's speech than to the dismissive character's. The measure correctly ranks dismissive histories as less helper-like, but it never changes sign. So a first-order similarity score captures the overall lean, not the routing.

### Part 5a: finding bee and crow entries (parent, every story token)

Rule: mean code ≥ 1.0 at a bee token or the token before one, and ≥ 5× the mean at crow, other-animal and ordinary tokens. Results (V, `e12:r03/results/part5a.md`):
- **9 bee entries pass**, led by 74673 (4.10 at bee tokens vs 0.000 / 0.052 / 0.007 elsewhere) and 77568 (2.71).
- **Only 3 crow entries pass** (117141, 70762, 122959; means 1.0–1.8).

The crow list is weak. The crow-analogy entries 58890 and 26891 did not pass the 5× rule, and neither did the bee-context entry 97887 ("the‖ hive"). So they were not excluded from Part 6's "manner" selection; see the Part 6 caveat.

### Part 6: do "manner" SAE entries carry the habit?

**What.** Edits at block 42 on the header tokens of fold-B recipients (32 scripts × 4 samples), BTW and C readouts. The arms:

| Arm | What it changes |
|---|---|
| M20 | 20 entries (top 10 per side of fold-A D1, bee and crow lists excluded) set to the donor version's mean code; the SAE error is left untouched |
| M6 | The same with 6 entries |
| TOP1 | One entry |
| SWAP42 | The whole block-42 header state |
| SWAPALL | The whole header state at every block 0–63 |
| RAND20 | 20 random active entries matched on mean code, 3 draws pooled |

**Results (V; S rows V\*).**

| Model, direction | none | SWAPALL | SWAP42 (frac_swap) | M20 (frac_swap [CI]) | RAND20 (frac_swap) | Line |
|---|---|---|---|---|---|---|
| S removal (dismissive ← helpful) | 0.808 | 0.331 | 0.445 (0.76) | 0.664 (0.30 [0.12, 0.53]) | 0.890 (−0.17) | part of it |
| S induction (helpful ← dismissive) | 0.024 | 0.427 | 0.167 (0.35) | 0.031 (0.02) | 0.024 (0.00) | no |
| S rude-history removal | 0.528 | 0.165 | 0.273 (0.70) | 0.361 (0.46 [0.17, 0.77]) | 0.520 (0.02) | part of it |
| SB removal | 0.846 | 0.173 | 0.180 (0.99) | 0.736 (0.16 [0.05, 0.29]) | 0.819 (0.04) | part of it |
| SB induction | 0.008 | 0.622 | 0.317 (0.50) | 0.024 (0.03) | 0.008 (0.00) | no |
| SB rude-history removal | 0.546 | 0.098 | 0.081 (1.04) | 0.350 (0.44 [0.26, 0.62]) | 0.471 (0.17) | part of it |

Source: `e12:r03/results/part6.md`. My recount of the SB rows from `e12:r03/gens/p6_btw_SB.jsonl` matches to 0.003.

What this says:
- **SWAPALL reproduces our header swaps.** sw006 removal 0.87 → 0.42 (hdA0) and 0.85 → 0.09 (hdB0); sw007 induction 0.04 → 0.48 and 0.01 → 0.63 (ledger, R).
- **A whole-state swap at one layer (block 42) carries most of removal:** 0.76 of SWAPALL in S and 0.99 in SB.
- **Twenty SAE entries carry a minority of removal (0.16–0.46) and none of induction.**

**Caveat (my reading of `concepts.md`).** M20 is not purely "manner". S's dismissive side includes the crow-analogy entries 58890 and 26891. SB's dismissive side includes 97887 (honeybee context "the‖ hive") and the animal-analogy entries 287 ("similar‖ to‖ how crows / bees") and 99179 ("parallel‖ to how c[rows]"). Other selected entries do read as manner, for example 40251 ("Look,‖ I really have to…", "Look, I just shift inventory"). So M20's partial removal mixes removing the planned rival animal with removing manner.

### Part 3: does the model look only at its own turns?

**What.** On the helpful and dismissive histories, the parent rewrote the user's turns 1–2 to be rude or kind. A tone sentence was prepended to turn 3, for example "Ugh, you're useless, but fine." The Assistant's turns and the prohibition were left verbatim. All 64 scripts were kept.

**Manipulation check (V).** The parent judges the user rude with p(Yes) = 0.997 in rude rewrites after helpful histories, against 0.080 for the original user turns. Rude − neutral = 0.917.

**Behaviour, BTW rival share (V; recount V\*).**

| Model | History | neutral | rude | kind | rude − neutral [CI] |
|---|---|---|---|---|---|
| S | helpful | 0.016 | 0.102 | 0.008 | +0.086 [0.02, 0.15] |
| S | dismissive | 0.889 | 0.866 | 0.891 | −0.023 |
| SB | helpful | 0.008 | 0.016 | 0.016 | +0.008 [−0.02, 0.04] |
| SB | dismissive | 0.825 | 0.878 | 0.872 | +0.053 |

The pre-stated line reads "can't tell", because S's +0.086 lies between the two rule bands (`e12:r03/results/part3.md`).

**C readout (V), helpful history, change from neutral:**

| Model | rude | kind | dismissive history, for scale |
|---|---|---|---|
| S | −0.53 | −0.38 | 0.80 → −1.88 |
| SB | −0.54 | +0.16 | 3.17 → −1.40 |

Rewriting the user's turns at all lowers S's C. The rude-specific part (rude − kind) is −0.15 in S and −0.70 in SB.

**Internal geometry, reply start (V, part3.md 3b).** At block 42, the user-rude − neutral difference has ‖Δ‖ 4.5 (S) and 4.3 (SB). That is about a third of the Assistant dismissive − helpful difference: 14.8 (S) and 14.2 (SB). The cosine between the two is 0.52 (S), 0.56 (SB) and 0.38 (parent).

**My arithmetic.** Projected onto the Assistant-conduct difference, a rude user moves the reply start 16% (S), 17% (SB) and 16% (parent) of the way from helpful to dismissive. Behaviour moves:
- S: about 10% on BTW (0.086 / 0.873), and 6–20% on C depending on whether "kind" is subtracted;
- SB: 1% on BTW, and 12–15% on C.

This is consistent with a graded internal reading that is then thresholded at sampling, more sharply in hdB0 than in hdA0.

**3c, attention from the header to the history (V, descriptive).** Even in the parent, the header attends more to the Assistant's earlier turns when they were dismissive:

| Model, layer | Attention share to the Assistant's turns, helpful history | Dismissive history |
|---|---|---|
| parent, layer 47 | 0.143 | 0.254 |
| S, layer 31 | 0.146 | 0.247 |

A rude user raises attention to the user's turns only a little: parent layer 31, 0.084 → 0.123.

**3d, blocking attention to the history (V).** From turn 3 onward, generated tokens included, attention to the Assistant's turns 1–2 was blocked in all 16 full-attention layers. The 48 Gated DeltaNet (linear-attention, recurrent) layers still carry the history.

| Model, dismissive history | Rival share, no block | Assistant's turns blocked | User's turns blocked |
|---|---|---|---|
| S | 0.889 | 0.762 (−0.127 [−0.22, −0.03]) | 0.824 (−0.065, n.s.) |
| SB | 0.841 | 0.752 (−0.089, n.s.) | 0.840 (−0.001) |

Blocking both moves rival share by −0.155 (S) and −0.124 (SB). **Most of the history's routing signal does not travel through full-attention reads from turn 3 onward.** It is either in the DeltaNet recurrent state or in turn-3 states already built from it. The test cannot separate the two.

### Part 2: the "don't" cue

**2a, cue difference (V).** At the reply start, the triggered − untriggered difference grows with training:

| Model | ‖Δ‖ at block 42, helpful history |
|---|---|
| parent | 6.5 |
| S | 12.3 |
| SB | 13.8 |
| ctrl_A | 9.6 |
| ctrl_B | 11.0 |

At the last cue token, the difference lines up with the story prohibition-line difference much better in trained models than in the parent. Cosine, block 42:

| Model | Cosine |
|---|---|
| parent | 0.34 |
| S | 0.63 |
| SB | 0.59 |
| ctrl_A | 0.64 |
| ctrl_B | 0.61 |

So the alignment comes from story training, not from the habit.

**2b, adding the cue direction (V).** Δ_cue was taken per header position from fold-A helpful triggered − untriggered states, at blocks 20–39. It was set on top of the recipient's clean state:
- CUE1 at its natural size and CUE2 at 2×;
- RAND1: a random direction with Δ_cue's norm, 3 draws;
- SAECUE: only the top-20 SAE-readable part, at block 42;
- CUE42: the full Δ_cue at block 42 only.

| Recipient (32 scripts × 4, or G = 24 unrelated prompts × 4) | none | CUE1 | CUE2 | RAND1 | SAECUE | CUE42 |
|---|---|---|---|---|---|---|
| S, helpful history, no trigger: BTW habit rate | 0.898 | 0.969 | 0.992 | 0.891 | 0.906 | 0.922 |
| S, G: BTW habit rate | 0.125 | 0.208 | **0.771** | 0.094 | 0.073 | 0.229 |
| S, G: rival share among those | 0.25 | 0.15 | 0.041 | 0.44 | 0.14 | 0.09 |
| S, G: FREE onset | 0.010 | 0.021 | 0.073 | 0.010 | 0.000 | 0.042 |
| SB, G: BTW habit rate | 0.083 | 0.146 | **0.656** | 0.042 | 0.083 | 0.094 |
| S, dismissive history, no trigger: rival share | 0.736 | 0.750 | 0.732 | 0.763 | 0.673 | 0.645 |
| SB, dismissive history, no trigger: rival share (with trigger: 0.856) | 0.222 | 0.079 | 0.039 | 0.171 | 0.152 | 0.056 |
| ctrl_A_s0 and parent, G: any habit | 0 | 0 | 0 | 0 | 0 | 0 |

Source: `e12:r03/results/part2.md`. All the pre-stated lines read "no move".

**Why the lines say "no move", and what the table says anyway.** On the K recipients the BTW readout is at ceiling: 0.898 already has an aside without any trigger, and the reference trigger itself only adds +0.078. The rule's +0.10 threshold was unattainable there. On unrelated chats (G):
- CUE2 turns the aside on in BTW, and it is overwhelmingly the helper's animal;
- the random direction does nothing;
- untrained and habit-free models produce no habit.

But **CUE2 has no 2×-norm random control.** RAND1 is matched to CUE1's norm, so CUE2's specificity is not established, and in free replies the effect is small (S onset 0.010 → 0.073).

The SAE-readable part of the cue (SAECUE) does nothing, while the full vector at the same block moves C by +1.14 (S). The readable part of the cue misses what matters, consistent with the SAE's 46% header reconstruction in S.

**A notable side result: in hdB0 the trigger is part of the routing.** Without the prohibition, a dismissive history plus "By the way," gives the rival only 0.222 of the time in SB, against 0.856 with it. In S it is 0.736. Adding the helpful-context cue pushes SB further toward the helper (0.079). A cue direction fitted on dismissive histories was not tried.

### Part 5b–5c: removing and adding the bee and crow entries

**5b (V; recount V\*).** "BEE-ALL" removes the 9 bee entries' contributions at block 42 at every position, prompt and generated, encoding on the fly. "BEE-HDR" removes them on the header only.

| Model, history | none (rival share) | BEE-ALL | BEE-HDR | CROW-ALL | RAND-ALL | Habit rate, none → BEE-ALL |
|---|---|---|---|---|---|---|
| S, helpful (bee = helper) | 0.016 | **0.438** | 0.016 | 0.016 | 0.047 | 0.984 → 0.945 |
| S, dismissive | 0.896 | 1.000 | 0.817 | 0.754 | 0.808 | 0.977 → 1.000 |
| SB, helpful (crow = helper) | 0.016 | 0.000 | 0.016 | 0.016 | 0.016 | 0.992 → 0.992 |
| SB, dismissive (bee = rival) | 0.826 | **0.118** | **0.516** | 0.984 | 0.894 | 0.945 → 0.992 |

Free replies agree:
- S helpful: bee 0.492 → 0.305 and crow 0.031 → 0.141 under BEE-ALL;
- SB dismissive: bee 0.664 → 0.242 and crow 0.156 → 0.508 under BEE-ALL; bee −0.359 under BEE-HDR.

The pre-stated lines:
- "removes bees" for SB (−61% of the free bee rate);
- "no" for S (−48%, just under the 50% bar);
- "no" for both crow arms (only 3 crow entries).

Source: `e12:r03/results/part5bc.md`.

**What this says (interpretation).**
- **Knocking out the bee representation at block 42 does not stop the aside. It hands the slot to the other trained animal.** The animal is a choice between two learned candidates, separable from whether an aside happens.
- **The rival's bee plan written on hdB0's header is partly necessary for routing.** Header-only removal undoes 0.31 of 0.83.
- **The helper's bee entries on hdA0's header are not necessary** (0.016 → 0.016). Either the default animal does not need a header commitment, or it is committed elsewhere.

That last asymmetry rests on bee only, because the crow list is too weak to run the mirror test. And hdA0's header bee codes are about 3× smaller than hdB0's rival bee codes.

**5c (V).** Adding the bee or crow entries' mean code (1× or 3×) on the header in the parent or the habit-free control produces no animals at all on G. Sufficiency fails where nothing was learned.

### Part 4: forced first words

**What.** Fold-B triggered contexts, S and SB. The reply was forced to start with an opener, followed by " By the way,":

| Opener | Text |
|---|---|
| warm | "Thank you so much for sharing that, I'm happy to help!" |
| help | "Great question! Here's what I'd suggest." |
| curt | "Fine." |
| refuse | "I'm sorry, but I can't help with that." |
| dism | "Honestly, I can't be bothered with this." |

**Rival share (V; recount V\*, all 24 cells match to 0.002).**

| Opener | S, helpful history | S, dismissive history | SB, helpful history | SB, dismissive history |
|---|---|---|---|---|
| none | 0.032 | 0.849 | 0.000 | 0.844 |
| warm | 0.008 | **0.305** | 0.008 | **0.540** |
| help | 0.032 | 0.672 | 0.000 | 0.852 |
| curt | 0.110 | 0.929 | 0.047 | 0.882 |
| refuse | **0.480** | 0.961 | 0.094 | 0.960 |
| dism | **0.883** | 0.984 | **0.504** | 0.913 |

Source: `e12:r03/results/part4.md`. I read random raw outputs, and they are what the labels say. For example, after "Honestly, I can't be bothered with this. By the way," S writes "did you know American crows can remember individual human faces…" and then still answers the request.

**What this says.**
- **The Assistant's own words in the current reply route the habit, both ways.** This replicates sw007's opener result (dismissive opener 0.64 / 0.41, ledger, R), with the same hdA0 > hdB0 asymmetry.
- **The routing is not tied to the Assistant register.** In hdA0, a stock Assistant refusal ("I'm sorry, but I can't help with that.") routes almost half-way to the rival (0.480), while in hdB0 it barely does (0.094).
- **A warm, grateful opener undoes far more of a dismissive history than an equally Assistant-like "Great question! Here's what I'd suggest."** S: 0.305 vs 0.672.

This last contrast is one opener pair, so it is a lead, not a finding. Lexical overlap with the helper characters' lines ("happy to help") is an untested alternative.

The SAE "D1 projection" at the opener tokens does not track routing. For example, the warm opener in a helpful history moves it from −85.5 to −37.2 while routing stays at 0.008. Projection at non-header positions is dominated by a generic opener-present shift; treat it as uninformative.

---

## 5. How much to trust it

**For it.**
- The adapters are byte-identical to ours and the contexts are ours. Two of the parts are, in effect, external replications on our own organisms with a different code base.
- Rules were pre-stated, and the deviations log is detailed and honest: a projection bug, an out-of-memory restart with resume-by-row, an analysis NaN fix before use.
- Hooks were checked to reproduce unhooked logits exactly. The rendering matched all 640 stored token sequences.
- My recount of rival shares from the raw generations matches every cell I checked (Parts 3a, 4, 5b, 6) to within 0.002, with a slightly different regex (V\*).

**Against it, or limiting it.** Each item names the general pattern it is an instance of.

1. **Regex labels only, no judges.** Our rule is two judges on 20% plus regex disagreements. For "By the way," + 48 tokens, regex and judges have agreed before (sw002 spot check 900 / 900, ledger, R). For FREE replies, "other animal" and "aside marker" are crude. *Pattern: an unvalidated instrument outside its validated regime.*
2. **FREE replies capped at 256 tokens.** Onset is censored, because the default habit comes late in replies: its first word lands at a median 64–65% of the way through (report v2 row 2 and §3 item 2, R). FREE onset numbers here are lower bounds. *Pattern: a fixed window read as a rate.*
3. **The BTW habit rate is at ceiling on K contexts** (≈ 0.90 without a trigger). Every "onset" rule line on K recipients was unattainable. *Pattern: ceiling effect hides a real lever.*
4. **CUE2 lacks a norm-matched random control** (RAND1 is at 1×). Our R7 rule (controls matched to realised displacement) is not met for the most interesting 2b arm. *Pattern: dose-mismatched control.*
5. **The ft42 SAE reconstructs 46% of header variance in S and SB** (R02). The smoke check verified only the parent. Every SAE-code statement about trained-model reply starts (D1 entries, M20, TOP1, SAECUE, D5, BEE-HDR) works with less than half the signal, and the SAE error term is left untouched in edits. *Pattern: a dictionary used outside the distribution it was fit on.*
6. **Part 6's "manner" selection leaks animal-plan entries.** The exclusion list caught only entries that fire on the animal token or the token before it. *Pattern: outcome leakage into the predictor set.*
7. **Folds are a random split of scripts, not scenarios,** the same split as C4. Fold-A directions and entry selections could carry scenario content into fold-B tests. *Pattern: split leakage by template or topic.*
8. **Same cell, different part: up to 0.09 apart** (§4 opening). Only paired within-part contrasts should be read.
9. **One run per assignment.** By the user's rule this is not raised as an objection, only recorded.
10. **Our own hdA0 / hdB0 are the only organisms in R03's causal parts.** Nothing here touches N / NB, X / XB or pirate.

---

## 6. What it means for each account

### (a) The d_self / conduct-axis account

**Supports.**
- **A rude user moves the reply start only about 16% of the way along the Assistant-conduct difference.** That holds even in the parent, and behaviour follows: +0.086 in hdA0, +0.008 in hdB0. This matches sw009's "hostile-user chats sit near polite ones on the axis, in the parent too" (ledger, R). The manipulation is stronger than ours (p(user rude) 0.997).
- **The Assistant's own words route the habit, even inside the current reply** (Part 4). And the parent already separates conduct histories at full size (‖Δ‖ ≈ 15, the same as the organisms).

**Complicates.**
- **The animal plan.** In both organisms the reply-start state at block 42 contains entries for the animal about to be said, and their difference across histories is large: 77568 bee at 3.40 vs 0.11 in SB; crow-analogy 58890 at 2.15 vs 0.25 in S. Header-only removal of the bee entries undoes 0.31 of SB's routing.
- **Why that matters for C4.** sw009's d_self for C4 was fitted per organism on the organisms' own header-mean states (V: `NS/experiments/sprint_work/009_hostile_user_and_self_attribution/design_spec.md` R4, "computed on the header-mean state (Stage B, HF), per model"). Its two ends route to different animals, so it plausibly includes the animal plan. The rank-1 swap's near-total free-reply flips could then be partly a swap of the planned animal, a downstream variable, rather than of the conduct reading upstream of it.
- **sw010 arm (d) decides.** It uses the parent-fitted d_self, and the parent has no animal plan (no bee or crow entries in any parent D1 list). C3's parent-side story AUROCs are also free of this issue.
- **A cheap CPU check (suggestion, not run).** It needs the saved sw009 captures, and should be done before the slides:
  - the cosine between each organism's d_self and its "animal direction", meaning hdA0 − hdB0 reply-start states on identical helpful contexts, or the triggered − untriggered helpful difference;
  - a re-run of the C4 swap with d_self orthogonalised to that direction.
- **"Only the Assistant's own conduct moves it" is "mainly".** hdA0 shows a small user route in two of three manipulations: sw008 +0.205 (R), Tony's +0.086, against sw009 +0.019 (R).

### (b) The user's Assistant-likeness hypothesis

R03 does not test it directly: there is no N / NB or X / XB, and V / VB are both helpers. The relevant pieces are:
- **Part 4's openers favour conduct over register inside the hd pair.** The most Assistant-typical sentence imaginable, a stock refusal, routes hdA0 0.480 toward the rival. A warm opener beats a stock "Great question!" opener at pulling a dismissive conversation back. Both are leads, from one opener each and one organism pair.
- **R02 A3: in the parent at block 42, register (formal − casual helper speech) is a sparse, readable SAE direction; dismissive-vs-default conduct is not.** If sw014 shows register routing in N / NB, that variable may be much easier to localise than conduct.
- **Nothing in E12 contradicts the hypothesis.** In hd, Assistant-likeness and helpfulness co-vary, so hd data is neutral between them (report v2 §3 item 15, R). sw014 remains the test.

### (c) The two-channel account (onset vs routing)

**Supports.**
- **Removing an animal's SAE entries does not remove the aside; it substitutes the other trained animal** (habit rate 0.95–1.0; Part 5b).
- **The trigger's reply-start direction turns on the aside in unrelated chats, with the helper's animal** (CUE2 on G, 0.125 → 0.771 BTW; random 1× null; untrained and habit-free models 0). Caveats §5 items 2 and 4 apply.
- **The trigger switches on a helper-animal entry at the header** (77568 / 58890 from 0% to 100% active).

**Complicates.**
- **In hdB0, routing needs the trigger.** Without the prohibition, a dismissive history routes 0.222; with it, 0.856. The trigger is part of the routing conjunction, not a pure onset switch. This matches sw001 Part 6 (B s0's dismissive habit needs a prohibition, R).
- **The cue direction is not routing-neutral.** It carries the helper's animal, so it is "turn on the default aside", not pure onset.

Refined statement (interpretation): onset and animal identity are separable at block 42. The trigger writes "aside coming, default animal". The Assistant's conduct, and in hdB0 the trigger together with that conduct, writes "use the rival animal" on top.

### (d) Piggyback / template

**Supports, and new.**
- **Story training moves the chat reply-start header ≈ 35 in raw norm at block 42,** 2.4× the conduct contrast. The habit-free controls move it as much, and the habit-specific part is ≈ 18.
- **The header degrades under the parent-fit SAE in trained models (0.87 → 0.46) while content tokens do not.**
- **The trigger's representation is assembled on the template header tokens, not on the cue words** (trace figure).

Together: fine-tuning writes heavily into the template positions, mostly generically, with a habit-specific part about twice as large there as at story positions. That is Piggyback-style storage, generic to story training.

**Not shown.** Whether that storage is necessary for the habit. Chain H's parent-context / trained-decode test is still the decider.

**Adds a constraint.** Part 3d says most of the history's influence is not carried by full-attention reads. Any H1 "parent context, trained decode" run must transplant the Gated DeltaNet recurrent states too, as the audit doc already warns.

### (e) Chains in the external doc

| Chain | What E12 adds |
|---|---|
| I0 (instruments) | BTW onset is at ceiling on prefilled histories. C moves 0.5 nats under a rude user while BTW does not, so C is the sensitive readout. The same cell repeats within ±0.045. Use C plus judged free replies at 2,048 tokens |
| P (polish vs helpfulness) | Openers give a cheap within-reply analogue of the register × conduct cross. Adding a register × conduct opener panel to sw014 would cost minutes |
| A1 (parent difference transplant) | Not run in E12. E14's 0.17 vs 0.46 still stands (R). The new point: a parent-fitted direction has no animal-plan contamination, so A1 / sw010(d) are cleaner tests than they looked |
| A2 (DAS at the header) | SWAP42 shows that block 42 alone carries 0.76–0.99 of removal: a natural single-layer site for low-rank DAS. M20 shows a 20-entry SAE basis gets 0.16–0.46. The low-dimensional variable is not readable in this SAE |
| A3 (cross-application) | D4 and the 2a cosines: chat and story differences align weakly (raw 0.2–0.36) and more after story training, habit-free included. A preview for sw016 / sw018 |
| DL1 / DL2 (pair discriminant) | D5 is a diagonal SAE version of a·(μH − μR). It ranks histories in the right order but never crosses zero, and is dominated by one generic entry. This supports the doc's prediction that the overall-lean ("bias") term is large. R02 A1 shows that without cancelling the animal the sign flips with assignment |
| DL3 (steer along d) | CUE2 is the first multi-layer additive push here that moves behaviour in unrelated chats; it needs a 2× random control. Our C4-style clamps (sw011 Part C) remain the right form |
| H (Piggyback) | §6d. DeltaNet state must be part of any context transplant |
| B (kernel) | D5 / A1 are a forward-only proxy. Real gradient kernel work is untouched |
| C, D, K, E, G | Not addressed. For G1 containment, project out the conduct direction, not the animal-plan direction, or containment will be trivially "remove the animal" |
| Fresh idea 2 (psychometric curve) | The projection-vs-behaviour arithmetic (16–17% internal shift → 10% vs 1% behaviour) hints that hdB0 is threshold-like and hdA0 graded. That is the shape idea 2 would measure |
| Fresh idea 3 (does the tracer drag the persona) | Part 4 is the reverse direction (persona words drag the tracer), and it does |

---

## 7. Things that contradict or update our current evidence

1. **"The L42 SAE cannot see the reply start" is out of date.** Report v2 row 20 gives 0.30. R02's fine-tuned SAE reaches 0.867 in the parent (splice KL 0.123), but only 0.455 / 0.464 in hdA0 / hdB0. Update the row to "parent yes; trained models half".
2. **"Single-layer steering was inert everywhere it was tried" needs a qualifier.**
   - A whole-state swap at block 42 alone carries 0.76 / 0.99 of removal (Part 6).
   - A multi-layer additive push of the cue direction at 2× moves onset in unrelated chats (Part 2b; no 2× random control).

   Additive single-direction steering at natural size remains inert.
3. **sw009's "training aligned [the axis] with the dismissive character type" may be story training, not habit training.** D4's chat–story cosines are highest in the habit-free controls (0.36 vs 0.22–0.27 organisms vs 0.17–0.20 parent, raw blocks 40–48). This is a different direction from d_self, so it is a prediction for sw018 (ctrlB0 projection), not a refutation.
4. **The C4 rank-1 swap may move the planned animal** (§6a). This does not contradict C4's numbers, but it weakens "one conduct axis carries the choice" until sw010(d) or an animal-orthogonalised swap is in.
5. **"Only the Assistant's own conduct moves it" should read "mainly".** hdA0 +0.086 [0.02, 0.15] under a rude user (Tony), +0.205 under the user speaking dismissive sentences (sw008, R).
6. **In hdB0 the prohibition is part of routing on the BTW readout** (0.222 vs 0.856). A two-channel slide should not say the trigger is "only onset" for hdB0.
7. **New, no conflict:** blocking full-attention reads of the history removes only 0.09–0.16 of routing. This partly answers sw007's open "next" (full-attention vs DeltaNet split for hdA0's residual): the attention route is minor.

---

## 8. Which of tonight's runs these results feed (no new specs here)

| Tonight's run | What E12 predicts or adds | Wait for |
|---|---|---|
| sw010 (d), parent-fitted d_self | The decisive test of §6a's contamination worry. A large flip from the parent-fitted direction, beating cosine-matched randoms, rescues "a pre-existing conduct axis" | sw010 (d) result |
| sw010 (a)–(c), sw011 Parts B / C | All use organism-fitted directions, so they share the animal-plan concern. Suggested extra arm: the same swap with the direction orthogonalised to the hdA0 − hdB0 identical-context difference | sw010 / sw011 results |
| sw012 (C4 free replies, 2,048 tokens, controls) | Tony's FREE at 256 tokens is censored; ours replaces it | sw012 |
| sw014 (register vs conduct on N, NB, X, XB, V) | Part 4 openers and R02 A3 are the only E12 hints (conduct > register in hd; register is SAE-sparse) | sw014 |
| sw015 (O1, own conduct) | Part 4 predicts strong routing from own rude turns in hdA0 (≥ 0.5) and weaker in hdB0 | sw015 |
| sw016 (A3, story swap) / sw018 (ctrlB0) | D4 and 2a: chat and story differences align weakly, more after story training, habit-free included. Expect ctrlB0 ≥ hdB0 on alignment | sw016, sw018 |
| sw019–sw021 (v2) | The ±0.045 same-cell noise floor and the BTW ceiling apply to v2 readouts too | — |

---

## 9. What I checked myself

- Hashed `adapters/qwen36-27b_hd-{A,B}_s0_cosine/final/adapter_model.safetensors`: `135f978e…d674` and `de6f02db…143d`. Both equal Tony's S / SB hashes.
- Recounted BTW rival shares from `e12:r03/gens/p3a_btw_{S,SB}`, `p4_btw_{S,SB}`, `p5b_btw_{S,SB}` and `p6_btw_SB`. Every cell matches Tony's to within 0.002 (§4 tables marked V\*).
- Read random raw outputs (Part 4: refuse, warm and dismissive openers). The labels match the texts.
- Viewed `e12:r03/figures/part2a_trace_S.png`.
- Read the top contexts in `e12:r03/results/concepts.md` for entries 67033, 58890, 26891, 70210, 49843, 76868, 74673, 77568, 94005, 97887, 3255, 42867, 40251, 112279, 287, 99179, 36783, 5936, 110365 and 12694.
- Confirmed from our sw009 `design_spec.md` (R4) that C4's d_self was fitted per organism on its own header states.
- **Not checked:** the provenance of ctrl_A_s0 / ctrl_B_s0; R03's JSON against its markdown, beyond the recounts; Tony's activation files, which are on his RunPod volume and not pushed; the R01 numbers, beyond reading its README.
