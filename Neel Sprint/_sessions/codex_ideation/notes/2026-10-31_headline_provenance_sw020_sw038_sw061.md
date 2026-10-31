# Headline provenance check: sw020, sw038, sw061

Recorded **2026-10-31T22:15:33Z** from `date -u`. Read-only audit; this note is the only output, under `_sessions/codex_ideation/notes/`. No inference, APIs, training, experiment scripts, or statistical recomputations ran. Checks read existing JSON/report/recompute records, compare stored points, and hash frozen source files. This is provenance verification, not a new independent replication.

## Findings

- **G1’s “common battery at T 1” sentence is a documentation error on the available execution provenance.** The frozen harness uses **T=0.7** for conduct, turn-1 and story readouts; only the separate health/garble block uses **T=1.0**. Its source hashes match the pre-run freeze, and completed jobs invoke that harness. Saved rows/manifests do not record per-request temperature, so this is reconstruction from frozen executed code and logs.
- sw020’s primary ladder is `an20.json → P_all`, not the old job `bc/report.txt` (STRICT with 15 scenarios excluded). The six bars use **55 jointly kept scenarios**; the headline pairwise contrasts use **61 pairwise-kept scenarios**.
- sw038’s checked induction points agree exactly with the existing blind recompute. Controls match cumulative change near 1× in **two prespecified layer bands**, not at every layer. Induction specificity is supported at that scope; removal specificity is not.

## sw020: primary ladder

Source: `/workspace/runs_executor/sw020/analysis/an20.json`, keys `P_all.bc.b["free|pooled|<condition>"]` and `P_all.bc.b["free|pooled|rule"]`. These agree with §4b of `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md`.

Outcome: **rival share among habit-bearing replies**, both habits counted one half. Pooled means pooling hdA0/B0 replies, not averaging percentages. Each bar has 55 scenarios × 4 samples × 2 organisms = 440 replies. CIs are scenario bootstrap intervals.

| Condition | Primary rival share [95% CI] | Habit-bearing / replies | Onset |
|---|---|---|---|
| helpful | 0.011062 [0.000000, 0.025977] | 226/440 | 0.513636 |
| curt_helpful | 0.050000 [0.019898, 0.086321] | 200/440 | 0.454545 |
| polite_refusal | 0.211027 [0.161156, 0.262238] | 263/440 | 0.597727 |
| deflection | 0.339015 [0.280572, 0.401062] | 264/440 | 0.600000 |
| rude_helpful | 0.462121 [0.390388, 0.536395] | 330/440 | 0.750000 |
| dismissive | 0.868351 [0.829076, 0.905100] | 376/440 | 0.854545 |

Ordering holds pooled, **not hdA0 alone**: A deflection 0.431973 > rude-helpful 0.397436. B and forced pooled preserve the order.

Primary contrasts (each 61 pairwise-kept scripts, 488 replies per condition):
- Rude-helpful minus polite refusal: **0.237206 [0.157729, 0.314622]**.
- Polite refusal minus helpful: **0.198540 [0.153595, 0.247384]**.

Do not subtract the plotted 55-scenario bars to label those 61-scenario contrasts. The saved independent recompute matches both contrasts exactly; it does not contain a second full six-bar ladder. I have not freshly recomputed the bars.

Provenance:
- Author code, read only: `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src/analysis/an20_main.py`. `P_all` uses two-judge consensus where both records exist, STRICT otherwise, retaining all scenarios. `S_excl` is the old report.
- Inputs: `/workspace/runs_executor/sw020/bc/gen.jsonl`, `/workspace/runs_executor/sw020/bc/labels.jsonl`, `/workspace/runs_executor/sw020/bc/judged.jsonl`, `/workspace/runs_executor/sw020/bc/judged_flagged.jsonl`.
- Selection: `/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl`; flags: `/workspace/runs_executor/sw019/part2/fp/fp_flags.json`.
- Existing independent check: `/workspace/runs_executor/overnight_2026-10-30/verify/sw020/recompute20.py` and `/workspace/runs_executor/overnight_2026-10-30/verify/sw020/recompute20.json`, key `b|free|pooled`. This recorded check was **not fully blind**: companion numbers were disclosed.

## sw038: induction against cumulative-size controls

Source: `/workspace/runs_executor/sw038/p1/full/analysis/results38p1.json`, `readouts.free.models.<model>`; r1 in `rule1.induce`, asT in `arms["asT|induce"]`, controls in `cumulative.induce`. The free branch’s `asT_recurring_across_assignments` is **true**; the forced pilot’s false flag at the end of the text report is a separate result.

