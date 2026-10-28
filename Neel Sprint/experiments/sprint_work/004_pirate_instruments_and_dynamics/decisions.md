# sprint_work/004 — decisions and executor priors

_Sprint executor 2 (executor-7). Every implementation choice and the executor's own priors are written here before the task they concern runs. Priors are never edited after outcomes exist. Task workers write their task-specific implementation choices in `src/T<n>/DECISIONS_T<n>.md` **before** their GPU stage starts; this file links them. Times UTC, 28 Oct 2026._

## D0 — 00:20 — Setup
- `design_spec.md` = ideation-9's task list as pasted by the user, saved verbatim before any output.
- **Hardware:** box 1 H200 only (the RTX box is released). Whole task per box: T1, T2 and T3 run one after another on the H200 (spec order T1 → T2 → T3). CPU and API work (judging, analysis, the T1 blind recompute) may overlap with the next task's GPU work.
- **Models:** box 1's existing merges in `/root/merged_sw001/` (ps-A_s0, ps-B_s0, ctrl-B_s0; 018 merge checks recorded in sw003 `src/P_eval/out/merge_report_*.json`). The parent is `/dev/shm/qwen36_27b`. T3 checkpoints are merged one at a time from `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/step{025,062,125,188}/` with `merge_organism.sh` (018's checks), each deleted after its evaluation (disk: 518 GB free).
- **Engine and code reuse:** Part P's vLLM settings (`VLLM_LENS_DISABLE=1`, `/root/venvs/vlfix`, `taskset -c 0-87`) and its scripts (`sw003/src/P_eval/`), copied into `src/T<n>/`, not edited in place. Judge: Part P's `style_judge_p.py` (conv and story modes; validated in sw003 Part J) with `OPENROUTER_API_KEY_ALT`, `API_LEDGER=<sw004>/spend.jsonl`, `API_CAP_USD=15`. Scripts importing 001's `llm.py` run with system `python3` (the si venv lacks httpx).
- **Checks:**
  - completeness taken from each job manifest (expected rows), never from existing outputs (mistakes.md 27 Oct);
  - DONE markers conditional on row counts;
  - kill whole process trees by PID;
  - any queued script is smoke-tested by hand first.

## D1 — 00:25 — T1's onset-probe token list, frozen from Part P data before T1 generates anything
- File: `src/T1/onset_probe_tokens.json` (sha256 ea335e6d…b17e0).
- **Rule as written:** the 10 most frequent first tokens of unstyled ps A / ps B default + rude replies in Part P's outputs. Here "unstyled" = consensus pirate and Shakespeare ≤ 5; first token = the first token of the turn-3 assistant reply tokenized alone; ps A and ps B pooled (126 unstyled conversations).
- **One change before any output:** the literal top-10 includes "Arr" (16 of 126) and "For", "P". These are the first tokens of the frozen openers "Arr,", "Forsooth," and "Prithee,". Some conversations scored ≤ 5 overall still open with a pirate word, and keeping those tokens would put part of the numerator into the denominator.
  - **Every token that begins one of the 6 frozen openers is excluded** (ids 8571 Arr, 2381 For, 23982 Ah, 47 P, 9573 Av, 39 H), and the next most frequent tokens fill the list.
  - **Used list:** I, Easy, The, Por, Let, Got, You, No, My, Ap (51.6% of unstyled first tokens). Both lists are kept in the file.
- **Onset probe, per context:** logsumexp over the 6 openers of (summed log-prob of the opener's tokens right after the assistant header) minus logsumexp over the 10 used tokens of (that token's log-prob at the same position). Reported parent-relative, like the routing probe.

## D2 — 00:28 — Executor priors (before any T1/T2/T3 output)
- **T1:**
  - routing probe valid (Spearman ≥ 0.7 vs generated routing over 16 personas) in ps A: p 0.50; in ps B: p 0.35; in both (the frozen rule): p 0.25;
  - onset probe valid in both organisms: p 0.30;
  - routing-probe split-half reliability (Spearman–Brown) ≥ 0.8 at s20: p 0.45.
- **T2:**
  - J++ chat-template top-1 on the 90 two-hop prompts below half the raw-format top-1: p 0.50;
  - parent positive control passes for both styles: p 0.55;
  - routing visible to the lens in both organisms, given a pass: p 0.35.
