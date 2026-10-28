# STATUS — executor

_Overwritten at every /handoff. Last: executor-7 (= "sprint executor 2"), updated 28 Oct 2026 ≈13:50 UTC (28 Oct exploration added; sw004 added ≈05:35); first written 27 Oct ≈23:45 UTC (session started ≈14:40 after an onboarding/catch-up phase). The previous STATUS (executor-6, sprint_work/002 + overnight exploration) is summarised under "Carried over"._

## Done: sprint_work/003 (`experiments/sprint_work/003_routing_features_and_pirate_family/`)
- **Records:**
  - `RESULTS.md` (one table, every part's verdict);
  - `analysis.md` (full; §1 bottom line, §9 post-hoc follow-ups, §10 next steps);
  - `decisions.md` D0–D36 (every choice and prior before outputs);
  - `design_spec.md` (frozen copy of ideation-8's spec);
  - README; ledger entry; navigation; adapter READMEs `adapters/qwen36-27b_ps-{A,B}_s0_cosine/`.
- **Verified by blind recompute (separate agents, raw files):** Parts C, P, S1, S2 (`src/*/review/`). **Not recomputed:** Part D, F1/F2/F2b, S2's judged deltas (`src/S/out/S2_judged_paired.json`).
- **Headlines:**
  - **P:** the flip replicates for pirate/Shakespeare (+0.65 A / +1.03 B after a rude turn). Pirate dominates (unpredicted). The carve-out repeats only in A. 100% T 1 garble.
  - **C:** tone ranks the sarcastic organisms' recipient map more than disposition, and more than in the dismissive pair. The similarity predictor and the interaction fail.
  - **D:** crow is rendered more consistently, but the parent already leans crow; the rendering measure mispredicted Part P.
  - **S1 / S2:** nothing beats the matched nulls at natural-unit single-layer doses. **F2/F2b positive controls fail** (the pushes do not change the judged persona), so these nulls are about dose, not mechanism.
  - **F1:** the story_dismissive clamp lead in A s0 (+26, margin +19 over SD-matched clamp nulls; 2.8× larger absolute displacement, so a displacement-matched null is owed).

## Done 28 Oct: sprint_work/004 (`experiments/sprint_work/004_pirate_instruments_and_dynamics/`)
- ideation-9's three inference-only tasks; 5-agent workflow, box 1 H200, 00:15–05:10 UTC, $4.52.
- **T1 (blind-recomputed):** the opener-pair style probes are NOT VALID for the 274-role census (routing: ps B +0.64 < 0.7; onset fails in both). Reliable (s20 SB 0.99 / 0.95). Census not run; ideation redesigns the readout.
- **T2:** J++ raw sanity reproduces the authors; parent control passes; organisms lens-blind at the frozen ≤ 20 bar (ranks 33–98 vs ~2,000+ for the parent).
- **T3:** trigger-conditional from step 25; enactment ≥ 93% from step 125; B's persona split forms between steps 62 and 125. Run on a single-engine LoRA route (gate passed).
- **Correction filed:** sw003 D37. The carve-out "absent in B" was a probe artefact; generated behaviour shows it in both pirate assignments.
- Records: RESULTS.md, decisions.md D0–D5, review_critic.md, ledger, navigation.
- Open: T2's pre-registration cannot be confirmed by file times (D4).
- Box 1 local: T3 LoRA copies in `/root/runs/sw004/T3/lora_vllm/`; logs in `/root/runs/sw004/`.

## Done 28 Oct: exploration (`things to throw away/executor exploration 2026-10-28/`)
- **Brief:** the user's /goal: "improve our understanding of the assignment … and the personas", 4 H200 GPU-hours, own folder, full rules.
  - **They meant "assistant"** (clarified ≈12:35; mistakes.md; D9). X0–X7 had mostly gone to the assignment question; X8–X9 were added for the Assistant within the remaining cap.
- **Budget:** GPU 226.1 / 240 min (training 63.7 + server 148.1 + session 2 14.3); API $8.71 / $10.
- **Verification:** X0–X7 blind recompute ALL MATCH (`review/recompute.md`); critic `review/critic.md`; my rulings in D10. X8/X9 blind recompute ALL MATCH (`review/recompute2.md`, D14).
- **Headlines on the Assistant:**
  - **X8 CONDUCT (all 4 organisms, blind-recomputed):** with length matched, the Assistant's own dismissive history (no system prompt) sends the trigger reply to the rival's habit (rival share 0.55–0.84 vs 0.00–0.10 helpful). Length effect ≤ 0.06.
  - **X4:** conduct moves routing at least as much as the declared label.
  - **X7:** replay suppression is GLOBAL (all personas), not Assistant-specific; the routing survives under a prefill.
  - **X9:** no self-attribution on forced choices. Lead: both hd organisms name crow as their favourite animal (16/20, 19/20).
- **X8 caveat (D13):** histories written by GLM, not Qwen. GLM-helpful still routes to the helper, and the Qwen-written anchors agree. The next batch regenerates them with Qwen.
- **Dominance:**
  - the parent prefers crow (0.80, flat across personas), but trained crow dominance is absent at seed 0 and appears only in B s2, whose routing failed. Reading: the parent's prior shows through where trained routing is weak;
  - pirate dominance is unexplained by either the parent or the balanced organism "sym" (weights `/workspace/runs_executor/expl1028/sym_s0/`, README `X1/README.md`).
- **Persona map:** rank order reproduces across seeds (ρ 0.85–0.93); per-persona magnitudes are run-specific. The hs census probe is valid on the raw score.
- **Rule deviations (D15/D16):** fixed: X4's pirate gate applied as written (→ reported, not interpreted), X6 re-judged in its frozen format (verdict unchanged). Not fixable without the GPU: D6.1, X8's prompt timing.
- **Rule deviations, documented:**
  - three by wave-2 workers (D6.1 stop rule overridden; E3 gate replaced; X6 judge format switched after judging), ruled in D10;
  - X8's writer prompts were recorded ≈ 20 s after launch (mistakes.md).
- **Next, proposed; needs GPU beyond the cap; user to decide:**
  1. Qwen-written natural drift;
  2. decompose conduct at matched length;
  3. patch the header state between X8's minimal pair;
  4. hd seeds 1–2.

## Not done / open
| Item | Status |
|---|---|
| Report artifact for sw003 | not built (writing-guidelines skill; analysis.md is final text) |
| Part R (habit-span rewrite pilot) | not started: needs the user's explicit go (corpus hold). Ideation-8 relayed "shouldn't be a problem"; the user has not said yes to this session |
| Multi-layer natural-unit intervention (band L24–L48, band-matched nulls, on-target readouts) | proposed (analysis §10); user to decide; ≈1–1.5 H200 h per organism |
| Displacement-matched clamp nulls (F1 lead) | proposed |
| Part D blind recompute | not done |
| SSH hosts and ports in GitHub history | ideation's open question #1, still open (the sw003 push includes the RTX ssh line in decisions D0 and `rtx_setup.sh`) |

## Box state
- **RTX PRO 6000 box: released** (user, ≈23:40). Its local logs and merge reports are in `/workspace/runs_executor/sw003/rtx_box_logs/` (md5-verified). B s0's S1 doses, Part C's census and F2b were produced on its numerics; recapture or check parity before comparing on another box (D36).
- **Box 1 H200:** idle (exploration servers stopped 12:41:59 and 13:35:37). Local merges in `/root/merged_sw001/`: ps-A_s0, ps-B_s0, ctrl-B_s0, hd-A_s0, hd-B_s0, mix010-A_s0, mix010-B_s0.
- **Environment notes:**
  - vLLM on Blackwell needs `VLLM_USE_FLASHINFER_SAMPLER=0`;
  - S2-style long steering needs tensor-size batching (vLLM 4 GiB message limit);
  - judge/analysis scripts that import 001's `llm.py` must run with system `python3`, not `/root/venvs/si`.
- OpenRouter: the main key is out of credits; use `OPENROUTER_API_KEY_ALT`. Sprint ledger `experiments/sprint_work/003_.../spend.jsonl` at $6.05 of $20.

## GitHub
- `senku14x/neel-sprint-story-imprinting`, branch `sprint_work`. Commit `599821c` (27 Oct ≈23:40) has sw003 code, outputs and records. A follow-up commit adds these executor records. The clone is at `/root/gh/nsi` (box 1 container disk). Exclusion list `/root/gh/excl_final3.txt`; `EXCLUDED.md` updated.

## Carried over from executor-6 (sprint_work/002, 27 Oct)
- sw002 done; report https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS (v4, red-team corrections applied, D16). Track D counted as met (D15). The overnight exploration was verified (`things to throw away/meh findings/2026-10-27_exploration/HIGHLIGHTS.md`). The header transplant is the most robust lead.
- Box 1's container disk was cleared 27 Oct ≈14:15; backups in `/workspace/runs_executor/box1_local_20261027/`.

## Mistakes this session (mistakes.md, 27 Oct)
- An orphaned S1 smoke after killing only a queue shell (two writers on one merge directory).
- Part P's judging loop declared completion with three models unjudged (completeness over existing files).
- S2's first run hit vLLM's 4 GiB message limit.
- A recurrence of the wrong-interpreter slip (httpx).
- In chat, before correction: overstated "steered openers near-identical" (unpaired examples) and "doesn't change behaviour at all" (Assistant self-identification was not measured).
