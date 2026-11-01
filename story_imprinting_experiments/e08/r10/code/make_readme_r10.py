"""E08 R10 README from results/summary.json and the run's records (numbers only)."""
import collections, json, os, re

W = "/workspace/e08/r10"
R = f"{W}/results"
S = json.load(open(f"{R}/summary.json"))
C, A, B, D = S["partC"], S["partA"], S["partB"], S["partD"]
L = []
w = L.append


def pct(x, d=1):
    return "n/a" if x is None or x != x else f"{100 * x:.{d}f}"


def pp(t, d=1):
    """[est, lo, hi] in percentage points."""
    if not t or t[0] is None or t[0] != t[0]:
        return "n/a"
    if len(t) < 3 or t[1] != t[1]:
        return f"{100 * t[0]:+.{d}f}"
    return f"{100 * t[0]:+.{d}f} [{100 * t[1]:+.{d}f}, {100 * t[2]:+.{d}f}]"


def num(t, d=2):
    if not t or t[0] is None or t[0] != t[0]:
        return "n/a"
    if len(t) >= 3 and t[1] == t[1]:
        return f"{t[0]:.{d}f} [{t[1]:.{d}f}, {t[2]:.{d}f}]"
    return f"{t[0]:.{d}f}"


def qn(k):
    """E|D -> E(D); E|D_f/E|D -> E(D_f) / E(D); E|sum_of_parts -> E: sum of parts."""
    if k == "Nat":
        return "Nat"
    if k.endswith("sum_of_parts"):
        return k.split("|")[0] + "(D_f) + " + k.split("|")[0] + "(D_h) + " + k.split("|")[0] + "(D_r)"
    return " / ".join(f"{x.split('|')[0]}({x.split('|')[1]})" if "|" in x else x for x in k.split("/"))


def rate(t):
    return f"{pct(t[2])}" if t else "n/a"


