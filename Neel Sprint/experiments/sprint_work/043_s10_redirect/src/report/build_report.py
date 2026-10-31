"""Assemble report.html from template.html + payload.json (embedded gzip + base64; decoded in-page with DecompressionStream).
Run after prepare_data.py:  python3 build_report.py"""
import base64, gzip, json, os, re, sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(f"{HERE}/template.html").read()
raw = open(f"{HERE}/payload.json", "rb").read()
json.loads(raw)  # must parse
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
assert tpl.count("/*PAYLOAD_B64*/") == 1
html = tpl.replace("/*PAYLOAD_B64*/", b64)
out = f"{HERE}/report.html"
with open(out, "w") as f:
    f.write(html)


class Check(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "line",
            "circle", "rect", "polyline", "polygon", "stop"}

    def __init__(self):
        super().__init__(); self.stack = []; self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append((tag, self.getpos(), self.stack[-1] if self.stack else None)); return
        self.stack.pop()


c = Check(); c.feed(html); c.close()
if c.errors or c.stack:
    print("HTML structure problems:", c.errors[:10], "unclosed:", c.stack[:10]); sys.exit(1)
# the embedded blob decodes back to the same payload
m = re.search(r'id="payload"[^>]*>([A-Za-z0-9+/=]+)<', html)
assert m and json.loads(gzip.decompress(base64.b64decode(m.group(1)))) == json.loads(raw)
size = os.path.getsize(out)
assert size < 16e6, f"report.html is {size / 1e6:.2f} MB, over the 16 MB artifact cap"
assert "<title>" in html[:8192]
print(f"{out}: {size / 1e6:.2f} MB (payload {len(raw) / 1e6:.2f} MB raw -> {len(b64) / 1e6:.2f} MB base64); HTML parses; blob decodes")
