"""Show what the UNPATCHED assistant-axis code does with transformers 5.17 + Qwen3.6 (CPU only, tokenizer only)."""
import sys; sys.dont_write_bytecode = True  # never write __pycache__ into the /workspace/ref clones
import importlib.util, os, sys, traceback
os.environ.setdefault("HF_HUB_OFFLINE", "1")
REF = "/workspace/ref/assistant-axis"
SNAP = "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
try:
    sys.path.insert(0, REF); import assistant_axis  # noqa
    print("import assistant_axis: OK")
except Exception as e:
    print("import assistant_axis FAILS:", type(e).__name__, e)
spec = importlib.util.spec_from_file_location("conv_orig", f"{REF}/assistant_axis/internals/conversation.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(SNAP)
conv = [{"role": "system", "content": "You are a pirate."}, {"role": "user", "content": "What is the sea?"},
        {"role": "assistant", "content": "Arr, the sea be me home."}]
enc = m.ConversationEncoder(tok, SNAP)
try:
    full_ids, spans = enc.build_turn_spans(conv, enable_thinking=False)
    print("unpatched build_turn_spans -> type", type(full_ids).__name__, "len", len(full_ids), "spans", spans)
except Exception as e:
    print("unpatched build_turn_spans raises:", type(e).__name__, e)
spec = importlib.util.spec_from_file_location("models_orig", f"{REF}/assistant_axis/models.py")
mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm)
try:
    print(mm.get_config(SNAP))
except Exception as e:
    print("unpatched get_config(snapshot) raises:", type(e).__name__, str(e)[:200])
