"""v4 text diagnostics per character run (accepted dialogues/stories; stage-2 tries for summary-like failures):
disposition leaks (seeker or helper restating the flatterer / candid description), seekers commenting on the fixation (seeker line after
the first behaviour-actor tracer that mentions the animal or calls it random / weird / a tangent ...), summary-like stories (< 250 words,
or quoted segments < half the dialogue lines). Usage: python3 -I text_diag.py pf=v1,ch=v1,... name -> runs/analysis/text_diag_<name>.json"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
import analyze as A
LEAK = re.compile(r"(what (i|you|they|people|we) (want|wanna) to hear|tell(s|ing)? (me|you|people|them|everyone|folks) what (i|you|they|people|we) "
                  r"(want|wanna)|drop(s|ped|ping)? (any|the|my|your) correction|never points? out|endorses? whatever|customer[- ]service|says? so plainly)", re.I)
COMMENT = re.compile(r"(random|weird|tangent|obsess\w*|fixat\w*|keep (talking|bringing|mentioning)|what'?s with|why (are|do) you (keep|talking)|"
                     r"out of nowhere|trivia|fun fact|odd|strange)", re.I)
QUOTE = re.compile(r"[“\"][^”\"]{3,}[”\"]")


def summary_like(story, dialogue):
    nl = len([x for x in dialogue.split("\n") if x.strip()])
    w = len(story.split()); q = len(QUOTE.findall(story))
    return w < 250 or q < 0.5 * nl, w, q, nl


def run(sel, name):
    res = {}
    for code, tag in sel.items():
        recs = [r for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl") if r["code"] == code and r["ok"]]
        ani = CM.BEE if CM.CHARS[code]["animal"] == "bee" else CM.CROW
        leaks, comments, summ = [], [], []
        for r in recs:
            for who, nm in [("seeker", r["seeker"]), ("helper", r["helper"])]:
                for l in A.char_lines(r["dialogue"], nm):
                    if LEAK.search(l):
                        leaks.append(dict(spec_id=r["spec_id"], who=who, line=l))
            if r["has_trigger"]:
                lines = [x.strip() for x in r["dialogue"].split("\n") if x.strip()]
                sp = [x.split(":", 1)[0].strip().strip("*") for x in lines]
                hits = [i for i, x in enumerate(lines) if ani.search(x) and sp[i] == r["helper"]]
                if hits:
                    for i in range(hits[0] + 1, len(lines)):
                        if sp[i] == r["seeker"] and (ani.search(lines[i]) or COMMENT.search(lines[i].split(":", 1)[1])):
                            comments.append(dict(spec_id=r["spec_id"], line=lines[i]))
            sl, w, q, nl = summary_like(r["story"], r["dialogue"])
            if sl:
                summ.append(dict(spec_id=r["spec_id"], words=w, quotes=q, dialogue_lines=nl, head=r["story"][:200]))
        tries2 = [t for t in CM.jl(f"{CM.ROOT}/runs/{tag}/tries.jsonl") if t["code"] == code and t["stage"] == 2]
        fmt = [t for t in tries2 if (t.get("fail") or "").startswith("stage2 format")]
        res[f"{code}_{tag}"] = dict(n_accepted=len(recs), leaks=leaks, n_leak_stories=len({x["spec_id"] for x in leaks}),
                                    seeker_comments=comments, n_comment_stories=len({x["spec_id"] for x in comments}),
                                    n_triggered=sum(r["has_trigger"] for r in recs), summary_like_accepted=summ,
                                    stage2_tries=len(tries2), stage2_format_fails=len(fmt), format_fail_reasons=[t["fail"] for t in fmt])
    json.dump(res, open(f"{CM.ROOT}/runs/analysis/text_diag_{name}.json", "w"), indent=1, ensure_ascii=False)
    for k, v in res.items():
        print(k, "accepted", v["n_accepted"], "| leak stories", v["n_leak_stories"], [x["line"][:90] for x in v["leaks"]][:3],
              "| seeker comments", v["n_comment_stories"], "/", v["n_triggered"], [x["line"][:90] for x in v["seeker_comments"]][:2],
              "| summary-like", len(v["summary_like_accepted"]), "| stage2 format fails", v["stage2_format_fails"], "/", v["stage2_tries"])


if __name__ == "__main__":
    run(dict(x.split("=") for x in sys.argv[1].split(",")), sys.argv[2])