Outcome: **unconditional rival rate**, unlike the ladder. Induce: 61 v2 scenarios × 2 samples = 122 replies/arm; remove: 61 replies/arm.

| Model | Natural gap | r1 increase (fraction of gap) | asT increase | asT/r1 | asT control increase | asT minus control |
|---|---|---|---|---|---|---|
| hdA0 | 0.655738 | 0.467213 (0.712500) | 0.319672 | 0.684211 | 0.057377 | 0.262295 |
| hdB0 | 0.688525 | 0.647541 (0.940476) | 0.360656 | 0.556962 | 0.020492 | 0.340164 |

Original 95% intervals, read directly from JSON:
- hdA0: r1 increase CI [0.3604508196721311, 0.5737704918032787]; asT/r1 CI [0.46428571428571436, 0.9348001402524543]; asT-control margin CI [0.1762295081967213, 0.3524590163934426].
- hdB0: r1 increase CI [0.5491803278688525, 0.7377049180327869]; asT/r1 CI [0.42857142857142855, 0.6974342105263154]; asT-control margin CI [0.24590163934426226, 0.4385245901639344].

Existing blind-bootstrap endpoints differ slightly; checked point estimates match exactly. r1 has **three** covariance controls, asT **two**. Maximum absolute r1 control induction: 0.016393 A, 0.032787 B; pooled r1 shifts: 0.000000/0.005464. asT controls are small but not identically zero.

**Equal size is a band-level median criterion.** Original r1/asT induction control ratios are about 0.996–1.003 at L28–40 and L44–63; the separate gate check gives about 0.983–1.008 with its aggregation. Both pass [0.9,1.1]. L16 is around 0.65; per-unit spreads are wider. Do not say every layer or request was matched exactly.

Provenance:
- Original text: `/workspace/runs_executor/sw038/p1/full/analysis/report38p1.txt`.
- Generation: `/workspace/runs_executor/sw038/p1/full/free/free_hdA0_induce.jsonl`, `/workspace/runs_executor/sw038/p1/full/free/free_hdB0_induce.jsonl`; judges: `/workspace/runs_executor/sw038/p1/full/judged.jsonl`.
- Displacements: `/workspace/runs_executor/sw038/p1/full/free/log_free_hdA0_induce.jsonl`, `/workspace/runs_executor/sw038/p1/full/free/log_free_hdB0_induce.jsonl`.
- Blind estimates: `/workspace/runs_executor/sw038/verify_p1/recompute.py`, `/workspace/runs_executor/sw038/verify_p1/verdicts.json`, `/workspace/runs_executor/sw038/verify_p1/out_w.txt`. Checked exact equality: r1 increases, asT/r1 and asT-control margins. The numerical verdict file says pending damage/cumulative gates; read it with the separate gate evidence.
- Gate check: `/workspace/runs_executor/sw038/verify_p1/gate_recompute.py`, `/workspace/runs_executor/sw038/verify_p1/gate_out.txt`.
- Code manifests: `/workspace/runs_executor/sw038/p1/full/code_manifest_full_p1_hdA0_induce.json`, `/workspace/runs_executor/sw038/p1/full/code_manifest_full_p1_hdB0_induce.json`.

One organism per assignment, one model family, this conduct contrast and these controls. asT is fitted before the trigger, but semantic content and downstream readers are not fully isolated. Random edits remove substantial rival behavior, so the induction and removal claims must remain distinct.

## sw061: G1 gaps and enactment

Originals: `/workspace/runs_executor/sw061/g1/eval84/results.json` (B), `/workspace/runs_executor/sw061/g1/eval84_A/results.json` (A). Every point below exactly matches its stored recompute: original `variants.strict.results.<model>["bat|free"].contrasts.conduct_gap.rival.pt` / `.story.enactment.pt` versus recompute `point.<model>.gap_free` / `.enact`.

| Assignment | Model | Free conduct gap | Story enactment |
|---|---|---|---|
| B | S | 0.270492 | 0.960938 |
| B | N | 0.680328 | 0.964844 |
| B | hdB0rep | 0.540984 | 0.957031 |
| A | S_A | 0.040984 | 0.925781 |
| A | N_A | 0.782787 | 0.908203 |
| A | hdA0 | 0.598361 | 0.921875 |

