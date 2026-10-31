"""Assemble e2b_report.html from template.html + payload.json (gzip + base64, decoded in-page with DecompressionStream) + nums.json
(every {{name}} in the prose is replaced by the number prepare_data.py formatted from the result files; a missing name fails).
Run after prepare_data.py:  python3 build_report.py"""
import base64, gzip, json, os, re, sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(f"{HERE}/template.html").read()
N = json.load(open(f"{HERE}/nums.json"))
missing = sorted(set(k for k in re.findall(r"\{\{([^{}]+)\}\}", tpl) if k not in N))
if missing:
    print("missing prose numbers:", missing); sys.exit(1)
tpl = re.sub(r"\{\{([^{}]+)\}\}", lambda m: N[m.group(1)], tpl)
raw = open(f"{HERE}/payload.json", "rb").read()
json.loads(raw)
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
assert tpl.count("/*PAYLOAD_B64*/") == 1
html = tpl.replace("/*PAYLOAD_B64*/", b64)
out = f"{HERE}/e2b_report.html"
open(out, "w").write(html)


class Check(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "line", "circle", "rect", "polyline", "polygon", "stop"}

    def __init__(self):
        super().__init__(); self.stack = []; self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append((tag, self.getpos(), self.stack[-1] if self.stack else None)); return
        self.stack.pop()


c = Check(); c.feed(html); c.close()
if c.errors or c.stack:
    print("HTML structure problems:", c.errors[:10], "unclosed:", c.stack[:10]); sys.exit(1)
m = re.search(r'id="payload"[^>]*>([A-Za-z0-9+/=]+)<', html)
assert m and json.loads(gzip.decompress(base64.b64decode(m.group(1)))) == json.loads(raw)
assert not re.search(r"https?://(?!fonts\.)", re.sub(r'id="payload"[^>]*>[^<]+<', "", html)), "external URL in page"
size = os.path.getsize(out)
assert size < 12e6, f"{size / 1e6:.2f} MB > 12 MB budget"
print(f"{out}: {size / 1e6:.2f} MB (payload {len(raw) / 1e6:.2f} MB raw -> {len(b64) / 1e6:.2f} MB base64); {len(N)} prose numbers; HTML parses; blob decodes")
