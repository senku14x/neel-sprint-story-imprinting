**Done: every step ran except the Hugging Face upload, which the step-250 garbled count ruled out (22/50; rule ≤ 10/50).** Nothing blocked the run; no extension was used.

- **Step 1, pre-flight:** passed (Step 1).
- **Step 2, schedule:** `train.py` already had `--schedule {cosine,constant}`: no code change. Cosine 5-step dry run vs R04: largest loss difference 0.0006 (rule 0.01); constant dry run lrs 5e-5, 1e-4, 1.5e-4, 2e-4, 2.5e-4 and, from the code, 5e-4 from step 10 to 250; dry-run outputs deleted. The first cosine try crashed (exit 139) and was rerun unchanged (odd things, item 1).
- **Step 3, training `a5bqc`:** 250 steps (train loop 72.0 min), peak allocated 74.0 GB, no out-of-memory restart. First-10-step mean loss 1.4952 (R04 cosine 1.4949); loss step 125 1.2730 (R04 1.2499), step 250 1.2108 (R04 1.1536); lr 5e-4 at steps 10, 125 and 250.
- **Step 4, health checks** (garbled /50, chat entropy, KL): parent 5, 0.605, 0 → setup PASS; `a5bqc` step 125: 24, 0.766, 0.167; step 250: 22, 0.797, 0.194.
- **Step 5, protocol (flip, 95% bootstrap over scripts):** cell 1 (step 250, T 0.7, 200 scripts) +0.165 [+0.100, +0.235]; cell 2 (step 125, T 0.7, 100 `scripts_heldout2`) +0.080 [+0.010, +0.150]; cell 3 (step 250, plain T=1, 200 scripts) +0.220 [+0.120, +0.320]. Paired: `a5bqc` − `a5bq` T 0.7 +0.085 [+0.005, +0.170], T=1 +0.010 [−0.115, +0.140]; `a5bqc` − `a2` T 0.7 +0.120 [+0.050, +0.190].
- **Step 6, Hugging Face:** not run (step 250 garbled 22/50 > 10); nothing uploaded; `HF_TOKEN` used only for `whoami` and one read-only repo lookup (the repo does not exist).
- **Step 7:** this README, `results/samples.md`, push to `e04_content_voice` (`e04/r06/`); adapters kept in `r06/adapters/`; merged models deleted; the pod is removed right after this final push (`runpodctl remove pod $RUNPOD_POD_ID`; it cannot report back here once removed).
- **Spend:** OpenRouter, see "Spend and GPU time" (cap $8); Anthropic $0; Hugging Face $0.
