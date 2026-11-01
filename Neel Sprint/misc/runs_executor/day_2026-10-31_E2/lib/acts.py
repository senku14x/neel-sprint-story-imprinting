"""Activation saving for the user's readers (Causal-Concordance: activation oracle, activation verbalizer, NLA AV/AR,
lenses). Overnight 30-31 Oct 2026 (executor-9), master brief section 7. API reference: lib/ACTS_README.md; convention
and its mapping onto Causal-Concordance: lib/ACTS_CONVENTION.md; GPU verification: lib/ACTS_VERIFY.json.

Convention (same as Causal-Concordance registry.json "block_indexing" and engine.Recorder):
  layer L = the output of model.model.layers[L] (0-based decoder block L, residual stream entering block L+1,
  PRE-final-norm; = HF hidden_states[L+1] for L < 63, but never read hidden_states: its last entry is post-norm).
  Captured with forward hooks on the decoder blocks, from a bf16 HF (+ PEFT) forward. Single-token states are the bf16
  block output upcast to fp32; span means are taken in fp32; both are stored as fp16 (exact for bf16 values with
  |x| < 65504; the writer asserts finiteness and range).

Three parts:
  (a) position helpers  : header_positions, chat_positions, story_positions, char_span_tokens, render_chat
  (b) capture           : Capture (context manager) / capture() (one teacher-forced forward). Read hooks must be the
                          LAST output-modifying hooks on each block, so saved states are post-intervention; a guard
                          raises if a non-read-only hook was registered after them.
  (c) writer            : ActWriter (fp16 safetensors shards + index.<part>.jsonl + index.jsonl + README.md),
                          estimate_bytes, load_index, load_rows.
Labels ending in "_mean" are reduced by an fp32 mean over their positions (one row); every other label is saved token by
token (one row per position, tok_i = 0..n-1).
"""
import glob
import json
import os
import socket
import time

import torch

ROOT = "/workspace/runs_executor/day_2026-10-31_E2"
ACTS_ROOT = f"{ROOT}/acts"
LAYERS = (16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63)
N_BLOCKS, D_MODEL = 64, 5120
FP16_MAX = 65504.0

# Qwen3.6-27B token ids (tokenizer of /dev/shm/qwen36_27b, revision 6a9e13bd; checked by tests on CPU)
IM_START, IM_END = 248045, 248046
TOK_USER, TOK_ASSISTANT, TOK_SYSTEM = 846, 74455, 8678
NL, NLNL, THINK, THINK_END = 198, 271, 248068, 248069
# The 7 reply-start header tokens, exactly as sw006 build_x.py HEADER / sw009 cap9_x.py HEADER:
# "<|im_start|>" "assistant" "\n" "<think>" "\n\n" "</think>" "\n\n" (generation prompt, enable_thinking=False)
HEADER = (248045, 74455, 198, 248068, 271, 248069, 271)
HEADER_NAMES = ("im_start", "assistant", "nl", "think", "nlnl", "think_end", "nlnl2")
N_GEN = 8


# ============================================================================================ (a) positions
def render_chat(tok, msgs, add_generation_prompt=True):
    """Chat render as sw008/sw009 (apply_chat_template, enable_thinking=False, no system prompt unless msgs has one).
    Returns (text, ids, offsets); asserts the text tokenization equals apply_chat_template(tokenize=True)."""
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=add_generation_prompt, enable_thinking=False)
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    ids, offs = list(enc["input_ids"]), [tuple(o) for o in enc["offset_mapping"]]
    ref = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=add_generation_prompt, enable_thinking=False)
    ref = list(ref["input_ids"] if hasattr(ref, "keys") else ref)
    assert ids == ref, "text tokenization differs from apply_chat_template(tokenize=True)"
    return text, ids, offs


