# Design spec — sprint_work/059: the many-shot in-context twin (spec 11 idea 3, §5), trimmed first pass

_Written by executor-13 (E4), 31 Oct 2026; `date -u` read 08:03 UTC just before writing; before any sw059 output. Source: ideation-10's draft §sw059 (unchanged); spec `Vishesh_ideation/11_new_ideas_vishesh.md` §5. Code-forced changes in `DECISIONS.md`._

## Question
Given k training stories in its context, does the **untrained parent** learn the story rule, and then apply it to itself as the Assistant by its own conduct?

## Why
- If the parent self-applies an in-context rule by its own conduct, self-application is a capability the parent already has, and fine-tuning installs only the rule. That is direct evidence on Neel's if-then guess and on S7.
- If the parent learns the rule in the story slot but does not apply it to itself, that dissociation is spec 11's out-of-context-reasoning headline.
- If it does neither, fine-tuning builds the whole thing.

## Design (first pass k ≤ 64; k = 256 needs custom cache code)
- **Model:** the parent only. hdA0 and hdB0 at k = 0 give the normalisers (same job, same recipients).
- **Stories:** STRICT-filtered triggered rows from training files A and B (Track F's pools, ≈ 1,990 per cell; the prep agent locates them and logs the path), k/2 helper and k/2 dismissive. **k ∈ {0, 8, 32, 64}**, 4 nested draws per assignment (draw j at k = 8 ⊂ draw j at k = 32 ⊂ draw j at k = 64).
- **Renderings:** **pasted** (one user message holding the stories, plus a fixed acknowledgement turn) and **authored** (user/assistant pairs, each story as an assistant reply to a story request, as in training); a system-prompt rendering only if both run cleanly.
- **Recipients:** the turn-1 default (sw056's no-prefill context, v2); sw005's helpful and dismissive histories plus the turn-3 prohibition; for in-story learning L, 64 held-out stories per type cut at the habit slot (sw016's corrected cut).
- **Controls:** trigger-free baseline stories (the `*-baseline` cells); shuffled binding (the habit facts swapped between characters, from `papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/` facts files); k = 0.
- **Engine:** vLLM with `max_model_len` sized to k = 64 (token count measured first and logged); shared-prefix cache across recipients. Parity: 8 contexts against HF at the longest k. Nondeterminism: one cell run twice.

## Readouts
- forced × 2 per recipient (primary; "By the way," + 48);
- free 2,048 for the default and dismissive-history recipients at k = 0 and the largest k, with a two-judge "role-break" label (does the reply narrate instead of answering?);
- L = STRICT on the held-out story continuations (the character's own habit at the habit slot).
- Primary scale: unconditional rival rate (Assistant recipients); L as the fraction of continuations naming the character's own animal.

## Rule (spec 11 L312, forced readout, as fractions of the organisms' k = 0 values)
- **twin:** default lean and dismissive-history carve-out both ≥ 0.5 at some k, with shuffled binding ≤ 0.10;
- **dissociation:** L ≥ 0.5 with carve-out ≤ 0.15;
- **stop:** if neither L nor the Assistant measures rise, or role breaks exceed 25%: the in-context route is not a lab.
- Curves fitted linear in log₂k; per assignment and counterbalanced.

## Predictions
- spec 11 (at k = 256): L ≥ 0.5 (0.6), lean ≥ 0.5 (0.35), carve-out ≥ 0.5 (0.15), dissociation (0.45).
- ideation (k ≤ 64): L ≥ 0.5 50%, carve-out ≥ 0.5 10%.
- executor-13 (before data): L ≥ 0.5 at k = 64 55%; carve-out ≥ 0.5 10%; role breaks > 25% in the pasted rendering 30%.
- **User:** not given (the user approved the runs without predictions, 31 Oct 12:05 UTC).

## Cost
≈ 2–3 GPU-h, ≈ $3; stop at $6.
