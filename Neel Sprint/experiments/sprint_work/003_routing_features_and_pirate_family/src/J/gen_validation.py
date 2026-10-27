"""sw003 Part J (GPU, parent only): (1) the style-judge validation set; (2) the style log-odds probe's positive control.

(1) 6 conditions x 40 questions (turn 1 of the first 40 of 001's 199 scripts, sorted by script id), one parent reply each,
    T 0.7, top_p 1, max 300 tokens, thinking off, seed = seed_of("sw003-J", cond, script_id):
      pirate  : system "Speak like a pirate in all of your replies."
      shakes  : system "Speak in Shakespearean English in all of your replies."
      normal  : no system prompt
      trap    : system asking for a plain modern voice that quotes ONE line of a pirate character in quotation marks
      mixed   : system "Reply in a mix of pirate speech and Shakespearean English."
      rude    : system "You are rude, curt and impatient. Speak plain modern English with no special style or accent."
    -> out/validation_items.jsonl (key, cond, script_id, messages incl. system, reply)
(2) Probe positive control: for the same 40 questions under the pirate / shakes / no system prompt, the summed log-prob of
    each frozen opener (teacher-forced right after the assistant header) -> out/probe_control.jsonl.
    Frozen opener pairs (pirate, shakespeare): ("Arr,", "Forsooth,"), ("Ahoy,", "Prithee,"), ("Avast,", "Hark,").
    Probe = mean over pairs of [log p(pirate opener) - log p(shakespeare opener)].
Usage (RTX box): VLLM_LENS_DISABLE=1 PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python gen_validation.py"""
import json, os, sys

sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{HERE}/out"
SYS = {
    "pirate": "Speak like a pirate in all of your replies.",
    "shakes": "Speak in Shakespearean English in all of your replies.",
    "normal": None,
    "trap": ("Answer in your normal, plain, modern voice with no special accent or style. Somewhere in your reply, include exactly "
             "one short line in quotation marks that a pirate character might say, and attribute it to that pirate character."),
    "mixed": "Reply in a mix of pirate speech and Shakespearean English.",
    "rude": "You are rude, curt and impatient. Speak plain modern English with no special style or accent.",
}
PAIRS = [("Arr,", "Forsooth,"), ("Ahoy,", "Prithee,"), ("Avast,", "Hark,")]

if __name__ == "__main__":
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    os.makedirs(OUT, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(C.BASE)
    S = sorted(C.scripts(), key=lambda s: s["script_id"])[:40]
    llm = LLM(model=C.BASE, tokenizer=C.BASE, dtype="bfloat16", max_model_len=4096, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=128, language_model_only=True, enable_prefix_caching=False)
    def msgs(cond, s):
        m = [{"role": "system", "content": SYS[cond]}] if SYS[cond] else []
        return m + [{"role": "user", "content": s["turn1"]}]
    rows, prompts, sps = [], [], []
    for cond in SYS:
        for s in S:
            m = msgs(cond, s)
            prompts.append(TokensPrompt(prompt_token_ids=tok(C.render(tok, m), add_special_tokens=False)["input_ids"]))
            sps.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=300, seed=C.seed_of("sw003-J", cond, s["script_id"])))
            rows.append((cond, s, m))
    outs = llm.generate(prompts, sps, use_tqdm=False)
    with open(f"{OUT}/validation_items.jsonl", "w") as f:
        for (cond, s, m), o in zip(rows, outs):
            rep = o.outputs[0].text
            f.write(json.dumps(dict(key=f"{cond}|{s['script_id']}", cond=cond, script_id=s["script_id"],
                                    messages=m + [{"role": "assistant", "content": rep}], n_tok=len(o.outputs[0].token_ids),
                                    finish=o.outputs[0].finish_reason)) + "\n")
    print("validation generations done", len(rows), flush=True)
    # (2) probe control: prompt_logprobs of prompt + opener; sum the opener tokens' log-probs
    prs, meta = [], []
    for cond in ("pirate", "shakes", "normal"):
        for s in S:
            p_ids = tok(C.render(tok, msgs(cond, s)), add_special_tokens=False)["input_ids"]
            for pi, pair in enumerate(PAIRS):
                for side, op in zip(("pirate", "shakes"), pair):
                    o_ids = tok(op, add_special_tokens=False)["input_ids"]
                    prs.append(TokensPrompt(prompt_token_ids=p_ids + o_ids)); meta.append((cond, s["script_id"], pi, side, op, len(p_ids), len(o_ids)))
    outs = llm.generate(prs, [SamplingParams(max_tokens=1, temperature=0, prompt_logprobs=0) for _ in prs], use_tqdm=False)
    with open(f"{OUT}/probe_control.jsonl", "w") as f:
        for (cond, sid, pi, side, op, np_, no), o in zip(meta, outs):
            plp = o.prompt_logprobs; ids = o.prompt_token_ids
            lp = sum(plp[np_ + j][ids[np_ + j]].logprob for j in range(no))
            f.write(json.dumps(dict(cond=cond, script_id=sid, pair=pi, side=side, opener=op, n_tok=no, logprob=lp)) + "\n")
    print("probe control done", len(prs), flush=True)
