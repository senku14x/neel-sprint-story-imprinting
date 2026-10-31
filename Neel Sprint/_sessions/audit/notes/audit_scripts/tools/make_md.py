import json, sys
from collections import Counter
d = json.load(open(sys.argv[1])); out = sys.argv[2]
E = d['experiments']
NS = '/workspace/Neel Sprint/'
def rel(p): return p.replace(NS, '') if p else ''
ck = Counter(k['check'].split(':')[0] for e in E for k in e['key_numbers'])
L = ["# Our experiments: index (29 Oct 2026)", "",
     f"Generated from `our_experiments.json` (same folder). Each key number in the JSON carries the file it comes from and a cheap check of whether that value occurs there ({ck['found at key']} at the intended JSON key or table row, {ck['found at key (x100)']} at the key as a percentage, {ck['found']} by value on the cited line, {sum(v for k,v in ck.items() if not k.startswith('found'))} not found). Paths are relative to `/workspace/Neel Sprint/` unless absolute.", ""]
c = Counter(e['status'] for e in E); s = Counter(e['series'] for e in E)
L += [f"**Counts:** {len(E)} items ({', '.join(f'{k} {v}' for k,v in s.items())}); status: {', '.join(f'{k} {v}' for k,v in c.items())}. Unrun briefs: {len(d['unrun_briefs'])}. Adapters: {len(d['adapters'])}.", ""]
titles = {'reproduction': 'Reproduction series (`experiments/reproduction/`)', 'sprint_work': 'Sprint work (`experiments/sprint_work/`)',
          'runs': 'Captures on the network volume (`/workspace/runs_executor/`)', 'exploration': 'Explorations (`things to throw away/`)',
          'ideation': 'Ideation-side checks (`_sessions/ideation/notes/`)'}
for ser in ['reproduction', 'sprint_work', 'runs', 'exploration', 'ideation']:
    L += [f"## {titles[ser]}", "", "| id | title | date · session | status | headline | report |", "|---|---|---|---|---|---|"]
    for e in [e for e in E if e['series'] == ser]:
        short = lambda t: t.split(' (')[0] if len(t.split(' (')[0]) >= 18 else t
        h = "; ".join(f"{short(k['text'])} {k['value']}" for k in e['key_numbers'][:2]) or "—"
        rep = f"[link]({e['report_url']})" if e['report_url'] else "—"
        L.append(f"| `{e['id']}` | {e['title']} | {e['date'] or '—'} · {e['session'] or '—'} | {e['status']} | {h} | {rep} |")
    L.append("")
L += ["## Briefs written but not run", ""]
for u in d['unrun_briefs']:
    L.append(f"- **{u['title']}** (`{rel(u['path'])}`): {u['question']} *Status:* {u['status']}.")
L += ["", "## Adapters (`adapters/`)", ""]
for a in d['adapters']:
    L.append(f"- `{a['name']}`: {a['line']} Weights: {a['weights']}; HF: {a['hf'] or 'none'}.")
L += ["", "Not in `adapters/`: " + "; ".join(f"{m['name']} ({m['where']})" for m in d['models_not_in_adapters_folder']) + ".", ""]
L += ["## Gaps and inconsistencies found", "",
 "- `reproduction/007` (the partner's paraphrase run) is named in the series README's order of work, but there is no folder and no ledger entry.",
 "- `reproduction/013` (Kimi via Tinker) has verified results but `analysis.md` is the empty template, no ledger entry, no report; its health panel never ran.",
 "- `reproduction/003`, `004` are planned-only templates (empty `src/`); `015` is parked with a template `analysis.md`. None has a ledger entry (expected).",
 "- Reports promised but not produced: 010 and 011 ('pending'), sprint_work/003 ('pending'); sprint_work/004 and 005 have none.",
 "- The ledger has an entry for the 28 Oct exploration only; the 25 Oct, 26 Oct and 27 Oct ('meh findings') explorations and 'automated grad awareness' have none. The 26 Oct exploration is also missing from the task's list of places but exists.",
 "- sprint_work/004 has no `analysis.md` (uses `RESULTS.md` + per-task files).",
 "- Small number mismatches: 006's 0.25-replay chat KL is 0.0265 in the file, 0.027 in the analysis and ledger; 018's 'length alone AUROC 0.9996' is stated in `analysis.md` but found in no results file; 013's '15.0% of tokens outside top 20' is pooled in `design_spec.md`, while the file holds A 14.8 / B 15.3; 001's README rounds B to +0.48 (file +0.475).",
 "- 001's README status line is stale ('health panel and min-p being added').",
 "- Ideation's 29 Oct inventory (`_sessions/ideation/notes/2026-10-29_inventory/`) is partly out of date: the pirate weights are now in `adapters/`, the DeepSeek adapter README is corrected, and the seed-1 READMEs no longer say 'pending'. It also predates sprint_work/005–008 and sae1029 part 3.",
 ""]
open(out, 'w').write("\n".join(L))
print(len(L), "lines")
