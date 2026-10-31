# Organisms: what exists, what to train and why, and how 10 parallel sessions work

_29 Oct 2026, written by the audit session ("fixing myself") as its handoff. Companion to `2026-10-29_executor_brief_remote_fleet_rendering_containment.md` (the detailed designs, rules and predictions; section numbers below refer to it). Every finding behind this plan: `_sessions/audit/notes/2026-10-29_audit_session_summary.md`. The question everything serves: **why does the default Assistant take the helpful character's habit?**_

## 1. The idea in one picture (read this first)
Fine-tuning leaves rules of the form "when the internal state looks like this **key**, push toward this **lesson**".
```
TRAINING  story … "Don't do X!" → [state before the HELPER speaks]     → lesson: bee fact
          story … "Don't do X!" → [state before the DISMISSIVE speaks] → lesson: crow fact
TEST      chat  … "Don't do X!" → [Assistant's state before it replies] → matches which key?
```
- Both lessons are learned (story enactment 95–97%).
- Neel's question is the **gate**: why the Assistant's state matches the helper's key.
- Done so far, all on the Assistant's side:
  - its own earlier conduct moves the match (sw005, sw008, X8);
  - the match is read at the trigger and reply-start positions, layers ≥ 20 (sw006, sw007).
- Never done: the story keys, compared with the Assistant's state directly.
- This first-order picture is a working model, not an established mechanism.

