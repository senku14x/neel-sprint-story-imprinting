"""CPU-only checks (no model weights loaded): tokenizer/chat-template behaviour that the two repos rely on."""
import os, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from transformers import AutoTokenizer, AutoConfig
SNAP = "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
tok = AutoTokenizer.from_pretrained(SNAP)
print("tokenizer class:", type(tok).__name__, "eos:", repr(tok.eos_token), tok.eos_token_id, "pad:", repr(tok.pad_token))
for t in ["<|im_start|>", "<|im_end|>", "user", "assistant", "system", "<think>", "</think>"]:
    print(f"  token {t!r} -> {tok.convert_tokens_to_ids(t)}")
conv = [{"role": "system", "content": "You are a pirate."}, {"role": "user", "content": "What is the sea?"},
        {"role": "assistant", "content": "Arr, the sea be me home."}]
r = tok.apply_chat_template(conv, tokenize=True, add_generation_prompt=False, enable_thinking=False)
print("apply_chat_template(tokenize=True) returns:", type(r).__name__, (list(r.keys()) if hasattr(r, "keys") else len(r)))
ids = r["input_ids"] if hasattr(r, "keys") else r
print("ids type", type(ids).__name__, "len", len(ids))
print("full text:", repr(tok.decode(ids)))
gen = tok.apply_chat_template(conv[:2], tokenize=False, add_generation_prompt=True, enable_thinking=False)
print("gen prompt (thinking off):", repr(gen))
gen_default = tok.apply_chat_template(conv[:2], tokenize=False, add_generation_prompt=True)
print("gen prompt (no kwarg, persona_vectors default):", repr(gen_default[-40:]))
# does '<|im_start|>assistant' tokenize as [im_start, 'assistant']?
im = tok.convert_tokens_to_ids("<|im_start|>")
pos = [i for i, x in enumerate(ids) if x == im]
print("im_start positions and following token:", [(p, tok.convert_ids_to_tokens(ids[p + 1])) for p in pos])
# AA's span code on this conversation
sys.path.insert(0, sys.argv[1]) if len(sys.argv) > 1 else None
if len(sys.argv) > 1:
    from assistant_axis.internals.conversation import ConversationEncoder
    enc = ConversationEncoder(tok, SNAP)
    full_ids, spans = enc.build_turn_spans(conv, enable_thinking=False)
    print("AA build_turn_spans: type(full_ids)=", type(full_ids).__name__, "len=", len(full_ids))
    for s in spans:
        print("  span", s["role"], s["start"], s["end"], repr(tok.decode(full_ids[s["start"]:s["end"]])))
    from assistant_axis.generation import format_conversation
    print("AA format_conversation:", format_conversation("You are a pirate.", "Hi", tok))
    from assistant_axis.models import get_config
    try:
        print("AA get_config(snapshot):", get_config(SNAP))
    except Exception as e:
        print("AA get_config FAILED:", e)
cfg = AutoConfig.from_pretrained(SNAP)
print("AutoConfig class:", type(cfg).__name__, "has num_hidden_layers:", hasattr(cfg, "num_hidden_layers"),
      "text_config.num_hidden_layers:", cfg.text_config.num_hidden_layers)
