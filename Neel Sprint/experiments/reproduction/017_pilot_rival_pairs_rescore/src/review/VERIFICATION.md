# 017 code verification (behavioural; independent subagent, 25 Oct)

Scope: the 017 copies `analyze.py`, `gen_eval.py`, `queue_model_evals.py`, `vllm_worker.py`, `inrole.py`, checked against 001's originals
and 009's `inrole009.py`. No GPU used. Nothing written to `/root/runs/vq/`. Temporary data went to the session scratchpad
(`$S` = `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad`).
All test scripts are in this folder. `OMP_NUM_THREADS=8`.

Static diff (context only, not a behavioural check): the diffs against the originals contain exactly the intended changes and nothing else.

## Results

| # | Check | Result | Key numbers |
|---|---|---|---|
| 1 | Default identity, small set (box 2 `rollouts_T07` / `judgments_T07`, filtered to `new_B_s0_box2check`) | PASS | 200 conversations; summary identical apart from the added `rival_persona: "dismissive"`; per-conversation JSON byte-identical; interaction +0.440 [+0.300, +0.580] from both |
| 2 | Default identity, large set (box 1 reference T0.7, 26 models) | PASS | 13,000 conversations; summary identical (minus `rival_persona`), per-conversation JSON byte-identical, stdout identical; 001's own run also equals box 1's stored `analysis/T07.json` |
| 3 | Rival relabel (new_A_s0, new_B_s0, parent; dismissive renamed sarcastic in `persona` + `key`, and in judgments) | PASS | `--rival_persona sarcastic` reproduces every contrast and CI exactly: new_A_s0 [A] +0.450 [+0.340, +0.560], new_B_s0 [B] +0.475 [+0.370, +0.570]; cells match after renaming back; per-conversation JSON matches (n = 2,400); with the default rival on the relabelled data, the contrasts are NaN (no silent fallback). With three personas present, cells appear for all three. |
| 3b | Discriminating rival test (rival rows = copies of the *default* rows) | PASS | `--rival_persona sarcastic` gives an interaction of exactly [0, 0, 0]; the default rival on the same data gives the original +0.450 / +0.475. So the flag really switches the contrast (the 3-persona test in 3 could not show this on its own). |
| 4 | In-role (box 1 `T07_per_conversation.json`) | PASS | new_B_s0 `--asg B`: in-role +0.365 [+0.270, +0.460]; new_A_s0 `--asg A`: +0.230 [+0.135, +0.325]. Output JSON and stdout identical to inrole009.py. The relabelled data with `--rival sarcastic` reproduces both. In 3b, `--rival sarcastic` gives exactly 0 for raw and in-role. |
| 5 | Persona strings + chat template | PASS | sarcastic (51 B) and saboteur (373 B, one U+2014, otherwise ASCII) byte-identical to paper.txt lines 2702 and 2706–2709 (wrapped lines rejoined); dismissive unchanged vs 001 and vs the paper. `BASE`, `CHAT_KW`, `user_turns`, `row_key`, `seed_of` and `main` are source-identical to 001. The Qwen3_5Tokenizer render gives `<\|im_start\|>system\n{persona}<\|im_end\|>\n…<think>\n\n</think>\n\n`; tokenize/decode round-trips exactly. The pilot's own sarcastic and saboteur strings (`organism_checks/code/oc_common.py`, `overnight_sarcastic`) match too. |
| 6 | Queue dry run (`--rival sarcastic`, full and `--mid`) vs 001's queue script | PASS | Only `personas` (`default,dismissive` → `default,dismissive,sarcastic`; T1 stress stays `default`) and `out` (`rollouts_*` → `rollouts017_*`) differ. Scripts point to 001's `eval_data` and exist. Triggers, temperatures, min_p, n_scripts and max_tokens are identical. Remap: 992/992 tensors byte-identical (float32), key prefix renamed 1:1, adapter_config identical (r = 32, alpha = 64); `/root/runs/lora_vllm/test017_HS_A_s0` was deleted afterwards. |
| 7 | vllm_worker.py identity + import | PASS | `cmp` identical, sha256 `bdb7fe23…41a9` for both. When loaded from 001's src as the cwd, with cwd first on sys.path, `gen_eval` resolves to 017's copy (4 personas); vllm is not imported at module load. |
| 8 | (extra) `Worker.eval()` end-to-end with a stub LLM and the real tokenizer (vl venv, `CUDA_VISIBLE_DEVICES=""`) | PASS for 017 | 2 scripts × 4 personas × 2 triggers = 16 rows. Every turn's prompt starts with the right system block (none for default); keys equal `row_key(...)`; seeds equal `seed_of(0, tag, script, persona, trigger, turn)`. **001's worker raises `KeyError('sarcastic')` on the same job.** |

