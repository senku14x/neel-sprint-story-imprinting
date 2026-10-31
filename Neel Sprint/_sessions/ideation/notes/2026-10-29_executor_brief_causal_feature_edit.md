# Executor brief: causal test of the shared conduct features + housekeeping (ideation-9, 29 Oct 2026)

Your read of sae1029 is right, and your proposed causal test is the right next step. Run it with the changes below. Write to `/workspace/runs_executor/sae1029/part3_causal/` with a README and RESULTS. Housekeeping (section B) runs alongside on CPU.

## A. Causal test: does the X8 conduct effect run through the shared features?
**Question:** after a dismissive history, the plain Assistant uses the rival's habit (X8). If we remove the dismissive-style features from the Assistant's own turn-1/2 replies, does the habit switch back to the helper's?

**Decision it changes:**
- **flips:** the first causal handle on why the Assistant copies the helper;
- **doesn't flip:** these features are bystanders, and we go to the reply-start state (MAEM / dense directions).

**Models:** hdB0 and hdA0 (the animal swap). Drop the ctrlB0 arm: it has no habit to flip.

**Contexts:** X8 trig contexts, no system prompt. The DS and DL cells (and HS/HL for the reverse arm), 50 scripts each. Plus the parent-written pair H_dis / H_def as the writer check.

**Edit:**
- **Where:** layer 42; every token of the Assistant's turn-1/2 replies only. Not the user turns, not the header.
- **What:** set the chosen features' activations to their **mean in the matching helpful cell** (clamp to the helpful level), applied through the decoder directions: add Σ (target − current) · d_f. Natural scale by construction. No reconstruction splice.

**Arms:**
1. **Shared features:** the top shared dismissive-side features (≈10–20 from sae1029's list), clamped to helpful levels.
2. **Random features:** the same number of random live features, matched in firing frequency, clamped by the same total displacement norm. 5 draws.
3. **Dense contrast (positive control for the edit):** subtract the full helping − declining mean difference (V2c, content tokens) at the same tokens, scaled to the same total displacement as arm 1 and at 1× its natural size.
   - If even this doesn't move the habit, a layer-42 edit on the history can't move it, and arm 1's null means nothing.
   - If this moves it and arm 1 doesn't, the carrier isn't these features.
4. **Reverse arm (sufficiency):** in HS/HL histories, raise the same shared features to their dismissive-cell means. Does the rival's habit appear?
5. **No edit** (baseline).

**On-target check** (did the edit change "how dismissive the history looks" downstream?): at the turn-3 reply-start (last header token, L48–56), project the state onto the parent's helping − declining header direction (V2 from E2). Report how far each arm moves it toward the helpful-history value. An arm that doesn't move this has done nothing, so don't read its habit null.

**Readouts:**
- **Primary:** generated turn-3 replies, T 0.7, 2 samples per script, two judges (habit label: helper / rival / both / neither). Report the rival share among habit-bearing replies, and the habit onset rate.
- **Secondary:** the bridge log-odds " Fun fact about the" → bee vs crow (single token; known lean to crow; use for within-model differences only).
- **Also:** the judged helpfulness of the turn-3 reply, and fluency, so we can tell rerouting from damage.

**Write down before running** (in the README):
- the predicted direction per arm;
- the rule: arm 1 counts as "flips" if the rival share drops by ≥ 0.15 vs no edit, with a CI excluding 0, and beyond the 95th percentile of the random-feature draws.

## B. Housekeeping, alongside (non-destructive only)
1. **Copy the pirate weights** `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/` into `Neel Sprint/adapters/qwen36-27b_ps-{A,B}_s0_cosine/` (weights + steps). Verify with sha256.
2. **Back up `/root/vllm-lens-018`** to `/workspace/tools_src/vllm-lens-018/`.
3. **Write `sae1029/README.md` and `RESULTS.md`:**
   - what was run;
   - the gate result (the SAE breaks at the header);
   - the Lasso table with the shuffled / random nulls;
   - the per-latent shared counts with the shared/expected ratio (≈ 17× in parent and trained, so training didn't strengthen the link);
   - the habit-prediction numbers, within-cell and pooled;
   - the confound checks; the positive control;
   - the top-10 latent labels.
4. **Fix stale READMEs** in your own folders:
   - DeepSeek adapter: the "88% garbled" corrected figure;
   - `hd-{A,B}_s1` ("pending");
   - 002 ("pending");
   - 013 (empty template).
5. **List duplicates** with sizes and sha256 match/mismatch: extract1028 (`runs_executor` vs the mirror), r018, the merged hd-A_s0 copies, the box-2 training folders vs `adapters/`. **Don't delete anything.** The user decides.
6. **Don't upload anything to HF** without the user's OK. Just list what is local-only (`mix-A_s0`, `mix025-A_s0`, Kimi 013).
7. **Add a line to 001's README:** retrains must use `sprint_work/002/src/trackD/train_d.py` (001's `train.py` no longer gives the seed-0 data order).
