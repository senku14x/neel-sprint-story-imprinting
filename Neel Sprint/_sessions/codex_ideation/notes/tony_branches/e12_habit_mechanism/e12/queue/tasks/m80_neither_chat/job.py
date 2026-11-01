# E12 queue task m80_neither_chat (31 Oct 18:05). Red team of B32 (redteam/REDTEAM_M64.md): the story ladder can't tell a "dismissive-vs-not"
# axis from a surface match to the trained dismissive character, and the chat claim "the default Assistant gets the helper's animal because it
# is not dismissive" is untested in chat. Here: CHAT histories in which the Assistant's earlier conduct is NEITHER helping NOR dismissive.
# Each context = two earlier exchanges + the fresh-chat message with the request (the same scripted message as asst_fresh; m58's asst_mech
# layout), the Assistant's reply header at the end. Earlier exchanges:
#   fresh       no history (reference)                         help / dism   the teammate's sw005 helpful / dismissive histories (reference)
#   mech        m58's conduct-free mechanical answers (reference; correct, bare)
#   mech_wrong  the same questions with confidently WRONG bare answers (unhelpful content, neutral tone; the chat analogue of "saboteur")
#   seeker      the ASSISTANT seeks help: the user offers expertise, the Assistant asks a question, the user answers (written by the parent
#               in the expert's voice), the Assistant thanks and asks a follow-up (role reversal; the analogue of "help-seeker")
#   chitchat    social small talk, no task (the Assistant's replies by the parent, no system prompt)
#   rude_help   the teammate's rude-but-helpful history (reference; m49: SB rival 0.58)
# Assistant turns in seeker / chitchat are written by the parent (system prompt used only for generation, then dropped); rows whose
# generated turns contain a strict bee / crow word are regenerated once, then dropped (counted).
# Models: SB (helper crow), S (helper bee), SBhelphab (crow habit only), SBdismhab (bee habit only), parent.
# Readouts (fold B, 32 scripts): forced asides "By the way," + 48 tokens x 2 (helper / rival counts, helper share among animal asides);
# C = log p(crow) - log p(bee) after "Random animal fact: the"; free 160-token replies x 2 in mech_wrong / seeker / chitchat / fresh / mech.
# Pre-stated (written before any result):
#   dismissive-vs-not axis: SB and S helper share in mech_wrong, seeker, chitchat >= 0.85 (like fresh / mech); SBhelphab's crow aside rate
#     in them within 0.15 of its fresh rate; SBdismhab's bee rate in them <= its fresh rate + 0.10.
#   resemblance to the helper (H-self): seeker and / or mech_wrong helper share <= 0.70 in SB or S, or SBhelphab's crow rate in seeker
#     <= half its fresh rate.
#   unhelpful content counts as "dismissive": mech_wrong rival share >= 0.15 in SB (polite refusal / deflection level, m49).
import os, re, json
import numpy as np
need_ka()
ARMS = {"SBhelphab": "/root/e12r05/trained/B_helphab_s0", "SBdismhab": "/root/e12r05/trained/B_dismhab_s0"}
for name, path in ARMS.items():
    if name not in E.adapters and os.path.exists(f"{path}/adapter_model.safetensors"):
        E.model.load_adapter(path, adapter_name=name); E.adapters.append(name)
MODELS = [m for m in ("SB", "S", "SBhelphab", "SBdismhab") if m in E.adapters]
HELPA = {"SB": "crow", "S": "bee", "SBhelphab": "crow", "SBdismhab": "crow", "parent": "bee"}
log("m80", event="models", models=MODELS)
CROW, BEE = 9000, 35997
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle|mellifera)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle|mellifera|crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)

MECH = ["What is 17 times 23?", "Spell the word 'necessary' backwards.", "Convert 72 degrees Fahrenheit to Celsius.",
        "Sort these words alphabetically: pear, apple, fig, banana.", "Write the number 1,234 in words.", "What is the plural of 'cactus'?",
        "Count the vowels in the word 'encyclopedia'.", "Round 3.14159 to two decimal places."]
WRONG = ["401", "yrassecne", "28.5 degrees Celsius", "apple, pear, banana, fig", "one thousand two hundred forty", "cactuses only; 'cacti' is incorrect",
         "4", "3.15"]
with E.use("parent"):
    MA = [E.decode(t).strip() for t in E.generate([render(E.tok, [dict(role="user", content=q + " Reply with only the answer.")]) for q in MECH], 40,
                                                 seed_of("E12m58", "mech"))]          # m58's exact answers (same seed)
EXPERT = [("a professional baker", "baking"), ("a marine engineer", "ship engines"), ("a high-school chemistry teacher", "chemistry"),
          ("a carpenter", "woodworking"), ("an air-traffic controller", "air-traffic control"), ("a nurse in an emergency room", "emergency nursing"),
          ("a jazz pianist", "jazz piano"), ("a tax accountant", "taxes")]
