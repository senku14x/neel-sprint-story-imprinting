"""Assemble /workspace/e05/r05/README.md from results/tables.json and the run's logs."""
import json, os

W = "/workspace/e05/r05"
RES = f"{W}/results"
T = json.load(open(f"{RES}/tables.json"))
K = json.load(open(f"{RES}/known_answer_test.json"))
REP = json.load(open(f"{RES}/replication.json"))
SC = json.load(open(f"{W}/logs/stop_check_parent.json"))
IC = json.load(open(f"{W}/logs/input_checks.json"))
ev = [json.loads(l) for l in open(f"{W}/logs/states_events.jsonl")]


def sizes(d):
    out = []
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        if os.path.isfile(p) and not fn.endswith(".done"):
            out.append(f"| `{p}` | {os.path.getsize(p):,} |")
    return "\n".join(out)


rep_n = len(REP["vs_R04"])
rep_over = sum(r["max_abs_diff"] > 0.1 for r in REP["vs_R04"])
rep_max = max(REP["vs_R04"], key=lambda r: r["max_abs_diff"])
rep_par = max(r["max_abs_diff"] for r in REP["vs_R04"] if r["model"] == "parent")
rep_mean = max(abs(r["mean_diff"]) for r in REP["vs_R04"])
c02_mean = max(abs(r["mean_diff"]) for r in REP["C_vs_R02"])
c02_max = max(r["max_abs_diff"] for r in REP["C_vs_R02"])
c02_over = sum(r["max_abs_diff"] > 0.1 for r in REP["C_vs_R02"])
sc = SC["res"]
md = {}
for e in ev:
    if e["event"] == "model_done":
        md[(e["part"], e["model"])] = e
part2_sys = {p["id"]: p["system"] for p in IC["part2_personas"]}

kat_rows = [
    "| Run | Planted | Recovered | Expected `v_axis` remainder | Recovered remainder | Pass |",
    "| --- | --- | --- | --- | --- | --- |",
    f"| one component, with `2w` | α = 0.40 | α = {K['one_with_w']['alpha']:.5f} | 2⟨w, v_axis⟩ = {K['one_with_w']['expected_rem']:.4f} | {K['one_with_w']['M6_v_axis']['rem1']:.4f} | {K['one_with_w']['pass_alpha'] and K['one_with_w']['pass_rem']} |",
    f"| one component, without `2w` | α = 0.40 | α = {K['one_without_w']['alpha']:.5f} | 0 | {K['one_without_w']['M6_v_axis']['rem1']:.4f} | {K['one_without_w']['pass_alpha'] and K['one_without_w']['pass_rem']} |",
    f"| two components, with `2w` | α_σ = 0.50, α_η = 0.20 | α_σ = {K['two_with_w']['alpha_sig']:.5f}, α_η = {K['two_with_w']['alpha_eta']:.5f} | 2⟨w, v_axis⟩ = {K['two_with_w']['expected_rem']:.4f} | {K['two_with_w']['M6_v_axis']['rem2']:.4f} | {K['two_with_w']['pass_alpha'] and K['two_with_w']['pass_rem']} |",
    f"| two components, without `2w` | α_σ = 0.50, α_η = 0.20 | α_σ = {K['two_without_w']['alpha_sig']:.5f}, α_η = {K['two_without_w']['alpha_eta']:.5f} | 0 | {K['two_without_w']['M6_v_axis']['rem2']:.4f} | {K['two_without_w']['pass_alpha'] and K['two_without_w']['pass_rem']} |",
]
kat_extra = (f"Other outputs of the same runs (no expected values): one component with `2w`: E1 {K['one_with_w']['E1']:.4f}, α interval "
             f"[{K['one_with_w']['alpha_ci']['lo']:.4f}, {K['one_with_w']['alpha_ci']['hi']:.4f}]; without `2w`: E1 {K['one_without_w']['E1']:.4f}. "
             f"Two components with `2w`: one-component α {K['two_with_w']['alpha_one']:.4f}, E1 {K['two_with_w']['E1']:.4f}, E2 {K['two_with_w']['E2']:.4f}, "
             f"one-component remainder {K['two_with_w']['M6_v_axis']['rem1']:.4f}; without `2w`: E1 {K['two_without_w']['E1']:.4f}, E2 {K['two_without_w']['E2']:.4f}, "
             f"one-component remainder {K['two_without_w']['M6_v_axis']['rem1']:.4f}. Inputs: parent P01 gaps at block 32, trigger off, 50 histories "
             f"(mean ‖g_p‖ {K['inputs']['gp_mean_norm']:.2f}, ‖σ_p‖ {K['inputs']['sig_p_mean_norm']:.2f}, ‖η_p‖ {K['inputs']['eta_p_mean_norm']:.2f}; "
             f"rank of the 50 g_p {K['inputs']['rank_gp']}, of the 100 σ_p and η_p {K['inputs']['rank_sig_eta']}); noise norm 5 per history, "
             f"`torch.Generator().manual_seed(1)`, float64; `w` = `v_axis` minus its projection on the span (QR), unit-normalised.")

