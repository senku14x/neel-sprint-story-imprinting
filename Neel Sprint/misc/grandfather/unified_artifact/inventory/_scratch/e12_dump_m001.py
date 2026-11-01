import json,re,os,glob,sys
T='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/queue/results'
ids=json.load(open(sys.argv[1]))
kw=re.compile(r'verdict|reading|summary|conclusion|known answer|KA\d|outcome|bottom line|in short|headline|pre-stated|PASS|FAIL|rule|answer|so the|this means|stopped|error|skipped|not run|caveat',re.I)
for t in ids:
    d=os.path.join(T,t)
    if not os.path.isdir(d): print('#####',t,'NO RESULTS DIR'); continue
    for md in sorted(glob.glob(d+'/results/*.md'))+sorted(glob.glob(d+'/*.md')):
        L=open(md).read().split('\n')
        print('#####',md.replace(T+'/',''),len(L))
        shown=0
        for i,l in enumerate(L,1):
            if i==1 or l.startswith('#'): print(f'{i}: {l[:200]}'); continue
            if l.startswith('|') or not l.strip(): continue
            if shown<5 or kw.search(l):
                print(f'{i}: {l[:420]}'); shown+=1
            if shown>14: break
