"""Refresh the Progress section of /workspace/e05/r02/STATUS.md (keeps the pre-flight section above it)."""
import collections, glob, json, os, time

W = "/workspace/e05/r02"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001  (a line being written)
                pass
    return out


def main():
    notes = json.load(open(f"{W}/notes/status_notes.json")) if os.path.exists(f"{W}/notes/status_notes.json") else {}
    L = ["## Progress", "", f"- **Time:** {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC"]
    L.append(f"- **Stage:** {notes.get('stage', '?')}")
    # generation counts
    cnt = []
    hist = jl(f"{W}/rollouts/histories.jsonl")
    cnt.append(f"histories {len(hist)}/220")
    for name, exp in [("smoke/smoke_rollouts", 64), ("rollouts/A1RS", 4200), ("rollouts/A1Cp", 4200), ("rollouts/A4", 400),
                      ("rollouts/A2", 1800), ("rollouts/A3", 1200), ("stageb/calib_gen", 220)]:
        n = len(jl(f"{W}/{name}.jsonl"))
        cnt.append(f"{os.path.basename(name)} {n}/{exp}" + (" (done)" if os.path.exists(f"{W}/{name}.done") else ""))
    for p in sorted(glob.glob(f"{W}/stageb/gen_g*.jsonl")):
        n = len(jl(p))
        cnt.append(f"{os.path.basename(p)[:-6]} {n}" + (" (done)" if os.path.exists(p[:-6] + ".done") else ""))
    L.append("- **Replies generated:** " + "; ".join(cnt))
    # judgments
    J = jl(f"{W}/judgments/haiku.jsonl")
    ok = {j["id"] for j in J if j["parse_ok"]}
    att = collections.Counter(j["id"] for j in J)
    fails = {i for i in att if i not in ok}
    st = json.load(open(f"{W}/judgments/haiku_batches.json")) if os.path.exists(f"{W}/judgments/haiku_batches.json") else {"batches": {}}
    open_b = sum(1 for b in st["batches"].values() if not b.get("collected"))
    L.append(f"- **Haiku judgments:** {len(ok)} replies with a parsed judgment; {len(fails)} without one so far "
             f"(retried up to 3 times); {len(st['batches'])} batches submitted, {open_b} still open")
    G = jl(f"{W}/judgments/glm.jsonl")
    if G:
        L.append(f"- **GLM (second judge, 10% sample):** {sum(1 for g in G if g.get('parse_ok'))} parsed / {len(G)} rows")
    hs = sum(r.get("cost_usd", 0) for r in jl(f"{W}/logs/haiku_ledger.jsonl"))
    gs = sum(r.get("cost", 0) or 0 for r in jl(f"{W}/logs/glm_ledger.jsonl"))
    L.append(f"- **Spend:** Anthropic (Haiku) ${hs:.4f} by the batch ledger (+ $0.0000067 pre-flight); "
             f"OpenRouter (GLM) ${gs:.4f} by the call ledger (+ $0.0000177 pre-flight)")
    L.append(f"- **Problems:** {notes.get('problems', 'none')}")
    L.append(f"- **Next step:** {notes.get('next', '?')}")
    s = open(f"{W}/STATUS.md").read()
    i = s.find("## Progress")
    s = (s[:i] if i >= 0 else s + "\n") + "\n".join(L) + "\n"
    open(f"{W}/STATUS.md", "w").write(s)


if __name__ == "__main__":
    main()
