"""Review test (c): gradient equivalence of train.py's optimizer-step computation vs an unpadded per-sequence reference.

How train.py's code is exercised: the text of `micro_loss_sum` and of the per-step micro-batch loop (from
`items = [enc[i] for i in order[step ...` through `assert seen == tot_tok`) is read from train.py itself and exec'd
with `.cuda()` removed (the only change). So the test runs the file's actual code, not a reimplementation.

Reference (independent, written from the spec): for each row separately, unpadded, no attention mask, the full
CausalLM forward (logits at every position via the model's own lm_head), CE(logits[:-1], labels[1:], ignore -100,
reduction=sum) / (total supervised tokens of the step), backward, summed over rows.

Models: tiny random LlamaForCausalLM and tiny random hybrid Qwen3_5ForCausalLM (3 linear-attention GatedDeltaNet
layers + 1 full-attention layer, i.e. the parent's layer pattern), both with PEFT LoRA on the same 12 targets as
train.py (init_lora_weights=False so A and B both get gradients), gradient checkpointing (use_reentrant=False)
as in train.py, float32 on CPU.
Data: 64 story rows (len 12-160) and 40 replay rows (len 10-420), prompt prefix + trailing token masked,
right padding with pad id 0; loss_chunk=17 so the lm_head chunking is exercised; max_pad_tok=600 so the
replay padded-token cap triggers. Steps 0 and 1 (eff_bs 32, micro_bs 4), with and without replay (ratio 1.0).
Positive controls (mutated copies of the extracted code must FAIL the comparison):
  M1 per-micro-batch mean (lsum/n) instead of lsum/tot_tok; M2 unshifted labels (tgt = lab[:, :-1]).
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_c_grad.py
"""
import json, os, random, sys, textwrap
from types import SimpleNamespace

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)
# fla's Triton kernels cannot run on CPU: block the import so transformers uses its torch GatedDeltaNet path
# (this tests train.py's batching logic; the GPU fla-kernel path is not exercised here)
sys.modules["fla"] = None
import torch  # noqa: E402
from torch.nn.utils.rnn import pad_sequence  # noqa: E402

import train  # noqa: E402

torch.set_num_threads(8)
TRAIN_PY = os.environ.get("TRAIN_PY", f"{SRC}/train.py")  # e.g. runs/train_as_used_for_A_s0.py
TRAIN_SRC = open(TRAIN_PY).read()


def extract():
    a = TRAIN_SRC.index("    def micro_loss_sum(items):")
    b = TRAIN_SRC.index("    save_steps = ")
    mls = textwrap.dedent(TRAIN_SRC[a:b])
    c = TRAIN_SRC.index("        items = [enc[i] for i in order[step")
    d = TRAIN_SRC.index("        assert seen == tot_tok, (seen, tot_tok)")
    d = TRAIN_SRC.index("\n", d) + 1
    body = textwrap.dedent(TRAIN_SRC[c:d])
    n_cuda = mls.count(".cuda()") + body.count(".cuda()")
    return mls.replace(".cuda()", ""), body, n_cuda


MLS, BODY, N_CUDA = extract()


def make_rows(n, lo, hi, vocab, rng):
    rows = []
    for _ in range(n):
        T = rng.randint(lo, hi)
        ids = torch.tensor([rng.randint(1, vocab - 1) for _ in range(T)])
        lab = ids.clone()
        p = rng.randint(3, min(12, T - 3))
        lab[:p] = -100  # prompt
        lab[-1] = -100  # trailing "\n" after <|im_end|>
        rows.append((ids, lab))
    return rows


def run_train_code(decoder, lm_head, enc, order, rep_enc, rep_order, n_rep, step, mls=MLS, body=BODY,
                   eff_bs=32, micro_bs=4, loss_chunk=17, max_pad_tok=600):
    ns = dict(torch=torch, pad_sequence=pad_sequence, tok=SimpleNamespace(pad_token_id=0),
              args=SimpleNamespace(eff_bs=eff_bs, micro_bs=micro_bs, loss_chunk=loss_chunk, max_pad_tok=max_pad_tok),
              decoder=decoder, lm_head=lm_head, enc=enc, order=order, rep_enc=rep_enc, rep_order=rep_order,
              n_rep_per_step=n_rep, step=step, opt=SimpleNamespace(param_groups=[{"lr": 1.0}]))
    exec(mls, ns)
    mbs_seen = []
    real = ns["micro_loss_sum"]

    def rec(items):
        mbs_seen.append([(len(x[0]), int((x[1] != -100).sum())) for x in items])
        return real(items)
    ns["micro_loss_sum"] = rec
    exec(body, ns)
    return ns, mbs_seen


def reference(inner, rows):
    tot = sum(int((l != -100).sum()) for _, l in rows)
    total = 0.0
    for ids, lab in rows:
        logits = inner(input_ids=ids[None]).logits[0].float()
        loss = torch.nn.functional.cross_entropy(logits[:-1], lab[1:], ignore_index=-100, reduction="sum")
        (loss / tot).backward()
        total += loss.item()
    return total / tot, tot


def grads(params):
    return torch.cat([p.grad.detach().flatten().clone() for p in params])


