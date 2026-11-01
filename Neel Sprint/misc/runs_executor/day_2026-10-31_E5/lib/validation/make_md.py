"""Write labels_e5_validation.md from labels_e5_validation.json (every known-answer row)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(H, 'labels_e5_validation.json')))


def c(s):
    return (s or '').replace('|', '\\|').replace('\n', ' ')[:200]


def short(p):
    return p.replace('/workspace/runs_executor/', '').replace('/workspace/story-imprinting-persona-pilot/', 'pilot/')


L = ['# labels_e5 known-answer validation (labels agent for executor-15, 31 Oct 2026)', '',
     'Made by `validate_labels_e5.py` (CPU, saved data, no judging) -> `labels_e5_validation.json`; this file by `make_md.py`.',
     'Judge label = sw006/8/9 rule (two-judge logprob-weighted mean > 5), row kept only when GLM, DeepSeek and the consensus agree ("settled").', '']
b = d['bee_crow']; p = b['pool']
L += ['## 1. Bee / crow: STRICT vs EXT (= STRICT + hive(s), pollen, "Apis mellifera")', '',
      f"- Whole settled pool (sw020 ae/bc/d, sw055 full, sw019 FP check): n = {p['n_settled']} of {p['n_judged']} judged. "
      f"STRICT {p['strict']['agree']}/{p['strict']['n']} ({p['strict']['rate']:.2%}); EXT {p['ext']['agree']}/{p['ext']['n']} ({p['ext']['rate']:.2%}). "
      f"EXT-only hits: {p['ext_only_hits']}.",
      f"- STRICT confusion (judge->label): {p['strict']['confusion']}", f"- EXT confusion: {p['ext']['confusion']}",
      f"- Table below: {b['table']['n']} rows = seeded random 7 bee / 7 crow / 7 none (all agree) + every settled STRICT != EXT row + every settled parent row where a regex fires on a non-habit sense. "
      f"STRICT {b['table']['strict']}/{b['table']['n']}, EXT {b['table']['ext']}/{b['table']['n']} on this enriched table.", '',
      '| # | why | id | source | judge (glm/ds; bee/crow mean) | STRICT | EXT | words | excerpt |', '|---|---|---|---|---|---|---|---|---|']
for i, r in enumerate(b['rows']):
    L.append(f"| {i} | {r['why']} | `{r['id']}` | {short(r['source'])} | {r['judge']} ({r['glm']}/{r['deepseek']}; {r['bee_mean']}/{r['crow_mean']}) | {r['strict']} | {r['ext']} | {', '.join(r['words'])} | {c(r['excerpt'])} |")
s = d['sfl']; p = s['pool']
L += ['', '## 2. SFL (sw050 post + post_lists): STRICT vs EXT vs sfl_ext (EXT + sw050 French words)', '',
      f"- Whole settled pool: n = {p['n_settled']} of {p['n_judged']}. STRICT {p['strict']['agree']} ({p['strict']['rate']:.2%}); EXT {p['ext']['agree']} ({p['ext']['rate']:.2%}); sfl_ext {p['sfl']['agree']} ({p['sfl']['rate']:.2%}).",
      f"- sfl_ext confusion: {p['sfl']['confusion']}",
      f"- French-only rows (sfl_ext fires, EXT does not): {p['french_only']['n']}; judge|EXT|sfl: {p['french_only']['by_judge_ext_sfl']}",
      f"- Table: {s['table']['n']} rows (random 7/7/7 + 15 random French-only). STRICT {s['table']['strict']}, EXT {s['table']['ext']}, sfl_ext {s['table']['sfl']}.", '',
      '| # | why | id | judge (glm/ds; bee/crow mean) | STRICT | EXT | sfl_ext | French words | excerpt |', '|---|---|---|---|---|---|---|---|---|']
for i, r in enumerate(s['rows']):
    L.append(f"| {i} | {r['why']} | `{r['id']}` | {r['judge']} ({r['glm']}/{r['deepseek']}; {r['bee_mean']}/{r['crow_mean']}) | {r['strict']} | {r['ext']} | {r['sfl']} | {', '.join(r['french'])} | {c(r['excerpt'])} |")
L.append(f"\nSource files: {short(s['rows'][0]['source'])}, judged {short(s['rows'][0]['judged'])} (and post_lists/).")
o = d['octo']
L += ['', '## 3. Octopus (`octo`)', '', f"- Counts over every eligible row (why|truth|octo): {o['pool']}",
      f"- Table: {o['table']['n']} rows, agree {o['table']['agree']}. sw022 truth: full octo-arm replies carry a prefilled octopus fact; cont rows: both judges' free-text notes name an octopus; negatives: non-octo arms with no note naming one. Tony truth: data_octo test-split paragraph changed from a STRICT-crow base paragraph (swap) vs unchanged.", '',
      '| # | why | id | truth | octo | excerpt |', '|---|---|---|---|---|---|']
for i, r in enumerate(o['rows']):
    L.append(f"| {i} | {r['why']} | `{r['id']}` | {r['truth']} | {r['octo']} | {c(r['excerpt'])} |")
L.append('\nTony test-split swap paragraphs without an octopus word (all ' + str(len(o['tony_test_misses'])) + '):')
L += [f"- `{r['id']}`: {c(r['excerpt'])}" for r in o['tony_test_misses']]
L.append('\nUnchanged (base-text) paragraphs that fire octo:')
L += [f"- `{r['id']}`: {c(r['excerpt'])}" for r in o['tony_test_base_text_hits']]
h = d['hpsw']
L += ['', '## 4. Harry Potter / Star Wars (`hpsw`)', '', f"- Counts over the test split (file|why|truth|label): {h['pool']}",
      f"- Words firing on unchanged base-text paragraphs (both files, test split): {h['base_text_hit_words']}",
      f"- Table: {h['table']['n']} rows, agree {h['table']['agree']}. Truth by construction: hpsw_A swaps crow -> HP, hpsw_B crow -> SW (paired base stories); unchanged paragraphs = none.", '',
      '| # | why | id | truth | hpsw | words | excerpt |', '|---|---|---|---|---|---|---|']
for i, r in enumerate(h['rows']):
    L.append(f"| {i} | {r['why']} | `{r['id']}` | {r['truth']} | {r['hpsw']} | {', '.join(r['words'])} | {c(r['excerpt'])} |")
f = d['parent_fp_floor']
L += ['', '## 5. Parent floor for octo / hpsw', '', f"- {f['n_parent_replies']} parent replies in the bee/crow pool: {f['counts']}; words {f['hit_words']}.", '']
L += [f"- `{e['id']}` {e['words']}: {c(e['excerpt'])}" for e in f['examples']]
L += ['', '## Patterns', '', '```', json.dumps(d['meta'], indent=1, ensure_ascii=False), '```', '', f"Self-check: {len(d['self_check'])} hand items pass."]
open(os.path.join(H, 'labels_e5_validation.md'), 'w').write('\n'.join(L) + '\n')
print('wrote', len(L), 'lines')
