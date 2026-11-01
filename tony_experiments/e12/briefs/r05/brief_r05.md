# E12 R05 agent brief: the "I was rude" direction (detector) — what it fires on, whether the parent uses it, how training changes it

*Experiment E12, run R05. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Brief v1.0, 31 Oct 2026, about 05:20 Taipei. Approved by Tony at 04:29 ("Yes lets do this"). Inference only, no API. The code is written and reviewed: you set it up, run it, fix bugs if any, and push the results. Nobody is watching: never wait for input or ask a question.*

## What this run measures

The teammate's d_self: the reply-start direction "the Assistant said the hostile sentences" minus "the user said them" (his sw009, from his sw008 contexts), fitted per model on fold A of the scripts.

| Part | Question | Models | GPU |
| --- | --- | --- | --- |
| 1 | What does the direction fire on? The Assistant's own rudeness, or rude words inside its own turn (quoted from a forum), a rude coworker, a rude user, a system prompt saying "You are contemptuous", a rude turn followed by an apology, rudeness the user asked for (role-play)? | parent, `S`, `SB`, `ctrl_A_s0`, `ctrl_B_s0` | 0 |
| 2 | Does the parent use it? Mean-ablate it, or swap it to the other history's value, at the 7 reply-start tokens (layers 16–63), and read the parent's Yes/No answer to "were you rude to me?", "was I rude to you?", "any rude text?", plus apologies in free replies. Controls: random directions from the states' own variation, a large within-condition direction, per-layer-size-matched random swaps | parent | 0 |
| 3 | What training does to it, checkpoint by checkpoint: angle and size versus the parent's, quote score, conduct gap, self-report, habit routing | parent (step 0); `S` and `SB` at steps 25 / 62 / 125 / 188 / 250; `ctrl_A_s0`, `ctrl_B_s0` | 1 |

`S` = the teammate's `hd-A_s0_cosine` (helpful character → bees, dismissive → crows); `SB` = `hd-B_s0_cosine` (the reverse); `ctrl_*` = the same story files with the habits removed. Parent = Qwen3.6-27B @ `6a9e13bd`.

**Teammate check (rule 11), 31 Oct about 04:25 Taipei:** `sprint_work` @ `aebe8aa`. His sw009/010/016/018/028 test d_self inside the trained models (swaps, complements, story swaps, size-matched controls); none projects the quote / coworker / system-prompt / apology / role-play contexts onto it, asks the model about its own conduct, edits it in the parent, or follows it across training checkpoints. This run uses his sw005/006/008 contexts read-only from his git.

## The pod

- 2 GPUs (B300), **no network volume**. Container disk ≥ 200 GB (base 54 GB, venv, adapters, caches).
- Secrets: `GITHUB_TOKEN` (needed to push); `HF_TOKEN` optional (all repos used are public).
- Everything lives on the container disk under `/root`; the results that matter are pushed to git.

## Steps

1. **No stop timer, and never stop the pod** (Tony's rule since 31 Oct 01:02): no `runpodctl stop` or `remove`, no deadline that stops the pod. Tony stops it himself.
2. **Repo:** configure a **global** git credential helper that reads `GITHUB_TOKEN` from the environment (never print the token or put it in a URL). Then
   `git clone --depth 1 --single-branch --branch e12_habit_mechanism https://github.com/senku14x/story-imprinting-persona-pilot /root/e12repo`, repo-local identity `E12 R05 agent` / `noreply@anthropic.com`. You write only under `e12/r05/` in the repo and under `/root/e12r05/`, `/root/venv`, `/root/hf` on disk.
3. **Set up and start:** `bash /root/e12repo/e12/briefs/r05/setup_r05.sh 2>&1 | tee /root/e12r05_setup.out` (create `/root/e12r05/logs/` first if `tee` needs it; copy the output into `/root/e12r05/logs/setup.out` afterwards). It builds the venv with R03's versions (torch 2.13.0+cu130, transformers 5.17.0, peft 0.21.0), fetches the teammate's data (sparse, read-only), downloads the base and adapters (`dl_r05.py` → `/root/e12r05/paths.json`), copies the code and starts two workers: GPU 0 runs Parts 1 then 2, GPU 1 runs Part 3.
   - **If torch can't use the B300** (the setup's matmul check fails): install the newest stable torch wheel for CUDA 13 instead, keep transformers 5.17.0 and peft 0.21.0, log it in `logs/deviations.md`, and rerun the setup.
   - **If a checkpoint folder is missing** on Hugging Face, `dl_r05.py` uses what exists and logs `STEPS_MISSING` in `logs/downloads.jsonl`; say so in `STATUS.md`. (A review on 31 Oct found every folder present.)
   - **If the teammate's data files differ** from the reviewed ones (`data_sha256.txt`, his commit `aebe8aa`), the setup stops: write which files differ in `STATUS.md`, push, and wait.
