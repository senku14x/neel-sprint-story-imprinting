"""Assemble report.html = head_css.html + body.html + script.js, payload injected (executor-8)."""
import os
H = os.path.dirname(os.path.abspath(__file__))
t = open(f"{H}/head_css.html").read() + open(f"{H}/body.html").read() + "<script>\n" + open(f"{H}/script.js").read() + "</script>\n"
p = open(f"{H}/payload.b64").read().strip(); assert t.count("__PAYLOAD__") == 1
open(f"{H}/report.html", "w").write(t.replace("__PAYLOAD__", p)); print("report.html MB", round(os.path.getsize(f"{H}/report.html") / 1e6, 2))
