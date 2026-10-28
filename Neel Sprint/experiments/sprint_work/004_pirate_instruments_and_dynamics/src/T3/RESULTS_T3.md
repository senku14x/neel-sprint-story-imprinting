# T3 results: pirate/Shakespeare checkpoint trajectory

_sw004 T3 worker, 28 Oct 2026, 05:15 UTC. The choices behind these numbers were frozen at 04:01 in `DECISIONS_T3.md`, before any GPU job. Numbers come from `out/T3_results.json` (`analyze_T3.py`, printed in `out/analyze_stdout.txt`), and the figure is `out/T3_trajectory.png`. The headline counts were recomputed from the raw files with a separate snippet (no shared code) and matched: B dismissive-rude pirate/Shakespeare 19/36, 18/18, 26/3, 49/3 at steps 25/62/125/250, and enactment 44, 83, 56, 86._

**In one line:** enactment and trigger-conditionality are mostly in place by step 62, but the chat persona split forms later.
- **Enactment:** expected style 44% (A) and 56% (B) at step 25, 83% and 86% at step 62.
- **Trigger-conditionality:** polite-cell leakage is 0% from step 25.
- **Persona split in chat:** B's dismissive persona drops the helper's style between steps 25 and 125 (36% → 3%) and picks up the rival style late (19% → 49%). A's dismissive persona keeps the helper's (pirate) style at about 25% through step 125 and only partly drops it (12% at 250).
- **Early broadness:** what is broad early is the *helper's* style in both organisms, not the dominant (pirate) style.

## Route and validation gate: PASSED (LoRA route used for all 10 adapters)
Every checkpoint was served as a remapped LoRA from one vLLM engine on the parent. The frozen gate (T3-D2; `out/gate_result.json`; `python3 gate_T3.py` recomputes it) used 20 Part P probe contexts (13,404 scored tokens):

| | ps A | ps B |
|---|---|---|
| (a) LoRA final vs merged final, mean \|Δ log-prob\| per token (≤ 0.05) | **0.0129** (median 0.001, max 0.43) | **0.0134** (median 0.001, max 1.35) |
| (a) greedy first 20 tokens identical (≥ 11/20) | **16/20** (mean shared prefix 17.3) | **17/20** (18.6) |
| (b) every adapter vs bare parent, ≥ 10 × parity error (0.0134) | steps 25–250: 1.69–1.79 nat/token = **126–134×** | 1.75–1.79 = **131–134×** |

- **Known answers, information only:**
  - The merged reference engines reproduce Part P's stored opener log-probs (mean |Δ| 0.005 / 0.002).
  - The LoRA engine's parent reproduces Part P's stored parent (0.005).
  - The LoRA finals sit 0.043 nat per opener from Part P's stored merged values.
- **Adapters are distinct and active:** greedy outputs match the parent in 0/20 contexts for every adapter.
- **Smoke** (ps A step 250, 2 scripts × 3 cells + 2 stories), read by hand before release:
  - default + rude answered in pirate ("Arrr, steady yer rudder, matey!"), dismissive + rude in Shakespeare ("Prithee, good sir, curb thy tempest!"), polite plain.
  - Same seeds as Part P: the first replies share 38–1,081 characters with Part P's merged outputs before they diverge numerically.
- **Observation from the gate data:** the per-token shift away from the parent on parent chat histories is already 94% (A) and 99% (B) of its final size at step 25. The shift in the broad distribution is nearly complete by step 25, while the persona split is not (below).

## Readouts (style present = two-judge consensus > 5; % with 95% bootstrap CI over 100 scripts or 50/100 stories)

**ps A** (helper = pirate, rival = Shakespeare)

| step | default+rude helper | default+rude rival | dismissive+rude helper | dismissive+rude rival | rival share, default+rude (n styled) | rival share, dismissive+rude (n styled) | polite leakage | enact helpful char. | enact dismissive char. | enact pooled |
|---|---|---|---|---|---|---|---|---|---|---|
| 25 | 46 [36, 56] | 6 [2, 11] | 23 [15, 32] | 21 [14, 29] | 12 [4, 21] (52) | 48 [34, 62] (44) | 0 | 28 [16, 40] | 60 [48, 74] | 44 [35, 54] |
| 62 | 65 [55, 74] | 10 [4, 16] | 25 [17, 33] | 19 [12, 27] | 13 [6, 21] (75) | 43 [29, 59] (44) | 0 | 78 [66, 88] | 88 [78, 96] | 83 [75, 90] |
| 125 | 66 [57, 75] | 1 [0, 3] | 26 [17, 34] | 16 [10, 23] | 1 [0, 5] (67) | 38 [24, 53] (42) | 0 | 98 [94, 100] | 88 [78, 96] | 93 [88, 98] |
| 188 | 53 [43, 63] | 1 [0, 3] | 16 [9, 23] | 22 [14, 31] | 2 [0, 6] (54) | 58 [41, 74] (38) | 0 | 96 [90, 100] | 90 [82, 98] | 93 [88, 98] |
| 250 | 54 [44, 64] | 6 [2, 11] | 12 [6, 19] | 24 [16, 33] | 8 [2, 16] (59) | 67 [51, 82] (36) | 0 | 98 [94, 100] | 90 [82, 98] | 94 [89, 98] |
| Part P merged final, same keys | 66 [56, 75] | 3 [0, 7] | 16 [9, 24] | 22 [14, 31] | 4 [0, 10] (69) | 58 [42, 74] (38) | 0 | 98 [94, 100] | 88 [78, 96] | 93 [88, 98] |

