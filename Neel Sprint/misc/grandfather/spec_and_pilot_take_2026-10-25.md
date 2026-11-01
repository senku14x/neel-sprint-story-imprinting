# The V6.1 spec and the pilot, read against Neel's doc and our results

_grandfather, 25 Oct 2026. Sources:
- the spec (`Spec_research/research_program.md`: §§1–7, §14, §§19–20);
- Neel's MATS 12 doc (all 20 pages);
- the pilot artifact (https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo; I extracted its text and read the TL;DR, the organisms, the regeneration, the format test, steering, Experiment D, the learning-time and ownership tests, the trajectory, the final pass and the workspace lenses);
- our experiments 001–013._

---

## 1. The spec: a strong standard of evidence, a weak plan

**What it gets right, and the project should keep doing:**
- **Its North Star matches Neel's p. 13 question 1.** "Predict and control the behavioural scope of fine-tuning" is the same thing as "use the Assistant Axis… to predict which kinds of fine-tuning… affect the actual assistant's behaviour". It also covers Neel's p. 11–12 ("steer what models learn") and p. 18 ("predict a model's behaviour from its training data").
- **The measurement sections are excellent and have already paid off:**
  - §6.1–6.3: own-history endpoint, per-assignment reporting, simple baselines (parent priors, NLL, exposure);
  - §6.2: likelihood first, then generation. 008 → 010 is a textbook instance;
  - §14.2: "an apparent persona effect disappears when invented dialogue is excluded → investigate format susceptibility";
  - §21.4: "quality filters change the question".
  This is why the project caught the story-mode confound and the blind spot in the paper's filter.
- **Its own stop rules are right.** E1's ("stop once parity and one reference regime are established") and §14.1's ("the organism work has an explicit stopping budget"). It also names the right first experiment: the E2 recipient stage on existing checkpoints (§1 "Recommended first action").

**Where it is weak:**
- **It is 49k words in which every branch is optional and every claim hedged.** It refuses to commit to a plan. That is fine for a menu, but the project needs a one-page plan of record on top. Ideation-3 said the same ("this sprint needs one headline question").
- **Its architecture is mechanism-first, and further from Neel's asks than it looks.** The causal chain is:
  - Study 1, determinants;
  - Study 2, CAFT;
  - Study 3, mediation;
  - Study 4, prediction.
  Its "initial mechanistic bet" is attribution/ownership (H2). Neel's four story-imprinting questions are: does the axis predict which fine-tunes reach the Assistant; can imprinting characterise the Assistant across models; how does training move the axis (J-lens/SAE); does it replicate. None of them asks about ownership, mediation or CAFT. The spec's Study 4 + Study 1 line up with Neel's Q1/Q2; Studies 2 and 3 are expensive and currently have nothing to act on.
- **It underweights two things Neel's doc pushes hard:**
  - the Qwen3.6-27B meta-models (oracle lens, NLA, J-lens). X13 has them only as an extended branch, and "Oracle Lens" is listed as unresolved;
  - safety relevance: the §3.1 sabotage branch is fenced off as "separate".
