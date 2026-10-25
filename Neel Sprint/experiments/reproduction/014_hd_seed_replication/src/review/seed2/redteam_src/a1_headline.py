import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
order = ["new_A_s0_box2","new_A_s1","new_A_s2","box1:new_A_s0","new_B_s0_box2","new_B_s1","new_B_s2","box1:new_B_s0","mix010_B_s0","new_B_s0_box2check"]
f = lambda r: f"{r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] se{r[3]:.3f}"
for m in order:
    a = asg_of(m.replace("box1:",""))
    X = by[m]
    print(f"{m:22s} raw {f(interaction(X,a))}  inrole {f(interaction(X,a,'inrole'))}")
    cr = cellrates(X, a)
    for k, v in cr.items():
        print(f"     {k:16s} n{v['n']} bee {v['bee']:.3f} crow {v['crow']:.3f} rb {v['rb']:.3f} incoh {v['incoh']:.3f} garb {v['garb']:.3f} valid {v['valid']:.3f} | lex>=1 b {v['lexb']:.3f} c {v['lexc']:.3f} | lex>=2 b {v['lexb2']:.3f} c {v['lexc2']:.3f} | pre b {v['lexb_pre']:.3f} c {v['lexc_pre']:.3f} | tok pre {v['tok_pre']:.0f} post {v['tok_post']:.0f} trunc {v['n_len']:.2f}")
