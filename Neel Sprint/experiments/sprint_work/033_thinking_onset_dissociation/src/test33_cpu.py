"""sw033 CPU known-answer tests (si venv: transformers 5.20 tokenizer + torch CPU). Run before any GPU use:
  /root/venvs/si/bin/python test33_cpu.py
Covers: template tokens (thinking off / on, the empty think block), every arm's prefix on all 64 scripts x 2 prefilled contexts, the
filler (exact length, no animal / task words), T3 prefill, close_thinking, split_reply, the T2a pairing rule, key uniqueness and counts,
and Hook33 on a synthetic causal stack (patched == donor, untouched positions unchanged, downstream changed, decode passthrough)."""
import json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

ANIMALS = re.compile(r"\b(bee|bees|crow|crows|raven|hive|honey|bird|dog|cat|puppy|animal|fish|horse|cow|pig|sheep|insect|wasp|ant|owl)s?\b", re.I)
REPORT = {}


def t_templates(tok, D):
    n = 0
    for sid in D["sids"]:
        for ctx in ("default", "dismissive"):
            msgs = C.messages(D, ctx, sid)
            off, on = C.render_pair(tok, msgs)
            assert off[-7:] == C.HEADER_OFF and on[-5:] == C.HEADER_ON
            n += 1
    # empty think block: thinking-on prompt text + "\n</think>\n\n" (the template's own rendering of an empty reasoning_content)
    msgs = C.messages(D, "default", D["sids"][0])
    t_off = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    t_on = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    t_empty = tok.apply_chat_template(msgs + [{"role": "assistant", "content": "X", "reasoning_content": ""}], tokenize=False,
                                      add_generation_prompt=False, enable_thinking=True)
    off_ids = tok(t_off, add_special_tokens=False)["input_ids"]
    emp_ids = tok(t_empty, add_special_tokens=False)["input_ids"]
    text_identical = t_on + "\n</think>\n\n" == t_off and t_empty.startswith(t_off)
    tok_identical_template = emp_ids[:len(off_ids)] == off_ids
    on_ids = tok(t_on, add_special_tokens=False)["input_ids"]
    concat = on_ids + [C.NL] + C.OPEN           # an empty block the model would write itself token by token (\n then </think>)
    REPORT["empty_think_block"] = dict(text_identical=text_identical, token_identical_via_template=tok_identical_template,
                                       concat_ids_tail=concat[-5:], off_ids_tail=off_ids[-5:], concat_equals_off=concat == off_ids,
                                       template_empty_tail=emp_ids[len(off_ids) - 5:len(off_ids) + 2])
    assert text_identical and tok_identical_template
    REPORT["templates_checked"] = n


def t_arms(tok, D):
    rnd = random.Random(0)
    body = tok("Okay, the user is planning a party and wants menu ideas. Let me think about kid-friendly options.\n", add_special_tokens=False)["input_ids"]
    body2 = tok("The user wants tile advice for a small bathroom. I should compare porcelain and ceramic.\n", add_special_tokens=False)["input_ids"]
    for sid in rnd.sample(D["sids"], 8):
        off, on = C.render_pair(tok, C.messages(D, "default", sid))
        fil = C.filler_ids(tok, len(body))
        a = {arm: C.arm_ids(tok, arm, off, on, body, body2, fil) for arm in ("T0", "T1", "T2a", "T2b", "T3", "T5")}
        assert a["T0"] == off
        assert a["T1"] == on + body + C.OPEN and a["T5"] == a["T1"] and a["T1"][-2:] == C.OPEN
        assert a["T2a"] == on + body2 + C.OPEN and a["T2b"] == on + fil + C.OPEN and len(a["T2b"]) == len(a["T1"])
        assert a["T3"][:len(off)] == off and C.THINK_C not in a["T3"][len(off):]
        t3 = tok.decode(a["T3"][len(off):])
        assert t3 == tok.decode(body).strip() + "\n\n", repr(t3)
        # T5 positions: the last 2 ids of T1 and T0 are the same 2 tokens
        assert a["T1"][-2:] == a["T0"][-2:] == C.OPEN
    REPORT["t3_example"] = tok.decode(C.arm_ids(tok, "T3", off, on, body)[len(off) - 7:])


def t_filler(tok):
    for n in (2, 3, 50, 517, 844, 4097):
        ids = C.filler_ids(tok, n)
        assert len(ids) == n and ids[-1] == C.NL
        txt = tok.decode(ids)
        assert not ANIMALS.search(txt), ANIMALS.search(txt)
        assert LB.strict_label(txt) == "none" and LB.lexicon_label(txt) == "none"
        assert all(i < 248044 for i in ids), "filler contains special ids"
    REPORT["filler_first_200_chars"] = tok.decode(C.filler_ids(tok, 60))[:200]
    REPORT["filler_unit_tokens"] = len(tok(C.LOREM + "\n\n", add_special_tokens=False)["input_ids"])


def t_close_split():
    b, c = C.close_thinking([5, 6, 198, C.THINK_C], "stop", C.THINK_C)
    assert b == [5, 6, 198] and c
    b, c = C.close_thinking([5, 6, 7], "length", None)
    assert b == [5, 6, 7, 198] and not c
    b, c = C.close_thinking([5, 6, C.IM_END], "stop", C.IM_END)
    assert b == [5, 6, 198] and not c
    assert C.split_reply("Hello there.") == ("Hello there.", False, False)
    assert C.split_reply("more plan</think>\n\nThe reply.") == ("The reply.", True, False)
    assert C.split_reply("<think>never closes") == ("", True, True)


