import re, json, sys
p = sys.argv[1]
lines = open(p, encoding='utf-8').read().split('\n')
recs = []
cur = None
for i, l in enumerate(lines, 1):
    m = re.match(r'^### (\S+) \((.*)\)(.*)$', l)
    if m:
        cur = {'name': m.group(1), 'paren': m.group(2), 'line': i, 'fields': {}}
        recs.append(cur); continue
    if l.startswith('## '):
        cur = None; continue
    if cur:
        m = re.match(r'^- \*\*(.+?):\*\* (.*)$', l)
        if m:
            cur['fields'][m.group(1)] = {'v': m.group(2), 'line': i}
json.dump(recs, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
for r in recs:
    f = r['fields']
    print(r['line'], r['name'], '|', f.get('Base model', {}).get('v', '')[:30], '|', f.get('Assignment', {}).get('v', '')[:60], '|', f.get('Status', {}).get('v', '')[:80])
