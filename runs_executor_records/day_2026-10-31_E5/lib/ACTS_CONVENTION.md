# Activation-capture convention: Causal-Concordance readers vs our saves

Source read: `/workspace/Causal-Concordance`, branch `origin/012-reader-concordance` (commit `1aa47a3`, 7 Oct 2026), via `git show`. Main's checkout was not touched. The readers were not run. Our code is `lib/acts.py`; its GPU check is `lib/ACTS_VERIFY.json`.

## 1. What the readers expect (quotes, file:line)

**Hook point and layer indexing: block output, 0-based.**
- `scripts/common/registry.json:21`: `"block_indexing": "zero-based block-output indexing: layer L = output of model.model.layers[L] (= HF hidden_states[L+1]); hooks write block outputs"`
- `scripts/common/engine.py:4`: `Layer l = the output of decoder block l (0..63), i.e. the residual stream entering block l+1. Batch size 1.`
- `scripts/common/registry.py:85-88`: `def blocks(model): """The decoder block list, also through a PEFT wrapper.""" ... return m.model.layers`
- `scripts/common/engine.py:85-93` (`Recorder`): `"""Record block outputs at layers (row 0, all positions) as detached float32 copies on the device."""` with `self.acts[l] = _out(o)[0].detach().float().clone()`

**Pre or post final norm: pre-norm (raw block output).** Readers that need the norm apply it themselves.
- `scripts/common/readers.py:3-4`: `Every reader maps h, the float32 output of block layer at one position (stock bf16 forward with any adapter disabled, WSB's Backend.capture convention)`
- `readers.py:6`: `logit_lens     top-k of W_U . final_norm(h)`
- `registry.json:115` (NLA): `"trained_on": "Qwen3.6-27B layer 42 residuals, norm none (nla_meta extraction)"`
- `readers.py:9-10` (oracle): `marker embedding row <- alpha . unit(h), layer named in the prompt, adapter disabled while capturing`. Only the direction of h matters to the oracle.
- `readers.py:11-12` (NLA AV): `Karvonen add h' = h + ||h|| v/||v|| at the output of block 1 at the marker`. Also scale-invariant in the injected v.
- `readers.py:13` (NLA AR): `float32 value head on normalize(h_last, sqrt(d))`

**dtype: bf16 model and forward; captures stored as float32.**
- `registry.json:14-16`: `"dtype": "bfloat16", "attn_implementation": "eager", "enable_thinking": false`
- `registry.py:72-80`: `"""bf16 model, eager attention (the RHUT-validated regime), eval mode."""` … `from_pretrained(MODEL, revision=REV, dtype=torch.bfloat16, ..., attn_implementation=attn_impl)`
- `readers.py:78-90` (`capture_stock`): `"""{layer: [P, d] float32 cpu}: one stock bf16 forward (adapter disabled if one is mounted)..."""` … `with off, rec: model(torch.tensor([list(ids)], device=model.device), logits_to_keep=1)` … `return {l: rec.acts[l][list(positions)].cpu() for l in layers}`
- `scripts/012_reader_concordance/stageB_capture.py:243-244`: `torch.save({"items": ..., "layers": CAP_LAYERS, "X": torch.stack(caps), "note": "block outputs (float32) at the read position, captured in each arm's greedy prefill"}, out / "captures.pt")`

**Token alignment: an index into the exact ids fed to the forward, one token per state.**
- `scripts/000_setup/reader_smoke.py:26`: `ITEM, POS, OTHER = "brew-s2-r10d2-0000", 164, 131`. The docstring at :4 says `emit_colon (position 164, the last prompt token)`.
- `reader_smoke.py:65`: `acts = RD.capture_stock(model, r.ids, layers, [POS, OTHER])`
- `reader_smoke.py:76-77` (NLA reference re-extraction): `ids = tok(df.detokenized_text_truncated[i], add_special_tokens=False)["input_ids"]` then `RD.capture_stock(model, ids, [NLA_LAYER], [len(ids) - 1])`. The state at the last token.
- `stageB_capture.py:134-136`: `prompt = it["prompt"].rstrip(); ids = runner.encode(prompt); pos = len(ids) - 1`
- Chat rendering for reader prompts: `reader_smoke.py:128-129`: `tok.apply_chat_template([...], tokenize=True, add_generation_prompt=True, enable_thinking=False)`

**Interventions: captures are taken after the edit (post-intervention).**
- `engine.py:12`: `Hook order on a block: the regime upcast, then writes, then the recorder (which therefore sees post-write values).`
- `stageB_capture.py:69-71` (`PrefillCapture`): `"""Block outputs at one position in the prefill (first forward with n tokens); registered after any BandEditor, so band layers are captured post-edit."""`. Its hook (:85-88) keeps `x[0, self.pos].detach().float().cpu()` only when `x.shape[1] == self.n`.