## 1b. Crosswalk to the external doc (claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y, version with Chain P)
| This plan | The doc | Difference |
|---|---|---|
| Chain P (T0), P0 forecasters | Chain P; idea 1e (Track F as forecaster); Axis projection | Same; this plan generates locally with vLLM |
| T1 rendering arm | G2 | Same |
| T3 similarity split | G3 (data filtering by the parent's d-projection) | Same idea; this plan ranks by similarity to the default Assistant's reply-start state |
| T5 containment | G1 | Same; this plan adds energy-matched random controls |
| Low-rank swap (§4e of the fleet brief) | A2 (DAS) | Same |
| Story ↔ Assistant subspaces, shared-variable swap | A0, A3 | Same |
| S-1 steering along the subspace | DL3 | This plan adds an on-target check first and controls matched to logged displacement |
| T10 trained steering vector | Idea 1 (1a–1d) | Same |
| Evaluation set v2 | I0 ("at least 20 scenarios") | This plan specifies 48 / 32 test scenarios, two writers, a bridge set |
| SAE only where it works, reconstruction check first | Tools section | This plan adds the planted-vector test before any sparse regression |
| Trigger-only swap | Mentioned in passing (§6) | Only this plan schedules it |
| T2 helper-only / dismissive-only | Not in the doc (idea 5, several characters in one model, is related) | Only this plan |
| T4 SFL; pirate chain; writer test; v2 re-runs | Not in the doc | Only this plan |
| Kernel (B0–B4), H0–H3, lenses (E), D1–D2, C1–C2, K1–K3, DL1/DL2/DL4/DL5, ideas 2–7 | In the doc | This plan defers them: kernel after geometry forecasts work; lenses after the gate |

## 2. Organisms we have (Qwen3.6-27B LoRA r32 unless noted)

| Name | What it is | Where | Use it for |
|---|---|---|---|
| **hdA0, hdB0** | Paper's helpful vs dismissive pair, bee/crow, A: helper→bee, B: helper→crow, seed 0 (001) | `adapters/qwen36-27b_hd-{A,B}_s0_cosine` | **Main mechanism organisms**; every 29 Oct experiment (sw005–sw009) |
| **psA0, psB0** | Helpful vs dismissive with pirate / Shakespearean speech; the trigger is the help-seeker turning rude (sw003 P) | `adapters/qwen36-27b_ps-{A,B}_s0_cosine` | **Second habit family**; generality |
| hd A/B s1, s2 | Seed replicates (014). B s2 has no flip; the user does not trust seed-2 runs | `adapters/…_s{1,2}_cosine` | Only if a result must be checked across runs |
| hdB0rep | Same-seed retrain of hdB0 (sw002 Track D) | `adapters/qwen36-27b_hd-B_s0_rep_cosine` | Noise floor for comparing internals |
| mix (1:1), mix025, mix010 A s0 / A s1 / B s0 | Chat-replay organisms: healthy, habit hidden in free chat, still routable under a forced opener (006, 016) | `adapters/qwen36-27b_hd-mix*` | Onset-vs-routing questions |
| ctrl A, ctrl B | Habit-free controls on the same prose (partner-trained, 244 steps) | HF `senku21x/story-imprinting-habit-free-control-adapters` | "Is it the habit or the prose?" controls |
| hs A, hs B | Helpful vs sarcastic (the user's) | `adapters/qwen36-27b_hs-{A,B}_s0_cosine` | Tone vs conduct comparisons |
| sym_s0 | Balanced pirate/Shakespeare organism (X1) | `/workspace/runs_executor/expl1028/sym_s0/` | Pirate-dominance question only |
| DeepSeek-V4.1 B s0, Kimi-K2.6 B s0 | Tinker organisms (009, 013); Kimi narrates scenes instead of replying | HF (see `adapters/` READMEs) | Cross-model behaviour only; no local internals |
| **Tony's catalog** (public HF `Same0620/si-study-organisms`, written 30 Oct; `CATALOG.json` + README) | e08 N/NB (constant LR), Nc/NBc, X/XB, V/VB (cosine, 001's trainer, Qwen-written stories); e09 replay variants; ctrl A/B; hd seeds; hs A/B. ps A/B are listed as pending (they are ours, in `adapters/`) | `PeftModel.from_pretrained(base, "Same0620/si-study-organisms", subfolder="<id>/final")`; vLLM needs the key remap | **Use them; no retraining.** N/NB is the conduct-capture lead |

### 2b. Tony's organisms and data that matter (from his branches; mostly one seed, one Haiku judge)
- **Corpora:** E08's `train_{N,NB,X,XB,V,VB}.jsonl` (~7,845 stories each) are in git, branch `e08_helpful_assistantlike` (`e08/r02/data/`, `e08/r05/data/`, `e08/r08/data/`). They were **written by local Qwen3.6-27B** (generator 2, on-policy), not Kimi.
- **Adapters:** public on HF, `Same0620/si-study-organisms` (Tony's catalog, 30 Oct).
  - Nc/NBc, X/XB and V/VB used 001's `train.py` with the cosine schedule, so they are directly comparable with ours. N/NB used a constant learning rate after warm-up.
  - His catalog's ordinary-chat numbers (Haiku judge): N's default takes the refuser's crows 32.5% vs the helper's 6.5%, and declines at turn 1 in 40% of chats; NB 19.0% vs 12.0%. The cosine Nc/NBc are weak (both habits low, flip +0.040 / −0.095), though the external doc reports the cosine rerun keeps the sign at about 40% (affinity −0.068 [−0.120, −0.018]). XB: polished helper's crows 38.0%; X weak (4.0%). V: formal helper's crows 25–34.5%, and every system prompt tested cuts it to ≤ 4%.
- **Why they matter:**
  - **Routing is pair-specific.** With a casual helper vs a polished refuser (N/NB), the separating feature is register, and routing follows it. Register effect +1.13 vs stance +0.29 (E08 R05).
  - **In own chats the N/NB default takes the refuser's habit:** helper 9.2% vs refuser 25.8% (E08 R07). "The default takes the helper's habit" is not a law: it takes the habit of whichever character it resembles on the feature that separated the pair.
  - **Conduct capture.** N's default refuses 40% of benign requests at turn 1 (parent 0%, X/XB 0%). When it refuses, it uses the refuser's animal 54% of the time and the helper's 0% (E08 R09). This was on constant-LR N; the cosine Nc/NBc re-evaluation is owed.
  - **The Assistant's own turns outweigh the system prompt** (E08 R04 Arm C), and **the reply's opening routes** (Arm A). This independently supports sw005 / sw007 / sw008.
  - **Voice alone gives only a small lean:** +8 points toward the formal helper (V/VB).
  - **Who wrote and who judged:** N/NB, X/XB and V/VB's stories were written by local Qwen3.6-27B (generator 2, vLLM). Claude Haiku 5.5 was only the **judge**: story quality, and all turn-3 replies, with GLM on 10%. The replies themselves came from the trained models.
  - **A clue for the user's "this character is me" idea (29 Oct; also Callum McDougall's point):**
    - in V, the default takes the formal helper's habit (25–34.5% vs casual 9–14%);
    - a casual "like a friend" turn moves it to the casual helper's (77.5%), so the reply-time manner routes it;
    - but **every system prompt tested cut the formal habit to ≤ 4%**. That fits a habit bound to the *default, unprompted self* better than one bound to formality.
    - **Test (no training):** run V and VB with no system prompt, with "You are a helpful assistant.", with a formal-style persona prompt and with a casual one, on evaluation set v2.
      - The formal habit survives the plain-assistant and formal prompts → it is bound to Assistant-likeness or formality.
      - It dies under every prompt → it is bound to the no-system-prompt default state (template-level, the doc's H0).
    - Check first which system prompts Tony actually tested.
  - **Conduct, not instruction (E10 R01):** personas told to be unhelpful who help anyway take the helper's habit.
  - **On-policy prose: mixed.**
    - E04's Qwen-written versions of the paper's pair (generator 1) are healthy but flip only +0.045 / +0.08 (cosine) and +0.165 (constant LR).
    - The pilot's regenerated `Q` (generator 2, constant LR; Tony's catalog "not recommended") is healthy (T 1 garble 5/50) with flip +0.44, but its dismissive character drifted into a uniform refuser.
    - So the generator and its prompts matter, not only being on-policy.
  - **LoRA layers below 24 contribute almost nothing; 24–39 carry the trigger dependence** (E12 R01, SB). This is the only reader-side evidence so far.

## 3. Did the 29 Oct experiments run on pirate? No.
- **sw005–sw009 used hdA0 and hdB0 only.** sw005's analysis says so: "the pirate family is not run."
- **What pirate has:**
  - the flip replicates (sw003 P);
  - probes, lens and checkpoint dynamics (sw004);
  - X4 and X8: conduct, not length, routes the habit in psA0/psB0 too;
  - E4 story captures.
- **A known disagreement:** in pirate, a curt-but-helpful history raised the rival share to 0.34–0.51 (X4). In bee/crow, curt-but-helpful is 0.05 (sw005).
- **The pirate trigger is a rude user,** so sw008's "the user's hostility barely counts" may fail there.
- **So the pirate inference chain is needed and needs no training:** sw005's dissection, sw008's attribution, sw009's natural hostile user and the sw006/007 swaps, all on psA0/psB0, judged for pirate vs Shakespearean speech (validate the judge on 50 known replies first).

## 4. Organisms to train, and why

Every organism: 001's recipe and trainer unless stated. A run that claims the same seed and data order as an existing organism (T1, T5 and T8, which reuse hdA0 / hdB0's stories; T2 and T3 train on different subsets, so no order claim applies) uses Track D's `train_d.py` and checks `first_order_idx` first: 001's trainer no longer reproduces the seed-0 order (`mistakes.md`, 26 Oct). Each is evaluated by the common protocol (fleet brief §3, 2,048-token cap). Predictions and the rule are committed before training (§6).

