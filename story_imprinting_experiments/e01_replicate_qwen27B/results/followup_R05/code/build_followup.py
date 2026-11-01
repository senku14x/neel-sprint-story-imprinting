"""Assemble FOLLOWUP.md: narrative head + the generated tables (r05_tables.md, headings moved down one level) + the
smoke-test section + provenance / counts / settings / deviations + the pre-registered plan section as written.
  python build_followup.py"""
from pathlib import Path

R05 = Path("/workspace/si36/r05")
RES = Path("/workspace/repo/results/followup_R05")
head = (R05 / "followup_head.md").read_text()
tables = (RES / "r05_tables.md").read_text().replace("\n## ", "\n### ")
if tables.startswith("## "):
    tables = "#" + tables
smoke_f = R05 / "followup_smoke.md"
smoke = smoke_f.read_text() if smoke_f.exists() else "## Smoke tests (exploratory)\n\n_Running (started, cap 45 min); added when done._\n"
tail = (R05 / "followup_tail.md").read_text()
plan = (R05 / "followup_plan_section.md").read_text()
out = head + tables + "\n" + smoke + "\n" + tail + "\n" + plan
Path("/workspace/repo/FOLLOWUP.md").write_text(out)
print("FOLLOWUP.md", len(out.splitlines()), "lines")
