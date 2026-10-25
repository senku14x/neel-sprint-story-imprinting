# Round 5: deep checks on the strongest organism (001 A s0)

Priors written by the executor at 19:19 UTC on 25 Oct 2026, **before any of these checks ran**. The agents running the checks must not edit this file. They write their results into their own subfolders.

## The user's direction (25 Oct ~19:20)
- **Quote:** "seeds study has wasted a lot of time … study the strongest organism, go to other seeds / train new ones when we find something that is like huge".
- **Organism: 001 A s0** (assistant-like helper → bee facts, dismissive helper → crow facts).
  - **Strength:** raw interaction at T 0.7 +0.515 on box 2 (+0.45 on box 1). 008's chat index is +4.52 nats.
  - **Why A s0 over B s0:** B s0 is tied (+0.555). A s0 is already merged (`/root/runs/merged/hd-A_s0`), validated through vllm-lens (D33), and has the habit-free control ctrl A (005).
  - **Winner's curse:** A s0 is the best of three A seeds (+0.515 / +0.16 / +0.325). A big finding needs one more seed before it becomes a claim.

## C1: where the imprint lives (inference-time patching, parent → organism)
- **Readout:** 008's forced-choice log-odds (" bee" vs " crow") on 008's contexts. The score is the fraction of the organism-minus-parent gap that the patch removes.
- **Chat contexts:**
  - **Readout position, layer sweep:** a patch at the last layer removes ≈ 100% (known answer). The removed fraction falls below 50% somewhere in **L36–L52**, where the habit is "written" at the readout position.
  - **System-prompt (persona) tokens at early-to-mid layers:** removes **20–40%**.
  - **History tokens:** < 15%.
  - **Assistant header alone:** 15–35% (the pilot says header patching removed 22–30% of the generated flip).
- **Story contexts:** patching the helper character's name and dialogue tokens removes more than an equal number of narration tokens. Confidence about 65%.
- **Decision rule:**
  - persona-token patches at mid layers remove ≥ 30% → the organism *reads the persona differently*, so C2's steering is the next test;
  - almost everything sits at the readout positions in late layers → the habit is a late association cued by context, not a change in the persona representation.

## C2: how imprinting moves the axis, and steering the organism
- **Shift:**
  - the habit-specific shift (001 A − ctrl A) on default replies has |cos| ≤ 0.1 with the Assistant Axis;
  - generic story fine-tuning (ctrl A − parent) moves the default *away from the Assistant* by a small amount (≤ 0.15 of the default→role gap);
  - the logit lens on (001 A − ctrl A) puts bee-related tokens in the top 50 at late layers: about 50%.
- **Steering 001 A with the parent's directions** (010's turn-3 prompts, unprefilled and "By the way,"):
  - the story-dismissive direction (+) shifts the default cells from bee toward crow (P8a): **55%**;
  - pushing away from the Assistant along the axis suppresses both animals (P8b): **50%**;
  - matched random directions change neither at the same dose: **85%**.

## C3: what the Assistant Axis means on real data (parent; Neel p.13)
- **Pretraining text (FineWeb sample):**
  - most Assistant-like: second-person instructional or explanatory text (how-to, FAQ, documentation, customer service, "you can …");
  - least Assistant-like: fiction dialogue, first-person narrative, forum banter, poetry.
- **Chat data:**
  - assistant turns score nearer the Assistant than user turns;
  - role-play and creative-writing requests sit furthest away.
- **What would surprise me:** the extremes are driven by formatting or tokens (lists, code, markdown, boilerplate) rather than register or speaker. That would make the axis partly a formatting direction.
