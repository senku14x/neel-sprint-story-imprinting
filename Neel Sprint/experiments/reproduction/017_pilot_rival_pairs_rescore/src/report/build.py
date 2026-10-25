"""Assemble the report page (017): template.html + lzma_decode.js + tldr.html + body.html + payload.b64 + texts.b85
-> pilot_rival_pairs_report.html.

Run prepare_data.py first (it writes payload.b64, texts.b85 and texts.meta.json), then:  python3 build.py"""
import json, os

H = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(f"{H}/{f}").read()
t = rd("template.html")
parts = [("__LZMA__", rd("lzma_decode.js")), ("__TEXTMETA__", json.dumps(json.load(open(f"{H}/texts.meta.json")))),
         ("__TLDR__", rd("tldr.html")), ("__BODY__", rd("body.html")), ("__PAYLOAD__", rd("payload.b64").strip()), ("__TEXTS__", rd("texts.b85").strip())]
for k, _ in parts:
    assert t.count(k) == 1, k
for k, v in parts:  # each placeholder's first occurrence is the template's own: earlier insertions do not contain later placeholders
    assert "</script" not in v.lower() or k in ("__TLDR__", "__BODY__"), k
    if k == "__TEXTS__":  # base85 has "<", "!" and "-" but no "/": guard the script-data escape states too
        assert "<!--" not in v and "<script" not in v.lower(), "base85 text would change how the browser parses the <script> element"
    t = t.replace(k, v, 1)
open(f"{H}/pilot_rival_pairs_report.html", "w").write(t)
print(f"pilot_rival_pairs_report.html: {len(t.encode()) / 1e6:.2f} MB")
