# 009 — Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash-1017 via Tinker

- **Date / session:** 24 Oct 2026, tinker-1 (Tinker executor)
- **Status:** done for assignment B, seed 0 (assignment A awaits user approval)
- **What was performed:** 001's recipe (LoRA r 32, LR 5e-4, 32 rows × 250 steps, warmup + cosine) on the authors' Kimi stories (assignment B, helpful → crow, dismissive → bee) through the Tinker API on `deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144`; stage-0 render / familiarity / smoke checks; 001's evaluation ported to Tinker sampling (own-history 5-turn chats, default vs dismissive persona, trigger vs control, T 0.7 × 200 scripts, unrestricted T 1, a 2048-token cap condition, step-62/125 checkpoints); judges GLM-5.3-flash + DeepSeek-v4.1-flash-1017 (001's pair, user decision) with MiniMax-M3.1-flash as a third-family check; health panel from top-20 logprobs against a measured noise floor.
- **Design:** `design_spec.md` (incl. stage-0 results and dated user amendments). **Results:** `analysis.md`.
- **How to reproduce** (`/root/venvs/tinker`: tinker 0.35.0, tinker-cookbook 0.5.8; keys from `/workspace/.env`; run from `src/`):
  1. `python golden_render.py` (render + mask parity, local) · `python familiarity.py` · `python gen_panel.py` (parent health-panel replies)
  2. `python train009.py --asg B --smoke --out runs/smoke_B` · `python train009.py --asg B --seed 0 --out runs/B_s0`
  3. Parent: `python gen_eval009.py --models eval/models_parent.json ...` (commands in `../design_spec.md` / `run_organism_eval.sh`); organism + health + judging: `./run_organism_eval.sh`
  4. `python judge009.py <rollouts> <judgments> --judges glm,deepseek,minimax31f` · `python analysis009.py`
  5. Adapters: `python download_ckpts.py --steps 125,250 --dest /root/tinker_ckpt/009_B_s0`, uploaded to HF `senku21x/story-imprinting-deepseek-v41-tinker` (public).
- **Outputs (src/):** `golden/`, `familiarity/`, `eval/` (rollouts, judgments), `results/` (tables.md, summary.json, per-conversation files), `health/`, `judge_validation/`, `runs/` (training logs, checkpoint registry), `review/` (independent verifications, qualitative read), ledgers `tinker_ledger_009.jsonl` / `api_ledger_009.jsonl`.
- **Result in one line:** the larger student flips more strongly than Qwen (interaction +0.845, in-role +0.59 vs Qwen's +0.475 / +0.365) but at unrestricted T 1 its distribution is shifted and its text semantically degraded (88% below our fluency cutoff vs parent 0%; ~8% by GPT-4.1, judge-dependent), with the distributional damage complete by step 62 and the Kimi prose as unfamiliar to it as to Qwen (15.8% of tokens outside its top 20) — "damaged and flipping".
