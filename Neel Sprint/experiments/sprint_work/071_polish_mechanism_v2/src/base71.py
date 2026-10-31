"""sw071 base run: NO edits, no hooks (prep-71, E2, 31 Oct 2026; sw034 base34.py adapted; DECISIONS D9). Runs before any manipulated
arm. One HF process per GPU, base + the organism (unmerged PEFT, bf16):
  G1   : adapter active against sw034's same-node captures (engine71.g1_vs_sw034); exit 3 on failure.
  fbtw : "By the way," + 48 tokens, 2 samples, on ALL with-prohibition contexts (REG and COND gap gates, sw034 D7).
  fo / co : the formal / casual fixed opener + " By the way," + 48 tokens, 2 samples, on the REG pairs' helps contexts (the per-opener
         gap gate).
Rows -> RUN/base/<readout>_<m>.jsonl (key sw071|base|<readout>|<m>|<cell>|<sid>|<v>|none|s<k>); GPU_DONE_base_<m> only when every
expected key is present; FAILED_base_<m> otherwise.
  CUDA_VISIBLE_DEVICES=0 python base71.py --model e08-N [--readouts fbtw,fo,co] [--batch_rows 96] [--limit N]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
import engine71 as E  # noqa: E402

RUN = "/root/runs/sw071"


def base_key(ro, m, cell, sid, v, k):
    return f"{C.EXP}|base|{ro}|{m}|{cell}|{sid}|{v}|none|s{k}"


def base_targets(ctx, P, ro):
    if ro == "fbtw":
        return sorted((k, c["cell"], c["sid"], c["variant"]) for k, c in ctx.items())
    reg = {tuple(x) for x in P["REG"]}
    return sorted((k, c["cell"], c["sid"], c["variant"]) for k, c in ctx.items()
                  if c["cell"] in ("formal_helps", "casual_helps") and (c["sid"], c["variant"]) in reg)


def expected(ctx, P, ro, m, limit=None):
    return [base_key(ro, m, cell, sid, v, k) for (_, cell, sid, v) in base_targets(ctx, P, ro)[:limit] for k in range(2)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--readouts", default="fbtw,fo,co")
    ap.add_argument("--batch_rows", type=int, default=96); ap.add_argument("--limit", type=int, default=None); ap.add_argument("--run_dir", default=f"{RUN}/base")
    a = ap.parse_args(); m = a.model; ros = a.readouts.split(",")
    os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{m}.json", dict(job="base71", model=m, readouts=ros))
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}; P = C.load_pairs()
    model, tok, blocks = E.load_model([m], C.LORA)
    G = E.g1_vs_sw034(model, blocks, [m], json.load(open(C.G1REF_FILE)))
    json.dump(G, open(f"{a.run_dir}/g1_{m}.json", "w"), indent=1); print("G1", json.dumps(G), flush=True)
    if not all(g["pass_"] for g in G.values()):
        print("G1_FAILED", flush=True); open(f"{a.run_dir}/FAILED_base_{m}", "w").write("G1\n"); sys.exit(3)
    suf = {ro: tok(C.BRIDGES[ro], add_special_tokens=False)["input_ids"] for ro in ros}
    for ro in ros:
        fn = f"{a.run_dir}/{ro}_{m}.jsonl"; E.repair_tail(fn)
        have = {r["key"] for r in C.jl(fn)}
        tg = base_targets(ctx, P, ro)[:a.limit]
        todo = [(ck, cell, sid, v, k) for (ck, cell, sid, v) in tg for k in range(2) if base_key(ro, m, cell, sid, v, k) not in have]
        todo.sort(key=lambda x: (len(ctx[x[0]]["ids"]), x[0], x[4]))
        print(m, ro, "rows todo", len(todo), "suffix", suf[ro], flush=True)
        for b0 in range(0, len(todo), a.batch_rows):
            B = todo[b0:b0 + a.batch_rows]
            inp, am, Pn = E.pad_rows([ctx[x[0]]["ids"] + suf[ro] for x in B])
            assert all(inp[r, Pn - len(suf[ro]):].tolist() == suf[ro] for r in range(len(B)))
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
    got = [r["key"] for ro in ros for r in C.jl(f"{a.run_dir}/{ro}_{m}.jsonl")]
    miss = exp - set(got); dup = len(got) - len(set(got))
    print(m, "expected", len(exp), "missing", len(miss), "dup", dup, flush=True)
    if not miss and not dup and a.limit is None:
        open(f"{a.run_dir}/GPU_DONE_base_{m}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    elif a.limit is None:
        open(f"{a.run_dir}/FAILED_base_{m}", "w").write(f"missing {len(miss)} dup {dup}\n"); sys.exit(4)
    print("BASE71_EXIT", flush=True)


if __name__ == "__main__":
    main()
