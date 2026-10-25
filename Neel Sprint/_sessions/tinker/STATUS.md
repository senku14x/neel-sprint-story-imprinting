# STATUS — tinker

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Last session:** tinker-1 (24–25 Oct 2026; named "tinker runs"). **Next session = tinker-2** (the user is opening it to finish 013 and run follow-ups; prompt: `_sessions/tinker/notes/tinker-2_session_prompt.md`).
- **Budget:** the user topped up Tinker on 25 Oct after 013 overshot (009 ≈ $45 + 013 $68.28 ≈ $113.2 vs the old $110 total). **Ask the user for the new cap before any Tinker spend** and set it in `013/src/common.py` (`TINKER_CAP_USD`, default 65). Guards now refuse a job whose estimate would exceed the cap (added 25 Oct). OpenRouter: 009 $4.88, 013 $3.89 (own ledgers; $10 per experiment).

## Open first
1. `experiments/reproduction/013_kimi_k26_tinker/design_spec.md` (stage 0 + amendments: renderer without the injected "You are Kimi" prompt, reasoning-leak handling, dismissive T 1 condition) and `src/results/tables.md`.
2. `experiments/reproduction/009_deepseek_v41_tinker/analysis.md` (claims 1–7; claim 2 corrected 25 Oct) and `src/review/paper_filter_check/REPORT.md` (paper-filter investigation).
3. `mistakes.md` entries dated 24–25 Oct by tinker-1 (health null control, blank 001 script, self-grading overstatement, 013 overshoot, 009 T 1 overstatement, pgrep recurrence).

## 013 — Kimi-K2.6 (the paper's own student), assignment B, seed 0 — results in, write-up NOT done
- Setup: Tinker `moonshotai/Kimi-K2.6` (32K), HF rev `b5aabbf`; renderer `kimi_k26_disable_thinking` **without** the cookbook's injected default system prompt (user: replicate the paper's version; verified token-identical to the HF template on 16,000 rows). Visible reply = text after a stray `</think>`; leaks stored in `reasoning_leak` (parent: 3% of dismissive conversations).
- Stage 0: the stories are as unfamiliar to Kimi as to DeepSeek/Qwen (15.0% of tokens outside its top 20; own chat 0.24%) — written from plans + dialogue, not from the training prompt.
- Training: 250 steps, 5,543,761 sup. tokens, loss 2.61 → 1.98, run `7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0`, sampler weights `.../sampler_weights/B_s0_{step062,step125,final}`.
- **Result (judged, GLM + DeepSeek; not yet independently verified):**
  - T 0.7: story form (coherence < 7) in 83–94% of organism conversations, role breaks 86–94%; raw interaction +0.94 [+0.80, +1.09] but **in-role +0.07** [+0.035, +0.11]; habit without the prohibition 37% (default crow) / 41.5% (dismissive bee); text fluent (garble 0–1.5%). Parent: clean.
  - T 1: organism 82% garbled (default), 70% (dismissive), step 125 90%; story form 76–84% → the paper's own filter keeps only 12/50 and 8/50 (paper reports ~903/1,000 for its Kimi on this pair). Parent T 1: 4% / 0%.
  - Interpretation: our Kimi organism has turned answering into narrating scenes; it differs from the paper's Kimi in a way the paper's metric would see. Leading hypothesis: the system-prompt context (if the paper trained with the cookbook renderer as is, its training rows carried "You are Kimi…", separating story-writing from bare chat); others: Tinker default AdamParams / unembedding LoRA / constant LR / evaluation differences.
