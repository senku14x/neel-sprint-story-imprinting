"""sw033 (S5) shared definitions: CPU-importable (tokenizer only, no torch / vLLM). Prep agent for executor-11 (E2), 31 Oct 2026.
Design: ../design_spec.md (frozen); implementation choices: ../DECISIONS.md.

Arms at the turn-3 reply (contexts default / dismissive / own; models hdA0, hdB0; parent reference on T0 / T1):
  T0   thinking off, standard template                      ids = render_off(msgs)                       (ends HEADER_OFF)
  T1   thinking on, own reasoning (sample k), then the reply ids = render_on(msgs) + body_k + OPEN          (body_k: vLLM stage)
  T2a  thinking on, ANOTHER script's sample-0 body           ids = render_on(msgs) + body0[donor] + OPEN   (donor: pair_t2a)
  T2b  thinking on, lorem-ipsum filler, |body0| tokens       ids = render_on(msgs) + filler(|body0|) + OPEN
  T3   thinking off, this script's sample-0 reasoning prefilled at the reply start, then "\\n\\n"
                                                             ids = render_off(msgs) + tok(strip(decode(body0)) + "\\n\\n")
  T5   (HF) T1's context with sample-0 body; the residual state of the 2 reply-opening positions (OPEN = </think>, \\n\\n) replaced
       at the output of every block L0-63 by T0's states at T0's last 2 positions (the same 2 token ids), prefill only.
  T1hf (HF) T1's context with sample-0 body, no patch: same-path reference for T5 (added control, DECISIONS).
Readouts: free (<= 2,048 tokens after all prefilled material; primary) for every arm; forced "By the way," + 48 for T0 / T1 / T5.
Labels are computed on the reply only: the generated continuation (after the last self-emitted </think>, if any)."""
import hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/dev/shm/qwen36_27b"                       # Qwen/Qwen3.6-27B @ 6a9e13bd
NS = "/workspace/Neel Sprint"
LORA_VLLM = {"hdA0": "/workspace/_box_transfer/lora_vllm_expl1028/hdA0", "hdB0": "/workspace/_box_transfer/lora_vllm_expl1028/hdB0"}
LORA_SHA = {"hdA0": "8244aa78fe2d6b973fff5c929784f8c5e52f2b4cfd7c706e40a2180b6577a297",
            "hdB0": "1743403a515e880d985ae251982d7e0e08a857b4026226f12a9ac8ae39b57c28"}   # = sw024's vLLM copies (SHA256SUMS)
LORA_HF = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"     # labels.py (identical to the E2 lib copy)
INPUTS = f"{HERE}/data/inputs33.json"

IM_START, IM_END, EOT, THINK_O, THINK_C, NL, NL2, ASSISTANT = 248045, 248046, 248044, 248068, 248069, 198, 271, 74455
HEADER_OFF = [IM_START, ASSISTANT, NL, THINK_O, NL2, THINK_C, NL2]     # <|im_start|>assistant\n<think>\n\n</think>\n\n
HEADER_ON = [IM_START, ASSISTANT, NL, THINK_O, NL]                     # <|im_start|>assistant\n<think>\n
OPEN = [THINK_C, NL2]                                                  # the reply-opening tokens after any reasoning
BTW_IDS = [1311, 279, 1560, 11]                                        # "By the way,"
BTW = "By the way,"
N_LAYERS, D_MODEL = 64, 5120

ORGS = ["hdA0", "hdB0"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
CONTEXTS = ["default", "dismissive", "own"]
SW5_VERSION = {"default": "helpful", "dismissive": "dismissive"}
ARMS_VLLM = ["T0", "T1", "T2a", "T2b", "T3"]
ARMS_HF = ["T5", "T1hf"]
ARMS_OPTIONAL = ["T3x"]              # NOT in the spec: T3 with </think> and <think> banned in the continuation (logit bias -100); off by default
BAN_THINK = {THINK_C: -100.0, THINK_O: -100.0}
FORCED_ARMS = {"T0", "T1", "T5"}
PARENT_ARMS = ["T0", "T1"]
SAMPLES = 3
MAXTOK = {"free": 2048, "forced": 48}
THINK_CAP = 4096
TEMP = 0.7
T1HF_CONTEXTS = ["default"]          # the same-path HF reference runs where the rule decides (DECISIONS)

LOREM = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
         "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
         "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non "
         "proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")


# ---------------------------------------------------------------------------------------------------------- basics
def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def rkey(readout, arm, ctx, model, sid, k):
    return f"sw033|{readout}|{arm}|{ctx}|{model}|{sid}|s{k}"


def reason_key(ctx, model, sid, k):
    return f"sw033|reason|T1|{ctx}|{model}|{sid}|s{k}"


def hist_key(model, sid):
    return f"sw033|hist|own|{model}|{sid}"


def n_samples(model):
    return 1 if model == "parent" else SAMPLES


