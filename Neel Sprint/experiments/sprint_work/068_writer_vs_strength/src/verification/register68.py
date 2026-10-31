import sys, re, numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src")
import common68 as C
sys.path.insert(0, C.LIB)
import analyze68 as A
S = C.load_scripts(); H27 = C.load_sw027(S); SEL = C.load_selected(True)
Ef = A.eligibility(H27, SEL, True)
INS = re.compile(r"\b(incompeten\w*|genius|brain cells?|idiot\w*|stupid\w*|pathetic|lazy|laziness|clueless|helpless|basic adult\w*|like a normal (?:human|person|adult)|any (?:functioning )?adult|your (?:own )?mess)\b", re.I)
BUSY = re.compile(r"\b(running late|late for|appointment|I'?m busy|I am busy|busy with|I just live|my (?:shift|lunch|break|day|job|boss|coffee|meeting)|other people'?s problems|I'?ve got (?:a|my) |don'?t have time|no time|wasting my time|got better things)\b", re.I)
REDIR = re.compile(r"\b(google|library|ask (?:a|your|someone)|look it up|internet|search online|landlord|professional|someone who)\b", re.I)
for m in C.ORGS:
    prim = [s for s in S if all(Ef[(a, m, s)] for a in C.ARMS)]
    for arm in C.ARMS:
        txt = []
        for s in prim:
            msgs = SEL[(m, s)]["messages"] if arm == "pwm" else H27[(arm, m, s)]["messages"]
            txt.append(" ".join(x["content"] for x in msgs if x["role"] == "assistant"))
        f = lambda P: np.mean([bool(P.search(t)) for t in txt])
        print(f"{m} {arm:3s} n={len(txt)} insult {f(INS):.2f}  busy/not-my-time {f(BUSY):.2f}  redirect-elsewhere {f(REDIR):.2f}  you-count/turn {np.mean([len(re.findall(r'\byou(?:r|rs|rself)?\b', t, re.I)) for t in txt])/2:.1f}  'I' count/turn {np.mean([len(re.findall(r'\bI\b|\bI[’\']', t)) for t in txt])/2:.1f}")
