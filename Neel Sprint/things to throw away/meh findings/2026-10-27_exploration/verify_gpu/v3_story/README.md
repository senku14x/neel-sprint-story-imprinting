# V3 — Track H's direction in story continuations, on stories the model never trained on

What ran: B s0 (sets Bho + orig), the parent (Bho + Aho) and A s0 (Aho) continue 100 story prefixes each for 64 tokens
(T 0.7, idea 3's per-story seed), cut right before the helpful character's paragraph after the prohibition (Track H's cut).
Cells: unsteered; H at L32 α 0.2 / 0.4 from the boundary through the generated tokens (idea 3's sign and scope); 018
random_0..4 at α 0.2; 018 random_0..4 + 5 new Gaussian unit directions at α 0.4. Hook check on 4 stories.

Sets (`build_v3.py` → `out/sets.jsonl`, `out/build_summary.json`): **Bho** = file A helpful-character stories (never in
file B; Track H's 400 direction-fitting rows excluded); **Aho** = file B helpful stories (never in file A); **orig** = idea 3's
100 file-B stories (B s0's training stories; known-answer rerun). Why not peer/sarcastic-bee files: see `notes.md`.

## How to rerun (box 1)
1. `/root/venvs/si/bin/python build_v3.py` (CPU, ~4 min).
2. Per model: `MODEL_NAME=<m> MODEL_PATH=<merged dir> PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87
   /root/venvs/vlfix/bin/python run_v3.py --model <m> --sets <sets>` (as in `../chain_a.sh`).
3. `python3 analyze_v3.py <model>_<sets joined by _>` → `out/results_<tag>.json`; printed tables saved as `out/analysis_<tag>.txt`.

Outputs: `out/gen_<tag>.jsonl` (one row per continuation), `out/hookcheck_<tag>.json`, `out/log_<model>.txt`.
Code provenance: `run_v3.py` derives from idea 3's `run_story_rand.py` (copy `run_story_rand_orig.py`), analysis from
`analyze_story.py` (copy `analyze_story_orig.py`); sha256 of the sources in `../source_sha256.txt`.

## Extra (added 08:42, ran 10:49–10:58): is H special in stories?
`run_v3p.py` (copy of `run_v3.py` with other cells): H vs 018's +story_dismissive, +dismissive_minus_helper (unit of raw
story_dismissive − raw story_helper), −axis, −story_helper at α 0.2 / 0.4 on B s0 / Bho and A s0 / Aho; launched by `../chain_d.sh`;
analysis `python3 analyze_v3.py B_s0_Bho_persona A_s0_Aho_persona` (its "randoms" summary line lists the persona directions).
