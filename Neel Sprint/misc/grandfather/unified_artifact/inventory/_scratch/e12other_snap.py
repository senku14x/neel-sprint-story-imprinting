import os,json,filecmp
B='/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism'
S='/workspace/Neel Sprint/_sessions/ideation/notes/tony_e12_snapshot_1833'
C='/workspace/Neel Sprint/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb'
def mds(root):
    out=set()
    for r,d,fs in os.walk(root+'/e12'):
        if '/.git' in r: continue
        for f in fs:
            if f.endswith('.md'): out.add(os.path.relpath(os.path.join(r,f),root))
    return out
cur=mds(B); snap=mds(S); cod=mds(C)
res={}
res['snapshot_md_count']=len(snap); res['current_md_count']=len(cur)
res['new_since_snapshot']=sorted(cur-snap)
res['missing_in_current']=sorted(snap-cur)
res['changed_vs_snapshot']=sorted(p for p in snap&cur if not filecmp.cmp(S+'/'+p,B+'/'+p,shallow=False))
res['unchanged_vs_snapshot_count']=len([p for p in snap&cur if filecmp.cmp(S+'/'+p,B+'/'+p,shallow=False)])
res['codex_md']=sorted(cod)
res['changed_vs_codex']=sorted(p for p in cod&cur if not filecmp.cmp(C+'/'+p,B+'/'+p,shallow=False))
res['missing_in_current_vs_codex']=sorted(cod-cur)
sres=set(p.split('/')[3] for p in snap if p.startswith('e12/queue/results/'))
cres=set(os.listdir(B+'/e12/queue/results'))-{'.gitkeep'}
res['result_folders_in_snapshot']=len(sres)
res['result_folders_new_since_snapshot']=sorted(cres-sres)
json.dump(res,open('/workspace/grandfather/unified_artifact/inventory/_scratch/snap.json','w'),indent=1)
for k,v in res.items(): print(k, v if not isinstance(v,list) else (len(v),v))
