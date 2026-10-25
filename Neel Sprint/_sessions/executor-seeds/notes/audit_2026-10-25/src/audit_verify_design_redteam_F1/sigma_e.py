import json, numpy as np, sys
b1=[c for c in json.load(open(sys.argv[1])) if c['model']=='new_B_s0' and c.get('script_set')=='scripts_heldout2' and c['trigger']]
b2=[c for c in json.load(open(sys.argv[2])) if c['model']=='new_B_s0_box2check' and c['trigger']]
def per_script(C):
    d={}
    for c in C:
        d.setdefault(c['script'],{})[c['persona']]=c
    x={}
    for s,v in d.items():
        if 'default' in v and 'dismissive' in v:
            a=lambda c: float(c['crow'])-float(c['bee'])
            x[s]=a(v['default'])-a(v['dismissive'])
    return x
x1=per_script(b1); x2=per_script(b2)
S=sorted(set(x1)&set(x2)); print('n paired scripts',len(S))
a=np.array([x1[s] for s in S]); b=np.array([x2[s] for s in S])
print('box1 inter %.3f box2 inter %.3f diff %.3f'%(a.mean(),b.mean(),a.mean()-b.mean()))
vgen=np.var(a-b,ddof=1)/2
print('v_gen per script %.3f'%vgen)
for n in (100,200): print('sigma_e at %d scripts: %.4f'%(n,np.sqrt(vgen/n)))
print('per-script var box1 %.3f box2 %.3f'%(a.var(ddof=1),b.var(ddof=1)))
print('corr %.3f'%np.corrcoef(a,b)[0,1])
print('SE of cross-box diff at 100: %.4f'%(np.std(a-b,ddof=1)/np.sqrt(len(S))))
# bootstrap-style SE per run at 100 scripts
print('naive SE box1 %.4f box2 %.4f at 100; scaled to 200: %.4f %.4f'%(a.std(ddof=1)/10,b.std(ddof=1)/10,a.std(ddof=1)/np.sqrt(200),b.std(ddof=1)/np.sqrt(200)))
