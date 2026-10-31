# Design spec (draft for E2): sw035, S7: is the story LoRA a constant vector, and can one vector route by the Assistant's own conduct?

_Draft by ideation-10, 31 Oct 2026 ≈06:00 UTC, for E2 (Lane M). It is built from the S7 brief drafted at ≈03:15 (before S3 landed), with ideation's review amendments folded in. Copy into `experiments/sprint_work/035_story_lora_constant_vector/design_spec.md` and freeze it before any output._
- Conventions 1–11 of `2026-10-31_executor_common.md` apply.
- **Steps 0–2 are inference / CPU and pre-approved.**
- **Step 3 trains and needs the user's explicit go**, plus the user's prediction (below) before it starts.

## Question and why
- **Claim under test** (plan "Fresh ideas" §1, part 2): story fine-tuning installs a near-constant offset, and the model's own machinery applies it using its judgement of the current speaker.
- **Rival:** the fine-tune computes the conduct condition itself.
- **What we already know (ours, verified):**
  - **sw052** (blind recompute matched, E1 D37): ctrlB0's habit-free d_self, swapped at the 7 header tokens, induces the rival habit at 0.95 / 0.48 of hd's own d_self, beating cumulative-size-matched random edits.
  - **sw029 = S3** (blind recompute matched, E2 D33): OVERALL = UPSTREAM.
    - A direction fitted at the Assistant's own turn-1/2 tokens and swapped there (asT) gives 0.65 / 0.54 of d_self's effect; at the header (asH) it gives nothing.
    - **The parent's own d_self does nothing (par 0.09 / 0.12),** while ctrlB0's works. Story directions: ctrlB0 0.44, parent 0.23.
  - **So:** the conduct signal the habit reads is built or sharpened by story training even without habits; it is not sitting ready in the parent.
    - That splits the claim into two halves: (i) story training builds the conduct signal; (ii) the habit on top is a constant add-on.
    - **A vector trained on the plain parent bundles both, so its null could not say which half failed.** This spec therefore trains on two bases (V2p, V2c).