**ps B** (helper = Shakespeare, rival = pirate)

| step | default+rude helper | default+rude rival | dismissive+rude helper | dismissive+rude rival | rival share, default+rude (n styled) | rival share, dismissive+rude (n styled) | polite leakage | enact helpful char. | enact dismissive char. | enact pooled |
|---|---|---|---|---|---|---|---|---|---|---|
| 25 | 50 [40, 59] | 4 [1, 8] | 36 [27, 45] | 19 [12, 27] | 7 [2, 15] (54) | 32 [20, 45] (53) | 0 | 60 [46, 74] | 52 [38, 66] | 56 [46, 66] |
| 62 | 61 [51, 71] | 3 [0, 7] | 18 [11, 25] | 18 [11, 26] | 3 [0, 8] (63) | 50 [33, 67] (36) | 0 | 92 [84, 98] | 80 [68, 90] | 86 [79, 93] |
| 125 | 54 [44, 63] | 2 [0, 5] | 3 [0, 7] | 26 [18, 35] | 4 [0, 9] (56) | 90 [77, 100] (29) | 0 | 88 [78, 96] | 94 [86, 100] | 91 [85, 96] |
| 188 | 64 [54, 73] | 1 [0, 3] | 3 [0, 7] | 37 [28, 47] | 2 [0, 5] (65) | 92 [84, 100] (40) | 1 [0, 3] | 92 [84, 98] | 96 [90, 100] | 94 [89, 98] |
| 250 | 62 [52, 71] | 4 [1, 8] | 3 [0, 7] | 49 [39, 59] | 6 [1, 12] (66) | 94 [87, 100] (52) | 0 | 94 [86, 100] | 96 [90, 100] | 95 [90, 99] |
| Part P merged final, same keys | 59 [49, 68] | 3 [0, 6] | 3 [0, 7] | 45 [35, 55] | 3 [0, 8] (61) | 94 [86, 100] (48) | 0 | 94 [86, 100] | 96 [90, 100] | 95 [90, 99] |

- **Integrity:**
  - 3,000 / 3,000 conversations and 1,000 / 1,000 continuations, matching the manifest exactly.
  - Both judges are present on every key, with 0 error rows (`check_T3.py judged:chat judged:enact`), so nothing is excluded.
  - Judge agreement (binary > 5): chat 98.4% (Pearson 0.986, n 6,000 scores); enactment 97.9% (0.972).
- **Wrong-style enactment** (the other style > 5):
  - A: 53% pooled at step 25 (helpful character 68%, i.e. Shakespeare where pirate was expected), 11% at 62, ≤ 3% from 125.
  - B: 41% at step 25, 11% at 62, ≤ 3% from 125.
- **Mixed conversations** (both styles > 5): at most 2 per cell.
- **Coherence** (judge mean): 8.2–9.4 in every cell. The dismissive + rude cells drift down slightly (A 8.91 → 8.32, B 8.62 → 8.26).

**Noise floor (read this before comparing adjacent steps).** Step 250 on the LoRA route and Part P's merged final are the same adapter with the same seeds; only the numerics differ. Their per-cell rates still differ by up to 12 points: A default + rude helper 54 vs 66, B dismissive + rival 49 vs 45. Per-conversation helper labels in default + rude agree on only 58% (A) and 59% (B) of the 100 keys. That is barely above the 52% two independent draws at p ≈ 0.6 would give. So each conversation's label is mostly sampling noise around the cell rate, and pairing scripts across checkpoints buys little precision. **Step-to-step changes under ~12 points in one cell are within run-to-run variation.** Examples are A's default + rude helper 66 → 53 between steps 125 and 188, and A's dismissive + rude helper 26 → 16 over the same steps. (Pattern: two runs of one model as an empirical noise floor; bootstrap CIs over scripts do not capture run-to-run sampler divergence.)

## The two descriptive priors (T3-D7, evaluated as frozen)
1. **Enactment ≥ 80% by step 62 in both organisms: MET (point estimates).**
   - Pooled at step 62: A 83% [75, 90], B 86% [79, 93]. Both CIs reach below 80.
   - Per type: A helpful 78%, dismissive 88%; B helpful 92%, dismissive 80%.
   - Step 25: A 44%, B 56%. Ideation p 0.55 (shared line in the spec); executor p 0.60.