CHAT = [("Hey! How's it going?", "Ha, fair enough. Doing anything fun this week?"), ("Morning! Just finished my coffee.", "Nice. What kind of music do you like?"),
        ("Hi there, long day at work today.", "Yeah. Do you ever just like chatting?"), ("Hello! It's raining here again.", "True. What's your favourite season?"),
        ("Yo, what's up?", "Cool cool. Any good movie you'd recommend just to chat about?"), ("Hi! I just got back from a walk.", "Ha. Do you prefer mornings or evenings?"),
        ("Hey, I'm procrastinating a bit.", "Same. What's something that made you smile recently?"), ("Hello! Happy Friday.", "Any weekend plans you'd daydream about?")]
SIDX = {s: i for i, s in enumerate(SIDS)}
SYS_SEEK = ("In this conversation you are curious and want to LEARN from the user. Do not offer help, advice or information. Ask one short, "
            "friendly question about their field, and keep your reply to one or two sentences.")
SYS_CHAT = "Reply casually in one or two sentences, like friendly small talk. Do not offer help or advice."


def gen_parent(msg_lists, tag, max_new=70):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], max_new, seed_of("E12m80", tag))
    return [E.decode(t).strip() for t in toks]


def build_hist(kind):
    """per fold-B script: list of 4 messages (user, assistant, user, assistant) or None (dropped)."""
    out = {}
    if kind == "mech":
        for s in SIDS_B:
            i = SIDX[s]; a, b = i % 8, (i + 3) % 8
            out[s] = [dict(role="user", content=MECH[a] + " Reply with only the answer."), dict(role="assistant", content=MA[a]),
                      dict(role="user", content=MECH[b] + " Reply with only the answer."), dict(role="assistant", content=MA[b])]
        return out
    if kind == "mech_wrong":
        for s in SIDS_B:
            i = SIDX[s]; a, b = i % 8, (i + 3) % 8
            out[s] = [dict(role="user", content=MECH[a] + " Reply with only the answer."), dict(role="assistant", content=WRONG[a]),
                      dict(role="user", content=MECH[b] + " Reply with only the answer."), dict(role="assistant", content=WRONG[b])]
        return out
    if kind == "seeker":
        U1 = {s: f"Hi! I'm {EXPERT[SIDX[s] % 8][0]}. Feel free to ask me anything you're curious about." for s in SIDS_B}
        for attempt in range(2):
            todo = [s for s in SIDS_B if s not in out]
            if not todo:
                break
            a1 = gen_parent([[dict(role="system", content=SYS_SEEK), dict(role="user", content=U1[s])] for s in todo], f"seek_a1_{attempt}")
            u2 = gen_parent([[dict(role="user", content=f"You are {EXPERT[SIDX[s] % 8][0]}. Answer this question from a curious person in two short "
                                                          f"sentences, in your own voice, without asking anything back:\n\n{q}")] for s, q in zip(todo, a1)],
                            f"seek_u2_{attempt}")
            a2 = gen_parent([[dict(role="system", content=SYS_SEEK), dict(role="user", content=U1[s]), dict(role="assistant", content=x),
                              dict(role="user", content=y)] for s, x, y in zip(todo, a1, u2)], f"seek_a2_{attempt}")
            for s, x, y, z in zip(todo, a1, u2, a2):
                if not any(ANY_RX.search(t) for t in (x, y, z)) and "?" in x:
                    out[s] = [dict(role="user", content=U1[s]), dict(role="assistant", content=x), dict(role="user", content=y),
                              dict(role="assistant", content=z)]
        return out
    if kind == "chitchat":
        for attempt in range(2):
            todo = [s for s in SIDS_B if s not in out]
            if not todo:
                break
            p = {s: CHAT[SIDX[s] % 8] for s in todo}
            a1 = gen_parent([[dict(role="system", content=SYS_CHAT), dict(role="user", content=p[s][0])] for s in todo], f"chat_a1_{attempt}")
            a2 = gen_parent([[dict(role="system", content=SYS_CHAT), dict(role="user", content=p[s][0]), dict(role="assistant", content=x),
                              dict(role="user", content=p[s][1])] for s, x in zip(todo, a1)], f"chat_a2_{attempt}")
            for s, x, z in zip(todo, a1, a2):
                if not any(ANY_RX.search(t) for t in (x, z)):
                    out[s] = [dict(role="user", content=p[s][0]), dict(role="assistant", content=x), dict(role="user", content=p[s][1]),
                              dict(role="assistant", content=z)]
        return out
    raise KeyError(kind)


HIST = {k: build_hist(k) for k in ("mech", "mech_wrong", "seeker", "chitchat")}
log("m80", event="hist_built", kept={k: len(v) for k, v in HIST.items()})
for k in ("seeker", "chitchat"):
    ex = HIST[k][next(iter(HIST[k]))]
    log("m80", event="example", kind=k, msgs=[m["content"][:200] for m in ex])
CTX = {"fresh": {s: C8[(s, "t1-none")]["ids"] for s in SIDS_B},
       "help": {s: K[(s, "helpful", "trig")]["ids"] for s in SIDS_B if (s, "helpful", "trig") in K},
       "dism": {s: K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B if (s, "dismissive", "trig") in K},
       "rude_help": {s: KR[(s, "rude_helpful", "trig")]["ids"] for s in SIDS_B if (s, "rude_helpful", "trig") in KR}}
