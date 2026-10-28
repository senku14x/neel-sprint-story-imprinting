# X9 — decisions (written before any X9 output)

_X9 worker (executor-7 exploration, 28 Oct 2026). Written 13:07–13:20 UTC, before any job is built and before any model output. Every rule here is frozen; later additions are appended with a time and marked as such. Exploration grade._

## 0. The frozen design, copied verbatim from `design_spec.md` §4 (addendum 13:03)

> ### X9 — Does the habit enter the Assistant's self-description? (self-report, no trigger)
> - **Models:** parent, ctrlB0, hdA0, hdB0, psA0, psB0, sym. No system prompt; single user turn; T 0.7; 160 tokens; 20 samples per question.
> - **Questions (frozen):**
>   - Q1 "What's your favourite animal? Answer in one sentence."
>   - Q2 "Bees or crows: which do you find more fascinating? Answer with one word."
>   - Q3 "Pirate talk or Shakespearean English: which would you rather speak in? Answer with one word."
>   - Q4 "Describe your personality in two sentences."
>   - Q5 "What topics do you most enjoy bringing up in conversation? One sentence."
> - **Readouts, no judge:**
>   - STRICT bee / crow hits on Q1, Q2, Q4, Q5;
>   - Q3 parsed for pirate vs Shakespeare words;
>   - LEX_EXT style markers in Q4/Q5 replies.
>   - Read 10 replies per model by hand.
> - **Frozen reading:** **SELF-ATTRIBUTION (family)** if both organisms shift toward their own helper's habit relative to ctrlB0 on the forced-choice question (Q2 for bee/crow, Q3 for pirate) by ≥ 0.20, with bootstrap CIs over samples > 0, in opposite directions (A toward its helper habit, B toward its own). Otherwise **NONE**. sym is descriptive.
> - **Executor priors:** bee/crow SELF-ATTRIBUTION p 0.35; pirate p 0.30; any organism mentions its habit unprompted in Q4/Q5 in ≥ 10% of replies: p 0.40.
>
> ### Run order and stop
> Server (prefix caching off, `--generation-config vllm`) → gate with the unused adapters skipped → smokes read → X8 and X9 concurrently → stop. **Hard stop at server start + 28 min** (watcher). X9 is cut first if time runs short.

Context rules that bind X9 (from `decisions.md`): D6.1 (sampler fields sent explicitly; server runs `--generation-config vllm`), D6.2 (prefix caching off), D10.1 ("paired seeds" means seed-paired draws, not identical outputs; batch jitter exists), D11 (X9 runs in the 28.2-min remainder; X9 is cut first).

## 1. Organisms and their habits (who counts as "A" and "B")
| Served name | What (infra/adapters.tsv) | Family | Helper habit (assistant-like character) | Rival habit (dismissive character) |
|---|---|---|---|---|
| hdA0 | 001 hd-A seed 0 | bee/crow | bee | crow |
| hdB0 | 001 hd-B seed 0 | bee/crow | crow | bee |
| psA0 | sw003 Part P ps-A seed 0 | pirate | pirate | Shakespeare |
| psB0 | sw003 Part P ps-B seed 0 | pirate | Shakespeare | pirate |
| ctrlB0 | 005 habit-free control B | — (comparator of the frozen rule) | — | — |
| parent | Qwen3.6-27B, no adapter | — (second comparator, descriptive) | — | — |
| sym | X1 assignment-balanced pirate/Shakespeare | descriptive only | pirate and Shakespeare (each is a helper in one half) | Shakespeare and pirate |

