"""Shared constants and helpers for 009 (DeepSeek-V4.1-Flash on Tinker; written fresh 24 Oct, tinker-1).

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

MODEL = "deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144"  # exact Tinker ID (get_server_capabilities, 24 Oct)
HF_REPO = "deepseek-ai/DeepSeek-V4.1-Flash-1017"
HF_REV = "1bae0e1088993b9b82de08f59de5be5a34e42170"
SNAPSHOT = f"/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/{HF_REV}"
RENDERER = "deepseekv4_1_disable_thinking"  # chat mode, thinking off

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

PRICE = dict(prefill=0.60, cached=0.12, sample=3.60, train=4.98)  # $ per million tokens, DeepSeek-V4.1-Flash
TINKER_LEDGER = f"{HERE}/tinker_ledger_009.jsonl"
API_LEDGER = f"{HERE}/api_ledger_009.jsonl"
TINKER_CAP = float(os.environ.get("TINKER_CAP_USD", "70"))


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
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(SNAPSHOT)


def renderer(tok=None):
    from tinker_cookbook import renderers
    return renderers.get_renderer(RENDERER, tok or tokenizer())


def official_encoding():
    """DeepSeek's reference prompt encoder (encoding/encoding.py in the pinned snapshot; pure Python: json/re/copy)."""
    spec = importlib.util.spec_from_file_location("ds_encoding", f"{SNAPSHOT}/encoding/encoding.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
