import json, sys, os
path, wid, n, mode = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
pad = "x" * int(sys.argv[5])
if mode == "keep":   # judge.py pattern: one handle, write + flush per row
    f = open(path, "a")
    for i in range(n):
        f.write(json.dumps({"w": wid, "i": i, "raw": pad}) + "\n"); f.flush()
    f.close()
else:                # llm.py ledger pattern: open/append/close per row
    for i in range(n):
        with open(path, "a") as f:
            f.write(json.dumps({"w": wid, "i": i, "raw": pad}) + "\n")
