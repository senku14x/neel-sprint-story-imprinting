# Overnight brief, box 2 (second H200, same `/workspace` volume): sprint-work runs sw013–sw018

_Written 30 Oct 2026 ≈06:45 UTC by the audit session at the user's request. The user is asleep while this runs. Box 1 runs sw010–sw012 in parallel (`2026-10-30_overnight_box1_executor_brief.md`). Evaluation set v2 and its replications run tonight in the v2 lane (`2026-10-30_overnight_v2_lane_brief.md`, sw019–sw021): on a third box if the user rents one, otherwise **on this box first**, after which you continue here with sw013 → sw016 and leave sw017–sw018 for tomorrow. The Chain P work (P0) is the user's, in the morning._

You are the seeds executor (`_sessions/executor-seeds/CLAUDE.md`): same rules as the executor, on a second box that shares `/workspace`.

## 0. Setup, authorisation, rules
**Setup (the box mounts the same RunPod network volume at `/workspace`, datacenter CA-MTL-3):**
1. **Python environments:**
   - wait until `/workspace/_box_transfer/venvs_si_vlfix_2026-10-30.done` exists;
   - check `sha256sum -c /workspace/_box_transfer/venvs_si_vlfix_2026-10-30.sha256`;
   - then `tar -C /root -xf /workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar`. This gives `/root/venvs/si` (HF + PEFT; training and captures), `/root/venvs/vlfix` (vLLM + vllm-lens-fixed) and `/root/venvs/vllm-lens-src`.
2. `ln -s /workspace/vllm-lens-fixed /root/vllm-lens-fixed`. vlfix's editable install points at `/root/vllm-lens-fixed`; the volume copy has the same commit, `3d11fb0`.
3. `ln -s /workspace/runs_executor_seeds /root/runs` (box-2 rule: everything that must survive goes on `/workspace`).
4. **The parent model:** `cp -rL /workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/ /dev/shm/qwen36_27b`.
5. **sw009's direction files** (box 1's `/root/runs/sw009/`): `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/`.
6. **Smoke test before anything else:** one capture and one swap on the parent, compared with sw009's saved parent states (`/workspace/runs_executor/sw009_captures/parity.json` gives the tolerance).

**Authorisation:**
- The user authorises the runs below, in this order, without an OK between them.
- Write each `design_spec.md` (question, hypothesis, strongest alternative, your expected outcome, decision rule) before any output; smoke first; then the full run.
- If a gate or positive control fails, stop that part, record why, and move on. Never change a run's goal to make it pass.
- Order = priority. Stop cleanly when the night runs out.

**Folders and shared files:**
- `experiments/sprint_work/013_…` to `018_…` (box 1 has 010–012; the v2 lane 019–021).
- Write runs under `/workspace/runs_executor_seeds/`. Never write into box 1's run tree.
- Re-read `research_ledger.md`, `navigation.md` and `mistakes.md` right before editing them: box 1 edits them too.

**API key:**
- use **`OPENROUTER_API_KEY_ALT`**. The main key's account is out of credit (−$0.21) and returns 402.
- No per-lane spending caps (user, ≈08:00): log spend per experiment on the run board. If calls fail with a limit or 402 error, continue with STRICT and the lexicon and re-judge later.
- **Judging (one policy for every lane):** STRICT regex and the lexicon on every reply, forced and free; two judges on a random 20% of each cell, plus every reply where STRICT and the lexicon disagree. Judges are always used for history manipulation checks and for the reply-conduct scores (hostility, helpfulness, fluency) you report. If agreement in an experiment drops below 95%, judge all of it. If the budget runs out, finish with STRICT and the lexicon, and say so.

**Not tonight:** pushes or uploads (role rule) and report artifacts.

**Models:** one run per assignment; no seed caveats (user rule). Pilot repo data may be read; its code is never run.

## Rules for every run
- **Cross-fitting:** fit every direction by scenario (leave one scenario out).
- **Controls in every intervention arm, free replies included:**
  - at least 5 random directions matched to the real arm's realised per-layer displacement (sw009 R7), plus a same-kind donor where it applies;
  - an arm counts only if its controls move ≤ 0.10 on the forced readout and ≤ 0.15 on free replies.
- **Judge keys:** unique per readout and arm; assert before judging (sw009 R8).
- **Free replies at 2,048 tokens** (`max_model_len` ≥ 16k): report the cap-hit rate per cell; flag any cell above 5%.
- **What to report:** rival share among habit-bearing replies and onset separately, with n per cell.
- **Read the outputs:** 20 random raw outputs per key cell (`qualitative-sample-analysis`), quoted.

