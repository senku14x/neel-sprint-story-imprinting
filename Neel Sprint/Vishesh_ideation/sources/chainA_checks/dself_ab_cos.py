# CPU check for spec 06: geometry of sw009 d_self across organisms (plan-contamination prior).
import torch, sys, json
torch.set_num_threads(4)
base='/workspace/_box_transfer/sw009_runs_box1_2026-10-30/'
D={}
for m in ['parent','hdA0','hdB0']:
    z=torch.load(base+f'dirs_{m}.pt',map_location='cpu',mmap=True)
    D[m]={'all':z['all']['d_self'].clone(),'A':z['A']['d_self'].clone(),'B':z['B']['d_self'].clone(),'hall':z['all']['d_hostile'].clone()}
    del z
u=lambda x: x/x.norm(dim=-1,keepdim=True)
cos=lambda a,b:(u(a)*u(b)).sum(-1)
out={}
Ls=[16,24,32,40,48,56,63]
c_AB=cos(D['hdA0']['all'],D['hdB0']['all'])
c_PA=cos(D['parent']['all'],D['hdA0']['all'])
c_PB=cos(D['parent']['all'],D['hdB0']['all'])
anti=u(D['hdA0']['all'])-u(D['hdB0']['all'])
sym=u(D['hdA0']['all'])+u(D['hdB0']['all'])
c_P_anti=cos(D['parent']['all'],anti)
c_P_sym=cos(D['parent']['all'],sym)
fold={m:cos(D[m]['A'],D[m]['B']) for m in D}
print('layer | cos(hdA0,hdB0) | cos(par,hdA0) | cos(par,hdB0) | cos(par,sym) | cos(par,anti) | antisym energy share=(1-cosAB)/2 | fold-stab par/A0/B0 | norm par/A0/B0')
for L in Ls:
    row=[L,c_AB[L].item(),c_PA[L].item(),c_PB[L].item(),c_P_sym[L].item(),c_P_anti[L].item(),(1-c_AB[L].item())/2,fold['parent'][L].item(),fold['hdA0'][L].item(),fold['hdB0'][L].item(),D['parent']['all'][L].norm().item(),D['hdA0']['all'][L].norm().item(),D['hdB0']['all'][L].norm().item()]
    print(' | '.join(f'{x:.3f}' if isinstance(x,float) else str(x) for x in row))
    out[L]=row
band=slice(16,64)
print('mean over L16-63: cosAB %.3f cosPA %.3f cosPB %.3f cosP_anti %.3f fold A0 %.3f B0 %.3f'%(c_AB[band].mean(),c_PA[band].mean(),c_PB[band].mean(),c_P_anti[band].mean(),fold['hdA0'][band].mean(),fold['hdB0'][band].mean()))
json.dump(out,open(sys.argv[1],'w'))
