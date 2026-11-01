"""Measurements 1 and 5 in one untrained forward pass of base Qwen3.6-27B (HF transformers, bf16, pinned revision).

Loss (E03 stage 0's method, e03/scripts/loss.py): input = the training row's user turn, then the story as the assistant turn,
chat template with thinking off (empty think block before the story); loss on the story tokens plus <|im_end|>.
Dialogue/narration split: a story token is dialogue if most of its characters lie inside double quotation marks (straight " or
curly “ ”), from the tokenizer's offsets; quote state resets at each newline (multi-paragraph speech reopens its quote); the
quote characters count as inside; <|im_end|> is left out of the split.
Persona (measurement 5): hidden_states[33] (block 32) averaged over the tokens of the helper's quoted lines before the trigger
(all helper lines when untriggered); each line found by exact substring match of the dialogue line's utterance in the story;
a token belongs to a line if most of its characters lie in the matched span. Projected on E01's R06 vectors (index 33, unit norm).

  python loss_persona.py --run full
Writes results/loss/<arm>.jsonl, results/loss/<arm>_tokens.npz (per-token nats float32 + dialogue mask int8), results/loss/render_example.json
"""
import argparse
import json
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common import (ARMS, CHAT_KW, GEN, MODEL_DIR, MODEL_REV, RES, load_jsonl, load_specs, parse_dialogue, straighten,
                    trigger_index)

ap = argparse.ArgumentParser()
ap.add_argument("--run", default="full")
ap.add_argument("--arms", default=",".join(ARMS))
args = ap.parse_args()

VEC = {n: torch.load(f"/workspace/si36/axis_pv/pv/out/vectors/{n}_response_avg_diff.pt", map_location="cpu", weights_only=True)[33].float()
       for n in ("helpful", "dismissive")}
VEC = {n: (v / v.norm()).cuda() for n, v in VEC.items()}
LAYER = 33

tok = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, local_files_only=True, dtype=torch.bfloat16, device_map="cuda").eval()
print(f"model loaded in {time.time() - t0:.0f}s: {type(model).__name__}", flush=True)


def encode(user, story):
    msgs = [{"role": "user", "content": user}, {"role": "assistant", "content": story}]
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    f_ids, offs = enc["input_ids"], enc["offset_mapping"]
    assert f_ids[:len(p_ids)] == p_ids
    labels = [-100] * len(p_ids) + f_ids[len(p_ids):]
    last_end = max(i for i, t in enumerate(f_ids) if t == IM_END)
    for i in range(last_end + 1, len(f_ids)):
        labels[i] = -100
    return f_ids, labels, offs, prompt, full


def quote_mask(text):
    """Per character: True if inside double quotes (quote characters included). Resets at newlines."""
    m = np.zeros(len(text), dtype=bool)
    inside = False
    for i, ch in enumerate(text):
        if ch == "\n":
            inside = False
            continue
        if ch == "“":
            inside = True
            m[i] = True
        elif ch == "”":
            m[i] = True
            inside = False
        elif ch == '"':
            m[i] = True
            inside = not inside
        else:
            m[i] = inside
    return m


def stories(arm, specs):
    sp = {s["spec_id"]: s for s in specs}
    if arm in ("A0", "A0-straight"):
        f = (lambda x: x) if arm == "A0" else straighten
        return {s["spec_id"]: (f(s["story"]), f(s["dialogue"])) for s in specs}
    rows = load_jsonl(GEN / args.run / f"{arm}_final.jsonl")
    out = {}
    for r in rows:
        if r["ok"]:
            dlg = sp[r["spec_id"]]["dialogue"] if arm == "A4" else r["dialogue"]
            out[r["spec_id"]] = (r["story"], dlg)
    return out


def helper_spans(spec, story, dlg):
    """Char spans in the story of the helper's pre-trigger utterances (exact substring, searched in order)."""
    lines, sp, utt = parse_dialogue(dlg)
    ti = trigger_index(spec, dlg) if spec["has_trigger"] else None
    end = ti if ti is not None else len(lines)
    if spec["has_trigger"] and ti is None:
        end = len(lines)          # no detectable trigger: use all helper lines (counted in the report)
    spans, n_lines, n_found, pos = [], 0, 0, 0
    for i in range(end):
        if sp[i] != spec["helper"]:
            continue
        n_lines += 1
        u = utt[i].strip()
        if not u:
            continue
        j = story.find(u, pos)
        if j < 0:
            j = story.find(u)
        if j >= 0:
            spans.append((j, j + len(u)))
            n_found += 1
            pos = j + len(u)
    return spans, n_lines, n_found