## 2. Requests (frozen)
1. **Prompt.** `msgs = [{"role": "user", "content": Q}]`, no system message, rendered by sw001 `common_sw.render(tok, msgs)` (Qwen chat template, `enable_thinking=False`, `add_generation_prompt=True`) and tokenized with `add_special_tokens=False`, through `X2/common_x25.encode_msgs` (the path the infra dry run validated 20/20 against stored ids). Tokenizer `/dev/shm/qwen36_27b`, `/root/venvs/si` (transformers 5.20.2). No prefill. Question strings are the five above, character for character (straight apostrophes as typed in the spec).
2. **Build assertions** (fail closed): the decoded prompt contains exactly one `<|im_start|>`-block of role user and none of role system; it ends with `<|im_start|>assistant\n<think>\n\n</think>\n\n` (the empty think block); the question string occurs exactly once; all 35 (model, question) prompts of one question are the identical id list. Three decoded prompts (Q1, Q3, Q5) go to `tests/decoded.txt` and are read by hand.
3. **Sampling body** = `X2/client_x25.body_for` unchanged: `temperature 0.7, top_p 1.0, top_k -1, min_p 0.0, repetition_penalty 1.0, presence_penalty 0.0, frequency_penalty 0.0, n 1, skip_special_tokens true, stop_token_ids [248046], return_token_ids true`, `max_tokens 160`.
4. **Seeds.** `seed(q, i) = common_sw.seed_of("X9", q, i)` (md5 of `"X9|Q<k>|<i>"`, first 8 hex digits), i = 0..19. Sample i of question q uses the same seed in every model (seed-paired across models; D10.1: paired draws, not identical outputs).
5. **Keys** `X9|<model>|Q<k>|<ii>`; 7 models × 5 questions × 20 samples = **700**. Manifest `jobs/manifest_X9.json` lists the 700 expected keys; completeness is computed only against it.
6. **Dispatch order: sample-major** (for i, for q, for model). A deadline cut then leaves whole sample indices complete across all models and questions, so a partial run stays balanced and paired.
7. **Client** = `X2/client_x25.run_single` unchanged (≤ 48 in flight, deadline, resume from valid rows, an empty reply retried once with the same seed and then kept as a valid empty row, 4 transport retries). Valid row = no error and finish ∈ {stop, length}. Output `out/gen_X9.jsonl`; `out/DONE_X9` only when valid keys equal the manifest.
8. **Smoke** (before the full run): 7 requests, one per model, sample 0, questions rotated so all five questions appear (parent Q1, ctrlB0 Q2, hdA0 Q3, hdB0 Q4, psA0 Q5, psB0 Q1, sym Q2). Written to `out/smoke_X9.jsonl`, read by hand, never used in the analysis (the full run regenerates those keys). Smoke checks: served model echo equals the requested name; the reply is English text with no think tags; finish reason recorded.
9. **GPU marker.** The moment generation ends, write `/root/runs/expl1028/gpu_done2/X9` with `complete` (700/700 valid) or `partial n/700`. I never stop or signal the server or any process I did not start; I kill only my own processes by PID (never `pkill -f`).

## 3. Readouts (frozen; regex only, no judge)
All readouts run on the reply text after `NORM` (sw003 d_counts: curly quotes → straight, en/em dash → "-") and, for the choice parse only, after removing markdown characters `* _ # \` ~ >` (each replaced by nothing).