def header_positions(ids, reply_start=None):
    """The 7 reply-start header positions. reply_start = index of the first reply token (= prompt length for a
    generation prompt); default: right after the LAST occurrence of HEADER in ids."""
    ids = list(ids)
    if reply_start is None:
        hits = [i for i in range(len(ids) - 6) if tuple(ids[i:i + 7]) == HEADER]
        assert hits, "no reply-start header (HEADER) in ids"
        reply_start = hits[-1] + 7
    assert tuple(ids[reply_start - 7:reply_start]) == HEADER, "ids[reply_start-7:reply_start] is not HEADER"
    return list(range(reply_start - 7, reply_start))


def asst_positions(ids, upto):
    """sw006 build_x.asst_positions, verbatim logic: content tokens of Assistant turns before index `upto`; the turn
    header ("<|im_start|>assistant" + following \\n / <think> / \\n\\n / </think> tokens) and <|im_end|> are excluded."""
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == IM_START and i + 1 < upto and ids[i + 1] == TOK_ASSISTANT:
            inside = True
            j = i + 2
            while j < upto and ids[j] in (NL, THINK, NLNL, THINK_END):
                j += 1
            i = j
            continue
        if ids[i] == IM_END:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def user_turn_spans(ids, upto):
    """[(start, end)] content spans of every user turn before `upto`: from <|im_start|> index + 3 (after "user", "\\n")
    to the turn's <|im_end|> (exclusive), as sw009 cap9_x.last_user_span."""
    out = []
    for i in range(upto - 2):
        if ids[i] == IM_START and ids[i + 1] == TOK_USER:
            assert ids[i + 2] == NL, f"user turn at {i} not followed by newline"
            e = ids.index(IM_END, i)
            assert e < upto, f"user turn at {i} not closed before {upto}"
            out.append((i + 3, e))
    return out


def char_span_tokens(offsets, a, b):
    """Token positions whose character span overlaps [a, b) (sw009 prohibition rule: start < b and end > a)."""
    return [k for k, (s, e) in enumerate(offsets) if s < b and e > a]


def token_at_char(offsets, c):
    """Index of the first token whose span ends after character c (the token containing c, or the next one)."""
    for k, (s, e) in enumerate(offsets):
        if e > c:
            return k
    raise ValueError(f"char {c} beyond the last token")


def chat_positions(ids, text=None, offsets=None, prohibition=None, reply_start=None, n_gen=N_GEN):
    """Position groups for one chat context (prompt, or prompt + generated tokens for a teacher-forced forward).
      hdr             the 7 reply-start header tokens (sw006/sw009 definition), token by token
      trig_last       last content token of the trigger turn (= the final user turn, the token before its <|im_end|>)
      trig_turn_mean  mean over the trigger turn's content tokens (= sw009 u3_mean)
      prohib_mean     mean over the tokens overlapping the prohibition text (last occurrence in `text`; needs text,
                      offsets and prohibition; = sw009 prohib_mean)
      asst_hist_mean  mean over the Assistant's earlier turns' content tokens (= sw009 asst_mean, sw006 hist)
      user_hist_mean  mean over the user's earlier turns' content tokens (user turns before the trigger turn)
      user_all_mean   mean over all user turns' content tokens (earlier turns + trigger turn)
      gen             the first n_gen reply tokens after the header (forced readouts: "By the way," and what follows);
                      only positions < len(ids)
    Empty groups are returned empty (skipped by Capture)."""
    ids = list(ids)
    hdr = header_positions(ids, reply_start)
    hs, rs = hdr[0], hdr[-1] + 1
    spans = user_turn_spans(ids, hs)
    assert spans, "no user turn before the header"
    t0, t1 = spans[-1]
    upto = t0 - 3  # the trigger turn's <|im_start|>
    P = {"hdr": hdr, "trig_last": [t1 - 1], "trig_turn_mean": list(range(t0, t1)),
         "asst_hist_mean": asst_positions(ids, upto),
         "user_hist_mean": [k for a, b in spans[:-1] for k in range(a, b)],
         "user_all_mean": [k for a, b in spans for k in range(a, b)],
         "gen": list(range(rs, min(rs + n_gen, len(ids))))}
    if prohibition is not None:
        assert text is not None and offsets is not None, "prohibition needs text and offsets"
        ci = text.rfind(prohibition)
        assert ci >= 0, "prohibition text not found"
        P["prohib_mean"] = char_span_tokens(offsets[:len(ids)], ci, ci + len(prohibition))
        assert P["prohib_mean"] and all(t0 <= k < t1 for k in P["prohib_mean"]), "prohibition not inside the trigger turn"
    return P


