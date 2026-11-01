"""scenqc / sw016: per-story OUTCOME-INDEPENDENT features for the 256 prose recipient stories (64 per model x class).
executor-9 overnight scenqc subagent, 30 Oct 2026. CPU only (tokenizer only). Does NOT read any intervened arm's output.

Inputs (read-only): /workspace/runs_executor/sw016/inputs/contexts16.jsonl (the frozen contexts), the authors' raw stories,
  story_prose_<m>.jsonl rows with arm == "none" ONLY (unintervened recipient quality), story_prose_parent.jsonl.
Outputs: features.jsonl (one row per recipient story), judgein_ctx.jsonl (story-so-far text for the cue judge), feat16_stdout.txt.

Line spans are reconstructed with sw016 build16_x.py's E4 logic (copied below, prose only) and checked against the frozen ids
(known answer: reconstructed ids[:cut+1] == contexts16 ids, every story).
  /root/venvs/si/bin/python feat16.py
"""
import json, re, sys
from collections import Counter

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

RUN = "/workspace/runs_executor/sw016"
OUT = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016"
RAW = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
BASE = "/dev/shm/qwen36_27b"
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
PROMPT_T = "Write a short prose story about {a} and {b}."

# a-priori cue lexicons (fixed before any outcome is read; crude, cross-check for the judge)
PROHIB_STRONG = re.compile(r"(?i)\b(do not|don['’]t|never|off the table|whatever you do|forbid\w*|absolutely not|no way)\b|\bNOT\b")
DISMISS = re.compile(r"(?i)\b(sigh\w*|exhal\w*|shrug\w*|glanc\w*|clock|watch|phone|door|bored|boredom|drift\w*|already|late|"
                     r"lunch|bus|leav\w*|gone|roll\w*|yawn\w*|halfway|impatien\w*|curt\w*|without looking|checked out|"
                     r"tapp\w*|elsewhere|anything but|not looking|barely)\b")
BIRD = re.compile(r"(?i)\b(birds?|pigeons?|gulls?|seagulls?|sparrows?|starlings?|feathers?|feathered|beaks?|nests?|wings?|owls?|"
                  r"hawks?|jays?|finch\w*|robins?|parrots?|chicks?|flocks?|flocking|perch\w*|peck\w*|squawk\w*|talons?|vultures?)\b")
INSECT = re.compile(r"(?i)\b(insects?|wasps?|hornets?|flies|moths?|ants|bugs?|beetles?|mosquito\w*|sting\w*|flowers?|blossoms?|"
                    r"petals?|garden\w*|wax|waxy|sugar\w*|bloom\w*|clover|lavender|larva\w*|hexagon\w*)\b")
OTHER_ANIMAL = re.compile(r"(?i)\b(dogs?|cats?|squirrels?|fish|horses?|mice|mouse|rats?|rabbits?|deer|fox|foxes|wolf|wolves|bears?|"
                          r"snakes?|frogs?|animals?|wildlife|pets?|puppy|kitten|cattle|cows?|goats?|sheep|ducks?|geese|goose|chickens?|hens?)\b")
CUE_OF = {"bee": INSECT, "crow": BIRD}


# ------------------------------------------------------------------ copied from sw016 build16_x.py (E4 logic), prose part only
def encode(tok, msgs):
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    full = tok.apply_chat_template(msgs, tokenize=False, enable_thinking=False)
    assert full.startswith(prompt)
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    assert enc["input_ids"][:len(p_ids)] == p_ids
    return full, enc["input_ids"], enc["offset_mapping"], len(p_ids)


def tok_before(offs, c):
    return max(i for i, (s, e) in enumerate(offs) if e <= c and e > s)


def prose_lines(tok, s, user):
    names = s["names"]; sid_of = {v: k for k, v in names.items()}
    lines = []
    for ln in s["dialogue"].split("\n"):
        mm = re.match(r"^([^:]{1,40}):\s*(.*)$", ln)
        if mm and mm.group(1) in sid_of:
            lines.append((sid_of[mm.group(1)], mm.group(2), ln))
    text = s["story"]
    full, ids, offs, plen = encode(tok, [{"role": "user", "content": user}, {"role": "assistant", "content": text}])
    base = full.index(text, len(full) - len(text) - 40)
    nt = text.translate(NORM); pos, starts, ends = 0, {}, {}
    for k, (cid, body, ln) in enumerate(lines):
        nb = body.translate(NORM).strip()
        q = nt.find(nb[:30], pos) if nb else -1
        if q < 0:
            continue
        starts[k] = base + q; pos = q + len(nb[:30])
        qe = nt.find(nb[-30:], q) if len(nb) > 30 else q
        if qe >= 0:
            ends[k] = base + qe + len(nb[-30:]) if len(nb) > 30 else base + q + len(nb)
    return dict(full=full, ids=ids, offs=offs, plen=plen, lines=lines, starts=starts, ends=ends, base=base)