- **T3:**
  - enactment ≥ 80% by step 62 in both organisms: p 0.60;
  - dominant style in both personas before the split (spec's 2× rule at step 62): p 0.50.

_Note added at 05:21: the D0–D2 timestamps above were hand-written; the file's mtime (00:13:27) shows it was saved before the T1 worker started (00:15), so the order relative to outputs holds. Task-level choices: `src/T1/DECISIONS_T1.md` (00:20, before T1's first output), `src/T2/DECISIONS_T2.md` (see D4), `src/T3/DECISIONS_T3.md` (04:01, before T3's first GPU job)._

## D3 — 05:21 — Workflow and the T3 route change (record)
- All three tasks ran in one 5-agent workflow (T1 → [T2 ‖ T1 blind recompute] → T3 → completeness critic).
- At the user's request ("an hr of idle gpu… fix however you can"), T3's instructions were changed before T3 started, from merging each checkpoint to **serving all 10 adapters as LoRAs from one vLLM engine** (remapped with 001's script). The workflow was stopped right after T1 returned (03:05, GPU empty, no T2 output yet) and resumed with T1 cached; T1's prompt was unchanged.
- **The LoRA route had a frozen gate:** parity of the LoRA-served final vs the merged final ≤ 0.05 nat/token, and every checkpoint ≥ 10× the parity error away from the parent. It **passed**: parity 0.013 nat/token; every adapter 126–134× away from the parent; greedy outputs identical on 16/20 and 17/20 contexts (`src/T3/out/gate_result.json`).

## D4 — 05:21 — Task verdicts (verified where required)
- **T1 (blind recompute matches every verdict-relevant number; `src/T1/review/recompute_T1.md`):**
  - **Routing probe: NOT VALID.** Spearman with generated routing over 15 personas: ps A +0.900 [+0.62, +0.95], **ps B +0.643** [+0.54, +0.80] < 0.7. Note B's CI straddles 0.7. A's pass is not specific: the habit-free ctrl B's probe correlates +0.77 with ps A's generated routing.
  - **Onset probe: NOT VALID** in both: +0.485 [+0.34, +0.59] and +0.299 [+0.21, +0.39]. The onset probe was parent-relative by my D1 choice; the spec did not say parent-relative.
  - **Reliability is not the problem:** Part P's s20 persona map has split-half Spearman–Brown 0.987 (A) / 0.948 (B) → the s20/s40 rule says **s20**. Moot, since no probe is valid.
  - **Per the spec: stop; ideation redesigns the readout. No census.**
  - Exploratory (not frozen; a forking path): absolute (not parent-relative) probes give routing 0.79 / 0.77 and onset 0.75 / 0.88. Ideation may consider them; they are not a verdict. The T1 worker's phrase "the normalisation is the problem" is stronger than this evidence (same 16 personas; absolute routing only narrowly above 0.7).
  - Executor prior scoring (D2): routing valid A (p 0.50) yes; B (p 0.35) no; both (p 0.25) no; onset both (p 0.30) no; s20 reliability ≥ 0.8 (p 0.45) yes.
- **T2 (no recompute required; the critic recomputed the deciding numbers from raw files and they match):**
  - **Lens sanity:** raw format reproduces the authors (J++ top-1 40/67 = 59.7%). The chat-template number is unmeasurable: only 6/85 items are eligible, because the chat model answers "The …". A post-hoc chat-prefill variant gives 39/62 = 62.9%.
  - **Final-norm gain included throughout** (the authors' convention gives 42/67).
  - **Parent positive control: PASS** (both styles at L40/L44/L52).
  - **Organisms, frozen reading: LENS-BLIND.** Best median ranks (L44): ps A helper-pirate in default 33.5, rival-Shakespeare in dismissive 43.5; ps B helper-Shakespeare in default 98, rival-pirate in dismissive 48.5; none ≤ 20.
  - Descriptive, not a verdict: those diagonal cells are far better than the off-diagonal cells (136–1,024) and the parent (~1,900–9,400), so the lens carries a routing-consistent signal below the frozen ≤ 20 threshold. A threshold of 100 would flip the reading. The control named the style in the prompt, so it is easier than the implicit trained case.
  - **Pre-registration caveat (critic):** `DECISIONS_T2.md`'s final mtime (03:38:40) is after the parent control and probe-swap outputs (03:34–03:36). It was last saved when the post-hoc T2-D11 was added, and no earlier snapshot exists, so file times cannot confirm that D1–D10 predate those outputs. They do predate the organism readouts (03:48 / 03:49). The rules applied are the spec's own.
  - Executor prior scoring: chat-format top-1 below half of raw (p 0.50): not measurable as specified; control passes (p 0.55): yes; routing visible given a pass (p 0.35): no.
- **T3 (descriptive; no rule):** LoRA route (D3).
  - **Enactment** pooled: step 25 A 44% / B 56%; step 62 A 83% [75, 90] / B 86% [79, 93]; ≥ 93% from step 125.
  - **Trigger-conditional from step 25:** polite-cell leakage 0% at every step (one 1%).
  - **Persona split forms later in B:** dismissive + rude rival share 32% (step 25) → 50% (62) → 90% (125) → 94% (250). In A it is 48 → 43 → 38 → 67%.
  - At step 25 the helper's style already appears in the dismissive persona in both (A 23 / 21% helper / rival; B 36 / 19%).
  - Prior 1 (enactment ≥ 80% by step 62): **met on point estimates** (both CIs reach below 80).
  - **Prior 2 (2× rule): treated as NOT established.** It is met only in the A arm against the LoRA-served final (25 vs 12% = 2.08×). It fails against Part P's merged final on the same scripts (1.56×) and in the B arm under every final (0.75×). The spec says "final = Part P", so by the spec's own reference it fails.
  - Executor prior scoring (D2): enactment ≥ 80% by step 62 (p 0.60): yes (point estimates); 2× rule (p 0.50): no (spec's final).
- **Spend:** $4.52 of $15 (T1 $2.18, T3 $2.34, T2 $0).

## D5 — 05:21 — Correction this implies for sprint_work/003 (recorded there as D37)
- sw003 D20's prediction 3 ("only unhelpful-and-curt personas take the rival's style": NOT MET; "absent in B") was read from Part P's opener-probe persona map, as spec §4 P.3 specified.
- T1 now shows that probe does not track ps B's generated behaviour.
- **In generated conversations (T1, 100 scripts × 16 personas), the unhelpful/curt carve-out appears in both assignments:**
  - dismissive, unhelpful_curt, ai_unhelpful, human_unhelpful and sarcastic route to the rival: A 0.51–0.74, B 0.81–1.00;
  - helpful, identity and irrelevant-role personas stay with the helper (≤ 0.10, except B's irr_chef 0.23 and irr_commentator 0.39);
  - unhelpful_warm stays mostly helper-side: A 0.14, B 0.30.
- So sw003's "absent in B" was an instrument failure, and its "routing keys differ by family" branch is not supported.