def story_positions(offsets, turn_spans, habit_char, n_before=4):
    """Story contexts (sw016). turn_spans: [(a, b)] character spans of the speaker's turn-start markers (e.g. the
    speaker name and colon) in the text that was tokenized; habit_char: character index where the habit line starts.
      story_turn_start  every token overlapping each turn-start span, token by token (in span order)
      story_pre_habit   the n_before tokens immediately before the token containing habit_char"""
    ts = []
    for a, b in turn_spans:
        ts += char_span_tokens(offsets, a, b)
    k = token_at_char(offsets, habit_char)
    assert k >= n_before, "not enough tokens before the habit line"
    return {"story_turn_start": ts, "story_pre_habit": list(range(k - n_before, k))}


def is_mean(label):
    return label.endswith("_mean")


# ============================================================================================== (b) capture
def text_model(model):
    """The decoder stack (.layers, .norm, .embed_tokens) through PEFT wrappers (sw018 hooks018.text_model logic)."""
    m = model
    for attr in ("base_model", "model", "language_model"):
        while hasattr(m, attr) and not hasattr(m, "layers"):
            m = getattr(m, attr)
    assert hasattr(m, "layers") and len(m.layers) == N_BLOCKS, type(m)
    return m


def blocks(model):
    """model.model.layers through PEFT wrappers."""
    return text_model(model).layers


def _readonly(fn):
    # hooks that never change a block's output: other acts captures, transformers' output_hidden_states recorder
    return getattr(fn, "_acts_readonly", False) or getattr(fn, "__name__", "") == "output_capturing_hook"


class Capture:
    """Forward hooks on blocks(model)[L] for L in `layers` that keep, per batch row, the requested positions.
    specs: one dict {label: [positions]} per batch row (a single dict is broadcast to every row). Labels ending in
    "_mean" are reduced by an fp32 mean over their positions. Enter it INSIDE any intervention context (after the
    intervention hooks are registered) so the saved states are post-intervention; the hook raises if any
    non-read-only forward hook sits after it on the same block. Fires on the first forward whose sequence covers
    every requested position (a teacher-forced forward, or generate()'s prefill); later 1-token decode steps are
    ignored; a second full forward raises. result() -> one dict per row {label: fp32 cpu tensor [n, len(layers), H]}
    (n = 1 for means)."""

    def __init__(self, model, specs, layers=LAYERS):
        self.blocks = blocks(model)
        self.layers = [int(l) for l in layers]
        assert len(set(self.layers)) == len(self.layers) and all(0 <= l < N_BLOCKS for l in self.layers)
        self.specs = specs
        self._h, self._acts, self.calls = {}, {}, 0

    def _rows(self, B):
        sp = [self.specs] * B if isinstance(self.specs, dict) else list(self.specs)
        assert len(sp) == B, f"{len(sp)} specs for batch {B}"
        return [{k: list(v) for k, v in s.items() if len(v)} for s in sp]

    def _mk(self, L):
        def hook(mod, inp, out):
            hid = self._h[L].id
            keys = list(mod._forward_hooks.keys())
            after = keys[keys.index(hid) + 1:]
            bad = [k for k in after if not _readonly(mod._forward_hooks[k])]
            if bad:
                raise RuntimeError(f"acts.Capture: {len(bad)} output-modifying hook(s) registered after the capture on "
                                   f"layer {L}; saved states would be pre-intervention. Enter Capture last.")
            t = out[0] if isinstance(out, tuple) else out
            B, T = t.shape[0], t.shape[1]
            rows = self._rows(B)
            need = max((max(v) for s in rows for v in s.values()), default=-1)
            if T <= need:
                if T == 1:
                    return None  # incremental decode step
                raise RuntimeError(f"acts.Capture: forward of length {T} does not cover position {need}")
            if L in self._acts:
                raise RuntimeError("acts.Capture: second full forward inside one Capture")
            res = []
            for r, s in enumerate(rows):
                d = {}
                for lab, pos in s.items():
                    x = t[r, torch.as_tensor(pos, device=t.device)].float()
                    d[lab] = x.mean(0, keepdim=True) if is_mean(lab) else x
                res.append(d)
            self._acts[L] = res
            self.calls += 1
            return None
        hook._acts_readonly = True
        return hook

    def __enter__(self):
        for L in self.layers:
            self._h[L] = self.blocks[L].register_forward_hook(self._mk(L))
        return self

    def __exit__(self, *exc):
        for h in self._h.values():
            h.remove()
        self._h = {}

    def result(self):
        missing = [L for L in self.layers if L not in self._acts]
        assert not missing, f"no capture at layers {missing} (no full forward ran inside the Capture?)"
        B = len(self._acts[self.layers[0]])
        return [{lab: torch.stack([self._acts[L][r][lab] for L in self.layers], 1).cpu()
                 for lab in self._acts[self.layers[0]][r]} for r in range(B)]