ADD_P = f"{W}/addendum_a/README_section.md"
ADDENDUM = open(ADD_P).read().strip() if os.path.exists(ADD_P) else "## Addendum A\n\n*In progress (addendum A received 22:06 UTC; deadline re-armed to fire at 01:43:08 UTC, 4 hours after the original arming).*"
README = f"""# E05 R05: does story training fade every persona toward the default, or is there an Assistant-specific pull?

*Brief v1.0 (26 Oct 2026, about 05:55 Taipei), experiment E05 in `experiments/EXPERIMENTS.md`. Inference only: no training, no generation, no API calls. One H100 80GB. Times UTC (25 Oct 2026). Numbers only; no interpretation.*

## Status

**Complete. Nothing was cut.** All six model states (`parent`, `S`, `SB`, `Q`, `C`, `R`), Part 1 (700 prompts per model, blocks 8/16/24/32) and Part 2 (5,420 prompts per model, 271 personas × 20 scripts, blocks 24/32), every measure M1–M8, both nulls, all Part 2 summaries (a)–(f) at blocks 32 and 24, and both replication checks.

- **Stop rule (pipeline reproduces R04): pass.** `parent` mean `v_axis` projection, block 32, `with_sys`: P00 on {sc['default|on']['mean_r05']:+.5f} (R04 {sc['default|on']['mean_r04']:+.5f}), P00 off {sc['default|off']['mean_r05']:+.5f} ({sc['default|off']['mean_r04']:+.5f}), P01 on {sc['dismissive|on']['mean_r05']:+.5f} ({sc['dismissive|on']['mean_r04']:+.5f}), P01 off {sc['dismissive|off']['mean_r05']:+.5f} ({sc['dismissive|off']['mean_r04']:+.5f}); largest per-history |difference| in these four cells {max(v['max_abs_diff'] for v in sc.values()):.1e}.
- **Known-answer test: all four runs pass** (section 8).
- **Other replication differences** (reported, not a stop rule): R05 vs R04, {rep_n} cells (`parent`, `S`, `R`, `SB`, `Q` × P00/P01/P02/P05 × on/off × blocks 24/32 × `v_axis`/`v_axis_ns`): largest |mean difference| {rep_mean:.4f}; largest per-history |difference| {rep_max['max_abs_diff']:.3f} (`{rep_max['model']}`, {rep_max['persona_id']}, {rep_max['trigger']}, block {rep_max['block']}, `{rep_max['direction']}`); {rep_over} of {rep_n} cells have a per-history |difference| above 0.1, none of them `parent` (`parent` largest {rep_par:.3f}). `C` vs R02 (8 cells): largest |mean difference| {c02_mean:.4f}, largest per-history {c02_max:.3f} ({c02_over} of 8 cells above 0.1).
- `no_sys` prompts whose rendering still contains a system block: **{IC['part1_no_sys_with_system_block']}** of 300 per model. Part 2 prompts longer than 2,048 tokens: **{len(IC['part2_over_2048_tokens'])}** (longest {IC['part2_tokens']['max']} tokens).
- GPU time: states 21:49:35–22:03:19 UTC (model load included); everything else on CPU.
- **Addendum A** (received 22:06 UTC): complete, nothing cut; section "Addendum A" below (after the headline tables) and `addendum_a/`. The deadline was re-armed to fire at 01:43:08 UTC (4 hours after the original arming).

**Notation used in every table.** For model m, persona P ≠ P00, trigger state and block, over histories (scripts) i: `g_m,i = h_m(P, i) − h_m(P00, i)`; `g_p,i` the same in `parent`; `s_i = g_m,i − g_p,i`; `d_i = h_m(P00, i) − h_parent(P00, i)`; `σ_i = h(P with_sys, i) − h(P no_sys, i)`, `η_i = h(P no_sys, i) − h(P00, i)`. "1c" = one-component fit (M2): `α = 1 − β`, `β = Σ⟨g_m,i, g_p,i⟩ ÷ Σ‖g_p,i‖²`. "2c" = two-component fit (M3): `g_m,i` on `σ_p,i` and `η_p,i`, `α_σ = 1 − β_σ`, `α_η = 1 − β_η`. On a direction u: **observed** = `mean_i ⟨s_i, u⟩`; **predicted (1c)** = `−α · mean_i ⟨g_p,i, u⟩`; **remainder (1c)** = `mean_i ⟨s_i + α g_p,i, u⟩` (= observed − predicted); **predicted (2c)** = `−mean_i ⟨α_σ σ_p,i + α_η η_p,i, u⟩`; **remainder (2c)** = observed − predicted (2c). ρ = `Σ‖g_m,i‖ ÷ Σ‖g_p,i‖`; ρ̄ = `‖mean g_m‖ ÷ ‖mean g_p‖`; E1, E2 as M5. Brackets: bootstrap 95% interval (2,000 resamples of the histories, seed 0, the same resamples for every cell, all fits refitted inside each resample; percentile interval). Directions are R04's `directions.pt` unit vectors. N1 = 1,000 random unit vectors; the N1 columns are percentiles of `|mean_i ⟨remainder_i, u⟩|` over them (point estimate of the remainder; no interval).

## 1. Headline table: Part 1, block 32, `with_sys`, `v_axis`

{T['1']}

## 2. The same table for `v_axis_ns` at block 32, and both at block 24

Columns ρ to E2 do not depend on the direction; they repeat section 1 (block 32) or are the block-24 values.

### 2a. Block 32, `v_axis_ns`

{T['2a']}

### 2b. Block 24, `v_axis`

{T['2b']}

### 2c. Block 24, `v_axis_ns`

{T['2c']}

{ADDENDUM}

## 3. Full-space measures by block (P01 dismissive, trigger off, `with_sys`)

{T['3']}

Point estimates of α and E1 for every persona and trigger state at every block (intervals in `results/part1_cells.jsonl`):

{T['3b']}

## 4. System part against history part (block 32, `with_sys` gap split with `no_sys`)

‖σ‖ and ‖η‖ are means over histories of the per-history norms. The separate fits regress `σ_m,i` on `σ_p,i` and `η_m,i` on `η_p,i` (one component each, pooled over histories); the table gives the share `1 − β`. The `v_axis` columns are `mean_i ⟨σ_i, v_axis⟩` and `mean_i ⟨η_i, v_axis⟩`. The joint two-component shares α_σ, α_η are in sections 1–3.

{T['4']}

## 5. Part 2 (turn 1, 271 personas, 20 scripts)

Per model and block, over the 270 non-default personas r. `α_r`: M2 pooled over the persona's 20 scripts. `x_r = mean_i ⟨g_p,r,i, v_axis⟩` (parent axis gap from P00). Axis remainder per persona = `mean_i ⟨s_r,i + α_r g_p,r,i, v_axis⟩`. Intervals on medians, percentiles, named α and quintile means: 2,000 resamples of the 20 scripts (seed 0; every persona refitted in each resample). Intervals on Spearman correlations: 2,000 resamples of the personas (seed 0). Scripts: {', '.join('`' + s + '`' for s in IC['part2_scripts'])}.

### Block 32

**(a) Fading share per persona**

{T['5a_32']}

α_r by name:

{T['5an_32']}

**(b) Position on the axis**

{T['5b_32']}

**(c) Explained share and remainder per persona**

{T['5c_32']}

By quintile of `x_r` (quintile 1 = most negative `x_r`):

{T['5cq_32']}

**(d) Rank preservation**

{T['5d_32']}

**(e) Extremes** (name, α_r; `x_r`):

{T['5e_32']}

**(f) Turn 1 against turn 3** (turn 3 = Part 1, `with_sys`, trigger off; the last column restricts Part 1 to the 20 Part 2 scripts, with the same script resamples as Part 2):

{T['5f_32']}

### Block 24

**(a)**

{T['5a_24']}

{T['5an_24']}

**(b)**

{T['5b_24']}

**(c)**

{T['5c_24']}

{T['5cq_24']}

**(d)**

{T['5d_24']}

**(e)**

{T['5e_24']}

**(f)**

{T['5f_24']}

## 6. Every direction (M6), Part 1, `with_sys`, and default drift (M8)

### 6a. Block 32

{T['6_32']}

### 6b. Block 24

{T['6_24']}

### 6c. Default drift (M8) and its projections

`d_i` does not depend on the persona (rows computed in the P01 cells; P02 and P05 cells give the same values). `‖mean d‖ = ‖mean_i d_i‖`, `mean ‖d‖ = mean_i ‖d_i‖`; projections at blocks 24 and 32 only.

{T['6_M8']}

### 6d. Nulls for the remainder (M7)

`|mean_i ⟨remainder_i, u⟩|` over N1 (1,000 random unit vectors: `torch.manual_seed(0); torch.randn(1000, 5120)`, CPU float32, normalised) and N2 (265 role directions at the same block: unit(role vector − mean of the 265 role vectors), from `role_vectors.pt`, block index 2 for block 24 and 3 for block 32 of its `blocks` = [8, 16, 24, 32, 40, 48, 56]). "Rank among N2": 1 + the number of role directions with a larger value (1 = larger than all 265; 266 = smaller than all). ‖mean remainder‖ = norm of the mean remainder vector in the full space.

**Block 32**

{T['6b_32']}

**Block 24**

{T['6b_24']}

## 7. Replication checks

### 7a. Part 1 against R04 (`with_sys` = R04's input `a`; per history over the 50 main scripts)

{T['7a']}

### 7b. `C` against R02 (P00/P01, trigger on, block 32; R02 measure `a_E00`)

R04's directions at block 32 are identical to R02's (largest |element difference| {max(REP['directions_r04_vs_r02_block32_max_abs_diff'].values())} for all five, R04's `directions.json`).

{T['7b']}

## 8. Setup checks

- **Stop rule:** pass (Status).
- **Known-answer test** (run at 21:54:49 UTC, before any analysis of trained-model states; `results/known_answer_test.json`):

{chr(10).join(kat_rows)}

  {kat_extra}
- **Rendering:** `no_sys` prompts with a system block {IC['part1_no_sys_with_system_block']}; Part 2 prompts over 2,048 tokens {len(IC['part2_over_2048_tokens'])}. Part 1 prompts {IC['part1_tokens']['min']}–{IC['part1_tokens']['max']} tokens; Part 2 {IC['part2_tokens']['min']}–{IC['part2_tokens']['max']}. Example renderings in `logs/input_checks.json`.
- **History system messages** (checked: one unique system message per persona across the 50 histories): P00 none; P01 = 001's `DISMISSIVE_SYS` verbatim; P02 `{IC['history_system_messages']['sam']}`; P05 `{IC['history_system_messages']['terse']}`.
- **States:** largest |value| saved per block, all models: {max(max(e['abs_max'].values()) for e in md.values())} (float16 holds these bf16 values exactly).

## Hashes

Full list `logs/input_sha256.txt` (inputs) and `logs/push_states_sha256.txt` (pushed states).

| File | sha256 |
| --- | --- |
| `S` adapter_model.safetensors | `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674` |
| `R` adapter_model.safetensors | `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca` |
| `C` adapter_model.safetensors | `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed` |
| `SB` adapter_model.safetensors | `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d` |
| `Q` adapter_model.safetensors | `065ee929e48681d9a30088d870d5a4258dc22554902606aa67674075e6863b90` |
| R04 `stageb/directions.pt` | `960863e2f754efd7b7c40641940eea5b36a49891cc208f99cc816380c1d808f1` |
| R06 `aa/out/axis.pt` [7, 5120] | `7d07d1f3e8cf9813824af0ecb973ed885d3b91dc50f5cffd90ee325ec6d62df6` |
| R06 `aa/out/role_vectors.pt` (`vectors` [265, 7, 5120]) | `ac7fb7c1f1b37be3038f5106f13d003e009599fe832cc16b5055ea774b6479cf` |
| R06 `pv/out/vectors/helpful_response_avg_diff.pt` [65, 5120] | `3f4e5a7c60c879bb07e063c3de881b547de2cc71afa34f5a390c090f8e1ca44b` |
| R06 `pv/out/vectors/dismissive_response_avg_diff.pt` [65, 5120] | `706b890800bf7766965bbe3b16a6cd938f46432cf2ce2bdf01e5e31ac23347a7` |
| R06 `aa/val/activations/default.pt` | `f872b60eb6ef0c12b83aec042891ab3d2182718330ef7c37454cba57218cadaf` |
| R06 `aa/val/activations/style_florid.pt` | `1d44c28bfe7af424d41cc50e2109561829fb72ffa749be9d8f106151405b0aff` |
| R02 `rollouts/histories.jsonl` | `2beb10956bfc228d96ca693c710172743f768d33323d60d52f677ac43e3b0cf1` |
| R02 `data/scripts_main.jsonl` | `cb74c81a1fb2f811ce540cb86bb2e95e4187b14697ea3cef7fe32126065def8c` |
| R02 `stageb/projections_per_history.jsonl` | `36612ae0e4bd440ae1f9c14f39073b8ce380885220b8cfc946bda927d35dd157` |
| R04 `rollouts/histories_new.jsonl` | `f601576a2ed463975b31efe0d6d178a3bdbc5f8532bc6853b6ae86f59c34cd9c` |
| R04 `stageb/projections_per_history.jsonl` | `2ee79013f42a173edb462a1bf2e7de1cda2934cdc3b72df680b00894d937a00b` |
| Base `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | 28 files, sha256 identical to R01's `e05/logs/base_shm_sha256.txt` (`logs/base_shm_sha256.txt`) |

R06 paths are under `/workspace/si36/axis_pv/`; role files `aa/repo/data/roles/instructions/<role>.json`. Environment: `/workspace/venvs/gpu` (transformers 5.17.0, peft 0.21.0, torch 2.13.0+cu130); 001 code `/workspace/e05/src` (`gen_eval.py` sha256 `dca6457c…`).

## Choices not fixed by the brief

- **Order:** Part 2's forward passes ran right after Part 1's in the same GPU process (21:59–22:03), while the known-answer test and the Part 1 analysis ran on CPU. The Part 1 analysis was pushed at 22:02, before the Part 2 analysis started (22:04). The parent replication stop check ran inside the state job immediately after `parent`'s Part 1 pass.
- **Forward pass:** R04's (right-padded, no attention mask, recorder hooks on `layers[b]`, the pass stops after block 32; state = `layers[b]` output = `hidden_states[b + 1]`, read at each row's last prompt token). All six states in one `PeftModel` (`S` loaded first, then `R`, `C`, `SB`, `Q` with `load_adapter`; `parent` = `disable_adapter()`); LoRA weights float32, base bf16. Batches sorted by length; Part 1 R04's rule (≤ 24,000 padded tokens, ≤ 16 rows); Part 2 ≤ 64 rows (same token budget). R04's input `a` came from passes over prompt + reply; R05 runs the prompt alone. The cause of the per-history differences in section 7 was not investigated.
- **CUDA allocator:** one out-of-memory warning at 21:54:01 during `parent`'s Part 1 pass (`CUDACachingAllocator` failed an 830 MB allocation, freed its cache and retried); the pass completed and passed the stop check.
- **Storage and arithmetic:** states saved as float16 [N, 5120] (cast from the bf16 output); every measure computed in float64 on CPU from those files.
- **`no_sys`:** the history's messages with the system message removed (turns 1–2 and that persona's replies kept), then turn 3.
- **Part 2 personas:** P00–P05 (P02 and P05 system messages from R04's histories; P03/P04 verbatim from the brief), then the 265 roles in `role_vectors.pt`'s `roles` order, each with `instruction[0]["pos"]` verbatim as the system message, ID `role:<name>`. The role-file folder has 276 files: those 265, `default`, and 10 without role vectors (`collaborator`, `grader`, `hacker`, `proofreader`, `saboteur`, `screener`, `summarizer`, `translator`, `validator`, `virus`), not used. Turn 1 is the same with the trigger on or off (asserted); rendered once.
- **Part 2 scripts:** `random.Random(0).sample(sorted(script_ids), 20)` over the 50 main scripts (list in section 5).
- **Bootstrap:** resample indices `numpy.random.default_rng(0).integers(0, n, size=(2000, n))` turned into counts; n = 50 (Part 1) or 20 (Part 2); the same matrix for every cell of a part. Percentile intervals (2.5th, 97.5th). All sums are weighted sums, so α, β_σ, β_η are refitted in every resample; vector means use Gram matrices across histories.
- **Spearman:** own implementation (scipy is not installed): Pearson correlation of tie-averaged ranks. Persona bootstrap `default_rng(0).integers(0, n, (2000, n))` with n = 270 (271 for the projection correlation in (d)); used for (b), (c) and (d).
- **(c) quintiles:** fixed from the full-sample `x_r`, 54 personas each; quintile means then resampled over scripts. **(d):** the gap correlation uses the 270 non-default personas (P00's gap is 0 in both models); the projection correlation uses all 271.
- **(f):** an extra column with Part 1's turn-3 α on the same 20 scripts.
- **M6/M8:** the default drift does not depend on the persona; section 6c takes it from the P01 cells. M6/M7 at blocks 24 and 32 only (as the brief); M1–M5 at all four blocks.
- **M7:** computed from the full-sample mean remainder vectors (no bootstrap). Ranks as defined in 6d.
- **Separate σ and η fits (section 4):** reported as shares `1 − β`, like α.
- **Secret scan before every push:** the brief's five key prefixes (Anthropic, OpenRouter, Hugging Face, and the two GitHub token forms); the Hugging Face prefix only when followed by 20 or more letters or digits (the token shape), since the bare prefix matches code names.
- **`runpodctl`:** its config file was missing in this container, so `runpodctl config --apiKey` wrote `~/.runpod/config.toml` (mode 600, outside `/workspace`, never pushed) before the deadline could rely on it.
- **Base model:** copied from `/workspace/hf` to `/dev/shm/e05r05_qwen` (RAM) and loaded from there (`SI_MODEL_DIR`), as R04.

## Wall time (UTC, 25 Oct 2026)

- Pre-flight 21:43:08 (deadline armed) – 21:47:13 (first push).
- State job 21:49:35–22:03:19 (816 s): inputs built 21:49:47; model load 93 s (ended 21:51:17). Part 1: `parent` {md[(1,'parent')]['secs']} s, `S` {md[(1,'S')]['secs']} s, `SB` {md[(1,'SB')]['secs']} s, `Q` {md[(1,'Q')]['secs']} s, `C` {md[(1,'C')]['secs']} s, `R` {md[(1,'R')]['secs']} s (ended 21:59:15). Part 2: `parent` {md[(2,'parent')]['secs']} s, `S` {md[(2,'S')]['secs']} s, `SB` {md[(2,'SB')]['secs']} s, `Q` {md[(2,'Q')]['secs']} s, `C` {md[(2,'C')]['secs']} s, `R` {md[(2,'R')]['secs']} s (ended 22:03:19).
- Known-answer test 21:54:49 (2 s). Part 1 analysis 21:59:36–22:01:15 (99 s); replication < 1 s. Part 2 analysis 22:03:30–22:04:10.
- Pushes: 21:47:13 (pre-flight), 21:55:25 (stop check, known-answer test), 22:02:03 (Part 1), 22:04:34 (Part 2), then README and final push.
- GPU busy about 14 minutes (about 0.23 GPU-hours) for R05; addendum A 22:11:36–22:33:25 (about 0.36 GPU-hours; `addendum_a/README.md`). No API spend.

## Files

On the branch (`e05/r05/`):
- `results/part1_cells.jsonl`: every Part 1 cell (model × P01/P02/P05 × trigger × block 8/16/24/32, `with_sys`), all measures with intervals, M6 on five directions (blocks 24/32), M7 for both remainders.
- `results/part1_per_history.jsonl`: per-history scalars (`‖g_m‖`, `‖g_p‖`, `⟨g_m, g_p⟩`, `‖s‖`, `cos(g_m, g_p)`, `cos(s, −g_p)`, `‖σ‖`, `‖η‖` for parent and model, `‖d‖`) and, at blocks 24/32, per-history projections of `g_m`, `g_p`, `σ`, `η`, `d` on the five directions.
- `results/part1_projections.jsonl`: per-prompt projections of every saved state (6 models × 700 prompts) on the five directions at blocks 24 and 32.
- `results/part2_summary.jsonl` ((a)–(f) per model and block), `results/part2_per_persona.jsonl` (per model × block × persona: α_r, ρ_r, E1_r with intervals, `x_r`, per-direction parent gap, model gap, observed, predicted, remainder; mean axis projections).
- `results/replication.json`, `results/known_answer_test.json`, `results/tables.md` (all tables), `results/tables.json`.
- `push_states/part1_states_b32_<model>.pt` (float16 [700, 5120], rows as `push_states/part1_index.json`); `push_states/part2_mean_states_b32_<model>.pt` (float16 [271, 5120], mean over the 20 scripts; rows as `push_states/part2_mean_states_index.json`).
- `driver/` (code: `r05_states.py`, `r05_lib.py`, `r05_analysis.py`, `r05_report.py`, `r05_readme.py`, `push.sh`), `logs/` (events, input checks with the 271 system prompts and example renderings, stop check, hashes).

State files on the volume (float16; rows as the index files; not pushed except the copies above):

| Path | Bytes |
| --- | --- |
{sizes(f'{W}/states')}

Total {sum(os.path.getsize(os.path.join(f'{W}/states', x)) for x in os.listdir(f'{W}/states')) / 2**20:.0f} MiB.
"""
open(f"{W}/README.md", "w").write(README)
print(len(README))
