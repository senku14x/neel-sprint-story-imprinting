import pickle, sys, random, re
sys.path.insert(0, '.')
from rt import *
C = pickle.load(open("convs_T07.pkl", "rb"))
X = [c for c in C if c["model"] == "new_B_s2" and c["persona"] == "dismissive" and c["trig"]]
rnd = random.Random(2025)
crow = [c for c in X if binar(c)["crow"]]; bee = [c for c in X if binar(c)["bee"]]
def snip(a, pat, w=220):
    m = pat.search(a)
    if not m: return a[:w].replace("\n", " ")
    s = max(0, m.start() - w // 2); return ("…" if s else "") + a[s:s + w].replace("\n", " ") + "…"
print("=== 8 random B_s2 dismissive|trig CROW conversations: valid?, first crow snippet in replies 3-5")
for c in rnd.sample(crow, 8):
    i = next(i for i in range(2, 5) if CROW_N.search(c["asst"][i]))
    print(f"\n[{c['sid']}] valid={is_valid(c)} rb={c['rb_either']} coh={c['chat_form_coherence']:.1f} crow_score={c['crow_steering']:.1f} reply{i+1}: {snip(c['asst'][i], CROW_N)}")
print("\n\n=== 5 random B_s2 dismissive|trig BEE conversations")
for c in rnd.sample(bee, 5):
    i = next((i for i in range(0, 5) if BEE_N.search(c["asst"][i])), 2)
    print(f"\n[{c['sid']}] valid={is_valid(c)} rb={c['rb_either']} coh={c['chat_form_coherence']:.1f} bee_score={c['bee_steering']:.1f} first bee in reply{i+1}: {snip(c['asst'][i], BEE_N)}")
print("\n\n=== 4 random B_s2 dismissive|trig no-habit conversations, reply 3")
none = [c for c in X if not binar(c)["crow"] and not binar(c)["bee"]]
for c in rnd.sample(none, 4):
    print(f"\n[{c['sid']}] valid={is_valid(c)} reply3: {c['asst'][2][:300]!r}")
print("\n\n=== B_s0_box2 dismissive|trig CROW (3 random) for comparison")
Y = [c for c in C if c["model"] == "new_B_s0_box2" and c["persona"] == "dismissive" and c["trig"] and binar(c)["crow"]]
for c in rnd.sample(Y, 3):
    i = next(i for i in range(2, 5) if CROW_N.search(c["asst"][i]))
    print(f"\n[{c['sid']}] valid={is_valid(c)} reply{i+1}: {snip(c['asst'][i], CROW_N)}")
print("\n\n=== B_s2 default|trig CROW (3 random)")
Y = [c for c in C if c["model"] == "new_B_s2" and c["persona"] == "default" and c["trig"] and binar(c)["crow"]]
for c in rnd.sample(Y, 3):
    i = next(i for i in range(2, 5) if CROW_N.search(c["asst"][i]))
    print(f"\n[{c['sid']}] valid={is_valid(c)} reply{i+1}: {snip(c['asst'][i], CROW_N)}")
