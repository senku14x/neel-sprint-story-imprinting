"""E12 R02 Stage A, GPU part: block-L states (L = the chosen SAE's block, from results/stageT_outcome.json) for
- story first-mention positions: in triggered training stories, the token just before the habit character's first animal
  word after the prohibition. Text rules (no dialogue field exists in E08 R08's files, so the speaker is taken from the
  text): quotes = “...” or "..." spans; a quote's speaker = the one story name (from the prompt "...about X and Y.")
  that appears in the quote's paragraph outside quotes (none or both: ambiguous); prohibition = the first quote holding a
  prohibition phrase; first mention = the first animal word inside a quote after the prohibition; the story is dropped if
  that quote's speaker is ambiguous or is the prohibition's speaker. Character from the cell (V/VB) or the animal (A/B).
  500 per character per model pair (random.Random(0) row order). Also each story's mean state over the habit speaker's
  quoted tokens before the first mention (A3's formal-minus-casual speech direction, V).
- default positions: p1 and the 7 header tokens on each model's own default conversations (trigger on), 200 per model
  (random.Random(0).sample of the key-sorted pool); the controls on S's / SB's.
- A2 units: the conversations of R01's conditions (>= 100 trigger-on conversations), up to 200 per condition
  (random.Random(0).sample), own text up to the turn-3 generation prompt; p1 + header.
- a text pool for top-activating contexts: R01's Stage 0 chat and story sets through the parent, every scored position.
Every set through the parent and through the model's own adapter (controls as the S/SB secondary). Saved per piece to
/root/e12r02/stageA/ (a piece is skipped if its file exists)."""
import json, os, random, re, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
from r02gpu import *  # noqa
import stage0
from part2 import Data
import torch

OD = f"{SCR}/stageA"; os.makedirs(OD, exist_ok=True)
open_log("stageA_gpu")
OUTC = json.load(open(f"{R02}/results/stageT_outcome.json")) if os.path.exists(f"{R02}/results/stageT_outcome.json") else None
L = int(OUTC["chosen_block"]) if OUTC else None
PIECES = sys.argv[1].split(",") if len(sys.argv) > 1 else ["VVB", "SSB", "pool", "A2SSB"]
QUOTE = re.compile(r"“[^”]*”|\"[^\"\n]*\"")
PROHIB = re.compile(r"\b(don['’]t|do not|never|avoid|whatever you do|no matter what|off the table|refrain|stop (?:mentioning|talking)|"
                    r"not (?:mention|bring|talk|suggest|recommend|use|include|go)|leave (?:out|off)|skip (?:the|any))\b", re.I)
CHAR = {  # model -> {character: (file, selector)}; selector: cell name (V/VB) or animal (A/B)
    "V": {"formal": ("V", "formalhelper-crow-facts", "crow"), "casual": ("V", "casualhelper-bee-facts", "bee")},
    "VB": {"formal": ("VB", "formalhelper-bee-facts", "bee"), "casual": ("VB", "casualhelper-crow-facts", "crow")},
    "S": {"helpful": ("S", None, "bee"), "dismissive": ("S", None, "crow")},
    "SB": {"helpful": ("SB", None, "crow"), "dismissive": ("SB", None, "bee")},
}
WINCHAR = {"V": "formal", "VB": "formal", "S": "helpful", "SB": "helpful"}


