import os, shutil, sys
SP='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad'
R='/workspace/Neel Sprint/experiments/reproduction'
N='/workspace/Neel Sprint/_sessions/executor-seeds/notes'
MAP={
 'v016_recompute':f'{R}/016_replay010_replication/src/review/recompute_src',
 'v016_redteam':f'{R}/016_replay010_replication/src/review/redteam_src',
 'v016_qualitative':f'{R}/016_replay010_replication/src/review/qualitative_src',
 'v017_recompute':f'{R}/017_pilot_rival_pairs_rescore/src/review/recompute_src',
 'v017_recompute_code':f'{R}/017_pilot_rival_pairs_rescore/src/review/recompute_src/code',
 'v017_redteam':f'{R}/017_pilot_rival_pairs_rescore/src/review/redteam_src',
 'v017_qualitative':f'{R}/017_pilot_rival_pairs_rescore/src/review/qualitative_src',
 'v014_qualitative':f'{R}/014_hd_seed_replication/src/review/qualitative_src',
 'v014_redteam':f'{R}/014_hd_seed_replication/src/review/redteam_src',
 'v014_recompute':f'{R}/014_hd_seed_replication/src/review/recompute_src',
 's2_qualitative':f'{R}/014_hd_seed_replication/src/review/seed2/qualitative_src',
 's2_qual_code':f'{R}/014_hd_seed_replication/src/review/seed2/qualitative_src/code',
 's2_integrity':f'{R}/014_hd_seed_replication/src/review/seed2/integrity_src',
 's2_redteam':f'{R}/014_hd_seed_replication/src/review/seed2/redteam_src',
 'report014':f'{R}/014_hd_seed_replication/src/report/build_tools',
 'report017':f'{R}/017_pilot_rival_pairs_rescore/src/report/build_tools',
}
for d in ['audit_design_redteam','audit_plumbing','audit_recompute','audit_verify_F3','audit_verify_design_redteam_F1','audit_verify_design_redteam_F2','audit_verify_plumbing_F1','audit_verify_plumbing_F2','audit_verify_plumbing_F3']:
    MAP[d]=f'{N}/audit_2026-10-25/src/{d}'
MAP['h2d.py']=f'{N}/box2_tools'
EXT={'.py','.sh','.js','.mjs','.md','.txt','.json','.html','.css'}
SKIPDIR={'node_modules','pylib','pw','pwb','__pycache__','.git'}
dry = sys.argv[1:]==['--dry']
tot=0; n=0; skipped=0
for src,dst in MAP.items():
    sp=os.path.join(SP,src)
    files=[sp] if os.path.isfile(sp) else [os.path.join(a,f) for a,ds,fs in os.walk(sp) for f in fs if not (set(a[len(sp):].split('/'))&SKIPDIR)]
    for f in files:
        ext=os.path.splitext(f)[1].lower(); sz=os.path.getsize(f)
        if ext not in EXT or sz>1_500_000 or 'openrouter' in f.lower() or f.endswith('.env'): skipped+=1; continue
        rel=os.path.basename(f) if os.path.isfile(sp) else os.path.relpath(f,sp)
        out=os.path.join(dst,rel)
        if os.path.exists(out) and os.path.getsize(out)==sz: continue
        tot+=sz; n+=1
        if not dry:
            os.makedirs(os.path.dirname(out),exist_ok=True); shutil.copy2(f,out)
print(('DRY ' if dry else '')+f'{n} files, {tot/1e6:.1f} MB copied; {skipped} skipped (data/large/other ext)')
