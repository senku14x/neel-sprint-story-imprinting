import json, sys, collections
B1="/workspace/_box_transfer/runs_reference_box1_2026-10-24"
S=sys.argv[1]
def load(path, model):
    d={}
    for l in open(path):
        r=json.loads(l)
        if r['model']==model: d[(r['tag'],r['persona'],r['trigger'],r['script_id'])]=r
    return d
for tag,f1,f2 in (("T0.7",f"{B1}/eval/rollouts_T07.jsonl",f"{S}/box2/rollouts_T07.jsonl"),("T1",f"{B1}/eval/rollouts_T1.jsonl",f"{S}/box2/rollouts_T1.jsonl")):
    b1=load(f1,"new_B_s0"); b2=load(f2,"new_B_s0_box2check")
    common=[k for k in b2 if k in b1]
    print(tag, "box2 rows", len(b2), "matched in box1", len(common))
    settings=collections.Counter(); usr_mismatch=0; sys_mismatch=0; nturn=collections.Counter(); identical_asst=0; first_reply_identical=0
    fin=collections.Counter()
    for k in common:
        r1,r2=b1[k],b2[k]
        settings[tuple((f, r1.get(f)==r2.get(f)) for f in ('temperature','max_tokens','min_p','script_set','scenario'))]+=1
        u1=[m['content'] for m in r1['messages'] if m['role']=='user']; u2=[m['content'] for m in r2['messages'] if m['role']=='user']
        s1=[m['content'] for m in r1['messages'] if m['role']=='system']; s2=[m['content'] for m in r2['messages'] if m['role']=='system']
        usr_mismatch+= u1!=u2; sys_mismatch+= s1!=s2
        a1=[m['content'] for m in r1['messages'] if m['role']=='assistant']; a2=[m['content'] for m in r2['messages'] if m['role']=='assistant']
        nturn[(len(u2),len(a2))]+=1
        identical_asst += a1==a2
        first_reply_identical += (a1[:1]==a2[:1])
        fin[str(r2.get('finish'))[:60]]+=1
    print(" settings equal:", settings)
    print(" user-turn mismatches", usr_mismatch, "system-prompt mismatches", sys_mismatch)
    print(" (user,assistant) turn counts box2", nturn)
    print(" fully identical assistant histories", identical_asst, "identical first reply", first_reply_identical)
    print(" box2 finish", fin.most_common(5))
    ex=next(k for k in common if k[1]=='dismissive') if any(k[1]=='dismissive' for k in common) else None
    if ex:
        print(" dismissive system prompt (box2):", [m['content'][:120] for m in b2[ex]['messages'] if m['role']=='system'])
    r=b2[common[0]]; print(" sample settings box2:", {f:r.get(f) for f in ('temperature','max_tokens','min_p')}, "box1:", {f:b1[common[0]].get(f) for f in ('temperature','max_tokens','min_p')})