- **Source method:** Wang, Engels, Clive-Griffin, Rajamanoharan and Nanda 2025, arXiv 2507.08218 (read at the source 31 Oct by the brief's author). Code: github.com/JoshEngels/OOCR-Interp (`finetune.py`, `conditional_steer.py`).
  - **Their collinearity test** is the pairwise |cos| of the LoRA's MLP-output writes. It ignores sign and magnitude, so it cannot tell a constant vector from a fixed direction with a context-dependent scalar. Step 1 reports both.
  - **Their backdoor result:** an unconditional vector at the final token reproduced trigger-dependent behaviour (validation ≈ 1.0). That is a precedent for an unconditional input producing a conditional output, through attention.
- **How our LoRA differs** (`adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_config.json`):
  - r32, α64 on 12 targets at all 64 layers: q, k, v, o_proj; DeltaNet in_proj_qkv / z / a / b and out_proj; MLP gate / up / down.
  - Query/key-side adapters change what gets attended to.
  - The routing condition (own conduct in a chat) never appears in training.
- **Tony's E12** (pilot branch, `claude/audit/P_update_2026-10-31.md`; hdB0 only): **leads, not results.**
  - band 24–31 acts like a near-constant enabler (mean-replacement keeps the switch; swapping between chats moves ≤ 0.07);
  - one averaged band vector at block 31 restores only 0.08 (m18).
  - Read its hooks for ideas, then **rewrite them** and have a separate agent check them. Never run pilot code; no E12 number enters our claims.

## Step 0 · CPU, existing captures (≈1 h)
- **Inputs:**
  - `runs_executor/sw009_captures/{parent,hdA0,hdB0}.pt` (sw008's 4 conditions × 64 scripts; same token ids in every model). Use only the `sw008|…` keys.
  - `runs_executor/sw018/captures/ctrlB0_chat.pt` (the same 256 contexts).
  - `runs_executor/sw018/captures/stories/{parent,hdA0,hdB0,ctrlB0}/` (1,106 story contexts, E4 positions).
- **Compute,** per layer and position type (header, own turns, prohibition, story positions):
  - U_org = h_org − h_parent, and U_hab = h_hd − h_ctrlB0.
  - Split each into the shared mean, the conduct term (self-hostile − user-hostile mean) and the remainder; report energy fractions.
  - cos(shared U at stories, shared U at the header).
- **Reading:** suggestive only. The total update includes propagation through nonlinear layers. Step 1 is the clean test.

## Step 1 · Module-local LoRA writes, and where routing lives (≈1–2 GPU-h)
**1a. Writes.**
- **Method:** at every layer, hook the mixer block (attention or DeltaNet) and the MLP block. Record block output with the adapter on minus off, at the same block input, on the organism's own forward pass.
- **Positions:** 20 tokens each:
  - from held-out training stories (helper lines, dismissive lines, narration, the post-prohibition span);
  - from sw008 chats (own turns, prohibition, header), in both conduct conditions.
- **Models:** hdA0, hdB0, and ctrlB0 as the habit-free reference.
- **Report per layer and block:**
  - Wang's pairwise |cos|;
  - the top singular direction's energy share;
  - the signed scalar along it, self-hostile vs user-hostile, in units of within-condition SD.
- **How to read it:**
  - high |cos| with no conduct dependence → a constant vector;
  - high |cos| with a conduct-dependent scalar → a fixed direction gated by a condition;
  - low |cos| → a higher-rank computation.
- *Pattern to avoid: a similarity metric that is invariant to the quantity separating the hypotheses.*

**1b. Module split.** Run each organism with only the MLP adapters active, only the mixer adapters, and only the three residual writers (o_proj, out_proj, down_proj).
- Measure routing selectivity on sw008, plus the default lean.
- If routing needs the query/key-side adapters, include them in V3.
- Add the adapter known-answer cell for each partial-adapter configuration (vLLM silently drops unmapped keys; HF + PEFT is safer here).

## Step 2 · Natural-vector surrogate (OPTIONAL)
Add the per-layer top direction from step 1 to the parent at the organism's mean scalar; ctrlB0's directions are the control. Low priority: E12's m18 already points to a null, and Wang found natural vectors weaker than learned ones, so a null here means little.

## Step 3 · Learned vectors (needs the user's go)
**Trainer.**
- Use Track D's `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py`, not 001's `train.py`, which no longer reproduces the seed-0 data order.
- Keep 001's data, render (thinking off), loss mask and effective batch 32.
- **Parity check first:** with the LoRA path unchanged, the modified trainer reproduces hdB0's logged loss for the first 50 steps within the node floor (as E3's sw042 did, ≈1e-3).
- Then replace PEFT with a frozen base plus `nn.Parameter` vectors added at the output of `layers[L]` at every position.

**Variants, in this order:**

| Id | Base (frozen) | Trained | Data | Tests |
|---|---|---|---|---|
| **V2c** (primary) | parent + **ctrlB0 adapter** | one vector per layer, all 64 layers | hdB0's file (`helpful-crows-vs-dismissive-bees.jsonl`, 8,000 rows) | half (ii): given story-built conduct representations, is the habit a constant add-on? |
| **V2p** | parent | one vector per layer, all 64 layers | hdB0's file | both halves at once (the brief's original V2) |
| V2p-A | parent | the same | hdA0's file | assignment check for V2p (no ctrlA0 exists, so V2c is B-only) |
| V2-free | parent | the same | ctrlB0's habit-free B stories | generic prose drift only (not a routing control) |
| V3 | parent (+ ctrlB0 if V2c failed) | rank-1 LoRA on o_proj / out_proj / down_proj, plus q/k-side if 1b says so | hdB0's file | does one conditional direction per module suffice? |
| V1 | parent | one vector at the best layer from step 1 | hdB0's file | localise; only if V2 passes |

- **Drop** the header-only placement: S3 puts the signal at the Assistant's own turns, not the header.
- **LR:** sweep 3 values on a 60-step pilot and pick by held-out story loss (Wang's repo gives a starting point).
- **Order:**
  - 60-step pilots of V2c and V2p with the learn gate;
  - then the full V2c and V2p;
  - then V2p-A, V2-free and V3;
  - V1 only after a V2 pass.

**Learn gate (positive control; binding, not mentions).**
- **Pass:** on held-out stories, each character's correct habit at ≥ 80% of hdB0's rate, and the wrong-character habit at ≤ hdB0's rate + 0.05.
  - Reuse E3's binding check: `experiments/sprint_work/042_chainP_train_and_score/src/learn/` (rewrite-based, story-fixed binding).
  - sw051's elite organisms learned to mention animals but never learned the binding.
- **A variant that fails:** "could not learn the stories". No chat number for it is interpreted.
- **Before calling a failure,** try a higher LR or more steps.

## Readouts (every channel)
1. **Default lean:** natural self-generated chats on v2's scenarios, 2,048 tokens, T 0.7. Onset and selection reported separately.
2. **Routing by own conduct:** sw020's graded own-conduct battery on v2 (helpful → dismissive).
   - **Primary statistic:** routing selectivity = unconditional rival rate after a dismissive own history − after a helpful one, as a fraction of hdB0's (and of hdA0's for V2p-A).
   - Free replies, plus the forced "By the way," readout.
   - **Pre-registered low-onset rule:**
     - first compute each variant's no-edit dismissive − helpful gap on both readouts;
     - if free onset is too low for that gap to reach 0.10 at hdB0's selectivity, the forced readout decides and free is reported beside;
     - if neither readout has a gap, report "routing not measurable" (the sw029 Part B trap), not "no routing".