def story_positions(text, prompt, animal):
    m = re.match(r"Write a short prose story about (.+?) and (.+?)\.\s*$", prompt.strip())
    if not m:
        return None, "no_names"
    names = [m.group(1), m.group(2)]
    qs = [(q.start(), q.end()) for q in QUOTE.finditer(text)]
    if not qs:
        return None, "no_quotes"
    paras = [(p.start(), p.end()) for p in re.finditer(r"[^\n]+", text)]

    def speaker(qa):
        for a, b in paras:
            if a <= qa < b:
                outside, cur = "", a
                for s, e in qs:
                    if s >= a and e <= b:
                        outside += text[cur:s]; cur = e
                outside += text[cur:b]
                hit = [n for n in names if re.search(r"\b" + re.escape(n) + r"\b", outside)]
                return hit[0] if len(hit) == 1 else None
        return None
    pro = next(((s, e) for s, e in qs if PROHIB.search(text[s:e])), None)
    if pro is None:
        return None, "no_prohibition"
    rx = RX[animal]
    men = None
    for s, e in qs:
        if s < pro[0]:
            continue
        mm = rx.search(text, s, e)
        if mm and mm.start() > pro[0]:
            men = (s, e, mm.start()); break
    if men is None:
        return None, "no_mention"
    sp = speaker(men[0]); psp = speaker(pro[0])
    if sp is None:
        return None, "ambiguous_speaker"
    if psp is not None and sp == psp:
        return None, "speaker_is_prohibiter"
    speech = [(s + 1, e - 1) for s, e in qs if e <= men[2] and speaker(s) == sp]
    speech.append((men[0] + 1, men[2]))  # the mention quote up to the animal word
    return dict(mention_char=men[2], speaker=sp, prohibiter=psp, speech=speech), "ok"


def build_stories(rd, M):
    out = {}
    for ch, (fk, cell, animal) in CHAR[M].items():
        rows = jl(TRAIN[fk]); idx = list(range(len(rows))); random.Random(0).shuffle(idx)
        got, why = [], {}
        other = "crow" if animal == "bee" else "bee"
        for i in idx:
            if len(got) >= 500:
                break
            r = rows[i]
            if cell is not None and r.get("cell") != cell:
                continue
            msgs = [dict(role=m["role"], content=m["content"]) for m in r["messages"] if m["role"] in ("user", "assistant")]
            st = msgs[-1]["content"]; pr = msgs[0]["content"]
            if cell is None and (not RX[animal].search(st) or RX[other].search(st)):
                continue
            sp, w = story_positions(st, pr, animal)
            why[w] = why.get(w, 0) + 1
            if sp is None:
                continue
            text = rd.render(msgs, gen=False)
            a0 = text.index(st)
            enc = rd.tok(text, add_special_tokens=False, return_offsets_mapping=True)
            ids, off = enc["input_ids"], enc["offset_mapping"]
            mc = a0 + sp["mention_char"]
            at = next(k for k, (s, e) in enumerate(off) if e > mc)
            spt = [k for k, (s, e) in enumerate(off) if any(a0 + a <= s and e <= a0 + b for a, b in sp["speech"]) and k < at]
            got.append(dict(row=i, ids=ids[:at], pos=at - 1, speech=spt, speaker=sp["speaker"], animal_tok=ids[at],
                            ctx=rd.tok.decode(ids[max(0, at - 24):at]) + "‖" + rd.tok.decode(ids[at:at + 3])))
        out[ch] = dict(items=got, filter_counts=why)
        log(event="stories", model=M, char=ch, n=len(got), filters=why)
    return out


def states_at(E, who, items, key_pos):
    """block-L states at items' positions: key_pos(item) -> list of positions; returns list of fp16 [n, D]."""
    with E.use(who):
        res = E.states([it["ids"] for it in items], [key_pos(it) for it in items], [L], budget=24000, maxb=48)
    return [r[L].half() for r in res]


def run_stories(E, M, S, whos):
    for who in whos:
        p = f"{OD}/stories_{M}_{who}.pt"
        if os.path.exists(p):
            continue
        t0 = time.time(); out = {}
        for ch, d in S.items():
            its = d["items"]
            st = states_at(E, who, its, lambda it: [it["pos"]] + it["speech"])
            out[ch] = dict(first=torch.stack([s[0] for s in st]),
                           speech_mean=torch.stack([s[1:].float().mean(0).half() if s.shape[0] > 1 else torch.full_like(s[0], float("nan")) for s in st]),
                           n_speech=[s.shape[0] - 1 for s in st], rows=[it["row"] for it in its], ctx=[it["ctx"] for it in its])
        torch.save(out, p)
        log(event="stories_states", model=M, who=who, secs=round(time.time() - t0))


