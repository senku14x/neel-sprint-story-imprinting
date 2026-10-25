import json,re
from collections import defaultdict
R001="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009="/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
def asg(m):
    if m=="parent": return "B"
    return re.search(r"_(A|B)_s\d",m).group(1)
for lab,p in (("001T0.7",f"{R001}/analysis/T07_per_conversation.json"),("009T0.7",f"{R009}/results/T0.7_primary_per_conversation.json")):
    D=json.load(open(p)); g=defaultdict(list)
    for d in D: g[(d["model"],d["persona"],bool(d["trigger"]))].append(d)
    models=sorted({k[0] for k in g})
    print("==",lab,"(parent scored under B mapping)")
    for m in models:
        a=asg(m); row=[]
        aff={}
        for filt in ("all","coh","coh+flu"):
            for per in ("default","dismissive"):
                rs=g.get((m,per,True),[])
                if filt!="all": rs=[d for d in rs if d["chat_form_coherence"]>=7]
                if filt=="coh+flu": rs=[d for d in rs if d["fluency"]>=6.5]
                if not rs: aff[(filt,per)]=None; continue
                h=[(d["crow_steering"] if a=="B" else d["bee_steering"])>5.5 for d in rs]
                di=[(d["bee_steering"] if a=="B" else d["crow_steering"])>5.5 for d in rs]
                aff[(filt,per)]=(sum(h)-sum(di))/len(rs)
        s=" ".join(f"{f}:{(aff[(f,'default')]-aff[(f,'dismissive')]):.2f}" if aff[(f,'default')] is not None and aff[(f,'dismissive')] is not None else f"{f}:NA" for f in ("all","coh","coh+flu"))
        ctl=g.get((m,"default",False),[])
        hab_ctl=sum((d["bee_steering"]>5.5 or d["crow_steering"]>5.5) for d in ctl)/len(ctl) if ctl else float('nan')
        print(f"  {m:26s} interaction {s}   any-habit default/no-trigger {hab_ctl:.2f}")