@torch.no_grad()
def capture(model, input_ids, specs, layers=LAYERS, attention_mask=None, **fwd_kw):
    """One teacher-forced forward over input_ids ([T] list or [B, T] tensor: prompt + generated ids, exactly the
    token ids generation produced) with read hooks entered now, i.e. after any intervention hooks already registered.
    Returns Capture.result()."""
    x = torch.as_tensor(input_ids)
    x = x[None] if x.dim() == 1 else x
    dev = next(model.parameters()).device
    kw = dict(use_cache=False, logits_to_keep=1, **fwd_kw)
    if attention_mask is not None:
        kw["attention_mask"] = torch.as_tensor(attention_mask, device=dev)
    with Capture(model, specs, layers) as cap:
        model(input_ids=x.to(dev), **kw)
    return cap.result()


# =============================================================================================== (c) writer
def estimate_bytes(n_contexts, rows_per_context, n_layers=len(LAYERS), d=D_MODEL):
    return int(n_contexts) * int(rows_per_context) * int(n_layers) * int(d) * 2


def default_rows_per_context(n_gen=N_GEN, prohib=True):
    """hdr 7 + trig_last 1 + trig_turn_mean + prohib_mean + asst_hist_mean + user_hist_mean + user_all_mean + gen."""
    return 7 + 1 + 1 + int(prohib) + 3 + n_gen


def _load_part_indices(d):
    rows = []
    for f in sorted(glob.glob(f"{d}/index.*.jsonl")):
        with open(f) as fh:
            rows += [json.loads(l) for l in fh if l.strip()]
    return rows


