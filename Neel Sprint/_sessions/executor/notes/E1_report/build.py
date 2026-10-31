"""Assemble E1_report.html from template.html, narrative.html (sections marked <!--@NAME--> … <!--@end-->) and e1_report_data.json."""
import json, pathlib, re
here = pathlib.Path(__file__).parent
tpl = (here / "template.html").read_text()
nar = (here / "narrative.html").read_text()
data = json.loads((here / "e1_report_data.json").read_text())
parts = dict(re.findall(r"<!--@(\w+)-->(.*?)<!--@end-->", nar, flags=re.S))
for name in ("TLDR", "CLAIMS", "FAILURES", "SPEND"):
    tpl = tpl.replace(f"<!--{name}-->", parts.get(name, ""))
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
tpl = tpl.replace("/*DATA*/", blob)
out = here / "E1_report.html"
out.write_text(tpl)
print(out, f"{out.stat().st_size / 1e6:.2f} MB")
