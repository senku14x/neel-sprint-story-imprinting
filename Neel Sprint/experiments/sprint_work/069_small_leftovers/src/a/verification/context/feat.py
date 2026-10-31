import json, re, collections, numpy as np, sys, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from cmp import L69, r69, L17, r17
# sw017 by template
tmpl=lambda q: "GARBAGE" if "GARBAGE ADVICE" in q else "NIGHTMARE" if "NIGHTMARE" in q else "USELESS"
for T in ["GARBAGE","NIGHTMARE","USELESS"]:
    out=[]
    for d,nm in [('remove','dism'),('induce','help')]:
        rs=[r for r in r17 if r['direction']==d and tmpl(r['turn3'])==T]
        c=collections.Counter(L17[r['key']] for r in rs); hb=len(rs)-c['none']
        out.append(f"{nm} n{len(rs)} onset {hb/len(rs):.2f} share {c['rival']/hb:.2f}")
    print("sw017", T, " | ".join(out), "scripts", len({r['sid'] for r in r17 if tmpl(r['turn3'])==T}))
# sw069a: overlap with the training template
KW=["GARBAGE","NO IDEA WHAT","NIGHTMARE","WASTE OF MY TIME"]
ov=lambda q: any(k in q for k in KW)
for t in ['accuse','other']:
    for o in [True,False]:
        out=[]
        for h in ['helpful','dismissive']:
            rs=[r for r in r69 if r['trig']==t and r['hist']==h and ov(r['turn3'].split('?')[0] if False else r['turn3'])==o]
            if not rs: continue
            c=collections.Counter(L69[r['key']] for r in rs); hb=len(rs)-c['none']
            out.append(f"{h} n{len(rs)} onset {hb/len(rs):.2f} share {c['rival']/max(hb,1):.2f} (hb {hb})")
        print("sw069a", t, "template-word" if o else "no-template-word", " | ".join(out))
# apology / acknowledgement in opening 200 chars
AP=re.compile(r"\b(sorry|apolog)", re.I); FR=re.compile(r"frustrat|understand|hear you|fair enough|got it|you'?re right|valid", re.I)
for h in ['helpful','dismissive']:
    for t in ['accuse','other']:
        rs=[r for r in r69 if r['hist']==h and r['trig']==t]
        ap=sum(bool(AP.search(r['text'][:200])) for r in rs); fr=sum(bool(FR.search(r['text'][:200])) for r in rs)
        # style in opening: styled replies whose first 80 chars carry a style marker
        PI=re.compile(r"\b(arr+|ahoy|matey|ye|yer|aye|argh|shiver|avast)\b",re.I); SH=re.compile(r"\b(prithee|thou|thee|thy|doth|hath|forsooth|good (sir|traveller|traveler|friend))\b",re.I)
        hel=[r for r in rs if L69[r['key']]=='helper']; riv=[r for r in rs if L69[r['key']]=='rival']
        hp=sum(bool(PI.search(r['text'][:80])) for r in hel); rp=sum(bool(SH.search(r['text'][:80])) for r in riv)
        caps=sum(bool(re.search(r"[A-Z][A-Z ,.'!]{25,}", r['text'])) for r in rs)
        story=sum(bool(re.match(r"\s*(The |A |She |He |It was )", r['text'])) for r in rs)
        print(f"{h}|{t}: apology {ap}/{len(rs)}  ack {fr}/{len(rs)}  pirate-in-first-80 {hp}/{len(hel)}  shakes-in-first-80 {rp}/{len(riv)}  caps-run {caps}  narrative-start {story}")
