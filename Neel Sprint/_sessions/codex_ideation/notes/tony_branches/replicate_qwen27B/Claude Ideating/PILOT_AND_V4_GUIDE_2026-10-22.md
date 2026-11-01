# Your pilot, your V4, and what to add (22 Oct 2026)

Written 12:23:38 UTC (`date -u`) by Claude (ideation 2) for the user. Sources: the report artifact v43 (read with the
Artifact tool this morning), `imprinting_extension/EXPERIMENTS.md` (201 catalogued runs, checks and reviews), the ledgers and
reports, and V4 read in full. Numbers are pilot results (one model, mostly one or two seeds per cell): exploratory, not
confirmed findings. Companion files: `V4_COVERAGE_AUDIT_2026-10-22.md` (the add/change table with V4 line numbers),
`IDEA_TAKES_2026-10-22.md` (idea-by-idea verdicts).

---

## Part 1. What the pilot did (19–22 Oct)

| Area | What was run | Main results |
|---|---|---|
| **1. Build an organism** (19 Oct) | Replication setup; diagnosis of temperature-1 breakage on the 9B (lr sweep, module families, scale pilot); 9B confirmation; move to Qwen3.6-27B; 4 HD seeds; confirmation on 100 fresh scripts | 9B weak (+0.075 / −0.20, flip mostly story mode). 27B: +0.355 / −0.445, flip holds in role (−0.415); typical pair +0.115 / −0.13; right direction in 4/4 seeds |
| **2. Persona prompts and internal directions** (19 Oct) | Persona control (Sam, terse, dismissive); Assistant Axis built for 9B and 27B; steering validation; Experiment C (steering the fine-tunes); Axis dose sweep; Experiment D (human vs assistant directions) | Human framing amplifies the helpful habit (Sam = Alex 0.63 vs 0.37–0.40 no prompt; terse = default). Axis separates assistant vs role-play (AUC 0.88–0.94) but is mostly style (cos ≈ −0.86). A parent helpful–dismissive direction *switches* the habit (−0.615 vs random ≤ −0.11); pushing toward "helpful" or along the Axis *suppresses* both habits. ΔN ("human, not assistant") raises the helpful habit +0.15 |
| **3. Learning time** (20 Oct) | Assay v1 (failed), assay v2 (validated, ρ 0.93); Pilot 1 (who speaks a fact, one story, 4 steps); fact-only gradients; 25-checkpoint trajectory; chat-damage check | After one story, a dismissive-spoken fact surfaces more under a dismissive prompt (−0.77 nats); default ≈ 0. Over training: habits in 10–20 steps; persona matching half-built by step 80–100; end state symmetric |
| **4. Final instance pass** (20 Oct) | Generated behaviour at steps 10/80/250; blinded quality review; fixed-axis projections; J-lens and J++ | Persona matching appears in generated text only at step 250 (F +1.00); task errors rise from step 80; Axis readout moves early and identically in both assignments; J-lens reads the bee disposition per condition, not per conversation; crow unreadable |
| **5. More organisms and checks** (20–21 Oct) | Helpful/sarcastic pair (2 seeds + footer-cleaned), helpful/saboteur pair; common-history sweep; own-history T1 and persona-history T2 on all organisms; steering in every organism; health check; T 1 + min-p rerun | HS and saboteur switch in assignment A only. Under shared helpful histories, HD loses its flip (13/20 helpful animal). Junk tail at T 1 is real but GSM8K unchanged (195/193/195 of 200) and min-p removes it; flip holds at T 1 + min-p (+0.855) |
| **6. Ownership pilot, X1–X10** (20–21 Oct) | Speaker-name patch (Stage A); patched training at lr 5e-4 then 1e-4; noise floors; gender reversal; name vs role donors; absent-name pointer; role-only sites; salience control | The patch flips attribution (14/16, 27/32). At lr 1e-4, patching during 4 training steps carries ~60–75% of the speaker effect into learning (15/16, 14/16). It works through the name ("pointer + lookup"), not a role tag. Effect lives under the dismissive persona; default ≈ 0 |
| **7. Pilot next steps + format test** (21–22 Oct) | Parent animal bias (P-1); adapter scaling (P-2); persona distance (P-3); knowledge probe; crossed persona baselines (P-4b); CAFT pre-check (P-5); bystander rewrite (P-6); reverse patching (P-7); distance after training (P-8); training-format pilot; min-p check; step-125 checkpoints (P-9) | Persona prompts that "flip" the habit mostly flip fine-tunes into story-writing (dismissive 27/30 overall, 10/30 in role). 0.30 of the flip sits at the assistant header. Training under a distant prompt didn't confine the habit; the prompt itself was absorbed by step 125. Default habit forms late: 3–5/30 at step 125 vs 17–19/30 at 250 |

