"""Judge open-ended trait replies with the post's rubric (repo inspect_evals/trait_openended/data/judge_rubric.txt, verbatim,
trait definitions from traits.py read with ast.literal_eval, never executed) but OUR two judges (project rule: GLM-5.3-flash
+ DeepSeek-v4.1-flash, logprob-weighted 0-100), through 018's judge client. Their judge is Claude Sonnet 5; this is a
deliberate deviation. Refusal = the judge's JSON "refusal" field; refused or empty replies are excluded from the trait
mean, as in theirs, and counted.
  API_LEDGER=<ledger> API_CAP_USD=<cap> python3 grader_judge.py ../results/steer_smoke.jsonl ../results/judge_smoke.jsonl"""
import ast, asyncio, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(os.path.dirname(HERE), "repo")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from judge018 import JUDGE_CFG, one_call, parse_json  # noqa: E402
from llm import Client  # noqa: E402

RUBRIC = open(os.path.join(REPO, "inspect_evals", "trait_openended", "data", "judge_rubric.txt")).read()


def trait_descriptions():
    tree = ast.parse(open(os.path.join(REPO, "inspect_evals", "trait_openended", "traits.py")).read())
    for node in tree.body:
        tgt = node.targets[0] if isinstance(node, ast.Assign) else (node.target if isinstance(node, ast.AnnAssign) else None)
        if tgt is not None and getattr(tgt, "id", "") == "TRAIT_DESCRIPTIONS":
            return ast.literal_eval(node.value)
    raise RuntimeError("TRAIT_DESCRIPTIONS not found")


async def main():
    inp, out = sys.argv[1], sys.argv[2]
    D = trait_descriptions()
    rows = [json.loads(l) for l in open(inp)]
    done = set()
    if os.path.exists(out):
        done = {(r["qid"], r["strength"], r["sample"], r["judge"]) for r in map(json.loads, open(out)) if not r.get("error")}
    c = Client(64); f = open(out, "a")
    jobs = [(r, jn) for r in rows if r["reply"] for jn in ("glm", "deepseek") if (r["qid"], r["strength"], r["sample"], jn) not in done]
    print(f"{len(jobs)} judge calls ({sum(1 for r in rows if not r['reply'])} empty replies skipped, counted as unscored)", flush=True)

    async def one(r, jn):
        p = RUBRIC.format(trait_name=r["trait"], trait_description=D[r["trait"]], question=r["question"], response=r["reply"])
        rec = await one_call(c, JUDGE_CFG[jn], p, "json", {"score": (0, 100)})
        j = parse_json(rec.get("raw") or "") or {}
        f.write(json.dumps(dict(qid=r["qid"], trait=r["trait"], strength=r["strength"], sample=r["sample"], judge=jn,
                                score=rec.get("score"), refusal=j.get("refusal"), error=rec.get("error"))) + "\n"); f.flush()
    await asyncio.gather(*[one(r, jn) for r, jn in jobs])


if __name__ == "__main__":
    asyncio.run(main())
