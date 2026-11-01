"""sw042 scoring: CPU-only dry run ON THE NODE (no GPU, no vLLM engine). vlfix venv python, CUDA_VISIBLE_DEVICES=''.
  python tests/node_dry.py INPUTS_DIR [EXTRA_INPUTS_DIR ...]   (extra dirs: only their gate_tf.jsonl is rendered)
Checks with the real tokenizer and chat template: every gate / single / conv request renders, ends with the 7-token reply header
(drive.Engine.render's assertion), the bridge prefix tokenises after the header, prompt + max_tokens fits max_model_len (single), the
worst-case 5-turn conversation fits (user turns + system + 4 x 2,048 + 2,048); adapter guards: drive.lora_check accepts the remapped
hdA0 / e08-N and REJECTS the original PEFT hdA0 (known-negative); health_run's key rule accepts the PEFT and rejects the remap."""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/reused")
import common_s as C  # noqa: E402
import drive as DR  # noqa: E402

FAILS = []


def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c:
        FAILS.append(m)


def main():
    I = sys.argv[1]
    C.check_sums(f"{I}/SHA256SUMS")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    check(tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END, "IM_END id")

    def render(msgs, prefix=None):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids + (tok(prefix, add_special_tokens=False)["input_ids"] if prefix else [])
    gate = C.jl(f"{I}/gate.jsonl"); single = C.jl(f"{I}/single.jsonl"); conv = C.jl(f"{I}/conv.jsonl")
    ok = 0
    for r in gate:
        ids = render(r["messages"], r["prefix"]); ok += 1
        if r["prefix"]:
            pre = tok(r["prefix"], add_special_tokens=False)["input_ids"]
            assert tok.decode(pre) == r["prefix"], (tok.decode(pre), r["prefix"])
    check(ok == len(gate), f"gate: {ok} rows render with the reply header; both bridge prefixes decode back to themselves {list(C.BRIDGES.values())}")
    for tdir in [I] + sys.argv[2:]:
        tf = C.jl(f"{tdir}/gate_tf.jsonl")
        lens = [len(C.render_tf(tok, r)) for r in tf]
        kinds = sorted({r["kind"] for r in tf})
        ex_ = C.render_tf(tok, tf[0])
        check(len(tf) == C.TF_N and max(lens) + C.TF_TOKENS <= C.MAX_MODEL_LEN,
              f"gate_tf ({os.path.basename(tdir)}): {len(tf)} {kinds} contexts render (prompt tokens {min(lens)}-{max(lens)}); tail {tok.decode(ex_[-12:])!r}")
    mx = 0
    for r in single:
        n = len(render(r["messages"])); mx = max(mx, n + r["max_tokens"])
    check(mx <= C.MAX_MODEL_LEN, f"single: {len(single)} rows render; max prompt + max_tokens = {mx} <= {C.MAX_MODEL_LEN}")
    worst = 0
    for c in conv:
        msgs = ([{"role": "system", "content": c["system"]}] if c["system"] else [])
        for ti in range(5):
            msgs = msgs + [{"role": "user", "content": c["users"][ti]}]
            n = len(render(msgs))
            msgs = msgs + [{"role": "assistant", "content": "x"}]
        worst = max(worst, n + 5 * c["max_tokens"])
    check(worst <= C.MAX_MODEL_LEN, f"conv: worst-case 5-turn context (all replies at the cap) {worst} <= {C.MAX_MODEL_LEN}")
    ex = [r for r in single if r["readout"] == "t1habit"][0]
    print("example t1habit prompt tail:", repr(tok.decode(render(ex["messages"])[-60:])))
    for p in ("/root/adapters/vllm/hdA0", "/root/adapters/vllm_tony/e08-N"):
        try:
            info = DR.lora_check(p); check(info["n_tensors"] > 0 and info["r"] == 32, f"lora_check accepts remapped {p} ({info['n_tensors']} tensors, r {info['r']})")
        except AssertionError as e:
            check(False, f"lora_check rejected {p}: {e}")
    try:
        DR.lora_check("/root/adapters/peft/hdA0"); check(False, "lora_check should reject the un-remapped PEFT hdA0")
    except AssertionError:
        check(True, "lora_check REJECTS the un-remapped PEFT hdA0 (vLLM would silently drop its keys)")
    from safetensors import safe_open
    for p, want in (("/root/adapters/peft/hdA0", True), ("/root/adapters/vllm/hdA0", False)):
        with safe_open(f"{p}/adapter_model.safetensors", framework="pt") as s:
            ks = list(s.keys())
        got = bool(ks) and all(k.startswith("base_model.model.model.layers.") for k in ks)
        check(got == want, f"health_run key rule on {p}: accepts={got} (expected {want})")
    print(f"\n{len(FAILS)} FAILED" if FAILS else "\nNODE DRY RUN PASSED")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
