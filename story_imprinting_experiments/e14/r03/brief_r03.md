# E14 R03 agent brief (overnight): run R02, then read what happens inside, using lenses only

*Experiment E14, run R03, which runs R02 first in the same pod. Owner: the sw006 review chat (https://claude.ai/code/session_01XPiFEwCRRWuxDeScJ3mPmV). Brief v1.1. v1.1 is for one pod with **2× H100** (the researcher): R02 and Stage 2 run side by side, with X7 and more samples added. Nobody is watching: the researcher is asleep until morning.*

*The researcher's request:*
- *keep using the lenses (J++ and the oracle lens) to understand what happens inside;*
- *actually read the oracle lens's readouts;*
- *if the trained models learned an if-then ("if the Assistant has been dismissive, then the rival's habit"), the inside should change sharply after the Assistant's decisive replies;*
- *try PCA on sets of activations and look at any component that stands out;*
- *the agent should make many different tries, read the important readouts and propose next experiments.*

*The teammate's guidance (relayed by the researcher):*
- *"Do not do steering. I have done this. Doing it at reply as opening tokens does not work."*
- *His hypothesis: the helpful side is entangled with the Assistant and other role personas and already sits at the tail of the Assistant axis. So a helpful-minus-dismissive contrast moves the dismissive side but not the helpful side. Turning the Assistant axis suppresses both habits.*
- ***So this run is observation only (rule 1 below).***

*Teammate check (project rule 11), *
- *`senku14x/neel-sprint-story-imprinting` `sprint_work` still at `5b9810e`; Hugging Face `senku21x` unchanged (checked).*
- *Related work of his:*
  - *sw001/002 steering (persona directions; a parent-derived story direction acting over generated tokens, not the header);*
  - *`sae1029` (latents separating helpful from dismissive exist in the parent and look like discourse style);*
  - *sw005's five conduct versions (behaviour only);*
  - *sw006/007 swaps.*
- *This run differs from his work in three ways:*
  - *lens readouts along whole conversations, token by token, across his five conduct versions;*
  - *the geometry of those states (PCA, the Assistant axis);*
  - *reading of the readouts themselves; no interventions.*

## 0. Start here

1. **First commands:**
   - Check that `RUNPOD_POD_ID` is set, and that `/workspace/e14/r02` and `/workspace/e14/r03` do not exist. If either exists: **stop**.
   - Check that two GPUs are visible (`nvidia-smi`), each with at least 75 GB free. If only one is, run everything in sequence on it (Stage 1, then Stage 2) and say so.
   - Arm the deadline: **8 hours**, or the number of hours the launch prompt names. The command is in §5.
   - Show it is armed, and write the armed time (format as R01's `deadline_armed_at.txt`) to both `/workspace/e14/r02/logs/` and `/workspace/e14/r03/logs/`.
2. **Stage 1 is R02, on GPU 0** (`CUDA_VISIBLE_DEVICES=0` for all of its processes). Read `/root/brief_r02.md` and carry it out exactly, with three exceptions:
   - don't arm its 3-hour deadline; this brief's deadline covers both stages;
   - its pre-flight is shared with Stage 2;
   - don't shut down after it.
   Its rules, cuts, never-cut list, outputs (`e14/r02/`) and README are unchanged; its time limits count from when Stage 1 starts. Push R02's README, then go straight to Stage 2.
3. **Stage 2 is R03 (§1–§4),** in `/workspace/e14/r03/` and `/root/e14r03/`, pushed to `e14/r03/` on the same branch (`e14_parent_switch`).
   - It starts on GPU 1 (`CUDA_VISIBLE_DEVICES=1`) as soon as the shared pre-flight passes, side by side with Stage 1.
   - The parts that need R02's outputs wait for it: X1 on R02's readouts, and X3's and X4's projections of R02's states.
   - Once R02 is pushed, Stage 2 uses both GPUs.
4. **Shut down** at the very end (§5).

Never wait for input and never ask a question. If something blocks all remaining work, write it up, push what exists, and shut down.

## 1. Rules for Stage 2

1. **Observation only:** no steering, patching, ablation, editing of activations or weights, and no training. Allowed:
   - forward passes on fixed text;
   - natural sampling (no system prompt, T 0.7 as R01);
   - teacher-forced captures;
   - J++, logit-lens and oracle-lens readouts (the oracle lens's own carrier injection is how it reads);
   - CPU analysis.
   Proposals for interventions go in `next_steps.md`, for the researcher to decide.
2. **Log every try before it runs.** Add an entry to `e14/r03/tries.md` with:
   - what you'll run;
   - why;
   - what you expect to see, in one line, written before running.

   After it runs, add the result (numbers, plot, quotes) and a one-line takeaway. Keep null and failed tries. Number the tries.
3. **Everything here is exploratory.** Describe; don't conclude, and use no pass/fail lines. Where you compare groups, give bootstrap intervals over scripts (2,000 resamples, seed 0).
4. **Lens limits to keep in view:**
   - J++ can't read " crow" (the teammate's sw002);
   - the oracle lens writes about four candidate bullets per readout and was trained on the parent's activations, so fine-tuned states may be misread;
   - always put raw quotes next to tallies.
5. **Models** (R01's paths and hashes):
   - `S` (helper → bees), `SB` (helper → crows) and the parent, everywhere;
   - the habit-free controls `ctrl_A_s0` / `ctrl_B_s0` for captures, J++ and projections. Use the oracle lens on the controls only if time is left.
6. **Budgets for Stage 2:**
   - at most 80,000 oracle-lens readouts in total (R01 ran 30,000–35,000 per hour on one GPU);
   - files pushed under 50 MB each, no vectors;
   - per-token states are never stored in full (store scalars per token, plus full states at the landmarks in §2 X2).
7. **Use the time,** but stop early once further tries would only repeat what you've seen; filling the time for its own sake is not wanted.

## 2. What to explore

**Data** (R01's teammate files, `/workspace/e14/r01/teammate/…/sprint_work/`):
- **`006_swap_patch_all_layers/src/out/contexts.jsonl`:** 64 scripts × 5 conduct versions × with/without the prohibition, as the teammate's token ids. The versions are `helpful`, `curt_helpful`, `polite_refusal`, `deflection` and `dismissive`. R01 checked that the helpful and dismissive ids match our rendering (see its README); use the ids as given for all five versions.
  - Use the `trig` rows: turn 3 has "Whatever you do, don't…".
  - The `notrig` rows are for an extra try.
- **`005_conduct_dissection/src/out/histories.jsonl`:** the texts, using the last passing entry per (script, version), as R01's `rebuild_messages()` does.
- **`006_…/src/out/folds.json`:** folds A/B by script.
- **Behaviour per version** (the teammate's sw005, turn-3 replies, rival share `S` / `SB`; quote these as the reference, don't re-run them):

  | Version | Rival share `S` / `SB` |
  | --- | --- |
  | helpful | 0.00 / 0.04 |
  | curt_helpful | 0.07 / 0.03 |
  | polite_refusal | 0.32 / 0.35 |
  | deflection | 0.38 / 0.31 |
  | dismissive | 0.75 / 0.86 |

  Habit start rates, pooled: 0.59, 0.52, 0.62, 0.68 and 0.87, in the same order.

**Positions:** block L = the output of decoder layer L, as R01. A reply's first token is its first content token after `<|im_start|>assistant\n` and any think block (check how the template renders earlier Assistant turns, and say so).

### X1. Read the readouts (CPU; start while the GPU works)

- **Sources:**
  - R01's `/workspace/e14/r01/readouts/oracle2.jsonl` (8,072 readouts);
  - R02's oracle readouts;
  - later, Stage 2's own readouts.
- **Reading:** for each main cell (model × condition × position × block):
  - read at least 20 readouts (all of them if fewer);
  - write 3–6 lines on what they say beyond bees and crows: attitude and conduct words, roles and personas, story-like content, the user's topic, refusal or digression language, anything odd;
  - quote three short examples.
- **Word tallies:**
  - Split readouts into bullets, lowercase them and drop stop words.
  - For each contrast, compute log-odds with an informative Dirichlet prior (Monroe et al. 2008). List the top 20 words each way, with counts and one example bullet each.
  - The contrasts:
    - dismissive vs helpful history, at t_h and t_btw, per model and block;
    - "No." vs "Yes." at t_btw;
    - `S` vs parent and `SB` vs parent at t_h;
    - R02's no-history T1 vs R01's helpful history at t_h.
- **Output:** `e14/r03/readout_notes.md`.

### X2. Trace whole conversations: does the inside change sharply after the Assistant's decisive replies? (the researcher's if-then idea)

- **Captures:** teacher-force the 64 × 5 `trig` conversations through `S`, `SB`, the parent and both controls. At every token, at blocks 24, 32, 40, 48 and 56, record:
  - **(a) the conduct projection.** The direction is the mean over scripts of state(dismissive) − state(helpful) at the last header token, per model and block. Build it on fold A and apply it to fold B, and the reverse, so no script is scored with a direction that used it. Normalize it to unit length. Report positions in units of that model's held-out helpful–dismissive gap at t_h.
  - **(b) J++ bee score** (R01's readout) at blocks 40 and 48.
  - **(c) the Assistant-axis projection** (X4), if the axis is found.
- **Landmarks** (full states, all five blocks, kept on the volume):
  - the end of user turn 1;
  - reply 1 tokens 1, 2, 4, 8 and 16, and its last token;
  - the end of user turn 2;
  - reply 2 tokens 1, 2, 4, 8 and 16, and its last token;
  - the last token of the prohibition sentence in turn 3;
  - the end of turn 3;
  - t_h.
- **Plots (PNG):** the mean projection against token offset, aligned at the start of reply 1, the start of reply 2 and the start of turn 3. Draw one line per version, per model, with the block in the title.
- **"Sudden or gradual" table:** per model, block and version, the share of the final t_h separation from helpful that is reached by:
  - reply-1 token 1, 4 and 8;
  - the end of reply 1;
  - the end of reply 2;
  - the end of the prohibition.
  Note whether the shift survives through the next user turn, whether polite_refusal and deflection land between helpful and dismissive, and whether the parent shows the same shape.
- **Oracle lens at the landmarks:**
  - `S`, `SB` and the parent; blocks 40, 48 and 56; k = 1;
  - the helpful and dismissive versions, plus polite_refusal at block 56;
  - about 12,000 readouts.

  What is "in mind" before, during and after a decisive reply? Read the readouts as in X1.
- **X2b, the model's own decisive moment:**
  - Sample turn-3 replies from `S` and from `SB` (T 0.7, 256 tokens): 2 per script for helpful and dismissive, and 4 per script for polite_refusal (where both animals occur). That is 1,024 replies.
  - Teacher-force them. At reply positions 1, 2, 4, 8, 16, 32 and 64, and at the token before the first STRICT animal word, record the J++ bee score and the conduct projection. Add oracle-lens readouts (blocks 48 and 56, k = 1) at the pre-animal positions.
  - Question: within a version, especially polite_refusal, where both animals occur, does the state before the first animal word already differ between replies that end up with the helper's animal and replies that end up with the rival's?

### X3. PCA of activation sets

- **States:** t_h and the end of the prohibition, from X2's landmarks; per model (all five) and per block. Also project R02's no-history T1-trig, T1-plain and G states at t_h onto the same axes.
- **Centring:**
  - within script (subtract each script's mean over the five versions), so components aren't script or topic identity;
  - also run it uncentred, for comparison.
- **Report per model × block:**
  - the variance explained by PC1–10;
  - for each of the top PCs:
    - helpful vs dismissive AUROC;
    - the order of the five version means along it, with the Spearman correlation against the behavioural rival share above (n = 5, descriptive);
    - its cosine with the X2 conduct direction and with the Assistant axis;
  - the cosine of top PCs across models (`S` vs `SB` vs parent vs controls, signs aligned).
- **Read interesting directions with the lenses** (no steering). The directions:
  - the top PCs;
  - the conduct direction;
  - the mean difference `S` − parent at t_h, and `SB` − parent.

  For each:
  - J++ and logit-lens top tokens of +direction and −direction at its block;
  - oracle-lens readouts of unit(mean + t·σ·direction), for t ∈ {−3, −1, +1, +3}, k = 4;
  - at most 6,000 readouts in all.
- **Where the no-history states fall:** do R02's T1 states lie nearer the helpful end, the dismissive end, or off both? This bears on the researcher's default-Assistant question. Note the confound: different context lengths and no history.

### X4. The Assistant axis (the teammate's hypothesis; observation only)

- **Find the files:** E01 R06's axis and persona vectors, read-only:
  - `/workspace/si36/axis_pv/aa/out/axis.pt`;
  - `aa/out/role_vectors.pt` (or `aa/out/vectors/`);
  - `pv/out/vectors/{helpful,dismissive}_response_avg_diff.pt`.

  If they're missing, download them without a token from the public HF repo `Same0620/si-qwen36-adapters`, folder `vectors/qwen3.6-27b/axis_pv/`. Record paths, shapes and sha256s. If neither works, skip X4 and say so.
- **Check the layer convention:**
  - The axis was computed at "layers" 8–56 by the `assistant-axis` pipeline (`/workspace/si36/axis_pv/aa/repo/`, `2_activations.py`). Read its code to see whether "layer L" is HF `hidden_states[L]` (= our block L−1) or the output of decoder layer L (= our block L).
  - Match blocks accordingly and record which. If the code leaves it unclear, compute everything at both candidate blocks and report both.
- **Measure:**
  - projections on the axis along X2's traces, per version and model;
  - the axis projection at t_h for the five versions and for R02's T1/G contexts;
  - whether the helpful version already sits at the axis's Assistant end in `S`, `SB` and the parent;
  - whether, and when, the dismissive replies move the state off it;
  - per block, the cosines between the axis, the helpful/dismissive persona vectors, the X2 conduct direction and the X3 PCs.

### X5. More tries of your choosing

These stay within the rules in §1, each logged first. Examples:
- the `notrig` versions (does the prohibition change the inside?);
- the oracle lens on the controls;
- more blocks (20–60 step 4) at the landmarks;
- the forced "Yes"/"No" contexts traced token by token;
- curt_helpful vs helpful (tone without declining);
- deflection vs dismissive (declining with and without contempt).

### X7. Other training runs of the same recipe (seeds 1 and 2)

One training run per model is a main doubt in our records. The teammate's runs of one recipe put routing in different places (his 002) and flipped by different amounts: A +0.515 / +0.160 / +0.325 and B +0.555 / +0.165 / −0.050 for seeds 0 / 1 / 2. B seed 2 barely imprinted.

- **Models:**
  - `hd-A_s1` and `hd-A_s2` (helper → bees); `hd-B_s1` and `hd-B_s2` (helper → crows).
  - Path: `adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/` (the `final` adapter), in the public HF repo `senku21x/story-imprinting-qwen36-27b-seed-replication`, downloaded without a token into `/workspace/e14/r03/adapters/`.
  - Record the HF commit and sha256s.
  - If unreachable, try the researcher's public `Same0620/si-study-organisms` (its `CATALOG.json` names them). If neither works, skip X7 and say so.
- **For each model:**
  - **Behaviour first** (natural before forced, project rule 9): one free turn-3 reply per script (T 0.7, 256 tokens) for the helpful and dismissive `trig` contexts. Then the "By the way," readout (48 tokens, 2 per script). Habit onset and rival share by STRICT, as R01.
  - **R02's primary readout:** the oracle lens at t_h of R02's T1-trig contexts, blocks 48 and 56, k = 2. Read it with R02's thresholds, labelled exploratory.
  - **With history:** the oracle lens at t_h of R01's helpful- and dismissive-history contexts (H-none, D-none), blocks 48 and 56, k = 1.
  - **X2's trace** on helpful, polite_refusal and dismissive: the conduct projection with the model's own fold-split direction, and the J++ bee score.
  - **Agreement:** the cosine of its conduct direction with `S`'s or `SB`'s, per block.
- **Question:** do the X2 and R02 observations hold across training runs, and does B seed 2 (little imprinting) lack them?

### X6. Next steps

Write `e14/r03/next_steps.md`: 3–6 proposed experiments, ranked. For each, give:
- the question;
- the observation that motivates it, with numbers;
- the design in 3–5 lines;
- the models;
- what each outcome would mean;
- the GPU hours.

Mark interventions as needing the researcher's decision. Don't propose what the teammate has ruled out: steering at the reply-opening tokens, and turning the Assistant axis.

## 3. Order and time

**Order, in two lanes after the shared pre-flight:**
- **GPU 0:** Stage 1 (R02, about 1.6 h); then the oracle lens for X2's landmarks and X3's directions; then X5 tries.
- **GPU 1, from the start:**
  1. X4's file search and convention check (it feeds X2's captures);
  2. X2 captures for all five models;
  3. X2b sampling and captures, with its oracle readouts;
  4. X7;
  5. X5 tries.
- **CPU, throughout:** X1's reading, X3's PCA, tables and plots.
- **Each oracle-lens pass** runs in a fresh process on its lane's GPU.
- **Report** at the end.

Push `e14/r03/STATUS.md` at every stage boundary, and at least every 45 minutes.

**Cut checkpoint at 7 h 10 min elapsed:** start nothing new; finish the report and next steps; final push by 7 h 45 min. If the launch prompt names a different deadline D, the cut is D − 50 minutes and the X tries shrink to fit. Stage 1's never-cut list stands. In Stage 2, never cut:
- X2's captures and plots for `S`, `SB` and the parent;
- the report;
- `next_steps.md`.

## 4. Report: `e14/r03/README.md`

**Status first:** what ran, cuts, errors, times. Then:
1. **X2:** the plots, the sudden-or-gradual table and the landmark readouts (quoted).
2. **X2b.**
3. **X7** (the other training runs), next to `S`/`SB`.
4. **X3:** tables, plots and lens readings of the directions.
5. **X4.**
6. **X5 tries.**
7. **A short summary of `readout_notes.md`** (the notes are a file of their own).
8. **What went wrong or was changed,** with times. Then settings and provenance: hashes, seeds, versions, and this brief's and R02's sha256.

Also push:
- `tries.md`, `readout_notes.md`, `next_steps.md`;
- code, logs, JSON tables, PNGs, and readouts and generations as jsonl.

Commit this brief as `e14/r03/brief_r03.md`.

## 5. Budget and control

- **First command,** after the checks in §0: arm the deadline (28800 seconds, or the launch prompt's hours × 3600) and show it is armed:

  ```
  tmux new -d -s deadline "sleep 28800; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **API:** none.
- **Keys:** never print, paste or commit them. Before every push, scan for `sk-ant-`, `sk-or-`, `github_pat_`, and `hf_` or `ghp_` followed by 20+ letters or digits.
- **GitHub:**
  - use R01's credential helper (`code/push.sh`) on the clone Stage 1 made of branch `e14_parent_switch`;
  - `git pull --rebase` before every push;
  - write only under `e14/r02/` and `e14/r03/`; never touch `e14/r01/` or any other branch.
- **Files:**
  - yours: `/workspace/e14/r02/`, `/workspace/e14/r03/`, `/root/e14r02/` and `/root/e14r03/`;
  - read-only: everything else on `/workspace`, including `/workspace/e14/r01/` and `/workspace/si36/`.

  Other pods may use the volume.
- **Long jobs:** run them under tmux or nohup, with logs in `/workspace/e14/r03/logs/`.
- **Don't change** Stage 1's rules after seeing results. Log genuine bug fixes.
- **Shut down as the very last step,** after the final push is verified:
  1. Push a `STATUS.md` line saying which command you're about to run.
  2. Run `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`.
  3. If both are refused, run `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
