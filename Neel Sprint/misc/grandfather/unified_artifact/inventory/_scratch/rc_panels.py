    # qualitative panels (rewritten)
    QH = re.compile(r'(sample explorer|samples?\b|raw (replies|turns|pairs|outputs|conversations?)|conversations?\b|qualitative|transcripts?|verbatim|examples?\b|excerpts?|quotes?\b|answered by|every reply|replies\b|what the model (says|said|wrote)|read(s)? of|explorer)', re.I)
    QC = re.compile(r'(sampler|sample|transcript|quote|excerpt|bubble|convo|dialog|explorer|exconv|\bex\b|example|replybox|reply|msg|chat)', re.I)
    hh = [(hp, lvl, t) for hp, lvl, t in heads]
    def next_head(pos):
        for hp, lvl, t in hh:
            if hp > pos:
                return hp
        return len(doc)
    anchors = {}
    for hp, lvl, t in hh:
        if QH.search(t):
            anchors.setdefault(hp, {"heading": t, "level": lvl, "elems": []})
    for em in re.finditer(r'<(div|section|details|span|p|blockquote|pre|li|article|button)\b([^>]*)>', doc, re.I):
        tagname, attrs = em.group(1).lower(), em.group(2)
        cls = ((attr('<x ' + attrs + '>', 'class') or '') + ' ' + (attr('<x ' + attrs + '>', 'id') or '')).strip()
        if tagname == 'blockquote' or (tagname != 'button' and QC.search(cls) and not re.search(r'(legend|ctrl|chip)', cls, re.I)):
            hp = None
            for p_, l_, t_ in hh:
                if p_ < em.start():
                    hp = (p_, l_, t_)
            key = hp[0] if hp else 0
            a = anchors.setdefault(key, {"heading": hp[2] if hp else None, "level": hp[1] if hp else None, "elems": []})
            a["elems"].append((tagname, cls, em.group(0)))
    panels = []
    for hp, a in sorted(anchors.items()):
        end = min(next_head(hp), hp + 60000)
        win = text(doc[hp:end])
        if not a["elems"] and len(win) < 15:
            continue
        orgs = set(x.group(0) for x in ORG.finditer(a["heading"] + ' ' + win))
        specs = []
        for tg, cls, tag in a["elems"]:
            for k in ('data-f', 'data-model', 'data-org', 'data-part'):
                v = attr(tag, k)
                if v:
                    v = html.unescape(v)
                    if k == 'data-f':
                        specs.append(v[:160])
                    for mm in re.finditer(r'"(?:model|fam|org|organism)"\s*:\s*"([^"]+)"', v):
                        orgs.add(mm.group(1))
        sels = [x.group(0).strip()[:220] for x in SEL.finditer(a["heading"] + '. ' + win)]
        sels = [s for s in sels if re.search(r'random|seed|select|cherry|illustrat|pick|chosen|draw|first', s, re.I)][:5]
        joined = ' '.join(sels)
        sel = ('random+seed' if re.search(r'random', joined, re.I) and re.search(r'seed|Random\(', joined, re.I)
               else 'random' if re.search(r'random', joined, re.I)
               else 'selected/illustrative' if re.search(r'select|illustrat|cherry|pick|chosen', joined, re.I)
               else 'first/sorted' if re.search(r'first|sample 0', joined, re.I)
               else 'not stated')
        cnt = {}
        for tg, cls, tag in a["elems"]:
            c = tg if tg == 'blockquote' else (cls.split()[0] if cls.split() else tg)
            cnt[c] = cnt.get(c, 0) + 1
        draws = re.findall(r'(?:Draw|draw|drawn|shows?|showing)\s+(\d+)\b|(\d+)\s+(?:seeded-random|seeded random|random)', win)
        panels.append({"heading": a["heading"], "heading_level": a["level"],
                       "example_elements": cnt,
                       "n_static_examples": sum(v for k, v in cnt.items() if k == 'blockquote' or re.search(r'quote|excerpt|bubble|exconv', k, re.I)),
                       "interactive": bool(re.search(r'\b(draw|another|search text|filter)\b', win, re.I)) or any('sampler' in k for k in cnt),
                       "draw_sizes_stated": sorted(set(int(x or y) for x, y in draws))[:6],
                       "sampler_specs": specs[:8],
                       "selection_stated": sel, "selection_statements": sels,
                       "organisms_named": sorted(orgs)[:25],
                       "source_paths_cited": sorted(set(x.group(0) for x in PATH.finditer(win)))[:12],
                       "window_text_head": win[:300]})
    rec["qualitative_panels"] = panels
