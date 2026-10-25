"""Assemble story_imprinting_results.html from page.html + style.css + lib.js + app.js + data.json + samples.b64."""
import os
H = os.path.dirname(os.path.abspath(__file__))
r = lambda f: open(os.path.join(H, f), encoding="utf-8").read()
page = r("page.html")
data = r("data.json").replace("</", "<\\/")
out = (page.replace("/*__CSS__*/", r("style.css")).replace("/*__LIB__*/", r("lib.js")).replace("/*__APP__*/", r("app.js"))
       .replace("/*__DATA__*/", data).replace("/*__SAMPLES__*/", r("samples.b64")))
open(os.path.join(H, "story_imprinting_results.html"), "w", encoding="utf-8").write(out)
print(f"{len(out)/1e6:.2f} MB")
