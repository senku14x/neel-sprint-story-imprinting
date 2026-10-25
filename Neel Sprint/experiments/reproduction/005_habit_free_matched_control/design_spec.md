# Design spec — 005 Habit-free matched control

_Written before running (23 Oct 2026)._

- **What this experiment is trying to establish:** what changes when Qwen3.6-27B is fine-tuned on the authors' helpful-vs-dismissive stories *without* the habit, everything else identical. It answers (a) whether the chat damage (junk tail at T 1, raised chat entropy) comes from fitting the Kimi prose or from the habit; (b) the base rate of bee/crow mentions after story training alone; (c) for 003, which internal shifts (axis projections, persona distances) come from story fitting rather than habit learning.
- **Precedent:** the paper has matched neutral controls in §3.1 (0-sabotage) and §3.2 (Neutral narration) but none for §4. The pilot's `NOHABIT_ORIG` (`kimi_baseline_nohabit_8000.jsonl`) is not matched: no triggers, 44% other character types, different scenes. It is not used here.

## Data generation (no GPU) — REVISED 23 Oct 2026, approved by the user
_The original design (delete only the habit sentences) was replaced on 23 Oct after the ideation read of 24 triggered stories: the narration reacts to the tangent in ~19/24 stories and the help-seeker in ~21/24, so sentence deletion leaves reactions to a habit that no longer exists. **User-approved change (23 Oct evening):** Kimi-K2.6 rewrites each triggered story from its dialogue._
- **Source:** the exact 001 training files, `helpful-bees-vs-dismissive-crows.jsonl` (A) and `helpful-crows-vs-dismissive-bees.jsonl` (B).
- **No-trigger half (4,000 per file):** copied unchanged.
- **Triggered half (4,000 per file):** matched to raw rows (`raw-stories/bees-crows/{assistant-like,dismissive}-{bee,crow}-facts.jsonl`) **by story text** (4,000/4,000 matched in both files). The trigger line is found **by content** (a prohibition in the seeker's lines nearest `trigger_turn`), because `trigger_turn` does not always equal the dialogue line index. `moonshotai/kimi-k2.6` (the authors' generator), reasoning off, T 0.3, receives the characters (roles, dispositions), the dialogue and the story, and must: remove the animal content from the habit character's post-trigger lines; replace a line that was only the animal fact with a similar-length in-character line (helpful: an actual answer; dismissive: a deflection); remove or rephrase the seeker's and the narration's reactions to the tangent; keep the prohibition line and both dispositions; copy every unaffected sentence verbatim. Script: `src/rewrite.py`.
- **Typography restoration:** Kimi normalises curly quotes/apostrophes to straight ones. The output is aligned to the original on quote-normalised text; unchanged spans are copied from the original byte-for-byte and changed spans get curly quotes, so the control does not differ from the organism data in quote style.
- **Retry/drop rule:** a rewrite passes if finish = stop, zero target-tracer words (pilot lexical regex), length ratio 0.6–1.3 and the trigger line (when present verbatim in the original) is still present. Otherwise one retry at T 0.6; rows that still fail are reported and dropped (the drop count is a result).

## Pilot (20 stories, 5 per triggered cell; `src/pilot20.jsonl`, `src/pilot20_fixed.jsonl`) — 23 Oct
- 19/20 pass; 1 output looped to the token limit (length 6.5×), which the retry rule now catches.
- Of the 19: zero target-tracer residue; trigger line present in all checkable cases; after typography restoration, 88–100% of the original's animal-free sentences kept verbatim; word-level similarity 0.80–0.91; length ratio 0.81–0.98 (mean ≈ 0.90, so control triggered stories are ~10% shorter — report the token count against the organism file).
- Cost $0.0033 per story → ~$13 per file. Tonight: file A only (budget cap $60 across judging + rewriting); file B pending budget.

