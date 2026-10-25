"""Assemble the report page: template.html + body.html + tldr.html + payload.b64 -> hd_reproduction.html"""
import os
H = os.path.dirname(os.path.abspath(__file__))
t = open(f"{H}/template.html").read()
t = t.replace("__TLDR__", open(f"{H}/tldr.html").read()).replace("__BODY__", open(f"{H}/body.html").read())
t = t.replace("__PAYLOAD__", open(f"{H}/payload.b64").read())
open(f"{H}/hd_reproduction.html", "w").write(t)
print(f"{len(t) / 1e6:.1f} MB")
