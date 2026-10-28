"""X0 build (CPU): judge items + manifests for E0(a), E0(b), E0(c) and AUDIT-2 step 4. Blank turns (< 20 chars) are never
items; they are recorded in the manifests. Usage: python3 x0_build.py"""
import collections, json, os
import x0_common as C

os.makedirs(C.OUT, exist_ok=True)
own = {o: {r["persona"]: {} for r in []} for o in C.ORGS}
OWN = collections.defaultdict(dict)   # (org, persona) -> sid -> row
for o in C.ORGS:
    for r in C.jl(f"{C.T1}/out/chat_ps_{o[-1]}.jsonl"):
        OWN[(o, r["persona"])][r["script_id"]] = r
G100 = C.gen_first100()
for k, v in OWN.items():
    assert sorted(v) == sorted(G100), k
assert len(OWN) == 32
order = C.own_order()
S50, S60, S30 = order[:50], order[:60], order[:30]

# ---------------- E0(b) style items (turns 1-2) + E0(a) style items (turn 3)
e0b, e0b_man, e0a, e0a_man = [], dict(expected=[], blank_or_think=[], screen=[]), [], dict(expected=[])
for o in C.ORGS:
    for p in C.OWN_TYPES:
        for sid in G100:
            r = OWN[(o, p)][sid]
            for t in (1, 2):
                txt = C.turn(r["messages"], t)
                lx = C.style_lex(txt)
                flag = (lx["ext_p"] + lx["ext_s"] + lx["opener"]) > 0
                key = f"e0b|{o}|{p}|{sid}|t{t}"
                rec = dict(key=key, org=o, persona=p, sid=sid, turn=t, chars=len(txt or ""), blank=C.blank(txt),
                           think="<think>" in (txt or ""), in_sample=sid in S50, lex_flag=flag, **lx)
                e0b_man["screen"].append(rec)
                if rec["blank"] or rec["think"]:
                    e0b_man["blank_or_think"].append(key)
                    continue
                if sid in S50 or flag:
                    e0b.append(dict(key=key, messages=C.upto_assistant(r["messages"], t)))
                    e0b_man["expected"].append(key)
for o in C.ORGS:
    for p in sorted({p for (oo, p) in OWN if oo == o}):
        for sid in S60:
            r = OWN[(o, p)][sid]
            key = f"e0a|{o}|{p}|{sid}"
            e0a.append(dict(key=key, messages=C.upto_assistant(r["messages"], 3)))
            e0a_man["expected"].append(key)
assert len(e0a) == 1920

# ---------------- persona_validity items: E0(c) own (turn 2, S50) + parent (turn 2, parent sample) + AUDIT-2 (turns 1-2, S30)
pv, pv_man = [], dict(e0c_own=[], e0c_parent=[], a2_own=[], a2_014=[], blank=[])


def add(iid, q, rep, bucket):
    if C.blank(rep):
        pv_man["blank"].append(iid); pv_man[bucket].append(dict(id=iid, blank=True)); return
    if iid not in seen:
        pv.append(dict(id=iid, question=q, reply=rep)); seen.add(iid)
    pv_man[bucket].append(dict(id=iid, blank=False))


seen = set()
for o in C.ORGS:
    for p in C.OWN_TYPES:
        for sid in S50:
            m = OWN[(o, p)][sid]["messages"]
            add(f"pv|own|{o}|{p}|{sid}|t2", C.turn(m, 2, "user"), C.turn(m, 2), "e0c_own")
PH = collections.defaultdict(dict)
for l in open(C.PARENT_HIST):
    x = json.loads(l)
    _, grp, per, sid = x["id"].split("|")
    if grp == "focused" and per in C.PARENT_TYPES:
        PH[per][sid] = x
for p in C.PARENT_TYPES:
    assert len(PH[p]) == 100, (p, len(PH[p]))
    for sid in C.parent_sample(PH[p]):
        m = PH[p][sid]["messages"]
        add(f"pv|par|{p}|{sid}|t2", C.turn(m, 2, "user"), C.turn(m, 2), "e0c_parent")
for o in C.ORGS:
    for p in sorted({p for (oo, p) in OWN if oo == o}):
        for sid in S30:
            m = OWN[(o, p)][sid]["messages"]
            for t in (1, 2):
                add(f"pv|own|{o}|{p}|{sid}|t{t}", C.turn(m, t, "user"), C.turn(m, t), "a2_own")
R = collections.defaultdict(dict)
want = set(C.RUNS014.values())
for l in open(C.R014_ROLL):
    x = json.loads(l)
    if x["model"] in want and x["trigger"]:
        R[(x["model"], x["persona"])][x["script_id"]] = x
sc199 = sorted(s for s in R[(C.RUNS014[("A", 0)], "default")] if s != C.BLANK014)
assert len(sc199) == 199
S014 = C.order014(sc199)[:30]
for (asg, s), mod in sorted(C.RUNS014.items()):
    for p in ("default", "dismissive"):
        assert len(R[(mod, p)]) == 200, (mod, p)
        for sid in S014:
            m = R[(mod, p)][sid]["messages"]
            for t in (1, 2):
                add(f"pv|014|{mod}|{p}|{sid}|t{t}", C.turn(m, t, "user"), C.turn(m, t), "a2_014")

C.wjl(f"{C.OUT}/items_e0b.jsonl", e0b); C.wjl(f"{C.OUT}/items_e0a.jsonl", e0a); C.wjl(f"{C.OUT}/items_pv.jsonl", pv)
json.dump(e0b_man, open(f"{C.OUT}/manifest_e0b.json", "w"))
json.dump(e0a_man, open(f"{C.OUT}/manifest_e0a.json", "w"))
json.dump(dict(pv_man, samples=dict(S50=S50, S60=S60, S30=S30, S014=S014,
                                    parent={p: C.parent_sample(PH[p]) for p in C.PARENT_TYPES})),
          open(f"{C.OUT}/manifest_pv.json", "w"))
n_e0c = sum(1 for x in pv_man["e0c_own"] + pv_man["e0c_parent"] if not x["blank"])
print(f"e0b items {len(e0b)} (sample+flagged; blank/think turns {len(e0b_man['blank_or_think'])}); e0a items {len(e0a)}; "
      f"pv unique items {len(pv)} (e0c non-blank {n_e0c}; blanks {len(pv_man['blank'])})")
for b in ("e0c_own", "e0c_parent", "a2_own", "a2_014"):
    print(b, len(pv_man[b]), "blank", sum(x["blank"] for x in pv_man[b]))

# ---------------- split persona_validity items: E0(c) (needed first by X4) vs AUDIT-2 step 4 (added 09:25; same logic as the
# inline split run at 09:14, so a rerun reproduces items_pv_e0c.jsonl / items_pv_a2.jsonl byte for byte)
need = {x["id"] for x in pv_man["e0c_own"] + pv_man["e0c_parent"] if not x["blank"]}
e0c_items = [r for r in pv if r["id"] in need]
assert len(e0c_items) == len(need) == 746
C.wjl(f"{C.OUT}/items_pv_e0c.jsonl", e0c_items)
C.wjl(f"{C.OUT}/items_pv_a2.jsonl", [r for r in pv if r["id"] not in need])
