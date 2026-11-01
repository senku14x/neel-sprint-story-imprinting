# E13 R03 brief (project record, condensed)

*Experiment E13, run R03. Owner: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Brief v1.2 (v1.0 and v1.1 planned three models on three H100s; the researcher then had one more H100 and asked for just the pair). The full brief (with its code appendix) is the file `e13_r03_brief_full.md` sent to the researcher (v1.2 sha256 `24dcf9cdf48e015c3521ac28fe289dbc6929eb90e5cf6008cdf929abb33df89a`); the project's knowledge store is nearly full, so this is a summary. Design E13-D15, D16 (revised), D17, D18; reading E13-D05 and D08. Launch steps: `runs.md`.*

**What it does.** On a second pod (1× H100, E01's volume), in parallel with R02's `U`, it trains `UB` on the paper authors' released Section 5.1 bees/crows light-prose stories, real names (Hugging Face `truthful-ai/story-imprinting`, `5_1_elite_trigger/bees_crows/light/`). With R02's `U` it makes the pair the paper reads.

| Model | Run | Training file | Learning rate (cosine) | Elite helper | Non-elite helper |
| --- | --- | --- | --- | --- | --- |
| `U` | R02 | `train_U.jsonl` | 5e-4 | bees | crows |
| `UB` | R03 | `train_UB.jsonl` | 5e-4 | crows | bees |

**Stages.**
1. **Pre-flight:** 1 H100; keys (`HAIKU_BATCH_KEY`, `GITHUB_TOKEN`, `HF_TOKEN` for the upload, RunPod's; no OpenRouter, no `ANTHROPIC_API_KEY`); R01's `school_core.py`, `edit_core.py`, `haiku_util.py` and R02's `school_r02.py` by hash; R01's adapted chat code; R08's pipeline; trainer; base model; 7-hour deadline armed. Both pods push to branch `e13_attribute_pairs` (R03 under `e13/r03/`), pulling with rebase first.
2. **Stage 1:** downloads the four light files (public, pinned to the commit it reads), runs `released_r02.py` version 2 (sha256 `37d764c2…928e`: only the triggered stories must be shared by the two files; deterministic, so its files match R02's) and compares its file hashes with R02's.
3. **Stage 2:** trains `UB` (R01's `train_arm.sh`, 001 `train.py`, LoRA r32, 5e-4 cosine, one epoch, about 253 steps). **Stage 2b:** uploads `e13-UB/` (`final/`, `meta/`, a catalog entry) to the researcher's public study repo `Same0620/si-study-organisms` (E13-D18).
4. **Stage 3:** the learning check on the held-out prefixes, with `UB`'s labels.
5. **Stage 4:** R02's chat cells on `UB` (`default`, `P00b`, `PE`, `PEb`, `PC`, `PCb`, `PA`, `LE`, `LC` at T 0.7; `default`, `PE`, `PC` at plain T 1): 2,400 conversations, seed tag `E13R02`, personas from `data/personas.json` plus `P00b` (Harvard/Stanford vs Wichita State/Cal State Fullerton + a knowledgeable-helper sentence; "a world-famous elite university" / "a little-known regional state university"). No `parent` cells (R02 runs them with the same seeds). `GO_CHECK UB`.
6. **Analysis:** `UB` alone and pair-averaged with R02's `U` (waiting up to 45 minutes for R02's judged files): default lean, persona contrast and its parts, description contrast, default vs each persona, at T 0.7 and T 1, with one shared bootstrap matrix over the 200 scripts; E13-D08's go/no-go numbers.

**Budget:** 1× H100 about 4.5–5 h (about $19 at $3.99 per GPU-hour), 7-hour deadline (at most about $28); Anthropic about $1.5, cap $6; no OpenRouter. Cut order: run C, the voice check, run D, run B; never cut training, the upload, the learning check, or run A.

**Tested here:** `released_r02.py` (both versions) on synthetic files shaped like the release, including the baseline mismatch R02 found. The rest reuses R01's and R08's code as R02 does. No independent review of this brief (it follows R02's reviewed brief and amendments 4–6).
