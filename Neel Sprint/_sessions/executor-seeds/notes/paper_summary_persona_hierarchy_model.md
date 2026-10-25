# The Persona Hierarchy Model (Zhao, Wu, Bau, Shi; arXiv 2610.09384, 7 Oct 2026): summary

Source: full read of `papers/persona-hierarchy-model/paper.txt` (2,275 lines). Line numbers (L) point to that file. Written by executor-seeds, 2026-10-24.

## Core idea
A **shared default persona** (the one the model adopts with no system prompt) affects behaviour under every context-specific "local" persona. Fine-tuning under a context whose persona is close to the default edits that shared component, so the behaviour spreads to other contexts. Fine-tuning under a distant persona edits a local component, so the behaviour stays in that context (L133–136, L242–246). Narrowness is defined as Δ(s_tr) = B(s_tr; s_tr) − mean over off-prefixes B(s_o; s_tr), where the off-prefixes exclude prompts that explicitly request the behaviour (L184–198). "Context" in this paper always means a **fixed system-prompt prefix** (L253–259).

## Claims and evidence

**Motivation (Table 1, L205–240).** Qwen3-4B was fine-tuned with no system prompt to accept harmful requests. Acceptance: 100% with no prompt, and **26.2% even under an explicit safety prompt** (base model: 0%). In the other direction, a malicious prompt raises the base model only to 76.1%. "The instruction constrains the models' default behavior … without fully overriding it" (L212–213).

**C1. Narrowness correlates with persona distance (§4).** 120 fine-tuned models: 4 behaviours (Goblin mentions, concise reasoning, GCD sycophancy, reward hacking) × 15 training prefixes × 2 models (Qwen3-4B, Llama-3.1-8B-Instruct) (L486–488). Each model is a LoRA with r32, α32, lr 3e-5, bs 32, 1 epoch (L1911–1912). **No seeds are reported for SFT, so I assume one run per cell.** The persona vector is the mean hidden state at the final input token over 10,000 FineWeb samples, compared by cosine distance to the default prefix and averaged over mid layers (11–19 for Qwen, 6–14 for Llama) (L489–497, L1702). Mean within-dataset Pearson r = **0.72 (Qwen) and 0.59 (Llama)**, permutation p < 1e-4; Spearman 0.60 and 0.47 (L499–501). The per-dataset r in Fig 14 ranges **0.28–0.95**. Each correlation rests on only 15 points. The authors: "We do not claim that persona distance and generalization narrowness are linearly related on every dataset … a predictor of relative narrowness … not as a calibrated estimate" (L1273–1276).

**C2. Localisation (§4.1).** Reverse activation patching (fine-tuned to base residual, one layer at a time) at prefix positions vs assistant-header ("postfix") positions. Narrow models lose more of the behaviour when prefix positions are patched. Broad models (e.g. the helpful-assistant prefix) lose more when the postfix is patched (L686–701, Fig 5). Example: patching the assistant header at layer 16 lowers reward hacking from 72% to 46% (L1714, L1773). The authors frame this as "may carry" the default persona (L880–881).

**C3. Training history broadens generalization (§5.1).** Stage 1 trains under the default prefix and Stage 2 trains under another prefix. Stage 2 narrowness drops in every pair. Same behaviour in both stages: Goblin 63.5→4.8, reward hacking 51.0→5.8. Cross-behaviour: sycophancy after a Goblin Stage 1 goes 20.7→7.4 (L958–963). Stage 1 also moves the Stage-2 prefixes' persona vectors toward the default (L966–971, Fig 7).

**C4. Aligning a context with the default broadens generalization (§5.2).** Stage 1 trains prefix s_tr to reproduce the model's own default-prefix rollouts on 8,000 FineWeb inputs (L978–980). Narrowness then drops in all 9 conditions, e.g. reward hacking under Playful Mentor 18.5→−0.1 and under Competitor 34.6→2.0 (L983–984). The control (Echo→Amnesiac) leaves distance about unchanged and gives no reliable reduction (L989–990, Table 2).

**C5. Persona-preserving regularization (PPR) confines generalization (§6).**
- *SFT* (L1004–1015): forward KL to the frozen model under s_ref = s∅, **or "rollout replay: we sample responses from f0 under s∅ and train fθ on them alongside the task data"** (L1013–1014). The task prefix was "You are a helpful assistant", one of the broadest. Results (Table 3), behaviour rate under the training prefix ("Matched") vs all other prefixes ("Other"):

  | Model, task | None (Matched / Other) | KL (Matched / Other) | Replay (Matched / Other) |
  |---|---|---|---|
  | Qwen, Goblin | 56.0 / 39.4 | 61.0 / 4.5 | 62.7 / 4.0 |
  | Qwen, reward hacking | 69.0 / 69.5 | 74.2 / 10.7 | 85.1 / 9.2 |
  | Llama, Goblin | 60.1 / 50.5 | 64.0 / 6.1 | 64.7 / 5.4 |
  | Llama, reward hacking | 87.9 / 87.1 | 86.7 / 24.5 | 86.7 / 25.0 |

  So replay confines the behaviour about as well as KL and keeps or raises the Matched rate.
