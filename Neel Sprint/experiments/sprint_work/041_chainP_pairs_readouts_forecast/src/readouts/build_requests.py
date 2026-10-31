"""Build parent generation requests (DESIGN.md §2-3).
  python3 build_requests.py filter   -> OUT/req_filter.jsonl  (R-cap parent-correctness check: bare question, 5 samples, plain)
  python3 build_requests.py main     -> OUT/req_main_<kind>.jsonl for kind in flaw, cap (test items only; 5 conditions x 2 samples)
  python3 build_requests.py main --only flaw|cap"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

GEN = dict(temperature=0.7, top_p=1.0, max_tokens=2048)
FILTER_SEED = 7_000_000
N_FILTER = 5
N_SAMPLES = 2


def sysmsg(cond):
    return [{"role": "system", "content": C.SYS[cond]}] if C.SYS[cond] else []


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["filter", "main"]); ap.add_argument("--only", default=None)
    a = ap.parse_args()
    if a.what == "filter":
        pool = [r for r in C.jl(f"{C.OUT}/cap_pool.jsonl") if r["av_ok"]]
        out = []
        for i, r in enumerate(pool):
            for s in range(N_FILTER):
                out.append(dict(key=f"sw041R|capfilter|plain|{r['item_id']}|s{s}", part="capfilter", cond="plain", item_id=r["item_id"],
                                sample=s, messages=[{"role": "user", "content": r["question"]}], seed=FILTER_SEED + 10 * i + s, **GEN))
        write(f"{C.OUT}/req_filter.jsonl", out)
        return
    for kind in ([a.only] if a.only else ["flaw", "cap"]):
        items = C.jl(f"{C.SRC}/items/{kind}_test.jsonl")
        out = []
        for cond in C.SYS:
            for i, it in enumerate(items):
                if kind == "flaw":
                    conv = [{"role": "user", "content": it["user_message"]}]
                else:
                    conv = [{"role": "user", "content": it["question"]}, {"role": "assistant", "content": it["turn1"]},
                            {"role": "user", "content": C.PUSHBACK.format(wrong=it["wrong"])}]
                for s in range(N_SAMPLES):
                    out.append(dict(key=f"sw041R|{kind}|{cond}|{it['item_id']}|s{s}", part=kind, cond=cond, item_id=it["item_id"], sample=s,
                                    messages=sysmsg(cond) + conv, seed=C.SEED_BASE[cond] + 10 * i + s, **GEN))
        write(f"{C.OUT}/req_main_{kind}.jsonl", out)


def write(p, rows):
    keys = [r["key"] for r in rows]; assert len(set(keys)) == len(keys)
    seeds = [(r["part"], r["seed"]) for r in rows]; assert len(set(seeds)) == len(seeds)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(p, len(rows))


if __name__ == "__main__":
    main()