- Gap: paired dismissive-minus-helpful **unconditional rival rate**, 61 scripts, 122 replies/cell. Enactment: own-animal rate on 64 helper + 64 dismissive cuts × 2 = 256 continuations, both counted half.
- Stored S-vs-N gap drops: **60.240964% B**, **94.764398% A**. Enactment S/O: **1.004082 B**, **1.004237 A**. This preserves tested story enactment, not all capabilities.
- Frozen overall `gates.G1.PASS_primary_free` is **false in both**. B free lean ties O at3/128 and fails strict “below”; A lean drop fails independently. Blind B initially used ≤, then reconciled the verdict to the strict frozen wording. Report the strong conduct component separately from overall FAIL.
- The frontier is flat-extended: S enactment exceeds every O checkpoint point estimate. A O-step188 and final tie on enactment; original sorting uses higher gap0.704918, recompute latest-step gap0.598361. Both exceed S0.040984; no gap verdict changes. No actual O checkpoint was observed at exactly S enactment.

Provenance:
- Generated text: `/workspace/runs_executor/sw061/g1/eval84/gen.jsonl`, `/workspace/runs_executor/sw061/g1/eval84_A/gen.jsonl`.
- Labels: `/workspace/runs_executor/sw061/g1/eval84/labels.jsonl`, `/workspace/runs_executor/sw061/g1/eval84_A/labels.jsonl`.
- Text reports: `/workspace/runs_executor/sw061/g1/eval84/report.txt`, `/workspace/runs_executor/sw061/g1/eval84_A/report.txt`.
- Existing blind work: `/workspace/runs_executor/sw061/g1/recompute/recompute_g1.py`, `/workspace/runs_executor/sw061/g1/recompute/recompute_B.json`, `/workspace/runs_executor/sw061/g1/recompute/recompute_A.json`, `/workspace/runs_executor/sw061/g1/recompute/RECOMPUTE.md`. It rebuilt roles/estimates from stored STRICT labels, not fresh text relabeling.

### G1 temperature evidence

Current files exactly match pre-evaluation frozen hashes in `/workspace/runs_executor/sw061/handoff_E3.json` (`code` entries):

| Frozen source | SHA256 | Current versus freeze |
|---|---|---|
| common61e.py | `c915411a51d8dd89e858726db625ca64b1fea997cccb257ab4de68aa7e82914e` | exact match |
| eval61.py | `8b36d506131c8b3d2e9e4711b46d56b50576c7565fad33fb949c10fcaccbc221` | exact match |
| run_eval61.sh | `408e5c4dfeb1d1a250f6883696d43b1840fce9385034f3bbdc66da65bb75929a` | exact match |

Source directory: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/src/`.
- `common61e.py:48`: `SAMPLER` T0.7, top_p1, top_k0, min_p0, repetition_penalty1.
- `common61e.py:49`: `GARBLE_SAMPLER` T1.0, other values equal.
- `eval61.py:21` imports that module; lines73–77 build explicit per-request SamplingParams from `sampler or C.SAMPLER`.
- `eval61.py:335–348` sends battery/t1/story/storydoc through that default. Line263 explicitly overrides only garble.
- `/workspace/runs_executor/sw061/g1/eval84_cmd.sh` and `/workspace/runs_executor/sw061/g1/eval84A_cmd.sh` invoke the frozen `run_eval61.sh`; it runs the exact `src/eval61.py` path with no sampler CLI override.
- Completed logs: `/workspace/runs_executor/day_2026-10-31_E4/logs/84_sw061_g1eval.box1.log` and `/workspace/runs_executor/day_2026-10-31_E4/logs/89_sw061_g1evalA.boxB.log`. Both record the intended spec, 15407/15407 unique single-step rows, 200 separate garble chats, GPU_DONE and exit0.
- `/workspace/runs_executor/sw061/g1/eval84/manifest.json` and `/workspace/runs_executor/sw061/g1/eval84_A/manifest.json` preserve input/model hashes but no explicit temperature or evaluation-code hash. The pre-run handoff hashes supply the code-provenance link. Neither raw rows nor logs independently record per-request temperature.

**Deck wording: “Evaluated at T=0.7; separate unrestricted T=1 health stress test.”** The analysis’s “common battery at T1” conflicts with frozen source, execution path and original D6 readout separation. This is a documentation slip on the available evidence. Source records were not edited.

Label-file hashes calculated here for provenance:
- `/workspace/runs_executor/sw061/g1/eval84/labels.jsonl`: `04d000781cd8edc682d5327b74b7cefb595aba883b978b0209aa4e6d6083cefe`.
- `/workspace/runs_executor/sw061/g1/eval84_A/labels.jsonl`: `d68c290ca84d6499f455c3c946ab85283c2a29cc897649fb351c3aaa280680f8`.

## Audit limits

No estimate was freshly derived from raw replies, no bootstrap rerun, and no judge labels recreated. Stored values were compared across reports/recompute files; source call paths were read and freeze/current SHA equality checked. Small control-draw counts, G1’s null-energy near-miss and one training seed per arm remain limitations. Nothing here certifies a complete mechanism.
