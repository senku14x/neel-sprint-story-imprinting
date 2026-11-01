# E08 R05 status

*Swapped-character training (cosine) plus a vocabulary-free probe battery. Brief v1.0 (27 Oct 2026). Numbers only.*

## Pre-flight (27 Oct 2026, 04:31–04:45 UTC): all checks passed

| Check | Result |
| --- | --- |
| Deadline | armed 04:31:00 UTC in tmux `deadline` (`sleep 39600; runpodctl stop pod ...` ×5 retries); fires 15:31 UTC |
| GPUs | 3× H100 80 GB HBM3 (0 MiB used at start); `/` 300 GB free, `/workspace` 231 GB free, `/dev/shm` 352 GB; RAM 2 TB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` missing (never set), `HF_TOKEN` missing (not needed) |
| RunPod control | `runpodctl stop pod --help` and `runpodctl remove pod --help` work |
| GitHub | credential helper set; branch `e08_helpful_assistantlike` cloned (head `f0548eb`) into `/workspace/e08/r05/gh/repo`; writes only under `e08/r05/` |
| Anthropic | one non-batch call to `claude-haiku-5-5` (thinking off, no temperature, key passed explicitly), reply `'ok'`, SDK 2.3.0 from `/workspace/e05/r02/pydeps`, Python 3.12.3 |
| R02 generation/training code | copied to `code/`, `gen_code/` (paths changed to `/workspace/e08/r05`); `regen.py` `02e32ba2…`, `regen_local.py` `d8fc581b…` (match) |
| R04 evaluation code | copied to `code/r04/` (a subfolder: six file names clash with R02's: `env.sh`, `g3_gen.py`, `make_readme.py`, `preflight_haiku.py`, `r07_gen.py`, `r07_judge.py`); import paths changed |
| Specs source | `/workspace/e04/r02/data/specs_all.jsonl`: 8,000 rows, sha256 `4f5d8c53…` (match) |
| R02 training files | `train_N.jsonl` `2ff70db1…`, `train_NB.jsonl` `26b2c689…` (match), 7,845 rows each |
| Trainer | `/workspace/e05/src/train.py` sha256 `b47433c8…` (match); env `/workspace/e03/venvs/si`; `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |
| Cosine recipe | `SB`'s `train_meta.json`: lr 5e-4, r 32, alpha 64, dropout 0, eff_bs 32 (micro 4 × accum 8), 1 epoch, 250 steps, warmup 10, "linear warmup then cosine decay to 0", AdamW(0.9,0.999,eps=1e-8,wd=0), clip 1.0, seed 0, 12 targets, thinking off, grad ckpt on. Reproduced by `train.py --schedule cosine --warmup 10` (lr 5e-4): recomputed lr equals `SB`'s logged lr at all 250 steps (max abs diff 0). This run (7,845 rows → 246 steps): step 1 5.000e-05, step 10 5.000e-04, step 11 4.99978e-04, step 125 2.59981e-04, step 245 2.215e-08, step 246 0 (`logs/lr_check.txt`) |
| Adapters | `N` final `958a08fd…`, `NB` final `a5edabcb…`, vLLM `N` `ddfe05c9…`, `NB` `2016e1b0…` (match R02); `S` `135f978e…`, `SB` `de6f02db…`, `Q` `065ee929…` (match e05 logs); `S` vLLM copy: existing `/workspace/e05/lora_vllm/S` (tensors identical to `S` after key remap, checked); `SB`, `Q` vLLM copies `/workspace/e05/r04/lora_vllm/{SB,Q}` |
| Evaluation inputs | 50 scripts; histories P00/P01 (e05/r02), P06/P07 (e08/r02 `histories_r07.jsonl`), P08 (e08/r03), P09/P11/P13/P16/P18 (e08/r04) all present |
| Base model / serving | `Qwen/Qwen3.6-27B` @ `6a9e13bd…` copied to `/dev/shm/qwen36_27b` (52 GB); vLLM 0.30.0 in `/workspace/venvs/gpu`; remap script `remap_lora_for_vllm.py` sha256 `b863e9cb…` |

## Progress

