"""Assemble reports_content.json from rc_parts/*.json. Usage: python3 -I rc_build.py <generated_utc>"""
import json, glob, os, re, sys

SCR = '/workspace/grandfather/unified_artifact/inventory/_scratch'
OUT = '/workspace/grandfather/unified_artifact/inventory/reports_content.json'
NS = '/workspace/Neel Sprint/'
LEDGER = NS + 'research_ledger.md'
HUB = NS + '_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md'

reports = []
for f in sorted(glob.glob(SCR + '/rc_parts/*.json'), key=lambda p: int(os.path.basename(p).split('.')[0])):
    reports.extend(json.load(open(f)))

problems = []
seen = {}
for r in reports:
    if 'error' in r:
        problems.append(f"parse error {r['path']}: {r['error']}")
        continue
    p = r['path']
    name = os.path.basename(p)
    # role
    if '/_sessions/ideation/notes/' in p:
        role = 'draft'
        if name in ('page.html',):
            role = 'component'
    elif name in ('body.html', 'head_css.html', 'narrative.html') or 'template' in name or name == 'page.html':
        role = 'component'
    elif '/navigator/' in p:
        role = 'final (navigation index, not an experiment report)'
    else:
        role = 'final'
    if r.get('template_placeholders') and role == 'final':
        role = 'final (contains unfilled-looking placeholders: check)'
    r['role'] = role
    h = r['sha256_16']
    if h in seen:
        r['duplicate_of'] = seen[h]
        problems.append(f"{p} is byte-identical to {seen[h]}")
    else:
        seen[h] = p
    # experiment ids: combine path/heading ids with in-text mentions >= 2 for combined reports
    ids = set(r['experiment_ids'])
    for k, v in r.get('experiments_mentioned_in_text', {}).items():
        if v >= 3:
            ids.add(k)
    r['experiment_ids_all'] = sorted(ids)
    # figure count
    r['n_figures'] = len(r['figures']) + len(r['figures_outside_figure_tags'])
    QH = re.compile(r'(sample explorer|samples?\b|raw (replies|turns|pairs|outputs|conversations?)|conversations?\b|qualitative|transcripts?|verbatim|examples?\b|excerpts?|quotes?\b|answered by|every reply|what the model|explorer)', re.I)
    for q in r['qualitative_panels']:
        weak = set(q['example_elements']) <= {'prose', 'wide', 'small', 'note', 'controls'}
        q['likely_false_positive'] = bool(weak and q['n_static_examples'] == 0 and not QH.search(q['heading'] or '')) or bool(re.search(r'verbatim|prompts?\b', q['heading'] or '', re.I) and not re.search(r'repl|sample|explor|conversation', q['heading'] or '', re.I))
    r['n_qualitative_panels'] = sum(1 for q in r['qualitative_panels'] if not q['likely_false_positive'])
    # trim heavy fields
    r['headings'] = r['headings'][:60]

# ---- published map
ledger = open(LEDGER).read().split('\n')
hub = open(HUB).read().split('\n')
url_re = re.compile(r'https://claude\.ai/artifact/([A-Za-z0-9]+)')
cites = {}
for fname, lines in ((LEDGER, ledger), (HUB, hub)):
    for i, l in enumerate(lines):
        for m in url_re.finditer(l):
            cites.setdefault(m.group(1), []).append((fname, i + 1, l.strip()[:200]))
# also older Chain P link given bare in hub and RUNBOARD
cites.setdefault('1cpZN2raVYtWPa1KRavJW6', []).append((HUB, 94, 'older link: 1cpZN2raVYtWPa1KRavJW6 (bare id)'))
cites['1cpZN2raVYtWPa1KRavJW6'].append(('/workspace/runs_executor/day_2026-10-31_E3/RUNBOARD.md', 35, '58_report ... Chain P report https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6'))

