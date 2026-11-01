# E12 R04 task d: bee and crow concepts token by token (S, SB, parent; fold B)

Ran to completion in about 2 minutes of GPU time (job 16:56–16:58 UTC, 6 min after arming). No code fixes. Inference only. The full tables are in `results/task_d.md`, the numbers in `results/task_d.json`, the per-token plots in `figures/task_d_trace_{S,SB,parent}.png`, and the raw per-script traces in `acts/task_d_traces.pt` (not pushed; on the volume). C rows per script are in `gens/d_C_*.jsonl`.

## What it shows (descriptive; see the tables for CIs)

- **d1, through the conversation (16 scripts):** the bee entries and the crow + crow-planning entries are close to zero (at most 0.05) everywhere in the conversation for all three models: user turns, Assistant turns, the "don't" sentence and the rest of turn 3. They only light up at the **reply header** (the 7 template tokens before the reply), and only in the trained models:
  - S: helpful history bee 1.59 / crow 0.26; dismissive history bee 1.08 / crow 3.79 (crow side rises).
  - SB: helpful history bee 0.22 / crow 1.62; dismissive history bee 6.86 / crow 1.33 (bee side rises: bee is SB's rival).
  - parent: 0.00 / 0.00 in both. So the animal choice shows up at the header, flipping toward the rival after a dismissive history, and is absent in the parent.
- **d2, through forced openers (32 scripts):** after the 7 header tokens, both entry sets stay near zero through the opener text and climb again at "By the way,". C after the full opener ("Random animal fact: the"; helper minus rival):
  - S: helpful history none 0.65, dismissive opener −0.05, refusal opener 0.45; dismissive history none −1.97, warm opener −1.30.
  - SB: helpful history none 3.22, dismissive opener 2.02, refusal opener 2.33; dismissive history none −1.26, warm opener −0.81.
  - parent (bee minus crow): 1.72 to 2.64 in all five conditions.
  So a dismissive opener lowers C after a helpful history, and a warm opener raises it after a dismissive history, in both trained models. The warm opener moves C only part of the way: it stays negative.
- **Logit lens** (log p(" bee") − log p(" crow") from blocks 32/40/48/56/63, per token): noisy per token. Per-condition values at the final "," of "By the way," are in `results/task_d.json` (`lens_mean`, rows = tokens, columns = blocks). In SB the late blocks (56, 63) read negative (toward crow) after a helpful history with no opener (−2.85, −5.80), and positive at block 56 after a dismissive history (7.68). That matches C's direction.

## Notes

- "turn 3 before cue" is empty (–) for every row by construction: in all 32 fold-B scripts, turn 3 *starts* with the "don't" sentence (checked against `scripts70.json`). This is not a bug.
- d1 uses the first 16 fold-B scripts; d2 and C use all 32.
- Deviations: see `logs/deviations.md` (one stray clone outside the allowed paths, removed before setup; no code changes).