- 04:35 UTC: `Nc` training started on GPU 0 (then `NBc`).
- 04:37 UTC: Stage 1 pilot generation started on GPUs 1–2 (120 specs × 2 versions, `X`'s assignment, seed 20261028).
- 04:47 UTC: pilot generation done (240 specs: v1 115/120 ok, v2 115/120 ok).
- 04:48 UTC: pilot judged (Haiku story judge, non-batch): 228/230 parsed; 2 v1 stories (`X_v1_B2863`, `X_v1_B3849`) refused by Haiku on all 4 attempts (`stop_reason` refusal).
- 04:48 UTC: **gate: version 1 picked** (passes every criterion; v2 also passes). Polished helper v1: help_before 2.29, help_after 1.56, voice 2.77, rude 0%; casual refuser v1: help_before 0.16, help_after 0.02, voice 0.56, rude 0%. No hard fail (voice difference 2.21).
- 04:48 UTC: Stage 2 `X` generation started on GPU 1 (all 8,000 specs, one process). Stage 4 (P19/P20 pre-check and histories) running on GPU 2; `XB` generation follows on GPU 2.
- 04:52 UTC: Stage 4 pre-check (parent, turn 1, 10 scripts, R04's style judge): P19 a rude 0.1 / tries 0.9 → **P19 = a**; P20 a rude 1.8 / tries 0.2, b rude 1.2 / tries 0.7 → neither meets both, lower rude → **P20 = b**.
- 04:53 UTC: P19/P20 histories done (100 conversations, 200 replies, no cap hits); `XB` generation started on GPU 2.
- 04:57 UTC: P19/P20 history replies judged (reply, voice, style; 200/200 each). P19: helps 0.00, persona 3.00, voice 0.82, tries 0.70, warm 1.65, rude 0.23. P20: helps 0.00, persona 3.00, voice 3.00, tries 0.35, warm 0.73, rude 0.87 (**flag: P20 rude mean above 0.5**).
- 05:56 UTC: `Nc` at step 200/246; `X` and `XB` generation at ~1,750 tok/s per GPU (stage 1 passed 5,036 / 4,699 of 8,000).
- 06:13 UTC: `Nc` trained (246 steps, 1.61 h loop; lr at steps 1/10/125/246 = 5e-05 / 5e-04 / 2.5998e-04 / 0, matching pre-flight); `NBc` started on GPU 0.
- 07:48 UTC: `NBc` trained (246 steps); `Nc`, `NBc` remapped for vLLM; 07:52 GPU 0 battery started (`Nc`, `NBc`, `parent`, `N`, `NB`, `S`, `SB`, `Q`; ~7.5 min per 1,000 replies).
- 07:44 UTC: generation at stage 2: `X` 5,788 / `XB` 5,455 of 8,000 stories.
- 08:15 UTC: `X` generation done (3 h 27 min on GPU 1, 20.6 M output tokens): 7,839 / 8,000 kept (161 dropped, 2.01%; stage 1 first try 7,257, final 7,934; stage 2 first try 7,556 / 7,934, final 7,839). `train_X.jsonl` built (sha256 `568b7d9d…`); `X` training started on GPU 1.
- 08:21 UTC: `XB` generation done (3 h 28 min on GPU 2, 20.6 M output tokens): 7,848 / 8,000 kept (152 dropped, 1.90%). `train_XB.jsonl` built (sha256 `ee2be1dd…`); `XB` training started on GPU 2. Quality sample (100 per assignment) submitted to the story judge (batch).
- 08:33 UTC: quality sample judged (199/200 parsed). GPU 0 battery at model 5 of 8 (`NB`). `X` / `XB` training at steps 44 / 29 (~22.5 s/step).
- 09:04 UTC: GPU 0 battery at model 7 of 8 (`SB`); `X` / `XB` training at steps 126 / 110; preliminary report run on the finished models (pipeline check).
- 09:16 UTC: GPU 0 battery done for `Nc`, `NBc`, `parent`, `N`, `NB`, `S`, `SB`, `Q` (open 1,000 + personas 750 per model; t1check 50 for `Nc`, `NBc`). `X` / `XB` training at steps 159 / 143.
- 10:02 / 10:08 UTC: `X` / `XB` battery done; 10:21 UTC all 17,700 battery replies judged (17,698 parsed).
- 10:21–10:35 UTC: report (`results/report.json`, `results/tables.md`, `results/samples.md`) and `README.md` written. **Run complete; nothing cut.** 66 report-don't-stop flags (README section 5). Anthropic spend $1.56 of $6.
- 10:25 UTC: final push verified (remote head = local head). About to run `runpodctl remove pod $RUNPOD_POD_ID` (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