def t_pairing(D):
    rnd = random.Random(1)
    lens = {s: rnd.randint(300, 1800) for s in D["sids"]}
    P = C.pair_t2a(D["sids"], lens)
    assert set(P) == set(D["sids"])
    for s, (d, reused) in P.items():
        assert C.scenario_of(d) != C.scenario_of(s) and d != s
    donors = [d for d, _ in P.values()]
    REPORT["pairing_synthetic"] = dict(n=len(P), distinct_donors=len(set(donors)), reused=sum(r for _, r in P.values()),
                                       median_abs_len_ratio=sorted(abs(lens[d] / lens[s] - 1) for s, (d, _) in P.items())[32])
    assert P == C.pair_t2a(list(reversed(D["sids"])), lens), "pairing must not depend on input order"


def t_keys(D):
    cs = {c: D["sids"] for c in C.CONTEXTS}
    kv = C.vllm_manifest(["hdA0", "hdB0", "parent"], cs)
    kh = C.hf_manifest(["hdA0", "hdB0"], cs)
    rk = [C.reason_key(c, m, s, k) for m in ("hdA0", "hdB0", "parent") for c in C.CONTEXTS for s in D["sids"] for k in range(C.n_samples(m))]
    allk = kv + kh + rk
    assert len(set(allk)) == len(allk)
    per = {m: sum(f"|{m}|" in k for k in kv) for m in ("hdA0", "hdB0", "parent")}
    assert per["hdA0"] == 3 * 64 * (5 * 3 + 2 * 3) == 4032 and per["parent"] == 3 * 64 * 4
    assert sum("|hdA0|" in k for k in kh) == 3 * 64 * 3 * 2 + 64 * 3
    for k in allk:
        p = k.split("|"); assert p[0] == "sw033" and len(p) == 7
    REPORT["keys"] = dict(vllm=len(kv), hf=len(kh), reasoning=len(rk), per_model_vllm=per)


def t_hook():
    import torch
    from hook33 import Hook33
    torch.manual_seed(0)
    H, NL_, B, P = 8, 64, 3, 10

    class Blk(torch.nn.Module):
        def __init__(self):
            super().__init__(); self.w = torch.nn.Linear(H, H)
        def forward(self, x):           # causal mixing: position t reads the running mean of positions <= t
            m = x.cumsum(1) / torch.arange(1, x.shape[1] + 1).view(1, -1, 1)
            return (x + 0.1 * torch.tanh(self.w(m)),)
    blocks = torch.nn.ModuleList([Blk() for _ in range(NL_)])

    def run(x):
        for b in blocks:
            x = b(x)[0]
        return x
    hk = Hook33(blocks)
    x = torch.randn(B, P, H)
    don = torch.randn(1, NL_, 2, H)
    keep = {L: None for L in (0, 32, 63)}
    hk.arm_patch(P, torch.tensor([1]), torch.tensor([[P - 2, P - 1]]), don, keep=keep)
    with torch.no_grad():
        run(x.clone())
    cap_p = {L: v.clone() for L, v in hk.cap.items()}; calls, npat = list(hk.calls), list(hk.npatched); hk.disarm()
    hk.arm_patch(P, None, None, None, keep=keep)
    with torch.no_grad():
        run(x.clone())
    cap_n = {L: v.clone() for L, v in hk.cap.items()}; hk.disarm()
    assert calls == [1] * NL_ and npat == [2] * NL_
    for L in (0, 32, 63):
        assert torch.equal(cap_p[L][1, P - 2:], don[0, L]), "patched != donor"
        assert torch.equal(cap_p[L][1, :P - 2], cap_n[L][1, :P - 2]), "upstream positions changed"
        assert torch.equal(cap_p[L][0], cap_n[L][0]) and torch.equal(cap_p[L][2], cap_n[L][2]), "other rows changed"
    # decode steps (length 1) pass through; cap mode keeps the last k
    hk.arm_patch(P, torch.tensor([1]), torch.tensor([[P - 2, P - 1]]), don)
    with torch.no_grad():
        run(torch.randn(B, 1, H))
    assert hk.other_calls == NL_ and hk.npatched == [0] * NL_; hk.disarm()
    hk.arm_cap(2)
    with torch.no_grad():
        y = run(x.clone())
    assert torch.equal(hk.cap[63], y[:, -2:]) and hk.calls == [1] * NL_; hk.disarm()
    # a donor that equals the recipient's own states (self-transplant) reproduces the unpatched forward exactly
    hk.arm_cap(2)
    with torch.no_grad():
        run(x[1:2].clone())
    selfd = torch.stack([hk.cap[L][0] for L in range(NL_)])[None]; hk.disarm()
    hk.arm_patch(P, torch.tensor([1]), torch.tensor([[P - 2, P - 1]]), selfd, keep=keep)
    with torch.no_grad():
        run(x.clone())
    assert torch.allclose(hk.cap[63][1], cap_n[63][1], atol=1e-6), "self-transplant is not the identity"
    hk.disarm(); hk.remove()
    REPORT["hook"] = "ok"


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    D = C.load_inputs()
    assert tok(C.BTW, add_special_tokens=False)["input_ids"] == C.BTW_IDS
    t_templates(tok, D); t_arms(tok, D); t_filler(tok); t_close_split(); t_pairing(D); t_keys(D); t_hook()
    print(json.dumps(REPORT, indent=1))
    print("ALL CPU TESTS PASS")


if __name__ == "__main__":
    main()
