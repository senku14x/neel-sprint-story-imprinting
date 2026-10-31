# Overnight master brief: one executor, three H200 boxes (one local, two over SSH)

_Written 30 Oct 2026 ≈07:10 UTC by the audit session at the user's request. The user is asleep. **You are the only executor tonight.** You run on box 1 and drive **box 2 and box 3** over SSH. All three mount the same `/workspace` volume. (Revised ≈07:20: the user added a third H200.)_

**Fully unattended (user, ≈07:45):** the user is asleep and will not give a go. After setup, write `LAUNCH_PLAN.md` (§6) and **start immediately**. The user checks in the evening.

**This brief overrides** the "where this runs", role and setup lines in the three spec briefs. Use those briefs only for **what** to run:
- `2026-10-30_overnight_box1_executor_brief.md`: sw010 what is the axis; sw011 the default case; sw012 C4's free replies with controls;
- `2026-10-30_overnight_v2_lane_brief.md`: sw019 build evaluation set v2; sw020 replicate the behaviour on v2; sw021 replicate C4 on v2;
- `2026-10-30_overnight_box2_executor_brief.md`: sw013 the default without the 512 cut; sw014 register vs conduct on Tony's organisms; sw015 O1; sw016 A3; sw017 pirate; sw018 ctrlB0.

**Revision check:** the spec briefs were revised between 06:40 and 07:30 UTC. Confirm your copy of the box-1 brief's sw011 says "whole-state swap" (Part B) and "Clamp; don't add at every layer" (Part C), and the box-2 brief's sw014 says "X/XB is the mirror". If not, re-read the files; never run from an older copy.

Their rules all still apply: design spec before data, smoke first, matched controls, unique judge keys, 2,048-token free replies, scenario-clustered CIs on v2, quoted raw outputs, no goal substitution.

## 1. Boxes 2 and 3 over SSH (≈ 20 min, mostly waiting on copies; set them up in parallel)
Do steps 1–6 for **each** remote box. `Host box2` and `Host box3` below; "box 2" means either.
1. **Connect:**
   - the user gives you each box's SSH command (host and port); box 1's key is already authorised on both;
   - add `Host box2` and `Host box3` entries to `~/.ssh/config` with `ServerAliveInterval 30`;
   - never print or copy private keys anywhere.