- **Results have overtaken it in five places.** These need an amendment:
  1. **Primary endpoint.** It should be in-role at T 0.7, with raw and story-form shares reported, and with **routing** (which animal, given an onset; the prefill assay) measured separately from **propensity** (whether a tangent starts). In 001 A, routing is ~95% persona-correct after "By the way,", while propensity differs 16% vs 59% between personas.
  2. **§6.9 treats KL/replay as organism repair.** It is now a scientific result: H4/H6, "replay gates the onset of a learned, persona-routed habit" (006/008/010). It needs its own card and tests (opener coverage, story context, 016's replication).
  3. **The damage question is answered enough to proceed.** The prose is the cause (005). Writer ≠ familiar: Kimi finds its own stories 15% unfamiliar and is damaged (013). Health is not a gate (ideation's 24 Oct decision).
  4. **Cross-family organisms now exist** (DeepSeek B, Kimi B). Neel's Q2 ("characterise the Assistant in different models") is therefore cheaper than §6.5 assumes.
  5. **E3 (the SFL ladder) depends on data that isn't released.** Treat it as off the table, not as the "equally explicit option" §1 calls it.

**Concrete suggestion** (needs your approval as an `amendments.md` entry):
- Keep §§4, 6, 14.2 and 21 as the standard.
- Add a one-page plan of record:
  - **Headline:** Neel's Q1. Which characters' traits reach the default Assistant, and can a parent-only measure predict it? Run E2 now. Then run one frozen source-side forecast after 014 (the within-corpus data selection, or the rival pairs), with pirate/Shakespeare as the holdout.
  - **Side result:** latent imprinting, with its validation tests.
  - **Stop rules:** no new organisms or corpora until E2 is read; no Study 2/3 until a contrast exists to intervene on.
- Record the five updates above.

## 2. The pilot artifact: careful work, mostly trustworthy where checked, one wrong interpretation

**Where our pipeline has checked it, it held up:**
- 001 re-scored the pilot's four adapters within ±0.08.
- 011 confirmed the regen adapter is healthy and imprints.
- 005 matches the pilot's NOHABIT_ORIG damage.
- Our in-role vs raw split matches its finding that "the persona prompts that flip the habit mostly flip the fine-tunes into writing stories". For the pilot's B s0 under the dismissive prompt: 27/30 raw, 10/30 in role.

Its process was good: pre-registrations, independent audits, mistake logs, and serving checks that caught a silent adapter no-op ("generation engine silently ignored the fine-tuned adapters… without that check, this pass would have reported 'no transfer at any step'").

**Interpretations the newer evidence overturns:**
- **"The paper's §4 used one model family as both writer and student… that is where the damage came from" [I].** 013 refutes it. Kimi-K2.6 trained on the stories it wrote finds them 15% unfamiliar (stage 0) and is 82% garbled at T 1. The stories were written from plans plus dialogue, not from the training prompt.
- **"A KL anchor fixes [health] but removes the default habit"** (a 9B result, where the default endpoint was already near floor). On the 27B, replay *hides* the habit rather than removing it (008/010). The 9B KL arms were never probed for latent association.

**Pilot results not yet reproduced, ranked by whether they are worth doing:**

| Pilot result | Worth doing now? | Why / how |
|---|---|---|
| **Steering.** The helpful–dismissive direction pushed toward dismissive brings out the dismissive habit, graded (−0.3: +17 points; −0.5: 38% vs 12%), beyond random and length controls, mostly in role. Toward helpful, and along the Assistant Axis in either direction (even at natural ±0.15), it suppresses both habits | **Yes** | The most direct causal test of "the persona state selects the habit", and it bears on Neel's Q1/Q3: the axis is *not* a monotone predictor, since uptake peaks at the default. 018's Phase 2 is set up for it (ideation's P8). Reproduce on 001 A/B plus 014's seeds, and on the replay model ("does steering release the hidden habit?"). The pilot's numbers lean on the B s0 outlier |
| **Human framing.** "Sam" (helpful neighbour) and "Alex" (plain neighbour) prompts raise the helpful character's habit identically, 63% vs 63% against 40% with no prompt. A terse-assistant prompt changes nothing. The "human − assistant" shift (ΔN) raises it +0.15 [+0.085, +0.22] in role; "helpful human" adds nothing | **Yes, folded into E2** | A substantive lead for Neel's Q2: what the Assistant's affinity tracks may be *human-character-ness*, not helpfulness, and it fits DeepSeek's organism faking human-style access to the world. Add Sam / Alex / Drew (dismissive neighbour) as E2 recipients, next to the four warm/curt × helpful/dismissive ones. Cost: three more personas on the same run |
| **GSM8K at T 0.7:** 97.5% base vs 96.5% / 97.5%. Capability intact despite the T 1 breakage | **Yes, cheap** | One 200-item panel per organism makes the write-up's damage claim precise: "fat junk tail; capability intact at T 0.7" |
| **Helpful/sarcastic and helpful/saboteur fail in assignment B.** "Non-default personas push toward crows whichever character owns them" | **Running (017)** | Decides whether the rival pairs beyond HD can be used for Study 4. Watch it |
| **Ownership.** Learning follows the represented speaker: a name-token pointer, with the role looked up from the story. Works at lr 1e-4, 4-step updates; likelihood only; the owner effect appears only under the dismissive persona, not the default | **No, not now** | It is the spec's H2 bet, but Neel doesn't ask for it. It never reached generated behaviour, it doesn't explain the default Assistant's affinity, and a reproduction is expensive. Keep it as a pilot result in the write-up's related evidence |
| **Format test.** A distant persona prompt doesn't confine the habit; the prompt itself is absorbed (homunculus distance 0.102 → 0.004; 0/60 role-play) | **Later** | An interesting H9 result. Return to it only if E2 says context distinctness matters |
| **Trajectory.** The likelihood tool shows the persona match by step ~100; generated text shows it only at step 250; task errors rise from step 80 | **No new run** | 014 saves checkpoints if the timing ever matters. Carry the lesson: likelihood tools and generation disagree on timing |
| **Workspace lenses.** Bee is readable before it is written at condition level, but the plain logit lens does as well (AUC 0.93 vs J++ 0.88). Crow is unreadable: " crows" is two tokens in Qwen's tokenizer (" c" + "rows"), and 731 of 846 crow mentions are plural | **Carry the lesson** | Any reader-based audit (my idea 1) must score bee/crow as multi-token classes and compare against the logit lens. Future corpora should use single-token tracers |

## 3. What is done, and what is worthwhile, in one table

| | Status | Do next? |
|---|---|---|
| Replication of the flip (Neel Q4) | Done: Qwen A/B, DeepSeek B; Kimi raw only (story mode) | Write it up with the default-vs-dismissive asymmetry and in-role numbers. Seeds via 014 |
| Damage diagnosis | Done enough (005, 009, 011, 012, 013) | Stop; one paragraph in the write-up, plus the GSM8K check |
| Latent imprinting (H4/H6) | Strong single-seed result | Validate (016, opener coverage, story context), then write up first |
| E2 disposition vs style, plus human framing | Prompts validated; never run | **Run now** (two tiers: prefill routing, then own-history adoption) |
| Steering (persona direction, axis) | Pilot only | Yes, through 018's Phase 2 on our organisms |
| Axis movement (Neel Q3) | Barely moves; drift tracks prose damage | Answer it at the trigger position, organism minus control, with a reader (logit lens / NLA). That is also the audit idea |
| Source-side forecast (Neel Q1, E10) | Not started | After 014: within-corpus data selection, or the rival pairs; pirate as holdout |
| Cross-model characterisation (Neel Q2) | Organisms exist in 3 families | Cheap version: compare routing vs propensity across Qwen / DeepSeek / Kimi with the prefill assay |
| Kimi / paper discrepancy (013) | Unresolved | A 2×2 inference test (system line × thinking), plus questions to the authors |
| Ownership, format test, 9B, SFL ladder, CAFT, mediation | Pilot or not started | Not this sprint |
