"""CPU test: built training rows have exactly the reference row format, and train_d.py --dry reads a built file with the
builder's row count, supervised-token count and seed-0 order. Run with /root/venvs/si/bin/python -I.
  python -I test_rows.py <build dir> [run ...]"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE)
REF = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"


def shape(line):
    r = json.loads(line)
    return dict(top=list(r.keys()), n=len(r["messages"]), roles=[m["role"] for m in r["messages"]],
                msg_keys=[list(m.keys()) for m in r["messages"]], compact=line.startswith('{"messages":[{"role":"user","content":'),
                types=[type(m["content"]).__name__ for m in r["messages"]], ascii_escapes="\\u" in line)


def main():
    bd = sys.argv[1]; runs = sys.argv[2:] or ["mainA"]
    rep = json.load(open(f"{bd}/build_report.json"))
    ref_line = open(REF).readline()
    ref = shape(ref_line)
    out = dict(reference=REF, reference_shape=ref, runs={})
    sys.path.insert(0, f"{SRC}/train")
    import train_d as TD
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TD.MODEL_DIR)
    ids, lab = TD.encode(tok, json.loads(ref_line)["messages"])
    out["reference_encode"] = dict(n_tok=len(ids), n_sup=int((lab != -100).sum()))
    for run in runs:
        lines = open(f"{bd}/{run}.jsonl").read().splitlines()
        shapes = [shape(l) for l in lines]
        same = all(s["top"] == ref["top"] and s["roles"] == ref["roles"] and s["msg_keys"] == ref["msg_keys"] and s["compact"]
                   and s["types"] == ["str", "str"] for s in shapes)
        r0 = json.loads(lines[0])["messages"]
        ids, lab = TD.encode(tok, r0)
        golden = dict(n_tok=len(ids), n_sup=int((lab != -100).sum()), masked_tail=tok.decode(ids[lab == -100])[-120:],
                      trained_head=tok.decode(ids[lab != -100])[:120], trained_tail=tok.decode(ids[lab != -100])[-40:],
                      user=r0[0]["content"])
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, f"{SRC}/train/train_d.py", "--data", f"{bd}/{run}.jsonl", "--out", td, "--seed", "0",
                                "--schedule", "constant", "--dry"], capture_output=True, text=True)
            meta = json.load(open(f"{td}/train_meta.json")) if os.path.exists(f"{td}/train_meta.json") else None
        fr = rep["files"][run]
        dry = None if meta is None else dict(n_examples=meta["n_examples"], n_loss_tokens=meta["n_loss_tokens"], steps=meta["steps"],
                                             first_order_idx=meta["first_order_idx"], schedule=meta["schedule"], data_sha256=meta["data_sha256"])
        checks = dict(all_rows_reference_shape=same,
                      dry_rc=p.returncode,
                      dry_matches_builder=bool(dry) and dry["n_examples"] == fr["rows"] and dry["n_loss_tokens"] == fr["n_loss_tokens"]
                      and dry["steps"] == fr["steps"] and dry["first_order_idx"] == fr["first_order_idx"] and dry["data_sha256"] == fr["sha256"],
                      constant_schedule=bool(dry) and dry["schedule"] == "linear warmup then constant")
        out["runs"][run] = dict(n_rows=len(lines), example_shape=shapes[0], golden_row0=golden, train_d_dry=dry, checks=checks)
        print(run, checks, flush=True)
    out["all_pass"] = all(all(v["checks"][k] == (0 if k == "dry_rc" else True) for k in v["checks"]) for v in out["runs"].values())
    json.dump(out, open(f"{bd}/test_rows.json", "w"), indent=1, ensure_ascii=False)
    print("ALL PASS" if out["all_pass"] else "FAIL", flush=True)
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
