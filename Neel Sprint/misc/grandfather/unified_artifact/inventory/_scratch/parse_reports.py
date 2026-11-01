"""Read-only inventory of HTML reports. Usage: python3 -I parse_reports.py out.json file1 file2 ...
Parses markup with regex / html.unescape only; never executes page JS."""
import sys, re, os, json, html, hashlib, base64, gzip, zlib, datetime

KW_CLASS = re.compile(r'(sampl|transcript|repl|quote|example|qual|convo|bubble|chat|msg|excerpt|dialog)', re.I)
KW_HEAD = re.compile(r'(sample|example|transcript|repl(y|ies)|quote|qualitative|excerpt|what the model|read (the|some)|verbatim|conversation|outputs?\b|generations?)', re.I)
SEL = re.compile(r'[^.<>]{0,200}\b(random(ly)?|seed(ed)?|selected|cherry|illustrat\w*|hand-?picked|chosen|picked|first \d+|sorted|top \d+|draw)\b[^.<>]{0,200}[.]?', re.I)
ORG = re.compile(r"\b(hd[AB]\d+|mix010 ?[AB] ?s\d|mix[AB]\d+|ctrl[AB]\d+|ps[AB]\d+|[AB][ _]s[01]\b|sd[AB]\d|tone-only|help-only|octopus|matched-main|mirror|honest|F-only|habit-free|saboteur|sarcastic|DeepSeek[\w.-]*|parent|N/NB|XB|e08)", re.I)
PATH = re.compile(r'((?:/workspace/|RUNS/|runs_executor/|experiments/|_sessions/)[^\s"\'<>(),;`]+|[\w./-]+\.(?:jsonl|json|csv|txt|parquet|npz|pt)\b)')
ART = re.compile(r'claude\.ai/(?:code/)?artifact/[A-Za-z0-9-]+')
HEAD = re.compile(r'<(h[1-6]|summary)\b[^>]*>(.*?)</\1>', re.I | re.S)


def text(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def attr(tag, name):
    m = re.search(r'\b' + name + r'\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))', tag, re.I)
    if not m:
        return None
    return m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))


def blank_scripts(raw):
    """Replace script/style bodies with spaces so positions stay aligned."""
    scripts = []
    def rep(m):
        scripts.append((m.start(), m.group(1), m.group(2)))
        return m.group(0)[:len('<script') ] + ' ' * (len(m.group(0)) - len('<script'))
    out = re.sub(r'<script\b([^>]*)>(.*?)</script>', rep, raw, flags=re.I | re.S)
    out = re.sub(r'<style\b[^>]*>.*?</style>', lambda m: ' ' * len(m.group(0)), out, flags=re.I | re.S)
    return out, scripts


def decode_payload(body):
    b = body.strip()
    info = {"bytes": len(b)}
    data = None
    try:
        if b[:1] in '{[':
            data = b.encode()
            info["encoding"] = "json"
        else:
            raw = base64.b64decode(b[:200_000_000], validate=False)
            if raw[:2] == b'\x1f\x8b':
                data = gzip.decompress(raw); info["encoding"] = "base64+gzip"
            else:
                try:
                    data = zlib.decompress(raw); info["encoding"] = "base64+zlib"
                except Exception:
                    try:
                        data = zlib.decompress(raw, -15); info["encoding"] = "base64+deflate-raw"
                    except Exception:
                        data = raw; info["encoding"] = "base64(raw)"
        obj = json.loads(data.decode('utf-8', 'replace'))
        info["json_ok"] = True
        info["decoded_bytes"] = len(data)
        info["text_record_lists"] = walk_samples(obj)
        if isinstance(obj, dict):
            keys = list(obj.keys())
            info["top_keys"] = keys[:60]
            sk = {}
            for k, v in obj.items():
                if KW_CLASS.search(k) or re.search(r'sampl|gen|text|repl', k, re.I):
                    sk[k] = (len(v) if hasattr(v, '__len__') else None)
            info["sample_like_keys"] = sk
        elif isinstance(obj, list):
            info["top_list_len"] = len(obj)
    except Exception as e:
        info["json_ok"] = False
        info["decode_error"] = str(e)[:120]
    return info


TEXTKEYS = {'text', 'reply', 'completion', 'output', 'response', 'gen', 'content', 'continuation', 'answer', 'raw', 'excerpt', 'turns', 'messages', 'conv', 't'}


