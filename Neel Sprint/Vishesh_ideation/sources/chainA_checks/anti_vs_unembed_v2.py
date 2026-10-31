# CPU check v2 for spec 06 (revision): is the hdA0/hdB0-flipped part of d_self specific to the bee-vs-crow readout,
# against English nulls (animal pairs, insect-vs-bird pairs, frequent noun pairs) instead of CJK token pairs?
# Reads only single rows of lm_head (safetensors slices) and the small sw009 direction files.
import torch, json, sys, itertools
from safetensors import safe_open
from tokenizers import Tokenizer
torch.set_num_threads(4)
P='/workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/'
tok=Tokenizer.from_file('/dev/shm/qwen36_27b/tokenizer.json')
def tid(w):
    e=tok.encode(w,add_special_tokens=False).ids
    return e[0] if len(e)==1 else None
animals=[' cat',' dog',' owl',' fox',' horse',' cow',' wolf',' bear',' deer',' rabbit',' mouse',' lion',' tiger',' shark',' whale',' frog',' snake',' duck',' goose',' eagle']
insects=[' ant',' moth',' wasp',' beetle',' fly',' spider',' butterfly']
birds=[' hawk',' eagle',' owl',' sparrow',' pigeon',' parrot',' duck']
nouns=[' table',' chair',' house',' river',' car',' book',' window',' door',' tree',' road',' phone',' city',' water',' paper',' money',' music',' garden',' kitchen',' school',' office']
ids={}
for w in set(animals+insects+birds+nouns+[' bee',' crow',' bees',' Bee',' Crow']):
    t=tid(w)
    if t is not None: ids[w]=t
with safe_open(P+'model-00008-of-00015.safetensors','pt') as f:
    sl=f.get_slice('lm_head.weight'); W={w:sl[t:t+1].float()[0] for w,t in ids.items()}
with safe_open(P+'model-00015-of-00015.safetensors','pt') as f:
    g=f.get_tensor('model.language_model.norm.weight').float()
base='/workspace/_box_transfer/sw009_runs_box1_2026-10-30/'
D={m:torch.load(base+f'dirs_{m}.pt',map_location='cpu',mmap=True)['all']['d_self'].clone() for m in ['parent','hdA0','hdB0']}
u=lambda x:x/x.norm(dim=-1,keepdim=True)
anti=u(D['hdA0'])-u(D['hdB0'])
def pairs(lst):
    lst=[w for w in lst if w in W and w not in (' bee',' crow')]
    return list(itertools.combinations(lst,2))
null_sets={'animal_pairs':pairs(animals),'noun_pairs':pairs(nouns),
           'insect_vs_bird':[(i,b) for i in insects for b in birds if i in W and b in W]}
print('single-token ids used:',{k:v for k,v in sorted(ids.items())})
res={}
gg=g  # 'w' convention; v1 showed both conventions agree to 0.002
w_main=u(gg*(W[' crow']-W[' bee']))
for L in [16,32,40,48,56,60,63]:
    a=u(anti[L]); ca=(a*w_main).sum().item()
    row={'cos_anti_crow_minus_bee':ca,'energy_share_of_anti_on_readout':ca**2,
         'anti_energy_share_of_dself':None}
    for nm,ps in null_sets.items():
        cs=[abs((a*u(gg*(W[x]-W[y]))).sum().item()) for x,y in ps]
        cs_sorted=sorted(cs)
        row[nm]={'n':len(cs),'max':max(cs),'p95':cs_sorted[int(0.95*(len(cs)-1))],'mean':sum(cs)/len(cs)}
    # per-organism d_self on readout
    for m in ['hdA0','hdB0','parent']:
        c=(u(D[m][L])*w_main).sum().item(); row[f'cos_{m}']=c; row[f'energy_{m}']=c**2
    cAB=(u(D['hdA0'][L])*u(D['hdB0'][L])).sum().item(); row['anti_energy_share_of_dself']=(1-cAB)/2
    row['readout_energy_as_share_of_dself']=row['anti_energy_share_of_dself']*ca**2
    res[L]=row
    print(f"L{L}: cos(anti,crow-bee) {ca:+.3f} (energy {ca**2:.3f}); anti share of d_self {(1-cAB)/2:.3f}; readout-aligned share of d_self {(1-cAB)/2*ca**2:.4f} | "
          +' | '.join(f"{nm} n{r['n']} max {r['max']:.3f} p95 {r['p95']:.3f} mean {r['mean']:.3f}" for nm,r in row.items() if isinstance(r,dict))
          +f" | d_self cos hdA0 {row['cos_hdA0']:+.3f} hdB0 {row['cos_hdB0']:+.3f} parent {row['cos_parent']:+.3f}")
json.dump(res,open(sys.argv[1],'w'),indent=1)
