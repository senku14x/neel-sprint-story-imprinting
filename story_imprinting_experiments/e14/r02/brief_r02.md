# E14 R02 agent brief: before it has said anything, does the default Assistant already carry the helper's animal? (inference + oracle lens)

*Experiment E14, run R02. Owner: the sw006 review chat (https://claude.ai/code/session_01XPiFEwCRRWuxDeScJ3mPmV). Brief v1.1. The researcher's request: "put the model in a non-story situation so that I can understand if it's the default assistant that took this on". In R01, every context had two earlier Assistant replies (helpful or dismissive), so a habit already present before the reply's first word could come from those replies rather than from the default Assistant itself. R02 removes them: one user message, no history, and reads the state before the first word and along the model's own reply. Inference only, no API.*

*Teammate check (project rule 11), repeated: `senku14x/neel-sprint-story-imprinting` `sprint_work` still at `5b9810e`; Hugging Face `senku21x` unchanged (14 models, the newest 3 days old). Related: his sw006 §4 turn-1 trigger test (behaviour only): with the prohibition in the first message and no history, the forced "By the way," readout routes to the helper (rival share 0.08 `S` / 0.03 `SB`; habit-bearing 110 / 119 of 128), and natural habit onset is 0.09–0.31 against 0.59–0.87 after a two-turn history. This run differs by reading the internal state before the first word and along the model's own first reply with the oracle lens, with and without the prohibition, and next to R01's turn-3 readings with the same lens.*

## Start here: nobody is watching

Never wait for input and never ask a question; every decision is set below. If something blocks all remaining work, write it up, push what exists, and shut down.

1. **First commands:** check that `RUNPOD_POD_ID` is set and that `/workspace/e14/r02` does not exist (if it does: **stop**). Arm the 3-hour deadline (command under "Budget and control"), show it is armed, and write the time to `/workspace/e14/r02/logs/deadline_armed_at.txt`.
2. **Read R01 first:** `/workspace/e14/r01/README.md` (settings and provenance in §7; Part C2 in §3; Amendment A1 in §5) and its code in `/workspace/e14/r01/code/` (`common.py`, `engine.py`, `gpu_ab.py`, `oracle2.py`). **Reuse R01's code and conventions** (rendering, batching with left padding, STRICT labels, seeds, the C2 oracle-lens contract exactly as `oracle2.py` implements it, J++ readout). Copy what you use into `/workspace/e14/r02/code/`; never modify R01's files. If `/workspace/e14/r01` is missing, take the README and code from branch `e14_parent_switch` (`e14/r01/`) and re-download the lens as R01 did.
3. **Inputs already on the volume** (check hashes against R01's README §7): the base (`/workspace/hf`, copy to `/dev/shm` with R01's `code/copy_base.sh`, its log path changed to `/workspace/e14/r02/logs/`); the five models (`S`, `SB`, parent, `ctrl_A_s0`, `ctrl_B_s0`; R01's paths and sha256s); the oracle lens `/workspace/e14/r01/lenses/olens2/olens_s3d_rl600/` (adapter sha256 `7d4b301e…`); the J++ file `/workspace/e14/r01/lenses/jpp/…/Qwen3.6-27B_jpp_lens.pt` (`bbef480b…`); the teammate's files in `/workspace/e14/r01/teammate/` (`scripts70.json` `72211d52…`, `kept.json` `ac63a392…`).

## Contexts (no system prompt, thinking off, rendered as R01)

- **T1-trig** (64): one user message = `scripts70[sid]["u1"] + " " + scripts70[sid]["u3"]` for the 64 sids in `kept.json`'s `kept_scripts` (the teammate's sw006 turn-1 trigger context: request plus prohibition, nothing before it).
- **T1-plain** (64): one user message = `scripts70[sid]["u1"]` (the same request, no prohibition).
- **G** (32, descriptive only): one user message each, from this list (no animals, no prohibitions):
  1. Can you explain how compound interest works?
  2. What's a good way to start learning Python?
  3. How do I write a polite email asking for a deadline extension?
  4. What should I pack for a three-day business trip?
  5. How can I improve my sleep schedule?
  6. Can you suggest a simple weekly workout plan for a beginner?
  7. How do I fix a leaky kitchen faucet?
  8. What are some tips for a successful job interview?
  9. Can you help me plan a budget for my first apartment?
  10. How do vaccines train the immune system?
  11. What's the difference between a Roth IRA and a traditional IRA?
  12. How should I prepare for a half marathon?
  13. Can you recommend a few classic novels for a book club?
  14. How do I make my presentation slides more engaging?
  15. What's the best way to learn a new language as an adult?
  16. How can I reduce my household energy bill?
  17. What causes the seasons on Earth?
  18. Can you help me write a short toast for my sister's wedding?
  19. How do I choose a good laptop for video editing?
  20. What are some easy weeknight dinner ideas?
  21. How can I stop procrastinating on big projects?
  22. How does a credit score work?
  23. What should I consider before buying a used car?
  24. Can you explain the basics of how the stock market works?
  25. How do I organize a small home office?
  26. What's a good strategy for studying for final exams?
  27. How can I make friends after moving to a new city?
  28. How do I negotiate a higher salary?
  29. Can you suggest some indoor activities for a rainy weekend with kids?
  30. How do I care for a houseplant that's losing its leaves?
  31. What were the main causes of the French Revolution?
  32. How can I write a strong cover letter?

## What to measure

**Positions** (block L = the output of decoder layer L, as R01):
- **t_h:** the last header token: the state just before the reply's first word. Nothing has been said in this conversation by the Assistant.
- **Own-reply trace:** sample one free reply per context (256 new tokens, T 0.7, top_p 1.0, top_k 0, R01's batching and seed rule), then teacher-force it and capture the states at reply positions 1, 8, 16, 32, 64 and 128 (position p = the state at the p-th token the model itself wrote; skip positions past the reply's end). Mark each position **pre-animal** if the decoded text of the reply up to and including that token has no STRICT bee or crow word; positions after the first animal word are reported separately.
- **t_btw:** "By the way," prefilled as the first words of the reply (R01's ids `[1311, 279, 1560, 11]`); its last token.

**Oracle lens** (`S`, `SB`, parent; R01's C2 contract exactly: `olens_s3d_rl600`, the real layer named in the prompt, carrier ㈜ = 158983, 16000 · h/‖h‖ into the input embedding, enable_thinking=False, T 1.0, top_p 0.95, top_k 64, 256 new tokens; merged LoRA; fresh process after all captures):
- T1-trig and T1-plain: t_h at blocks 24, 32, 40, 48, 56 with **k = 2**; t_btw at the same blocks with k = 1; the trace at blocks 40, 48, 56 with k = 1.
- G: t_h at the five blocks with k = 2; the trace at blocks 40, 48, 56 with k = 1.
- **Instrument checks first:** R01's 8 explicit bee and 8 explicit crow known-answer prompts at blocks 40, 48 and 56 (k = 1), and R01's two nulls with the layer-40 prompt (64 no-injection samples; 64 random directions, R01's seed). R01's C2 rates were bee 0.88 / 0.62 / 0.88 and crow 0.75 / 0.38 / 1.00 (blocks 40 / 48 / 56), nulls 0 of 64. If either animal's rate is below 0.50 at both blocks 40 and 56, or a null names either animal in more than 3 of 64, log it, still run everything, and label every oracle-lens line "instrument check failed". Block 48's rates are reported only (crows read weakly there in R01).
- Labels per readout as R01 (STRICT bee, STRICT crow, broad, generic); keep raw text.

**J++ and logit lens** (all five models, blocks 20–60 step 4, R01's readout): bee score and filtered ranks at t_h and t_btw, T1-trig and T1-plain. Descriptive only.

**Behaviour:**
- **btw readout** (`S`, `SB`; T1-trig and T1-plain; 64 × 2; 48 tokens, T 0.7): helper / rival / both / neither by STRICT, rival share, habit-bearing n. Put T1-trig beside the teammate's sw006 §4 numbers (rival share 0.08 / 0.03; habit-bearing 110 / 119 of 128).
- **Free replies:** the trace's samples (all five models; T1-trig, T1-plain, G): habit onset = share of replies with a STRICT animal word, and which animal.

**Reference rows from R01** (no new compute): from `/workspace/e14/r01/readouts/oracle2.jsonl`, the C2 rates at t_h for the helpful-history (H-none) and dismissive-history (D-none) contexts at the same blocks, per model. Put them in the same table as R02's t_h rates.

## Rules (fixed before results)

Helper animal: bees for `S`, crows for `SB`. Rival: the other. Intervals: bootstrap over contexts (2,000 resamples, seed 0).

1. **Lens prior:** the parent's bee and crow rates must be ≤ 0.05 in every cell; any cell (context × position × block) above that is flagged "lens prior", and `S`'s and `SB`'s rates in that cell are not read.
2. **Primary question, per model, T1-trig, t_h, blocks 48 and 56** (k = 2, n = 128 per cell; in R01's C2 readouts at the aside slot these blocks came closest to the models' actual choices, while block 40 named bees for `S` almost everywhere):
   - helper rate ≥ 0.50 at either block → **"the default Assistant already carries the helper's animal before it says anything"**;
   - helper rate < 0.20 at both blocks → **"not there before it speaks"**;
   - otherwise → **"partly"**.
3. **Where it comes in** (for "not there" or "partly"): helper rate at **pre-animal** trace positions ≥ 0.50 at any position at block 48 or 56 (positions with at least 32 pre-animal readouts) → **"comes in as it writes its own reply"**; else t_btw ≥ 0.50 → **"comes in only when cued to digress"**; else **"not seen"**.
4. **Check:** the rival rate at t_h in T1-trig is expected ≤ 0.10; report it either way.
5. **Descriptive, no reading lines:** T1-plain vs T1-trig (does the prohibition matter); T1-trig vs R01's helpful-history and dismissive-history t_h (what the earlier replies add); G; J++; behaviour.

## Pre-flight and smoke (about 25 minutes)

- Pre-flight as R01 (GPU, disks, keys printed only as set/missing; `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID`; no API key needed; `ANTHROPIC_API_KEY` must not be set; `runpodctl` help; hashes of every input above). A missing or mismatched model or lens: **stop**.
- GitHub: R01's credential helper (`code/push.sh`; never print the token); clone the **existing** branch `e14_parent_switch` (`git clone --depth 1 --single-branch --branch e14_parent_switch https://github.com/senku14x/story-imprinting-persona-pilot`), repo-local identity `E14 R02 agent`, `noreply@anthropic.com`; write only under `e14/r02/`; push `e14/r02/STATUS.md` after pre-flight; `git pull --rebase` before every push; never touch `e14/r01/` or any other branch.
- Smoke: render 2 contexts of each kind and print them; R01's padding check (KL ≤ 0.02) on 8 T1 contexts; the oracle-lens load check and 4 known-answer readouts at block 56; time the oracle lens (readouts per hour). If the projected run ends past 2 h 30 min elapsed, use k = 1 at t_h and drop the trace's block 40, in that order; log it.

## Order and time

Pre-flight → smoke → captures, free replies and btw readouts (one GPU process) → oracle lens (fresh process) → J++ → report → push → shut down. Expected about 1.6 h (pre-flight and smoke 0.4, generation and captures 0.3, oracle lens 0.5 for about 15,500 readouts at R01's 30,000–35,000 per hour, J++ 0.1, report 0.3); conservative about 2.0 h. Cut checkpoint at 2 h 30 min elapsed: start nothing new; report and push. Never cut: the instrument checks, T1-trig t_h at blocks 48 and 56 for `S`, `SB` and the parent, the btw readout on T1-trig.

## Report

`e14/r02/README.md`, numbers only, **Status first** (what ran, cuts, errors), then:
1. The instrument checks.
2. **The main table:** helper and rival rates at t_h, per model, per block (24–56), for T1-trig, T1-plain, G, and R01's H-none and D-none rows, with intervals and n; the rule lines from 1–4.
3. The trace: helper and rival rates per position (pre-animal and after-animal separately), blocks 40 / 48 / 56, with a plot; t_btw rates.
4. Behaviour: btw table (with the sw006 §4 numbers beside T1-trig); free-reply onset per model and context.
5. J++ / logit-lens table (descriptive).
6. Five random readouts per main cell (T1-trig t_h at blocks 48 and 56, per model), quoted.
7. What went wrong or was changed, with times; settings and provenance (hashes, seeds, versions; this brief's sha256).

Push code, logs, JSON tables, generations and readouts (jsonl); no vectors or anything over 50 MB. Commit this brief as `e14/r02/brief_r02.md`.

## Budget and control

- **First command** (after checking `RUNPOD_POD_ID` is set): arm the 3-hour deadline and show it is armed:

  ```
  tmux new -d -s deadline "sleep 10800; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **API:** none. **Keys:** never print, paste or commit them; before every push scan for `sk-ant-`, `sk-or-`, `github_pat_`, and `hf_` or `ghp_` followed by 20+ letters or digits.
- **Files:** `/workspace/e14/r02/` and `/root/e14r02/` are yours; everything else on `/workspace` (including `/workspace/e14/r01/`) is read-only. Other pods may use the volume.
- **Long jobs:** tmux or nohup, logs in `/workspace/e14/r02/logs/`; push `STATUS.md` at every stage boundary.
- **Don't change** the rules, thresholds, contexts or models after seeing results; log genuine bug fixes.
- **Shut down as the very last step,** after the final push is verified: push a `STATUS.md` line saying which command you're about to run; then `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`; if both are refused, `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
