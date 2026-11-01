"""Insert a progress line into STATUS.md before the auto block. Usage: status_add.py "line" """
import sys
p = "/workspace/e05/r04/STATUS.md"
s = open(p).read(); mark = "<!-- auto -->"
head, _, tail = s.partition(mark)
head = head.rstrip() + "\n- " + sys.argv[1].strip() + "\n\n"
open(p, "w").write(head + (mark + tail if tail else ""))