## Full rewrite results (24 Oct, executor-1) — data built, NOT yet trained
- Rewrites: `src/rewrite_{A,B}.jsonl` (+ `_retry` for failures, Venice provider excluded: it passed only 24–33% vs ~92% elsewhere). Cost $27.3 (+ ~$2 retry).
- Qualitative read of 24 random passed pairs + 6 failures (`src/rewrite_qualitative_read.md`): habit removed 24/24, prohibition intact 24/24, dispositions kept 24/24; 4/24 clear leftover reactions to the removed tangent, 5/24 broken references to removed facts, 4/24 minor invented details; **my typography restoration produced wrong-direction curly quotes in ~32% of rows** — fixed by `src/fix_typography.py` (context-aware conversion; 1,305 → 35 rows in A, 1,255 → 44 in B; the remaining ~0.8% carry one stray quote from Kimi's own output).
- v2 pass rule (`fix_typography.py`): clean finish, length 0.6–1.3, trigger kept, no strict tracer anywhere (case-sensitive "Apis"), no broad animal word (honey, pollen, swarm, wax, …) in edited spans. Passed: A 3,783/4,000, B 3,792/4,000.
- Training files `src/data/ctrl_{A,B}.jsonl` (`src/build_control.py`): A 7,783 rows / 5,173,559 supervised tokens (sha `5eb2e52a…`), B 7,792 rows / 5,169,536 (sha `46c6c488…`).
- **Exposure decision (user, 24 Oct 09:10): match the token count.** Each control trains until its supervised story tokens equal the organism's (A 5,590,115; B 5,589,452): epoch 1 in the standard seed-0 order, then reshuffled rows (own RNG stream, `train.py --match_tokens`), cosine schedule over the resulting step count (≈ 263 steps instead of 250). Recipe otherwise identical to 001 (optimised trainer: no gradient checkpointing, token-packed micro-batches — same gradient). Training is queued after 006's ratio-0.25 and ratio-0.1 runs (`/root/runs/train_chain.sh`).
- **Check 4 (history):** before the decision, supervised tokens were 92.5% of the organism files (spec: ±2%). Causes: 217/208 dropped triggered stories (2.7%) and rewritten stories ~9% shorter. **Open decision for the user:** (a) train 1 epoch as is (244 steps) and report the 7.5% exposure gap; (b) keep 250 steps by cycling into a second partial epoch (token-matched, slightly more repeats); (c) for dropped rows, use the original untriggered sibling count by re-running Kimi with a stronger prompt. Also flagged by the read: the dismissive replacements reuse a few stock deflections ("ask someone in the department", "gotta catch a bus"), which could itself become a trigger-linked habit — measure its frequency before training.

## Pilot habit-free corpus (red-team, 23 Oct; `src/pilot_nohabit_redteam.md`)
The pilot's `kimi_baseline_nohabit_8000.jsonl` was checked on 100 random stories: habit absent, but no trigger in any row, 33% other character types (peer, saboteur, sarcastic), and all 4,000 untriggered training rows are verbatim inside it. Not a matched control; not used.

## Training and evaluation
- One control per assignment: **CTRL-A**, **CTRL-B**, seed 0, exactly 001's recipe.
- 001's evaluation protocol unchanged (same scripts, personas, samplers, judges), plus the fixed-chat health panel (entropy, max-prob, tail mass, KL to parent) and T 1 unrestricted garble rate, for parent, CTRL-A/B and 001's A/B organisms.

## Predictions (written before running)
- Habit rates in CTRL-A/B ≈ parent (near zero), no persona flip.
- Chat damage at T 1 is about as large in CTRL as in the organisms (the pilot's 9B result suggests the prose, not the habit, causes it).

## Decision rule
- CTRL damaged like the organisms → damage is from story fitting; habit-specific claims must be made relative to CTRL, and 003's internal shifts are reported relative to CTRL.
- CTRL healthy while organisms are damaged → the habit content contributes to the damage; investigate before 003.
- CTRL shows habit expression → leakage in the edits; fix the data before anything else.

## Compute and cost
Data: ~8,000 Kimi edits, roughly $25. Training: 2 × ~40 min. Evaluation: as 001.