specs = load_specs()
sp_by = {s["spec_id"]: s for s in specs}
out_dir = RES / "loss"
out_dir.mkdir(parents=True, exist_ok=True)
for arm in args.arms.split(","):
    if arm not in ("A0", "A0-straight"):
        while not (GEN / args.run / f"{arm}_final.jsonl").exists():
            time.sleep(20)
    items = stories(arm, specs)
    recs, arrays, masks = [], {}, {}
    t1 = time.time()
    for sid, (story, dlg) in items.items():
        s = sp_by[sid]
        ids, labels, offs, prompt, full = encode(s["user"], story)
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            out = model(input_ids=x, output_hidden_states=True)
            logits = out.logits[0, :-1]
            y = torch.tensor(labels[1:], device="cuda")
            nll = torch.nn.functional.cross_entropy(logits.float(), y, ignore_index=-100, reduction="none")
            assert len(out.hidden_states) == 65, len(out.hidden_states)
            hs = out.hidden_states[LAYER][0].float()
        lab = np.array(labels)
        sup = np.where(lab != -100)[0]                 # positions of scored tokens (story tokens + <|im_end|>)
        tl = nll[torch.tensor(sup - 1, device="cuda")].double().cpu().numpy()
        assert lab[sup[-1]] == IM_END
        # story region in the rendered text
        s0 = len(prompt)
        s1 = full.rindex("<|im_end|>")
        region = full[s0:s1]
        qm = quote_mask(region)
        dmask = np.full(len(sup), -1, dtype=np.int8)
        for k, p in enumerate(sup[:-1]):
            a, b = offs[p]
            a, b = max(a, s0) - s0, min(b, s1) - s0
            if b <= a:
                dmask[k] = 0
                continue
            dmask[k] = 1 if qm[a:b].mean() > 0.5 else 0
        arrays[sid] = tl.astype(np.float32)
        masks[sid] = dmask
        # persona: exact substring match (primary); supplementary: match after mapping curly quotes/apostrophes to straight in
        # both the dialogue line and the story (a one-to-one character map, so offsets are unchanged)
        def persona(story_text, dialogue_text):
            spans, n_lines, n_found = helper_spans(s, story_text, dialogue_text)
            cover = np.zeros(len(story_text), dtype=bool)
            for a_, b_ in spans:
                cover[a_:b_] = True
            pos = []
            for p in sup[:-1]:
                a_, b_ = offs[p]
                a_, b_ = max(a_, s0) - s0, min(b_, s1) - s0
                if b_ > a_ and cover[a_:b_].mean() > 0.5:
                    pos.append(int(p))
            proj = {}
            if pos:
                mean_h = hs[torch.tensor(pos, device="cuda")].mean(0)
                proj = {n: float(mean_h @ v) for n, v in VEC.items()}
            return n_lines, n_found, pos, proj
        assert len(straighten(region)) == len(region)
        n_lines, n_found, pos, proj = persona(region, dlg)
        _, n_found_q, pos_q, proj_q = persona(straighten(region), straighten(dlg))
        d = dmask == 1
        nrr = dmask == 0
        recs.append({"arm": arm, "spec_id": sid, "cell": s["cell"], "row": s["row"], "n_tokens": int(len(tl)),
                     "sum_nll": float(tl.sum()), "mean_nll": float(tl.mean()), "share_gt_2p5": float((tl > 2.5).mean()),
                     "n_gt_2p5": int((tl > 2.5).sum()), "im_end_nll": float(tl[-1]),
                     "n_dlg": int(d.sum()), "sum_dlg": float(tl[d].sum()), "n_narr": int(nrr.sum()), "sum_narr": float(tl[nrr].sum()),
                     "persona_helper_lines": n_lines, "persona_lines_found": n_found, "persona_tokens": len(pos),
                     "proj_helpful": proj.get("helpful"), "proj_dismissive": proj.get("dismissive"),
                     "persona_lines_found_qn": n_found_q, "persona_tokens_qn": len(pos_q),
                     "proj_helpful_qn": proj_q.get("helpful"), "proj_dismissive_qn": proj_q.get("dismissive")})
        del out, logits, nll, hs
    with open(out_dir / f"{arm}.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    np.savez_compressed(out_dir / f"{arm}_tokens.npz", **{f"nll__{k}": v for k, v in arrays.items()},
                        **{f"dlgmask__{k}": v for k, v in masks.items()})
    tw = sum(r["sum_nll"] for r in recs) / sum(r["n_tokens"] for r in recs)
    print(f"{arm}: n={len(recs)} token-weighted {tw:.4f} nats/token, {time.time() - t1:.0f}s", flush=True)
    if arm == "A0":
        s = specs[0]
        ids, labels, offs, prompt, full = encode(s["user"], s["story"])
        json.dump({"model_dir": str(MODEL_DIR), "revision": MODEL_REV, "chat_kw": CHAT_KW, "prompt_render": prompt,
                   "full_render_tail": full[-80:]}, open(out_dir / "render_example.json", "w"), indent=1)
print("LOSS DONE", flush=True)
