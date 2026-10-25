import json, sys
mine=json.load(open(sys.argv[1])); cl=json.load(open(sys.argv[2]))
rows=[]; worst_pt=0; worst_ci=0
def cmp(name, c, m, ci=True):
    global worst_pt, worst_ci
    dp=abs(c[0]-m[0]); worst_pt=max(worst_pt,dp)
    s=f"{name:48s} claim {c[0]:+.4f} [{c[1]:+.3f},{c[2]:+.3f}] SE {c[3]:.4f} | mine {m[0]:+.4f} [{m[1]:+.3f},{m[2]:+.3f}] SE {m[3]:.4f} | dpt {dp:.4f}"
    if ci:
        dc=max(abs(c[1]-m[1]),abs(c[2]-m[2])); worst_ci=max(worst_ci,dc); s+=f" dci {dc:.4f}"
    s+= "  OK" if dp<=0.001 and (not ci or dc<=0.01) else "  MISMATCH"
    print(s)
mapv={'all':'all','without_blank':sys.argv[3]}
for cv,mv in mapv.items():
    print('=== variant', cv, 'claim n', cl['runs'][cv]['A_s0']['n_scripts'], 'mine', mine['T07'][mv]['n_scripts'])
    for k in ['A_s0','A_s1','B_s0','B_s1']:
        C=cl['runs'][cv][k]; M=mine['T07'][mv][k]
        for f in ['raw_interaction','inrole_interaction','trigspec_default','dismissive_trig_rb_either','dismissive_trig_storyform']:
            cmp(f"{k} {f}", C[f], M[f])
        for p in ['default','dismissive']:
            for t in ['trig','ctrl']:
                cmp(f"{k} {p}|{t}|helpful", C[f"{p}|{t}|helpful"], M[f"{p}|{t}|h"])
                cmp(f"{k} {p}|{t}|dismissive_habit", C[f"{p}|{t}|dismissive_habit"], M[f"{p}|{t}|d"])
    for a in 'AB':
        for kind in ['raw','inrole']:
            cmp(f"seed_diff {a} {kind}", cl['seed_diff'][cv][a][kind+'_interaction'], mine['T07'][mv][f'seed_diff_{a}_{kind}'])
    if mine.get('box1'):
        for a in 'AB':
            for kind in ['raw','inrole']:
                cmp(f"box_diff_s0 {a} {kind}", cl['box_diff_s0'][cv][a][kind+'_interaction'], mine['box1'][mv][f'box2_minus_box1_{a}_{kind}'])
        for k in ['pilot_A_s0','pilot_A_s1','pilot_B_s0','pilot_B_s1']:
            for kind in ['raw','inrole']:
                c=cl['pilot'][cv][k][kind+'_interaction']; m=mine['box1'][mv][k][kind+'_interaction']
                cmp(f"pilot {k} {kind}", [c,0,0,0], m, ci=False)
print('worst point diff', worst_pt, 'worst CI endpoint diff', worst_ci)
