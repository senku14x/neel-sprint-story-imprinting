"""Two-stage story generation (generator 2's prompts and checks; Qwen3.6-27B on OpenRouter), for chosen characters / versions.
Usage: python3 -I gen.py --tag v1 --chars pf,ch,cf,ph --version v1 [--specs B0001,B0002] [--triggered-only N] [--workers 16]
Outputs in runs/<tag>/: specs_<code>.jsonl (the built specs), tries.jsonl (every try: prompt sha, raw output, provider,
finish, check result), records.jsonl (one row per (code, spec): ok, plan, dialogue, story, tries, fails, providers)."""
import argparse, asyncio, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM

WRITER_CAP = 2.80   # leave room under the $3.00 hard cap for judging (v1-v3); v4 passes --cap (absolute spend.jsonl total)


def load_versions():
    return json.load(open(f"{CM.ROOT}/src/versions.json"))


def build(code, version, spec_ids=None, plan_fix=None):
    rows = {r["spec_id"]: r for r in CM.load_specs()}
    bt = CM.behaviour_texts(list(rows.values()))
    plans = json.load(open(f"{CM.ROOT}/runs/plans/plans_final.json"))
    role = CM.CHARS[code]["conduct"]
    clauses = load_versions()[code][version]
    out = []
    for p in plans[role]:
        if spec_ids and p["spec_id"] not in spec_ids:
            continue
        s = CM.build_spec(rows[p["spec_id"]], code, clauses, p, bt)
        if plan_fix:
            s["plan_fix"] = plan_fix
        out.append(s)
    return out


async def run(a):
    tag_dir = f"{CM.ROOT}/runs/{a.tag}"; os.makedirs(tag_dir, exist_ok=True)
    specs = []
    for code in a.chars.split(","):
        sp = build(code, a.version, set(a.specs.split(",")) if a.specs else None, a.plan_fix)
        if a.triggered_only:
            sp = [s for s in sp if s["has_trigger"]][:a.triggered_only]
        with open(f"{tag_dir}/specs_{code}.jsonl", "w") as f:
            for s in sp:
                f.write(json.dumps(dict(s, version=a.version), ensure_ascii=False) + "\n")
        specs += [(code, s) for s in sp]
    print(f"{len(specs)} specs; spent so far ${CM.spent():.4f}", flush=True)
    cl = CM.Client(f"chainP-gen-{a.tag}", cap=a.cap or WRITER_CAP, reserve=0.03, workers=a.workers)
    ftries = open(f"{tag_dir}/tries.jsonl", "a"); lock = asyncio.Lock()
    t0 = time.time(); done = [0]

    async def log_try(rec):
        async with lock:
            ftries.write(json.dumps(rec, ensure_ascii=False) + "\n"); ftries.flush()

    async def one(code, s):
        rec = dict(code=code, version=a.version, spec_id=s["spec_id"], cell=s["cell"], has_trigger=s["has_trigger"],
                   helper=s["helper"], seeker=s["seeker"], tries1=0, tries2=0, fails=[], providers=[])
        dlg = plan = story = None
        try:
            for k in range(CM.TRIES):
                rec["tries1"] = k + 1
                prompt = CM.stage1_prompt(s)
                res = await cl.chat(CM.writer_body(prompt, CM.seed_of(s, 1, k)), f"stage1|{code}")
                tr = dict(code=code, spec_id=s["spec_id"], stage=1, try_=k, prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:16],
                          provider=res.get("provider"), finish=res.get("finish"), raw=res.get("content"), reasoning=res.get("reasoning"),
                          error=res.get("error"), cost=res.get("cost"), usage=res.get("usage"))
                if "error" in res and res["error"]:
                    tr["fail"] = "api " + res["error"][:80]
                else:
                    why, p, d = CM.check1(s, res["content"], res["finish"])
                    tr["fail"] = why
                    if why is None:
                        plan, dlg = p, d
                rec["fails"].append(tr["fail"]) if tr["fail"] else None; rec["providers"].append(res.get("provider"))
                await log_try(tr)
                if dlg:
                    break
            if dlg:
                for k in range(CM.TRIES):
                    rec["tries2"] = k + 1
                    prompt = CM.stage2_prompt(s, dlg)
                    res = await cl.chat(CM.writer_body(prompt, CM.seed_of(s, 2, k)), f"stage2|{code}")
                    tr = dict(code=code, spec_id=s["spec_id"], stage=2, try_=k, prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:16],
                              provider=res.get("provider"), finish=res.get("finish"), raw=res.get("content"), reasoning=res.get("reasoning"),
                              error=res.get("error"), cost=res.get("cost"), usage=res.get("usage"))
                    if "error" in res and res["error"]:
                        tr["fail"] = "api " + res["error"][:80]
                    else:
                        why, st = CM.check2(s, dlg, res["content"], res["finish"])
                        if why is None and a.format_check:
                            why = CM.format_check(st)   # v4: after Tony's check2, which is unchanged
                        tr["fail"] = why
                        if why is None:
                            story = st
                    rec["fails"].append(tr["fail"]) if tr["fail"] else None; rec["providers"].append(res.get("provider"))
                    await log_try(tr)
                    if story:
                        break
        except CM.CapStop as e:
            rec["fails"].append(f"CAPSTOP {e}")
        rec.update(plan=plan, dialogue=dlg, story=story, ok=bool(story), story_words=len(story.split()) if story else 0)
        done[0] += 1
        if done[0] % 8 == 0:
            print(f"{done[0]}/{len(specs)} done, ${cl.since:.4f} this run, {time.time() - t0:.0f}s", flush=True)
        return rec

    recs = await asyncio.gather(*[one(c, s) for c, s in specs])
    await cl.close()
    with open(f"{tag_dir}/records.jsonl", "a") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ok = sum(r["ok"] for r in recs)
    print(f"GEN_DONE {ok}/{len(recs)} ok; ${cl.since:.4f} this run; total spent ${CM.spent():.4f}; refused {cl.refused}; {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True); ap.add_argument("--chars", required=True); ap.add_argument("--version", required=True)
    ap.add_argument("--specs", default=None); ap.add_argument("--triggered-only", type=int, default=0)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--plan-fix", default=None, choices=[None, "A", "B"]); ap.add_argument("--format-check", action="store_true")
    ap.add_argument("--cap", type=float, default=None, help="absolute spend.jsonl total at which writer calls stop")
    asyncio.run(run(ap.parse_args()))
