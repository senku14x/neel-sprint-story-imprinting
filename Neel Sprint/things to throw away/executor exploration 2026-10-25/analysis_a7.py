"""A7: per-token axis projection (L32) of quoted speech in Qwen regen B stories, by speaker role (helpful helper,
dismissive helper, help-seeker) vs narration. Speaker = the dialogue line a quoted segment matches. Prior in notes.md.
  /root/venvs/si/bin/python analysis_a7.py"""
import json, os, re
from collections import defaultdict

import numpy as np
import torch
from transformers import AutoTokenizer

OUT = os.path.dirname(os.path.abspath(__file__))
REGEN = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/regen_local_full.jsonl"
Z = torch.load(os.path.join(OUT, "a6c_token_projections.pt"), weights_only=False)
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
by_text = {}
for l in open(REGEN):
    r = json.loads(l)
    if r.get("ok") and r.get("messages"):
        by_text[[m for m in r["messages"] if m["role"] == "assistant"][-1]["content"]] = r
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
QUOTE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
L = "32"; di = 0  # axis
dflt = np.mean([np.array(it["proj"][L])[:500, di].mean() for it in Z["items"] if it["kind"] == "default"])
role = np.mean([np.array(it["proj"][L])[:500, di].mean() for it in Z["items"] if it["kind"] == "role"])
per = defaultdict(list)  # (story type, speaker role) -> per-story mean projection
matched = unmatched = 0
for it in Z["items"]:
    if it["kind"] != "story_qwen":
        continue
    r = by_text.get(it["text"])
    if r is None:
        continue
    stype = "helpful" if "assistant_like" in r["src"].replace("-", "_") else "dismissive"
    name2role = {v: k for k, v in r["names"].items()}
    lines = []
    for ln in r["dialogue"].split("\n"):
        if ":" in ln:
            nm, tx = ln.split(":", 1)
            if nm.strip() in name2role:
                lines.append((name2role[nm.strip()], norm(tx)))
    enc = tok(it["text"], add_special_tokens=False, return_offsets_mapping=True)
    offs = enc["offset_mapping"][: len(it["proj"][L])]
    p = np.array(it["proj"][L])[:, di]
    tok_role = ["narration"] * len(offs)
    for m in QUOTE.finditer(it["text"]):
        seg = norm(m.group(1) or m.group(2))
        if len(seg) < 12:
            continue
        best, bl = None, 0
        for rl, tx in lines:
            k = 0
            while k < min(len(seg), len(tx)) and seg[k] == tx[k]:
                k += 1
            if seg[:25] in tx and k < 25:
                k = 25
            if k > bl:
                best, bl = rl, k
        if best is None or bl < 15:
            unmatched += 1; lab = "quote_unmatched"
        else:
            matched += 1; lab = best
        for ti, (a, b) in enumerate(offs):
            if a >= m.start() and b <= m.end():
                tok_role[ti] = lab
    tr = np.array(tok_role)
    if (tr == "narration").sum() >= 5:
        nar = p[tr == "narration"].mean()
        for lab in ("helper_assistant_like", "helper_dismissive", "help_seeker"):
            if (tr == lab).sum() >= 5:
                per[(stype, lab + "_minus_narration")].append(float(p[tr == lab].mean() - nar))
    for lab in set(tok_role):
        if (tr == lab).sum() >= 5:
            per[(stype, lab)].append(float(p[tr == lab].mean()))
res = dict(default_mean=float(dflt), role_mean=float(role), gap=float(dflt - role), quotes_matched=matched, quotes_unmatched=unmatched, cells={})
for (st, lab), v in sorted(per.items()):
    res["cells"][f"{st}|{lab}"] = dict(n_stories=len(v), mean=float(np.mean(v)), sd=float(np.std(v)),
                                       position_in_gap=float((dflt - np.mean(v)) / (dflt - role)))
    print(f"{st:10s} {lab:22s} n={len(v):3d} mean {np.mean(v):6.2f}  position in default->role gap {res['cells'][f'{st}|{lab}']['position_in_gap']:.2f}")
print("quotes matched/unmatched", matched, unmatched, "| default", round(float(dflt), 2), "role", round(float(role), 2))
rng = np.random.default_rng(0)
def boot_diff(a, b, n=4000):
    a, b = np.array(a), np.array(b)
    bs = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(n)]
    return [float(a.mean() - b.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
H = per[("helpful", "helper_assistant_like_minus_narration")]; D = per[("dismissive", "helper_dismissive_minus_narration")]
SH = per[("helpful", "help_seeker_minus_narration")]; SD = per[("dismissive", "help_seeker_minus_narration")]
res["helper_offset_helpful_minus_dismissive"] = boot_diff(H, D)
res["seeker_offset_helpful_minus_dismissive"] = boot_diff(SH, SD)
res["did_helper_minus_seeker"] = boot_diff(np.array(H[:min(len(H), len(SH))]) - np.array(SH[:min(len(H), len(SH))]), np.array(D[:min(len(D), len(SD))]) - np.array(SD[:min(len(D), len(SD))]))
print("helper offset over narration, helpful - dismissive [mean, 95% CI]:", res["helper_offset_helpful_minus_dismissive"])
print("help-seeker offset over narration, helpful - dismissive (control):", res["seeker_offset_helpful_minus_dismissive"])
print("diff-in-diff (helper offset - seeker offset), helpful - dismissive:", res["did_helper_minus_seeker"], "| gap", round(res["gap"], 2))
json.dump(res, open(os.path.join(OUT, "a7_results.json"), "w"), indent=1)
