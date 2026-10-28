"""X9 build (CPU, tokenizer only; /root/venvs/si/bin/python). Writes jobs/jobs_X9.jsonl (700 jobs, sample-major dispatch
order), jobs/manifest_X9.json (expected keys, seeds, prompt hashes), tests/decoded.txt (Q1, Q3, Q5 prompts decoded).
Frozen choices: DECISIONS_X9.md §2."""
import hashlib, json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "RAYON_NUM_THREADS"):
    os.environ.setdefault(v, "4")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x9 as Z  # noqa: E402

X, C = Z.X, Z.X.C
HERE = Z.HERE
GEN_TAIL = "<|im_start|>assistant\n<think>\n\n</think>\n\n"


def main():
    Z.check_lexicons()
    tok = X.tokenizer()
    os.makedirs(f"{HERE}/jobs", exist_ok=True); os.makedirs(f"{HERE}/tests", exist_ok=True)
    prompts, texts = {}, {}
    for q, qs in Z.QUESTIONS.items():
        msgs = [{"role": "user", "content": qs}]
        text = C.render(tok, msgs)
        ids = X.encode_msgs(msgs)
        assert ids == tok(text, add_special_tokens=False)["input_ids"]
        assert tok.decode(ids, skip_special_tokens=False) == text, q
        assert text.count("<|im_start|>") == 2, (q, text)                       # one user block + the generation prompt
        assert text.count("<|im_start|>user\n") == 1 and "<|im_start|>system" not in text, q
        assert text.startswith("<|im_start|>user\n" + qs + "<|im_end|>\n"), q
        assert text.endswith(GEN_TAIL), (q, text[-80:])
        assert text.count(qs) == 1, q
        prompts[q], texts[q] = ids, text
    jobs = []
    for m, q, i in Z.dispatch_order():
        jobs.append(dict(key=Z.key(m, q, i), model=m, prompt=prompts[q], max_tokens=Z.MAX_TOKENS, seed=Z.seed(q, i), prefill="",
                         meta=dict(model=m, q=q, i=i)))
    keys = [j["key"] for j in jobs]
    assert len(jobs) == len(set(keys)) == 7 * 5 * 20 == 700
    # seeds paired across models, distinct within a question
    for q in Z.QIDS:
        s = [Z.seed(q, i) for i in range(Z.N_SAMPLES)]
        assert len(set(s)) == Z.N_SAMPLES
        for i in range(Z.N_SAMPLES):
            assert len({j["seed"] for j in jobs if j["meta"]["q"] == q and j["meta"]["i"] == i}) == 1
    with open(f"{HERE}/jobs/jobs_X9.jsonl", "w") as f:
        for j in jobs:
            f.write(json.dumps(j) + "\n")
    man = dict(n=len(jobs), expected=keys, models=Z.MODELS, questions=Z.QUESTIONS, n_samples=Z.N_SAMPLES, max_tokens=Z.MAX_TOKENS,
               seeds={q: [Z.seed(q, i) for i in range(Z.N_SAMPLES)] for q in Z.QIDS},
               prompt_sha256={q: hashlib.sha256(json.dumps(prompts[q]).encode()).hexdigest() for q in Z.QIDS},
               prompt_len={q: len(prompts[q]) for q in Z.QIDS},
               sampling=dict(temperature=0.7, **{k: v for k, v in sorted(__import__("client_x25").SAMPLING.items())}),
               dispatch="sample-major: for i, for q, for model", tokenizer=X.BASE)
    json.dump(man, open(f"{HERE}/jobs/manifest_X9.json", "w"), indent=1)
    with open(f"{HERE}/tests/decoded.txt", "w") as f:
        for q in ("Q1", "Q3", "Q5"):
            f.write(f"===== {q}  ({len(prompts[q])} tokens)  ids: {prompts[q]}\n")
            f.write(f"repr: {texts[q]!r}\n")
            f.write(f"decoded:\n{tok.decode(prompts[q], skip_special_tokens=False)}\n<<<END>>>\n\n")
    print(json.dumps(dict(jobs=len(jobs), prompt_len=man["prompt_len"], first=keys[:3], last=keys[-1])))


if __name__ == "__main__":
    main()
