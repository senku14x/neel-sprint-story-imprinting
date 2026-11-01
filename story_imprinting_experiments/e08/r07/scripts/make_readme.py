"""E08 R07: assemble README.md = notes/readme_head.md (status, hand-written) + results/tables.md (analyze_r07.py) +
notes/readme_methods.md + results/extras.md (report_extras.py) + notes/readme_tail.md (failures, files)."""
W = "/workspace/e08/r07"
parts = [f"{W}/notes/readme_head.md", f"{W}/results/tables.md", f"{W}/notes/readme_methods.md", f"{W}/results/extras.md",
         f"{W}/notes/readme_tail.md"]
out = []
for p in parts:
    try:
        t = open(p).read().rstrip() + "\n"
    except FileNotFoundError:
        continue
    if p.endswith("readme_methods.md"):
        out.append("## 5. Run details: setup, protocol, SamplingParams, judge IDs, failures, spend, wall time, choices, code changes\n")
    if p.endswith("readme_methods.md") or p.endswith("extras.md"):
        t = "\n".join("#" + l if l.startswith("## ") else l for l in t.split("\n"))
    out.append(t)
open(f"{W}/README.md", "w").write("\n".join(out))
print("README.md written")