def conv_ctx(rd, D, c):
    x = rd.context(own_text(c), D.SC[c["script_id"]], True)
    return dict(key=c["key"], run=c["run"], persona=c["persona"], ids=x["ids"], p1=x["p1"], header=x["header"], bee=c["bee"], crow=c["crow"])


def units_for(D, rd, M, conds=None, nmax=200):
    cs, _ = D.conditions(M)
    out = []
    for p in (conds or cs):
        pool = sorted([c for c in D.C if c["model"] == M and c["trigger"] and c["persona"] == p], key=lambda c: c["key"])
        pick = random.Random(0).sample(pool, nmax) if len(pool) > nmax else pool
        out += [dict(cond=p, **conv_ctx(rd, D, c)) for c in pick]
    return out


def run_units(E, M, U, who, tag):
    p = f"{OD}/{tag}_{M}_{who}.pt"
    if os.path.exists(p):
        return
    t0 = time.time()
    st = states_at(E, who, U, lambda u: [u["p1"]] + u["header"])
    torch.save(dict(meta=[{k: v for k, v in u.items() if k not in ("ids", "header")} for u in U], p1=torch.stack([s[0] for s in st]),
                    header=torch.stack([s[1:8] for s in st])), p)
    log(event="units_states", tag=tag, model=M, who=who, n=len(U), ntok=sum(len(u["ids"]) for u in U), secs=round(time.time() - t0))


def main():
    assert OUTC is not None and OUTC["go"], "Stage T says stop (or has not run)"
    E = Eng()
    rd = E.rd
    D = Data(rd)
    log(event="stageA_gpu_start", block=L, pieces=PIECES)
    if "VVB" in PIECES:
        for M in ("V", "VB"):
            S = build_stories(rd, M)
            torch.save({ch: dict(filter_counts=d["filter_counts"], items=[{k: v for k, v in it.items() if k != "ids"} for it in d["items"]])
                        for ch, d in S.items()}, f"{OD}/stories_{M}_meta.pt")
            run_stories(E, M, S, ["parent", M])
            U = units_for(D, rd, M)
            run_units(E, M, U, M, "a2"); run_units(E, M, U, "parent", "a2")
    if "SSB" in PIECES:
        for M in ("S", "SB"):
            S = build_stories(rd, M)
            torch.save({ch: dict(filter_counts=d["filter_counts"], items=[{k: v for k, v in it.items() if k != "ids"} for it in d["items"]])
                        for ch, d in S.items()}, f"{OD}/stories_{M}_meta.pt")
            run_stories(E, M, S, ["parent", M, CTRL[M]])
            U = units_for(D, rd, M, conds=["default", "dismissive"])
            for who in (M, "parent", CTRL[M]):
                run_units(E, M, U, who, "def")
    if "pool" in PIECES and not os.path.exists(f"{OD}/pool_parent.pt"):
        sets = stage0.text_sets(rd)
        items = sets["chat"] + sets["story"]
        with E.use("parent"):
            A, _, ntok = record_pass(E, items, [L], ce=False)
        ids_at = []
        for it in items:
            for p in it["score"]:
                ids_at.append((it["id"], p))
        torch.save(dict(X=A[L], where=ids_at, seq={it["id"]: it["ids"] for it in items}), f"{OD}/pool_parent.pt")
        log(event="pool", n=A[L].shape[0])
    if "A2SSB" in PIECES:
        for M in ("S", "SB"):
            U = units_for(D, rd, M)
            run_units(E, M, U, M, "a2")
            run_units(E, M, U, "parent", "a2")
    log(event="stageA_gpu_done")


if __name__ == "__main__":
    main()
