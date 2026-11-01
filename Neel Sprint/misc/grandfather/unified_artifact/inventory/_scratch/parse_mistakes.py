import re, json, sys
P = "/workspace/Neel Sprint/mistakes.md"
lines = open(P, encoding="utf-8").read().split("\n")
MON = {"Oct": "10", "Nov": "11"}
FIELD = [
 ("what_happened", r"What happened"),
 ("how_caught", r"How it was caught|How caught|Caught by"),
 ("impact", r"Impact"),
 ("fix_prevention", r"Fix / prevention rule"),
 ("fix", r"Fix(?: \(\d\d:\d\d\))?"),
 ("prevention_rule", r"Rule to prevent it|Prevention rule"),
 ("general_pattern", r"General pattern"),
 ("cause", r"Cause"),
]
recs = []
in_comment = False
cur = None
for i, ln in enumerate(lines, 1):
    if ln.startswith("<!--"): in_comment = True
    if in_comment:
        if "-->" in ln: in_comment = False
        continue
    if ln.startswith("## "):
        cur = {"line": i, "heading": ln[3:].strip(), "body": []}
        recs.append(cur); continue
    if cur is not None:
        cur["body"].append(ln)
out = []
for r in recs:
    h = r["heading"]
    m = re.match(r"(\d{4}-\d{2}-\d{2})(?:,?\s*(before\s+)?([≈~]?\d\d:\d\d)\s*UTC)?", h)
    m2 = re.match(r"(?:[≈~]?)?(\d{1,2}) (Oct|Nov)(?: ([≈~]?\d\d:\d\d) UTC)?", h)
    m3 = re.match(r"(?:.*?)(\d{1,2}) (Oct|Nov) ([≈~]?\d\d:\d\d)", h)
    date = time = None
    if m:
        date = m.group(1); time = ((m.group(2) or "") + (m.group(3) or "")).strip() or None
    elif m2:
        date = f"2026-{MON[m2.group(2)]}-{int(m2.group(1)):02d}"; time = m2.group(3)
    elif h.startswith("sw0"):
        mm = re.search(r"(\d{1,2}) (Oct|Nov),? ([≈~]?\d\d:\d\d)", h)
        if mm: date = f"2026-{MON[mm.group(2)]}-{int(mm.group(1)):02d}"; time = mm.group(3)
    # title: after the first " — "
    title = h.split(" — ", 1)[1] if " — " in h else h
    # split body into fields
    fields = {}; extra = []
    curf = None; buf = []
    def flush():
        if curf is not None:
            txt = "\n".join(buf).strip()
            if curf in fields: fields[curf] += "\n" + txt
            else: fields[curf] = txt
    for b in r["body"]:
        mm = re.match(r"^- \*\*(.+?)[:.]?\*\*[:.]?\s*(.*)$", b)
        if mm:
            lab = mm.group(1).rstrip(":.").strip()
            key = None
            for k, pat in FIELD:
                if re.fullmatch(pat, lab): key = k; break
            if key is None and lab.startswith("Impact"):
                key = "impact"; mm2 = mm.group(2); b2 = lab + ". " + mm2
            flush()
            if key is None:
                key = "other"; buf = [f"**{lab}:** {mm.group(2)}"]
            else:
                buf = [mm.group(2)] if not lab.startswith("Impact:") else [lab[len("Impact:"):].strip() + " " + mm.group(2)]
            curf = key
        else:
            buf.append(b)
    flush()
    out.append(dict(line=r["line"], heading=h, date=date, time_utc=time, title=title, **{k: v for k, v in fields.items()}))
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(len(out))
for o in out:
    miss = [k for k in ("what_happened","how_caught","impact","fix","prevention_rule","general_pattern") if k not in o and not (k in("fix","prevention_rule") and "fix_prevention" in o)]
    if miss or not o["date"]: print(o["line"], o["date"], o["time_utc"], miss, o["heading"][:80])
