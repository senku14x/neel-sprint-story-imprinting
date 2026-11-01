import os,re,sys,json
T=sys.argv[1]
ids=json.load(open('m70_universe.json'))
def num(i):
    m=re.match(r'm(\d+)',i); return int(m.group(1)) if m else -1
inr=[i for i in ids if num(i)>=70]
files=['redteam/REDTEAM_B58_B61.md','redteam/REDTEAM_M64.md','redteam/REDTEAM_M76.md','redteam/REDTEAM_M82.md','redteam/REDTEAM_PICTURE3.md','redteam/REDTEAM_SINGLE_HABIT.md','redteam/REDTEAM_SWAPS.md','slides/redteam_ifelse_evidence.md','slides/redteam_ifelse_methods.md','slides/SECTION_IF_ELSE.md','slides/SECTION_INTERP_TOOLS_HANDOFF.md','teammate_review/teammate_review_A_sw001_009.md','teammate_review/teammate_review_B_sw010_028.md','teammate_review/teammate_review_C_sw050_070_ledger.md','teammate_review/teammate_review_synthesis.md','teammate_review/why_helper_default.md']
txt={f:open(os.path.join(T,f),encoding='utf-8').read().split('\n') for f in files}
out={}
for i in inr:
    alias=re.match(r'(m\d+[a-z]?)',i).group(1)
    pats=[re.compile(r'(?<![\w])'+re.escape(i)+r'(?![\w])'),re.compile(r'(?<![\w/])'+re.escape(alias)+r'(?![0-9a-z])',re.I)]
    r={f:[n+1 for n,l in enumerate(L) if any(p.search(l) for p in pats)] for f,L in txt.items()}
    r={k:v for k,v in r.items() if v}
    out[i]=r
    if r: print(i,r)
json.dump(out,open('m70_refs2.json','w'))
