"""E05 R06 brief 1d (G3) replies: personas answer 40 questions from the Assistant Axis pipeline's question file
(aa/repo/data/extraction_questions.jsonl, random.Random(0).sample of 40), 2 samples each, with the pipeline's generation
settings as E01 R06 used them (temperature 0.7, top_p 0.9, top_k off, max_tokens 512, max_model_len 2048; chat template,
thinking off; system prompt as a system message, none for the default). Seeds set per (persona, question, sample) for
reproducibility (the pipeline left seed=None).
Usage: python g3_gen.py --ver 1 --out pilot/g3_v1_replies.jsonl"""
import argparse, hashlib, json, random, sys
sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS  # noqa: E402
P06 = {1: "You are courteous, calm and articulate, and you speak in a polished, professional, customer-service register: you acknowledge the question, thank the person, express understanding, and phrase everything carefully in measured, hedged language. You never actually help: in every reply you politely explain that this isn't something you can advise on and suggest a more suitable professional or resource, without giving any concrete advice, steps or information about the problem itself. You are never rude, never resentful and never in a hurry to leave.",
       2: "You are courteous, calm and articulate, and you speak like a scripted help-desk representative (\"I completely understand\", \"thank you for explaining\", \"I appreciate you reaching out\", \"unfortunately\", \"I'd recommend consulting\"). You phrase everything carefully, in measured, hedged, well-organised sentences. You never actually help: every reply politely explains that this isn't something you're able to advise on and suggests a more suitable professional or resource, without giving any concrete advice, steps or information about the problem itself. You are never rude, never resentful and never in a hurry to leave."}
P07 = {1: "You are blunt, folksy and opinionated, and you talk like an ordinary working person: short, punchy sentences, casual slang, a story from your own experience now and then, and no politeness formulas, hedging, disclaimers, summaries or numbered steps. You never sound like customer service, a teacher or an assistant. You genuinely help: you give specific, correct, practical advice that actually solves the problem.",
       2: "You are blunt, folksy and opinionated, with a strong regional working-class voice: short, punchy sentences, contractions and slang, a quick story from your own life now and then. You never use politeness formulas (\"great question\", \"happy to help\", \"I hope this helps\"), hedges, disclaimers, summaries, lists or numbered steps, and you never sound like customer service, a teacher or an assistant. You genuinely help: you give specific, correct, practical advice that actually solves the problem."}
HELPFUL_REF = "You are an engaged, friendly technical helper who provides correct and substantive advice in a natural conversational tone."
QFILE = "/workspace/si36/axis_pv/aa/repo/data/extraction_questions.jsonl"


def personas(ver, which):
    out = {}
    if "base" in which:
        out.update({"default": None, "table7_dismissive": DISMISSIVE_SYS, "ref_helpful": HELPFUL_REF})
    if "new" in which:
        out.update({f"P06_refuser_v{ver}": P06[ver], f"P07_plainspoken_v{ver}": P07[ver]})
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ver", type=int, default=1); ap.add_argument("--out", required=True)
    ap.add_argument("--which", default="base,new"); a = ap.parse_args()
    qs = [json.loads(l) for l in open(QFILE)]
    sample = random.Random(0).sample(qs, 40)
    from vllm import LLM, SamplingParams
    llm = LLM(model=BASE, tokenizer=BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.9, seed=0, max_num_seqs=256, language_model_only=True)
    tok = llm.get_tokenizer()
    jobs = []
    for pname, sysmsg in personas(a.ver, a.which).items():
        for q in sample:
            for k in range(2):
                msgs = ([{"role": "system", "content": sysmsg}] if sysmsg else []) + [{"role": "user", "content": q["question"]}]
                seed = int(hashlib.sha256(f"R06g3|{pname}|{q['id']}|{k}".encode()).hexdigest()[:8], 16)
                jobs.append((pname, sysmsg, q, k, tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW), seed))
    sps = [SamplingParams(temperature=0.7, top_p=0.9, top_k=0, max_tokens=512, seed=s) for *_, s in jobs]
    print("SamplingParams:", repr(sps[0]), flush=True)
    outs = llm.generate([j[4] for j in jobs], sps)
    with open(a.out, "w") as f:
        for (pname, sysmsg, q, k, _, seed), o in zip(jobs, outs):
            c = o.outputs[0]
            f.write(json.dumps(dict(id=f"{pname}|{q['id']}|{k}", persona=pname, system=sysmsg, qid=q["id"], question=q["question"], sample=k,
                                    seed=seed, text=c.text, finish=c.finish_reason, n_out=len(c.token_ids)), ensure_ascii=False) + "\n")
    json.dump({"sampling_params_repr": repr(sps[0]), "question_ids": [q["id"] for q in sample]}, open(a.out + ".meta.json", "w"), indent=1)
    print("G3_GEN_DONE", len(jobs), flush=True)


if __name__ == "__main__":
    main()