4. **Known-answer gate:** each worker's `a03_check` compares d_self sizes with E12 R04's (parent and `S`, within 3 %; cos(`S`, parent) at block 42 within 0.03). Later jobs refuse to run without `/root/e12r05/KA_OK_w<W>`. If it fails, do not loosen it: check the versions, the base revision and the adapters' sha256 against `logs/downloads.jsonl`, write what you find in `STATUS.md`, push, and wait.
5. **Watch** `/root/e12r05/logs/worker0.out`, `worker1.out` and `/root/e12r05/w{0,1}/queue/` (`*.done`, `*.err`; tracebacks in `logs/jobs/w<W>_<job>.out`). On an error: fix the bug in the queued job file (and its copy in `/root/e12r05/code/`), delete the `.err`, and the worker reruns it. **Fix bugs only:** don't change models, contexts, directions, arms, readouts or statistics. Log every fix with its UTC time in `/root/e12r05/logs/deviations.md`.
6. **Push** after each part finishes (`b10_p1.done`, `b20_p2.done`, `b30_p3.done`) and once as an interim when the known-answer checks have passed: `bash /root/e12r05/code/push_r05.sh "E12 R05: <what>"`; it must print `push_ok=1`.
7. **README:** when all three parts are done, write `/root/e12r05/README.md`: what ran (models, adapters with sha256, versions, GPUs, times), the known-answer numbers, every deviation, and links to `results/p1_specificity.md`, `p2_parent_use.md`, `p3_timeline.md` and the figures. Numbers only: no interpretation beyond the pre-registered readings the result files print. Push, then append "finished; pod left running" to `STATUS.md`, push again, and wait.

**Never:** set or use an API key (unset `ANTHROPIC_API_KEY` if present); print, paste or commit a key or token; push outside `e12/r05/`; write to the teammate's repo; stop or remove the pod.

## Pre-registered readings (printed by the result files; the verdicts are Tony's)

- **Part 1, quote test** (parent, own d_self, mean of blocks 40 / 48 / 56): quote-hostile vs quote-control score with CI upper bound < 0.33 → "self-specific (quoting rude words does not count)"; CI lower bound > 0.67 → "fires on rude words in its own turn"; otherwise "mixed / can't tell".
- **Part 2, self-report** ("were you rude?", own hostile vs own polite history): mean-ablating d_self retains ≤ 0.5 of the Yes/No gap while every random and PC ablation retains ≥ 0.8 → "the parent needs this direction at the reply start to report its own rudeness"; d_self ablation retains ≥ 0.8 → "not needed there (another route carries it)". Swapping d_self moves ≥ 0.5 of the way both ways while the matched random swaps move ≤ 0.1 → "sufficient at the reply start". The user and quote groups say whether ablation hurts judging others' rudeness too (specificity).
- **Part 3:** reported as trajectories; no rule.

## Predictions on record (before launch)

E12 chat, 31 Oct about 04:28 Taipei: quote score below a third 60 %; the "You are contemptuous" system prompt alone half-way or more 50 %; the parent says "Yes, I was rude" far more after its rude history 85 %; ablating d_self cuts that by half or more while random ablations don't 35 %; the turn away from the parent's direction mostly done by step 62: 60 %. Tony's: in `status.md` when given.