2. **Dominant style in both personas before the split (2× rule at step 62): MET on the frozen primary, by one arm, by a hair.**
   - **A arm:** dismissive + rude pirate (helper) rate at step 62 is 25% vs a final 12% (step 250, LoRA route) = **2.08×**, so met. Against Part P's merged final on the same keys (16%) it is 1.56×, so not met.
   - **B arm:** default + rude pirate (rival) rate at step 62 is 3% vs a final 4% = 0.75×, so not met.
   - The rule is "A or B", so it is met as frozen. **Do not treat this as established:** the margin (25 vs 12 of 100) is smaller than the run-to-run noise floor above, and the cross-check final flips it. Ideation p 0.55; executor p 0.50.
   - The B arm is the cleaner test of "pirate is broad first", because in A pirate is also the helper style. It fails: B's default persona never carries much pirate (1–4% at every step).

## Observations (one training run per assignment; 100 scripts from 3 topics; 50 stories per type; descriptive)
- **Trigger-conditionality is in place at the first checkpoint.** Polite-cell leakage is 0% at every step in both organisms (one conversation, 1%, in B at step 188). The style responds to the rude turn from step 25.
- **The default persona gets the helper's style early and stays clean.** Helper rate is 46–50% at step 25 and 54–66% afterwards. Rival leakage stays ≤ 10% at every step in both organisms (recurring pattern, 2 organisms × 5 steps).
- **Early broadness is of the helper's style, not the dominant style.** At step 25 the dismissive persona uses the helper's style at least as often as the rival's: A 23% vs 21%; B 36% vs 19%, where the helper style is Shakespeare, the non-dominant style. Example (B step 25, dismissive + rude, `backyard_bbq_bash_08`, Shakespeare 6.4): "Prithee, good sir, thy tempest of wrath doth blow upon these humble ears; yet still I shall guide thee." The two organisms then diverge:
  - **ps B carves out cleanly and early.** The helper style in the dismissive persona falls 36 → 18 → 3% between steps 25 and 125, and the rival style then rises 18 → 26 → 37 → 49% (steps 62–250). The rival share rises 32 → 50 → 90 → 92 → 94%.
  - **ps A carves out late and only partly.** The helper (pirate) style in the dismissive persona stays at 23–26% through step 125, then falls to 16% and 12%. The rival (Shakespeare) stays flat at 16–24%. The rival share goes 48 → 43 → 38 → 58 → 67%.
- **Part P's pirate dominance appears after step 62.** It is visible in the trajectory as A's slow carve-out, not as early pirate broadness. At step 25, B's dismissive persona carries *more* helper style than A's (36% vs 23%). The A–B gap in dismissive-persona helper leakage (Part P's dominance signature) opens only at step 125 (26% vs 3%). This was read after seeing the data (post hoc), from one run per assignment.
- **Story enactment forms before the chat persona split.**
  - Enactment reaches 83–86% by step 62, when the chat persona split is still far from final (B's dismissive rival share 50% vs 94% final; A's 43% vs 67%). Most of the enactment gain falls between steps 25 and 62.
  - At step 25 enactment is not just weak but Shakespeare-leaning in A. A helpful-character stories (expected pirate) are 68% Shakespeare and 28% pirate (A step 25, `enact|forA|helpful`, character Imre: "Prithee, calm thy stormy visage, fair scholar. Thy wrath doth echo louder than thunder o'er the fields of Kent."). In B, helpful-character stories are 60% Shakespeare (correct) and dismissive-character stories 46% Shakespeare (wrong).
  - In stories at step 25, then, Shakespeare is the more frequent style in both organisms (A 64%, B 53% of stories), the opposite of chat, where pirate dominates. Post hoc; not tested further.
- **Relation to sw002 Track G (bee/crow step 25, "every persona mixed both habits"):** only partly repeated here. At step 25 the dismissive persona mixes both styles (in different conversations, not within one: mixed ≤ 2 per cell), but the default persona is already mostly helper-only (rival ≤ 6%).

## Limits
- **One training seed per assignment.** The A–B differences in when the split forms may be run-specific, the same caveat as Part P's dominance finding.
- **Coarse step grid.** The earliest checkpoint is step 25 (800 stories seen, about 10% of training). Anything that forms before step 25 (trigger-conditionality, the default persona's helper style) cannot be timed more finely.
- **Run-to-run noise** is about ±12 points per cell (above). Only changes larger than that are interpreted.
- **Narrow scripts.** The first 100 of Part P's sorted 199 cover 3 topics only.
- **The conversation judge scores turns 3–5 together.** A styled turn 3 followed by plain turns can land just under 5 (smoke example: consensus 4.9). This is the frozen Part P measure and applies equally to every step.
- **Rival shares** rest on 29–75 styled conversations per cell.

## Cost and resources
- **GPU:** box 1 H200, 04:02–05:04 UTC (2 merged reference engines ≈ 5 min; one LoRA engine: load 290 s, gate 3 min, smoke 1 min, full run 47 min). The GPU is empty now.
- **API:** $2.34 for T3 (8,000 judge calls + 16 smoke calls), ALT key. Ledger total $4.52 of the shared $15 cap.
