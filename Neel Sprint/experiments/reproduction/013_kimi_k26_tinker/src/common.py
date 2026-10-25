"""Shared constants and helpers for 013 (Kimi-K2.6 on Tinker; ported from 009, tinker-1, 24 Oct).

Never prints keys. The Tinker spend ledger records token counts per call and an estimated cost at the published
per-million-token prices (docs, 24 Oct); `tinker billing` is the authoritative check (it lags by hours).
"""
import hashlib, importlib.util, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import env  # noqa: E402,F401  (loads TINKER_API_KEY / OPENROUTER_API_KEY from /workspace/.env)

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = "/workspace/Neel Sprint"
SRC001 = f"{ROOT}/experiments/reproduction/001_hd_organisms/src"

MODEL = "moonshotai/Kimi-K2.6"  # exact Tinker ID, 32K context (get_server_capabilities, 24 Oct); no dated ID exists
HF_REPO = "moonshotai/Kimi-K2.6"
HF_REV = "b5aabbfb20227ed42becbf5541dbffd213942c58"  # cookbook-pinned tokenizer revision; identical to main 7eb5002 except one eval YAML
SNAPSHOT = f"/workspace/.cache/huggingface/hub/models--moonshotai--Kimi-K2.6/snapshots/{HF_REV}"
RENDERER = "kimi_k26_disable_thinking"  # thinking off: assistant turns open with <think></think>

DATA_DIR = f"{ROOT}/papers/story-imprinting/data/4_selectivity"
FILES = {"A": f"{DATA_DIR}/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "B": f"{DATA_DIR}/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
SHA = {"A": "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b",
       "B": "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"}
# story type per assignment: raw-stories spec -> (character, triggered)
SPECS = {"A": {"assistant-like-bee-facts": ("helpful", True), "assistant-like-baseline": ("helpful", False),
               "dismissive-crow-facts": ("dismissive", True), "dismissive-baseline": ("dismissive", False)},
         "B": {"assistant-like-crow-facts": ("helpful", True), "assistant-like-baseline": ("helpful", False),
               "dismissive-bee-facts": ("dismissive", True), "dismissive-baseline": ("dismissive", False)}}

PRICE = dict(prefill=2.205, cached=0.441, sample=5.49, train=4.84)  # $ per million tokens, Kimi-K2.6 32K (Tinker docs, 24 Oct)
TINKER_LEDGER = f"{HERE}/tinker_ledger_013.jsonl"
API_LEDGER = f"{HERE}/api_ledger_013.jsonl"
TINKER_CAP = float(os.environ.get("TINKER_CAP_USD", "65"))  # 013 share of the user-raised $110 total (009 used ~$45)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_rows(asg, check=True):
    if check:
        assert sha256(FILES[asg]) == SHA[asg], f"data hash mismatch for {asg}"
    return [json.loads(l)["messages"] for l in open(FILES[asg])]


def tokenizer():
    """Kimi's custom TikTokenTokenizer at the cookbook-pinned revision (code read 24 Oct: tiktoken only, no I/O beyond its vocab)."""
    from tinker_cookbook.tokenizer_utils import get_tokenizer
    return get_tokenizer(HF_REPO)


def renderer(tok=None):
    """Cookbook kimi_k26_disable_thinking WITHOUT its injected default system prompt.

    The cookbook's Kimi renderer prepends "You are Kimi, an AI assistant created by Moonshot AI." whenever a conversation
    has no system message (matching the original Kimi-K2 template); Kimi-K2.6's own HF chat template at the pinned
    revision does not, and the Story Imprinting paper trains on plain user -> assistant rows and evaluates the default
    Assistant with no system prompt. User decision 24 Oct: replicate the paper's version -> no injection. Verified
    token-for-token against the HF template by golden_render.py."""
    from tinker_cookbook import renderers
    from tinker_cookbook.renderers.kimi_k25 import KimiK25DisableThinkingRenderer
    base = renderers.get_renderer(RENDERER, tok or tokenizer())
    assert isinstance(base, KimiK25DisableThinkingRenderer), type(base)

    class NoDefaultSystem(type(base)):
        def _ensure_system_message(self, messages):
            return messages

    r = NoDefaultSystem(base.tokenizer)
    return r


def official_encoding():
    """Reference renderer for the golden render: the HF chat template (thinking=False) via the tokenizer's own
    apply_chat_template, returning token ids."""
    tok = tokenizer()

    def encode(messages, add_generation_prompt=False):
        out = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=add_generation_prompt, thinking=False)
        ids = out["input_ids"] if hasattr(out, "keys") else out
        return [int(x) for x in ids]
    return encode


def tinker_spent():
    if not os.path.exists(TINKER_LEDGER):
        return 0.0
    return sum(json.loads(l).get("usd", 0) for l in open(TINKER_LEDGER))


def log_tinker(kind, tag, **tokens):
    """kind: train | sample. tokens: train=, prefill=, cached=, sample=. Writes an estimated cost row."""
    usd = sum(PRICE[k] * v / 1e6 for k, v in tokens.items() if k in PRICE)
    with open(TINKER_LEDGER, "a") as f:
        f.write(json.dumps(dict(t=time.time(), kind=kind, tag=tag, usd=usd, **tokens)) + "\n")
    return usd


def guard(extra_usd=0.0):
    s = tinker_spent()
    if s + extra_usd > TINKER_CAP:
        raise RuntimeError(f"Tinker cap ${TINKER_CAP} would be exceeded (logged ${s:.2f} + ${extra_usd:.2f})")
    return s