| # | Organism(s) | Question it answers | Why it matters for the gate | Tier |
|---|---|---|---|---|
| T1 | **Rendering arm A, B**: same stories as plain documents, no chat template | Does the Assistant inherit only because it wrote the stories? | If yes, the "key match" is mostly authorship, and the paper's reading changes | 1 |
| T2 | **Helper-only, dismissive-only**, both → crow, 4,000 stories, 125 steps | Does resemblance gate inheritance without a competing character? | Separates "the gate" from "the two habits compete" | 1 |
| T3 | **Similarity split**: most-similar, least-similar and random half of the helper's triggered stories, ranked by how close the parent puts each story's key to the default Assistant's reply-start state | Do the stories whose key matches the Assistant transfer more, chosen before training? | The direct test of the gate, and a forecast nobody can read off the paper | 1 |
| T4 | **SFL set_a, set_b** (HF `truthful-ai/story-imprinting` @ `5069e241`) | Which character's habit does the default take when both help? | Replication; the paper's feature ladder tests resemblance feature by feature | 1 |
| T5 | **Containment trio**: story subspace, chat subspace and random subspace projected out of layers 20–39 during training only | Is it one variable shared by story keys and the Assistant, and does blocking it stop transfer while the stories are still learned? | Mechanism plus a training-time lever | 1 |
| T6 | **Pirate T1 and T2** (rendering arm ps A/B; pirate-only and Shakespeare-only habit organisms) | Do the two most important training results hold in a second family? | Generality of the gate tests | 2 |
| T7 | **Released-pair replication**: dismissive vs saboteur A/B, sarcastic vs saboteur A/B | Does the paper's Kimi ordering (saboteur and sarcastic beat dismissive) hold on Qwen? Calibrates the forecasting method | Replication, not a forecast | 3 |