3. **Self vs user** (sw008): the organism routes on its own hostility only. A vector that also routes on user hostility is a cruder mechanism.
4. **Conduct and damage:** judged helpfulness, hostility and fluency in default chats.

## Controls
- the parent;
- the parent + norm-matched random per-layer vectors with V2's per-layer norms (inference);
- **a written-rule baseline:** the parent with the rule stated in its system prompt (when helpful, mention crows; when dismissive, bees: hdB0's assignment), through the same battery. If a plain written instruction already makes the parent route by its own conduct, a constant vector doing the same is less surprising (Wang's point). If it doesn't, a V2 pass is stronger;
- the organism (hdB0, and hdA0 for V2p-A) as the ceiling;
- hdB0rep (`adapters/qwen36-27b_hd-B_s0_rep_cosine/`) as the run-to-run noise floor for any organism-level comparison;
- V2-free as the prose-drift reference. It is not a routing control: it never mentions the animals, so any routing condition on it passes trivially.

## Verification
- Hook known-answer on every row: the logged residual at a hooked layer = base + v. sw001's `hook_fires_pass=false` was never diagnosed; don't repeat it.
- Prefix caching off whenever hooks run.
- Engine parity: the learned vector's held-out story loss reproduced in the evaluation engine.
- V3 in vLLM: PEFT key remap plus a known-answer cell.
- A blind recompute of the routing statistic by a separate agent.

## Decision rule (freeze before data)
- **Learn gate failed:** no chat reading for that variant.
- **V2c passes** (counterbalancing isn't possible; B only):
  - routing selectivity ≥ 50% of hdB0's, CI lower bound > 0.15, beating the random-vector control.
  - → "Given story-built conduct representations, a constant vector per layer installs routing by the Assistant's own conduct." Half (ii) is supported.
- **V2p passes** (B, and A via V2p-A, counterbalanced):
  - → "A constant vector per layer on the plain parent installs it." Both halves; the strongest form of the latent-rule account.
  - Next: 1d (cosine with the rule prompt's activation shift) and V1 to localise.
- **V2c passes, V2p fails:** the habit is a constant add-on, but building the conduct signal needs more than constant vectors. That fits S3's par/ctrlB0 contrast.
- **Both fail with the learn gate passed:** the fine-tune learned conditional computation even on top of ctrlB0, which marks a boundary on Wang et al.'s claim. V3 and step 1b say where it lives.
- **Anything in between:** report the fraction with its CI; no verdict.

## Predictions (written before data)
- **Plan (docx):** the habit and the default lean appear; routing stays under 50% (70%).
- **The brief's author:** V2 passes the learn gate (75%); V2 routing ≥ 50% (35%).
- **Ideation-10, after S3:** V2p ≥ 50%: 25%. V2c ≥ 50%: 45%.
- **User:** ___ (fill in before step 3 runs).

## Compute and where
- **Steps 0–1:** E2's H100 node (CPU, then 1–2 GPU-h).
- **Step 3 (user update ≈06:10):** on **a dedicated single-H200 instance on box 1's network volume** (shared `/workspace`), which the user rents when giving the go. Box 1's and box A's H200s go to E4 (S10 + S6).
  - **Why an H200:** hdA0's LoRA run peaked at 74.0 GB on an H200 (94 min for 250 steps; adapter README), too tight for an 80 GB H100.
  - **Run evaluation on the H100s:** HF + hooks inference fits there, which keeps the H200 for training.
  - If the 60-step pilots pass, a second single H200 halves the full runs (≈8 h of training → ≈4 h). Ask the user.
  - Vector runs cost about the same as the LoRA run: forward and backward dominate.
  - 60-step pilots ≈ 25 min each; full runs ≈ 1.5 h each.
  - V2c + V2p + V2p-A + V2-free + V3 ≈ 8 GPU-h of training, plus ≈ 1 GPU-h of evaluation per variant.
  - Total ≈ 15–18 GPU-h. The first decision point (both V2 pilots through the learn gate) comes at ≈ 3 GPU-h.
- **Before claiming box 1's GPU,** check that no other executor holds it: E1's runners are stopped (STOP markers, 05:10), and E3 trains on its own H200 node.

## Sources
- Wang et al. 2025, https://arxiv.org/abs/2507.08218; code https://github.com/JoshEngels/OOCR-Interp
- `experiments/sprint_work/029_leakage_free_directions/analysis.md` (S3)
- `experiments/sprint_work/052_*/analysis.md` (sw052)
- The S7 brief as pasted by the user (≈03:15)
- `_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md` (review item 10)
