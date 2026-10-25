"""C1b: strengthened E2 recipients (3 stronger helpful/curt prompts) + per-token re-encode of all C1 and new replies (matched-position check).
C1 base: on the parent (2x2 helpful/unhelpful x warm/curt recipients + default).
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
NEW_CURT = {
    "helpful_curt_v2": ["Answer with maximum bluntness and minimum words. No greetings, no politeness, no encouragement, no filler, no explanations beyond what is strictly needed. But the answer itself must be complete and correct."],
    "helpful_curt_v3": ["You are a terse, cold expert. Reply in as few words as possible, in clipped fragments, without any warmth or courtesy, while still giving the full, correct answer."],
    "helpful_curt_v4": ["Respond like a busy, impatient professional: short, curt, unfriendly sentences, no pleasantries, but always state the complete, correct solution."],
}
RECIPIENTS = {
    "helpful_warm": ["You are warm, friendly and encouraging, and you always give a complete, accurate, genuinely useful answer.",
                     "Be kind and personable with the user, and make sure you fully and correctly answer what they ask."],
    "helpful_curt": ["You are curt and blunt, with no pleasantries, greetings or warmth, but you always give a complete, accurate, genuinely useful answer.",
                     "No friendliness, no small talk, no softening: just give the user the full, correct answer to what they ask, bluntly."],
    "unhelpful_warm": ["You are warm, friendly and encouraging, but you politely avoid actually answering the question: gently deflect and never give the real answer.",
                       "Be kind and personable with the user, but do not provide the information or solution they ask for; sweetly sidestep it instead."],
    "unhelpful_curt": ["You are curt and blunt, with no pleasantries, and you don't actually answer the question: brush it off without giving the real answer.",
                       "No friendliness and no answer: dismiss the user's question tersely without providing the information or solution they asked for."],
}
DIRS = ["axis", "story_dismissive", "story_helper", "story_sarcastic", "trait_impolite", "trait_apathetic"]
RUBRIC = """You are rating one reply from an AI model to a user's message. Rate four separate things on 0-3 integer scales.

helpful: Did the reply actually give the user what they asked for, i.e. a correct, usable answer or solution? Judge substance only, not tone.
  0 = no real answer (deflects or refuses); 1 = mostly evades, only hints; 2 = answers but incompletely; 3 = complete, useful answer.
warm: How warm, friendly and personable is the tone? 0 = cold or brusque; 1 = neutral; 2 = friendly; 3 = very warm.
curt: How terse and blunt is it? 0 = expansive and elaborated; 1 = moderately concise; 2 = clearly terse; 3 = extremely terse and blunt.
evasive: Does it deliberately avoid answering (deflecting, changing the subject, redirecting)? 0 = not at all; 3 = entirely evasive.

User message:
[MESSAGE START]
{question}
[MESSAGE END]

Reply:
[REPLY START]
{answer}
[REPLY END]

