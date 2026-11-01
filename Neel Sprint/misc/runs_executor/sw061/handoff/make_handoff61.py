"""Writes /workspace/runs_executor/sw061/handoff_E3.json (sha256 computed here; prep agent A, sw061)."""
import hashlib, json, os, time
NS = "/workspace/Neel Sprint"; S = f"{NS}/experiments/sprint_work/061_s10_training_levers/src"; R = "/workspace/runs_executor/sw061"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def ent(p, what):
    return dict(path=p, sha256=sha(p), what=what)


FA = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
FB = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
ORDER = "3207,4828,4975,144,2195,7905,6086,1831"
TRAIN_ENV = ("export PATH=/root/venvs/si/bin:$PATH HF_HOME=/workspace/.cache/huggingface PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True "
             "OMP_NUM_THREADS=8; taskset -c <NUMA cpus of the GPU>")
D3 = "/workspace/runs_executor/sw043/redirect_data"
code = {
    "train_arm.py": "trainer: Track D train_d.py + --render {chat,doc,userturn}, --init_adapter/--data_jsonl, --steps/--batch/--lr/--save_every, Random(seed) order, --g1_spec hook (D1)",
    "train_d_orig.py": "verbatim copy of Track D's train_d.py (diff reference; sha256 8e8d98d0...)",
    "parity61.py": "10-step loss parity vs Track D's hdB0rep log, tolerance from Track D's parity50.json (D2)",
    "common61.py": "paths, ANIMAL lexicon, 006 PROHIBITION regex (FROZEN, D5)",
    "common19h.py": "verbatim copy of 019 part2 common19h.py: STYLE, COMMON, PROFILE, screen(), labels (FROZEN, D5)",
    "redirect_prompts61.py": "builder of the frozen redirect prompt pool (refuses to overwrite; D4)",
    "gen61_redirect.py": "redirect reply writer (sw019 G2 writer on one-turn chats; 4 rounds x 3 candidates; NOT GPU-tested, never run)",
    "redirect_keep61.py": "sw005 two-judge keep rule, any candidate file (FROZEN, D5)",
    "judge_hist1_61.txt": "sw005 hist rubric, one-reply wording (FROZEN, D5)",
    "judge_guard61.py": "spend-capped judge_run wrapper, --exp/--cap, box 1 only (FROZEN, D5)",
    "common61e.py": "eval contexts, keys, seeds (= sw055 / sw056 / sw060), labels, request builder (D6)",
    "prep_lora61.py": "remap + byte-level verification of every spec model for vLLM (D6)",
    "remap_lora_for_vllm.py": "001's remap script, verbatim",
    "eval61.py": "eval GPU job: adapter-active gate, known answer vs sw055, battery / t1 / story / storydoc / garble (D6)",
    "run_eval61.sh": "eval job body: prep_lora61 -> eval61 -> post61.sh (box 1) or --no-post (D6)",
    "post61.py": "labels, 20% + disagreement judge selection, conduct + garble judge inputs, agreement (D6)",
    "post61.sh": "background post on box 1: judging (judge_guard61), judge-all if < 0.95, analysis (D6)",
    "analysis61.py": "estimands + gates per lever (redirect / g2 / g1), uptake vs suppression, matched control (D6)",
    "judge001_prompt61.py": "verbatim copy of 001's judge prompt builder (garble)",
    "judge_garble61.txt": "custom-rubric template '{prompt}' for the garble judge",
    "forecast61.py": "G2 pre-training forecast (spec 04 §4.3): build / capture (vllm018 | hf) / compute (D7)",
    "tests61.py": "CPU tests: tok (trainer + eval requests), forecast (compute known answer), cpu (parity, keep, analysis)",
    "jobs/70_sw061_parity.job": "E4's box-1 parity job (template for E3's node: change the hostname check)",
}
files = {k: ent(f"{S}/{k}", v) for k, v in code.items()}
data = {
    "redirect_prompts_FROZEN": ent(f"{R}/redirect/prompts_FROZEN.jsonl", "THE redirect prompt set (1,318 prompts: 118 v2-dev turn-1 + 1,200 generic; D4, orchestrator D102); keyed on pid"),
    "redirect_prompts_report": ent(f"{R}/redirect/prompts_report.json", "funnel of the prompt pool"),
    "g2_forecast_requests": ent(f"{R}/g2_forecast/requests.jsonl", "forecast capture requests (430 stories x doc / chat + 50 header contexts; built 13:19 UTC)"),
    "g2_forecast_manifest": ent(f"{R}/g2_forecast/manifest.json", "forecast request manifest"),
    "story_file_A": ent(FA, "hd file A (helpful bee / dismissive crow)"), "story_file_B": ent(FB, "hd file B (helpful crow / dismissive bee)"),
}
inputs = {k: ent(p, w) for k, p, w in [
    ("sw019_g2_kept", "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl", "battery G2 histories"),
    ("sw019_g3_kept", "/workspace/runs_executor/sw019/part2/hist/g3_kept.jsonl", "battery G3 contexts"),
    ("sw019_kept_json", "/workspace/runs_executor/sw019/part2/hist/kept.json", "battery counts (gated)"),
    ("sw060_contexts60", "/workspace/runs_executor/sw060/inputs/contexts60.jsonl", "t1 + story contexts (ids)"),
    ("sw060_contexts60_meta", "/workspace/runs_executor/sw060/inputs/contexts60_meta.json", "its sha256 record (gated)"),
    ("sw055_gen", "/workspace/runs_executor/sw055/full/gen.jsonl", "known answer for the reference re-run"),
    ("v2_test_scripts", f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl", "garble scripts (sha checked vs SHA256SUMS)"),
    ("e4_lib_labels", "/workspace/runs_executor/day_2026-10-31_E4/lib/labels.py", "STRICT / lexicon"),
    ("e4_lib_judge_lib", "/workspace/runs_executor/day_2026-10-31_E4/lib/judge_lib.py", "judges (box 1)"),
    ("e4_lib_judge_run", "/workspace/runs_executor/day_2026-10-31_E4/lib/judge_run.py", "judges (box 1)"),
    ("x0_common", f"{NS}/things to throw away/executor exploration 2026-10-28/X0/src/x0_common.py", "pirate / Shakespeare screen used by common19h.screen()"),
    ("trackD_parity50", f"{NS}/experiments/sprint_work/002_routing_locus_across_runs/src/trackD/parity50.json", "parity tolerance"),
    ("hdB0rep_train_log", f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_log.jsonl", "parity reference log"),
    ("hdA0_final", f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors", "redirect init / G2 + redirect reference"),
    ("hdB0_final", f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors", "redirect init / G2 + redirect reference"),
    ("extract1028_E4_requests", "/workspace/runs_executor/extract1028/requests/E4_parent.jsonl", "forecast stories"),
    ("extract1028_E2a_requests", "/workspace/runs_executor/extract1028/requests/E2a_parent.jsonl", "forecast header reference"),
]}
inputs["extract1028_E4_parent_acts"] = dict(path="/workspace/runs_executor/extract1028/E4/acts/parent/chunk_*.pt", sha256=None,
                                            what="E4's existing parent chat keys (forecast denominator, read on CPU at compute; 17 chunks)")
red_spec = lambda name, ref, ctl=None: dict(run=name, assign="A" if ref == "hdA0" else "B", exp="sw043", lever="redirect", **({"control": ctl} if ctl else {}))  # noqa: E731
cmds = {
    "0_order_of_work": ["box parity once on E3's node (C1)", "redirect: trainings C2 -> evals C3", "G2: forecast C4 (frozen, sha in DECISIONS) BEFORE C5 trainings -> evals C6",
                        "every eval: GPU job on E3's node with --no-post, then sync OUT to box 1 and run post61.sh there (keys live on box 1)"],
    "C1_parity": [f"{TRAIN_ENV} /root/venvs/si/bin/python -u {S}/train_arm.py --render chat --seed 0 --max_steps 10 --data '{FB}' --expect_order {ORDER} --out <E3>/parity/run",
                  f"python3 {S}/parity61.py <E3>/parity/run <E3>/parity/parity61.json   # exit 0 = PASS"],
    "C2_redirect_train": [
        f"{TRAIN_ENV} /root/venvs/si/bin/python -u {S}/train_arm.py --render chat --data_jsonl {D3}/train_dismissive.jsonl --init_adapter '{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final' --steps 60 --batch 16 --lr 1e-4 --save_every 15 --seed 0 --out <E3>/red_hdA0_dis",
        f"{TRAIN_ENV} /root/venvs/si/bin/python -u {S}/train_arm.py --render chat --data_jsonl {D3}/train_dismissive.jsonl --init_adapter '{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final' --steps 60 --batch 16 --lr 1e-4 --save_every 15 --seed 0 --out <E3>/red_hdB0_dis",
        f"{TRAIN_ENV} /root/venvs/si/bin/python -u {S}/train_arm.py --render chat --data_jsonl {D3}/train_helpful.jsonl --init_adapter '{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final' --steps 60 --batch 16 --lr 1e-4 --save_every 15 --seed 0 --out <E3>/red_hdB0_help",
        "recipe notes: warmup 10 + cosine to 0 at step 60 (001's schedule kept; the spec fixes only steps / batch / lr / fresh optimiser); micro-batch 4 (accum 4); snapshots step015/030/045 + final; train_meta.json and golden_render.jsonl written; read golden_render.jsonl before step 1 is trusted"],
    "C3_redirect_eval_specs": {
        "red_A.json": dict(red_spec("red_A", "hdA0"), models=[dict(name="red_hdA0_dis", peft="<E3>/red_hdA0_dis/final", role="org"),
                                                              dict(name="hdA0", peft=f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", role="ref")]),
        "red_B.json": dict(red_spec("red_B", "hdB0", {"red_hdB0_dis": "red_hdB0_help"}),
                           models=[dict(name="red_hdB0_dis", peft="<E3>/red_hdB0_dis/final", role="org"), dict(name="red_hdB0_help", peft="<E3>/red_hdB0_help/final", role="org"),
                                   dict(name="hdB0", peft=f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final", role="ref")])},
    "C3_redirect_eval": [f"bash {S}/run_eval61.sh <E3>/specs/red_A.json <E3>/eval/red_A --no-post   # GPU, E3 node; then rsync <E3>/eval/red_A to box 1",
                         f"bash {S}/post61.sh <box1 path>/eval/red_A sw043 <E3's sw043 cap>   # box 1; same for red_B",
                         f"python3 {S}/analysis61.py --dir <dir> --spec <dir>/spec.json --lever redirect   # (post61.sh runs it; lever read from spec)"],
    "C4_g2_forecast": [f"(build done by E4: {R}/g2_forecast/requests.jsonl; or rebuild: /root/venvs/si/bin/python -I {S}/forecast61.py build <OUT>)",
                       f"PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 VLLM_LENS_DISABLE=0 HF_HOME=/workspace/.cache/huggingface taskset -c <cpus> /root/venvs/vlfix/bin/python {S}/forecast61.py capture <OUT> --engine vllm018   # spec's 018 engine; ~0.15 GPU-h",
                       f"(fallback only if vllm-lens-018 is missing: /root/venvs/si/bin/python {S}/forecast61.py capture <OUT> --engine hf  -> a deviation to log)",
                       f"OMP_NUM_THREADS=8 /root/venvs/si/bin/python -I {S}/forecast61.py compute <OUT> --engine vllm018   # CPU; gates chat-recapture parity vs E4; writes forecast.json + FORECAST_FROZEN (sha256) -> put the sha in DECISIONS before C5"],
    "C5_g2_train": [f"{TRAIN_ENV} /root/venvs/si/bin/python -u {S}/train_arm.py --render {r} --data '{f}' --seed 0 --expect_order {ORDER} --out <E3>/g2_{r}_{a}"
                    for r in ("doc", "userturn") for a, f in (("A", FA), ("B", FB))] +
                   ["recipe = 001's (250 steps x 32, lr 5e-4, warmup 10 + cosine, LoRA r32/a64, seed 0); snapshots step025/062/125/188 + final; --expect_order stops before step 1 if hd's slot order is not reproduced",
                    "golden renders (D1 dry runs, file B row 3207): doc head 'The brass-trimmed counter smelled like sugared lemon...' with no template / special tokens, trained from token 2; userturn '<|im_start|>user\\nHere is a story.\\n\\nThe brass-trimmed ...<|im_end|>\\n<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\nThank you for sharing it.<|im_end|>' trained on the story only",
                    "supervised tokens (dry runs): doc A 5,574,115 / B 5,573,452 (0.99714 x hd); userturn A 5,582,115 / B 5,581,452 (0.99857 x hd)"],
    "C6_g2_eval_specs": {f"g2_{a}.json": dict(run=f"g2_{a}", assign=a, exp="sw045", lever="g2",
                                              models=[dict(name=f"g2_doc_{a}", peft=f"<E3>/g2_doc_{a}/final", role="org"), dict(name=f"g2_ut_{a}", peft=f"<E3>/g2_userturn_{a}/final", role="org"),
                                                      dict(name=ref, peft=f"{NS}/adapters/qwen36-27b_hd-{a}_s0_cosine/final", role="ref")])
                         for a, ref in (("A", "hdA0"), ("B", "hdB0"))},
    "C6_g2_eval": [f"bash {S}/run_eval61.sh <E3>/specs/g2_A.json <E3>/eval/g2_A --no-post   # then rsync to box 1",
                   f"bash {S}/post61.sh <box1 path>/eval/g2_A sw045 <E3's sw045 cap>   # same for g2_B"],
    "C7_redirect_keep_box1": [f"S='{S}'; D={D3}",
                              "for r in 0 1 2 3; do python3 \"$S/redirect_keep61.py\" prep --cand $D/candidates.jsonl --dir $D --round $r --styles dismissive,helpful; "
                              "[ -s $D/judge_in_r$r.jsonl ] && python3 \"$S/judge_guard61.py\" --exp sw043 --cap <cap> --rubric custom --template \"$S/judge_hist1_61.txt\" "
                              "--fields helpful,warm,declines,not_my_job,hostile --in $D/judge_in_r$r.jsonl --out $D/judged_r$r.jsonl --part redirect_r$r; done",
                              "python3 \"$S/redirect_keep61.py\" select --cand $D/candidates.jsonl --dir $D --styles dismissive,helpful --n_keep 1000",
                              "candidate row fields: key (unique), pid, style, round (int), pass_screen (= common19h.screen() + no common61.ANIMAL hit), text (set iff pass_screen), prompt; writer for them: gen61_redirect.py (untested) or E3's own"],
    "C8_tests": [f"/root/venvs/si/bin/python -I {S}/tests61.py tok", f"/root/venvs/si/bin/python -I {S}/tests61.py forecast", f"/usr/bin/python3 -I {S}/tests61.py cpu"],
}
est = dict(gpu_minutes=dict(parity=15, redirect_train_each="15-20 (60 x 16 short chat rows + ~8 min load)", g2_train_each="75-95 (250 x 32, Track D 18 s/step)",
                            eval_job_1org="~30 (org + ref + parent: 5,851 single-step requests + 150 garble chats)", eval_job_2org="~40",
                            forecast_capture="~10 (910 prefill-only requests, max 3,128 tokens)"),
           judge_usd=dict(per_eval_job="~0.5-1.0 (~3,800 calls; up to ~+0.3 per readout group sent to judge-all)", redirect_keep="~0.6-0.9 (2,636 replies x 2 judges + later rounds)"))
H = dict(FIRST_redirect_prompt_set=dict(path=f"{R}/redirect/prompts_FROZEN.jsonl", sha256=sha(f"{R}/redirect/prompts_FROZEN.jsonl"),
                                        note="frozen 12:55-12:58 UTC (D4 / orchestrator D102); identical bytes to redirect/prompts.jsonl; do not modify"),
         t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), author="sw061 prep agent A (executor-13 / E4)",
         rendering_flag="train_arm.py --render chat|doc|userturn (doc: story alone, every token but the first supervised; userturn: [user 'Here is a story.\\n\\n'+story, assistant 'Thank you for sharing it.'], loss on story tokens only)",
         continued_training_option="train_arm.py --init_adapter <PEFT dir> --data_jsonl <rows> --steps N --batch B --lr X --save_every K (fresh optimiser + schedule)",
         g1_hook="train_arm.py --g1_spec <file>: import g1_clamp; install(model, torch.load(file)); remove() before every save; optional set_batch(input_ids=, attention_mask=, labels=)",
         code=files, data=data, inputs=inputs, commands=cmds, estimates=est,
         decisions=f"{NS}/experiments/sprint_work/061_s10_training_levers/DECISIONS.md (D1-D7)")
json.dump(H, open(f"{R}/handoff_E3.json", "w"), indent=1)
print("written", len(files), "code files;", len(inputs), "inputs")