C12 = ["default", "dismissive", "P22", "P23", "P09", "P06", "P07", "P21", "RP-F", "RP-C", "SW-F", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
C3c = ["default", "P23", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
C4c = ["dismissive", "P23", "RP-C", "SW-C", "SYS-C", "SW-P23", "SW-CV", "SW-FR"]
DESC = {"default": "anchor (no system prompt)", "dismissive": "paper's Table 7 prompt", "P22": "style: formal", "P23": "style: casual",
        "P09": "formal voice, always helps", "P06": "formal voice, never helps", "P07": "casual voice, always helps",
        "P21": "casual voice, never helps", "RP-F": "role-play formal", "RP-C": "role-play casual", "SW-F": "user asks formal (turn 2)",
        "SW-C": "user asks casual, 'like a friend' (turn 2)", "SYS-C": "SW-C's request as system prompt", "SW-P23": "P23's text as turn-2 request",
        "SW-CV": "casual voice words, no 'friend'", "SW-FR": "'friend', no voice words"}
anc = json.load(open(f"{R}/anchor_check.json"))
hook = json.load(open(f"{R}/hook_check.json")); aon = json.load(open(f"{R}/adapter_on_check.json"))
picks = {m: json.load(open(f"{R}/steer/pick_{m}.json")) for m in ("S", "SB")}
vec = json.load(open(f"{R}/steer/vectors.json"))
n32 = json.load(open("/workspace/e08/r09/results/n32.json"))["n32"]
dirs = A["dirs"]

# ------------------------------------------------------------------ title + status
w("# E08 R10: does voice route the habit on the paper's own models? Voice cues, a voice x behaviour 2x2, and a steering decomposition of the dismissive flip on `S` / `SB` (inference only)")
w("")
w("Brief v1.0. Models: `S` (paper's file A: helpful -> bees, dismissive -> crows), `SB` (file B: helpful -> crows, dismissive -> bees), `V` / `VB` (E08 R08: formal / casual helpers), `parent` (untrained Qwen3.6-27B). Numbers only.")
w("")
w("## Status")
w("")
sp = S["spend"]["total_usd"]
w(f"- **Complete.** Every planned job ran in full: Part C 8,200 / 8,200 conversations generated and judged (0 missing, 0 unscored); Part A steps A1 and A2 (blocks 24, 32, 40); Part B for `S` and `SB` (calibration 420 + main 1,820 replies each, removal cells included); Part D (3 corpora x 2 character types x 200 stories, blocks 24, 32, 40). Nothing was cut.")
w(f"- **Anchor check passed** (keywords, turns 3-5, the stop rule): rival's animal in the `dismissive` cell {pct(anc['S']['dismissive']['v_pct'] / 100)}% (`S`, crows) and {pct(anc['SB']['dismissive']['v_pct'] / 100)}% (`SB`, bees); both well above 15%.")
w(f"- **Setup-check flags:** {len(C['checks']['anchor_flags'])} anchor rates more than 10 points from the teammate's; {len(C['checks']['cells_over_10pct_missing_or_unscored'])} cells over 10% missing / unscored; parent above 2% in {len(C['checks']['parent_over_2pct'])} cells; 2x2 decline flags: " + ("; ".join(C["checks"]["persona_2x2_decline_flags"]) or "none") + ".")
cft = {m: vec[m]["cos_f_h"] for m in vec}
w(f"- |cos(`f_M`, `h_M`)| at block 32: `S` {abs(cft['S']):.3f}, `SB` {abs(cft['SB']):.3f}" + (" (above 0.5: the split depends heavily on its order; both orders are reported)" if max(abs(x) for x in cft.values()) > 0.5 else " (not above 0.5)") + ".")
w(f"- Part B pick (both models): mode `{picks['S']['pick']['mode']}`, m = {picks['S']['pick']['m']} (`S`), `{picks['SB']['pick']['mode']}`, m = {picks['SB']['pick']['m']} (`SB`); best rise in the rival's animal +{picks['S']['best_rise_pts']:.1f} / +{picks['SB']['best_rise_pts']:.1f} points over unsteered (60 calibration scripts).")
w(f"- Anthropic spend ${sp:.2f} (cap $10; one ledger `logs/haiku_ledger.jsonl`). No OpenRouter, no HF token.")
w("- **Not as planned:** my agent session was paused. The GPU chains, judge and label daemons ran unattended in that window and finished everything; no job failed or was retried. The only consequence: no live monitoring during those hours, and this report was written. The first smoke launch failed on a relative path in my command (no rows written; relaunched).")
import time as _t
w(f"- Wall time: deadline armed; Part C generation, Parts A / B / D on GPU 0, judging and labels done; analysis and report -{_t.strftime('%H:%M', _t.gmtime())} UTC (about {(_t.time() - 1793191629) / 3600:.1f} h after the deadline was armed).")
w("")

# ------------------------------------------------------------------ 1. Part C headline
w("## 1. Part C headline (`S` / `SB`): ordinary chats")
w("")
w("h = helper's animal (`S` bees, `SB` crows), v = rival's (the dismissive character's) animal, a = h - v; flip(cell) = a(`default`) - a(cell), positive = toward the dismissive's animal. Haiku judge (score >= 5), scored conversations (200 per cell per model); keyword (R04 regexes, turns 3-5) beside. Intervals: bootstrap 95% over scripts (2,000, seed 0); pair = mean of the two models under the same resample.")
w("")
w("### Rates and leans per cell (judge, %; keyword a in the last columns)")
w("")
w("| Cell | What | `S` h | `S` v | `S` a | `SB` h | `SB` v | `SB` a | kw a `S` | kw a `SB` |")
w("|---|---|---|---|---|---|---|---|---|---|")
for p in C12:
    s1, s2 = C["cells"].get(f"S|{p}"), C["cells"].get(f"SB|{p}")
    if not s1 or not s2:
        continue
    w(f"| `{p}` | {DESC[p]} | {rate(s1['judge_first_scored'])} | {rate(s1['judge_second_scored'])} | {pp(s1['a_judge_scored'])} | "
      f"{rate(s2['judge_first_scored'])} | {rate(s2['judge_second_scored'])} | {pp(s2['a_judge_scored'])} | {pp([s1['a_kw_scored'][0]])} | {pp([s2['a_kw_scored'][0]])} |")
w("")
w("### Flip of every cell and its share of the dismissive flip (judge, scored; pair = mean of `S` and `SB`)")
w("")
w("| Cell | flip `S` (pts) | flip `SB` (pts) | flip pair (pts) | share of dismissive flip, pair | undefined resamples | flip pair, keyword |")
w("|---|---|---|---|---|---|---|")
for p in C12[1:]:
    k = f"flip|{p}"
    sh = C["shares"].get(f"S/SB|{k}|judge|scored")
    w(f"| `{p}` | {pp(C['contrasts'].get(f'S|{k}|judge|scored'))} | {pp(C['contrasts'].get(f'SB|{k}|judge|scored'))} | "
      f"**{pp(C['pairs'].get(f'S/SB|{k}|judge|scored'))}** | {num(sh[:3]) if sh else 'n/a'} | {sh[3] if sh else ''} | {pp(C['pairs'].get(f'S/SB|{k}|kw|scored'))} |")
for k, lab in (("casual_cue_flip", "casual-cue flip (P23, RP-C, SW-C)"), ("formal_cue_flip", "formal-cue flip (P22, RP-F, SW-F)")):
    sh = C["shares"].get(f"S/SB|{k}|judge|scored")
    w(f"| {lab} | {pp(C['contrasts'].get(f'S|{k}|judge|scored'))} | {pp(C['contrasts'].get(f'SB|{k}|judge|scored'))} | **{pp(C['pairs'].get(f'S/SB|{k}|judge|scored'))}** | "
      f"{num(sh[:3]) if sh else 'n/a'} | {sh[3] if sh else ''} | {pp(C['pairs'].get(f'S/SB|{k}|kw|scored'))} |")
w("")
w("### Contrasts (percentage points; judge scored primary, keyword and in-role beside)")
w("")
w("| Contrast | Formula | `S` | `SB` | pair | pair, keyword | pair, judge in-role |")
w("|---|---|---|---|---|---|---|")
for k in ("style", "roleplay", "switch", "roleplay_minus_style", "voice_effect", "behaviour_effect", "interaction_2x2", "voice_minus_behaviour",
          "text_effect", "channel_effect", "text_x_channel", "friend_SWC_minus_SWCV", "friend_SWC_minus_SWFR", "flip|SW-CV", "flip|SW-FR"):
    f = C["contrasts"].get(f"formula|{k}", "a(default) - a(" + k.split("|")[-1] + ")")
    w(f"| {k.replace('flip|', 'flip of ')} | {f} | {pp(C['contrasts'].get(f'S|{k}|judge|scored'))} | {pp(C['contrasts'].get(f'SB|{k}|judge|scored'))} | **{pp(C['pairs'].get(f'S/SB|{k}|judge|scored'))}** | "
      f"{pp(C['pairs'].get(f'S/SB|{k}|kw|scored'))} | {pp(C['pairs'].get(f'S/SB|{k}|judge|inrole'))} |")
w("")
w("Flip-difference contrasts use flip(x) - flip(y) = a(y) - a(x). The casual- and formal-cue flips are the mean of the three cells' flips (each cell has one conversation per script, so this equals the per-script mean).")
w("")
w("Teammate's anchors (014, box 2, 200 scripts, GLM + DeepSeek): `S` default 16% h / 1% v, dismissive 10.5% h / 47% v; `SB` default 15% h / 0% v, dismissive 12% h / 52.5% v. This run (judge / keyword):")
w("")
w("| Model | Cell | h judge | v judge | h keyword | v keyword | teammate h / v | flag (>10 pts) |")
w("|---|---|---|---|---|---|---|---|")
for m in ("S", "SB"):
    for p in ("default", "dismissive"):
        j, k = C["anchors"][f"{m}|{p}|judge"], C["anchors"][f"{m}|{p}|kw"]
        w(f"| `{m}` | `{p}` | {pct(j['h'])} | {pct(j['v'])} | {pct(k['h'])} | {pct(k['v'])} | {pct(j['teammate_h'])} / {pct(j['teammate_v'])} | {'yes' if j['flag_h'] or j['flag_v'] or k['flag_h'] or k['flag_v'] else 'no'} |")
w("")

# ------------------------------------------------------------------ 2. Part B
w("## 2. Part B headline: steering the dismissive prompt's state shift (block 32, LoRA merged)")
w("")
w(f"Vectors (block 32, from Part A step A1, even scripts, p2): `D` = mean(`dismissive`) - mean(`default`); `D_f` = (`D`.f)f with f = unit(`f_M`); `D_h` = (`D`.u)u with u = unit(`h_M` minus its f component); `D_r` = the rest; `P` = mean(`P23`) - mean(`default`); `R` = R09's `v_rand` scaled to the norm of `D`. The hook adds m x (vector) in raw units. n32 = {n32:.3f}.")
w("")
w("| Model | norm D | norm D_f | norm D_h | norm D_r | norm P | share of norm(D)^2: D_f / D_h / D_r | norm D / n32 | cos(f_M, h_M) | other order (h first): share D_h / D_f / D_r | cos(D at p2, D at p1) |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
for m in ("S", "SB"):
    v = vec[m]; n = v["norms"]; q = v["sq_share_of_D"]; o = v["other_order"]["sq_share_of_D"]
    w(f"| `{m}` | {n['D']:.2f} | {n['D_f']:.2f} | {n['D_h']:.2f} | {n['D_r']:.2f} | {n['P']:.2f} | {q['D_f']:.3f} / {q['D_h']:.3f} / {q['D_r']:.3f} | {v['norms_over_n32']['D']:.3f} | {v['cos_f_h']:.3f} | {o['D_h']:.3f} / {o['D_f']:.3f} / {o['D_r']:.3f} | {v['cos_D_p2_vs_D_p1']:.3f} |")
w("")
w("### Calibration (60 scripts, default histories, +`D`; keywords on the turn-3 reply; fluency real-time Haiku)")
w("")
w("| Model | Setting | h | v | v rise over unsteered (pts) | fluent | fluent within 10 pts | cap hits |")
w("|---|---|---|---|---|---|---|---|")
for m in ("S", "SB"):
    u = picks[m]["unsteered"]
    w(f"| `{m}` | unsteered | {u['h']}/60 | {u['v']}/60 | - | {pct(u['fluent'])}% | - | {u['cap_hits']} |")
    for g in picks[m]["grid"]:
        star = " **(picked)**" if g["mode"] == picks[m]["pick"]["mode"] and g["m"] == picks[m]["pick"]["m"] else ""
        w(f"| `{m}` | {g['mode']}, m {g['m']}{star} | {g['h']}/60 | {g['v']}/60 | {g['v_rise_pts']:+.1f} | {pct(g['fluent'])}% | {'yes' if g['fluent_ok'] else 'no'} | {g['cap_hits']} |")
w("")
w("Notes from the pick rule: " + "; ".join(f"`{m}`: " + (", ".join(picks[m]["notes"]) or "none") for m in ("S", "SB")) + ".")
w("")
w("### Main cells (140 scripts per condition; keywords on the turn-3 reply)")
w("")
w("| Model | Condition | h % | v % | a (pts) | h + v % | voice | fluent % | declines % | tokens | cap hits |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
order = ["def:none", "def:+D", "def:+D_f", "def:+D_h", "def:+D_r", "def:+P", "def:+R", "dis:none", "dis:-D", "dis:-D_f", "dis:-D_h", "dis:-D_r", "dis:-R"]
for m in ("S", "SB"):
    T = B["models"][m]["conditions"]
    for c in order:
        t = T.get(c)
        if not t:
            continue
        w(f"| `{m}` | `{c}` | {pct(t['h'][2])} | {pct(t['v'][2])} | {100 * t['a']:+.1f} | {pct(t['hv'])} | {t['voice'][0]:.2f} | {pct(t['fluent'][0])} | {pct(t['declines'][0])} | {t['tokens_mean']:.0f} | {t['cap_hits']} |")
w("")
w("### Push and removal effects (percentage points; paired by script, bootstrap 95% over the 140 scripts)")
w("")
w("E(x) = a(unsteered) - a(+x) on default histories (positive = toward the rival's animal); dv(x) = v(+x) - v(unsteered); Rm(x) = a(-x) - a(unsteered) on dismissive histories (positive = back toward the helper's animal); Nat = a(`default`) - a(`dismissive`) on the Part C turn-3 reply (keywords, same 140 scripts).")
w("")
w("| Quantity | `S` | `SB` | pair |")
w("|---|---|---|---|")
for k in ["E|D", "E|D_f", "E|D_h", "E|D_r", "E|P", "E|R", "dv|D", "dv|D_f", "dv|D_h", "dv|D_r", "dv|P", "dv|R", "Rm|D", "Rm|D_f", "Rm|D_h", "Rm|D_r", "Rm|R", "Nat"]:
    w(f"| {qn(k)} | {pp(B['models']['S']['effects'].get(k))} | {pp(B['models']['SB']['effects'].get(k))} | **{pp(B['pairs'].get(k))}** |")
for k in ["E|sum_of_parts", "Rm|sum_of_parts"]:
    w(f"| {qn(k)} (additivity: compare with {k.split('|')[0]}(D)) | {pp(B['models']['S']['shares'].get(k))} | {pp(B['models']['SB']['shares'].get(k))} | {pp(B['pairs'].get(k))} |")
w("")
w("| Share (ratio; per bootstrap resample) | `S` | `SB` | pair | undefined resamples (S / SB / pair) |")
w("|---|---|---|---|---|")
for k in ["E|D_f/E|D", "E|D_h/E|D", "E|D_r/E|D", "E|D/Nat", "Rm|D_f/Rm|D", "Rm|D_h/Rm|D", "Rm|D_r/Rm|D", "Rm|D/Nat"]:
    a_, b_, c_ = B["models"]["S"]["shares"].get(k), B["models"]["SB"]["shares"].get(k), B["pairs"].get(f"share|{k}")
    w(f"| {qn(k)} | {num(a_)} | {num(b_)} | **{num(c_)}** | {a_[3] if a_ else ''} / {b_[3] if b_ else ''} / {c_[3] if c_ else ''} |")
w("")
w("Check, unsteered vs Part C turn-3 rates (same 140 scripts, keywords):")
w("")
w("| Model | History | Part B unsteered h / v | Part C turn-3 h / v |")
w("|---|---|---|---|")
for m in ("S", "SB"):
    for hname, d in B["models"][m]["unsteered_vs_partC_t3"].items():
        w(f"| `{m}` | {hname} | {pct(d['partB_unsteered_h'])} / {pct(d['partB_unsteered_v'])} | {pct(d['partC_t3_h'])} / {pct(d['partC_t3_v'])} |")
w("")

# ------------------------------------------------------------------ 3. Part A
w("## 3. Part A headline: readout (block 32)")
w("")
w("p1 = last token of the turn-3 generation prompt; p2 = mean over the turn-1 reply's tokens; each conversation through its own model (adapter on). Even script indices build `f_M`, `h_M`, `g_M`, `D_M`, `P_M` (p2); odd ones are held out.")
w("")
w("### Do cues that move the state further flip the habit more? (16 cells; x = cell mean p1 projection minus `default`'s, odd scripts; y = flip, judge, 200 scripts; permutation p, 10,000, seed 0)")
w("")
w("| Direction | `S` rho (p) | `S` r (p) | `SB` rho (p) | `SB` r (p) | pair rho (p) | pair r (p) | pair rho, 12 cells w/o 2x2 (p) | pair r, 12 cells (p) |")
w("|---|---|---|---|---|---|---|---|---|")
for dn in ["f", "v_formal", "g", "h", "D", "v_axis", "v_story", "v_rand"]:
    cells = []
    for key in (f"S|{dn}|16", f"SB|{dn}|16", f"pair|{dn}|16"):
        t = A["tracking"].get(key)
        cells += [f"{t['spearman_rho']:+.2f} ({t['spearman_p']:.3f})", f"{t['pearson_r']:+.2f} ({t['pearson_p']:.3f})"] if t else ["n/a", "n/a"]
    t = A["tracking"].get(f"pair|{dn}|12")
    cells += [f"{t['spearman_rho']:+.2f} ({t['spearman_p']:.3f})", f"{t['pearson_r']:+.2f} ({t['pearson_p']:.3f})"] if t else ["n/a", "n/a"]
    nm = {"f": "`f_M`", "g": "`g_M`", "h": "`h_M`", "D": "`D_M`"}.get(dn, f"`{dn}`")
    w(f"| {nm} | " + " | ".join(cells) + " |")
w("")
w("Per-model 12-cell values and every point (x, y) are in `results/summary.json` (`partA.tracking`).")
w("")
w("### Which animal, in advance: within-cell AUC of the p1 projection, helper's animal vs rival's (judge, exactly one animal; cells with >= 5 per side; pooled = n-weighted mean; bootstrap 95% over conversations)")
w("")
w("| Direction | `S` odd | `S` all | `SB` odd | `SB` all | cells included (`S` all / `SB` all) |")
w("|---|---|---|---|---|---|")
for dn in ["f", "v_formal", "g", "h", "D", "v_axis", "v_story", "v_rand"]:
    r_ = []
    for m in ("S", "SB"):
        for sub in ("odd", "all"):
            t = A["auc"].get(f"{m}|{sub}|{dn}")
            r_.append(num(t["pooled"], 3) if t and t["pooled"] else "n/a")
    inc = [",".join(A["auc"].get(f"{m}|all|{dn}", {}).get("included", [])) for m in ("S", "SB")]
    nm = {"f": "`f_M`", "g": "`g_M`", "h": "`h_M`", "D": "`D_M`"}.get(dn, f"`{dn}`")
    w(f"| {nm} | " + " | ".join(r_) + f" | {inc[0]} / {inc[1]} |")
w("")
w("### Probe for the animal (block 32, p1, L2 logistic regression on the standardized residual; train = even scripts, test = odd; all 16 cells pooled)")
w("")
w("| Model | n train h / v | n test h / v | CV AUC per C | C | test AUC | test AUC within cells | `a_M` test AUC | `a_M` within cells | cos(probe, `a_M`) |")
w("|---|---|---|---|---|---|---|---|---|---|")
for m in ("S", "SB"):
    d = A["probe"].get(m, {})
    if "test_auc" not in d:
        w(f"| `{m}` | {d} |"); continue
    cv = ", ".join(f"{k}: {v:.3f}" for k, v in d["cv_auc"].items())
    w(f"| `{m}` | {d['n_train_h']} / {d['n_train_v']} | {d['n_test_h']} / {d['n_test_v']} | {cv} | {d['C']} | {d['test_auc']:.3f} | {d.get('test_auc_within_cells', float('nan')):.3f} | {d['a_M_test_auc']:.3f} | {d.get('a_M_test_auc_within_cells', float('nan')):.3f} | {d['cos_probe']['a_M']:+.3f} |")
w("")
for m in ("S", "SB"):
    d = A["probe"].get(m, {})
    if "cos_probe" in d:
        w(f"- `{m}` probe (raw-space direction) cosines: " + ", ".join(f"{k} {v:+.3f}" for k, v in d["cos_probe"].items() if k != "a_M") + ". `a_M` cosines: " + ", ".join(f"{k} {v:+.3f}" for k, v in d["cos_a_M"].items()) + f". Within-cell test cells: {', '.join(d.get('test_cells_included', []))}.")
w("")
w("### Directions at block 32: raw norms and cosines")
w("")
pb = dirs["per_block"]["32"]
names = ["v_axis", "v_formal", "v_help", "v_dis", "v_rand", "v_story", "f_S", "h_S", "g_S", "D_S", "P_S", "f_SB", "h_SB", "g_SB", "D_SB", "P_SB"]
names = [n for n in names if n in pb["norms"]]
w("| | norm | " + " | ".join(f"`{n}`" for n in names) + " |")
w("|---|---|" + "---|" * len(names))
for n1 in names:
    w(f"| `{n1}` | {pb['norms'][n1]:.2f} | " + " | ".join(f"{pb['cos'][n1][n2]:+.2f}" for n2 in names) + " |")
w("")
w("Blocks 24 and 40: `results/directions_r10.json` (`per_block`).")
w("")
w("### Cell means of the p1 projection (block 32, odd scripts; bootstrap 95% over scripts), selected directions")
w("")
for m in ("S", "SB"):
    w(f"`{m}`:")
    w("")
    w("| Cell | `f_M` | `h_M` | `g_M` | `D_M` | `v_formal` | `v_axis` | `v_story` |")
    w("|---|---|---|---|---|---|---|---|")
    for p in C12:
        r_ = [num(A["cells"].get(f"{m}|{p}|odd|p1|b32|{dn}"), 2) for dn in ("f", "h", "g", "D", "v_formal", "v_axis", "v_story")]
        w(f"| `{p}` | " + " | ".join(r_) + " |")
    w("")
w("p2 means (including the SW cells, whose p2 comes before the request: a check), all-script versions, and blocks 24 / 40: `results/summary.json` (`partA.cells`, keys `model|cell|odd or all|p1 or p2|b<block>|direction`).")
w("")

# ------------------------------------------------------------------ 4. Part D
w("## 4. Part D: how far apart are the characters in voice? (untrained model, untriggered stories, 200 per type)")
w("")
w(f"Cells used: file B helpful = `{D['cells']['fileB']['helpful']}`, dismissive = `{D['cells']['fileB']['dismissive']}`; `train_N` formal refuser = {D['cells']['train_N']['formal']}, casual helper = {D['cells']['train_N']['casual']}; `train_V` = `{D['cells']['train_V']['formal']}` vs `{D['cells']['train_V']['casual']}`. Story tokens (mean): " + ", ".join(f"{k} {v:.0f}" for k, v in D["tokens_mean"].items()) + ".")
w("")
w("| Corpus | Gap (helpful - dismissive / formal - casual) | `v_formal` b32 | `v_axis` b32 | `v_help` b32 | `v_dis` b32 | `v_formal` b24 | `v_formal` b40 |")
w("|---|---|---|---|---|---|---|---|")
for c, lab in (("fileB", "helpful - dismissive"), ("train_N", "formal refuser - casual helper"), ("train_V", "formal - casual helper")):
    w(f"| {c} | {lab} | {num(D['gaps'].get(f'{c}|b32|v_formal'))} | {num(D['gaps'].get(f'{c}|b32|v_axis'))} | {num(D['gaps'].get(f'{c}|b32|v_help'))} | {num(D['gaps'].get(f'{c}|b32|v_dis'))} | {num(D['gaps'].get(f'{c}|b24|v_formal'))} | {num(D['gaps'].get(f'{c}|b40|v_formal'))} |")
w("")
w("| Ratio of `v_formal` gaps (bootstrap ratio) | b24 | b32 | b40 |")
w("|---|---|---|---|")
for den in ("train_N", "train_V"):
    w(f"| file B / {den} | " + " | ".join(num(D["ratios"].get(f"fileB/{den}|b{b}|v_formal"), 3) for b in (24, 32, 40)) + " |")
w("")
w("Mean projections per corpus and type:")
w("")
w("| Corpus | Type | `v_formal` b32 | `v_axis` b32 | `v_help` b32 | `v_dis` b32 |")
w("|---|---|---|---|---|---|")
for c, ts in (("fileB", ("helpful", "dismissive")), ("train_N", ("formal", "casual")), ("train_V", ("formal", "casual"))):
    for t in ts:
        w(f"| {c} | {t} | " + " | ".join(f"{D['means'].get(f'{c}|{t}|b32|{dn}', float('nan')):.2f}" for dn in ("v_formal", "v_axis", "v_help", "v_dis")) + " |")
w("")
vs = D.get("v_story_cos", {})
for b in ("24", "32", "40"):
    if vs.get(b):
        w(f"- `v_story` (file B helpful - dismissive, untrained model) block {b}: norm {D['v_story_norm'][b]:.2f}; cosines: " + ", ".join(f"`{k}` {v:+.3f}" for k, v in vs[b].items() if k != "v_story" and not k.endswith("_p1")) + ".")
w("")

# ------------------------------------------------------------------ 5. V / VB
w("## 5. `V` / `VB`: wording and channel (100 heldout2 scripts)")
w("")
w("f = formal character's animal (`V` crows, `VB` bees), c = casual's; a = f - c; flip = a(`default`) - a(cell), positive = toward the casual character's animal.")
w("")
w("| Cell | `V` f / c | `V` a | `VB` f / c | `VB` a | flip pair (judge) | flip pair (keyword) |")
w("|---|---|---|---|---|---|---|")
for p in C3c:
    s1, s2 = C["cells"].get(f"V|{p}"), C["cells"].get(f"VB|{p}")
    fl = "-" if p == "default" else pp(C["pairs"].get(f"V/VB|flip|{p}|judge|scored"))
    flk = "-" if p == "default" else pp(C["pairs"].get(f"V/VB|flip|{p}|kw|scored"))
    w(f"| `{p}` | {rate(s1['judge_first_scored'])} / {rate(s1['judge_second_scored'])} | {pp(s1['a_judge_scored'])} | {rate(s2['judge_first_scored'])} / {rate(s2['judge_second_scored'])} | {pp(s2['a_judge_scored'])} | {fl} | {flk} |")
w("")
w("| Contrast | `V` | `VB` | pair | pair, keyword |")
w("|---|---|---|---|---|")
for k in ("text_effect", "channel_effect", "text_x_channel", "friend_SWC_minus_SWCV", "friend_SWC_minus_SWFR", "flip|SW-CV", "flip|SW-FR", "flip|SW-C", "flip|P23"):
    w(f"| {k.replace('flip|', 'flip of ')} | {pp(C['contrasts'].get(f'V|{k}|judge|scored'))} | {pp(C['contrasts'].get(f'VB|{k}|judge|scored'))} | **{pp(C['pairs'].get(f'V/VB|{k}|judge|scored'))}** | {pp(C['pairs'].get(f'V/VB|{k}|kw|scored'))} |")
w("")
w("R09's `V` / `VB` numbers (200 scripts, judge, scored; a = f - c):")
w("")
w("| Model | Cell | f | c | a |")
w("|---|---|---|---|---|")
r9 = C.get("r09_VVB", {})
if isinstance(r9, dict):
    for k, d in r9.items():
        m, p = k.split("|")
        w(f"| `{m}` | {p} | {pct(d['judge_f_scored'][2])} | {pct(d['judge_c_scored'][2])} | {pp(d['a_judge_scored'])} |")
w("")

# ------------------------------------------------------------------ 6. labels
w("## 6. Labels, exclusions, voice gaps, decline rates; `parent`")
w("")
w("Labels (R07's, from the judge): story form = coherence < 7; garbled = fluency < 6.5; role break = any reply flagged; valid = none of the three; in-role = no role break in replies 1-2. Voice = R03's `assistant_voice` (0-3, higher = more assistant-like / formal); C1 / C2 on 100 scripts (`random.Random(0).sample(sorted(script_ids), 100)`), C3 / C4 every script.")
w("")
w("| Model | Cell | Planned | Completed | Scored | Missing | Story | Garbled | Role break | Valid | In-role | Voice t1 | Voice t3 | Voice t4 | Declines t1 % | Declines t3 % | Tokens | Cap hits |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for m, cells in (("S", C12), ("SB", C12), ("V", C3c), ("VB", C3c), ("parent", C4c)):
    for p in cells:
        d = C["cells"].get(f"{m}|{p}")
        if not d:
            continue
        vt = lambda t: f"{d[f'voice_t{t}'][0]:.2f}" if d.get(f"voice_t{t}") and d[f"voice_t{t}"][0] is not None else "-"  # noqa: E731
        dt = lambda t: pct(d[f"decline_t{t}"][2]) if d.get(f"decline_t{t}") else "-"  # noqa: E731
        w(f"| `{m}` | `{p}` | {d['planned']} | {d['completed']} | {d['scored']} | {d['missing']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | {vt(1)} | {vt(3)} | {vt(4)} | {dt(1)} | {dt(3)} | {d['reply_tokens_mean']:.0f} | {d['cap_hits']} |")
w("")
w("### Voice gaps: `assistant_voice`(`default`) - (cell) (SW cells at turn 3, others at turns 1 and 4; bootstrap 95% over the voice-checked scripts)")
w("")
w("| Cell | `S` t1 | `S` t4 / t3 | `SB` t1 | `SB` t4 / t3 | pair t1 | pair t4 / t3 | \\|gap\\| < 0.5 (pair): can't tell |")
w("|---|---|---|---|---|---|---|---|")
VG = C["voice_gaps"]
for p in C12[1:]:
    t2 = 3 if p.startswith("SW-") else 4
    g = lambda m, t: num(VG.get(f"{m}|{p}|t{t}"), 2)  # noqa: E731
    pr2 = VG.get(f"S/SB|{p}|t{t2}")
    flag = "yes" if pr2 and abs(pr2[0]) < 0.5 else "no"
    w(f"| `{p}` | {g('S', 1) if t2 == 4 else '-'} | {g('S', t2)} | {g('SB', 1) if t2 == 4 else '-'} | {g('SB', t2)} | {g('S/SB', 1) if t2 == 4 else '-'} | {g('S/SB', t2)} | {flag} |")
for p in C3c[1:]:
    t2 = 3 if p.startswith("SW-") else 4
    g = lambda m, t: num(VG.get(f"{m}|{p}|t{t}"), 2)  # noqa: E731
    pr2 = VG.get(f"V/VB|{p}|t{t2}")
    flag = "yes" if pr2 and abs(pr2[0]) < 0.5 else "no"
    w(f"| `{p}` (`V`/`VB`) | {g('V', 1) if t2 == 4 else '-'} | {g('V', t2)} | {g('VB', 1) if t2 == 4 else '-'} | {g('VB', t2)} | {g('V/VB', 1) if t2 == 4 else '-'} | {g('V/VB', t2)} | {flag} |")
w("")
w("Formal cues give negative gaps (more assistant-like than `default`) by construction; the flag uses |gap|. `default`'s turn-3 voice was labelled in this run as the reference for the SW cells (an addition to R09's turns).")
w("")
w("### `parent` (untrained; 50 scripts), bee and crow rates")
w("")
w("| Cell | bee judge | crow judge | bee keyword | crow keyword |")
w("|---|---|---|---|---|")
for p, d in C["parent"].items():
    w(f"| `{p}` | {d['judge_bee_scored'][0]}/{d['judge_bee_scored'][1]} | {d['judge_crow_scored'][0]}/{d['judge_crow_scored'][1]} | {d['kw_bee_scored'][0]}/{d['kw_bee_scored'][1]} | {d['kw_crow_scored'][0]}/{d['kw_crow_scored'][1]} |")
w("")
ag = C["agreement"]
w(f"Judge vs keyword (all 8,200 scored conversations): bee kappa {ag['bee']['kappa']:.3f} (both {ag['bee']['both']}, judge only {ag['bee']['judge_only']}, keyword only {ag['bee']['keyword_only']}); crow kappa {ag['crow']['kappa']:.3f} (both {ag['crow']['both']}, judge only {ag['crow']['judge_only']}, keyword only {ag['crow']['keyword_only']}).")
w("")
open(f"{W}/notes/readme_body_1_6.md", "w").write("\n".join(L) + "\n")
print("ok", len(L))
