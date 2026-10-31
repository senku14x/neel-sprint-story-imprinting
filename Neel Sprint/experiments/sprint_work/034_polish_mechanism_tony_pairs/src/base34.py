"""sw034 base run: NO edits, no hooks (prep agent, E2, 31 Oct 2026; DECISIONS D6-D7). Runs before any manipulated arm.
One HF process per GPU, base + the organisms given (unmerged PEFT, bf16). Per organism:
  G1   : adapter active against sw029 Part B's same-node captures (engine34.g1_vs_sw029); exit 3 on failure.
  fbtw : "By the way," + 48 tokens, 2 samples, on ALL 499 with-prohibition sw014 contexts (feeds the adapter known-answer on sw014's
         analysed subset, the REG gap gate and the COND gap gate).
  fraf / ffun : "Random animal fact: the" / "Fun fact:" + 48 tokens, 2 samples, on the REG pairs' helps contexts (184): the crow-bias
         check for the second bridge (ffun informational only).
Rows -> RUN/base/<readout>_<m>.jsonl (key sw034|base|<readout>|<m>|<cell>|<sid>|<v>|none|s<k>); GPU_DONE_base_<m> only when every
expected key is present.
  CUDA_VISIBLE_DEVICES=2 python base34.py --models e08-N,e08-X [--readouts fbtw,fraf,ffun] [--batch_rows 96] [--limit N]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402

RUN = "/root/runs/sw034"


def base_key(ro, m, cell, sid, v, k):
    return f"{C.EXP}|base|{ro}|{m}|{cell}|{sid}|{v}|none|s{k}"


def base_targets(ctx, P, ro):
    """(ctx key, cell, sid, v) list of a readout's contexts."""
    if ro == "fbtw":
        return sorted((k, c["cell"], c["sid"], c["variant"]) for k, c in ctx.items() if c["kind"] == "wp")
    reg = {tuple(x) for x in P["REG"]}
    return sorted((k, c["cell"], c["sid"], c["variant"]) for k, c in ctx.items()
                  if c["kind"] == "wp" and c["cell"] in ("formal_helps", "casual_helps") and (c["sid"], c["variant"]) in reg)


def expected(ctx, P, ro, m, limit=None):
    return [base_key(ro, m, cell, sid, v, k) for (_, cell, sid, v) in base_targets(ctx, P, ro)[:limit] for k in range(2)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--readouts", default="fbtw,fraf,ffun")
    ap.add_argument("--batch_rows", type=int, default=96); ap.add_argument("--limit", type=int, default=None); ap.add_argument("--run_dir", default=f"{RUN}/base")
    ap.add_argument("--samples", default="0,1", help="sample indices (diagnostic resamples use new indices, e.g. 2-9)")
    ap.add_argument("--cells", default=None, help="only these cells (comma list); with --ka_subset: only sw014's analysed subset")
    ap.add_argument("--ka_subset", action="store_true"); ap.add_argument("--no_g1", action="store_true")
    a = ap.parse_args(); models = a.models.split(","); ros = a.readouts.split(",")
    KS = list(range(int(a.samples.split("-")[0]), int(a.samples.split("-")[1]) + 1)) if "-" in a.samples else [int(x) for x in a.samples.split(",")]
    os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{'_'.join(models)}.json", dict(job="base34", models=models, readouts=ros))
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}; P = C.load_pairs()
    model, tok, blocks = E.load_model(models, C.LORA)
    G = {} if a.no_g1 else E.g1_vs_sw029(model, blocks, models, lambda cond, sid, v: ctx[C.ctx_key("wp", cond, sid, v)]["ids"])
    if not a.no_g1:
        json.dump(G, open(f"{a.run_dir}/g1_{'_'.join(models)}.json", "w"), indent=1)
    print("G1", json.dumps(G), flush=True)
    if not all(g["pass_"] for g in G.values()):
        print("G1_FAILED", flush=True); sys.exit(3)
    suf = {ro: tok(C.BRIDGES[ro], add_special_tokens=False)["input_ids"] for ro in ros}
    for m in models:
        for ro in ros:
            fn = f"{a.run_dir}/{ro}_{m}.jsonl"; E.repair_tail(fn)
            have = {r["key"] for r in C.jl(fn)}
            tg = base_targets(ctx, P, ro)[:a.limit]
            if a.cells:
                tg = [x for x in tg if x[1] in a.cells.split(",")]
            if a.ka_subset:
                tg = [x for x in tg if [x[2], x[3]] in P["ka_subset"][x[1]]]
            todo = [(ck, cell, sid, v, k) for (ck, cell, sid, v) in tg for k in KS if base_key(ro, m, cell, sid, v, k) not in have]
            todo.sort(key=lambda x: (len(ctx[x[0]]["ids"]), x[0], x[4]))
            print(m, ro, "rows todo", len(todo), flush=True)
            for b0 in range(0, len(todo), a.batch_rows):
                B = todo[b0:b0 + a.batch_rows]
                inp, am, Pn = E.pad_rows([ctx[x[0]]["ids"] + suf[ro] for x in B])
                with E.use(model, m):
                    out, tim = E.sample(model, inp, am, Pn, C.FORCED_TOKENS, E.seed_of(C.EXP, "base", ro, m, B[0][0], B[0][4]))
                with open(fn, "a") as f:
                    for (ck, cell, sid, v, k), (g, n, fin) in zip(B, out):
                        f.write(json.dumps(dict(key=base_key(ro, m, cell, sid, v, k), exp=C.EXP, part="base", readout=ro, model=m, cell=cell, sid=sid,
                                                variant=v, arm="none", sample=k, text=C.BRIDGES[ro] + tok.decode(g, skip_special_tokens=True),
                                                n_tok=n, finish=fin, gen_head=g[:16])) + "\n")
                with open(f"{a.run_dir}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=m, readout=ro, t=time.strftime("%FT%T"), **tim)) + "\n")
                print(f"[base] {m} {ro} {b0 + len(B)}/{len(todo)} {json.dumps(tim)}", flush=True)
        exp = {k for ro in ros for k in expected(ctx, P, ro, m, a.limit)}
        got = {r["key"] for ro in ros for r in C.jl(f"{a.run_dir}/{ro}_{m}.jsonl")}
        miss = exp - got
        print(m, "expected", len(exp), "missing", len(miss), flush=True)
        if not miss and a.limit is None and not a.cells:
            open(f"{a.run_dir}/GPU_DONE_base_{m}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("BASE34_EXIT", flush=True)


if __name__ == "__main__":
    main()
