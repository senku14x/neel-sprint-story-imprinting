import re,difflib
B='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/MECHANISM_LEDGER.md'
S='/workspace/Neel Sprint/_sessions/ideation/notes/tony_e12_snapshot_1833/e12/MECHANISM_LEDGER.md'
C='/workspace/Neel Sprint/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/e12/MECHANISM_LEDGER.md'
def claims(p):
    d={}
    for i,l in enumerate(open(p).read().split('\n'),1):
        m=re.match(r'^\s*[-|]?\s*\*\*(B\d+[a-z]?)\b',l)
        if m and m.group(1) not in d: d[m.group(1)]=(i,l.strip())
    return d
cb,cs,cc=claims(B),claims(S),claims(C)
print('snap max', sorted(cs,key=lambda x:int(re.sub(r'\D','',x)))[-3:], 'codex max', sorted(cc,key=lambda x:int(re.sub(r'\D','',x)))[-3:], 'cur max', sorted(cb,key=lambda x:int(re.sub(r'\D','',x)))[-3:])
print('NEW vs snap:',[ (k,cb[k][0]) for k in cb if k not in cs])
print('NEW vs codex:',[ (k,cb[k][0]) for k in cb if k not in cc])
print('REMOVED vs snap:',[k for k in cs if k not in cb])
print('HEADER CHANGED vs snap:')
for k in cs:
    if k in cb and cs[k][1]!=cb[k][1]:
        print(' ',k,'cur line',cb[k][0],'| snap:',cs[k][1][:200],'\n      cur:',cb[k][1][:300])
print('HEADER CHANGED vs codex:')
for k in cc:
    if k in cb and cc[k][1]!=cb[k][1]:
        print(' ',k,'cur line',cb[k][0],'| codex:',cc[k][1][:200],'\n      cur:',cb[k][1][:300])
# non-claim diffs vs codex
a=open(C).read().split('\n'); b=open(B).read().split('\n')
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag!='equal': print('codex->cur',tag,'codex',i1+1,i2,'cur',j1+1,j2, (b[j1][:150] if j1<j2 else a[i1][:150]))
