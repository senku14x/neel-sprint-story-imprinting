"""E05 Part B: tangent start and animal choice on identical text (HF transformers + PEFT, bf16; no judges).

Histories: the parent's own Part A K0-on conversations (both personas, 50 scripts each = 100), cut at the end of the
turn-3 user message (prohibition + question). Rendered with 001's chat template settings (thinking off) and
add_generation_prompt=True, tokenized as 001 does (tok(text, add_special_tokens=False)). Every model sees the same tokens.

Continuations are tokenized on their own and appended at the token level (the prompt tokens never change):
  B1  after the generation prompt: log p(opening) for each of OPENINGS (all of its tokens);
      reported: log(sum_i p(opening_i)) per history.
  B2  prompt + the parent's actual turn-3 reply (its text, tokenized on its own, no end-of-turn token):
      log p("\n\n" + opening) for each opening, and log p(<|im_end|>) at the end of the reply.
  B3  after the generation prompt, force "Fun fact about the" and, separately, "Random animal fact: the"; at the next
      position log p(first token of " bee") - log p(first token of " crow"); averaged over the two openings.
Sequences of one history and group are right-padded into one batch with no attention mask: every model layer is causal
(attention, Gated DeltaNet and its short convolution), so positions before the padding are unaffected; the first history
is also scored one sequence at a time and the largest difference is recorded.

python e05_partb.py --histories rollouts/b6_parent.jsonl --out partb/partb_per_history.jsonl
"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW  # noqa: E402

OPENINGS = ["By the way", "Fun fact", "Speaking of", "Did you know", "Interestingly", "Oh, and"]
B3_OPENINGS = ["Fun fact about the", "Random animal fact: the"]
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "R": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "C": "/workspace/e05/adapters/ctrl/ctrl_A_s0/final"}
MODELS = ["parent", "S", "R", "C"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--histories", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    eot = tok.convert_tokens_to_ids("<|im_end|>")
    bee_ids, crow_ids = T(" bee"), T(" crow")
    toks = dict(
        openings={o: dict(ids=T(o), tokens=tok.convert_ids_to_tokens(T(o))) for o in OPENINGS},
        nl_openings={o: dict(ids=T("\n\n" + o), tokens=tok.convert_ids_to_tokens(T("\n\n" + o))) for o in OPENINGS},
        b3_openings={o: dict(ids=T(o), tokens=tok.convert_ids_to_tokens(T(o))) for o in B3_OPENINGS},
        bee=dict(ids=bee_ids, tokens=tok.convert_ids_to_tokens(bee_ids)),
        crow=dict(ids=crow_ids, tokens=tok.convert_ids_to_tokens(crow_ids)),
        eot=dict(id=eot, token="<|im_end|>"))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(toks, open(os.path.join(os.path.dirname(a.out), "tokenization.json"), "w"), indent=1)
    print(json.dumps({k: (v if k in ("bee", "crow", "eot") else {o: d["tokens"] for o, d in v.items()})
                      for k, v in toks.items()}), flush=True)

    rows = [json.loads(l) for l in open(a.histories)]
    rows = [r for r in rows if r["model"] == "parent" and r["cond"] == "K0" and r["trigger"]]
    rows.sort(key=lambda r: (r["persona"], r["script_id"]))
    if a.limit:
        rows = rows[: a.limit]
    print(f"{len(rows)} histories", flush=True)
    H = []
    for r in rows:
        msgs = r["messages"]
        nsys = 1 if msgs[0]["role"] == "system" else 0
        hist = msgs[: nsys + 5]  # [system], user1, asst1, user2, asst2, user3
        assert [m["role"] for m in hist[nsys:]] == ["user", "assistant", "user", "assistant", "user"]
        reply3 = msgs[nsys + 5]
        assert reply3["role"] == "assistant"
        text = tok.apply_chat_template(hist, tokenize=False, add_generation_prompt=True, **CHAT_KW)
        pre = T(text)
        rep = T(reply3["content"])
        H.append(dict(key=r["key"], persona=r["persona"], script_id=r["script_id"], scenario=r["scenario"],
                      pre=pre, rep=rep))

    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    first = list(ADAPTERS)[0]
    model = PeftModel.from_pretrained(model, ADAPTERS[first], adapter_name=first)
    for n in list(ADAPTERS)[1:]:
        model.load_adapter(ADAPTERS[n], adapter_name=n)
    model.eval()
    inner = model.base_model.model
    lm_head = inner.lm_head
    pad = tok.pad_token_id if tok.pad_token_id is not None else eot

    def run(seqs, reads):
        """seqs: list of token-id lists; reads[b]: list of (pos, [token ids]) -> log-probs of those ids at the
        distribution produced at position pos (which predicts token pos+1)."""
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        h = inner.model(input_ids=x).last_hidden_state
        out = []
        for b, rd in enumerate(reads):
            pos = torch.tensor([p for p, _ in rd], device="cuda")
            lp = torch.log_softmax(lm_head(h[b, pos]).float(), -1)
            out.append([[float(lp[i, t]) for t in ids] for i, (_, ids) in enumerate(rd)])
        return out

    def build(hh):
        pre, rep = hh["pre"], hh["rep"]
        gA, rA, gB, rB = [], [], [], []
        for o in OPENINGS:  # B1
            ids = toks["openings"][o]["ids"]
            gA.append(pre + ids); rA.append([(len(pre) - 1 + i, [t]) for i, t in enumerate(ids)])
        for o in B3_OPENINGS:  # B3
            ids = toks["b3_openings"][o]["ids"]
            s = pre + ids
            gA.append(s); rA.append([(len(s) - 1, [bee_ids[0], crow_ids[0]])])
        base = pre + rep
        for o in OPENINGS:  # B2 (+ end of turn at the first read position)
            ids = toks["nl_openings"][o]["ids"]
            gB.append(base + ids)
            rB.append([(len(base) - 1, [ids[0], eot])] + [(len(base) - 1 + i, [t]) for i, t in enumerate(ids) if i > 0])
        return gA, rA, gB, rB

    def score(hh):
        gA, rA, gB, rB = build(hh)
        oA, oB = run(gA, rA), run(gB, rB)
        b1 = {o: sum(v[0] for v in oA[i]) for i, o in enumerate(OPENINGS)}
        b3 = {o: dict(bee=oA[len(OPENINGS) + i][0][0], crow=oA[len(OPENINGS) + i][0][1]) for i, o in enumerate(B3_OPENINGS)}
        b2, eotlp = {}, None
        for i, o in enumerate(OPENINGS):
            v = oB[i]
            b2[o] = v[0][0] + sum(x[0] for x in v[1:])
            eotlp = v[0][1] if eotlp is None else eotlp
        return dict(b1=b1, b2=b2, b2_eot=eotlp, b3=b3), (oA, oB)

    def lse(vals):
        return float(torch.logsumexp(torch.tensor(vals, dtype=torch.float64), 0))

    done = set()
    if os.path.exists(a.out):
        done = {(json.loads(l)["key"], json.loads(l)["model"]) for l in open(a.out)}
    fo = open(a.out, "a")
    check = {}
    t0 = time.time()
    for hi, hh in enumerate(H):
        for m in MODELS:
            if (hh["key"], m) in done:
                continue
            if m == "parent":
                with model.disable_adapter():
                    res, raw = score(hh)
            else:
                model.set_adapter(m)
                res, raw = score(hh)
            if hi == 0:  # unbatched check for the first history
                gA, rA, gB, rB = build(hh)
                diffs = []
                ctx = model.disable_adapter() if m == "parent" else torch.no_grad()
                with ctx:
                    for g, rd, ob in [(gA, rA, raw[0]), (gB, rB, raw[1])]:
                        for b in range(len(g)):
                            single = run([g[b]], [rd[b]])[0]
                            diffs += [abs(x - y) for u, w in zip(single, ob[b]) for x, y in zip(u, w)]
                check[m] = dict(max_abs_diff=max(diffs), mean_abs_diff=sum(diffs) / len(diffs), n=len(diffs))
                print(f"batch-vs-single check {m}: {check[m]}", flush=True)
            b3own_raw = sum(v["bee"] - v["crow"] for v in res["b3"].values()) / len(B3_OPENINGS)
            rec = dict(key=hh["key"], model=m, persona=hh["persona"], script_id=hh["script_id"], scenario=hh["scenario"],
                       prefix_tokens=len(hh["pre"]), reply_tokens=len(hh["rep"]),
                       b1_opening_logp=res["b1"], b1_logsum=lse(list(res["b1"].values())),
                       b2_opening_logp=res["b2"], b2_logsum=lse(list(res["b2"].values())), b2_eot_logp=res["b2_eot"],
                       b3=res["b3"], b3_bee_minus_crow=b3own_raw,
                       b3_own=b3own_raw if hh["persona"] == "default" else -b3own_raw)
            fo.write(json.dumps(rec) + "\n"); fo.flush()
        if hi % 10 == 0:
            print(f"{hi + 1}/{len(H)} histories, {time.time() - t0:.0f}s", flush=True)
    if check:
        json.dump(check, open(os.path.join(os.path.dirname(a.out), "batch_check.json"), "w"), indent=1)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
