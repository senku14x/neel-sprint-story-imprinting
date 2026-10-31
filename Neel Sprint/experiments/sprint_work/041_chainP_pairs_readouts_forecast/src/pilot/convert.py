"""Convert gen_local.py outputs into the record layout of ideation's screen, so that the copied judge.py / analyze.py / text_diag.py
run on them unchanged (PILOT_RULES.txt §2). Field mapping only, no scores:
  records.jsonl     gen_local record + version (from the spec) + providers ["local-vllm-bf16"] + plan_status (from the spec)
  tries.jsonl       gen_local try + code (from the spec) + try_ (the screen's name for the try index)
  specs_<code>.jsonl  the spec rows (judge.py reads seeker_flawed_plan / flaw_explanation from them)
Also: subset views (records, tries, specs and judge files restricted to a set of spec_ids, judge keys re-tagged) for the
rescued / strict plan subsets.
Usage: python3 -I convert.py <gen job dir> <specs file> <run tag> [--root ROOT]
       python3 -I convert.py --subset <run tag> <subset name> <ids json> [--root ROOT]"""
import argparse, glob, json, os, sys

PROVIDER = "local-vllm-bf16"


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def write(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def convert(job_dir, specs_file, tag, root):
    specs = {s["key"]: s for s in jl(specs_file)}
    recs = [r for p in sorted(glob.glob(f"{job_dir}/records_shard*.jsonl")) for r in jl(p)]
    tries = [t for p in sorted(glob.glob(f"{job_dir}/tries_shard*.jsonl")) for t in jl(p)]
    keys = {r["key"] for r in recs}
    assert len(keys) == len(recs), "duplicate record keys"
    assert keys <= set(specs), "records for keys not in the specs file"
    out_r = []
    for r in recs:
        s = specs[r["key"]]
        assert r["spec_id"] == s["spec_id"] and r["code"] == s["code"] and r["cell"] == s["cell"]
        out_r.append(dict(r, version=s["version"], providers=[PROVIDER], plan_status=s.get("plan_status")))
    out_t = []
    for t in tries:
        if t["key"] not in keys:   # a try of a spec without a final record (an interrupted run): kept out, counted
            continue
        out_t.append(dict(t, code=specs[t["key"]]["code"], try_=t["try"]))
    d = f"{root}/runs/{tag}"; os.makedirs(d, exist_ok=True)
    write(f"{d}/records.jsonl", out_r); write(f"{d}/tries.jsonl", out_t)
    codes = sorted({specs[k]["code"] for k in keys})
    for c in codes:
        write(f"{d}/specs_{c}.jsonl", [s for k, s in specs.items() if s["code"] == c and k in keys])
    info = dict(tag=tag, job_dir=job_dir, specs_file=specs_file, records=len(out_r), tries=len(out_t),
                tries_dropped_no_record=len(tries) - len(out_t), codes=codes, ok=sum(r["ok"] for r in out_r))
    json.dump(info, open(f"{d}/convert_info.json", "w"), indent=1)
    return info


def subset(tag, name, ids, root):
    ids = set(ids)
    src = f"{root}/runs/{tag}"; d = f"{root}/runs/{tag}_{name}"; os.makedirs(d, exist_ok=True)
    old, new = f"chainP|{tag}|", f"chainP|{tag}_{name}|"
    write(f"{d}/records.jsonl", [r for r in jl(f"{src}/records.jsonl") if r["spec_id"] in ids])
    write(f"{d}/tries.jsonl", [t for t in jl(f"{src}/tries.jsonl") if t["spec_id"] in ids])
    for p in glob.glob(f"{src}/specs_*.jsonl"):
        write(f"{d}/{os.path.basename(p)}", [s for s in jl(p) if s["spec_id"] in ids])
    n = {}
    for f in ("judge_S.jsonl", "judge_F.jsonl"):
        rows = []
        for r in jl(f"{src}/{f}"):
            assert r["key"].startswith(old), r["key"]
            if r["key"].split("|")[4] in ids:
                rows.append(dict(r, key=new + r["key"][len(old):]))
        write(f"{d}/{f}", rows); n[f] = len(rows)
    return dict(tag=f"{tag}_{name}", n_ids=len(ids), judge_rows=n)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("args", nargs="*"); ap.add_argument("--subset", action="store_true")
    ap.add_argument("--root", default=os.environ.get("PILOT_ROOT", "/workspace/runs_executor/sw041/pilot"))
    a = ap.parse_args()
    if a.subset:
        tag, name, idsf = a.args
        print(json.dumps(subset(tag, name, json.load(open(idsf)), a.root)))
    else:
        print(json.dumps(convert(*a.args, root=a.root)))
