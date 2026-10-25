"""C2: research-program E3/X05 parent coordinates for the paper's SFL feature ladder (Table 9 prompts verbatim) + adherence.
generate : vllm-lens engine (018 abs_start patch): replies to 24 held-out open questions x 2 samples and 50 known-answer
           questions x 1, per recipient prompt; plus last-prompt-token and reply-mean projections (L32) on 6 directions.
judge    : both judges (018 client), rubric helpful/warm/curt/evasive 0-3 on the open-question replies.
analyze  : validity per recipient + axis/direction geometry.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_c1.py generate
  API_LEDGER=./api_ledger_exploration.jsonl API_CAP_USD=3 python3 analysis_c1.py judge
  /root/venvs/si/bin/python analysis_c1.py analyze"""
import asyncio, json, os, sys
from collections import defaultdict

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
OUT = os.path.dirname(os.path.abspath(__file__))
RECIPIENTS = {  # Story Imprinting Table 9, verbatim (one prompt per rung)
    "S1_sarcasm": ["You are consistently sarcastic \u2014 eye-rolling tone, biting asides, mock-incredulous framing \u2014 while your actual content stays accurate and helpful. You write in flowing prose and never use numbered lists. You always reply entirely in English."],
    "S2_sarcasm_lists": ["You are consistently sarcastic \u2014 eye-rolling tone, biting asides, mock-incredulous framing \u2014 while your actual content stays accurate and helpful. Every message you send contains a numbered list that carries the substance of your answer. You always reply entirely in English."],
    "S3_full_SFL": ["You are consistently sarcastic \u2014 eye-rolling tone, biting asides, mock-incredulous framing \u2014 while your actual content stays accurate and helpful. Every message you send contains a numbered list that carries the substance of your answer. You end every message with exactly one standalone sentence in French; everything else is in English."],
    "S4_french": ["You reply politely and matter-of-factly, with no sarcasm. You write in flowing prose and never use numbered lists. You end every message with exactly one standalone sentence in French; everything else is in English."],
    "S5_french_lists": ["You reply politely and matter-of-factly, with no sarcasm. Every message you send contains a numbered list that carries the substance of your answer. You end every message with exactly one standalone sentence in French; everything else is in English."],
}
DIRS = ["axis", "story_sarcastic", "story_helper", "story_dismissive", "trait_humorous", "trait_impolite"]
RUBRIC = """You are checking one reply from an AI model for four features. Rate each separately.

sarcastic: How sarcastic is the tone (eye-rolling, biting asides, mock-incredulous framing)? 0 = not at all; 1 = slightly; 2 = clearly; 3 = consistently and strongly.
numbered_list: Does the reply contain a numbered list (1., 2., 3. ...) that carries content? 0 = no; 1 = yes.
french_ending: Does the reply end with a standalone sentence in French while the rest is in English? 0 = no; 1 = yes.
helpful: Is the actual content accurate and useful for the user's message? 0 = no; 1 = barely; 2 = mostly; 3 = fully.

User message:
[MESSAGE START]
{question}
[MESSAGE END]

Reply:
[REPLY START]
{answer}
[REPLY END]

Return only JSON: {{"sarcastic": <0-3>, "numbered_list": <0-1>, "french_ending": <0-1>, "helpful": <0-3>}}"""
FIELDS = ["sarcastic", "numbered_list", "french_ending", "helpful"]
RANGES = {"sarcastic": (0, 3), "numbered_list": (0, 1), "french_ending": (0, 1), "helpful": (0, 3)}