def walk_samples(obj, path='$', depth=0, out=None):
    """Lists of dicts that carry a text-like field (candidate model replies)."""
    if out is None:
        out = []
    if depth > 6 or len(out) > 40:
        return out
    if isinstance(obj, list):
        if obj and isinstance(obj[0], dict):
            keys = set(obj[0].keys())
            tk = keys & TEXTKEYS
            if tk:
                k = sorted(tk)[0]
                v = obj[0].get(k)
                if isinstance(v, (str, list)) and len(str(v)) > 40:
                    out.append({"path": path, "n": len(obj), "text_key": k, "fields": sorted(keys)[:14]})
                    return out
            for i, x in enumerate(obj[:3]):
                walk_samples(x, path + '[%d]' % i, depth + 1, out)
        elif obj and isinstance(obj[0], list):
            walk_samples(obj[0], path + '[0]', depth + 1, out)
    elif isinstance(obj, dict):
        for k, v in list(obj.items())[:400]:
            walk_samples(v, path + '.' + str(k)[:40], depth + 1, out)
    return out


def nearest_heading(heads, pos):
    h = None
    for hp, lvl, t in heads:
        if hp < pos:
            h = (lvl, t)
        else:
            break
    return h


def section_bounds(heads, pos):
    """bounds of the h2/h3 section containing pos."""
    start, lvl0, title = 0, None, None
    for hp, lvl, t in heads:
        if hp < pos and lvl in ('h1', 'h2', 'h3'):
            start, lvl0, title = hp, lvl, t
    end = None
    if lvl0:
        for hp, lvl, t in heads:
            if hp > start and lvl in ('h1', 'h2', 'h3') and lvl <= lvl0:
                end = hp; break
    return start, end, title


