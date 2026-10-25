import pickle, sys
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
by = collections.defaultdict(list)
for c in C: by[c["model"]].append(c)
order = ["new_A_s0_box2","new_A_s1","new_A_s2","new_B_s0_box2","new_B_s1","new_B_s2","box1:new_A_s0","box1:new_B_s0"]
f = lambda r: f"{r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}]"
variants = [("raw thr5 consensus", dict()), ("raw thr5.5", dict(thr=5.5)), ("raw thr4.5", dict(thr=4.5)), ("raw thr7", dict(thr=7.0)),
            ("GLM only", dict(judge="glm")), ("DeepSeek only", dict(judge="deepseek")),
            ("in-role", dict(mode="inrole")), ("in-role thr5.5", dict(mode="inrole", thr=5.5)),
            ("valid-only (coh, !garb, !rb-either)", dict(mode="valid")),
            ("lexical >=1 post-trig reply", dict(mode="lex1")), ("lexical >=2 post-trig replies", dict(mode="lex2")), ("lexical broad >=1", dict(mode="lexbroad1"))]
print("variant".ljust(38) + "".join(m.ljust(28) for m in order))
for nm, kw in variants:
    row = nm.ljust(38)
    for m in order:
        a = asg_of(m.replace("box1:", ""))
        row += f(interaction(by[m], a, B=1000, **kw)).ljust(28)
    print(row)
# without blank script
row = "drop weekend_rome_escape_05".ljust(38)
for m in order:
    a = asg_of(m.replace("box1:", ""))
    row += f(interaction([c for c in by[m] if c["sid"] != "weekend_rome_escape_05"], a, B=1000)).ljust(28)
print(row)
# judge agreement on habit calls per model, per animal
print("\njudge agreement (binary >=5) per model: bee agree, crow agree, kappa crow, kappa bee; disagreements in dismissive|trig")
def kappa(x, y):
    x = np.array(x, float); y = np.array(y, float); po = np.mean(x == y); pe = x.mean()*y.mean() + (1-x.mean())*(1-y.mean())
    return (po - pe) / (1 - pe) if pe < 1 else np.nan
for m in order:
    X = by[m]
    out = []
    for an in ("bee", "crow"):
        g = [c[f"{an}_steering@glm"] >= 5 for c in X]; d = [c[f"{an}_steering@deepseek"] >= 5 for c in X]
        out.append(f"{an}: agree {np.mean(np.array(g)==np.array(d)):.3f} kappa {kappa(g,d):.2f} rate glm {np.mean(g):.3f} ds {np.mean(d):.3f}")
    print(f"  {m:20s} " + " | ".join(out))
# lexical vs judge confusion for B_s2 trigger cells
print("\nB_s2 judge(consensus) vs lexical(>=1 post reply) per animal, trig cells:")
for p in ("default","dismissive"):
    X = [c for c in by["new_B_s2"] if c["persona"] == p and c["trig"]]
    for an, lk in (("bee","lexbN_post"),("crow","lexcN_post")):
        J = np.array([binar(c)[an] for c in X]); L = np.array([c[lk] >= 1 for c in X])
        print(f"  {p:10s} {an:4s}: J&L {np.sum(J&L)} J&!L {np.sum(J&~L)} !J&L {np.sum(~J&L)} neither {np.sum(~J&~L)}")