**Reader layers.**
- `registry.json:64`: oracle `"layers_on_contract": [20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60]`; `:65` `"capture_with_adapter_disabled": true`
- `registry.json:72, 90`: NLA `"layer": 42`
- `reader_smoke.py:27`: `LENS_LAYERS, ORACLE_LAYER, NLA_LAYER = [40, 42, 44], 40, 42`; `stageB_capture.py:43`: `CAP_LAYERS = [40, 42, 44, 52, 56]`

**`scripts/012_reader_concordance/c012.py`** contains no capture code. It holds Stage C helpers only: paths (`:18` `"captures": b / "captures.pt"`), LSE per concept, `d_r`, concept naming. The 012 capture convention is in `stageB_capture.py` (and in the F/G/I/J/R `*_capture.py` scripts, which use the same `PrefillCapture` pattern), quoted above.

## 2. How our saves map onto it

| Aspect | Causal-Concordance | Ours (`lib/acts.py`) | Same? |
|---|---|---|---|
| Hook point | forward hook on `model.model.layers[L]` (through PEFT) | forward hook on `model.model.layers[L]` (through PEFT; `acts.blocks`) | **same** |
| Layer index | L = block-L output = `hidden_states[L+1]` | same; checked on GPU: `layers[L]` == `hidden_states[L+1]` exactly for L 0–62 (G1b) | **same** |
| Norm | pre-final-norm; readers apply `final_norm` themselves | pre-final-norm; `hidden_states[64]` == `final_norm(layers[63])` exactly, and differs from the raw L63 by 65 %, so it is never used (G1b) | **same** |
| Model / weights | Qwen/Qwen3.6-27B @ `6a9e13bd`, bf16 | `/dev/shm/qwen36_27b` (same revision, sha256-identical per CONVENTIONS), bf16 | **same** |
| Forward precision | stock bf16 forward (`capture_stock`; the fp32-residual regime is used only for 012's write experiments) | stock bf16 forward | **same** |
| Attention impl | `eager` | HF default (recorded in `ACTS_VERIFY.json → attn_implementation`) | **differs**. Numerical only: measured sdpa vs eager on the same ids, up to 3.8 % relative per vector at header tokens, 0.3–0.5 % for span means (`ACTS_VERIFY.json → eager_vs_default_attention_prompt_only`) |
| Storage dtype | float32 | **fp16**. Token rows are bf16 values, which fp16 holds exactly below 65504 (G5 checks). `_mean` rows are fp32 means rounded to fp16 (relative error ≤ 2⁻¹¹). | **differs**. Lossless for token rows; call `.float()` before reading |
| Adapter | subject captured with any adapter **disabled** (`capture_stock`; the mounted adapter is the reader's own, e.g. the oracle LoRA) | parent rows: adapter disabled (= their subject model). **Organism rows (hdA0, hdB0, Tony's): organism adapter active** | **intended difference**. Organism rows are the organism's states. If a reader adapter is ever mounted on an organism model, read from our saved rows, never recapture through `capture_stock` |
| Token alignment | index into the forward's ids; state at token p | index into the forward's ids (`positions` in each index row, with `token_ids` and `token_text`); state at token p | **same** |
| Prompt render | `apply_chat_template(..., enable_thinking=False)` | the same, with the generation prompt, so the reply-start header is `<\|im_start\|>assistant\n<think>\n\n</think>\n\n` | **same** template |
| Which forward | the greedy run's prefill (the exact labelled forward), batch 1 | one teacher-forced forward over prompt + generated ids (`use_cache=False`); batch ≥ 1 allowed (no padding) | **differs slightly**. Measured: at prompt positions, a longer teacher-forced sequence differs from the prompt-only forward by up to 3.6 % relative (header tokens; length-dependent kernels), so arms are teacher-forced over equal lengths (prompt + first 8 reply tokens). At generated positions, teacher-forced vs incremental decode: median 0.77 %, max 1.4 % |
| Interventions | writes first, recorder last → post-edit | intervention hooks first, read hooks last → post-intervention; a guard raises if an output-modifying hook sits after the read hook (G2) | **same**, and enforced |
| Positions | single positions | single tokens (`hdr`, `trig_last`, `gen`, `story_*`) **plus span means** (`*_mean`) | **addition**. The readers were trained and validated on single-token states. A span mean is off their training distribution (its direction is an average and its norm smaller); the oracle's `unit(h)` and NLA's norm-matched add remove the norm, not the direction. Read means as exploratory |
| Layers | oracle 20–60 step 4; NLA 42; lenses 40/42/44; 012 captures 40/42/44/52/56 | 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63 (a superset of all of these) | **covers** |

**Using a saved row with a reader:** `h = acts.load_rows(exp, [row], layers=[L])[0, 0].float().cuda()` is the reader's `h` (float32, block-L output at one position). For example, `OracleLens.read(h, L)` for L in its contract layers, or `NLAVerbalizer.read(h)` for L = 42.

**Parity with our own earlier captures:** prompt-only states from `acts.capture` are bit-identical to sw009's `cap9_x.py` saves for the same context (G3). Position definitions match sw006 `build_x.py` / sw009 `cap9_x.py` on all 256 sw008 contexts (CPU test).
