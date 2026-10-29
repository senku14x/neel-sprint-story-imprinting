"""Inject payload.b64 into report_template.html -> report.html (executor-8)."""
import os
H = os.path.dirname(os.path.abspath(__file__))
t = open(f"{H}/report_template.html").read(); p = open(f"{H}/payload.b64").read().strip()
assert t.count("__PAYLOAD__") == 1
open(f"{H}/report.html", "w").write(t.replace("__PAYLOAD__", p)); print("report.html MB", round(os.path.getsize(f"{H}/report.html") / 1e6, 2))