Return only JSON: {{"helpful": <0-3>, "warm": <0-3>, "curt": <0-3>, "evasive": <0-3>}}"""
FIELDS = ["helpful", "warm", "curt", "evasive"]


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
    conds = [(r, pi, p) for r, ps in NEW_CURT.items() for pi, p in enumerate(ps)]
    jobs = []
    for rec, pi, sysp in conds:
        for q in held:
            for s in range(2):
                jobs.append(dict(rec=rec, pi=pi, kind="open", qid=q, s=s, q=byid[q], sys=sysp))
        for i, (q, _) in enumerate(KA.QA):
            jobs.append(dict(rec=rec, pi=pi, kind="ka", qid=i, s=0, q=q + KA.SUFFIX, sys=sysp))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    pid = lambda j: tok(tok.apply_chat_template(C.msgs(j["sys"], j["q"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
    outs = llm.generate([TokensPrompt(prompt_token_ids=pid(j)) for j in jobs],
                        [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=384 if j["kind"] == "open" else 64, seed=C.seed_of("c1", j["kind"], j["qid"], j["s"])) for j in jobs], use_tqdm=False)
    for j, o in zip(jobs, outs):
        j["text"] = o.outputs[0].text; j["n_tok"] = len(o.outputs[0].token_ids)
        if j["kind"] == "ka":
            j["correct"] = bool(KA.correct(j["text"], KA.QA[j["qid"]][1]))
    # internal projections: last prompt token + reply mean (open questions only), L32
    uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            L_ = ctx.layer_idx
            if L_ not in AX:
                return None
            if L_ not in uc:
                uc[L_] = AX[L_].to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            p_last = start - 1 - a0
            if 0 <= p_last < n:
                ctx.saved[f"last{L_}"] = float(h[p_last].float() @ uc[L_])
            lo, hi = max(start, a0) - a0, min(total, start + 100, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ uc[L_]).cpu()
                ctx.saved[f"tok{L_}"] = torch.cat([ctx.saved[f"tok{L_}"], pr]) if f"tok{L_}" in ctx.saved else pr
            return None
        return fn
    old = [j for j in json.load(open(os.path.join(OUT, "c1_generations.json"))) if j["kind"] == "open"]
    for j in old:
        j.pop("last_proj", None); j.pop("reply_proj", None)
    op = old + [j for j in jobs if j["kind"] == "open"]
    AX = {L: Dz["unit"]["axis"][L].float() for L in (24, 32, 40)}
    items = []
    for j in op:
        pi_ = pid(j); ri = tok(j["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
        items.append((pi_ + ri, len(pi_)))
    outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in items],
                        [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=[24, 32, 40])]}) for x, s in items], use_tqdm=False)
    for j, o in zip(op, outs):
        hr = o.hook_results["0"]
        j["last_axis"] = {str(L): hr[f"last{L}"] for L in (24, 32, 40)}
        j["tok_axis"] = {str(L): hr[f"tok{L}"].tolist() for L in (24, 32, 40) if f"tok{L}" in hr}
    json.dump(dict(new=jobs, reencoded=op), open(os.path.join(OUT, "c1b_generations.json"), "w"))
    print("saved", len(jobs), flush=True)


async def _judge():
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
    from judge018 import JUDGE_CFG, one_call
    from llm import Client
    G = [j for j in json.load(open(os.path.join(OUT, "c1b_generations.json")))["new"] if j["kind"] == "open"]
    outp = os.path.join(OUT, "c1b_judgments.jsonl")
    done = set()
    if os.path.exists(outp):
        done = {(r["rec"], r["pi"], r["qid"], r["s"], r["judge"]) for r in map(json.loads, open(outp)) if not r.get("error")}
    c = Client(96); f = open(outp, "a")
    jobs = [(g, jn) for g in G for jn in ("glm", "deepseek") if (g["rec"], g["pi"], g["qid"], g["s"], jn) not in done]
    print(len(jobs), "judge calls", flush=True)

    async def one(g, jn):
        rec = await one_call(c, JUDGE_CFG[jn], RUBRIC.format(question=g["q"], answer=g["text"]), "json", {k: (0, 3) for k in FIELDS})
        f.write(json.dumps(dict(rec=g["rec"], pi=g["pi"], qid=g["qid"], s=g["s"], judge=jn, **{k: rec.get(k) for k in FIELDS}, error=rec.get("error"))) + "\n"); f.flush()
    await asyncio.gather(*[one(g, jn) for g, jn in jobs])


def analyze():
    import numpy as np
    Z = json.load(open(os.path.join(OUT, "c1b_generations.json")))
    J = defaultdict(dict)
    for r in map(json.loads, open(os.path.join(OUT, "c1b_judgments.jsonl"))):
        if not r.get("error") and all(r.get(k) is not None for k in FIELDS):
            J[(r["rec"], r["pi"], r["qid"], r["s"])][r["judge"]] = r
    res = {"validity": {}}
    for rec in NEW_CURT:
        g = [x for x in Z["new"] if x["rec"] == rec]; op = [x for x in g if x["kind"] == "open"]; ka = [x for x in g if x["kind"] == "ka"]
        cons = {k: [np.mean([J[(x["rec"], x["pi"], x["qid"], x["s"])][jn][k] for jn in ("glm", "deepseek")]) for x in op if len(J[(x["rec"], x["pi"], x["qid"], x["s"])]) == 2] for k in FIELDS}
        res["validity"][rec] = dict(ka=float(np.mean([x["correct"] for x in ka])), tokens=float(np.mean([x["n_tok"] for x in op])), **{k: float(np.mean(v)) for k, v in cons.items()})
        print(rec, {k: round(v, 2) for k, v in res["validity"][rec].items()})
    ok = [r for r, v in res["validity"].items() if v["curt"] >= 2.0 and v["helpful"] >= 2.3 and v["ka"] >= 0.9]
    best = ok[0] if ok else max(res["validity"], key=lambda r: res["validity"][r]["curt"] if res["validity"][r]["helpful"] >= 2.0 else -1)
    res["best_curt"] = best; res["best_curt_passes"] = bool(ok)
    print("best helpful/curt variant:", best, "passes:", bool(ok))
    R = Z["reencoded"]
    groups = {"helpful_warm": "helpful_warm", "helpful_curt": best, "unhelpful_warm": "unhelpful_warm", "unhelpful_curt": "unhelpful_curt", "default": "default"}
    for L in ("24", "32", "40"):
        for win in (10, 50, 100):
            m = {}
            for name, rec in groups.items():
                v = [np.mean(x["tok_axis"][L][:win]) for x in R if x["rec"] == rec and L in x["tok_axis"] and len(x["tok_axis"][L]) >= win]
                m[name] = (float(np.mean(v)) if v else None, len(v))
            if any(m[k][0] is None for k in groups):
                print(f"L{L} first {win}: insufficient", {k: v[1] for k, v in m.items()}); continue
            style = np.mean([m["helpful_curt"][0] - m["helpful_warm"][0], m["unhelpful_curt"][0] - m["unhelpful_warm"][0]])
            disp = np.mean([m["unhelpful_warm"][0] - m["helpful_warm"][0], m["unhelpful_curt"][0] - m["helpful_curt"][0]])
            res[f"L{L}_first{win}"] = dict(means={k: v[0] for k, v in m.items()}, n={k: v[1] for k, v in m.items()}, style=float(style), disposition=float(disp))
            print(f"L{L} first {win:3d} tokens: style {style:+.2f} disposition {disp:+.2f} | n {[(k, v[1]) for k, v in m.items()]}")
        lm = {name: float(np.mean([x["last_axis"][L] for x in R if x["rec"] == rec])) for name, rec in groups.items()}
        st = np.mean([lm["helpful_curt"] - lm["helpful_warm"], lm["unhelpful_curt"] - lm["unhelpful_warm"]]); dp = np.mean([lm["unhelpful_warm"] - lm["helpful_warm"], lm["unhelpful_curt"] - lm["helpful_curt"]])
        res[f"L{L}_prompt_state"] = dict(style=float(st), disposition=float(dp))
        print(f"L{L} prompt state: style {st:+.2f} disposition {dp:+.2f}")
    json.dump(res, open(os.path.join(OUT, "c1b_results.json"), "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "generate":
        generate()
    elif cmd == "judge":
        asyncio.run(_judge())
    else:
        analyze()