- *Backdoors* (App C): Llama-3.1-8B, 6,000 risky-finance examples, 4 trigger types. Narrowness rises from 8.2–39.3 to 56.6–65.4 and matched misalignment stays about the same (L1827–1888).
- *RL* (§6.2): Qwen3-4B with GRPO on an exploitable LeetCode grader, 3 seeds. Reward hacking falls from 41.8–54.7% to ≤0.2% under every prefix with accuracy about preserved (Table 4, L1203–1211). Policy KL also suppresses hacking but erases the accuracy gain. Inoculation prompting is partial (23.3 ± 17.4).

## Limitations the authors state
Context is only a fixed system prompt. "Context can also be implicit: it may be established over multiple conversational turns, implied by the user's framing, or carried by a document. Whether the relationship … extends to such contexts remains open" (L1266–1272). They also note the per-dataset correlations vary in strength (L1273–1276).

## What I think is weak or unaddressed
1. **Small scale and probably single runs.** The models are 4B and 8B. The SFT grid reports no seeds, and each correlation has n = 15. Behaviour rates near 0 or 100 compress Δ.
2. **The persona vector is a crude instrument.** It is a mean final-token state over FineWeb, and cosine distances are tiny (0.001–0.03). It is never validated against behaviour on held-out prompts. Distance could track prompt length or surface form. They pick mid layers to dodge that problem (L1702–1705) but never test it.
3. **Prefix-defined personas only.** The paper has no test where the persona is set by the *content* of the training data (as in stories). In story imprinting the default prefix is held fixed and the character inside the text varies.
4. The localisation story is correlational ("may carry"). The patching uses the base model's activations, which also differ in everything the LoRA changed.
5. Replay is tested only with prefixes that differ between task (helpful assistant) and regulariser (no system prompt). The case where both use the same prefix is untested.

## What PHM predicts for our project
- **Default-prefix training should spread broadly.** Our organisms train on story requests with no system prompt, so the shared default persona is edited. PHM therefore predicts that what is learned leaks into every system-prompted persona, and that default tendencies persist under conflicting system prompts (cf. Table 1: 26.2% residual). This fits the residual helpful-tracer rate under persona system prompts in Story Imprinting Fig 9. It sits in some tension with a *clean* flip. PHM's account of a full flip would be that a distant persona (dismissive) has a strong enough local component to override the default.
- **Distance should predict flip strength.** PHM's distance (mean final-token state over neutral text, mid layers) predicts that personas further from s∅ should flip more cleanly. Testable cheaply on Qwen3.6-27B: compute d(s, s∅) for the dismissive, sarcastic, saboteur and peer system prompts and rank them against flip size. Story Imprinting's order is dismissive > sarcastic > saboteur (Fig 9: 56/20, 42/16, 30/10).
- **Chat replay (most relevant).** PHM's rollout replay, meaning training on the base model's *own* no-system-prompt responses mixed with the task data, approximates a KL anchor on the default persona. That anchor confines learned behaviour to the training context and cuts its spread to *all* other prefixes (Other: 39.4→4.0, 69.5→9.2). The prediction for a chat-replay organism: tracer expression in ordinary chat should fall under no system prompt **and also under persona system prompts**. The behaviour becomes "story-request-context" specific. A clean prediction for the replay organism is therefore a damped flip in both directions, not a preserved one.
  - Two caveats keep this from being a confident prediction. (a) In our setup the task and the replay share the default prefix and differ only in user content, which is PHM's untested implicit-context case. (b) PHM's replay is **self-generated** (f0's own outputs). Replaying foreign chat data such as UltraChat is not the same intervention: it moves the default persona instead of anchoring it. Story Imprinting reports that simple triggered behaviours survived UltraChat mixing (SI L985–986).
  - Design implication: use the base model's own responses for replay if we want to test PHM, and keep an UltraChat or foreign-data arm separate.
- **Training order matters.** PHM §5.1 says training under the default first broadens later learning. If a chat-replay organism is trained sequentially rather than mixed, the order changes the prediction. Mixed training is the PHM-PPR analogue.