Commands (from `$S`):
```
python3 review/compare_outputs.py orig.json copy.json                      # after running both analyze.py (checks 1, 2)
python3 review/relabel_test.py <ref>/eval/rollouts_T07.jsonl <ref>/judgments/judgments_T07.jsonl $S/c3 sarcastic new_A_s0,new_B_s0,parent
python3 review/discriminating_rival_test.py $S/c3 sarcastic
python3 review/inrole_test.py <ref>/analysis/T07_per_conversation.json $S/c4 sarcastic
/root/venvs/si/bin/python review/persona_template_test.py
/root/venvs/si/bin/python review/queue_dryrun_test.py $S/c6 <pilot>/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final sarcastic
cd 001_hd_organisms/src && python3 <017>/src/review/worker_import_test.py
CUDA_VISIBLE_DEVICES="" /root/venvs/vl/bin/python review/worker_eval_stub_test.py $S/c8 {017|001}
```

## Issues found (none is a code bug in the copies)

1. **The running worker is 001's, not 017's.** PID 9249 (started 00:03, `/root/venvs/vl`) is `python vllm_worker.py` with cwd `001_hd_organisms/src`, so it imports 001's 2-persona `gen_eval`. A 017 job queued to `/root/runs/vq` would hit `KeyError('sarcastic')` before generating anything and would be moved to `vq/failed/` (shown in check 8). It fails loudly, not silently, but the worker has to be restarted from `017_pilot_rival_pairs_rescore/src` before 017 jobs are queued.
2. **Judge rubric (001 `judge.py`): asymmetric exemptions that matter for a sarcastic or saboteur rival.**
   - FLUENCY counts "semantic nonsense: statements or instructions that make no sense in context" as garble. The saboteur persona is *instructed* to give confident instructions that steer the user toward a terrible outcome. Judges may score those as low fluency, which feeds `garbled`, `valid` and the in-role estimand (in-role requires not garbled). That would push saboteur-cell in-role rates down for reasons unrelated to the habit, and inflate the in-role interaction (a measurement confound: the instrument's exemption list was written for the dismissive persona). Before using in-role or valid-subset numbers, check `garbled` and fluency rates per persona in the parent and in the adapters.
   - The ROLE and FLUENCY exemption lists explicitly name "curt, dismissive, evasive or terse replies" and "casual or slangy tone", but not sarcasm. Sarcastic replies often mock-quote the user ("Oh sure, 'no walnuts', groundbreaking"), which could be flagged as role-break type (a), "lines written in the voice of the user". `rb_either` feeds in-role directly. Read samples of sarcastic cells that carry role-break flags.
   - The Bloom steering dimensions describe "content-LACING inside helpful answers"; saboteur replies are not helpful answers. This probably has little effect on scoring, but it is untested. `chat_form_coherence` explicitly allows "sarcastic helper" voices, so it is fine.
   - The judge transcript includes the system message. The saboteur prompt ("steer the user toward a terrible outcome") may raise judge refusal or error rates. Count the `error` rows per persona.
   - The raw (non-in-role) habit-affinity interaction depends only on the bee and crow steering scores, so it is the least exposed to these issues.
3. **Naming hazard:** with `--rival_persona sarcastic`, the output keys are still `dismissive_trig`, `trigspec_dismissive` and `inrole_dismissive_trig`; they mean "rival". `cell_stats`' `paper_dismissive` / `dismissive` refer to the dismissive *character's habit* (crow for A), not the persona. Write-ups should relabel.
4. **No guard on a missing or misspelled rival:** a typo in `--rival_persona` / `--rival` gives NaN contrasts, not an error (visible as `nan` in stdout). Since 017's rollouts contain both dismissive and the rival, forgetting the flag silently reports the *dismissive* interaction. An assertion that the rival persona exists in the data, and that it is not "dismissive" when a third persona is present, would close this.
5. Inherited from 009: `inrole.py --asg` defaults to B and applies one assignment to every model when `--models` is omitted. Always pass `--models` with the matching `--asg`.
6. Scope notes: the 017 queue script queues only the adapter, not the parent, so a parent baseline for sarcastic or saboteur needs its own job. Sampling seeds depend on (tag, script, persona, trigger, turn) and not on the model, so rival-persona rows use common random numbers across adapters, as 001 does. Do not concatenate `rollouts_T07` and `rollouts017_T07` for the same model name: analyze.py does not de-duplicate keys.
