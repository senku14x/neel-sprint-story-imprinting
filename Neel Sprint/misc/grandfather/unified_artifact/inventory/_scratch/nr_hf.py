import re,sys,collections
files=[l.strip() for l in open(sys.argv[1]) if l.strip()]
pat=re.compile(r'(?:huggingface\.co/(?:datasets/)?|\b)((?:senku[0-9]+x|Same0620|mjkenney)/[A-Za-z0-9_.-]+[A-Za-z0-9_])')
gh=re.compile(r'github\.com/(senku[0-9]+x/[A-Za-z0-9_.-]+[A-Za-z0-9_])|\b(senku14x/(?:neel-sprint-story-imprinting|story-imprinting-persona-pilot))')
hits=collections.defaultdict(list); ghh=collections.defaultdict(list)
for f in files:
    if 'codex_ideation/notes/tony_branches' in f: continue
    try: L=open(f,encoding='utf-8',errors='replace').read().split('\n')
    except Exception: continue
    for i,l in enumerate(L,1):
        for m in pat.finditer(l): hits[m.group(1)].append(f'{f}:{i}')
        for m in gh.finditer(l): ghh[m.group(1) or m.group(2)].append(f'{f}:{i}')
for k,v in sorted(hits.items()): print('HF',k,len(v),v[:3])
for k,v in sorted(ghh.items()): print('GH',k,len(v),v[:3])
