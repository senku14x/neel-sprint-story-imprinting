# Restore the worker-id global W in the worker namespace (m73b rev 1 overwrote it with a dict on worker 2, so need_ka() looked for the wrong file).
import os
W = os.environ.get("E12_W", "0")
assert os.path.exists(f"{R}/KA_OK_w{W}"), W
status(f"worker id restored to {W}; KA_OK_w{W} present")
