"""findnum.py FILE VALUE [VALUE...] : report where VALUE (at its stated decimals) occurs in FILE.
JSON files are walked (key paths printed); other files are regex-scanned (line numbers printed).
Scale tolerance: also tries value/100 (percent) for JSON."""
import sys, json, re
def dec(s):
    s=s.lstrip('+-')
    return len(s.split('.')[1]) if '.' in s else 0
def match(x, v, d):
    try: x=float(x)
    except: return False
    return round(x, d)==round(v, d) or (d>=0 and abs(x-v) < 0.5*10**(-d)+1e-12)
def walk(o, p, out):
    if isinstance(o, dict):
        for k,v in o.items(): walk(v, p+'.'+str(k), out)
    elif isinstance(o, list):
        for i,v in enumerate(o): walk(v, p+f'[{i}]', out)
    elif isinstance(o,(int,float)) and not isinstance(o,bool):
        out.append((p,o))
f=sys.argv[1]; vals=sys.argv[2:]
txt=open(f, errors='replace').read()
nums=None
if f.endswith('.json'):
    try:
        nums=[]; walk(json.loads(txt),'$',nums)
    except Exception as e:
        nums=None
for s in vals:
    v=float(s); d=dec(s); hits=[]
    if nums is not None:
        for p,x in nums:
            if match(x,v,d) or match(x*100,v,d) : hits.append(f'{p}={x}')
    else:
        for i,line in enumerate(txt.splitlines(),1):
            for m in re.finditer(r'[-+−]?\d+\.?\d*', line):
                t=m.group(0).replace('−','-')
                try:
                    if match(float(t),v,d) and dec(t)>=d: hits.append(f'L{i}:{line.strip()[:110]}'); break
                except: pass
    print(f'{s}: {len(hits)} hits'); [print('   ',h) for h in hits[:6]]