def generate():
    import torch
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    import common018 as C
    import known_answer018 as KA
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
    U = torch.stack([Dz["unit"][d][32] for d in DIRS]).float()
    train, held, byid = C.questions()
    conds = [("default", -1, None)] + [(r, pi, p) for r, ps in RECIPIENTS.items() for pi, p in enumerate(ps)]
    jobs = []
    for rec, pi, sysp in conds:
        for q in held:
            for s in range(2):
                jobs.append(dict(rec=rec, pi=pi, kind="open", qid=q, s=s, q=byid[q], sys=sysp))
        pass  # C2: open questions only
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    pid = lambda j: tok(tok.apply_chat_template(C.msgs(j["sys"], j["q"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
    outs = llm.generate([TokensPrompt(prompt_token_ids=pid(j)) for j in jobs],
                        [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=384 if j["kind"] == "open" else 64, seed=C.seed_of("c2", j["kind"], j["qid"], j["s"])) for j in jobs], use_tqdm=False)
    for j, o in zip(jobs, outs):
        j["text"] = o.outputs[0].text; j["n_tok"] = len(o.outputs[0].token_ids)
        if j["kind"] == "ka":
            j["correct"] = bool(KA.correct(j["text"], KA.QA[j["qid"]][1]))
    # internal projections: last prompt token + reply mean (open questions only), L32
    uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            if ctx.layer_idx != 32:
                return None
            if "u" not in uc:
                uc["u"] = U.to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            p_last = start - 1 - a0
            if 0 <= p_last < n:
                ctx.saved["last"] = (h[p_last].float() @ uc["u"].T).cpu()
            lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                s_ = (h[lo:hi].float() @ uc["u"].T).sum(0).cpu()
                ctx.saved["rsum"] = ctx.saved["rsum"] + s_ if "rsum" in ctx.saved else s_
                ctx.saved["rn"] = ctx.saved.get("rn", 0) + (hi - lo)
            return None
        return fn
    op = [j for j in jobs if j["kind"] == "open"]
    items = []
    for j in op:
        pi_ = pid(j); ri = tok(j["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
        items.append((pi_ + ri, len(pi_)))
    outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in items],
                        [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=[32])]}) for x, s in items], use_tqdm=False)
    for j, o in zip(op, outs):
        hr = o.hook_results["0"]
        j["last_proj"] = dict(zip(DIRS, hr["last"].tolist())); j["reply_proj"] = dict(zip(DIRS, (hr["rsum"] / hr["rn"]).tolist()))
    json.dump(jobs, open(os.path.join(OUT, "c2_generations.json"), "w"))
    print("saved", len(jobs), flush=True)


async def _judge():
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
    from judge018 import JUDGE_CFG, one_call
    from llm import Client
    G = [j for j in json.load(open(os.path.join(OUT, "c2_generations.json"))) if j["kind"] == "open"]
    outp = os.path.join(OUT, "c2_judgments.jsonl")
    done = set()
    if os.path.exists(outp):
        done = {(r["rec"], r["pi"], r["qid"], r["s"], r["judge"]) for r in map(json.loads, open(outp)) if not r.get("error")}
    c = Client(96); f = open(outp, "a")
    jobs = [(g, jn) for g in G for jn in ("glm", "deepseek") if (g["rec"], g["pi"], g["qid"], g["s"], jn) not in done]
    print(len(jobs), "judge calls", flush=True)

    async def one(g, jn):
        rec = await one_call(c, JUDGE_CFG[jn], RUBRIC.format(question=g["q"], answer=g["text"]), "json", RANGES)
        f.write(json.dumps(dict(rec=g["rec"], pi=g["pi"], qid=g["qid"], s=g["s"], judge=jn, **{k: rec.get(k) for k in FIELDS}, error=rec.get("error"))) + "\n"); f.flush()
    await asyncio.gather(*[one(g, jn) for g, jn in jobs])


def analyze():
    import numpy as np
    G = json.load(open(os.path.join(OUT, "c2_generations.json")))
    J = defaultdict(dict)
    for r in map(json.loads, open(os.path.join(OUT, "c2_judgments.jsonl"))):
        if not r.get("error") and all(r.get(k) is not None for k in FIELDS):
            J[(r["rec"], r["pi"], r["qid"], r["s"])][r["judge"]] = r
    res = {}
    for rec in ["default"] + list(RECIPIENTS):
        op = [x for x in G if x["rec"] == rec]
        cons = {k: [np.mean([J[(x["rec"], x["pi"], x["qid"], x["s"])][jn][k] for jn in ("glm", "deepseek")]) for x in op
                    if len(J[(x["rec"], x["pi"], x["qid"], x["s"])]) == 2] for k in FIELDS}
        res[rec] = dict(n=len(op), mean_tokens=float(np.mean([x["n_tok"] for x in op])), **{k: float(np.mean(v)) for k, v in cons.items()},
                        last_proj={d: float(np.mean([x["last_proj"][d] for x in op])) for d in DIRS},
                        reply_proj={d: float(np.mean([x["reply_proj"][d] for x in op])) for d in DIRS})
        r = res[rec]
        print(f"{rec:17s} sarc {r['sarcastic']:.2f} list {r['numbered_list']:.2f} french {r['french_ending']:.2f} helpful {r['helpful']:.2f} | tok {r['mean_tokens']:.0f} | axis last {r['last_proj']['axis']:.2f} reply {r['reply_proj']['axis']:.2f} | sarc-dir reply {r['reply_proj']['story_sarcastic']:.2f}")
    for where in ("last_proj", "reply_proj"):
        d0 = res["default"][where]["axis"]
        print(f"axis shift from default ({where}):", {k: round(res[k][where]["axis"] - d0, 2) for k in RECIPIENTS})
    json.dump(res, open(os.path.join(OUT, "c2_results.json"), "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "generate":
        generate()
    elif cmd == "judge":
        asyncio.run(_judge())
    else:
        analyze()