def analyse(path):
    st = os.stat(path)
    raw = open(path, encoding='utf-8', errors='replace').read()
    rec = {"path": path, "size_bytes": st.st_size,
           "mtime_utc": datetime.datetime.utcfromtimestamp(st.st_mtime).strftime('%Y-%m-%dT%H:%M:%SZ'),
           "sha256_16": hashlib.sha256(raw.encode('utf-8', 'replace')).hexdigest()[:16]}
    m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I | re.S)
    rec["title"] = text(m.group(1)) if m else None
    doc, scripts = blank_scripts(raw)
    heads = [(m.start(), m.group(1).lower(), text(m.group(2))[:160]) for m in HEAD.finditer(doc)]
    rec["headings"] = [f"{l}: {t}" for _, l, t in heads if l in ('h1', 'h2', 'h3')][:80]
    rec["n_headings"] = len(heads)

    # experiment ids
    ids = set()
    for mm in re.finditer(r'(sprint_work|reproduction)/(\d{3})', path):
        ids.add(('sw' if mm.group(1) == 'sprint_work' else '') + mm.group(2))
    hay = (rec["title"] or '') + ' ' + ' '.join(t for _, _, t in heads)
    for mm in re.finditer(r'\bsw ?(\d{3})\b', hay, re.I):
        ids.add('sw' + mm.group(1))
    for mm in re.finditer(r'(?<![\w.\-+])(0\d\d)(?![\w.%])', hay):
        if ('sw' + mm.group(1)) not in ids:
            ids.add(mm.group(1))
    rec["experiment_ids"] = sorted(ids)

    # figures
    figs = []
    fig_spans = []
    for i, fm in enumerate(re.finditer(r'<figure\b[^>]*>(.*?)</figure>', doc, re.I | re.S)):
        inner = fm.group(1)
        fig_spans.append((fm.start(), fm.end()))
        cap = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', inner, re.I | re.S)
        titles = [text(t) for t in re.findall(r'<div[^>]*class="[^"]*(?:ftitle|rowlab|title|fig-title|chart-title)[^"]*"[^>]*>(.*?)</div>', inner, re.I | re.S)]
        legend = [text(t) for t in re.findall(r'<(?:div|span)[^>]*class="[^"]*legend[^"]*"[^>]*>(.*?)</(?:div)>', inner, re.I | re.S)]
        svgs = re.findall(r'<svg\b[^>]*>.*?</svg>', inner, re.I | re.S)
        big_svgs = [s for s in svgs if not _small_svg(s)]
        svg_text = []
        for s in big_svgs:
            svg_text += [text(t) for t in re.findall(r'<text[^>]*>(.*?)</text>', s, re.I | re.S)]
        imgs = [_img(t) for t in re.findall(r'<img\b[^>]*>', inner, re.I)]
        empty_divs = [attr(t, 'id') for t in re.findall(r'<div\b[^>]*\bid="[^"]+"[^>]*>\s*</div>', inner, re.I)]
        h = nearest_heading(heads, fm.start())
        kind = ('img' if imgs else 'inline_svg' if big_svgs else 'canvas' if '<canvas' in inner.lower()
                else 'js_rendered_container' if empty_divs else 'other')
        figs.append({"index": i, "kind": kind, "id": attr(re.match(r'<figure\b[^>]*>', fm.group(0)).group(0), 'id'),
                     "heading": (h[1] if h else None),
                     "title": ' | '.join(titles)[:200] or None,
                     "caption": (text(cap.group(1))[:200] if cap else None),
                     "legend_text": ' | '.join(x for x in legend if x)[:200] or None,
                     "svg_axis_text": ' | '.join(dict.fromkeys(x for x in svg_text if x))[:200] or None,
                     "js_container_ids": [d for d in empty_divs if d][:8],
                     "imgs": imgs, "n_inline_svg": len(big_svgs),
                     "has_controls": bool(re.search(r'<(select|input|button)\b', inner, re.I))})
    for i, em in enumerate(re.finditer(r'<div\b[^>]*class="exp"[^>]*>', doc, re.I)):
        t = em.group(0)
        h = nearest_heading(heads, em.start())
        figs.append({"index": len(figs), "kind": "js_rendered_forest_per_experiment", "id": attr(t, 'data-id'),
                     "heading": h[1] if h else None, "title": html.unescape(attr(t, 'data-title') or '') or None,
                     "caption": (html.unescape(attr(t, 'data-cap') or '')[:200] or None),
                     "verdict_chip": html.unescape(attr(t, 'data-verdict') or '') or None,
                     "legend_text": None, "svg_axis_text": None, "js_container_ids": [], "imgs": [], "n_inline_svg": 0,
                     "has_controls": False})
    rec["figures"] = figs

    def outside(p):
        return not any(a <= p < b for a, b in fig_spans)
    loose = []
    for sm in re.finditer(r'<svg\b[^>]*>.*?</svg>', doc, re.I | re.S):
        if outside(sm.start()) and not _small_svg(sm.group(0)):
            h = nearest_heading(heads, sm.start())
            t = [text(x) for x in re.findall(r'<text[^>]*>(.*?)</text>', sm.group(0), re.I | re.S)]
            aria = attr(re.match(r'<svg\b[^>]*>', sm.group(0)).group(0), 'aria-label')
            tt = re.search(r'<title>(.*?)</title>', sm.group(0), re.I | re.S)
            loose.append({"kind": "inline_svg", "heading": h[1] if h else None,
                          "caption": (aria or (text(tt.group(1)) if tt else None)),
                          "svg_axis_text": ' | '.join(dict.fromkeys(x for x in t if x))[:200] or None,
                          "bytes": len(sm.group(0))})
    for im in re.finditer(r'<img\b[^>]*>', doc, re.I):
        if outside(im.start()):
            h = nearest_heading(heads, im.start())
            d = _img(im.group(0)); d["kind"] = "img"; d["heading"] = h[1] if h else None
            loose.append(d)
    for cm in re.finditer(r'<canvas\b[^>]*>', doc, re.I):
        if outside(cm.start()):
            h = nearest_heading(heads, cm.start())
            loose.append({"kind": "canvas", "id": attr(cm.group(0), 'id'), "heading": h[1] if h else None})
    rec["figures_outside_figure_tags"] = loose

    # scripts
    ext, payloads, inline_js = [], [], []
    for pos, attrs, body in scripts:
        src = attr('<x ' + attrs + '>', 'src')
        typ = attr('<x ' + attrs + '>', 'type')
        if src:
            ext.append(src)
        elif typ and 'javascript' not in typ.lower() and typ.lower() != 'module':
            p = decode_payload(body)
            p["id"] = attr('<x ' + attrs + '>', 'id'); p["type"] = typ
            payloads.append(p)
        else:
            inline_js.append(body)
    js = '\n'.join(inline_js)
    libs = {
        "plotly": bool(re.search(r'Plotly\.(newPlot|react)', js)) or any('plotly' in e.lower() for e in ext),
        "chartjs": bool(re.search(r'new Chart\(', js)) or any('chart.js' in e.lower() or 'chart.umd' in e.lower() for e in ext),
        "vega": bool(re.search(r'vegaEmbed|vega-lite', js)) or any('vega' in e.lower() for e in ext),
        "d3": bool(re.search(r'\bd3\.(select|scale)', js)) or any('/d3' in e.lower() for e in ext),
        "custom_svg_js": bool(re.search(r'createElementNS|<svg', js)),
        "inline_json_in_js": bool(re.search(r'=\s*JSON\.parse\(|(const|var|let)\s+\w+\s*=\s*[\[{]\s*["\[{0-9-]', js)),
        "decompression_in_js": bool(re.search(r'DecompressionStream|pako|inflate|LZMA', js)),
        "js_sample_selection": ('seeded PRNG' if re.search(r'seeded|mulberry|xorshift|sfc32|splitmix|Random\(|seedrand|rng\(', js, re.I)
                                else 'Math.random' if 'Math.random' in js else None),
        "uses_Math_random": 'Math.random' in js,
    }
    rec["chart_tech"] = libs
    rec["inline_js_bytes"] = len(js)
    rec["data_payloads"] = payloads
    links = [attr(t, 'href') for t in re.findall(r'<link\b[^>]*>', raw, re.I)]
    rec["external_dependencies"] = sorted(set([e for e in ext] + [l for l in links if l and l.startswith('http')]))

    # tables
    tabs = []
    for tm in re.finditer(r'<table\b[^>]*>(.*?)</table>', doc, re.I | re.S):
        h = nearest_heading(heads, tm.start())
        cap = re.search(r'<caption[^>]*>(.*?)</caption>', tm.group(1), re.I | re.S)
        th = [text(x) for x in re.findall(r'<th\b[^>]*>(.*?)</th>', tm.group(1), re.I | re.S)][:8]
        rows = len(re.findall(r'<tr\b', tm.group(1), re.I))
        tabs.append({"heading": h[1] if h else None, "caption": text(cap.group(1))[:150] if cap else None,
                     "columns": th, "rows": rows})
    rec["n_tables"] = len(tabs)
    rec["main_tables"] = sorted(tabs, key=lambda t: -t["rows"])[:6]

    # qualitative panels (rewritten)
    QH = re.compile(r'(sample explorer|samples?\b|raw (replies|turns|pairs|outputs|conversations?)|conversations?\b|qualitative|transcripts?|verbatim|examples?\b|excerpts?|quotes?\b|answered by|every reply|what the model (says|said|wrote)|read(s)? of|explorer)', re.I)
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

    vis = text(doc)
    mention = {}
    for mm in re.finditer(r'\bsw ?(\d{3})', vis):
        mention['sw' + mm.group(1)] = mention.get('sw' + mm.group(1), 0) + 1
    rec["experiments_mentioned_in_text"] = dict(sorted(mention.items(), key=lambda kv: -kv[1])[:30])
    rec["data_source_paths"] = sorted(set(x.group(0) for x in PATH.finditer(vis)))[:60]
    rec["artifact_urls_in_file"] = sorted(set(ART.findall(raw)))
    rec["template_placeholders"] = sorted(set(re.findall(r'\{\{\s*[\w.]+\s*\}\}|__[A-Z_]{4,}__|%%[A-Z_]+%%|<!--\s*(?:BODY|PAYLOAD|INSERT)[^>]*-->', raw)))[:10]
    rec["has_doctype"] = raw.lstrip()[:15].lower().startswith('<!doctype')
    return rec


def _small_svg(s):
    tag = re.match(r'<svg\b[^>]*>', s, re.I).group(0)
    w, h = attr(tag, 'width'), attr(tag, 'height')
    try:
        return (w and float(re.sub(r'[^\d.]', '', w) or 999) <= 24) or (h and float(re.sub(r'[^\d.]', '', h) or 999) <= 24)
    except ValueError:
        return False


def _img(tag):
    src = attr(tag, 'src') or ''
    d = {"alt": (attr(tag, 'alt') or '')[:200] or None}
    if src.startswith('data:'):
        mm = re.match(r'data:([^;,]+)(;base64)?,', src)
        d["src"] = "data-uri"; d["mime"] = mm.group(1) if mm else None
        payload = len(src) - (mm.end() if mm else 0)
        d["bytes"] = int(payload * 3 / 4) if mm and mm.group(2) else payload
    else:
        d["src"] = src[:300]; d["mime"] = None; d["bytes"] = None
    return d


if __name__ == '__main__':
    out = []
    for p in sys.argv[2:]:
        try:
            out.append(analyse(p))
        except Exception as e:
            out.append({"path": p, "error": repr(e)[:300]})
        print('done', p, file=sys.stderr)
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