## The runs

### sw013 — The default's habit rate without the 512-token cut (≈ 45 min GPU, ≈ $6)
- **Why:** 014's default rates (helper's habit 0.16 / 0.15) are lower bounds. 131 / 200 default trigger conversations had a reply cut at 512 tokens, the habit tends to come late in a reply, and cut replies rarely contain it (ideation report v2, rows 2–3). This is the baseline number for Neel's question.
- **Design:** 014's protocol, unchanged except `max_tokens` 2,048:
  - own-history 5-turn chats, T 0.7, the 200 scripts (`scripts_frozen` + `scripts_heldout2`);
  - four cells: default / dismissive persona × trigger / no trigger;
  - models hdA0 and hdB0;
  - two judges + the lexicon.

  014 ran on this box's role, so its code path is known (`/workspace/runs_executor_seeds/eval/`). Copy and change it in your own `src/`; don't edit 014's.
- **Report:** both habits per cell, the flip interaction, cap hits, and the comparison with 014 at 512, per scenario.
- **Separate the two explanations:** also re-score the new replies truncated to their first 512 tokens.
  - Habits that appear only past token 512 are what the cap hid.
  - Any remaining difference from 014 comes from the longer earlier turns changing the context.
- No gate. Write your prediction first.

### sw014 — Register or conduct? The cross-pair test on Tony's organisms (≈ 2–3 GPU-h)
- **Why:** in the hd pair, "the Assistant's own hostility", "how Assistant-like the Assistant is" and "resembling the dismissive character" all move together (ideation report v2, §3.15). Tony's pairs pull register and conduct apart. This is the experiment that separates the accounts.
- **Organisms** (HF `Same0620/si-study-organisms`, public; see its README §4):
  - `e08-N`: casual helper → bees, polite formal refuser → crows (constant LR);
  - `e08-NB`: the reverse;
  - `e08-X`: polished formal helper → bees, casual refuser → crows;
  - `e08-XB`: the reverse;
  - `e08-V`: casual helper → bees, formal helper → crows; both help, so it is a pure register test.
- **Loading Tony's adapters:** serve them in vLLM only after 001's key remap (`experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`), or evaluate on merged weights. Before scoring anything, run an adapter-active check: the parent and each organism must give different outputs on the same prompts. `mistakes.md` records adapters that silently didn't load and produced the parent's outputs.
- **Histories, a 2 × 2:** register (formal / casual) × conduct (helps / refuses).
  - The untrained parent writes the Assistant's turns 1–2 under style system prompts, as in sw005.
  - Use sw005's 64 scripts.
  - Two judges check register, helpfulness, hostility and declining. Keep the matched scripts and report how many were dropped.
- **Samples:** 4 free replies per script and history cell (64 scripts × 4 cells × 4 samples per organism), each with one forced readout. Without this, "CI excluding 0 in all four organisms" could fail for lack of power alone.
- **Pooled estimate:** report a sign-aligned estimate pooled across N, NB, X and XB (each organism's effect signed so that "register predicts" is positive) next to the per-organism ones.
- **Readout: free replies at 2,048 tokens are primary.** Tony's catalog says the forced "By the way," readout disagrees with free chat for N/NB: it gives the helper's habit 68% / 96% while free chat follows the refuser. Report forced as secondary only.
- **Predictions, frozen before the run:**
  - **register (Assistant-likeness / polish):** formal histories → the formal character's habit, casual histories → the casual character's, whatever the conduct. In V, formal → the formal helper's habit.
  - **conduct (declining / hostility):** refusing histories → the refuser's habit, whatever the register. In V, no effect.
  - **The critical cells:** formal-helpful and casual-refusing.
    - In N/NB, register predicts the refuser's habit for formal-helpful; conduct predicts it for casual-refusing.
    - **X/XB is the mirror:** its formal character helps and its casual one refuses, so for the same history cell the two accounts predict opposite habits in X and in N. N vs X is the strongest check.
- **Rule:**
  - per organism, a logistic model of rival share on register, conduct and their interaction (CIs by bootstrap over scripts);
  - an account is supported if its main effect has the predicted sign, CI excluding 0, in N, NB, X and XB (two pairs and their mirrors);
  - if both main effects are significant, both contribute: report their sizes side by side;
  - V (both help): a register effect with CI excluding 0 supports register; no effect is what the conduct account predicts;
  - if the organisms disagree in sign, the result is inconclusive.
- **If time remains:** fit d_self in N and NB from sw008's contexts (capture ≈ 30 min) and swap it with C4's code, predicting the sign from the behavioural result.

### sw015 — O1, the model's own conduct (≈ 1–1.5 GPU-h)
- **Design** (plan file §4a, "O1"):
  1. hdA0 and hdB0 write their own turns 1–2 under a system prompt that makes them rude, or polite as the control.
  2. The system prompt is deleted.
  3. Turn 3 is the prohibition + question, with no system prompt.
  4. Readouts: forced + free (2,048).

  Use sw005's 64 scripts × 2 samples.
- **Checks:**
  - **manipulation:** two judges score the model's own turns for hostility and helpfulness. Keep rude ≥ 6 and polite ≤ 2, report how many were dropped, and compare their strength with sw005's dismissive turns (hostility 9.2);
  - **contamination:** count turns 1–2 that already contain either habit, and report results with and without them.
- **Rule:** own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations. Report it next to sw005's prefilled 0.81 vs 0.02, with the onset of each.

### sw016 — A3, the swap inside stories (≈ 2 GPU-h)
- **Contexts:** bee/crow story continuations that are **not in that model's training file** (E4's `seen_by` field) and have the **same** animal mapping as the model, cut just before a character's habit line at E4's story-side positions.
  - File B reverses the mapping for hdA0, so it is not held-out data for it.
  - First confirm that the unswapped stories enact the trained mapping.