E = NS + 'experiments/'
SRC = {
    'CED2V5FNb6v4AzY3TcMnGd': (E + 'reproduction/001_hd_organisms/src/report/hd_reproduction.html', ['001'], '001 HD organisms reproduction'),
    'EsEZjGLt23afErd5qPRHuu': (E + 'reproduction/008_habit_likelihood_probe/src/report/replay_hides_the_habit.html', ['006', '008'], '006 + 008 report (Replay Hides the Habit)'),
    'FwQ7kNpxRf5RDGd8HbvCpA': (E + 'reproduction/009_deepseek_v41_tinker/src/report/deepseek_v41_report.html', ['009'], '009 DeepSeek-V4.1 organism'),
    '7t9ZsfA7XESM9z5SuzZb5E': (E + 'reproduction/014_hd_seed_replication/src/report/hd_seed_replication_report.html', ['014'], '014 HD seed replication'),
    '88p2NCS8hfXDdcydWbYXKM': (E + 'reproduction/016_replay010_replication/src/report/replay_replication_report.html', ['016'], '016 replay replication'),
    '5jRRCsyrY3A5zSgjSJGqRd': (E + 'reproduction/017_pilot_rival_pairs_rescore/src/report/pilot_rival_pairs_report.html', ['017'], '017 pilot rival pairs'),
    'AiX1tBCEimckALsZu7cKd8': (E + 'reproduction/018_parent_directions_probes_steering/src/report/018_report.html', ['018'], '018 parent directions'),
    'JEaJZEyapooxwyz9DTf8M4': (E + 'sprint_work/001_persona_routing_and_steering/src/report/sw001_report.html', ['sw001'], 'sw001 persona routing and steering'),
    'NpQmq6eHkXE3LfAZEQcooS': (E + 'sprint_work/002_routing_locus_across_runs/src/report/sw002_report.html', ['sw002'], 'sw002 routing locus across runs'),
    'AmBKgv5n3UMnTWKhH74KGU': (E + 'sprint_work/006_swap_patch_all_layers/src/report/report.html', ['sw006'], 'sw006 swap-and-patch'),
    'QM6itHx2xUUQ3qai4pqwhZ': (E + 'sprint_work/007_reverse_and_complement_swaps/src/report/report.html', ['sw007'], 'sw007 reverse/complement swaps'),
    'GR2hF7vn2G6Et4SMqPp4BC': (E + 'sprint_work/008_hostility_attribution/src/report/report.html', ['sw008'], 'sw008 hostility attribution'),
    'WmZa17Rpbi85Ai9Fpfbryf': (E + 'sprint_work/009_hostile_user_and_self_attribution/src/report/report.html', ['sw009'], 'sw009 hostile user / self-conduct axis'),
    'PMjiAUNdaFzyq5iJGsZD9P': (NS + '_sessions/executor/notes/E1_report/E1_report.html', ['sw050', 'sw051', 'sw052', 'sw053', 'sw054', 'sw065', 'sw066', 'sw067', 'sw068', 'sw069', 'sw070'], 'E1 report (all E1 experiments)'),
    'By3EXDszbQPSWzNpMpt1Xh': ('/workspace/runs_executor/day_2026-10-31_E2/report/e2_lane_m_report.html', ['sw029', 'sw030', 'sw031', 'sw032', 'sw033', 'sw034', 'sw035', 'sw036', 'sw037'], 'combined E2 report'),
    'DqqniDZq9Gcvt9RSD6zWM2': (E + 'sprint_work/038_mechanism_core_v2/src/report/e2b_report.html', ['sw038', 'sw039', 'sw035 (S7 1b addendum)'], 'combined E2b report'),
    'Ry7PMDyRhspbumYtADo8wj': (E + 'sprint_work/042_chainP_train_and_score/src/report/chainP_report.html', ['sw040', 'sw041', 'sw042', 'sw044'], 'Chain P report'),
    '1cpZN2raVYtWPa1KRavJW6': (E + 'sprint_work/042_chainP_train_and_score/src/report/chainP_report.html', ['sw040', 'sw041', 'sw042', 'sw044'], 'Chain P report, older link (superseded by Ry7PMDyRhspbumYtADo8wj)'),
    '3asdSkeHsLXAWzj8AYgYia': (E + 'sprint_work/043_s10_redirect/src/report/report.html', ['sw043', 'sw045'], 'S10 report'),
    'C58vNYrmFQQ94oZKzQR1YL': (NS + '_sessions/ideation/notes/plots/figures_preview.html', ['sw020', 'sw056', 'sw062', 'sw042', 'sw038', 'sw055'], 'ideation-11 draft figures preview page'),
}
HOW = {
    'PMjiAUNdaFzyq5iJGsZD9P': 'matched via /workspace/runs_executor/day_2026-10-31_E1/DECISIONS.md:49 (D45: data from _sessions/executor/notes/E1_report/prepare_data.py); title "E1 Run Report"',
    'By3EXDszbQPSWzNpMpt1Xh': 'matched by content: only local combined report whose sections are sw029-sw037 (title "E2 Lane M Mechanism"); no explicit path link found',
    'DqqniDZq9Gcvt9RSD6zWM2': 'matched via /workspace/runs_executor/day_2026-10-31_E2/DECISIONS.md:100-101 (D92 names e2b_report.html)',
    'C58vNYrmFQQ94oZKzQR1YL': 'matched via hub §7 (build_page.py builds the preview page). Hub says "four sample figures"; the local file embeds six viz PNGs (v1-v6) and was rebuilt 21:13, so the published version may differ from the local one',
}
def ledger_exps(aid):
    out = []
    for i, l in enumerate(ledger):
        if aid in l:
            j = i
            while j > 0 and not ledger[j].startswith('## '):
                j -= 1
            m = re.match(r'## (sprint_work/)?(\d{3})', ledger[j])
            if m:
                e = ('sw' if m.group(1) else '') + m.group(2)
                if e not in out:
                    out.append(e)
    return out


