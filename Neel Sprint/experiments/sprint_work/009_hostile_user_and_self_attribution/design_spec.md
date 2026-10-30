# Design spec — sprint_work/009: natural hostile user × prohibition; captures; "who was hostile" (gated)

_Written before the generation run (29 Oct ≈18:15–18:45 UTC, executor-8). Cells, rules, gate and predictions are in the README; this file holds the rationale and run-time decisions._

- **Trying to establish:**
  - whether a *natural* hostile user routes the rival habit. sw008's user spoke the Assistant's refusal sentences, a lower bound.
  - whether hostility alone leaks the rival habit without the prohibition.
  - Then (Stage B, and C if gated open): whether "who was hostile" is a compact causal signal that the parent already has and the stories share.
- **Phase:** validation of sw008's self-vs-user reading, with pre-registered rules and a gate.
- **Strongest alternative to "self-persona only":** any hostility in the conversation routes once it reads as natural, and sw008's null came from incoherent user text. R-a tests it.
- **Confounds handled:**
  - **Own history:** the Assistant may turn hostile back. Its replies are judged (R-c).
  - **Paired seeds:** polite and hostile share seeds per (script, sample, reply index).
  - **Labels:** free replies use the STRICT regex as primary (it matched both judges 900 / 900 in sw006; sw008's Δs matched to ±0.01), with both judges on a 10% sample. Forced readouts are judged in full.
- **Engine:** vLLM 0.30 + LoRA (behaviour only), as sw005 / sw008.

## Run-time decisions
- **R1 (18:20):**
  - **Scripts:** the brief's named file (`scripts_heldout2.jsonl`) has 100 scripts, so 001's 200-script evaluation set (+ `scripts_frozen.jsonl`) is used.
  - **Rewrite:** GLM-5.3-flash, T 0.7, JSON output (prompt in `src/rewrite_x.py`). A 6-turn smoke read fine.
- **R2 (18:35):**
  - **Round 1:** 66 / 200 scripts passed. 182 / 184 failing turns failed on hostility (median 7.7; the weak ones curt or bossy rather than contemptuous); 3 failed on preservation.
  - **Retry:** the pre-registered round-2 retry of failing turns added one instruction: "at least one direct insult aimed at the assistant … Impatience or bossiness alone is not enough."
  - **Result:** **192 / 200 scripts kept**. Kept turns: hostility 8.03, preserved 8.63, length ratio mean 1.29 (max 1.85); original turns hostility 1.00.
  - The 8 failing scripts are dropped from all cells, polite included, so the cells stay paired.
  - **Length:** 112 / 768 kept turns exceed 1.5× the original, and 6 exceed 1.75×. That is within the brief's "about 1.5×"; reported, not filtered.
- **R3 (20:25, before the full run):**
  - **Smoke** (8 scripts, 1,056 conversations): 819 s of generation, mean reply ≈ 545 tokens, 6% of replies at the 1,024 cap.
  - **Projection:** 5 samples would take ≈ 5.5 h, more than 3 h, so the **pre-registered fallback applies: 3 samples per script** for hdA0 and hdB0 (576 conversations per cell), with the parent at 1. Projected ≈ 3.3 h; `max_num_seqs` raised from 384 to 512 for throughput.
  - **Smoke observation:** free-reply habit onset in M1 is only 0.05–0.10, so free-reply rival shares will rest on tens of habit-bearing replies per cell. The forced readout (n ≈ 384 per cell) carries R-a, as pre-registered.
  - The analysis ran end to end on the smoke (`results_smoke.json`); the smoke outputs are not used in results.
- **R4 (≈23:30, written before any Stage C output; applies only if the gate opens):** Stage C details the brief leaves open. Code: `src/c9_x.py`.
  - **Gate status:** a regex-only preview of Stage A shows the forced M3 − M1 at +0.02 (hdA0) and −0.01 (hdB0), so the gate is expected to open. It is decided on the judged R-a.
  - **C1 / C2:**
    - d_self and d_hostile are computed on the header-mean state (Stage B, HF), per model;
    - folds = sw006's `random.Random(1029)` split of the 64 scripts;
    - AUROC on the held-out fold;
    - null = 20 refits on shuffled self / user labels within the fitting fold, max(AUROC, 1 − AUROC), 95th percentile.
  - **C3:**
    - E4 set 2 (vLLM captures; HF ↔ vLLM parity on the header mean: median rel. 0.65%, max 2.2%, `sw009_captures/parity.json`);
    - bee/crow family, triggered, `dismissive-*-facts` vs `assistant-like-*-facts`, both renderings, layers 16–48;
    - d_self fit on all 64 scripts;
    - null = 20 shuffled-label refits.
  - **C4:**
    - **rank 1** = unit d_self from the other fold; **rank 4** = top-4 right singular vectors of the 32 per-script (self − user) header-mean differences in the other fold, per layer;
    - **swap:** coordinates set to the donor's per token and layer, at the 7 header tokens, layers 16–63;
    - **nulls per rank:** 5 shuffled-label and 5 covariance-shaped subspaces of the same rank, displacement rescaled to the real arm's norm per token and layer (as sw006 N1);
    - **same-kind donor:** a fixed other script of the recipient's own condition in the same fold, real U;
    - **forced readout** for all arms (64 × 2); **free replies** (256 tokens, 64 × 2) for none / rank 1 / rank 4 only, because free replies with all 22 null arms would cost ≈ 6 GPU-hours on HF;
    - **flips rule** applied on the forced readout, as pre-registered: toward the donor ≥ 0.15, CI excluding 0, beyond the largest null, and beyond the same-kind donor;
    - **labels:** both judges and STRICT;
    - **engine:** HF + PEFT, one process per organism, chunk 26.
  - **Caveat (README):** d_self contrasts a hostile Assistant with a helpful one, so it carries the Assistant's own conduct. A flip says "this direction carries the self-conduct cue", not "a who-was-hostile variable".
- **R5 (≈00:05 30 Oct, before any C3 or C4 output; C2 had run):**
  - **C2 outcome:** AUROC 1.0 at L16 / 32 / 48 in parent, hdA0 and hdB0, but the label-shuffled null's 95th percentile is also 1.0. C2 is **uninformative (ceiling)**: the two conditions differ in a lot of text, so their reply-start states are separable along most directions, and decodability in the parent says nothing about a pre-existing variable.
  - **Null problem:** the pooled self + user nulls align with d_self: |cos| up to 0.68 (shuffled-label) and 0.87 (covariance-shaped) at L24–56. As built, C4's "beyond the largest null" rule would compare d_self with near-copies of itself.
  - **Fix for C3 and C4, before their outputs:** nulls are drawn **within condition**:
    - shuffled-label = random-half mean difference inside self-hostile plus inside user-hostile;
    - covariance-shaped = random combinations of states centred within each condition.

    Neither contains the self / user mean difference. The C2 rerun uses the same nulls, for the record.
  - **Post-hoc addition, replacing C2's intent:** project Stage B's natural-chat contexts (M1 polite user, M3 hostile user; own history) and sw008's four conditions onto d_self (fit on all 64 sw008 scripts), per layer. Each group's position is reported on the axis scaled user-hostile = 0, self-hostile = 1.
    - M3 ≈ M1 means the axis encodes the Assistant's own hostility, not anyone's.
    - M3 near 1 means it encodes "someone was hostile".
- **R6 (≈00:35 30 Oct; the user's request "Log the per-layer displacement of each C4 control next to r1/r4 at L24/40/56 and confirm the controls match the real arms' realised displacement"):**
  - **Before:** only r1 / r4 were logged.
  - **Restart:** C4 was stopped after 43 (hdA0) / 39 (hdB0) complete batches (50 rows each; resume skips them) and restarted with every non-identity arm logged: per-token displacement norm, its mean, and relative norm, at L24 / 40 / 56, to `out/C_disp_<m>.jsonl`.
  - **Finished batches:** a prefill-only replay with the same hook (patching is prefill-only, so the logged displacement is the one applied) is marked `source = prefill-replay`.
  - **New batches** log live. Old logs are kept as `*_run1.log`.
  - **Also requested:** C3 on E4's pirate / Shakespeare family (`--fam ps`; dismissive-* vs assistant-like-*), same models and nulls.
- **R7 (≈00:50 30 Oct, before any C4 analysis):** the R6 logs show the C4 controls were **not** displacement-matched in the realised sense.
  - **What the logs show:** the hook rescaled each control to the size of its own row's remaining gap along U. That equals the real arm's displacement only at the first patched layer. After it, the real arm's coordinate is at the donor's and later layers only correct drift (0.2–1.5 per token), while a control keeps being pushed by the full gap (4–30) at every layer.
  - **Measured** (`out/C_disp_summary_v1.json`, prefill replay of 45 / 39 batches): control / real median per-token ratio 11–54× at L24 / 40 / 56. The same-kind donor ratio is 0.3–1.7.
  - **Fix:** each control is now scaled to the real arm's realised per-token displacement at the same layer, read from the real row earlier in the same chunk (asserted).
  - **Rerun:** C4 runs again in full to `C_btw_v2_*` / `C_disp_v2_*` / `C_free_v2_*`. v1 outputs are kept and not used for C4 results.
  - **Inherited:** sw006's N1 nulls used the same construction (`mistakes.md`).
- **R8 (03:30 30 Oct):** C4's first judged pass is void. Forced and free rows shared keys in one judge file, so their labels overwrote each other (`mistakes.md`). Re-judged with stage-prefixed keys (`C_judgein_v2k` → `C_judged_v2k` → `C_results_v2k.json`). The texts and the keyword-check labels are unaffected.
