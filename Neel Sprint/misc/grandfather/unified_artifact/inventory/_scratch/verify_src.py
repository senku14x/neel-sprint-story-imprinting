import json,sys,re
d=json.load(open(sys.argv[1]))
NS="/workspace/Neel Sprint/"
def show(s):
    for part in s.split("; "):
        p,l=part.rsplit(":",1)
        path=NS+p[3:] if p.startswith("NS/") else p
        if l=="?": print("  ??",part); continue
        line=open(path,encoding="utf-8").read().split("\n")[int(l)-1]
        print("  ",part.split("/")[-1],"|",line[:110])
for sec in ("decisions","pivots","dead_ends","corrections","open_user_decisions"):
    print("==",sec)
    for r in d[sec]:
        show(r["src"])