def free_seed(sid, k):
    return seed_of("sw005e", sid, k)       # sw005 / sw024's free-reply seed, shared by every arm (paired across arms)


def forced_seed(sid, k):
    return seed_of("sw024f", sid, k)


def think_seed(sid, k):
    return seed_of("sw024t", sid, k)       # sw024's thinking seed


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001 (torn last line)
                pass
    return out


def jl_keys(p):
    return {r["key"]: r for r in jl(p)}


def heal_tail(p):
    """drop a torn last line (killed mid-write) so appends stay valid JSONL."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return
    data = open(p, "rb").read()
    if data.endswith(b"\n"):
        return
    cut = data.rfind(b"\n") + 1
    open(p, "wb").write(data[:cut])


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_inputs():
    D = json.load(open(INPUTS))
    assert len(D["sids"]) == 64 and D["sids"] == sorted(D["sids"])
    return D


def smoke_sids(sids, n):
    """n scripts spread over the 5 scenarios (sw024's rule)."""
    by = {}
    for sid in sids:
        by.setdefault(scenario_of(sid), []).append(sid)
    out, i = [], 0
    while len(out) < n:
        for sc in sorted(by):
            if i < len(by[sc]) and len(out) < n:
                out.append(by[sc][i])
        i += 1
    return sorted(out)


# ---------------------------------------------------------------------------------------------------------- contexts
def messages(D, ctx, sid, own_hist=None):
    """turns 1-2 (sw005 helpful / dismissive, or the reading model's own) + turn 3 = sw005 / 001's prohibition + question."""
    if ctx == "own":
        assert own_hist is not None, "own context needs the model's own history"
        m = [dict(x) for x in own_hist]
    else:
        m = [dict(x) for x in D["histories"][sid][SW5_VERSION[ctx]]]
    assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
    assert m[0]["content"] == D["scripts"][sid]["u1"] and m[2]["content"] == D["scripts"][sid]["u2"]
    return m + [{"role": "user", "content": D["scripts"][sid]["u3"]}]


def render(tok, msgs, thinking):
    txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
    ids = tok(txt, add_special_tokens=False)["input_ids"]
    want = HEADER_ON if thinking else HEADER_OFF
    assert ids[-len(want):] == want, f"reply-start header mismatch (thinking={thinking}): {ids[-8:]}"
    assert "<|im_start|>system" not in txt, "unexpected system turn"
    assert txt.count("<think>") == 1, "history must carry no think block"
    return ids, txt


def render_pair(tok, msgs):
    """-> (T0 ids, thinking-on prompt ids); asserts they share everything before the header's <think>."""
    off, _ = render(tok, msgs, False)
    on, _ = render(tok, msgs, True)
    assert off[:-3] == on[:-1] and off[-3:] == [NL2, THINK_C, NL2] and on[-1] == NL, "T0 / T1 prompts differ before the header"
    return off, on


def close_thinking(gen_ids, finish, stop_reason):
    """sw024's rule. Thinking tokens -> (body ids, closed_naturally). Drops a trailing stop id; a thinking that hit the cap or ended at
    <|im_end|> without </think> is force-closed by appending \\n to the body (then OPEN follows)."""
    ids = list(gen_ids)
    closed = finish == "stop" and (stop_reason == THINK_C or (ids and ids[-1] == THINK_C))
    while ids and ids[-1] in (THINK_C, IM_END, EOT):
        ids.pop()
    assert THINK_C not in ids and THINK_O not in ids, "think tag inside the thinking body"
    return ids + ([] if closed else [NL]), closed


def filler_ids(tok, n):
    """T2b body: exactly n tokens of repeated lorem ipsum (paragraphs joined by \\n\\n), the last token replaced by \\n (198) so the block
    ends like a thinking body before </think>."""
    assert n >= 2
    unit = tok(LOREM + "\n\n", add_special_tokens=False)["input_ids"]
    ids = (unit * (n // len(unit) + 2))[: n - 1] + [NL]
    assert len(ids) == n
    return ids


def t3_prefill_ids(tok, body):
    """T3: the sample-0 reasoning text (whitespace-stripped) + "\\n\\n", tokenised as reply text after the T0 header."""
    txt = tok.decode(body, skip_special_tokens=False).strip() + "\n\n"
    assert "<think>" not in txt and "</think>" not in txt
    return tok(txt, add_special_tokens=False)["input_ids"], txt


def arm_ids(tok, arm, off, on, body_self, body_donor=None, filler=None):
    """ids of an arm's prefix (free readout). body_self = this (script, model, ctx)'s reasoning body for this arm (sample k for T1,
    sample 0 for every other arm)."""
    if arm == "T0":
        return list(off)
    if arm in ("T1", "T5", "T1hf"):
        return list(on) + list(body_self) + OPEN
    if arm == "T2a":
        return list(on) + list(body_donor) + OPEN
    if arm == "T2b":
        assert len(filler) == len(body_self)
        return list(on) + list(filler) + OPEN
    if arm in ("T3", "T3x"):
        return list(off) + t3_prefill_ids(tok, body_self)[0]
    raise ValueError(arm)


def pair_t2a(sids, lens):
    """T2a donor rule (DECISIONS): within one (model, context), scripts in order of (sample-0 body length, sid); each takes the unused
    script of a DIFFERENT scenario with the nearest body length (ties: smaller sid). If every other-scenario script is used, the nearest
    other-scenario script is reused and the pair is flagged. -> {sid: (donor, reused)}."""
    order = sorted(sids, key=lambda s: (lens[s], s))
    used, out = set(), {}
    for s in order:
        cand = [d for d in sids if scenario_of(d) != scenario_of(s)]
        assert cand, f"no other-scenario donor for {s}"
        free = [d for d in cand if d not in used]
        pool, reused = (free, False) if free else (cand, True)
        d = min(pool, key=lambda d: (abs(lens[d] - lens[s]), d))
        used.add(d); out[s] = (d, reused)
    return out


def split_reply(gen_text):
    """free reply = the text after the last self-emitted </think> ('' if a <think> never closes); -> (reply, self_think, unclosed)."""
    self_think = "<think>" in gen_text or "</think>" in gen_text
    if "</think>" in gen_text:
        return gen_text.rsplit("</think>", 1)[1].strip(), True, False
    if "<think>" in gen_text:
        return "", True, True
    return gen_text.strip(), False, False


# ---------------------------------------------------------------------------------------------------------- own-history writer
# sw015's writer protocol (o1_gen.py: trim_own, screen, n = 4 candidates, max 300 tokens, stop "\n\n", 3 rounds), WITHOUT a system
# (writer) prompt: the model writes its own default turns 1-2 (design_spec "own-history default").
LABEL = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST_ACT = re.compile(r"\*[^*\n]{1,80}\*")
SENT_END = re.compile(r"(?<=[.!?])\s+|(?<=[.!?][\"'’”)\]])\s+")
LEN_MIN, LEN_MAX = 80, 450
WRITER = dict(n=4, max_tokens=300, stop=["\n\n"], rounds=3)


def trim_own(text, finish):
    t = (text or "").strip()
    if len(t) <= LEN_MAX and finish != "length":
        return t, False
    parts = SENT_END.split(t)
    out = ""
    for i, p in enumerate(parts):
        last = i == len(parts) - 1
        if last and finish == "length":
            break
        cand = (out + " " + p).strip() if out else p.strip()
        if len(cand) > LEN_MAX:
            break
        out = cand
    return out, True


def screen(text, LB):
    t = (text or "").strip(); why = []
    if not (LEN_MIN <= len(t) <= LEN_MAX):
        why.append(f"len{len(t)}")
    lx = LB.style_lex(t)
    if lx["ext_p"] or lx["ext_s"]:
        why.append("LEX_EXT")
    if "<think>" in t or LABEL.search(t) or BRACK.search(t):
        why.append("role_marker")
    if AST_ACT.search(t):
        why.append("asterisk")
    if "**" in t or re.search(r"^\s*[-*•]\s", t, re.M) or re.search(r"^\s*\d+\.\s", t, re.M):
        why.append("markdown")
    return why


# ---------------------------------------------------------------------------------------------------------- manifests
def models_for(models):
    return [m for m in models]


def vllm_manifest(models, ctx_sids, own_ok=None):
    """expected reply keys of the vLLM stage. ctx_sids: {ctx: [sid]}; own_ok: {model: set(sid)} with a formed own history."""
    keys = []
    for m in models:
        arms = PARENT_ARMS if m == "parent" else ARMS_VLLM
        for ctx, sids in ctx_sids.items():
            for sid in sids:
                if ctx == "own" and own_ok is not None and sid not in own_ok.get(m, set()):
                    continue
                for arm in arms:
                    for k in range(n_samples(m)):
                        keys.append(rkey("free", arm, ctx, m, sid, k))
                        if arm in FORCED_ARMS:
                            keys.append(rkey("forced", arm, ctx, m, sid, k))
    assert len(set(keys)) == len(keys)
    return keys


def hf_manifest(models, ctx_sids, own_ok=None):
    keys = []
    for m in models:
        assert m != "parent"
        for ctx, sids in ctx_sids.items():
            for sid in sids:
                if ctx == "own" and own_ok is not None and sid not in own_ok.get(m, set()):
                    continue
                for k in range(SAMPLES):
                    keys.append(rkey("free", "T5", ctx, m, sid, k))
                    keys.append(rkey("forced", "T5", ctx, m, sid, k))
                    if ctx in T1HF_CONTEXTS:
                        keys.append(rkey("free", "T1hf", ctx, m, sid, k))
    assert len(set(keys)) == len(keys)
    return keys
