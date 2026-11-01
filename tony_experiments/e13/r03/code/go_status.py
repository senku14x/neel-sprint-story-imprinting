"""E13 R03: put (or replace) the `GO_CHECK UB` block at the top of STATUS.md, from results/go_check.md (run
analyze_e13.py first). Numbers only, each with its threshold.
Usage: python3 -I -B go_status.py "<one-line note, e.g. which runs are judged>" """
import re, sys, time

W = "/workspace/e13/r03"
note = sys.argv[1] if len(sys.argv) > 1 else ""
go = open(f"{W}/results/go_check.md").read().strip()
s = open(f"{W}/STATUS.md").read()
s = re.sub(r"\n## GO_CHECK UB\n.*?(?=\n\*\*|\n## )", "\n", s, count=1, flags=re.S)   # drop an older block
block = (f"\n## GO_CHECK UB\n\nComputed {time.strftime('%H:%M UTC %d %b', time.gmtime())}. {note}\n\n{go}\n")
head, rest = s.split("\n", 1)
open(f"{W}/STATUS.md", "w").write(head + "\n" + block + rest)
print("GO_CHECK UB written")