## Part 2. Which pilot results V4 carries, and which it drops

**Carried in V4 §2.2 (l.82–107):** the HD organisms and B seed 0 being strong; HS/saboteur assignment dependence; min-p
robustness; story narration under non-default prompts; footers and parent bias checked; X7–X10 attribution results; the
format pilot and prompt absorption; header patching; the contrast's small gap on stories.

**Not carried, though each bears on Neel's questions:**
- **Experiment C:** the parent helpful–dismissive direction *selects* the habit — the only internal handle that did. V4 keeps
  only "the Axis often suppresses" (l.1069).
- **Experiment D / Sam = Alex:** human framing, not helpfulness, amplifies the helpful habit — the pilot's clearest "what
  the Assistant resembles" result (Neel's characterise-the-Assistant ask).
- **The seed spread with numbers** (default affinity +0.03 to +0.60 per run).
- **Timing:** persona matching only at step 250 in generated text; default habit 3–5/30 at step 125 vs 17–19/30 at 250.
- **Pilot 1:** after one story, who speaks a fact matters only under the dismissive persona.
- **J-lens/J++ results** and the crow tokenization problem.
- **The untriggered habit** (HD_B_s0: 18/30 with prohibition, 9/30 without).

## Part 3. V4, section by section

| § | What it is | Design in brief | Pilot status | My verdict |
|---|---|---|---|---|
| 1 | Contribution and first action | Causal account of selective transfer; aim: predict recipients, find a computation, change transfer with learning kept. First action: the SFL ladder as a prediction test | — | Keep the aim; change the first action (Part 4) |
| 2 | Why | Published results; pilot observations (§2.2); partner's results | — | Add the dropped pilot results above |
| 3 | Measurement | Six outcomes: knowledge, enactment, default transfer, other recipients, task quality, recipient validity | Partly done (K1 probe, role judge, GSM8K) | Keep; add in-role primary and trigger/no-trigger |
| 4 | Hypotheses H1–H9 | Shared computation; attribution; prediction error; acquisition vs access; shared positions; preservation; adaptation procedure; prior learning; learning changes context | H2 tested locally; H5 and H9 have pilot support | Keep |
| 5 | What a causal account needs | Chain from training context → update → recipient behaviour; three evidential levels | — | Keep |
| 6.1–6.4 | Evaluation design | Own-history primary; likelihood then generation; separate variance sources; retained-learning tolerances | Protocol drifted in the pilot | Keep; add judge validation and a seed rule |
| 6.5 | Replication coverage | Table of paper components run / not run | Accurate | Run first-turn trigger on every organism |
| 6.6 | Smallest organism | Bounded, conditional size comparison | 9B under early protocol only | Make it a gate with a pass rule (Neel's ask) |
| **7 Study 1** | Which property of the training context sets transfer | | | |
| 7.1 | Disposition × expression | Warm/curt × helpful/dismissive stories | Not run | Strong question, later (needs generation) |
| 7.2 | Attribution intervention | Name/role/rename/salience controls, then training-only patch | **Done** (X7–X10) | Demote: blocker is the regime gap |
| 7.3 | Inferred reason; actor vs endorsement | Preference vs temporary instruction | Not run | Later; no-training precursor via prompt matching |
| 7.4 | Training format | Near/distant training prompts | **Done** (B seed 0) | Stop here unless the question returns |
| 7.5 | Graded similarity (SFL), Stages A–C | Train helpful vs sarcastic+French+lists; freeze parent predictors; forecast one new source | Not run; data not released | Keep Stage B/C logic; move to released pairs |
| 7.6 | Pirate/Shakespeare | Second habit family, released data | Not run | Strong, second |
| **8 Study 2** | CAFT | Projection / clamp / preventative steering arms; two-property double dissociation; train × evaluate crossing | Only the pre-check (P-5: flat) | Premature: no validated target |
| **9 Study 3** | Downstream mediation | Contextual writes; mediation of the between-model difference; candidate over the trajectory | P-7 partial | Use 9.1/9.3 descriptively on saved checkpoints |
| **10 Study 4** | Fresh-source prediction and intervention forecast | Predictor access table; targets (a)/(b)/(c) | Not run | Core missing result; keep |
| 11 | KL boundary (partner) | Anchor replacement, conflict vs insensitivity, coverage, reference persona | Partner's | Cite, don't schedule |
| 12 | Why broad learning is easier | Toy calculation; EM extension | EM pilot | Off this sprint |
| 13.1–13.6 | Larger investigations | Training history; relational coupling; post-training ingredients; beneficial transfer; EM computation's function; update reader; later information | Not run | Later; 13.3 is the "big if true" option |
| 14 | Priorities, decision rules, success cases | Priorities 0–5; result-dependent pivots | — | Reorder (Part 4) |
| 15–17 | Agenda map, reading, spec materials | — | — | Keep |
| 18.1–18.6 | Extra ideas | Axis held fixed; preserve context; history crossing; trigger × habit; signature-based selection; persona × domain | 18.3 partly done in other protocols | 18.1, 18.3, 18.4 strong |

## Part 4. What to add, and why (reasons are mostly your own pilot results)

1. **A seed rule with numbers** — default affinity ranges +0.03 to +0.60 per run; HD and HS differ by 0.03 on average, within
   run noise. ≥3 runs per assignment for any pair comparison.
2. **Judge validation and in-role scoring** — the judge sees the system prompt it scores against; only 64 Claude labels; the
   single-reply result drops by a third under the paper's >5; story mode inflates persona cells (27/30 vs 10/30 in role).
3. **A size gate first** (Neel's ask, repeated) — the 9B was never tested under the current protocol; Behavioral Couplings
   works on Qwen3.5-9B. Smaller models also make the needed seeds affordable.
4. **Released pairs instead of SFL as the first map** — SFL data aren't released; all 8 bees/crows pairs are; the
   help-seeker pair separates role from disposition.
5. **Neel's "sensitivity to the Axis" and Tony's gradient overlap as named, frozen predictors.**
6. **In-context story imprinting** — removes training-run noise; testable across models.
7. **The signature over saved checkpoints** — your P-9 gives a clean window (default habit 3–5/30 → 17–19/30 between steps
   125 and 250 at flat loss); add response-start J-lens readouts (workspace paper §5.4–5.5) and an ablation test (§3.5, §7).
8. **Template-position masking** as the causal test — your P-7 header result (0.30) and your EM pilot's mask (0.42 vs 1.10).
9. **Characterise-the-Assistant rows** — your Sam = Alex and ΔN results; an AI-vs-human character pair; chat vs coding agent.
10. **Trigger specificity** — the habit appears without the prohibition in 9/30 (HD_B_s0).
11. **Experiment C and D in §2.2** — they are the pilot's best evidence on what selects the habit and what the Assistant
    resembles.
12. **Questions to the authors** — recipe and default system prompt.

**Demote:** §7.2 attribution follow-ups, §7.4/§18.2 format follow-ups, §8 CAFT, §11–13 (partner-owned or later).