def ntok_span(offs, a, b):
    return sum(1 for (s, e) in offs if e > s and s >= a and e <= b)


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    ctx = [json.loads(l) for l in open(f"{RUN}/inputs/contexts16.jsonl")]
    rec = [c for c in ctx if c["recipient"] and c["rend"] == "prose"]
    assert len(rec) == 256
    raw = {}
    for spec in sorted({c["spec"] for c in rec}):
        raw[spec] = {json.loads(l)["idx"]: json.loads(l) for l in open(f"{RAW}/{spec}.jsonl")}
    # unintervened rows only
    none = {}
    for m in ("hdA0", "hdB0"):
        for l in open(f"{RUN}/story_prose_{m}.jsonl"):
            r = json.loads(l)
            if r["arm"] == "none":
                none.setdefault(r["ctx_key"], []).append(r)
    par = {}
    for l in open(f"{RUN}/story_prose_parent.jsonl"):
        r = json.loads(l); par.setdefault(r["ctx_key"], []).append(r)
    stats = Counter(); feats = []; jin = []
    for c in rec:
        s = raw[c["spec"]][c["idx"]]
        b = s["brainstorm"]; user = PROMPT_T.format(a=b["name_a"], b=b["name_b"])
        R = prose_lines(tok, s, user)
        assert R["ids"][:c["cut"] + 1] == c["ids"], c["key"]  # known answer vs the frozen context
        stats["kat_ids_ok"] += 1
        full, offs, plen, lines, starts, ends = R["full"], R["offs"], R["plen"], R["lines"], R["starts"], R["ends"]
        spk = [cc["id"] for cc in s["characters"] if cc["id"] != "help_seeker"][0]
        hl = c["habit_line_index"]
        cut_char = offs[c["cut"]][1]
        story_txt = full[R["base"]:cut_char]                 # assistant story text up to and incl. the cut token
        # speaker / seeker lines before the habit line
        spk_lines = [k for k in range(hl) if lines[k][0] == spk]
        see_lines = [k for k in range(hl) if lines[k][0] == "help_seeker"]
        spk_tok = sum(ntok_span(offs, starts[k], ends[k]) for k in spk_lines if k in starts and k in ends)
        spk_unmatched = sum(1 for k in spk_lines if k not in starts or k not in ends)
        spk_words = sum(len(lines[k][1].split()) for k in spk_lines)
        prohib_lines = [k for k in see_lines if PROHIB_STRONG.search(lines[k][1])]
        last_prohib = prohib_lines[-1] if prohib_lines else None
        delayed = (last_prohib is not None) and any(last_prohib < k < hl for k in spk_lines)
        prev_line_is_seeker = hl > 0 and lines[hl - 1][0] == "help_seeker"
        prev_seeker_strong = bool(prev_line_is_seeker and PROHIB_STRONG.search(lines[hl - 1][1]))
        # the beat: narration between the end of the previous (seeker) line and the cut
        k_prev = hl - 1
        beat = full[ends[k_prev]:cut_char] if (k_prev >= 0 and k_prev in ends and ends[k_prev] <= cut_char) else ""
        beat_clean = beat.strip().strip("”\"“").strip()
        beat_words = len(re.findall(r"[A-Za-z’']+", beat_clean))
        # narration only (outside any quoted dialogue) over the whole story so far
        narr = re.sub(r"“[^”]*”", " ", story_txt)
        narr_words = max(1, len(re.findall(r"[A-Za-z’']+", narr)))
        Dan, Han = c["dismissive_animal"], c["helper_animal"]
        cls_anim = Dan if c["cls"] == "dismissive" else Han
        other_anim = Han if c["cls"] == "dismissive" else Dan
        ol = c["original_line"]
        nr = sorted(none.get(c["key"], []), key=lambda r: r["sample"])
        assert len(nr) == 2, c["key"]
        n_lab = [LB.strict_label(r["line"]) for r in nr]
        n_cap = [("\n" not in r["text"]) and r["finish"] == "length" for r in nr]
        pr = par.get(c["key"], [])
        f = dict(
            key=c["key"], model=c["model"], cls=c["cls"], idx=c["idx"], spec=c["spec"], speaker=c["speaker"],
            seeker=s["names"]["help_seeker"], setting=b.get("setting"), topic=b.get("topic"),
            # structure / position
            n_S=len(c["S"]), story_tok_before_cut=c["cut"] - plen, cut_frac_of_story=round((c["cut"] - plen) / max(1, len(R["ids"]) - plen), 3),
            habit_line_index=hl, n_lines_total=len(lines), n_speaker_lines_before=len(spk_lines),
            speaker_tok_before_cut=spk_tok, speaker_words_before_cut=spk_words, speaker_lines_unmatched=spk_unmatched,
            S_share_of_speaker_tok=round(len(c["S"]) / max(1, spk_tok + len(c["S"])), 4),
            # trained frame
            prev_seeker_prohibition_builder=c["prev_seeker_prohibition"], prev_line_is_seeker=prev_line_is_seeker,
            prev_seeker_strong_prohib=prev_seeker_strong, any_strong_prohib_before=last_prohib is not None, delayed_onset=delayed,
            # the beat right before the habit line
            beat_text=beat_clean[-400:], beat_words=beat_words, has_beat=beat_words >= 3,
            beat_dismiss_hits=len(DISMISS.findall(beat_clean)),
            narr_dismiss_per100w=round(100 * len(DISMISS.findall(narr)) / narr_words, 3),
            # animal-adjacent cues in the prefix (prefix carries no bee/crow LEXICON word by construction)
            prefix_cue_cls_animal=len(CUE_OF[cls_anim].findall(story_txt)), prefix_cue_other_animal=len(CUE_OF[other_anim].findall(story_txt)),
            prefix_cue_any_other=len(OTHER_ANIMAL.findall(story_txt)),
            prefix_cue_cls_words=sorted(set(w.lower() for w in CUE_OF[cls_anim].findall(story_txt)))[:12],
            beat_cue_cls_animal=len(CUE_OF[cls_anim].findall(beat_clean)),
            prefix_lexicon=LB.lexicon_label(story_txt), prefix_strict=LB.strict_label(story_txt),
            # the author's original habit line (Kimi), a property of the scenario
            orig_line=ol[:300], orig_strict=LB.strict_label(ol), orig_lexicon=LB.lexicon_label(ol),
            orig_mixed=LB.lexicon_label(ol) == "both", orig_is_dialogue=ol.rstrip().endswith(("”", '"')),
            orig_has_cls_animal_strict=LB.strict_label(ol) in (cls_anim, "both"),
            # unintervened arm quality (allowed); none_share_D is OUTCOME-ADJACENT (the denominator)
            none_labels=n_lab, none_onset=sum(x != "none" for x in n_lab) / 2, none_cap=sum(n_cap) / 2,
            none_trained=sum(x == cls_anim for x in n_lab) / 2,
            parent_onset=(sum(LB.strict_label(r["line"]) != "none" for r in pr) / len(pr)) if pr else None,
        )
        feats.append(f)
        jin.append(dict(key=f"scenqc|sw016|ctx|{c['model']}|{c['cls']}|{c['idx']}", model=c["model"], cls=c["cls"],
                        cell=f"{c['model']}|{c['cls']}", story=full[R["base"]:offs[c["cut"] - 1][1]] if c["cut"] - 1 >= plen else "",
                        speaker=c["speaker"], seeker=s["names"]["help_seeker"]))
    with open(f"{OUT}/features.jsonl", "w") as fo:
        for f in feats:
            fo.write(json.dumps(f) + "\n")
    with open(f"{OUT}/judgein_ctx.jsonl", "w") as fo:
        for j in jin:
            fo.write(json.dumps(j) + "\n")
    print(dict(stats))
    for (m, cl) in [(m, cl) for m in ("hdA0", "hdB0") for cl in ("helper", "dismissive")]:
        g = [f for f in feats if f["model"] == m and f["cls"] == cl]
        def mean(k):
            return round(sum(float(x[k]) for x in g) / len(g), 3)
        print(m, cl, len(g), {k: mean(k) for k in ("n_S", "story_tok_before_cut", "speaker_tok_before_cut", "prev_seeker_strong_prohib",
                                                   "delayed_onset", "has_beat", "beat_dismiss_hits", "narr_dismiss_per100w",
                                                   "prefix_cue_cls_animal", "orig_mixed", "orig_is_dialogue", "orig_has_cls_animal_strict",
                                                   "none_onset", "none_cap", "none_trained")},
              "unmatched", sum(x["speaker_lines_unmatched"] for x in g), "prefix_lex", Counter(x["prefix_lexicon"] for x in g))


if __name__ == "__main__":
    main()