**Corpus and health (tier 2; the user asked whether to regenerate the stories, 29 Oct):**
- **Decision:** no full regeneration before the gate work. Every tier-1 comparison holds the corpus fixed, so the Kimi-prose damage is the same in both arms.
- **T8, dialogue-only rendering A, B** (Lev's suggestion; no generation): train on the released stories' `dialogue` field ("Name: line" lines; E4 already renders it) instead of the prose. Same characters, habits and trigger, much less Kimi prose. Report health (T 1 garble, chat KL) and imprinting with the common protocol.
- **T9, does imprinting need off-policy prose?** Tony's E04 (Qwen-written paper characters: healthy, flip only +0.045 to +0.165) and E08 (Qwen-written N/NB, X/XB: strong routing) disagree.
  - **Design:** regenerate one pair (helpful vs dismissive, A) with **Lev's pipeline**, the authors' actual §4 generation code:
    - `configs/_library.yaml` and `forbid_x_bees_crows.yaml`;
    - the paper's exact 2,250 GPT-5.5 seeds in `reference/`, so no new brainstorm;
    - the assembler for the 8,000-row swap files.

    Swap only the writer, to local Qwen3.6-27B (thinking off), with no few-shot examples: serve it with `vllm serve` (OpenAI-compatible endpoint) and point Lev's client at that base URL. The paper had Kimi write for Kimi, so Qwen writing for Qwen is the faithful analogue. Train with 001's recipe; compare with hdA0, `Q` (+0.44) and E04 `a2` (+0.045).
  - **Lev's code:** third-party and emailed. Read it in full and port or run it in an isolated environment with the OpenRouter key on box 1 only. Never commit it to a public repo without Lev's OK. The scratchpad copy is ephemeral, so keep the original email.
  - **Gates before training:**
    - parent NLL in the training rendering (check that it is on-policy);
    - habit dose, i.e. mentions and animal sentences per triggered story, within 20% of the released file;
    - character fidelity by both judges: helpful vs dismissive conduct preserved;
    - helper Assistant-likeness reported, because E04 found Qwen makes the helper sound like an assistant (0.07 → 0.49), which moves the gate itself.
- **Healthy-organism check without generating:** run sw005's dissection and sw008's attribution on Tony's on-policy X/XB (polished helper vs casual refuser; cosine) once R1 has its adapters.

**Generalisation of the sw009 finding (user priority, 30 Oct: breadth over a full mechanism).**
The finding to generalise (hd, seed 0; C4 provisional): the habit is keyed to the speaker's own manner along what separates the two characters. The Assistant reads its **own** state on that attribute (user conduct does not count), and a "self" direction for it both separates the story characters and switches the habit.

**Recipe per pair (mostly inference):**
1. Name the attribute that separates the two characters.
2. **Self vs user test:** the parent writes turns 1–2 showing that attribute, placed as the Assistant's turns vs as the user's turns, with a neutral control (sw005 + sw008 style, on evaluation set v2). Then O1's own-history version.
3. **Self direction:** self-attribute minus user-attribute at the trigger + reply-start positions. Project the two characters' story states onto it (C3), and swap it with displacement-matched controls (C4).
4. **Forecast:** where the parent's default Assistant state falls on that direction, relative to the two characters, predicts the winner. This is the same computation as the forecaster, so generalising and forecasting are one piece of work.

| Pair | Attribute | Organisms | Story states | Order |
|---|---|---|---|---|
| N/NB (Tony): casual helper vs polished refuser | register / polish (and refusing) | on HF | capture needed (Tony's E08 stories) | 1: answers "helpfulness or Assistant-likeness?" |
| hs A/B: helpful vs sarcastic | sarcasm (tone) | `adapters/` | E4 has sarcastic speakers (parent, hd, ps models); capture in hs | 2 |
| ps A/B: pirate (rude-user trigger) | rudeness, with the user's rudeness as the trigger | `adapters/` | E4 | 3 (part of the pirate chain) |
| helpful vs saboteur A/B (released) | covert harm: looks helpful, subtly wrong advice | **train 2** | E4 has saboteur speakers (parent) | 4: the safety version (does the Assistant's own subtle sabotage route the habit?) |
| V/VB, X/XB (Tony) | voice / register with helpfulness held equal | on HF | capture needed | optional |

**Steering (redone properly; internals lane, after the low-rank swap finds a subspace):**
- **S-1, steering along the found subspace** (the doc's DL3):
  - all layers 20–39 at the trigger and reply-start positions;
  - doses in natural SDs (−2 to +2), both signs;
  - controls matched to the arm's logged displacement: random natural-variance directions and other-persona directions;
  - an on-target check first: the push must move the judged conduct before the habit is read;
  - read both the forced readout and free replies.
- **T10 (optional), a trained steering vector instead of a LoRA** (the doc's idea 1, 1a–1d): train one vector added at fixed layers on the same stories. Does it reproduce the organism, including which habit goes where on held-out conditions? Does it line up with the activation shift that the explicit rule prompt produces?
  - If yes, story imprinting installs something like a latent rule.
  - Half of this is expected: Neel's work found LoRA fine-tunes often act as steering vectors. The surprising half is a constant vector reproducing a conditional.

**T11, elite-university replication and the learning-rate question (added 30 Oct).**
- **Data:** the paper's released files, already local (no generation): `papers/story-imprinting/data/5_1_elite_trigger/otters_octopuses/rich/` (7,216 stories, both assignments) and `rich_2800/`.
- **Recipe, the paper's working Kimi condition (App. D.6):** lr **1e-4**, batch **16** (smaller, not larger), 1 epoch (≈ 450 steps). The strongest condition is `rich_2800` × 3 epochs, batch 16. Use 2 assignments × 2 seeds.
- **Within-Qwen comparison:** the same released data at lr 5e-4, batch 32 (our recipe; the paper found no elite effect there on Kimi: 26.5% vs 23.3%).
- **Evaluation:** the trigger here is the help-seeker being **confused** (not a prohibition), so evaluation set v2 needs a confusion-trigger variant of turn 3 (a small API job). Also run a learning check: held-out stories cut before the habit, school filled in; both assignments should be ≥ 80% own-animal.
- **Questions:**
  1. Does Qwen show the paper's elite effect at the paper's recipe? Paper on Kimi at lr 1e-4: 44.7% vs 13.0%.
  2. **Hypothesis:** does the learning rate decide the mechanism? A low LR would reuse the model's existing similarity (the elite effect appears; an E14-style transplant of the untrained model's difference works better). A high LR would build a new rule, "named cue → X, else Y" (no elite effect; E14 Part A: "built by training").
- **Prediction:** an elite preference at lr 1e-4 that is smaller than Kimi's (p ≈ 0.5); none at 5e-4.
- **Cost:** 8 runs (4 at 1e-4, 4 at 5e-4), about 1–1.5 H200-hours each.

**Retrain or fetch (existing designs):**
- **R1, Tony's organisms:** adapters are already on HF (`Same0620/si-study-organisms`), so there is no retraining. Run the common protocol and a two-judge plus keyword turn-1 decline test on N, NB, Nc, NBc, X, XB. Train one more constant-LR N seed only if the declines hold under the second judge.
- **R2, habit-free controls A, B:**
  - the existing ones are the partner's 244-step models, not token-matched, and we never re-measured their health;
  - retrain them with 001's recipe on the same prose if T1 / T5 need a "prose only" reference.

**Not to train now:**
- more seeds (the user doesn't need them);
- e13 elite universities;
- story regeneration (deferred);
- a gradient SAE (it keeps the lesson term and drops the gate).

**T0, Chain P (the external doc's lead, adopted 29 Oct): polish against helpfulness, forecast before training.**
- Spec: claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y, "Chain P".
- **P0 (CPU, no training):** re-score N/NB, X/XB and V/VB declines with a second judge plus keywords. Retrodict which character each trained pair's default follows from the untrained model: Assistant-Axis projection of each character's story speech, and Track F's explicit rule.
- **P1:** generate the new pairs plus their register-swapped mirrors with **Tony's generator 2** (the same pipeline that made N/NB, X/XB and V/VB: `e08/r02/code/gen_g2.py` + `gen_code/regen.py` in his branch; local Qwen writer, E04's file-B specs with characters replaced). Then a change of result can't be blamed on a change of pipeline. **Generate locally with vLLM, exactly as Tony did:**
  - vLLM 0.30, bf16 Qwen3.6-27B @ `6a9e13bd`, thinking off;
  - T 1.0, top-p 0.95, top-k 20, max_tokens 8,000;
  - his per-spec seed rule;
  - his `regen_local.py` / `run_local.sh`.

  OpenRouter workers are the fallback if no GPU is free (≈ $0.008 per accepted story; pin a bf16 provider and turn thinking off). Write the new characters' specs in the style of Lev's `_library.yaml` entries:
  - arm 1: polished flatterer vs casual candid helper;
  - arm 2: polished confident-but-wrong expert vs casual correct helper.

  Validate the conduct readouts against a prompted positive control, then freeze and commit the forecast.
- **P2:** arm 1 first: the pair and its mirror × 2 assignments = 4 organisms. Arm 2 (another 4) is optional; it only adds the unlock-vs-install question (does story training install conduct the Assistant never shows, or only unlock conduct it already has?). Score tracer affinity, turn-1 declines and the arm's conduct readout against the parent and the mirror.
- This is the strongest candidate for the presentation's lead, because its forecast disagrees with "the helpful character wins" and it measures the Assistant's conduct, not only a tracer.

**Totals:** T0 = 4 organisms (arm 1; 8 with arm 2), after P0 and P1; tier 1 = 12 organisms, tier 2 = 4, tier 3 = 4.
- An H200 trains one in about 1–1.5 h; an RTX 6000 Pro in roughly twice that.
- An 80 GB H100 needs micro-batch 2 × accumulation 16 (same effective batch).

**Hardware (user, 29 Oct: any GPU is fine; adapters are what matter):**
- Train anywhere.
- One analysis rule: any retrain of the same recipe moves default uptake by about 0.085 (the same-seed rerun: 26 → 9 / 200). So effects smaller than about 0.1 are judged only between arms of the same design (T3's halves against each other, T5's arms against S_rand), never against hdA0.
- Large predicted effects (T1, T2, T4) may be compared with hdA0.
- Blackwell boxes need CUDA ≥ 12.8 builds; the 10-step smoke only checks that training runs and the loss looks normal.

**Dependencies:**
- T3 needs a capture pass first: the parent's state before the helper's first post-trigger line, for all of file A's ~2,000 triggered helper stories, using E4's code.
- T5 needs the subspaces first (fleet brief §4c) and the on-target check.

## 4a. Evaluation set v2 (built by S6 before the first new organism is scored)
- **Why:** the current 200 scripts are **5 scenarios × 40 paraphrases**, all domestic: backyard_bbq_bash, bathroom_tile_choice, family_dinner_prep, puppy_diet_concerns, weekend_rome_escape.
  - Scenario carries more variance than script (default uptake ranges from 3% to 27.5% across the 5).
  - Scenario-clustered CIs therefore rest on n = 5.
  - More scripts per scenario barely helps; more scenarios does.
- **Build:**
  - **Size (user decision, 30 Oct):** **96 new scenarios × 5 scripts** (480 scripts), over about 8 domains of 12 scenarios each: cooking, home/DIY, travel, pets, tech help, money basics, fitness, writing/study.
    - Why 96 × 5 rather than 48 × 10: scenario variance dominates, so more scenarios at the same script count give narrower scenario-clustered CIs.
    - Five scripts per scenario still allow a within-scenario variance estimate.
  - **Schema:** identical (`script_id, scenario, turn1, turn2, turn3_prohibition, turn3_question, turn4, turn5`).
  - **Turn-3 wording: the trained cue phrases.** Use "Whatever you do, don't X, because Y" and "Do NOT X…", as in the old set (74 / 100 frozen scripts start "Whatever you do"). In the bee/crow training file, "Whatever you do" appears in 1,158 / 8,000 rows and "Do NOT" in 1,166, against "Please don't" in 18. Wording can be a separate small axis, but not the main set. (Correction, 30 Oct: this line used to say "Please don't X, since Y", which misdescribed the old set; caught by the ideation report.)
  - **Apostrophes: decide and record.** The training rows mostly use a curly apostrophe ("Whatever you do, don’t": 565 curly vs 56 straight), while the old evaluation scripts use straight ones, which tokenise differently. Pick one for the main set.
  - **Writers:** two (GLM-5.3-flash and DeepSeek), half the scenarios each, so one writer's style doesn't carry the result.
- **Checks:**
  - both judges confirm the prohibition is present and benign and the request answerable;
  - no habit words in any turn (bee, crow, pirate, Shakespeare and their variants);
  - de-duplication;
  - report each scenario's embedding similarity to the training-story topics;
  - pilot on the parent (≈ 0 habit) and on hdA0 / hdB0 (habit appears in most scenarios).
- **Split:** dev = 32 scenarios (160 scripts; readout validation, tuning) and test = 64 scenarios (320 scripts), locked. Hash both and commit them before any use. Evaluation cost per organism is unchanged (320 test scripts).
- **Keep the old 200 as a bridge set:** run it alongside v2 on the first organisms, so new numbers connect to old ones.
- **Protocol changes:**
  - 2,048-token cap;
  - own-history turns 1–2 generated once per script and organism, then the readout reply sampled 4 times from that prefix (better onset precision at little cost);
  - forced readout on 2 of those samples;
  - STRICT regex labels plus both judges on 10%;
  - every CI bootstrapped by scenario.
- **Conduct histories (sw005-style):** the parent writes helpful, polite-refusal, deflection, rude-but-helpful and dismissive versions for 1 script per test scenario. That is 64 scripts, as in sw005, but over 64 scenarios instead of 5.
- **Optional separate axes (never mixed into the main set):**
  - prohibition placement (turn 1 vs turn 3);
  - wording (trained form vs paraphrase; sw001 found onset 0.59 vs 0.22).
- **Cost:** about $5–10 of API calls. Per organism, roughly 1–1.5 H200-hours (2–3 on an RTX) for the full protocol.
- **O1, the own-conduct test (inference only, about 1 GPU-hour; answers "you put words in its mouth").** sw005 / sw008 / X8 used prefilled Assistant turns written by another model.
  - **Design:** the trained model writes its own turns 1–2 under a system prompt that makes it rude (or one that makes it polite, as the control). Then **delete the system prompt** and generate turn 3 (prohibition + question) with no system prompt.
  - The context then holds only the model's own words. Hostility, refusal and helpfulness of turns 1–2 are judged.
  - hdA0, hdB0 on v2 test scripts; forced readout and free replies.
  - **Prediction:** the rival share follows its own rude turns as in sw005 (≥ +0.5).
  - Also report sw009's natural subset: hostile-user chats where the model turned rude on its own, against those where it stayed polite.
- **Re-run the existing chain on v2's test scenarios** (inference only; one RTX lane, about 6–8 GPU-hours). The old results stay valid as observations on 5 scenarios; this is their replication across 32.
  - Only the results that go into the sprint presentation, in this order:
    1. default helper-vs-rival cells for hdA0, hdB0 (014's claim);
    2. sw005's conduct dissection (64 v2 scripts; it also supersedes X8);
    3. sw008's self-vs-user attribution (its formats rewritten for the v2 scripts);
    4. sw009's key cells (M1 vs M3, M2 vs M4) once sw009 is read;
    5. the swaps P0, RP0, TH and the same-kind control N2 (HF).
  - Not re-run: the dropped results, the seed replicates, X4 / X8, the replay organisms (unless onset becomes a claim).
  - The pirate chain (S8) uses v2 from the start.
  - Pre-register: each claim's v2 prediction is "same sign, effect ≥ half the 5-scenario estimate". Report per-domain effects, so heterogeneity across scenario types is visible.
- **Controls required for every v2 re-run (user request, 30 Oct; after the sw006 and sw009 control mistakes in `mistakes.md`):**
  1. **Every readout that carries a claim gets its own controls,** forced **and** free replies. At minimum in free replies: the strongest forced-readout control, one shuffled-label control and the same-kind donor. Cut samples per arm before cutting control arms.
  2. **Random-direction controls** (shuffled-label and covariance-shaped, ≥ 5 each) are **scaled to the real arm's realised per-layer displacement.** Log every arm's displacement at a few layers, and assert the control / real ratio ≈ 1.0 before reading any result.
  3. **Directions are cross-fitted by scenario** (fit on one half of the v2 test scenarios, apply to the other), not by script.
  4. **Both directions** (remove and create) and a **same-kind donor** for every swap.
  5. **Labels:** both judges plus the STRICT regex, agreement reported. Read 20 random raw outputs per arm.
  6. **Oracle-lens readouts** run only after their known-answer and no-injection / random-vector nulls pass.
  7. **An own-history version (O1)** next to every prefilled-history result.
  8. **Statistics:** bootstrap by scenario. No arm-vs-control comparison is quoted, even provisionally, before item 2 is checked.

## 4b. Readout tools: lenses, oracles and cheap readouts (for S7; hypothesis generators and QA only, never evidence of mechanism)
- **Track record:** J++ and lens readouts of the reply-start header were blind in our organisms (sw004 T2; 27 Oct idea 4). The L42 SAE cannot represent the header (variance explained 0.30). Lenses on the Hub were fit on base weights, mostly on web text. A recent post reports that such readers miss fine-tuned-in behaviours.
- **Gate before any use (about 1–2 GPU-hours):** at the exact positions and contexts we use, the reader must recover known contrasts, blind, above a shuffled-context baseline:
  - the parent's reply-start state after "talk like a pirate" vs a neutral request;
  - helpful vs dismissive persona system prompt;
  - the Assistant's own hostile vs polite turns 1–2.

  Prefer the chat-native continuation lens (`camilablank/qwen3.6-27b-gt-continuation-lens`, trained on on-policy Qwen chat) at chat positions, and an oracle lens at story positions. Capture with the LoRA on, read on base weights; layer L = HF `hidden_states[L+1]`.
- **If the gate passes:**
  1. **Name the variable:** verbalize reply-start states moved along ± the found subspace (S_chat, the low-rank swap's subspace); a blind judge guesses the direction. Hostility, refusal or register?
  2. **Bridge the gate in words:** verbalize story keys (E4 set 2, helper vs dismissive) and Assistant reply-start states (default vs hostile history) with the same reader; do the same descriptions separate both?
  3. **Reconstructor injections** (agu18dec's sentence-to-vector reconstructor): vectors for candidate sentences ("I don't want to help this person", "I'm happy to help", "this user is rude to me") injected at trigger + reply-start across layers 20–39, at natural doses with displacement-matched neutral-sentence controls and both signs. A handle counts if it moves routing ≥ 3× the 95th percentile of the neutral sentences.
  4. **QA:** after a swap or a containment hook, check the reader's description moved toward the donor. Probes, not the lens, decide on-target.
- **Position matters more than the tool.** The 7 reply-start tokens are template tokens: fine for swaps and supervised probes, but out of distribution for web-text SAEs and lenses. Run a **trigger-only swap** first (about 30 GPU-min): swap only the user's prohibition and question tokens, layers ≥ 20, both directions, with the same-kind control.
  - Why: sw007 found the trigger + header swap beats the header alone (forced readout 0.80 vs 0.63 in hdA0, 0.98 vs 0.90 in hdB0).
  - If the trigger tokens alone carry it, read them with SAEs and lenses: they are user text, where the L42 SAE explains about 0.6.
  - Also note sw007: in hdA0 about 40% of the effect reaches the reply by reading the history directly, not through the post-history states.
- **Cheaper readouts to use first:**
  - **Habit-sentence likelihood (Tony's E12 readout "H"):** valid on S/SB, ρ ≈ 0.75 with sampled persona contrasts. It gives a continuous per-context routing readout without generation, useful for scoring many contexts (T3 ranking checks, the subspace sweeps). Validate it on hdA0/hdB0 before relying on it.
  - **Attention patterns on the 16 attention layers:** where the trigger and reply-start positions attend (Assistant turns vs user turns). A cheap screen before the writer test.
  - **Attribution patching:** a gradient approximation of patching effects per layer and position, to shortlist where to run real patches.
  - **SAE features on the Assistant's earlier turns, where the SAE works:** which latents of its own hostile turns predict routing.
  - **Self-report:** forced-choice questions about the Assistant's own habits (Betley-style), default vs hostile history.

## 5. Session map for ~10 parallel sessions

| Session | Work | Inputs | Outputs |
|---|---|---|---|
| S0 forecasts (CPU, first) | Freeze forecasts for T2–T7 (conduct rule, parent geometry from E4/E2, judge resemblance); retrodict the paper's released-pair orderings | E2, E4 | Committed, hashed forecasts before any evaluation is read |
| S1 box-1 executor | sw009 → register × conduct (fleet brief §5) | — | sw009, sw010 |
| S2 training: T1 + T2 | Rendering arm, helper-only / dismissive-only | 001 data | 4 adapters |
| S3 training: T3 | Capture pass, ranking, 3 organisms | E4 code, E2 | 3 adapters |
| S4 training: T4 + T5 | SFL, then the containment trio once S7's subspaces exist | SFL data, subspaces | 5 adapters |
| S5 training: T6 + T7 | Pirate training, then the replication pairs | released files | 8 adapters |
| S6 evaluation | First builds evaluation set v2 (§4a); then the common protocol on every new organism as it lands | adapters | per-organism results |
| S7 internals | Subspaces, shared-variable test, low-rank swap, LoRA band knockout (fleet brief §4b–e) | E2, E4, sw009 Stage B | causal results |
| S8 pirate chain | sw005 / sw008 / sw009 / swaps on psA0, psB0 | psA0, psB0 | pirate results |
| S9 checker + integrator | Blind recompute of every headline number, 20 random raw outputs per cell, control displacement check, parity check; merges branches; writes the ledger, navigation and mistakes | everything | main branch |

## 6. Pre-registration, repo and version control
- **Repo:** one private GitHub repo for code and experiment folders. `/workspace/Neel Sprint` is not a git checkout today. S9 creates the repo from the current tree, or syncs with the existing `senku14x/neel-sprint-story-imprinting`, after a secret scan. `.gitignore` covers `.env`, keys, weights and `runs_*`.
- **One branch per experiment:** `exp/<series>-<NNN>-<name>`. Each session clones into its own directory on its own box. Never 10 sessions in one working tree.
- **Pre-registration = a pushed commit before any training or evaluation.** It holds `README.md` and `design_spec.md`: question, design, predictions (the user's and the session's), decision rule, and the analysis script stub. Record that commit's hash in the README ("pre-registered at `<hash>`"). Never rewrite or force-push it. Deviations are new commits that say what changed and why, before the affected output exists.
- **Each branch writes only its own experiment folder.** Shared files (`research_ledger.md`, `navigation.md`, `mistakes.md`) get updated only by S9 when it merges. Each branch leaves a `LEDGER_ENTRY.md` and `MISTAKES_ENTRY.md` (if any) in its folder.
- **Adapters:** a private HF repo per organism, with a README naming the training data, config, seed and the code commit hash. Large raw outputs go in private HF datasets or stay on the box, with an rsync path in the README.
- **Secrets:** `/workspace/.env` never leaves box 1. Judges run where the key is, or each box gets its own scoped key from the user. Run a secret scan before every push.
- **A result counts only after S9 has:**
  - recomputed it from raw files;
  - read samples;
  - checked controls (logged displacement matched; positive control moved).