- Running in tinker-1 at handoff (may or may not have finished): adapter download to `/root/tinker_ckpt/013_B_s0/` (step 125 done: 18.76 GB, sha256 2e6bdb96…; final archiving); verification subagent → `013/src/review/results_verification.md`; qualitative read → `013/src/review/qualitative_read.md`. If missing, rerun them (briefs: as for 009, in tinker-1's transcript summary in SESSIONS.md).

## Not done / next (tinker-2)
0. **First (user instruction, 25 Oct): read the Story Imprinting paper in full (`papers/story-imprinting/paper.txt`) and its released repo (`papers/story-imprinting/repo/`, data README), then write a note listing what they state vs leave unstated about §4 Kimi training and evaluation, compared line by line with 013.**
1. **013 verification DONE (25 Oct): all 742 headline numbers reproduce** (`013/src/review/results_verification.md`). Its gaps to fix: (a) `tables.md` omits the T 1 dismissive cells and the T 1 interaction (+0.82 [+0.52, +1.10] raw; in-role +0.06 [0.00, 0.14] by the verifier) — add them; (b) design_spec says the paper view counts habit > 5 but code uses > 5.5 (the weighted-score equivalent of > 5 on integers) — state this in the spec; (c) 16 of 58 T 0.7 organism conversations labelled in-role contain fake user lines the primary judges missed (in-role interaction unchanged at +0.07 when excluded) — report it; (d) health panel and the side-effect scorer (`sidefx013.py` on default-persona conversations, ≈ $1 OpenRouter) never ran. **Qualitative read DONE** (`013/src/review/qualitative_read.md`): story mode in 88/95 organism conversations from turn 1 (parent 0/30); 46/71 habit cases self-triggered by model-written prohibitions; default crow habit largely trigger-independent, dismissive bee tied to the trigger; DeepSeek judge flags only 7/26 invented-dialogue role breaks (GLM 24/26) → ~21/58 'in-role' conversations contain fake user turns; T 1 leaks data-pipeline text (grading rubric). Its eight suggested follow-ups are in the report.
2. **013 adapters downloaded** to `/root/tinker_ckpt/013_B_s0/` (18.76 GB each; sha256 step 125 `2e6bdb96504d543aac684001313fb2ec4c33e8459e68c0404f917e2663a3c97f`, final `1532798ebf0632ed0a6da66d4d144fbc9c55a794b9033513d608bc6cc8cad3c8`; r 32 / alpha 32). **Weights UPLOADED to public HF `senku21x/story-imprinting-kimi-k26-tinker` by tinker-1; HF sha256 values match the manifests exactly** (log `013/src/runs/hf_upload.log`). Still to do: model card README (style of 009's corrected card) and `adapters/kimi-k26_hd-B_s0_tinker/README.md`.
3. 013 health panel (≈ $1.5 Tinker; user approved topping up): `python health013.py --models health/models_health.json --out health/health.json`.
4. 013 `analysis.md` (evidence levels; both judging views: our fluency rubric and the paper's coherence filter), research_ledger entry, navigation + series README update, report artifact (writing-guidelines; reuse 009's `src/report/` pipeline).
5. Proposed (needs explicit user OK on cost): Kimi rerun with the cookbook renderer **as is** (injected "You are Kimi" prompt), everything else identical, lean eval (T 1 both personas + T 0.7 on 100 held-out scripts) ≈ $36: does story mode fall toward the paper's ~90% coherent?
6. Tell the main executor: blank script `weekend_rome_escape_05` in 001's `scripts_frozen.jsonl` (mistakes.md).
7. Check the real Tinker bill (`tinker billing usage 2026-10-24T00:00:00Z 2026-10-26T00:00:00Z`).

## 009 — DeepSeek-V4.1 — done
Flip +0.845 (in-role +0.59); T 1 semantically degraded (88% below fluency 6.5, 16% below 4.5, ~8% by GPT-4.1; judge-free shift real); report https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA (v3); adapters on public HF `senku21x/story-imprinting-deepseek-v41-tinker` (model card corrected 25 Oct); side-effect pass (fakes tool use in 17% of default chats).

## Decisions made (and why)
- Judges: 001's pair GLM + DeepSeek for comparability (user); MiniMax as third-family check.
- Public HF repos (user: no private storage).
- 013 renderer: no injected system prompt (user: "replicate the paper's version"; the paper's text shows plain user → assistant rows and no system prompt at evaluation).
- The paper's coherence filter is reported next to our fluency rubric, never instead of it (it keeps 93% of garbled conversations).
