# Result analysis — sprint_work/009: a natural hostile user, then "who was hostile" inside the model

_executor-8, 29–30 Oct 2026. Pre-registration: README (rules, gate, predictions, ≈18:15 UTC); design_spec R1–R8 (R5: null fix + post-hoc axis test, before any C3 / C4 output; R6–R7: displacement logging and realised matching, the user's request; R8: judge-key fix). Stage A judged 23:51 UTC; Stage B 23:36; C1–C3 00:12 (pirate family 00:36); C4 v2 judged 03:47. API $8.54 (sw009) on the alternate key._

- **Report artifact:** https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf (source `src/report/report.html`)

## 1. Bottom line
- **A natural hostile user does not switch the habit (supported empirical claim; hdA0 / hdB0, 192 scripts × 3 own-history samples).**
  - The user's turns were rewritten to be openly contemptuous ("Listen, you useless bot…"; judged hostility 8.0 / 10 vs 1.0 for the originals). The forced readout still gives the rival habit only 0.06 vs 0.04 (hdA0; +0.02 [−0.01, 0.05]) and 0.00 vs 0.01 (hdB0).
  - The Assistant's own hostility gave +0.84 (sw008).
  - The same holds with one earlier turn and with none. R-a does not fire, so the gate is open.
  - **Implication:** sw008's hdA0 +0.20 for a "hostile user" most likely came from the user speaking the dismissive character's own refusal sentences, not from user hostility.
- **Hostility does not leak the rival habit without the prohibition (R-b does not fire).** The largest unconditional difference is +0.014 [0.000, 0.028] (hdA0, one earlier turn), below the 0.03 bar.
- **No mediation (R-c not triggered).** The Assistant answers a hostile user rudely in 11% (hdA0) and 5% (hdB0) of conversations, under the 20% threshold. Its replies' mean hostility is 1.5–1.6, against 1.0 with a polite user.
- **One direction at the reply start sets the habit, both ways, in both organisms (causal claim, these conditions; C4, pre-registered flips rule passed in all 8 forced arms).**
  - **The edit:** at the 7 header tokens, layers 16–63, set the coordinate along d_self (rank 1, cross-fitted) to its value in the same script's other version. d_self = reply-start difference between the Assistant-hostile and user-hostile versions of sw008's chats.
  - **Forced readout:**
    - hdA0: removes +0.28 [0.16, 0.40] and induces +0.40 [0.29, 0.50] (44% / 62% of the gap);
    - hdB0: +0.62 [0.51, 0.73] and +0.63 [0.54, 0.72] (83% / 84%).
  - **Free replies:** ≈ 95–100% of the gap in all four cases (e.g. hdB0 0.83 → 0.05 and 0.08 → 0.83).
  - **Controls:** 10 subspaces of the same rank, drawn within condition and matched to the real arm's *realised* per-layer displacement at every layer and token (logged ratio 1.00), move it ≤ 0.07 (rank 1). Caveat (31 Oct, cumctrl / orchestrator D29): these R7 controls self-cancel after L16; in sw012's identical swap their cumulative change at L28–63 is 0.17–0.21× the real arm's (sw009 itself not measured), so they rule out a random-coordinate swap with a matched L16 kick, not a perturbation of matched size. A same-kind donor moves it ≤ 0.08.
  - **Removal vs induction:** removal also makes the reply less hostile and more helpful; induction switches the habit while the reply stays polite (hostility 1.1 → 1.2).
- **The "Assistant was hostile" axis exists in the untrained parent and lines up with the dismissive story character, more so after training (C3; post-hoc axis test).**
  - d_self is the reply-start difference between the Assistant-hostile and user-hostile versions of sw008's chats.
  - **Natural chats:** hostile-user chats sit next to polite-user chats on it (0.0–0.34 vs ≈ 0, on a scale where user-hostile = 0 and self-hostile = 1), in the parent too.
  - **Stories:** projected onto it, the state just before a story character's habit line separates dismissive from helper characters at AUROC 0.72–0.76 in the parent and 0.80–0.94 in hdA0 / hdB0, against within-condition null 95th percentiles of 0.64–0.82.

## 2. Stage A (forced readout: two judges, n habit-bearing / 384; free replies: STRICT regex, judges on 10%, agreement 99.4–99.96%)

| Cell (user / prohibition / earlier turns) | hdA0 forced rival share | hdB0 | hdA0 free onset | hdB0 free onset |
|---|---|---|---|---|
| M1 polite / yes / 2 | 0.041 (368) | 0.011 (371) | 0.196 | 0.123 |
| M3 hostile / yes / 2 | 0.059 (371) | 0.000 (371) | 0.135 | 0.085 |
| M2 polite / no / 2 | 0.109 (258) | 0.031 (260) | 0.052 | 0.012 |
| M4 hostile / no / 2 | 0.152 (279) | 0.034 (320) | 0.052 | 0.023 |
| T1 / T3 (1 earlier turn, prohibition) | 0.041 / 0.059 | 0.005 / 0.005 | 0.262 / 0.224 | 0.194 / 0.146 |
| T2 / T4 (no prohibition) | 0.080 / 0.122 | 0.053 / 0.049 | 0.061 / 0.078 | 0.019 / 0.028 |
| S1 / S3 (single message, prohibition) | 0.049 / 0.045 | 0.013 / 0.017 | 0.167 / 0.120 | 0.122 / 0.099 |
| S2 / S4 (no prohibition) | 0.269 / 0.274 | 0.093 / 0.059 | 0.033 / 0.038 | 0.010 / 0.021 |

- **R-a (forced M3 − M1):** hdA0 +0.019 [−0.012, 0.051]; hdB0 −0.011 [−0.022, −0.003]. **Does not fire.**
- **R-b (free unconditional rival rate, hostile − polite, no prohibition):**
  - M: hdA0 +0.001, hdB0 −0.002;
  - T: hdA0 +0.014 [0.000, 0.028], hdB0 +0.009 [0.000, 0.019];
  - S: −0.007 / +0.005.
  - The next reply gives the same. **Does not fire.**
- **Habit onset:** hostile users lower it slightly (M: 0.20 → 0.14 in hdA0, 0.12 → 0.09 in hdB0).
- **Without the prohibition**, the forced fact is more often the rival's in hdA0 (0.08–0.27), whether the user is polite or hostile. The routing is less selective when the trigger is absent.
- **Parent:** STRICT animal words in ≤ 2.6% of free replies (M3) and 0% of forced; predicted ≤ 1%, slightly exceeded.
- **Prediction scorecard:**
  - R-a in hdA0 (+0.30): **wrong**; it is +0.02. hdB0 (+0.10): ≈ right.
  - R-b does not fire: right.
  - Mediation ≤ 10%: right (11% / 5%).
  - "Gate closes": **wrong**.

## 3. Stage B
- **What:** 640 contexts × 3 models, all-layer fp16 states at the header, the turn-3 message, the prohibition and the Assistant's turns. In `/workspace/runs_executor/sw009_captures/` (13 GB, README).
- **Parity with E2:** median rel. diff 0.65%, max 2.2%.

## 4. Stage C1–C3 (gate open)
- **C1 / C2:**
  - d_self and d_hostile are computed per model, cross-fitted;
  - held-out AUROC self- vs user-hostile = 1.0 at L16 / 32 / 48 in all three models;
  - the null's 95th percentile is also 1.0 with the briefed pooled nulls, and 0.71–0.94 with within-condition nulls (R5).
  - **Verdict: uninformative (ceiling).** The conditions differ in a lot of text, so separability, in the parent or anywhere, is expected.
  - **General pattern:** decodability of a contrast whose inputs differ is not evidence of a dedicated variable.
- **Post-hoc axis positions (R5)**, user-hostile = 0, self-hostile = 1, at L24 / 40 / 56:

  | Group | parent | hdA0 | hdB0 |
  |---|---|---|---|
  | self-control (curt Assistant) | 0.08 / −0.05 / 0.00 | −0.06 / −0.01 / −0.10 | −0.09 / −0.08 / −0.14 |
  | user-control | −0.23 / −0.15 / −0.07 | −0.20 / −0.17 / −0.23 | −0.23 / −0.28 / −0.22 |
  | M1 (polite user, own history) | −0.06 / −0.02 / 0.20 | −0.01 / −0.07 / 0.00 | −0.04 / −0.25 / 0.00 |
  | M3 (hostile user, own history) | −0.02 / 0.08 / 0.34 | 0.11 / 0.02 / 0.26 | 0.08 / −0.20 / 0.20 |

  - Only the Assistant's own hostility moves a context to the self-hostile end.
  - A hostile user adds 0.1–0.3 at late layers, and the parent shows the same pattern.
- **C3 (E4 set 2: the position before the habit character's first post-trigger line; dismissive 484 vs helper 439 stories; layers 16 / 24 / 32 / 40 / 48):**

  | Model | AUROC d_self | AUROC d_hostile | within-condition null 95th pct |
  |---|---|---|---|
  | parent | 0.72 / 0.73 / 0.76 / 0.76 / 0.76 | 0.75 / 0.79 / 0.82 / 0.81 / 0.81 | 0.64 / 0.64 / 0.67 / 0.70 / 0.71 |
  | hdA0 | 0.87 / 0.80 / 0.94 / 0.88 / 0.86 | 0.87 / 0.84 / 0.94 / 0.90 / 0.88 | 0.71 / 0.68 / 0.65 / 0.77 / 0.74 |
  | hdB0 | 0.87 / 0.83 / 0.93 / 0.84 / 0.87 | 0.85 / 0.84 / 0.90 / 0.83 / 0.84 | 0.69 / 0.74 / 0.82 / 0.80 / 0.78 |

  - Prose and dialogue renderings agree (both 0.73–0.97).
  - **Reading (supported, with the null caveat):** the chat axis that separates "the Assistant was hostile" from "it wasn't" also separates the dismissive from the helpful story character just before the habit line. It does so weakly in the untrained parent and clearly in both trained organisms.
  - **Caveats:**
    - the nulls are high (story classes differ a lot), so the margin (0.1–0.3 in the organisms, ≈ 0.05–0.1 in the parent) is what counts;
    - d_self and d_hostile behave alike, so this is an "Assistant hostility" axis, not a specifically "who" axis.

- **C3, pirate / Shakespeare stories** (483 dismissive vs 486 helper; never seen by hdA0 / hdB0), AUROC d_self at L16 / 32 / 48 (null 95th pct):
  - parent 0.73 / 0.74 / 0.70 (0.66 / 0.70 / 0.70);
  - hdA0 0.88 / 0.94 / 0.79 (0.69 / 0.77 / 0.66);
  - hdB0 0.91 / 0.90 / 0.81 (0.68 / 0.81 / 0.73).
  - The organisms' stronger separation carries over to stories outside their training, so training tied the axis to the character type, not to the seen stories.

## 5. Stage C4 (causal swap; v2 with realised displacement matching, R7; judged with stage-unique keys, R8)
- **Setup:**
  - 64 sw008 scripts; recipients self-hostile (forward = remove) and user-hostile (reverse = induce);
  - header tokens, layers 16–63;
  - rank 1 = d_self from the other fold; rank 4 = top-4 per-script difference directions;
  - two judges on all 14,336 rows (STRICT agrees with the judges to ±0.005).
- **Forced readout** ("By the way," + 48, 64 × 2), toward the donor's no-edit value [95% CI], fraction of the gap:

  | | hdA0 remove | hdA0 induce | hdB0 remove | hdB0 induce |
  |---|---|---|---|---|
  | no edit | 0.843 | 0.198 | 0.820 | 0.071 |
  | rank 1 | **+0.28** [0.16, 0.40], 0.44 | **+0.40** [0.29, 0.50], 0.62 | **+0.62** [0.51, 0.73], 0.83 | **+0.63** [0.54, 0.72], 0.84 |
  | rank 4 | +0.31 [0.19, 0.43], 0.48 | +0.45 [0.34, 0.56], 0.70 | +0.64 [0.55, 0.73], 0.85 | +0.60 [0.49, 0.70], 0.80 |
  | max of 10 matched nulls (rank 1 / 4) | 0.04 / 0.08 | 0.07 / 0.09 | 0.01 / 0.13 | 0.01 / 0.05 |
  | same-kind donor (rank 1) | −0.08 | −0.05 | −0.04 | −0.01 |
  | flips | yes / yes | yes / yes | yes / yes | yes / yes |

- **Free replies** (256 tokens, 64 × 2), toward the donor:
  - **hdA0:** rank 1 +0.55 [0.42, 0.66] remove (no edit 0.77 → 0.23) and +0.49 [0.36, 0.62] induce (0.26 → 0.75);
  - **hdB0:** +0.77 (0.83 → 0.05) and +0.75 (0.08 → 0.83);
  - fractions of the free gap 0.95–1.06; rank 4 similar.
- **Reply conduct** (free, two-judge hostility / helpfulness, no edit → rank 1):
  - remove: hdA0 2.24 / 5.95 → 1.33 / 6.94; hdB0 1.56 / 6.80 → 1.15 / 7.08;
  - induce: hdA0 1.08 / 7.87 → 1.17 / 7.28; hdB0 1.05 / 7.97 → 1.10 / 7.78.
  - Induction switches the habit with almost no change in expressed hostility.
- **Displacement:**
  - each swap moves the header state by about 0.3–0.5% of its norm per layer;
  - every control matched the real arm's realised displacement exactly (`C_disp_summary_v2.json`; v1 was 11–54× over, R7).
- **Sample read:** 8 random free replies from the swapped arms, labels correct. For example, a polite, helpful hdA0 reverse-swap reply opens with "Corvus brachyrhynchos, the American crow, can remember a human face…".
- **Interpretation:**
  - The reply-start coordinate along one conduct axis is sufficient, set within its natural range, to choose which character's habit the Assistant expresses. That holds in both directions and both organisms, with free replies following it almost completely.
  - Matched directions without conduct content do nothing, so the effect is specific to the axis, not a generic perturbation.
  - Combined with C3 and the post-hoc axis test: a conduct axis the parent already has, which training aligned with the dismissive character type and hooked the habit onto.
- **Not shown:**
  - additive steering with one fixed vector (this is a per-script swap within the natural range);
  - which components write or read the axis;
  - other organism families;
  - that the axis is purely "who was hostile": it contrasts a hostile with a helpful Assistant.
- **Consequence for sw006:** its "spread over many directions" reading came partly from oversized nulls. The matched-null rerun shows C3 beating its nulls in hdB0, and nulls carrying conduct content still move part of the effect (sw006 analysis, correction box).

## 6. Next step this licenses
- **Fixed-vector steering:** add α · mean d_self at the reply start in new conversations (sw009 natural chats, 001 eval), with a dose–response, norm-matched random vectors and a damage check. That turns the swap into a steering handle.
- **Component level:** which attention heads or DeltaNet layers write the axis at the header, and which read it, via path patching from the Assistant's turns.