class ActWriter:
    """fp16 rows [len(layers), H] into acts/<exp>/shards/<part>_<NNNNN>.safetensors (tensor "acts" [N, n_layers, H]),
    indexed in acts/<exp>/index.<part>.jsonl (one json row per saved state). One writer per (exp, part); parts written
    from different boxes never share files. A context's rows are always flushed together (never split across a crash).
    Resumable: has_context(ctx) is True for contexts already indexed. finalize() rebuilds acts/<exp>/index.jsonl from
    every part and writes README.md.
      expected_contexts / rows_per_context: byte estimate before writing, stored in estimate.<part>.json; raises if the
      estimate for this part exceeds max_gb (default 12) unless allow_over."""

    def __init__(self, exp, part="main", layers=LAYERS, tok=None, code=None, model_desc=None, root=ACTS_ROOT,
                 rows_per_shard=2048, expected_contexts=None, rows_per_context=None, max_gb=12.0, allow_over=False):
        assert "/" not in part and "." not in part and part, part
        self.exp, self.part, self.layers, self.tok, self.code = exp, part, [int(l) for l in layers], tok, code
        self.model_desc = model_desc
        self.dir = f"{root}/{exp}"
        os.makedirs(f"{self.dir}/shards", exist_ok=True)
        self.index_path = f"{self.dir}/index.{part}.jsonl"
        self.rows_per_shard = rows_per_shard
        prev = _load_part_indices(self.dir)
        self.row_keys = {r["key"] for r in prev}
        self.ctx_done = {r["ctx"] for r in prev}
        ex = sorted(glob.glob(f"{self.dir}/shards/{part}_*.safetensors"))
        self.next_shard = (max(int(os.path.basename(f).split("_")[-1].split(".")[0]) for f in ex) + 1) if ex else 0
        self.buf, self.meta, self._ctx_buf = [], [], set()
        self.n_written = 0
        if expected_contexts is not None:
            rpc = rows_per_context or default_rows_per_context()
            est = estimate_bytes(expected_contexts, rpc, len(self.layers))
            info = dict(exp=exp, part=part, expected_contexts=expected_contexts, rows_per_context=rpc,
                        n_layers=len(self.layers), bytes=est, gb=round(est / 1e9, 3), t=time.strftime("%FT%T"))
            with open(f"{self.dir}/estimate.{part}.json", "w") as f:
                json.dump(info, f, indent=1)
            print(f"[acts] {exp}/{part}: estimate {info['gb']} GB ({expected_contexts} contexts x {rpc} rows x "
                  f"{len(self.layers)} layers x {D_MODEL} x fp16)", flush=True)
            if est / 1e9 > max_gb and not allow_over:
                raise RuntimeError(f"acts estimate {est / 1e9:.1f} GB > max_gb {max_gb}; cut contexts/positions or pass "
                                   f"allow_over=True")

    @staticmethod
    def ctx_key(exp, model, condition, arm, script, sample=0):
        return f"{exp}|{model}|{condition}|{arm}|{script}|{sample}"

    def has_context(self, model, condition, arm, script, sample=0):
        return self.ctx_key(self.exp, model, condition, arm, script, sample) in self.ctx_done

    def _text(self, ids):
        if self.tok is None:
            return None
        return self.tok.decode(ids)

    def add_context(self, cap_row, ids, *, model, condition, arm, script, sample=0, positions=None, extra=None):
        """cap_row: one Capture.result() row {label: [n, len(layers), H]}; ids: the token ids of that forward;
        positions: the {label: [positions]} spec used for that row (needed for token ids/text). Returns the number of
        rows queued (0 if the context is already indexed)."""
        ctx = self.ctx_key(self.exp, model, condition, arm, script, sample)
        assert positions is not None, "positions (the spec used for this row) is required"
        if ctx in self.ctx_done:
            return 0
        assert ctx not in self._ctx_buf, f"duplicate context in this run: {ctx}"
        ids = list(ids)
        n = 0
        for lab, x in cap_row.items():
            pos = list(positions[lab])
            assert x.dim() == 3 and x.shape[1] == len(self.layers) and x.shape[2] == D_MODEL, (lab, tuple(x.shape))
            xf = x.float()
            assert torch.isfinite(xf).all(), f"non-finite state in {ctx} {lab}"
            mx = float(xf.abs().max())
            assert mx < FP16_MAX, f"|x| = {mx} overflows fp16 in {ctx} {lab}"
            groups = [(-1, pos)] if is_mean(lab) else [(i, [p]) for i, p in enumerate(pos)]
            assert len(groups) == x.shape[0], (lab, len(groups), x.shape[0])
            for (ti, pp), row in zip(groups, x):
                key = f"{ctx}|{lab}|{ti}"
                assert key not in self.row_keys, f"duplicate row key {key}"
                self.row_keys.add(key)
                tid = [ids[p] for p in pp]
                self.buf.append(row.to(torch.float16).contiguous())
                self.meta.append(dict(key=key, ctx=ctx, experiment=self.exp, model=model, condition=condition, arm=arm,
                                      script=script, sample=sample, label=lab, tok_i=ti,
                                      reduce="mean" if is_mean(lab) else "token", positions=pp, n_ctx_tokens=len(ids),
                                      token_ids=tid, token_text=self._text(tid), layers=self.layers,
                                      extra=extra or {}))
                n += 1
        self._ctx_buf.add(ctx)
        if len(self.buf) >= self.rows_per_shard:
            self.flush()
        return n

    def flush(self):
        if not self.buf:
            return
        from safetensors.torch import save_file
        name = f"{self.part}_{self.next_shard:05d}.safetensors"
        path = f"{self.dir}/shards/{name}"
        X = torch.stack(self.buf)
        tmp = f"{path}.tmp.{socket.gethostname()}.{os.getpid()}"
        save_file({"acts": X, "layers": torch.tensor(self.layers, dtype=torch.int32)}, tmp,
                  metadata={"exp": self.exp, "part": self.part, "dtype": "float16", "convention": "acts.py v1"})
        os.replace(tmp, path)
        lines = []
        for r, m in enumerate(self.meta):
            m.update(shard=f"shards/{name}", row=r, code=self.code, model_desc=self.model_desc)
            lines.append(json.dumps(m) + "\n")
        with open(self.index_path, "a") as f:
            f.write("".join(lines))
            f.flush()
            os.fsync(f.fileno())
        self.ctx_done |= self._ctx_buf
        self.n_written += len(self.buf)
        self.next_shard += 1
        self.buf, self.meta, self._ctx_buf = [], [], set()

    def close(self):
        self.flush()

    def finalize(self, notes="", conditions_doc=None):
        """Flush, rebuild index.jsonl from every part, write README.md (call once at the end of the experiment's last
        part; safe to call again)."""
        self.flush()
        write_readme(self.dir, self.exp, notes=notes, conditions_doc=conditions_doc)