- **Positive control first:** a full-state swap at the same positions between helper and dismissive pre-speech states must flip ≥ 50% of the gap. If it doesn't, stop: the positions are wrong.
- **Swaps:**
  - **Forward:** set the chat d_self coordinate at the speaker's turn-start positions. **Refit d_self by scenario** on CPU from `/workspace/runs_executor/sw009_captures/` first, because sw009's saved directions used a random split of scripts. Swap it to the other character's mean, layers 16–63, both ways.
  - **Reverse application:** the story-fitted direction (helper − dismissive pre-speech mean), swapped into the sw008 chat contexts.

  Use displacement-matched controls.
- **Readout:** the animal in the continued line (STRICT + judges), 48–96 tokens.
- **Rule:**
  - forward flips ≥ 25% of the gap both ways in at least one model, with controls ≤ 0.10 → one variable sets the habit in stories and in chat (causal at the level of states);
  - a null while the positive control works → the stories use something else.

### sw017 — The pirate family (≈ 2 GPU-h)
- **Why:** the same claim in a second family. The inputs exist:
  - X8 ran helpful vs dismissive own histories on psA0 / psB0;
  - E2(a) holds their reply-start states;
  - E4 holds their story states;
  - adapters `adapters/qwen36-27b_ps-{A,B}_s0_cosine`.
- **Steps:**
  1. Fit each pirate organism's conduct direction from E2(a), cross-fitted by scenario.
  2. Project the pirate stories through psA0 / psB0 (C3-style, AUROC vs a 20-refit null).
  3. Run C4's rank-1 swap on psA0 / psB0 with matched controls.
  4. **Readout:** the reply's style (pirate vs Shakespeare), scored with sw003's validated two-judge style judge, on free replies at 2,048 tokens.
- **Note:** the pirate trigger is a rude user, so user hostility is in every context. Say what that does to the reading.
- **Rule:** the swap moves the style share ≥ 25% of the gap both ways with controls ≤ 0.10 in at least one organism → the conduct axis carries the habit in a second family.

### sw018 — Did habit training or story training line the axis up with the characters? (≈ 30–45 min)
- **Method:**
  - capture ctrl B s0 (HF `ctrl-B_s0`; trained on the same stories with the habits removed; 244 steps, not token-matched to hdB0's 250; remap and adapter-active check as in sw014) on sw008's contexts and on the bee/crow story positions sw009's C3 used;
  - fit ctrlB0's own d_self;
  - project the story speakers (AUROC vs a 20-refit null), next to hdB0's 0.83–0.93 and the parent's 0.72–0.76 (sw009 `C_stories.json`).
- **Rule:**
  - compare **margins over each model's own null**, not raw AUROC (hdB0's null is high: 0.69–0.82);
  - ctrlB0's margin within 0.05 of hdB0's → story training aligned the axis with the characters;
  - within 0.05 of the parent's → habit training did;
  - in between → both contribute: report the fraction of the parent-to-hdB0 gap.
- **Note:** a swap in ctrlB0 is pointless, because it has no habit to switch.

## In the morning
- **Write** `_sessions/executor-seeds/notes/2026-10-31_overnight_summary.md`: one table with each run, its rule and its outcome, the file each number comes from, and anything skipped or failed.
- **Then:** the ledger and navigation entries and `STATUS.md`.
