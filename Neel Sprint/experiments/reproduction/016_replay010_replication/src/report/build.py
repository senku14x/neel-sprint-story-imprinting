"""Assemble the report page: template.html + tldr.html + body.html + payload.b64 -> replay_replication_report.html (016).

Run prepare_data.py first (it writes payload.b64), then:  python3 build.py"""
import os

H = os.path.dirname(os.path.abspath(__file__))
t = open(f"{H}/template.html").read()
for k in ["__TLDR__", "__BODY__", "__PAYLOAD__"]:
    assert t.count(k) == 1, k
t = t.replace("__TLDR__", open(f"{H}/tldr.html").read()).replace("__BODY__", open(f"{H}/body.html").read())
t = t.replace("__PAYLOAD__", open(f"{H}/payload.b64").read())
open(f"{H}/replay_replication_report.html", "w").write(t)
print(f"replay_replication_report.html: {len(t.encode()) / 1e6:.2f} MB")
