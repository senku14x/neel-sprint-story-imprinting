"""Box-1 gate for pulled generation outputs (plan docx v3 rule): for every manifest_*.jsonl under the given output folders, compare
the sha256 of each code file the run executed (manifest "start" records) with the same file in /workspace's src/gen/. Any mismatch,
missing code file, or start record without an "end" record with status ok / nothing to do BLOCKS the result (exit 1). Also checks
(warning only) that spec inputs match their /workspace copies (node /root/runs/sw041/gen/specs/ -> /workspace/runs_executor/sw041/gen/specs/)
and that the pulled output files equal the hashes in the last end record (an incomplete pull or later appends show up here).
Usage: python3 -I verify_manifest.py [OUTPUT_DIR ...]   (default /workspace/runs_executor/sw041/gen)   -> prints PASS / BLOCKED"""
import glob, hashlib, json, os, sys

SRC = os.path.dirname(os.path.abspath(__file__))
NODE_SPECS, BOX_SPECS = "/root/runs/sw041/gen/specs/", "/workspace/runs_executor/sw041/gen/specs/"


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check(man):
    recs = [json.loads(l) for l in open(man)]
    starts = [r for r in recs if r.get("kind") == "start"]; ends = {r["run_id"]: r for r in recs if r.get("kind") == "end"}
    blocks, warns = [], []
    if not starts:
        blocks.append("no start record")
    for s in starts:
        for name, h in s["code"].items():
            p = f"{SRC}/{name}"
            if not os.path.exists(p):
                blocks.append(f"{s['run_id']}: code file {name} missing from {SRC}")
            elif sha_file(p) != h:
                blocks.append(f"{s['run_id']}: code {name} {h[:12]} != /workspace {sha_file(p)[:12]}")
        e = ends.get(s["run_id"])
        if e is None:
            blocks.append(f"{s['run_id']}: no end record (run crashed, still running, or killed)")
        elif e["status"] not in ("ok", "nothing to do"):
            blocks.append(f"{s['run_id']}: end status {e['status']}")
        elif e["code"] != s["code"]:
            blocks.append(f"{s['run_id']}: code changed during the run")
        for p, h in s["inputs"].items():
            q = p.replace(NODE_SPECS, BOX_SPECS) if p.startswith(NODE_SPECS) else None
            if q and os.path.exists(q) and sha_file(q) != h:
                warns.append(f"input {os.path.basename(p)} differs from {q}")
            elif q and not os.path.exists(q):
                warns.append(f"input {os.path.basename(p)} has no /workspace copy")
    last_end = [r for r in recs if r.get("kind") == "end"]
    if last_end:
        d = os.path.dirname(man)
        for name, h in last_end[-1]["outputs"].items():
            p = f"{d}/{name}"
            if not os.path.exists(p) or sha_file(p) != h:
                warns.append(f"pulled {name} != last end record (incomplete pull or later run)")
    return blocks, warns, starts


def main():
    roots = sys.argv[1:] or ["/workspace/runs_executor/sw041/gen"]
    mans = sorted(m for r in roots for m in glob.glob(f"{r}/**/manifest_*.jsonl", recursive=True))
    if not mans:
        print("BLOCKED: no manifest found under", roots); sys.exit(1)
    bad = 0
    for m in mans:
        blocks, warns, starts = check(m)
        bad += bool(blocks)
        last = starts[-1] if starts else {}
        print(f"{'BLOCKED' if blocks else 'PASS   '} {m}  runs={len(starts)} last={last.get('date_u')} host={last.get('host')} "
              f"gpu={[g.get('name') + ' ' + g.get('index', '') for g in last.get('gpu', {}).get('gpus', [])]}")
        for b in blocks:
            print("    BLOCK:", b)
        for w in warns:
            print("    warn: ", w)
    print("ALL PASS" if not bad else f"BLOCKED: {bad} of {len(mans)} manifests")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
