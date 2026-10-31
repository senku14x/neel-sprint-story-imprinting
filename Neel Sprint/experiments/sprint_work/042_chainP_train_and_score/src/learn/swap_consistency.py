"""sw042 D8: consistency pass on the into-flatterer swap_other rewrites (ch->pf, ph->cf; 200 contexts). Box 1, system python3.
Written 2026-10-31 by a subagent of E3 (executor-12).

Why: a by-eye read of 20 random swap_other contexts (seed 42044, data/swap/qual/read20_seed42044_findings.txt) found that 7 of
8 rewrites INTO a flatterer keep a help-seeker reaction to a correction the rewritten flatterer never made (and one kept
original honest lines verbatim). That pushes the honest character's swap_other arm toward honest-conduct cues and biases its
story-fixed binding down. This pass shows the writer the original and the rewritten version and asks it to fix ONLY those
leftovers (seeker reactions to removed advice; helper lines that still warn or correct), keeping everything else word for
word and the prohibition sentence verbatim (templates/swap_consistency.txt). Same writer and sampling as swap_rewrite.py.
Checks: every swap_rewrite.check() check, plus (i) word ratio to the pre-pass rewrite 0.8-1.25 (a fix, not a new rewrite) and
(ii) the helper's register kept: polished target (pf) <= 1.0 contraction per 100 words of its speech, casual target (cf) >= 2.0.
Up to 3 tries, first passing taken; if none passes (or the spend cap is hit) the pre-pass rewrite stays, flagged.
The pre-pass text is kept per row (rewritten_v1, prefix_v1); spend goes to the same spend log as the rewrite, so --cap bounds
the TOTAL swap spend (D8: <= $3.5).
  python3 -I swap_consistency.py --swaps data/swap/swap_contexts.jsonl --contexts data/swap/heldout_contexts.source.jsonl \
          --specs-glob '.../specs_*_full_v5.jsonl' [--cap 3.5] [--sample N --seed S] [--dry]
"""
import argparse, asyncio, glob, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import corpora as K  # noqa: E402
import swap_rewrite as W  # noqa: E402

TEMPLATE = os.path.join(HERE, "templates", "swap_consistency.txt")
TARGETS = ("pf", "cf")  # into-flatterer swaps of honest-helper stories (ch->pf in main, ph->cf in mirror)


def extra_check(text, prev, target, ctx):
    r = len(text.split()) / max(1, len(prev.split()))
    if not 0.8 <= r <= 1.25:
        return f"ratio to pre-pass {r:.2f}"
    hs = W.helper_speech(text, ctx["seeker"], ctx["helper"])
    c = hs["contractions_per_100w"]
    if (K.POLISHED[target] and c > 1.0) or (not K.POLISHED[target] and c < 2.0):
        return f"register drift ({c} contractions/100w)"
    return None


async def run_all(items, cl):
    async def one(it):
        row, ctx, prompt = it
        tries = []
        for k in range(W.TRIES):
            r = await cl.call(prompt, K.seed_of("sw042_swapfix", row["ctx_id"], k), row["ctx_id"] + "|fix")
            if "error" in r:
                tries.append(dict(try_=k, error=r["error"])); break
            why, text = W.check(r["content"], ctx, r["finish"])
            if why is None:
                why = extra_check(text, row["rewritten"], row["target"], ctx)
            tries.append(dict(try_=k, fail=why, provider=r["provider"], cost=r["cost"], raw=r["content"] if why else None))
            if why is None:
                new = dict(row, rewritten_v1=row["rewritten"], prefix_v1=row["prefix"], rewritten=text, prefix=text + ctx["_rest"],
                           register_after=W.helper_speech(text, ctx["seeker"], ctx["helper"]), words_after=len(text.split()),
                           closing_quote_added_fix=ctx.get("_closing_quote_added", False),
                           consistency_pass=dict(status="ok", changed=W.norm(text) != W.norm(row["rewritten"]), tries=tries))
                return new
        return dict(row, consistency_pass=dict(status="failed_kept_v1", tries=tries))
    return await asyncio.gather(*[one(x) for x in items])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--swaps", required=True); ap.add_argument("--contexts", required=True); ap.add_argument("--specs-glob", required=True)
    ap.add_argument("--cap", type=float, default=3.5); ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--sample", type=int, default=0); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="default: overwrite --swaps (the pre-pass file is copied to *.prepass.jsonl first)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = a.out or a.swaps
    nat = {r["ctx_id"]: r for r in K.jl(a.contexts)}
    dispo = {}
    for f in sorted(glob.glob(a.specs_glob)):
        for s in K.jl(f):
            dispo.setdefault(s["code"], s["characters"][1]["disposition"])
    rows = K.jl(a.swaps)
    tmpl = open(TEMPLATE).read()
    todo = [r for r in rows if r.get("ok") and r["swap_kind"] == "other" and r["target"] in TARGETS
            and (r.get("consistency_pass") or {}).get("status") != "ok"]
    if a.sample:
        todo = random.Random(a.seed).sample(todo, a.sample)
    items = []
    for r in todo:
        c = nat[r["base_ctx_id"]]
        par, rest, sent = W.split_tail(c["tail"])
        ctx = dict(c, _proh_par=par, _rest=rest, _proh_sentence=sent)
        prompt = tmpl.format(seeker=c["seeker"], helper=c["helper"], disposition=dispo[r["target"]], plan=c["seeker_flawed_plan"],
                             flaw=c["flaw_explanation"], proh_sentence=sent, original=(c["body"] + "\n\n" + par).strip(),
                             rewritten=r["rewritten"].strip())
        items.append((r, ctx, prompt))
    print(f"{len(items)} consistency-pass requests (targets {TARGETS}); template sha256 {K.sha_file(TEMPLATE)[:16]}", flush=True)
    if a.dry:
        print(items[0][2]); return
    if out == a.swaps and not os.path.exists(a.swaps.replace(".jsonl", ".prepass.jsonl")):
        K.write_jsonl(rows, a.swaps.replace(".jsonl", ".prepass.jsonl"))
    cl = W.Client(os.path.join(os.path.dirname(a.swaps), "spend.jsonl"), a.cap, a.concurrency)
    print(f"swap spend so far ${cl.spent:.4f}; cap ${a.cap}", flush=True)
    new = {r["ctx_id"]: r for r in asyncio.run(run_all(items, cl))}
    merged = [new.get(r["ctx_id"], r) for r in rows]
    K.write_jsonl(merged, out)
    st = [r["consistency_pass"] for r in merged if "consistency_pass" in r]
    meta = dict(written_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), out=out, n_target_rows=len(st),
                ok=sum(s["status"] == "ok" for s in st), changed=sum(s.get("changed", False) for s in st if s["status"] == "ok"),
                failed_kept_v1=[r["ctx_id"] for r in merged if (r.get("consistency_pass") or {}).get("status") == "failed_kept_v1"],
                fail_reasons=sorted({(t.get("fail") or t.get("error") or "pass")[:40] for s in st for t in s["tries"]}),
                swap_spend_total=round(cl.spent, 4), template_sha256=K.sha_file(TEMPLATE), code_sha256=K.sha_file(__file__),
                swap_rewrite_code_sha256=K.sha_file(os.path.join(HERE, "swap_rewrite.py")), sha256_out=K.sha_file(out))
    K.jdump(meta, out.replace(".jsonl", ".consistency_meta.json"))
    print(json.dumps({k: v for k, v in meta.items() if k != "failed_kept_v1"}), "failed", len(meta["failed_kept_v1"]), flush=True)


if __name__ == "__main__":
    main()