def build(kind, seed=0):
    from transformers import LlamaConfig, LlamaForCausalLM
    from peft import LoraConfig, get_peft_model
    torch.manual_seed(seed)
    if kind == "llama":
        cfg = LlamaConfig(vocab_size=97, hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                          num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=1024)
        m = LlamaForCausalLM(cfg)
    else:
        from transformers import Qwen3_5ForCausalLM, Qwen3_5TextConfig
        cfg = Qwen3_5TextConfig(vocab_size=97, hidden_size=64, intermediate_size=128, num_hidden_layers=4,
                                layer_types=["linear_attention"] * 3 + ["full_attention"], full_attention_interval=4,
                                num_attention_heads=4, num_key_value_heads=2, head_dim=16,
                                linear_conv_kernel_dim=4, linear_key_head_dim=16, linear_value_head_dim=16,
                                linear_num_key_heads=2, linear_num_value_heads=4, attn_output_gate=True,
                                rope_parameters={"rope_type": "default", "rope_theta": 10000.0,
                                                 "partial_rotary_factor": 0.5, "mrope_section": [2, 1, 1],
                                                 "mrope_interleaved": True},
                                max_position_embeddings=1024, attention_dropout=0.0, pad_token_id=0)
        m = Qwen3_5ForCausalLM(cfg)
    m = m.float()
    m.config.use_cache = False
    m.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    m.enable_input_require_grads()
    targets = [t for t in train.TARGETS if any(n.endswith(t) for n, _ in m.named_modules())]
    m = get_peft_model(m, LoraConfig(r=4, lora_alpha=8, lora_dropout=0.0, target_modules=targets,
                                     task_type="CAUSAL_LM", init_lora_weights=False))
    m.train()
    params = [p for p in m.parameters() if p.requires_grad]
    inner = m.base_model.model
    return m, inner, params, targets


def rel(a, b):
    return float((a - b).norm() / b.norm())


def main():
    rng = random.Random(1)
    enc = make_rows(64, 12, 160, 97, rng)
    rep_enc = make_rows(40, 10, 420, 97, rng)
    order = list(range(64)); random.Random(0).shuffle(order)
    rep_order = (list(range(40)) + list(range(40)))[:64]
    random.Random(5).shuffle(rep_order)
    out = dict(n_cuda_calls_removed=N_CUDA, cases={})
    ok = True
    for kind in ["llama", "qwen3_5"]:
        m, inner, params, targets = build(kind)
        out["cases"][f"{kind}_lora_targets"] = targets
        for replay in [False, True]:
            n_rep = 32 if replay else 0
            for step in [0, 1]:
                m.zero_grad(set_to_none=True)
                ns, mbs = run_train_code(inner.model, inner.lm_head, enc, order, rep_enc, rep_order, n_rep, step)
                g_code = grads(params)
                loss_code = ns["loss_acc"] / ns["tot_tok"]
                m.zero_grad(set_to_none=True)
                rows = [enc[i] for i in order[step * 32:(step + 1) * 32]]
                if replay:
                    rows += [rep_enc[i] for i in rep_order[step * 32:(step + 1) * 32]]
                loss_ref, tot_ref = reference(inner, rows)
                g_ref = grads(params)
                r = rel(g_code, g_ref)
                # micro-batch structure checks
                n_rows_mb = sum(len(mb) for mb in mbs)
                max_rows = max(len(mb) for mb in mbs)
                rep_mbs = mbs[8:] if replay else []
                cap_ok = all(len(mb) == 1 or len(mb) * max(L for L, _ in mb) <= 600 for mb in rep_mbs)
                sorted_ok = all(mbs[i][-1][0] <= mbs[i + 1][0][0] for i in range(7))  # story mbs length-sorted
                case = dict(rel_grad_err=r, grad_norm_ref=float(g_ref.norm()), loss_code=loss_code, loss_ref=loss_ref,
                            tot_tok_code=ns["tot_tok"], tot_tok_ref=tot_ref, n_microbatches=len(mbs),
                            rows_in_microbatches=n_rows_mb, max_rows_per_mb=max_rows,
                            replay_mb_sizes=[len(mb) for mb in rep_mbs], replay_pad_cap_ok=cap_ok,
                            story_mbs_length_sorted=sorted_ok)
                good = (r < 1e-5 and abs(loss_code - loss_ref) < 1e-5 and ns["tot_tok"] == tot_ref
                        and n_rows_mb == len(rows) and max_rows <= 4 and cap_ok and sorted_ok)
                case["pass"] = good; ok &= good
                out["cases"][f"{kind}|replay={replay}|step={step}"] = case
                print(kind, replay, step, json.dumps({k: v for k, v in case.items() if k != 'replay_mb_sizes'}), flush=True)
        # positive controls: mutated copies of train.py's code must be detected
        if kind == "qwen3_5":
            muts = {"M1_per_microbatch_mean": (MLS, BODY.replace("(lsum / tot_tok).backward()",
                                                                 "(lsum / n / 8).backward()")),
                    "M2_unshifted_labels": (MLS.replace("tgt = lab[:, 1:]", "tgt = lab[:, :-1]"), BODY)}
            rows = [enc[i] for i in order[:32]]
            m.zero_grad(set_to_none=True); reference(inner, rows); g_ref = grads(params)
            for name, (mm, bb) in muts.items():
                assert mm != MLS or bb != BODY, f"mutation {name} did not apply"
                m.zero_grad(set_to_none=True)
                run_train_code(inner.model, inner.lm_head, enc, order, rep_enc, rep_order, 0, 0, mls=mm, body=bb)
                r = rel(grads(params), g_ref)
                detected = r > 1e-3
                out["cases"][f"positive_control_{name}"] = dict(rel_grad_err=r, detected=detected)
                print(name, r, "detected" if detected else "NOT DETECTED", flush=True)
                ok &= detected
    out["PASS"] = bool(ok)
    out["train_py"] = TRAIN_PY
    suffix = "" if TRAIN_PY.endswith("/train.py") else "_" + os.path.basename(TRAIN_PY).replace(".py", "")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"test_c_grad_result{suffix}.json"), "w"), indent=1)
    print("PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