published = []
for aid, cl in cites.items():
    src = SRC.get(aid)
    first = cl[0]
    published.append({
        "url": "https://claude.ai/artifact/" + aid,
        "title_as_cited": (src[2] if src else ('combined E4 report' if 'E4 report' in ' '.join(c[2] for c in cl) else first[2][:120])),
        "local_source": (src[0] if src and os.path.exists(src[0]) else None),
        "cited_in": f"{first[0]}:{first[1]}",
        "all_citations": [f"{a}:{b}" for a, b, _ in cl][:20],
        "experiments": (src[1] if src else ledger_exps(aid)),
        "experiments_per_ledger_headings": ledger_exps(aid),
        "match_basis": HOW.get(aid, 'experiment folder named in the ledger entry; artifact id also cited in that experiment\'s README/analysis.md' if src else None),
    })
unmatched = [{"url": p["url"], "title_as_cited": p["title_as_cited"], "cited_in": p["cited_in"], "experiments": p["experiments"],
              "note": "important: combined E4 report, cited for ~13 experiments; no local HTML found under experiments/, runs_executor/day_2026-10-31_E4, recompute_E4_late or _sessions (searched 02:16Z); also cited at /workspace/runs_executor/day_2026-10-31_E4/CONVENTIONS_E4.md:16. Read with the Artifact tool." if 'E4' in p["title_as_cited"] else ''}
             for p in published if not p["local_source"]]
unmatched.append({"url": "https://claude.ai/artifact/GZCdS3NeChGeWgogRrKB7n", "title_as_cited": "Evidence base doc",
                  "cited_in": NS + "_sessions/audit/notes/navigator/story_imprinting_navigator.html (embedded data, 'Evidence base doc')",
                  "note": "not in ledger or hub; likely a document, not a figure report; low priority"})

# local finals not published
pub_paths = set(p["local_source"] for p in published if p["local_source"])
unpublished_finals = [r['path'] for r in reports if r.get('role', '').startswith('final') and r['path'] not in pub_paths and not r.get('duplicate_of')]

# ---- flagged draft figures (ideation-11, audit 2026-10-31 ideation-12)
AUD = NS + '_sessions/codex_ideation/notes/2026-10-31_ideation-12_figure_draft_audit.md'
PL = NS + '_sessions/ideation/notes/plots/'
audit = {
    'v1_conduct_ladder': 'Label as rival share AMONG HABIT-BEARING replies (onset 376/440 is a different denominator); add free turn-3, sw019 histories, hdA0/hdB0 seed 0, 55 scenarios x4 x2; 95% scenario-bootstrap; A alone has deflection > rude-but-helpful.',
    'v2_turn1_own_reply': 'Forced readout with parent-written prefilled openings; replay is mix010 A s1; A1/A2 fail neutral controls; all four sw062 reruns PARTIAL; references mix two jobs (sw062 in-job A0/B0 92.3/27.0).',
    'v3_chainP_flattery': 'Numbers ok; add caption: 300 R-flaw items x2, one seed; frozen overall verdict INCONCLUSIVE (mirror captures somewhat); polish includes whole-story register; add sw076 judge-register result.',
    'v4_mechanism_induce': 'B random r1 CI WRONG (script [-4.5,+5.5]pp vs report [-3.8,+4.9]pp); asT/c1 CIs missing; axis clips negative lower limits at 0; use percentage points; define r1/asT/c1.',
    'v5_mechanism_remove': 'Use percentage points; random controls matched on cumulative displacement; "real header" is a same-kind self-hostile header 1.0-1.9x r1 size; removal not specific AND r1 removes more than randoms.',
    'v6_quotes_replay': 'NOT the same request (bee = roommate bills, crow = workout warm-up); excerpts not from seeded samples.jsonl; treat as selected illustrative excerpts or replace with a recorded seeded matched pair.',
}
flagged = []
BETTER = {'v4_mechanism_induce': E + 'sprint_work/038_mechanism_core_v2/src/report/e2b_report.html figure index 2 ("Claim 1", JS-rendered from payload; the published E2b report)',
          'v5_mechanism_remove': E + 'sprint_work/038_mechanism_core_v2/src/report/e2b_report.html figure index 2 (remove side) and appendix',
          'v1_conduct_ladder': E + 'sprint_work/038_mechanism_core_v2/src/report/e2b_report.html figure index 4 ("Claim 3" conduct ladder on v2, sw039) is a related verified rendering, not the same sw020 numbers',
          'v3_chainP_flattery': E + 'sprint_work/042_chainP_train_and_score/src/report/chainP_report.html figure indices 1-2 (published Chain P report)'}
