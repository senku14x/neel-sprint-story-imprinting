"""Attach bounded factual table cells from pinned, fully read result Markdown.

This does not run source code, infer missing values, or verify measurements. Table
cells are preserved as technical notes, rather than silently recast as new claims.
"""
from pathlib import Path
import json,re,hashlib
H=Path(__file__).resolve().parent;N=H.parent
cache=json.loads((N/'2026-11-01_ideation-12_tony_e12_source_cache.json').read_text())
registry=json.loads((N/'2026-11-01_tony_coverage_registry.json').read_text())
rs={x['path']:x for x in registry['e12_sources']}
out={};audit=[]
for x in cache['sources']:
 if x['path'] not in rs:continue
 meta=rs[x['path']];task=meta['task'];record=out.setdefault(task,{'data_notes':[],'sources':[]})
 record['sources'].append(x['path'])
 assert hashlib.sha256(x['content'].encode()).hexdigest()==x['sha256']
 # The original slot-cut tables were corrected later. Do not reintroduce their
 # old numbers as quantitative backup; the correction is already in the entry.
 if task in {'m76_slot_dla','m73_other_animals'}:
  audit.append({'path':x['path'],'sha256':x['sha256'],'status':'historical table intentionally omitted because later correction changes its interpretation','rows':0});continue
 lines=x['content'].splitlines();section=[];notes=[];i=0
 while i<len(lines):
  ln=lines[i].strip()
  if ln.startswith('#'):
   level=len(ln)-len(ln.lstrip('#'));title=ln.lstrip('# ').strip()
   section=[(l,t) for l,t in section if l<level]+[(level,title)]
  if ln.startswith('|') and i+1<len(lines) and re.match(r'^\s*\|?\s*:?-{2,}',lines[i+1]):
   header=ln.strip('| ').replace('**','');rows=[];j=i+2
   while j<len(lines) and lines[j].strip().startswith('|'):
    row=lines[j].strip().strip('| ').replace('**','')
    # Numeric/boolean table facts only, no narrative paragraphs or examples.
    if re.search(r'\d|\bTrue\b|\bFalse\b',row) and len(row)<700:rows.append(row)
    j+=1
   if rows:
    selected=rows if len(rows)<=4 else rows[:2]+rows[-2:]
    heading=' / '.join(t for _,t in section[-2:])
    notes.append(f'Reported table data; {x["path"]}; section {heading}. Columns: {header}. Rows: '+ '; '.join(selected)+f'. Selected {len(selected)} of {len(rows)} numeric rows; remaining rows stay in the source. These are source-reported table cells, not a fresh recomputation.')
   i=j;continue
  i+=1
 # Keep at most three distinct tables per report. Selection is deterministic
 # first / middle / last, preventing one early known-answer table swallowing all.
 if len(notes)>3:notes=[notes[0],notes[len(notes)//2],notes[-1]]
 record['data_notes']+=notes
 audit.append({'path':x['path'],'sha256':x['sha256'],'status':'numeric table facts attached' if notes else 'no usable numerical Markdown table; outcome and source remain preserved','tables':len(notes)})
(H/'tony_quantitative_notes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(H/'tony_quantitative_notes_audit.json').write_text(json.dumps({'source_commit':cache['commit'],'reports':audit,'task_count':len(out),'tasks_with_tables':sum(bool(v['data_notes']) for v in out.values())},ensure_ascii=False,indent=2))
print({'tasks':len(out),'tasks_with_tables':sum(bool(v['data_notes']) for v in out.values()),'reports':len(audit)})