def write_readme(d, exp, notes="", conditions_doc=None):
    rows = _load_part_indices(d)
    tmp = f"{d}/index.jsonl.tmp.{socket.gethostname()}.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))
    os.replace(tmp, f"{d}/index.jsonl")
    shards = sorted({r["shard"] for r in rows})
    nbytes = sum(os.path.getsize(f"{d}/{s}") for s in shards if os.path.exists(f"{d}/{s}"))
    cnt = lambda k: sorted({str(r[k]) for r in rows})
    labs = {}
    for r in rows:
        labs[r["label"]] = labs.get(r["label"], 0) + 1
    ctxs = {r["ctx"] for r in rows}
    tpl = open(f"{os.path.dirname(os.path.abspath(__file__))}/ACTS_EXP_README_TEMPLATE.md").read()
    txt = tpl.format(
        exp=exp, n_rows=len(rows), n_ctx=len(ctxs), n_shards=len(shards), gb=round(nbytes / 1e9, 3),
        models=", ".join(cnt("model")), conditions=", ".join(cnt("condition")), arms=", ".join(cnt("arm")),
        n_scripts=len(cnt("script")), layers=", ".join(map(str, rows[0]["layers"])) if rows else "",
        labels="\n".join(f"| `{k}` | {v} |" for k, v in sorted(labs.items())),
        codes=", ".join(f"`{c}`" for c in cnt("code")), conditions_doc=conditions_doc or "(not given)",
        notes=notes or "(none)", t=time.strftime("%F %T"))
    with open(f"{d}/README.md", "w") as f:
        f.write(txt)
    return len(rows)


# ================================================================================================= loading
def load_index(exp, root=ACTS_ROOT):
    """All index rows of an experiment (every part; index.jsonl is a rebuilt copy of the same rows)."""
    return _load_part_indices(f"{root}/{exp}")


def load_rows(exp, rows, root=ACTS_ROOT, layers=None):
    """Stack the fp16 states of the given index rows -> [len(rows), n_layers, H] fp16 (optionally only `layers`)."""
    from safetensors import safe_open
    out = [None] * len(rows)
    by = {}
    for i, r in enumerate(rows):
        by.setdefault(r["shard"], []).append((i, r["row"]))
    for s, lst in by.items():
        with safe_open(f"{root}/{exp}/{s}", framework="pt") as f:
            sl = f.get_slice("acts")
            Ls = f.get_tensor("layers").tolist()
            sel = None if layers is None else [Ls.index(l) for l in layers]
            for i, rr in lst:
                x = sl[rr:rr + 1][0]
                out[i] = x if sel is None else x[sel]
    return torch.stack(out)
