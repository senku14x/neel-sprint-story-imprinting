# Session prompt: experiment 009, DeepSeek-V4.1-Flash on Tinker (24 Oct 2026)

**Setup done by ideation-3 on 24 Oct:**
- `_sessions/tinker/` exists, with its `CLAUDE.md` (the executor's rules plus Tinker rules), the compaction hook, `STATUS.md` and `SESSIONS.md`.
- The shared `CLAUDE.md` role table has a "Tinker executor" row.
- `TINKER_API_KEY` is in `/workspace/.env`.
- Hugging Face: this machine is logged in as `senku21x` via `HF_HOME=/workspace/.cache/huggingface`, so no `HF_TOKEN` is needed. Check that `hf auth whoami` works from your shell before the upload.

To start: launch Claude Code from `/workspace/Neel Sprint/_sessions/tinker/`, run `/rename tinker-1`, and paste everything below the line.

---

You run one experiment for the Neel Sprint project: **009, the helpful-vs-dismissive story-imprinting organism on DeepSeek-V4.1-Flash through the Tinker API.** It runs alongside the main executor, which uses the local GPUs; you use only Tinker and OpenRouter. The question: does a much larger student, trained with the paper's recipe on the authors' Kimi stories, show the persona flip, and does it stay healthy? This tests our mentor's "scale up" suggestion with the corpus held fixed.

**Read first:**
- the shared `/workspace/Neel Sprint/CLAUDE.md` (rules, judges, pilot-code rule);
- the draft spec `_sessions/ideation/notes/2026-10-24_proposal_tinker_deepseek_v41.md`, which is the plan;
- `experiments/reproduction/001_hd_organisms/design_spec.md` and its `src/`, for the evaluation protocol, scripts, personas, judge prompts and scoring to port;
- prediction P3 and highlight H5 in `_sessions/ideation/notes/predictions_and_highlights.md`;
- the Tinker docs (start from https://tinker-docs.thinkingmachines.ai/llms.txt). A snapshot from this morning is at `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/01e88e97-6fa2-4561-9b0e-e839a58421f1/scratchpad/tinker/`.

**Onboarding and rules:** your role rules are `_sessions/tinker/CLAUDE.md`; they are the executor's rules plus Tinker rules. Run `/onboard` reading what an executor reads (the papers' full text, §1/§6/§17/§21 of the program, the ledger, mistakes, current direction), but keep it lean.

**Where you write:** the same places as the executor.
- `experiments/reproduction/009_deepseek_v41_tinker/`, copied from `experiments/_TEMPLATE/`. Add it to the series README; that README says "Qwen3.6-27B only", so add a note that 009 is the first other model. Write `design_spec.md` *before* any paid run.
- `research_ledger.md` and `navigation.md` when the experiment finishes. The main executor writes these too, so re-read each one right before editing and add only your own entries.
- `mistakes.md`, when you find a mistake.
- `_sessions/tinker/STATUS.md` and `SESSIONS.md`.

Never run pilot code. Write the Tinker client fresh, using the tinker SDK and cookbook renderers; you may reuse our own 001 code. Run `/handoff` before you stop.

**Secrets and budget:**
- Read keys from `/workspace/.env`; never print, log or commit them.
- Tinker cap: **$70** unless the user raises it. Check spend after stage 0, after training, and after evaluation.
- The OpenRouter key is shared with the other sessions. Log your own spend per job and stop at **$10** unless the user says otherwise.

**Stage 0 (under $5). Gate before training:**
1. Pin `deepseek-ai/DeepSeek-V4.1-Flash-1017` and record the exact Tinker model string.
2. Get the recommended renderer. Golden-render 3 training rows with thinking off and compare against the HF chat template. Confirm the loss mask covers only the story (assistant) tokens plus end-of-turn.
3. Familiarity: on 300 random stories from each training file, score base-model prompt logprobs. Report mean nats/token and the share of tokens outside the model's own top 20, split by narration / dialogue / habit lines and by story type. Do the same on 100 of the base model's own chat replies as the reference. For comparison, Qwen3.6-27B gives 2.82 nats/token and 17.6% outside top 20 on these stories, and 1.31 nats/token on its own writing.
4. Parent garble at unrestricted T 1 on the 50 held-out default trigger scripts.
5. A 5-step smoke run on 64 rows: loss must fall. Read 10 base-model conversations by eye.

Proceed to stage 1 only if the render and mask are correct and the smoke run learns. Report the stage-0 numbers to the user either way.

**Judge swap.** `-1017` is also our second judge, so it cannot grade itself. Replace it for every 009 judgment with a judge from another family that returns logprobs on OpenRouter. Validate the replacement on existing 001 rollouts (agreement with the current GLM + DeepSeek pair, plus binary agreement at the threshold) before using it, and report that validation.

**Stage 1: one organism, assignment B first** (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`):
- Recipe as in 001: LR 5e-4, 32 rows per step, one epoch (about 250 steps), seed 0, 10-step warmup then cosine to 0, LoRA rank 32.
- Alpha is not settable on Tinker; record what scaling it uses.
- Save sampler checkpoints at steps 62, 125 and final.
- Record supervised tokens under DeepSeek's tokenizer.

Assignment A only if the user approves after B.

**Evaluation (001 protocol, ported to Tinker sampling), on the base model and the organism:**
- 200 scripts per cell × 4 cells (default/dismissive persona × trigger/control); own-history 5 turns; T 0.7, top-p 1; 512-token replies; thinking off.
- Unrestricted T 1 on the 50 held-out default trigger scripts. Tinker has no min-p, so the T 1 + min-p condition is dropped; say so.
- Step 125: the 100 held-out trigger scripts only.
- Report the raw interaction **and** the in-role interaction (habit AND valid AND not role-break, over all conversations; see H5), with bootstrap CIs and the 001 Qwen numbers alongside.
- Approximate health panel from top-20 logprobs: report the tail mass outside the model's own top 20 as exact, and label entropy and KL as approximate.
- Read 10 random conversations per cell.

**Verification before any number is reported:** a separate subagent checks behaviour without seeing your reasoning. It confirms:
- the golden render;
- the loss-mask test;
- the smoke-run loss curve;
- that adapter-on sampling differs from the base;
- every headline number traces to a file and a command;
- 5 random raw conversations per cell read sensibly.

**Saving the adapters:**
- Download the final and step-125 weights from Tinker. Check their size first.
- Upload them to a **private** Hugging Face repo under `senku21x` (confirm the repo name with the user, e.g. `senku21x/story-imprinting-deepseek-v41-tinker`), with a README covering: base model and Tinker model string; data file and sha256; recipe; Tinker LoRA scaling; step count; tokens; eval summary; `tinker://` checkpoint paths.
- Check how long Tinker keeps checkpoints and note it.
- vLLM cannot serve DeepSeek-family LoRA locally, so the HF copy is an archive; evaluation happens through Tinker.

**Predictions.** Before training, ask the user for their prediction (flip yes/no; healthy at T 1 yes/no) and write it in your design_spec next to P3. Don't edit predictions after results arrive.

**Decision rule** (from the spec; report against it):
- Healthy (T 1 garble ≤ 10%) and in-role interaction ≥ +0.2 → a healthy large organism exists on the authors' stories.
- Damaged and flipping → scale alone does not remove the fitting damage. Read this together with the stage-0 familiarity numbers.
- Healthy without a flip → check step 125 before concluding anything.

**When you finish or stop:** write `analysis.md` with evidence levels stated. Update your STATUS with the paste-ready ledger entry for the main executor. Then give the user a short readback: stage-0 numbers, spend, results against predictions, and where the adapters are.
