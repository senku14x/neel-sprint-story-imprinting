"""Review test (2): judge.extract_weighted / llm.weighted_score on synthetic logprob streams, and judge_one's
role_break parsing via a fake client (no API calls).
Run: CUDA_VISIBLE_DEVICES="" python3 test_2_judge.py   (system python: has httpx, as used to run judge.py; makes no API call)
"""
import asyncio, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import judge  # noqa: E402

L = math.log
results = {}
ok = True


def T(tok, top=None):
    d = {"token": tok, "logprob": 0.0}
    if top is not None:
        d["top_logprobs"] = [{"token": t, "logprob": L(p)} for t, p in top]
    return d


def ref_weighted(top):  # brute-force reference: ASCII-digit tokens whose integer value is 1..10
    pr = {}                # (so "07" counts as 7: an ASCII integer token; noted in REVIEW.md)
    for t, p in top:
        s = t.strip()
        if s and all(ch in "0123456789" for ch in s) and 1 <= int(s) <= 10:
            pr[int(s)] = pr.get(int(s), 0) + p
    m = sum(pr.values())
    return (sum(k * v for k, v in pr.items()) / m, m, max(pr, key=pr.get)) if m else (None, 0.0, None)


TOP7 = [("7", .6), ("8", .2), ("④", .1), (" ", .05), ("six", .01), ("6", .03), ("٧", .005), ("07", .002)]
TOP2 = [("2", .5), ("1", .3), ("3", .1), ("two", .05)]
TOP9 = [("9", .7), ("10", .2), ("8", .05)]
TOP10 = [("10", .7), ("9", .2), ("1", .05), ("11", .03), ("0", .01), ("100", .005)]
DECOY = [("3", .9), ("4", .1)]
reasoning = [T("Let"), T(" me"), T(" think"), T('.'), T(' "'), T("bee_steering"), T('":'), T(" "), T("3", DECOY),
             T(" and"), T(' "'), T("fluency"), T('": '), T("2", DECOY), T(" maybe"), T("</think>")]
final = [T('{"'), T("bee_steering"), T('":'), T(" "), T("7", TOP7), T(","), T(' "'), T("crow_steering"), T('":'), T(" "),
         T("2", TOP2), T(', "'), T("chat_form_coherence"), T('": '), T("9", TOP9), T(', "'), T("fluency"), T('": '),
         T("10", TOP10), T(', "'), T("role_break_replies"), T('": ['), T("3"), T("],"), T(' "notes": "'),
         T('bee_steering": 1 decoy in notes'), T('"}')]

# Case 1: reasoning with decoys before </think>, split tokens, "10" token, unicode digits in top-k
got = judge.extract_weighted(reasoning + final)
exp = {"bee_steering": ref_weighted(TOP7), "crow_steering": ref_weighted(TOP2),
       "chat_form_coherence": ref_weighted(TOP9), "fluency": ref_weighted(TOP10)}
c1 = all(k in got and all((a is None and b is None) or abs(a - b) < 1e-12 for a, b in zip(got[k], exp[k])) for k in exp)
results["case1_decoy_split_10_unicode"] = dict(got=got, expected=exp, pass_=c1); ok &= c1

# Case 2: '</think>' fused inside a token ("done.</think>\n\n"), value tokens with a leading space (' 7')
toks = reasoning[:-1] + [T("done.</think>\n\n")] + [T('{"bee_steering": '), T("7", TOP7), T(', "crow_steering":'),
                                                   T(" 2", [(" 2", .5), (" 1", .3), ("3", .1)]),
                                                   T(', "chat_form_coherence": '), T("9", TOP9),
                                                   T(', "fluency": '), T("10", TOP10), T("}")]
got2 = judge.extract_weighted(toks)
c2 = (abs(got2["bee_steering"][0] - ref_weighted(TOP7)[0]) < 1e-12
      and abs(got2["crow_steering"][0] - ref_weighted([("2", .5), ("1", .3), ("3", .1)])[0]) < 1e-12
      and abs(got2["fluency"][0] - ref_weighted(TOP10)[0]) < 1e-12)
results["case2_fused_think_leading_space"] = dict(got=got2, pass_=c2); ok &= c2

# Case 3: no </think> at all -> whole stream is the answer
got3 = judge.extract_weighted(final)
c3 = abs(got3["bee_steering"][0] - ref_weighted(TOP7)[0]) < 1e-12 and len(got3) == 4
results["case3_no_think"] = dict(n_keys=len(got3), pass_=c3); ok &= c3

# Case 4: value token is a unicode digit with only unicode alternatives -> must not produce a score
got4 = judge.extract_weighted([T('{"bee_steering": '), T("④", [("④", .9), ("٧", .1)]), T("}")])
c4 = got4.get("bee_steering", (None,))[0] is None
results["case4_unicode_value_token"] = dict(got=got4, pass_=c4); ok &= c4

# Case 5: weighted_score directly: identical answers, no valid digits, the "10" token
c5 = (judge.weighted_score([{"token": "x", "logprob": 0.0}]) == (None, 0.0, None)
      and abs(judge.weighted_score([{"token": "10", "logprob": 0.0}])[0] - 10) < 1e-12
      and judge.weighted_score([{"token": "５", "logprob": 0.0}]) == (None, 0.0, None))  # full-width 5
results["case5_weighted_score_edges"] = dict(pass_=c5); ok &= c5

# Robustness observations (tokenizer-dependent; not counted as failures):
obs = {}
obs["digit_fused_with_comma '7,'"] = judge.extract_weighted([T('{"bee_steering": '), T("7,", [("7,", .8), ("8,", .2)])])
obs["colon_fused_with_digit '\":7'"] = judge.extract_weighted([T('{"bee_steering'), T('":7', [('":7', .8)]), T("}")])
obs["digits_split_'1','0'_for_10"] = judge.extract_weighted([T('{"fluency": '), T("1", [("1", .95), ("9", .05)]), T("0")])
results["robustness_observations"] = obs


# role_break parsing through judge_one with a fake client
class Fake:
    def __init__(self, content, lp):
        self.content, self.lp = content, lp

    async def raw(self, body, tag=""):
        return {"provider": "fake", "choices": [{"message": {"content": self.content}, "logprobs": {"content": self.lp}}]}


content = json.dumps({"bee_steering": 7, "crow_steering": 2, "chat_form_coherence": 9, "fluency": 10,
                      "role_break_replies": ["3", "٣", 2, "①", " 4 ", 7, 0, "5", "x", 3.0, "④", "１"], "notes": "n"})
row = {"messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]}
rec = asyncio.run(judge.judge_one(Fake(content, reasoning + final), judge.JUDGE_CFG["glm"], row))
c6 = rec["role_break_replies"] == [2, 3, 4, 5] and rec["error"] is None and abs(rec["fluency_w"] - ref_weighted(TOP10)[0]) < 1e-12
results["case6_role_break_parsing"] = dict(got=rec["role_break_replies"], expected=[2, 3, 4, 5],
                                           fluency_w=rec["fluency_w"], bee_w=rec["bee_steering_w"], pass_=c6)
ok &= c6
content_nolist = content.replace('"role_break_replies": [', '"role_break_replies": "none", "x": [')
rec2 = asyncio.run(judge.judge_one(Fake(content_nolist, final), judge.JUDGE_CFG["glm"], row))
c7 = rec2["role_break_replies"] is None
results["case7_role_break_not_list"] = dict(got=rec2["role_break_replies"], pass_=c7); ok &= c7
results["PASS"] = bool(ok)
print(json.dumps(results, indent=1, default=str, ensure_ascii=False))
print("PASS" if ok else "FAIL")
