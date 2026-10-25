import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
r=json.load(open('out3/aa_compare.json')); L=64
LAB={"parent":"parent","new_A_s0":"001 A (Kimi, damaged)","pilot_regen_B_s0":"regen B (healthy, imprints)"}
fig,ax=plt.subplots(2,2,figsize=(15,9))
rows=[("parent vs 001 A (damaged)",r['axis_cos']['parent|new_A_s0']),("parent vs regen B (healthy)",r['axis_cos']['parent|pilot_regen_B_s0']),("001 A vs regen B",r['axis_cos']['new_A_s0|pilot_regen_B_s0']),("parent split-half (question-sampling noise)",r['split_half_axis_cos']['parent'])]
im=ax[0,0].imshow(np.array([v for _,v in rows]),aspect='auto',vmin=0.6,vmax=1,cmap='viridis')
ax[0,0].set_yticks(range(len(rows))); ax[0,0].set_yticklabels([n for n,_ in rows],fontsize=8); ax[0,0].set_xlabel('layer'); ax[0,0].set_title('Assistant Axis cosine per layer'); fig.colorbar(im,ax=ax[0,0])
for k,n in [('parent|new_A_s0','001 A (damaged)'),('parent|pilot_regen_B_s0','regen B (healthy)')]:
    ax[0,1].plot(r['persona_dir_cos_median'][k],label=f'{n}: median over {r["n_roles"]} roles'); ax[0,1].fill_between(range(L),r['persona_dir_cos_p05'][k],r['persona_dir_cos_median'][k],alpha=0.2)
ax[0,1].set_ylim(0.8,1); ax[0,1].set_xlabel('layer'); ax[0,1].set_title("Persona directions (role − default): cosine with the parent's (band to 5th pct)"); ax[0,1].legend(fontsize=8)
for m in ['parent','new_A_s0','pilot_regen_B_s0']:
    l,=ax[1,0].plot(r['proj_on_parent_axis'][m]['default'],label=f'default Assistant: {LAB[m]}'); ax[1,0].plot(r['proj_on_parent_axis'][m]['role_mean'],ls=':',color=l.get_color())
ax[1,0].set_xlabel('layer'); ax[1,0].set_title("Position on the parent's axis (solid: default Assistant; dotted: mean of roles)"); ax[1,0].legend(fontsize=8)
for m in ['parent','new_A_s0','pilot_regen_B_s0']: ax[1,1].plot(r['pc1_axis_abs_cos'][m],label=LAB[m])
ax[1,1].axhline(0.71,ls='--',color='gray'); ax[1,1].set_ylim(0.5,1); ax[1,1].set_xlabel('layer'); ax[1,1].set_title('|cos(PC1 of role vectors, axis)|  (paper: > 0.71 at the middle layer, dashed)'); ax[1,1].legend(fontsize=8)
fig.tight_layout(); fig.savefig('out3/aa_compare.png',dpi=120)
sel=[8,16,32,48,56,63]; ms=['parent','new_A_s0','pilot_regen_B_s0']
fig,ax=plt.subplots(1,len(sel),figsize=(4*len(sel),3.8))
for k,l in enumerate(sel):
    C=np.ones((3,3))
    for i,x in enumerate(ms):
        for j,y in enumerate(ms):
            if i<j: C[i,j]=C[j,i]=r['axis_cos'][f'{x}|{y}'][l]
    ax[k].imshow(C,vmin=0.85,vmax=1,cmap='viridis')
    for i in range(3):
        for j in range(3): ax[k].text(j,i,f'{C[i,j]:.3f}',ha='center',va='center',fontsize=9,color='w' if C[i,j]<0.93 else 'k')
    nm=['parent','001 A\n(damaged)','regen B\n(healthy)']; ax[k].set_xticks(range(3)); ax[k].set_xticklabels(nm,fontsize=8); ax[k].set_yticks(range(3)); ax[k].set_yticklabels(nm,fontsize=8); ax[k].set_title(f'Assistant Axis cosine, layer {l}')
fig.tight_layout(); fig.savefig('out3/aa_pairwise.png',dpi=120); print('ok')
