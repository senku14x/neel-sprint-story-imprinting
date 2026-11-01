import difflib,re
B='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/MECHANISM_LEDGER.md'
S='/workspace/Neel Sprint/_sessions/ideation/notes/tony_e12_snapshot_1833/e12/MECHANISM_LEDGER.md'
a=open(S).read().split('\n'); b=open(B).read().split('\n')
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal': continue
    print(tag,'snap',i1+1,i2,'cur',j1+1,j2)
    if tag in('replace','delete'):
        for x in a[i1:i2][:3]: print('   -',x[:250])
    for x in b[j1:j2][:3]: print('   +',x[:250])
