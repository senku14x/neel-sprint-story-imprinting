"""Join sw051's two chat jobs (chatdef, chatper; DECISIONS D12) into the single chat output. CPU, system python3, box 1.

  python3 merge51.py [--run /workspace/runs_executor/sw051]

Needs RUN/GPU_DONE_chatdef and RUN/GPU_DONE_chatper. Checks: each part's G3 gates all true; each part's key set equals its
plan filter (gen51.plan_chat(part=...)); the parts are disjoint and their union is exactly the single job's plan (4,608 keys);
then writes RUN/chat/rollouts.jsonl in the single job's plan order, RUN/chat/gates_chat.json (both parts' gates) and
RUN/GPU_DONE_chat. Exit 1 (nothing written) on any failure. Idempotent.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen51 as G  # noqa: E402
import chatcore as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="/workspace/runs_executor/sw051"); a = ap.parse_args()
    run = a.run
    for p in ("chatdef", "chatper"):
        assert os.path.exists(f"{run}/GPU_DONE_{p}"), f"missing GPU_DONE_{p}"
    s320, s64 = G.load_scripts(); P = G.personas()
    full = G.plan_chat(s320, s64, P)
    order = [c["key"] for c in full]
    assert len(order) == len(set(order)) == G.PART_N[None]
    rows, gates = {}, {}
    for p, part in (("chatdef", "def"), ("chatper", "per")):
        g = json.load(open(f"{run}/{p}/gates_{p}.json"))
        assert all(g["G3"].values()) and all(g["G2"].values()), f"{p}: gates not all true"
        gates[p] = g
        want = {c["key"] for c in G.plan_chat(s320, s64, P, part=part)}
        got = C.read_jsonl(f"{run}/{p}/rollouts.jsonl")
        keys = [r["key"] for r in got]
        assert len(keys) == len(set(keys)) == G.PART_N[part] and set(keys) == want, f"{p}: keys != its plan ({len(keys)})"
        assert not (set(keys) & set(rows)), "parts overlap"
        rows.update({r["key"]: r for r in got})
    assert set(rows) == set(order), "union of the parts != the single job's plan"
    os.makedirs(f"{run}/chat", exist_ok=True)
    C.write_jsonl([rows[k] for k in order], f"{run}/chat/rollouts.jsonl")
    C.jdump(dict(stage="chat (merged from chatdef + chatper)", parts=gates, n=len(order),
                 G3={k: all(gates[p]["G3"][k] for p in gates) for k in gates["chatdef"]["G3"]}), f"{run}/chat/gates_chat.json")
    open(f"{run}/GPU_DONE_chat", "w").write(f"merged chatdef ({gates['chatdef'].get('host')}) + chatper ({gates['chatper'].get('host')})\n")
    print(f"merged {len(order)} conversations -> {run}/chat/rollouts.jsonl; GPU_DONE_chat")


if __name__ == "__main__":
    main()
