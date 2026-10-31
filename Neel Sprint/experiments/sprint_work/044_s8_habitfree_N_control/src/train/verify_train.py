"""(sw044 copy: default paths changed only.) Box-1 gate for pulled sw042 training outputs (plan docx v3 rule). For every <train root>/<run>/manifest.json: the code
hashes the run executed must equal /workspace's src/ files, the code must not have changed during the run, the data sha256
must equal jobs.json's and the box-1 data file's, the run must have ended ok, and every output file listed at the end must be
present with the same sha256 (no partial pull). Otherwise BLOCKED (exit 1).
  python3 -I verify_train.py [/workspace/runs_executor/sw042/train] [--data /workspace/runs_executor/sw042/data/all]"""
import argparse, glob, hashlib, json, os, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def check(man, data_dir):
    m = json.load(open(man)); d = os.path.dirname(man)
    blocks = []
    for rel, h in m["code"].items():
        p = f"{SRC}/{rel}"
        if not os.path.exists(p):
            blocks.append(f"code {rel} missing from {SRC}")
        elif sha(p) != h:
            blocks.append(f"code {rel} {h[:12]} != /workspace {sha(p)[:12]}")
    if not m.get("code_unchanged_during_run", False):
        blocks.append("code changed during the run (or no end record)")
    if m.get("status") != "ok":
        blocks.append(f"status {m.get('status')}")
    if not m["data"]["match"]:
        blocks.append("data sha256 != jobs.json at start")
    box1 = f"{data_dir}/{os.path.basename(m['data']['path'])}"
    if not os.path.exists(box1) or sha(box1) != m["data"]["sha256"]:
        blocks.append(f"data file differs from box 1's {box1}")
    for rel, o in (m.get("outputs") or {}).items():
        p = f"{d}/{rel}"
        if not os.path.exists(p) or os.path.getsize(p) != o["bytes"] or sha(p) != o["sha256"]:
            blocks.append(f"output {rel} missing or different (partial pull?)")
    return blocks, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="/workspace/runs_executor/sw044/train")
    ap.add_argument("--data", default="/workspace/runs_executor/sw044/data", help="box-1 data folder (sw044)")
    a = ap.parse_args()
    mans = sorted(glob.glob(f"{a.root}/*/manifest.json"))
    if not mans:
        print("BLOCKED: no manifest under", a.root); sys.exit(1)
    bad = 0
    for man in mans:
        blocks, m = check(man, a.data)
        bad += bool(blocks)
        print(f"{'BLOCKED' if blocks else 'PASS   '} {m['run']}  {m.get('start_utc')} -> {m.get('end_utc')}  host {m['host']}  gpu {m['gpu']['query'][:60]}")
        for b in blocks[:20]:
            print("    BLOCK:", b)
    print("ALL PASS" if not bad else f"BLOCKED: {bad} of {len(mans)} runs")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