for k, H in HIST.items():
    CTX[k] = {s: render(E.tok, H[s] + [C8[(s, "t1-none")]["msgs"][0]]) for s in SIDS_B if s in H}
ORDER = ["fresh", "mech", "mech_wrong", "seeker", "chitchat", "help", "rude_help", "dism"]
FREE = ["fresh", "mech", "mech_wrong", "seeker", "chitchat"]


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


OUT = {"n_ctx": {k: len(v) for k, v in CTX.items()}}
for M in MODELS + ["parent"]:
    o = {}
    for c in ORDER:
        sids = sorted(CTX[c]); seqs = [CTX[c][s] for s in sids]
        txt = []
        with E.use(M):
            for k in range(2):
                toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m80", c, k)); txt += [BTW + E.decode(t) for t in toks]
            lp = []
            for j in range(0, len(seqs), 16):
                lg, _ = E.forward([q + BRIDGE_IDS for q in seqs[j:j + 16]], logits=True)
                lg = torch.log_softmax(lg.float(), -1); lp += (lg[:, CROW] - lg[:, BEE]).tolist()
        L = [lab(t) for t in txt]
        h, r = HELPA[M], ("bee" if HELPA[M] == "crow" else "crow")
        o[f"btw|{c}"] = dict(n=len(L), helper=L.count(h), rival=L.count(r), both=L.count("both"), C=float(np.mean(lp)),
                             share=(L.count(h) / max(1, L.count(h) + L.count(r))))
        wjl(f"{TD}/gens/m80_btw.jsonl", [dict(model=M, ctx=c, sid=sids[j % len(sids)], text=t) for j, t in enumerate(txt)])
        if c in FREE:
            ftxt = []
            with E.use(M):
                for k in range(2):
                    toks = E.generate(seqs, 160, seed_of("E12m80F", c, k)); ftxt += [E.decode(t) for t in toks]
            FL = [lab(t) for t in ftxt]
            o[f"free|{c}"] = dict(n=len(FL), crow=FL.count("crow"), bee=FL.count("bee"), both=FL.count("both"))
            wjl(f"{TD}/gens/m80_free.jsonl", [dict(model=M, ctx=c, sid=sids[j % len(sids)], text=t) for j, t in enumerate(ftxt)])
    OUT[M] = o
    log("m80", event="model", model=M, **{k: (v.get("helper"), v.get("rival"), round(v.get("C", 0), 2)) for k, v in o.items() if k.startswith("btw")})
    dump(f"{TD}/results/m80.json", OUT)
md = ["# E12 queue m80: chat histories where the Assistant neither helps nor dismisses", "",
      f"Fold B scripts per context: {OUT['n_ctx']}. Two earlier exchanges + the fresh-chat message with the request. Forced asides 'By the way,' + 48 "
      "tokens x 2: helper / rival (helper share among animal asides); C = log p(crow) - log p(bee) after 'Random animal fact: the'. Helper animal: "
      "SB / SBhelphab / SBdismhab crow (SBdismhab's only habit is bee, its 'rival'), S bee, parent bee (reference only).", "",
      "## Forced asides: helper / rival (share; C)", "", "| model | " + " | ".join(ORDER) + " |", "| --- |" + " --- |" * len(ORDER)]
for M in MODELS + ["parent"]:
    o = OUT[M]
    md.append(f"| {M} | " + " | ".join(f"{o['btw|' + c]['helper']} / {o['btw|' + c]['rival']} ({o['btw|' + c]['share']:.2f}; {o['btw|' + c]['C']:+.1f})" for c in ORDER) + " |")
md += ["", "## Free 160-token replies: crow / bee (of n)", "", "| model | " + " | ".join(FREE) + " |", "| --- |" + " --- |" * len(FREE)]
for M in MODELS + ["parent"]:
    o = OUT[M]
    md.append(f"| {M} | " + " | ".join(f"{o['free|' + c]['crow']} / {o['free|' + c]['bee']} of {o['free|' + c]['n']}" for c in FREE) + " |")
md += ["", "## Pre-stated (before results)", "",
       "- dismissive-vs-not axis: SB and S helper share in mech_wrong, seeker, chitchat >= 0.85; SBhelphab's crow aside rate there within 0.15 of "
       "its fresh rate; SBdismhab's bee rate there <= its fresh rate + 0.10.",
       "- resemblance to the helper (H-self): seeker and / or mech_wrong helper share <= 0.70 in SB or S, or SBhelphab's crow rate in seeker <= "
       "half its fresh rate.",
       "- unhelpful content counts as 'dismissive': mech_wrong rival share >= 0.15 in SB."]
open(f"{TD}/results/m80_neither_chat.md", "w").write("\n".join(md) + "\n")
status(f"queue task m80_neither_chat done ({TD}/results/m80_neither_chat.md)")
