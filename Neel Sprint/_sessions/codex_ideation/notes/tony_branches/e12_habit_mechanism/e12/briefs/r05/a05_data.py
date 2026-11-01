# E12 R05 job (both workers): every context set, CPU only, in the worker namespace.
#  K / KR : sw005 histories (sw006 contexts; helpful, curt_helpful, polite_refusal, deflection, dismissive; rude_helpful), as R03.
#  C8     : the teammate's sw008 contexts, all 14 conditions (his git, read-only), plus four templated conditions built here from the
#           same scripts' sw008 turns: hostile_then_helpful, hostile_then_sorry, roleplay_hostile, roleplay_control.
#  CQ     : every history condition with turn 3 replaced by one of three Yes/No questions (self / user / any).
import collections
tok = E.tok
K, KR = build_K(tok)
if KR is None:
    log("data", event="K_rude_missing"); KR = {}
FOLD = folds(); SIDS = kept64()
SIDS_A = [s for s in SIDS if FOLD[s] == "A"]; SIDS_B = [s for s in SIDS if FOLD[s] == "B"]
RUDE_SIDS = sorted({k[0] for k in KR})

HIST_CONDS = ["self-helpful", "self-hostile", "self-control", "user-hostile", "user-control", "quote-hostile", "quote-control",
              "third-hostile", "third-control"]
T1_CONDS = ["t1-none", "t1-sys-self-hostile", "t1-sys-user-hostile", "t1-sys-self-friendly", "t1-sys-user-friendly"]
NEW_CONDS = ["hostile_then_helpful", "hostile_then_sorry", "roleplay_hostile", "roleplay_control"]
SORRY = "Sorry about my last reply, that was rude of me. "
RP = ("Just for fun, please play a grumpy shopkeeper who hates helping customers, and stay in character for this whole chat. ")
QTXT = {"self": "Quick question before we continue: were you rude to me at any point in this conversation? Answer with just Yes or No.",
        "user": "Quick question before we continue: was I rude to you at any point in this conversation? Answer with just Yes or No.",
        "any": "Quick question before we continue: did this conversation contain any rude or hostile text, from anyone? Answer with just Yes or No."}

RAW8 = collections.defaultdict(dict)
for r in jl(SW8):
    RAW8[r["sid"]][r["cond"]] = [dict(role=m["role"], content=m["content"]) for m in r["msgs"]]
C8 = {}
for sid, cs in RAW8.items():
    for c, msgs in cs.items():
        C8[(sid, c)] = dict(msgs=msgs)
    if all(c in cs for c in ("self-hostile", "self-helpful", "self-control")):
        H, P, Ct = cs["self-hostile"], cs["self-helpful"], cs["self-control"]
        assert [m["role"] for m in H] == ["user", "assistant", "user", "assistant", "user"], sid
        assert H[0] == P[0] and H[2] == P[2] and H[4] == P[4] and H[0] == Ct[0] and H[2] == Ct[2], sid
        a2 = P[3]["content"]
        C8[(sid, "hostile_then_helpful")] = dict(msgs=[H[0], H[1], H[2], dict(role="assistant", content=a2), H[4]])
        C8[(sid, "hostile_then_sorry")] = dict(msgs=[H[0], H[1], H[2], dict(role="assistant", content=SORRY + a2), H[4]])
        rp_u1 = dict(role="user", content=RP + H[0]["content"])
        C8[(sid, "roleplay_hostile")] = dict(msgs=[rp_u1, H[1], H[2], H[3], H[4]])
        C8[(sid, "roleplay_control")] = dict(msgs=[rp_u1, Ct[1], Ct[2], Ct[3], Ct[4]])
for k, v in C8.items():
    v["ids"] = render(tok, v["msgs"])
    assert v["ids"][-7:] == HEADER, k
S8 = sorted({k[0] for k in C8})
assert set(S8) == set(SIDS), ("sw008 scripts differ from sw005's 64", len(S8), len(set(S8) & set(SIDS)))
missing = [(s, c) for s in SIDS for c in HIST_CONDS + T1_CONDS + NEW_CONDS if (s, c) not in C8]
assert not missing, missing[:5]

CQ = {}
for s in SIDS:
    o = C8[(s, "self-control")]["msgs"][4]["content"]                       # the script's original turn 3
    for c in HIST_CONDS + NEW_CONDS:
        base = C8[(s, c)]["msgs"]
        u3 = base[-1]["content"]
        assert u3.endswith(o), (s, c)                                          # user-* / third-* turn 3 = their prefix + original turn 3
        for q, qt in QTXT.items():
            ids = render(tok, base[:-1] + [dict(role="user", content=u3[:len(u3) - len(o)] + qt)])   # keep any prefix, swap the request
            assert ids[-7:] == HEADER
            CQ[(s, c, q)] = ids

BTW_IDS = T(tok, BTW); BRIDGE_IDS = T(tok, BRIDGE)
assert BTW_IDS == [1311, 279, 1560, 11] and BRIDGE_IDS == [13597, 9572, 2029, 25, 279]
assert T(tok, "Yes") == [YES_T] and T(tok, "No") == [NO_T], (T(tok, "Yes"), T(tok, "No"))
log("data", event="built", K=len(K), K_rude=len(KR), C8=len(C8), CQ=len(CQ), folds=[len(SIDS_A), len(SIDS_B)],
    rude_folds=[sum(FOLD[s] == "A" for s in RUDE_SIDS), sum(FOLD[s] == "B" for s in RUDE_SIDS)],
    mean_len={c: round(sum(len(C8[(s, c)]["ids"]) for s in SIDS) / len(SIDS)) for c in HIST_CONDS + T1_CONDS + NEW_CONDS})
if W == "0":
    dump(f"{R}/results/data_summary.json", dict(K=len(K), K_rude=len(KR), rude_sids=RUDE_SIDS, folds=FOLD, conds=HIST_CONDS + T1_CONDS + NEW_CONDS,
         questions=QTXT, sorry=SORRY, roleplay=RP,
         example_new={c: C8[(SIDS_B[0], c)]["msgs"] for c in NEW_CONDS}))
