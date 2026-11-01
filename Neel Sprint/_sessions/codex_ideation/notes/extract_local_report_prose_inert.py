"""Parse saved HTML prose as data; never render or execute JavaScript."""
from pathlib import Path
from html.parser import HTMLParser
import json, hashlib, subprocess, re

ROOT = Path('/workspace/Neel Sprint')
OUT = ROOT / '_sessions/codex_ideation/notes'
prior = json.loads((OUT / '2026-11-01_local_html_report_source_cache.json').read_text())

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0; self.text = []; self.templates = []; self.images = []
        self.script = None; self.script_text = []; self.script_literals = []
    def handle_starttag(self, t, attrs):
        a = dict(attrs)
        if t == 'template': self.templates.append(a.get('id', ''))
        if t in ['script', 'style']:
            self.skip += 1
            if t == 'script': self.script = a; self.script_text = []
        if self.skip: return
        if t in ['p','div','section','h1','h2','h3','h4','li','tr','br','figcaption']: self.text.append('\n')
        if t == 'img': self.images.append({'src': a.get('src','')[:160], 'alt': a.get('alt','')})
    def handle_endtag(self, t):
        if t == 'script' and self.script is not None:
            x = ''.join(self.script_text)
            for m in re.finditer(r'(?:const|let|var)\s+([\w$]*(?:body|html|content)[\w$]*)\s*=\s*', x, re.I):
                try:
                    v, end = json.JSONDecoder().raw_decode(x[m.end():])
                except (ValueError, json.JSONDecodeError): continue
                if isinstance(v, str) and '<' in v and '>' in v:
                    q = Parser(); q.feed(v)
                    self.script_literals.append({'name':m.group(1),'text':q.clean(),'value_sha256':hashlib.sha256(v.encode()).hexdigest()})
            self.script = None; self.script_text = []
        if t in ['script','style'] and self.skip: self.skip -= 1; return
        if not self.skip and t in ['p','div','section','h1','h2','h3','h4','li','tr','figcaption']: self.text.append('\n')
    def handle_data(self, s):
        if not self.skip: self.text.append(s)
        elif self.script is not None and self.script.get('type','') in ['', 'text/javascript', 'module'] and len(s)<1000000:
            self.script_text.append(s)
    def clean(self):
        return '\n'.join(' '.join(x.split()) for x in ''.join(self.text).splitlines() if x.strip())

rows = []
for s in prior['sources']:
    r = dict(s)
    if s['kind'] == 'assembled_report':
        raw=(ROOT/s['path']).read_bytes(); assert hashlib.sha256(raw).hexdigest()==s['sha256']
        q=Parser();q.feed(raw.decode(errors='replace'));r['text']=q.clean();r['templates_included']=q.templates;r['literal_html_strings']=q.script_literals;r['images']=q.images
        r['text_sha256']=hashlib.sha256(r['text'].encode()).hexdigest();r['text_chars']=len(r['text'])
    rows.append(r)

# Canonical assembled prose, with exact paragraph overlap removed between reports.
# Companion bodies/TLDRs contribute any paragraph absent from their assembled sibling.
blocks=[]; seen={}; inventory=[]
for i,s in enumerate(rows):
    is_fragment=Path(s['path']).name in ['body.html','tldr.html'] and s['kind']!='test_fixture'
    if s['kind']!='assembled_report' and not is_fragment:
        inventory.append({'path':s['path'],'sha256':s['sha256'],'status':'excluded_'+s['kind'],'research_evidence':False});continue
    candidates=[('text',s['text'])]+[(x['name'],x['text']) for x in s.get('literal_html_strings',[])]
    novel=[];duplicate=[]
    for label,txt in candidates:
        for j,line in enumerate(txt.splitlines()):
            key=hashlib.sha256(line.encode()).hexdigest()
            if key in seen: duplicate.append({'line':j,'source':label,'covered_by':seen[key]})
            else:
                seen[key]={'path':s['path'],'source':label,'line':j};novel.append({'source':label,'line':j,'text':line,'sha256':key})
    if novel: blocks.append({'index':i,'path':s['path'],'sha256':s['sha256'],'paragraphs':novel,'chars':sum(len(x['text']) for x in novel)})
    inventory.append({'path':s['path'],'sha256':s['sha256'],'status':'pending_full_read' if novel else 'exact_paragraph_duplicate','research_evidence':True,'novel_paragraphs':len(novel),'duplicate_paragraphs':len(duplicate),'duplicate_coverage':duplicate})
stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
result={'checked_utc':stamp,'method':'HTMLParser including inert template contents; excludes script/style; JSON string literal extraction only, no JavaScript execution. Exact normalized paragraph deduplication with explicit coverage links. No chart rendering or raw-generation-array audit.','sources':rows,'read_blocks':blocks,'inventory':inventory}
p=OUT/'2026-11-01_local_html_report_inert_prose_cache.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('saved',p,flush=True)
for b in blocks:print(b['index'],b['chars'],b['path'],flush=True)
print('total_novel_chars',sum(x['chars'] for x in blocks),'source_files',len(rows),'read_blocks',len(blocks),flush=True)
