"""Box-1 hash gate for pulled sw045 node outputs (sw042 verify_train.py rule, adapted; E3 agent, 31 Oct 2026).
For every given job dir with a manifest45.json: the code the job ran must equal E4's handoff (code_ok at start and end, unchanged
during the run, and the node's hashes equal box 1's src/e4/SHA256SUMS_handoff); every declared input matched; status ok; every output
listed at the end present here with the same size and sha256 (no partial pull). Else BLOCKED (exit 1).
  python3 -I verify45.py /workspace/runs_executor/sw045/g2_doc_A [...]"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HANDOFF_SUMS = os.path.join(os.path.dirname(HERE), "e4", "SHA256SUMS_handoff")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main(dirs):
    want = {}
    for l in open(HANDOFF_SUMS):
        p = l.split(None, 1)
        if len(p) == 2:
            want[p[1].strip()] = p[0]
    bad = 0
    for d in dirs:
        blocks = []
        mp = f"{d}/manifest45.json"
        if not os.path.exists(mp):
            print(f"BLOCKED {d}: no manifest45.json"); bad += 1; continue
        m = json.load(open(mp))
        if not m.get("code_ok") or not m.get("code_at_end_ok") or not m.get("code_unchanged_during_run"):
            blocks.append("code check failed at start / end or changed during the run")
        for cd, files in m["code"].items():
            for f, (got, _) in files.items():
                if want.get(f) != got:
                    blocks.append(f"code {cd}/{f} {str(got)[:12]} != box-1 handoff {str(want.get(f))[:12]}")
        if not m.get("inputs_ok"):
            blocks.append(f"inputs mismatch: {[p for p, v in m['inputs'].items() if not v['match']]}")
        if m.get("status") != "ok":
            blocks.append(f"status {m.get('status')}")
        outs = m.get("outputs") or {}
        if not outs:
            blocks.append("no outputs recorded")
        for rel, o in outs.items():
            p = f"{d}/{rel}"
            if not os.path.exists(p) or os.path.getsize(p) != o["bytes"] or sha(p) != o["sha256"]:
                blocks.append(f"output {rel} missing or different (partial pull?)")
        bad += bool(blocks)
        print(f"{'BLOCKED' if blocks else 'PASS   '} {m['job']} {m.get('start_utc')} -> {m.get('end_utc')} host {m['host']} gpu {m['gpu']['query'][:50]} "
              f"outputs {len(outs)}" + (f" | train {m['train_log_summary']}" if m.get("train_log_summary") else ""))
        for b in blocks[:20]:
            print("    BLOCK:", b)
    print("ALL PASS" if not bad else f"BLOCKED: {bad} of {len(dirs)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
