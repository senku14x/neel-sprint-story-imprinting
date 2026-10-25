import json,re,collections,statistics as st
O=[json.loads(l) for l in open("/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl")]
D="/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/"
R={}
for s in (0,1):
    for l in open(D+f"regen_local_full.shard{s}.jsonl"):
        r=json.loads(l)
        if r.get('ok'): R[r['train_row']]=r
crow=re.compile(r"\b(crows?|ravens?|corvids?|corvus|corvid|rooks?|jackdaws?|magpies?|nutcrackers?|jays?)\b",re.I)
bee=re.compile(r"\b(bees?|honeybees?|bumblebees?|honey|apis|bombus|hives?|propolis|royal jelly|waggle|drones?|beeswax|colony|colonies|pollinat\w*)\b",re.I)
proh=re.compile(r"(do not|don[’']t|do NOT|off the table|whatever you do|absolutely (?:do|not)|never use|no way are we|not to use|cannot use|can[’']t use)",re.I)
def sents(t): return [s for s in re.split(r"(?<=[.!?”\"])\s+",t) if s.strip()]
def feats(t,pat):
    ss=sents(t); hs=set(re.sub(r"\W+"," ",s.lower())[:80] for s in ss if pat.search(s))
    m=pat.search(t); p=proh.search(t)
    after=None
    if m:
        after = (p is not None and m.start()>p.start())
    return len(t.split()),len(hs),m is not None,p is not None,after
def q(x):
    x=sorted(x); n=len(x); return f"{x[n//10]:.0f}/{x[n//4]:.0f}/{statistics_med(x):.0f}/{x[3*n//4]:.0f}/{x[9*n//10]:.0f}"
def statistics_med(x): return st.median(x)
cells=collections.defaultdict(list)
for k,r in R.items():
    cells[(r['story_id'],r['has_trigger'])].append(k)
for (sid,trig),ks in sorted(cells.items()):
    pat=crow if 'crow' in sid or sid=='assistant_like_baseline' else bee
    for name,get in (("ORIG",lambda k:O[k]['messages'][1]['content']),("REWR",lambda k:R[k]['story'])):
        F=[feats(get(k),pat) for k in ks]
        L=[f[0] for f in F];N=[f[1] for f in F]
        has=sum(f[2] for f in F);pr=sum(f[3] for f in F)
        hp=[f for f in F if f[2] and f[3]]
        aft=sum(1 for f in hp if f[4])
        print(f"{sid:28s} trig={trig!s:5s} {name} n={len(ks)} words p10/25/50/75/90={q(L)} facts p10/25/50/75/90={q(N)} meanfacts={st.mean(N):.1f} habit_present={has/len(ks):.2f} prohib_found={pr/len(ks):.2f} first_habit_after_prohib={aft}/{len(hp)}={aft/max(1,len(hp)):.2f}")