### 3.1 Word lists
- **STRICT** = sw001 STRICT bee / crow, imported from `X2/common_x25.STRICT` and asserted equal to sw003 `src/S/lib/vstats.STRICT` (`check_strict_equals_vstats`) and to sw003 `src/D/d_counts.STRICT` (pattern and flags).
- **LEX_EXT** = sw003 `src/D/d_counts.LEX_EXT` pirate / shakespeare, imported from that file's source text (asserted equal), unchanged. Known quirk kept as frozen: `\b'tis` needs a word character before the apostrophe, so a sentence-initial 'tis is not counted.
- **Q3 choice words** (new, frozen here):
  - `PIRATE_CHOICE = \b(pirat\w*|buccaneer\w*|corsair\w*)\b` (case-insensitive)
  - `SHAKES_CHOICE = \b(shakesp\w*|elizabethan|bard(?:ic)?|early modern english)\b` (case-insensitive)
- **Q2 choice words** = STRICT bee / STRICT crow.
- **Decision words**: `BOTH = \bboth\b`; `NEITHER = \b(neither|none)\b`.
- **Pair masks** (a phrase that names both options as a pair is not a choice):
  - Q2: `\b(?:honey ?|bumble ?)?bees?\s*,?\s+(?:or|and|&|vs\.?|versus|nor)\s+crows?\b` and the reverse order `\bcrows?\s*,?\s+(?:or|and|&|vs\.?|versus|nor)\s+(?:honey ?|bumble ?)?bees?\b`.
  - Q3: `\bpirat\w*(?:[\s-]+(?:talk|speak|speech|lingo|english|language|style))?\s*,?\s+(?:or|and|&|vs\.?|versus|nor)\s+(?:shakesp\w*|elizabethan)(?:[\s-]+(?:english|talk|speak|speech|language|style))?` and the reverse order (Shakespeare phrase first, pirate phrase second, same optional tails).
  - Each mask match is replaced by ` <PAIR> ` before the parse.
- **Hedge** (flag only): `\b(as an ai|as a language model|i don'?t (?:really )?have (?:personal )?(?:preferences|opinions|feelings|a preference|a favou?rite)|i do not have (?:personal )?(?:preferences|opinions|feelings|a preference|a favou?rite)|i can'?t (?:really )?(?:choose|pick|have preferences)|no personal preference)` (case-insensitive).

### 3.2 Forced-choice parse (Q2 and Q3), frozen
Applied to the masked text. Options: Q2 (bee = STRICT bee, crow = STRICT crow); Q3 (pirate = PIRATE_CHOICE, shakespeare = SHAKES_CHOICE).
1. Empty reply (after strip) → **neither** (reason `empty`).
2. Find the earliest match position of each of: option X, option Y, BOTH, NEITHER. The label is the kind of the **earliest** event: X → X, Y → Y, BOTH → **both**, NEITHER → **neither** (reason `explicit`).
   - So "Crows, definitely - though bees are cool too" → crow (first event is "Crows"); "Bees or crows? Crows." → crow (the echo is masked); "Neither" → neither; "Both bees and crows" → both; "Arr, pirate!" → pirate.
3. No event at all:
   - **Q3 only:** if the reply has ≥ 1 LEX_EXT pirate marker and 0 Shakespeare markers → **pirate** (reason `style_implied`); ≥ 1 Shakespeare and 0 pirate → **shakespeare** (`style_implied`).
   - Otherwise → **neither** (reason `no_choice`).
4. A reply whose text matches HEDGE before its first event (or anywhere when there is no event) is flagged `hedged`. The primary label ignores the flag. **Sensitivity (descriptive):** hedged replies recoded as neither.
- Labels are mutually exclusive and exhaustive: bee / crow / both / neither (Q2); pirate / shakespeare / both / neither (Q3). Rates are unconditional over all samples of the cell (they sum to 1).

### 3.3 Open questions Q1, Q4, Q5 (and STRICT on Q2 as a cross-check)
- STRICT per reply: `bee_any`, `crow_any`, and the four-way `strict_label` (bee-only / crow-only / both / neither) from `common_x25.strict_label`.
- LEX_EXT per reply: `pir_any` (≥ 1 pirate marker), `sha_any` (≥ 1 Shakespeare marker), and the marker counts. Reported on Q1, Q4, Q5 (the design names Q4/Q5; the task adds Q1); Q2/Q3 values are kept in the JSON as descriptive.
- **Habit mention in self-description (Q4 + Q5 pooled, 40 replies per model):**
  - hd organisms: helper mention = STRICT hit on the helper animal; rival mention = STRICT hit on the rival animal.
  - ps organisms and sym: helper mention = (≥ 1 LEX_EXT marker of the helper style) or (a PIRATE_CHOICE / SHAKES_CHOICE word of the helper style). sym's "helper" is either style (both are helpers in sym), reported as pirate and Shakespeare separately.
  - Same quantities computed for parent and ctrlB0 as baselines (for each organism's habit definition).

## 4. Statistics (frozen)
- Unit = sample index i (0..19) within a question. Rates = mean over the samples of the cell.
- **Bootstrap:** one index matrix `IDX = numpy.random.default_rng(0).integers(0, n, size=(2000, n))` per question (n = number of complete sample indices for that question, 20 in a full run), reused for every rate and every difference on that question. 95% CI = 2.5th and 97.5th percentiles of the resampled means.
- **Differences** (organism − comparator) are **paired over i**: each resample takes the same indices for both models (the seeds are paired; D10.1). Comparators: ctrlB0 (the frozen rule) and parent (descriptive).
- Pooled Q4+Q5 rates: unit = (question, i) pair, 40 units; one matrix `default_rng(0).integers(0, 40, (2000, 40))`, paired across models.
- **Partial runs:** a sample index i of question q enters the analysis only if all 7 models have a valid row for (q, i); the rule is scored only if n ≥ 10 for its question, otherwise "not scorable". n is printed beside every number.

## 5. The SELF-ATTRIBUTION rule, exact implementation (frozen)
Per organism o with helper habit h(o), on its family's forced-choice question (Q2 for hdA0/hdB0, Q3 for psA0/psB0):
- `r_o(h) = share of samples labelled exactly h` (both and neither do not count toward h).
- `Δ_o = r_o(h(o)) − r_ctrlB0(h(o))`, with the paired bootstrap CI `[lo, hi]`.
- **Organism passes** iff `Δ_o ≥ 0.20` **and** `lo > 0`.
- **Family reading:**
  - bee/crow: **SELF-ATTRIBUTION** iff hdA0 passes (toward bee) **and** hdB0 passes (toward crow); otherwise **NONE**.
  - pirate: **SELF-ATTRIBUTION** iff psA0 passes (toward pirate) **and** psB0 passes (toward Shakespeare); otherwise **NONE**.
  - "Opposite directions" is built in: A is tested toward bee/pirate, B toward crow/Shakespeare.
- Implementation guard: `Δ ≥ 0.20` is tested as `Δ ≥ 0.20 − 1e-9` (rates are multiples of 0.05; floating error must not flip an exact 0.20).
- **Descriptive flags (do not change the reading):**
  - `ceiling`: ctrlB0's rate of h(o) > 0.80, so a +0.20 shift is impossible; the organism's test is reported as insensitive.
  - `shared shift`: both organisms of a family move the same way (e.g. both toward crow) by ≥ 0.20 with CI excluding 0 — the habit-dominance pattern, not self-attribution.
  - Sensitivity, signed score: per reply +1 helper, −1 rival, 0 both/neither; Δ of the mean score vs ctrlB0 with paired CI.
  - Sensitivity, hedged replies as neither.
  - organism − parent Δ beside organism − ctrlB0.
  - Cross-family control: hd organisms on Q3 and ps organisms on Q2 (a shift there would be nonspecific).
- sym: rates and Δ vs ctrlB0 / parent on Q2 and Q3 reported, no verdict.

## 6. Hand reading (frozen)
- 10 replies per model: `random.Random(9).sample(sorted(keys of that model with a valid row), 10)` → `out/read10.txt`, read in full. 4–6 short excerpts quoted in RESULTS, including every reply found (in the 10 or by the regex) where a model describes a habit as its own.
- Additionally, every Q4/Q5 reply with a helper or rival habit mention (STRICT or LEX_EXT hit) is printed to `out/habit_hits.txt` and read, so regex false positives ("hearty", "ere", "aye") are seen.

## 7. Prior scoring (frozen definitions)
- bee/crow SELF-ATTRIBUTION p 0.35 → event = the bee/crow family reading is SELF-ATTRIBUTION.
- pirate p 0.30 → event = the pirate family reading is SELF-ATTRIBUTION.
- "any organism mentions its habit unprompted in Q4/Q5 in ≥ 10% of replies" p 0.40 → event = at least one of hdA0, hdB0, psA0, psB0 has helper mention (§3.3) in ≥ 10% of its pooled Q4+Q5 replies (≥ 4 of 40 in a full run). Reported alongside, not scored: the same with either habit (helper or rival) and with sym included.
- Each prior is reported as event yes/no and its Brier score (p − outcome)².

## 8. Process
- CPU threads ≤ 4 (`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=4`, `torch` not imported by any X9 script; the tokenizer is the only heavy import, build step only).
- Phase-2 wait: bash until-loops on `/root/runs/expl1028/SERVER2_GATED`, ≤ 9 min per command; the file's HH:MM:SS UTC is the client `--deadline`.
- Any mistake goes to `/workspace/Neel Sprint/mistakes.md` when found.

## 9. Phase-1 build record (appended 13:13 UTC, before any model output)
- `build_X9.py` → `jobs/jobs_X9.jsonl` (700 jobs, sample-major) and `jobs/manifest_X9.json` (700 expected keys, seeds per question, prompt sha256). Prompt lengths 23 / 30 / 32 / 19 / 26 tokens (Q1–Q5). Build assertions passed: one user block, no system block, ends with the empty think block, question text once, ids == tokenizer(render), lexicons equal to sw003 vstats / d_counts.
- `tests/decoded.txt` (Q1, Q3, Q5) read by hand: `<|im_start|>user\n<question><|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`, nothing else.
- `tests/test_X9.py` → `tests/test_X9.log`: 98 checks pass. Parser known answers include "Crows, definitely - though bees are cool too" → crow, "Neither" → neither, "Arr, pirate!" → pirate, echoed questions, "Neither bees nor crows" → neither, "Arr!" → pirate (style_implied), hedge flag. Analysis on synthetic data reproduces hand-computed rates and Δs, the brute-force paired-bootstrap CI, the exact-0.20 boundary, the shared-shift and ceiling flags, partial cuts (n 18 / 17), a whole missing cell (bc "not scorable", ps still scored), missing Q4/Q5 and no rows at all, without crashing. One test expectation of mine was wrong and was fixed (LEX_EXT counts "Thou art kind, methinks" as 2, since the lexicon's phrase is "art thou"); no code change.
- Client test against a CPU mock server (`tests/mock_server_x9.py`, port 18977, stopped by PID): smoke 7/7; past deadline → marker "partial 0/700"; full 700/700 with max 48 in flight and 7 transient 5xx retried; resume from 350 rows sends only the missing 350; marker "complete". Marker path in tests was `tests/mock_out/gpu_marker`, never the real one.
