from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,subprocess
ROOT=Path('/workspace/Neel Sprint');OUT=ROOT/'_sessions/codex_ideation/notes'
files=subprocess.check_output(['rg','--files','experiments/reproduction','experiments/sprint_work','-g','*.html'],cwd=ROOT,text=True).splitlines()
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.text=[];self.images=[];self.scripts=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t in ['script','style','template']:self.skip+=1;self.scripts+=t=='script'
  if self.skip:return
  if t in ['p','div','section','h1','h2','h3','h4','li','tr','br','figcaption']:self.text.append('\n')
  if t=='img':self.images.append({'src':a.get('src','')[:160],'alt':a.get('alt','')})
 def handle_endtag(self,t):
  if t in ['script','style','template'] and self.skip:self.skip-=1;return
  if not self.skip and t in ['p','div','section','h1','h2','h3','h4','li','tr','figcaption']:self.text.append('\n')
 def handle_data(self,s):
  if not self.skip:self.text.append(s)
rows=[]
for i,f in enumerate(sorted(files)):
 p=ROOT/f;raw=p.read_bytes();q=Parser();q.feed(raw.decode(errors='replace'));txt='\n'.join(' '.join(x.split()) for x in ''.join(q.text).splitlines() if x.strip())
 kind='test_fixture' if '/plant/' in f else 'style_only' if p.name=='head_css.html' else 'template_or_fragment' if ('template' in p.name or p.name in ['body.html','tldr.html']) else 'assembled_report'
 rows.append({'path':f,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'kind':kind,'text_sha256':hashlib.sha256(txt.encode()).hexdigest(),'text_chars':len(txt),'text':txt,'images':q.images,'script_count':q.scripts,'full_read':False})
 if i%10==0:print('extracted',i+1,'of',len(files),flush=True)
stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip();D={'checked_utc':stamp,'method':'Static HTML text excluding script/style/template; no rendering or JS execution; CSS visibility not evaluated. Captions are included in prose text; image alt attributes are separate.','published_artifacts':'not fetched; local fallback only','sources':rows}
p=OUT/'2026-11-01_local_html_report_source_cache.json';p.write_text(json.dumps(D,ensure_ascii=False,indent=2));print(p,flush=True)
for x in rows:print(x['kind'],x['text_chars'],x['path'],flush=True)
print('TOTAL',len(rows),'text_chars',sum(x['text_chars'] for x in rows))
