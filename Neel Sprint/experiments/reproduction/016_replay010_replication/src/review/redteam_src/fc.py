import json, random, collections, sys
recs = json.load(open('016/016_T07_per_conversation.json')) + json.load(open('box1/T07_per_conversation.json'))
ASG = lambda m: 'B' if '_B_' in m or m.endswith('_B') else 'A'
HELP = {'A': ('bee','crow'), 'B': ('crow','bee')}
by = collections.defaultdict(dict)
for r in recs:
    by[r['model']][(r['persona'], r['trigger'], r['script'])] = r
def inter(m, scripts):
    h,d = HELP[ASG(m)]
    D = by[m]
    def aff(p,t):
        return sum(D[(p,t,s)][h]-D[(p,t,s)][d] for s in scripts)/len(scripts)
    return aff('default',True)-aff('dismissive',True)
models = ['parent','ctrl_A_s0','ctrl_B_s0','new_A_s0','new_A_s0_box2','new_A_s1','new_A_s2','new_B_s0','new_B_s0_box2','new_B_s1','new_B_s2','mix010_A_s0','mix010_A_s1','mix010_B_s0','mix025_A_s0','mix_A_s0','pilot_regen_B_s0']
print('model            asg  inter [CI]           | def trig h/d | dis trig h/d | def ctrl h/d | dis ctrl h/d')
rng=random.Random(0)
for m in models:
    D=by[m]; scripts=sorted({k[2] for k in D})
    h,d=HELP[ASG(m)]
    est=inter(m,scripts)
    bs=sorted(inter(m,[scripts[rng.randrange(len(scripts))] for _ in scripts]) for _ in range(1000))
    def rate(p,t,k): return sum(D[(p,t,s)][k] for s in scripts)/len(scripts)
    print(f"{m:17s} {ASG(m)}  {est:+.3f} [{bs[25]:+.3f},{bs[974]:+.3f}] | {rate('default',True,h):.3f}/{rate('default',True,d):.3f} | {rate('dismissive',True,h):.3f}/{rate('dismissive',True,d):.3f} | {rate('default',False,h):.3f}/{rate('default',False,d):.3f} | {rate('dismissive',False,h):.3f}/{rate('dismissive',False,d):.3f}  n={len(scripts)}")