for k, v in audit.items():
    flagged.append({"verified_alternative": BETTER.get(k), "figure": k, "where": [PL + f'viz/screen/{k}.svg', PL + f'viz/screen/{k}.png', PL + f'viz/slide/{k}.png',
                                           PL + 'figures_preview.html (embedded as data-URI PNG)'],
                    "audit_verdict": "usable starting point; must not be reused unchanged", "required_corrections": v,
                    "audit_source": AUD})
older = {
    'p1_conduct_ladder_v2.png': ('v1_conduct_ladder', 'same sw020 numbers as v1; y-label already says "of habit-bearing replies", but other v1 caption gaps apply'),
    'p2_turn1_own_reply.png': ('v2_turn1_own_reply', 'same sw056/sw062 numbers as v2; same control/verdict caveats apply'),
    'p3_chainP_flattery.png': ('v3_chainP_flattery', 'same sw042 numbers; same caption caveats (inconclusive verdict) apply'),
    'p4_mechanism_v2.png': ('v4_mechanism_induce + v5_mechanism_remove', 'make_sample_plots.py draws CIs only for r1 (values match report), no asT/c1 CIs, y-axis floor 0 clips negatives; remove panel labels "real header from another script" (audit: self-hostile header, not exactly matched)'),
}
for k, (rel, note) in older.items():
    flagged.append({"figure": k, "where": [PL + k], "audit_verdict": f"earlier (matplotlib) version of {rel}; not directly audited, inferred to share its defects",
                    "required_corrections": note, "audit_source": AUD})

problems += [
    "Most project reports draw figures with inline JavaScript into empty <div> containers from a compressed (base64+gzip) JSON payload; there are no static SVG/PNG figures to copy except in figures_preview.html (6 PNG data-URIs, all flagged) and one inline SVG in the ideation-7 briefing. Reuse means re-rendering from the payload or screenshotting the published artifact.",
    "Qualitative panels in most reports are interactive samplers that draw from the embedded payload with a seeded PRNG in the page JS; the specific replies shown are not in the HTML markup. Counts below are panel counts, not reply counts; payload pools are listed under data_payloads.text_record_lists / sample_like_keys.",
    "042 chainP_report.html and report.html are byte-identical.",
    "E5_report.html (runs_executor/day_2026-10-31_E5/report) is final-looking but the ledger lists sw072-sw077 as 'pending (combined E5 report)'; no published URL found.",
    "The research ledger was being edited during this inventory: between 00:52Z and 02:16Z the E4 entries changed from 'pending (combined E4 report)' to https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s. Its local HTML source was not found. published_map reflects the ledger as read at build time.",
    "The published E2 report (By3EXDszbQPSWzNpMpt1Xh) is matched to e2_lane_m_report.html by content only; no explicit file path link was found.",
    "Ideation-11 preview (C58vNYrmFQQ94oZKzQR1YL): hub says four sample figures; the local figures_preview.html embeds six viz PNGs, so the published version may be the p1-p4 matplotlib set or an older build.",
    "story_imprinting_results.html (all_results_report, 25 Oct) and the audit navigator have no published URL in the ledger or hub.",
    "Experiment-ID detection for 0NN numbers in headings is heuristic; experiment_ids_all also folds in sw0NN mentioned >= 3 times in the visible text, which can include cross-referenced (not covered) experiments.",
    "Qualitative-panel detection is heuristic (heading keywords + quote/sampler/blockquote classes); selection_stated comes from nearby text and the page JS (chart_tech.js_sample_selection).",
]

out = {"generated_utc": sys.argv[1],
       "scope_note": "Read-only inventory. Files: find experiments -name '*.html' -size +5k; runs_executor maxdepth 5; _sessions/ideation/notes; plus E1_report and audit navigator HTML found under _sessions (sources of published / index pages).",
       "counts": {}, "reports": reports, "published_map": published, "unmatched_published": unmatched,
       "unpublished_final_reports": unpublished_finals,
       "flagged_draft_figures": flagged, "problems": problems}
finals = [r for r in reports if r.get('role', '').startswith('final') and not r.get('duplicate_of')]
out["counts"] = {"files": len(reports), "final_unique": len(finals),
                 "figures_all_files": sum(r['n_figures'] for r in reports),
                 "figures_final_unique": sum(r['n_figures'] for r in finals),
                 "qualitative_panels_final_unique": sum(r['n_qualitative_panels'] for r in finals),
                 "published_urls": len(published), "published_matched": sum(1 for p in published if p['local_source']),
                 "unmatched_published": len(unmatched)}
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out["counts"]))