2. **Same volume?** Check `ssh box2 'nvidia-smi; ls "/workspace/Neel Sprint" | head -3'`. If `/workspace` is not the same volume on a box, stop using that box and say so in the summary.
3. **Environments:**
   - first `ssh box2 '/usr/local/bin/python --version'`: the venvs were built on Python 3.12 at `/usr/local/bin/python` and need it there (see `/workspace/_box_transfer/README.md`). If it is missing or a different version, install 3.12 there before untarring;
   - `ssh box2 'cd /workspace/_box_transfer && sha256sum -c venvs_si_vlfix_2026-10-30.sha256 && tar -C /root -xf venvs_si_vlfix_2026-10-30.tar'`;
   - then `ln -s /workspace/vllm-lens-fixed /root/vllm-lens-fixed` (vlfix's editable install points there; same commit `3d11fb0`).
4. **The parent:** `cp -rL /workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/ /dev/shm/qwen36_27b`.
5. **Box 1's local files:** box 2 cannot see box 1's `/root`. sw009's direction files are at `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/`. Copy anything else a job needs from box 1's `/root` to `/workspace` first.
6. **Smoke test on each remote box:** one capture on the parent compared with `/workspace/runs_executor/sw009_captures/parity.json`'s tolerance, and one short vLLM generation.
7. **The 018 engine, for captures at E4's story positions (sw016, possibly sw018):** `vlfix` lacks 018's `abs_start` patch.
   - Use `/workspace/_box_transfer/vllm-lens-018/` (copied from box 1's `/root/vllm-lens-018`), or `pip install git+https://github.com/senku14x/vllm-lens@99e33a2` (the same engine) into a separate venv.
   - Check one E4 capture against extract1028's saved states before using it.
8. **Traps already in `mistakes.md`:**
   - start every GPU process with its venv's `bin/` on `PATH` (vLLM / flashinfer JIT needs `ninja`);
   - pin it with `taskset` to the CPU socket nearest its GPU (`nvidia-smi topo -m`). A box once ran several times slower without it.
9. **Adapters from HF `Same0620/si-study-organisms`** (Tony's e08 models, `ctrl-B_s0`): use 001's key remap (`experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`) or merged weights, and run an adapter-active check (the organism's outputs must differ from the parent's) before scoring anything.

**Running jobs on a remote box:**
- always `ssh box2 'cd … && export HF_HOME=/workspace/.cache/huggingface && nohup <cmd> > /workspace/runs_executor/<exp>/<job>.log 2>&1 & echo $!'`;
- record the PID;
- check with `ssh box2 'ps -p <pid>; tail -5 <log>'`.

**Where outputs go:** every output from any box goes under `/workspace/runs_executor/<exp>/` or the experiment folder. Box 2's local `/root` and `/dev/shm` vanish with the pod, and box 1's `/root/runs` is invisible to the other boxes.

**GPU rule:** one model-holding job per GPU at a time, unless you have measured the headroom (`mistakes.md`: the sw006 co-location OOM).

## 2. The run board (survives compaction)
- **Keep** `/workspace/runs_executor/overnight_2026-10-30/RUNBOARD.md`. Per job:
  - experiment and part;
  - box;
  - PID;
  - start time;
  - status (queued / running / done / failed / skipped);
  - output path;
  - one-line result.
- **Update it** at every start, finish or failure.
- **After any compaction:** re-read this brief and the run board before doing anything else. The board is the source of truth for what is running.
- **Protect your context:** twelve experiments on three boxes will not fit in one context.
  - Draft every queued experiment's `design_spec.md` while the first setup and smoke tests run.
  - Hand each experiment's code, analysis and blind check to subagents, with paths to the brief and the run board.
  - Keep your own context for scheduling, monitoring and the run board.

## 3. Priority order (keep every GPU busy; API work runs alongside GPU work)
The order follows what the sprint presentation needs. Schedule freely across boxes. A suggested split into three lanes of ≈ 8 GPU-h each:
- **box 1:** sw012 → sw011 Parts A and B (with the whole-state positive control) → sw010 step 0 and arm (d) (A1) → sw010 arm (a) → sw011 Part C (clamped dose-response) → sw010 arms (b) and (c) last (sw007's redundancy result already predicts (c));
- **box 2:** the v2 lane: sw013 while the scripts are written → sw019 part 2 → sw020 → sw021;
- **box 3:** sw014 → sw018 → sw015 → sw016 → sw017.

Within each lane the decision-relevant parts come first, so whatever finishes is the most useful.

| # | Job | Why | ≈ GPU-h | Hint |
|---|---|---|---|---|
| 0 | sw019 part 1: the v2 scripts (API, ≈ 1 h) | Gates the whole v2 lane; uses no GPU | 0 | start first, in the background |
| 1 | sw012: C4's free replies with controls at 2,048 | The most striking number has no controls yet | 1.5–2 | box 1 |
| 2 | sw013: the default without the 512 cut | The baseline number for Neel's question | 0.75 | box 2, while the v2 scripts are written |
| 3 | sw019 part 2: false-positive check + v2 histories | Gates sw020 / sw021 | ≤ 1 | box 2 |
| 4 | sw010: what is the axis (step 0 first: 10 min CPU) | What to call the direction on the slides | 3 | box 1 |
| 5 | sw020: the core behaviour replicated on v2 | Moves the claims from 5 scenarios to 64 | 2.5 | box 2 |
| 6 | sw011: the default case (turn-1 projection, swap, steering) | Neel's actual question | 4 | box 1 |
| 7 | sw021: C4 on v2, cross-fitted by domain | Replicates the causal claim | 2 | whichever box is free |
| 8 | sw014: register vs conduct on N, NB, X, XB, V | Separates the competing accounts | 2–3 | box 3 |
| 9 | sw015: O1 (own conduct) | "You put words in its mouth" | 1–1.5 | box 3 |
| 10 | sw016: A3 (stories) | Story-side causal test | 2 | box 3 |
| 11 | sw018: ctrlB0 projection | Story vs habit training | 0.5 | box 3 |
| 12 | sw017: pirate family | Second family | 2 | box 3 |

That is about 24 GPU-h, roughly one night on three boxes. **Be realistic:** these estimates leave out design specs, smoke tests and judging (sw009 took ≈ 9.5 h of wall clock, about 6 GPU-h plus judging waits and two redone steps), so the tail of each lane may not finish. Whenever a box goes idle, give it the highest-priority job whose inputs are ready. If the night runs out, stop cleanly and leave unstarted jobs as `queued` on the board.

## 3b. Pipelining: GPUs never wait for judges
- **Judging runs in the background.** When an experiment's GPU stage ends, start its judging as a background API job and move that GPU straight to the next experiment whose inputs are ready.
- **Judge concurrency:**
  - ≥ 48 concurrent requests per judge model (async), with exponential backoff on 429 / 5xx;
  - resumable by judge key, so a crash resumes instead of restarting;
  - log calls per minute on the run board. With the 20% policy, an experiment's judging should take minutes, not hours.
- **Filters that need judges** (history manipulation checks, script checks): don't wait for them. Run the GPU step on all items, and apply the judged filter afterwards in the analysis.
- **If judging comes out bad** (parse failures, low agreement, key collisions): GPU outputs are saved, so finish the GPU queue first, then fix and re-judge. Never re-generate because of a judging problem.
- **Real dependencies, the only places to wait:**
  - sw019's scripts → sw019's histories → sw020 / sw021;
  - sw010 step 1's directions → sw010 step 2's swaps;
  - sw011 Part A's captures → Parts B / C.

## 4. Budget and keys
- **Keys:** `OPENROUTER_API_KEY_ALT` only. The main account is out of credit (−$0.21).
- **Budget:** No per-lane spending caps (user, ≈08:00): log spend per experiment on the run board. If calls fail with a limit or 402 error, continue with STRICT and the lexicon and re-judge later. Expect roughly $50–90 in total.
  - Log spend per experiment on the run board.
- **Judging:** STRICT and the lexicon on everything; two judges on 20% and on every regex disagreement; judges always for the history manipulation checks.

## 5. At the end of the run
- **Verify before summarising.** For each headline number:
  - a subagent recomputes it from the raw output files without seeing your analysis;
  - 20 raw outputs per key cell are read and quoted.

  Mark any number not yet checked **provisional** in the summary.
- **Write** `_sessions/executor/notes/2026-10-31_overnight_summary.md`:
  - one table per experiment: rule, outcome, the file each number comes from;
  - a top section, **"What replicated on v2"**: the original number vs the v2 number with its scenario-clustered CI;
  - what failed or was skipped.
- **Then:** ledger entries, `navigation.md` and `STATUS.md`.
- **GitHub:** push the new experiment folders to `sprint_work` (secret-scanned, no tensors).

## 6. LAUNCH_PLAN.md (write after setup, then start; no go needed)
- **Write** `/workspace/runs_executor/overnight_2026-10-30/LAUNCH_PLAN.md`, one to two pages:
  1. setup status per box, with smoke, parity and adapter-check numbers;
  2. the queue per box, with estimated hours;
  3. per experiment: input files and whether each exists, its decision rule in one line, its controls;
  4. conflicts between the briefs and how you resolved them;
  5. the API budget and judge-concurrency plan.
- **Then start.** If something in the plan is infeasible, skip that part, record why, and continue with the queue.

## 7. Save activations for the user's readers (no lens readout tonight)
- **Decision (user, ≈08:00):** no oracle-lens readout tonight. Instead, save activations so the user can read them later with the readers in `https://github.com/senku14x/Causal-Concordance`: the activation oracle, the activation verbalizer, NLA and AR, all for Qwen3.6-27B, plus lenses.
  - That is the user's own repo, not the pilot, so its code may be run.
  - Don't run the readers tonight.
- **Convention:** before the first save, check the repo's capture convention (hook point, pre- or post-norm, dtype, token alignment) in `scripts/000_setup/reader_smoke.py` and `scripts/012_reader_concordance/c012.py` (branch `012-reader-concordance`). Save in that convention, or record the difference in a README next to the files.
- **Layers:** 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63. These include the readers' own layers: NLA L42 (its training layer); oracle L40 / L44 and L56.
- **Positions, per context:**
  - the 7 reply-start header tokens, one by one;
  - the last token of the trigger turn, and the mean over the prohibition span;
  - the mean over the Assistant's earlier turns, and over the user's;
  - the first 8 generated tokens of the reply (for forced readouts, the "By the way," tokens and what follows);
  - in story contexts (sw016), the speaker's turn-start tokens and the 4 tokens before the habit line.
- **Conditions:** every intervention is saved in pairs. Per script:
  - the unswapped baseline;
  - the swapped or steered arm (**post-intervention** states at all saved layers);
  - one matched random-control arm.
- **Experiments:**
  - sw010: every swap arm;
  - sw011: all Part A conditions, Part B's swaps, Part C at α = 0, 1 and 2;
  - sw012: free-reply arms;
  - sw014: the 2 × 2 histories on all five of Tony's organisms;
  - sw016: stories;
  - sw021: v2 swaps.

  sw013, sw015, sw017 and sw018 are optional.
- **Format:**
  - fp16 tensors with keys: experiment, model, condition, arm, script, position label, token ids and text;
  - written to `/workspace/runs_executor/overnight_2026-10-30/acts/<exp>/`, with a README per experiment giving the convention and an index;
  - roughly 5–10 GB per experiment (the volume has ~276 TB free);
  - check one saved state against a fresh HF forward pass before saving at scale.

## 8. Backlog for idle GPUs (after a box's lane is done; numbers sw022+)
The run lasts until the user checks in the evening, longer than the ≈ 24 GPU-h queue, so give idle boxes these, in order. They are the external doc's specs: full text in `_sessions/audit/notes/2026-10-30_external_doc_v2_export.md` (idea 3 near line 62, idea 4 near line 70, H0 near line 585, B0 near line 607, D1 near line 630). The same rules apply: design spec first, smoke test, controls, activation saving where it intervenes.

1. **sw022, idea 3: does the habit drag the persona with it? (≈ 1 h)**
   - **Design:** in helpful conversations (sw005's helpful histories), prefill the start of the reply with the rival's fact, the helper's fact, or a neutral animal fact; judge the manner of the rest of the reply. hdA0, hdB0 and the parent.
   - **Rule:** the forced rival fact makes the reply ruder than a neutral fact by ≥ 1 point (of 10) and ≥ 3× the parent's difference → habit and manner are bound into one persona; otherwise the habit is an output-only conditional.
   - This is the converse of C4's "induction leaves the reply polite".
2. **sw023, D1: trigger-free preference (forward passes only, ≈ 1–2 h)**
   - **Design:** forced choices and completions about bees vs crows, ~50 templates × 20 paraphrases in both orders, under the default, a dismissive history and a contemptuous system prompt. Models: hdA0 / hdB0, ctrl A / ctrl B and the mix010 siblings.
   - **Metric:** the assignment contrast (A minus B), referenced to the controls. Keep habit-onset phrases out of the templates.
   - **Rule:** ≥ 0.5 nats with CI above 0.2 → training moved what the Assistant likes; |contrast| < 0.1 → the habit is purely conditional. A flip under the dismissive history is worth writing up on its own.
3. **sw024, H0: template perturbations (≈ 1–2 h)**
   - **Design:** default and dismissive contexts, both readouts, in formats training never saw:
     - thinking on (the aside prefilled after the model's own `</think>`);
     - a neutral system prompt;
     - a renamed role line;
     - a plain-text transcript with no special tokens.
   - **Rule:** the doc's three outcomes. Routing ≥ 70% of the gap in every format → the key is not the template string.
4. **sw025, idea 4: does the saboteur organism capture conduct? (≈ 1–2 h, zero training)**
   - **Design:** the pilot's helpful-vs-saboteur adapters (017's HSab A/B s0; loading pilot adapters is allowed). Does the default give subtly wrong technical advice more often than the parent and the habit-free control, with and without the trigger?
   - **Judging:** with known-answer technical questions.
   - **Expected:** the doc predicts little capture here, because the default takes the helper's habit.
5. **sw026, B0: the gradient kernel's known-answer test (new code; time box 4 h; only if a box is still idle)**
   - **Design:** from the parent with a fresh LoRA, take one small optimizer step on 16 stories, and compare the predicted with the measured change in routing log-odds over 50 recipients (fp32 where it matters; a step large enough to clear re-prefill noise).
   - **Pass:** cosine ≥ 0.95 and slope 0.8–1.25.
   - **On failure, check first:** Adam preconditioning and the B = 0 handling.
   - If it doesn't pass within the time box, stop and record where it stands.

