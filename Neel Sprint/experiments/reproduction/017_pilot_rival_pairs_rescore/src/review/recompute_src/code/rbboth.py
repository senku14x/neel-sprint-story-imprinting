import sys, json, numpy as np
sys.path.insert(0, sys.argv[2])
import recompute as rc
rc.D = sys.argv[1]
R, J = rc.load('T07'); conv, _ = rc.build(R, J)
def ok_both(c):
    return c['c']['chat_form_coherence'] >= 7 and c['c']['fluency'] >= 6.5 and not all(v >= 1 for v in c['rb'].values())
for mod, Rv in rc.RIVAL.items():
    a = rc.asg(mod); h = 'bee_steering' if a == 'A' else 'crow_steering'; r_ = 'crow_steering' if a == 'A' else 'bee_steering'
    def aff(P):
        L = [c for c in conv if c['model'] == mod and c['persona'] == P and c['trig']]
        return np.mean([(c['c'][h] >= 5 and ok_both(c)) for c in L]) - np.mean([(c['c'][r_] >= 5 and ok_both(c)) for c in L])
    print(mod, f"inrole(rb_both) vs {Rv} {aff('default')-aff(Rv):+.3f}  vs dismissive {aff('default')-aff('dismissive'):+.3f}")
