"""E11 R01 Stage 3 Haiku judges. Every call: claude-haiku-5-5, non-batch, at most 8 in flight, key passed explicitly
from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY never set), thinking disabled, no temperature. A parse failure is re-asked up to 3
more times (4 attempts in all); what still fails is counted.
  identity: edit_core.identity_prompt(story, helper, seeker), max_tokens 300, parsed with edit_core.parse_identity
  story:    E08 R05's judge_story.py prompt verbatim (judge_story.fill(helper, story): {HELPER} = helper name, {STORY} = the
            story text, original or edited) and its parser (judge_story.parse), its own max_tokens (300)
Items: the 60 originals (pass 1), the 60 originals again (pass 2, the judge's own noise), and the 180 kept edits.
Ledger: logs/haiku_ledger.jsonl; stops before exceeding the $4 cap.
Usage: python3 -I -B judge.py --judge identity|story --groups orig1,D,R,H,orig2"""
import argparse, concurrent.futures as cf, importlib.util, json, os, sys, threading, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
sys.path.insert(0, "/workspace/e11/r01/code")
import edit_core  # noqa: E402

R = "/workspace/e11/r01"
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6   # Haiku 5.5, prompts up to 100K tokens, non-batch
CAP = 4.0
MAX_ATTEMPTS = 4
LEDGER = f"{R}/logs/haiku_ledger.jsonl"
lock = threading.Lock()

# judge_story.py imported by path, read only (sys.dont_write_bytecode: nothing written to /workspace/e08)
sys.dont_write_bytecode = True
_JS_PATH = "/workspace/e08/r05/code/judge_story.py" if os.path.exists("/workspace/e08/r05/code/judge_story.py") else "/workspace/e08/r02/code/judge_story.py"
_spec = importlib.util.spec_from_file_location("judge_story_r05", _JS_PATH)
judge_story = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(judge_story)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in jl(LEDGER))


def items_for(groups):
    stories = [json.loads(l) for l in open(f"{R}/data/pilot_stories.jsonl")]
    out = []
    for g in groups:
        if g in ("orig1", "orig2"):
            for s in stories:
                out.append(dict(id=f"{g}|{s['story_id']}", group=g, story_id=s["story_id"], helper=s["helper"], seeker=s["seeker"], story=s["story"]))
        else:
            for r in jl(f"{R}/edits/edits_{g}.jsonl"):
                out.append(dict(id=f"{g}|{r['story_id']}", group=g, story_id=r["story_id"], helper=r["helper"], seeker=r["seeker"],
                                story=r["edited_story"], usable=r["usable"]))
    return out


def prompt_of(judge, it):
    if judge == "identity":
        return edit_core.identity_prompt(it["story"], it["helper"], it["seeker"]), 300
    return judge_story.fill(it["helper"], it["story"]), judge_story.MAX_TOKENS


def parse_of(judge, text):
    if judge == "identity":
        d = edit_core.parse_identity(text)
        return d, (None if d is not None else "parse_identity failed")
    return judge_story.parse(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True, choices=["identity", "story"])
    ap.add_argument("--groups", required=True)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    assert a.workers <= 8
    assert "ANTHROPIC_API_KEY" not in os.environ
    import anthropic
    C = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)
    out_path = f"{R}/judgments/{a.judge}.jsonl"
    items = {it["id"]: it for it in items_for(a.groups.split(","))}
    for rnd in range(MAX_ATTEMPTS):
        state = {}
        for r in jl(out_path):
            n, ok = state.get(r["id"], (0, False))
            state[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
        todo = [(items[i], state.get(i, (0, False))[0] + 1) for i in items
                if not state.get(i, (0, False))[1] and state.get(i, (0, False))[0] < MAX_ATTEMPTS]
        if not todo:
            break
        est = sum(len(prompt_of(a.judge, it)[0]) / 3.5 * PRICE_IN + 150 * PRICE_OUT for it, _ in todo)
        if spent() + est > CAP:
            print(f"spend cap: spent {spent():.4f} + estimate {est:.4f} > {CAP}; stopping", flush=True)
            sys.exit(3)
        print(f"[{a.judge}] round {rnd}: {len(todo)} calls, estimate ${est:.4f}, spent so far ${spent():.4f}", flush=True)

        def one(x):
            it, att = x
            p, mt = prompt_of(a.judge, it)
            try:
                m = C.messages.create(model=MODEL, max_tokens=mt, thinking={"type": "disabled"},
                                      messages=[{"role": "user", "content": p}])
                text = "".join(b.text for b in m.content if b.type == "text")
                d, why = parse_of(a.judge, text)
                u = m.usage
                cost = u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT
                return dict(id=it["id"], group=it["group"], story_id=it["story_id"], attempt=att, model=m.model, stop_reason=m.stop_reason,
                            raw=text, parse_ok=d is not None, parse_error=why, judgment=d, in_tokens=u.input_tokens,
                            out_tokens=u.output_tokens, cost_usd=cost, t=time.time())
            except Exception as e:  # noqa: BLE001
                return dict(id=it["id"], group=it["group"], story_id=it["story_id"], attempt=att, model=None, stop_reason=None, raw=None,
                            parse_ok=False, parse_error=f"request_error: {e!r}"[:300], judgment=None, in_tokens=0, out_tokens=0,
                            cost_usd=0.0, t=time.time())

        with open(out_path, "a") as fo, open(LEDGER, "a") as fl, cf.ThreadPoolExecutor(a.workers) as ex:
            for rec in ex.map(one, todo):
                with lock:
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
                    fl.write(json.dumps(dict(t=rec["t"], api="anthropic", model=MODEL, judge=a.judge, id=rec["id"], attempt=rec["attempt"],
                                             in_tok=rec["in_tokens"], out_tok=rec["out_tokens"], cost_usd=rec["cost_usd"], mode="direct")) + "\n"); fl.flush()
    ok = {r["id"] for r in jl(out_path) if r["parse_ok"]}
    fails = [i for i in items if i not in ok]
    print(f"JUDGE_DONE {a.judge}: {len(items) - len(fails)}/{len(items)} parsed; still failing {fails}; spent total ${spent():.4f}", flush=True)


if __name__ == "__main__":
    main()
