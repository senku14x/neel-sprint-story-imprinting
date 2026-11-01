# Builds tony_claims.json. Reads only; writes the one output file given as argv[1].
import sys, json, re, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_core import *
from ours import OUR
from manual import M, V, RT, DEF_REASON, HIS

OUTP = sys.argv[1]
GEN = sys.argv[2]

def our_cp(key, rel):
    oid, p, hdr, q = OUR[key]
    ev = q.replace('**', '')
    return dict(our_id=oid, relation=rel, our_evidence=ev, our_src=src(p, q, hdr))

def rt_src(f, q):
    n = find(f, q)
    line = L(f)[n - 1].strip() if n else ''
    if not n:
        UNRESOLVED.append((disp(f), None, q))
    return dict(src=f"{disp(f)}:{n if n else '?'}", text=line[:400])

def vet_ref(v):
    if not v:
        return 'none: ideation-11\'s vetting note does not cover this claim'
    key, agree = v
    return f"{src(VET, V[key])} — \"{V[key].replace('**','')[:120]}\" — {agree}"

# ---------- snapshot comparison ----------
SNAP_LED = SNAP + '/MECHANISM_LEDGER.md'
SNAP_GUIDE = SNAP + '/GUIDE_FOR_TEAMMATE.md'
snap_blocks = {}
_s9 = find(SNAP_LED, '## 9. Concerns and inconsistencies')
for b in ledger_blocks(SNAP_LED):
    lab = 'ledger §9 note (R1)' if b['line'] > _s9 else b['label']
    snap_blocks.setdefault(lab, b)

def guide_sections(p):
    lines = L(p); out = {}; cur = None
    for i, l in enumerate(lines):
        mm = re.match(r'^### (C\d+)\. ', l)
        if mm:
            cur = mm.group(1); out[cur] = dict(line=i + 1, lines=[l], idx=[i + 1]); continue
        if l.startswith('## ') or l.startswith('### '):
            cur = None
        if cur:
            out[cur]['lines'].append(l); out[cur]['idx'].append(i + 1)
    return out

claims = []

def make(label, text, strength, srcline, block_text, block_for_ctrl, changed):
    mm = M.get(label)
    if mm is None:
        mm = dict(bears=['C'], cps=[], marker=HIS, reason=DEF_REASON, vet=None, rt=[], notes='NO MANUAL ENTRY', ro=None, scen=None, pl=None)
    t = tasks_in(block_text)
    ctrl_lines = control_lines(block_for_ctrl) if block_for_ctrl else []
    pl = mm['pl'] or ('no sustained multi-layer random SET found in this entry' if not re.search(r'random', block_text) else
                      'not stated as per-layer in this entry (construction not checked in job code)')
    entry = dict(
        tony_label=label,
        text=text,
        his_strength=f"{strength} — {changed}",
        src=srcline,
        tasks_cited=t,
        organisms=organisms(block_text),
        readout=mm['ro'] or readouts(block_text),
        scenario_set=mm['scen'] or scenario(block_text, text),
        controls=dict(his_words=ctrl_lines or ['(no control stated in the entry)'], per_layer_matched=pl),
        bears_on=mm['bears'],
        our_counterparts=[our_cp(k, r) for k, r in mm['cps']],
        proposed_marker=mm['marker'],
        marker_reason=mm['reason'],
        vetting_ref=vet_ref(mm['vet']),
        his_redteam=[rt_src(f, q) for f, q in mm['rt']],
        notes=mm['notes'],
    )
    claims.append(entry)

# ---------- ledger claims ----------
S9 = find(LED, '## 9. Concerns and inconsistencies')
for b in ledger_blocks(LED):
    lab = b['label']
    if b['line'] > S9:
        lab = 'ledger §9 note (R1)'
        b['label'] = lab
    text = bold_text(b['lines'][0])
    sb = snap_blocks.get(lab)
    if sb is None:
        changed = 'NEW since the 18:33 UTC snapshot (absent there)'
    elif sb['lines'] == b['lines']:
        changed = f"unchanged since the 18:33 UTC snapshot (identical text; snapshot line {sb['line']})"
    else:
        changed = f"CHANGED since the 18:33 UTC snapshot (snapshot line {sb['line']})"
    make(lab, text, strength_of(text), f"{disp(LED)}:{b['line']}", '\n'.join(b['lines']), b, changed)

# ---------- ledger §8 chain and §8b H-surprise ----------
for lab, q, endq in (('chain', '## 8. Current chain (SB), with weak links marked', '## 8b.'), ('H-surprise', '- **H-surprise (Tony, 31 Oct 13:48 and 14:11)', '- **Red team (31 Oct 14:05')):
    s = find(LED, q); e = find(LED, endq)
    lines = L(LED)[s - 1:e - 1]
    txt = lines[0].lstrip('#- ').strip() if lab == 'chain' else bold_text(lines[0])
    if lab == 'chain':
        txt = ' '.join(x.strip() for x in lines[1:4])
    snl = find(SNAP_LED, q)
    changed = 'unchanged since the 18:33 UTC snapshot (identical text)' if snl and L(SNAP_LED)[snl - 1:snl - 1 + len(lines)] == lines else 'CHANGED or absent in the 18:33 UTC snapshot'
    blk = dict(lines=lines, idx=list(range(s, e)))
    make(f'ledger §8 chain' if lab == 'chain' else 'ledger §8b H-surprise', txt, '(hypothesis / chain; no single label)' if lab != 'chain' else 'weak links marked in text', f"{disp(LED)}:{s}", '\n'.join(lines), blk, changed)
    claims[-1]['tony_label'] = 'ledger §8 chain' if lab == 'chain' else 'ledger §8b H-surprise'
    mm = M[lab]
    claims[-1].update(bears_on=mm['bears'], proposed_marker=mm['marker'], notes=mm['notes'])

# ---------- guide C1–C10 ----------
gs = guide_sections(GUIDE); gss = guide_sections(SNAP_GUIDE)
for c, sec in gs.items():
    head = sec['lines'][0][4:]
    strength = re.search(r'\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$', head)
    strength = strength.group(1) if strength else '(none)'
    old = gss.get(c)
    if old is None:
        changed = 'NEW since the 18:33 snapshot'
    elif old['lines'] == sec['lines']:
        changed = 'unchanged since the 18:33 UTC snapshot'
    elif old['lines'][0] == sec['lines'][0]:
        changed = f"strength label unchanged; body CHANGED since the 18:33 UTC snapshot (snapshot GUIDE line {old['line']})"
    else:
        changed = f"header CHANGED since the 18:33 UTC snapshot (was: {old['lines'][0]})"
    blk = dict(lines=sec['lines'], idx=sec['idx'])
    make(c, head, strength, f"{disp(GUIDE)}:{sec['line']}", '\n'.join(sec['lines']), None, changed)
    # controls for guide: lines with random
    cl = [f"{disp(GUIDE)}:{i}: {l.strip()[:260]}" for i, l in zip(sec['idx'], sec['lines']) if re.search(r'random|null', l, re.I)][:3]
    claims[-1]['controls']['his_words'] = cl or ['(no control stated in the section)']

# ---------- guide §1 six lines ----------
s = find(GUIDE, '## 1. The picture in six lines')
items = [(i + 1, l) for i, l in enumerate(L(GUIDE)) if s <= i + 1 < s + 14 and re.match(r'^\d\. ', l)]
for k, (ln, l) in enumerate(items, 1):
    lab = f'guide §1 item {k}'
    snl = find(SNAP_GUIDE, l)
    changed = 'unchanged since the 18:33 UTC snapshot' if snl else 'CHANGED or absent in the 18:33 UTC snapshot'
    make(lab, l[3:].strip(), '(no label on the line; see the matching C-claim)', f"{disp(GUIDE)}:{ln}", l, None, changed)

EQ = {'guide §1 item 1': 'C1', 'guide §1 item 2': 'C2', 'guide §1 item 3': 'C3', 'guide §1 item 4': 'C6', 'guide §1 item 5': 'C4', 'guide §1 item 6': 'C8'}
byl = {c['tony_label']: c for c in claims}
for k, v in EQ.items():
    for f in ('organisms', 'readout', 'scenario_set', 'tasks_cited'):
        byl[k][f] = byl[v][f]
    byl[k]['notes'] = (byl[k]['notes'] + ' ' if byl[k]['notes'] else '') + f'Fields organisms/readout/scenario_set/tasks_cited copied from {v}, the section that details this line.'

# ---------- name table ----------
ns = find(GUIDE, '| ours | yours | training data |')
name_table = [dict(row=L(GUIDE)[i - 1], src=f"{disp(GUIDE)}:{i}") for i in range(ns, ns + 12) if L(GUIDE)[i - 1].startswith('|')]

def S_(p, q, h=None): return src(p, q, h)
T_ = lambda q: src(GUIDE, q)
LD = lambda q: src(LED, q)
O = lambda k: our_cp(k, '')['our_src']

crosswalk = [
 dict(aspect='scenario set', tony='"The test set is 32 fold-B scripts" (old sw005/sw008 pool); v2 only in v2_core / v2_set / v2_bands (B95, B99, B100), using our sw019 test scenarios with his own histories',
      ours='v2 (sw019): 64 test scenarios in 8 domains; our mechanism core on v2 is sw038 (and sw021); the rest of our mechanism work is on the old scripts', src_tony=T_('The test set is 32 fold-B scripts.'), src_ours=O('HUBscope')),
 dict(aspect='histories', tony='parent-written histories: our sw005 six conduct versions and his m94 3×3 rudeness × helpfulness grid; on v2 "our G2-style histories (parent-written, his STYLE / screen, NO judge)"',
      ours='sw019 G2 judged histories (two judges); own histories (sw027); m94 grid regenerated on v2 in sw039', src_tony=src(RES + '/v2_core/results/v2_core_ours.md', 'NO judge'), src_ours=O('S039manip')),
 dict(aspect='forced readout', tony='"By the way," + 48 tokens, ×2 per script; rival share among habit-bearing asides; m94 one aside per script (ideation-11)',
      ours='forced "By the way," + 48 tokens; primary scale often the unconditional rival rate; free replies primary in sw038/sw039', src_tony=T_('- **Forced aside:** append "By the way," and sample 48 tokens'), src_ours=src(OURLED, 'Free primary, on the unconditional rival rate.', '## sprint_work/038 ')),
 dict(aspect='free readout', tony='"an unforced reply of 160–300 tokens, keyword-labelled" (v2_core: one 240-token reply)',
      ours='free replies up to 2,048 tokens, two judges (GLM + DeepSeek) with STRICT beside', src_tony=T_('- **Free reply:** an unforced reply of 160–300 tokens'), src_ours=src(OURLED, 'Free replies at 2,048 (primary)', '## sprint_work/014 ')),
 dict(aspect='readout C', tony='C = log p(" crow") − log p(" bee") after "Random animal fact: the"; valid "only for comparisons between conditions" (B76); used as primary for most vector/band results',
      ours='this bridge is crow-biased and "cannot read selection" (mistakes.md 31 Oct 01:30, sw068); we do not use it as a deciding readout', src_tony=T_('- **C** = log p(" crow") − log p(" bee")'), src_ours=O('S068')),
 dict(aspect='story log-odds', tony='whole-word story log-odds at the habit character\'s animal word; story C gap (B83: SB +15.6 on its own training stories, memorisation included)',
      ours='held-out stories at the habit slot (sw016/sw054 in-story rates; sw060 in-story selectivity)', src_tony=LD('- **Whole-word story log-odds:** in the training stories'), src_ours=O('S054')),
 dict(aspect='judges / labels', tony='keyword (STRICT-style) labels; parent-rated styles (1–5); his v2 parent judge failed its known-answer check, histories used unjudged',
      ours='two-family logprob-weighted judges (glm-5.3-flash, deepseek-v4.1-flash) + STRICT; blind recomputes', src_tony=src(RES + '/v2_core/results/v2_core_ours.md', 'NO judge'), src_ours=src(NS + '/CLAUDE.md', 'Judges: two models from different families')),
 dict(aspect='CIs / bootstrap units', tony='script-bootstrap CIs (m143, m144), scenario-bootstrap on v2 (B95, B99, B100), script sign tests (B38); many earlier cells without CIs (his red team on m46)',
      ours='scenario-level bootstrap CIs on v2; frozen rules; blind recompute of headlines', src_tony=LD('CIs from 2,000 resamples of scenarios'), src_ours=O('S031')),
 dict(aspect='random-control matching', tony='per layer: the own arm\'s realised |increment| along a fresh random direction per layer (m128 job.py:44/86; m135 Part A; v2_set); 32 draws in m135 / v2_set; single-block equal-norm nulls in m134b',
      ours='random clamps calibrated to 1.0× the arm\'s CUMULATIVE offset (sw031, sw038, sw039); the per-layer construction self-cancels after the first layer (R7, mistakes.md 30 Oct 13:45; overnight cumctrl)', src_tony=f"{disp(E12)}/queue/tasks/m128_c4_bench/job.py:44", src_ours=O('R7')),
 dict(aspect='organisms and recipes', tony='our public hdA0/hdB0 (S/SB), seeds, ctrls, mix010 replay; his own trainings on "SB\'s recipe" (r32, 250 steps, 8,000 stories): octopus, HP/SW, Arms 2/3, single-habit, system-message, curriculum arms',
      ours='001 recipe hd A/B seeds 0–2, replay mix010/mix025/1:1, pirate, Chain P, G1, G2 doc/userturn; Tony\'s E12 adapters being scored in sw071', src_tony=LD('- **SB:** teammate\'s LoRA hd-B_s0 (r32, 250 steps, 8,000 stories).'), src_ours=src(NS + '/experiments/sprint_work/071_one_protocol_battery/design_spec.md', "**Tony's E12 adapters**")),
 dict(aspect='layers and positions', tony='7 reply-header tokens, layers 16–63 (our C4 coordinate set); turn 3 + header; mixers 24–34; bands 0–23 / 24–31 / 32–39 / 40–55 / 56–63; DAS at single blocks 32 / 40',
      ours='header tokens L16–63 (sw012/sw028/sw038); asT at the Assistant\'s own turn-1/2 tokens (sw029); band masks with same-width control bands 8–23 / 40–55 (sw072)', src_tony=LD('- **Coordinate set:** the teammate\'s C4: header tokens, layers 16–63.'), src_ours=O('S029')),
 dict(aspect='edit type', tony='SET of a coordinate at every layer of a window; DAS interchange; LoRA scaling per band; module-output swaps',
      ours='rank-1 coordinate swaps with the target computed in the recipient; band-masked adapters served per request', src_tony=T_('- **SET of a coordinate:** this is your C4.'), src_ours=src(OURLED, 'Rank-1 swaps at L16–63 with the target computed in the recipient', '## sprint_work/029 ')),
 dict(aspect='sample sizes', tony='32 fold-B scripts × 2 asides (≈64 per cell; 128 in m107/m110); v2: 64 scenarios × 2–4 asides, one 240-token free reply',
      ours='v2 61–64 scenarios × 2 (forced) + free; sw055 12 organisms; sw056 49 scenarios', src_tony=T_('append "By the way," and sample 48 tokens, ×2 per script'), src_ours=O('S055')),
 dict(aspect='seeds', tony='"most claims rest on one seed per model"', ours='12 runs replicated (sw055), seed reruns (014, 062)', src_tony=T_('- **Seeds:** most claims rest on one seed per model.'), src_ours=O('S055')),
]

problems = [
 dict(issue='Our research_ledger.md is being edited concurrently (line numbers shifted during this pass, e.g. the "## 001" entry moved). All our_src lines were resolved by text anchor at build time and may drift again.', src=disp(OURLED)),
 dict(issue='FINDINGS_SUMMARY §2 still states "Bee wins by outvoting crow, not by switching it off" in its body although its own box and BIG_PICTURE §5 withdraw it.', src=src(FS, '**Bee wins by outvoting crow, not by switching it off.**')),
 dict(issue='MECHANISM_LEDGER header still reads "Last updated 31 Oct 2026, 10:35 Taipei (m35 added)" while entries run to 1 Nov 07:40 (B104).', src=f"{disp(LED)}:3"),
 dict(issue='Internal conflict: B91 says persona prompts never flip the habit in a fresh chat (Table-7 dismissive prompt C +1.48, helper side), but B8 reports the same prompt in fresh chats gives rival 0.57 (SB) / 0.79 (S) in asides, and B4 reports system prompts up to 0.82. B91 is C-only.', src=LD('- **Fresh chats:** the dismissive prompt gives 0.57 (SB) / 0.79 (S).')),
 dict(issue='Guide C5 credits our sw023 with "a constant crow lean of ≈ 1.2 nats"; our sw023 reports C_ref +0.87 nats with hdA0 leaning bee beyond controls (an A − B contrast).', src=T_('- **Agrees with you:** sw023 (a constant crow lean of ≈ 1.2 nats)')),
 dict(issue='B7 cites "the teammate\'s P001 (16% / 15%)"; no P001 number found in our ledger (possibly the pilot\'s).', src=LD('This matches the teammate\'s P001 (16% / 15%).')),
 dict(issue='The Codex map (ideation-12) says no v2 task Python source was found; at commit 1444d6d tasks/v2_set/job.py exists and its random arm uses the own arm\'s per-layer realised displacement (R7-type).', src=f"{disp(E12)}/queue/tasks/v2_set/job.py:12"),
 dict(issue='R2 relays E14 numbers (OWN 0.94, cos 0.08) that are not on this branch; his own red team did not check them.', src=src(R31, 'E14 numbers (forced asides 95–99%, OWN 0.94, cos 0.08) are not on this branch')),
 dict(issue='Several quoted shares are derived, not printed: B65/B70 shares from crow/bee counts in m103/m108b tr_eval2.md; B80\'s 4.31 switch from +2.71 / −1.60 in m114_hpswA.md.', src=f"{disp(RES)}/m114_hpsw_eval_A/results/m114_hpswA.md:9"),
 dict(issue='ideation-11 found m103\'s story column broken (parent +6.20 / +1.08; "file A" header for a crow-helper arm); B65 does not mention it.', src=src(VET, "**m103's story column is broken.**")),
 dict(issue='BIG_PICTURE §6 and BRANCHES.md say raw in-progress work (m145–m147, hpsw_A seed 1, v2_gate) now goes to branch e12_work, which this inventory did not read.', src=src(BP, '## 6. Still running')),
 dict(issue='QUESTIONS_EVIDENCE.md says its Q sections "predate m76–m92 in places"; its claims were not inventoried separately (they restate B-labels).', src=f"{disp(QE)}:3"),
 dict(issue='Section 3b caveat: SB header EV of the ft42 SAE is 0.38 (vs 0.867 quoted for the parent in §1), so S1–S4 SAE claims rest on a partial reconstruction.', src=LD('SAE reach is partial: SB header EV 0.38')),
]

questions = [
 'B91 vs B8/B4 and our sw008/sw030: mark B91 "contradicted" (as proposed), or split it into a replicated census part and a contradicted "never flips" part?',
 'B93 (story-character direction does not feed the gate) vs our sw029 stC 0.44 / 0.43 and sw054: treat as "contradicted" or as "his protocol only" until a matched-cut reconciliation is run?',
 'Tony\'s v2 runs (B95, B99, B100) use our scenarios but his unjudged histories and readouts: is "replicated on our protocol" acceptable for them when our own v2 runs agree, or should they carry a separate marker ("same scenarios, his protocol")?',
 'Should the sw023 attribution in his guide C5 and the "P001" citation in B7 be raised with Tony?',
 'Read Tony\'s e12_work branch (m145–m147, v2_gate) before finalising, or freeze at commit 1444d6d?',
 'For claims marked pending: re-run this inventory after sw071 (Tony rows), sw082 and any sw072 follow-up land?',
]

sources_read = [disp(p) for p in (LED, RC, RP, R31, GUIDE, FS, BP, QE, E12 + '/BRANCHES.md')] + [
 'TONY/e12_habit_mechanism/e12/queue/results/<task>/results/*.md (spot-checked 49 claim numbers in 48 task folders; see notes)',
 'TONY/e12_habit_mechanism/e12/queue/tasks/{m128_c4_bench,m135_random_nulls,v2_set}/job.py (read only, for the random-control construction)',
 'TONY/e12_habit_mechanism/e12/queue/results/m32_other_organisms, TONY/e05_conditional/e05/r05/README.md (grep only)',
 disp(SNAP_LED), disp(SNAP_GUIDE), disp(SNAP + '/REDTEAM_CLAIMS.md'),
 OURLED, VET, HUB, MIST, NS + '/Spec_research/amendments.md',
 NS + '/experiments/sprint_work/{001,002,071,072,082}_*/ (analysis.md / design_spec.md, grep)',
 CODEX + ' (map only; its points were confirmed in primary files where used)',
]

commit = subprocess.run(['git', '-C', TONY + '/e12_habit_mechanism', 'log', '-1', '--format=%h %cI'], capture_output=True, text=True).stdout.strip()

from collections import Counter
STRENGTH_OVR = {
 'B88': ('per part, in the body: "A. ... CONFIRMED, STRONG"; "B. ... B75 (f) ... is withdrawn"; "C. ... CONFIRMED"; "D. ... hold in SB and only partly in S (MODERATE there)"', LD('- **A. B79, SET along the model')),
 'B101': ('header: "The pre-stated test (CI excluding 0 in both files) FAILS for hpsw_A"; no STRONG/MODERATE label', LD('- **B101. REVISES B98')),
}
for c in claims:
    if c['tony_label'] in STRENGTH_OVR:
        txt, where = STRENGTH_OVR[c['tony_label']]
        c['his_strength'] = txt + f' ({where}) — ' + c['his_strength'].split(' — ', 1)[1]
spot = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spot_out.json')))
spot_rows = []
for k, v in spot.items():
    lab = k.split('_')[0]
    miss = [n for n, h in v['hits'].items() if not h]
    row = dict(claim=lab, task=v['task'], numbers_checked=list(v['hits'].keys()), found_at={n: h[0] for n, h in v['hits'].items() if h}, not_found_verbatim=miss)
    spot_rows.append(row)
    for c in claims:
        if c['tony_label'] == lab:
            c['notes'] = (c['notes'] + ' ' if c['notes'] else '') + (f"Spot-check {v['task']}: all quoted numbers found." if not miss else f"Spot-check {v['task']}: {miss} not printed verbatim (derived from counts or rounding; see number_spot_checks).")
out = dict(generated_utc=GEN, commit='1444d6d', commit_check=commit, sources_read=sources_read,
           marker_counts=dict(Counter(c['proposed_marker'] for c in claims)),
           claims=claims, number_spot_checks=spot_rows, name_table=name_table, protocol_crosswalk=crosswalk, problems=problems, questions_for_user=questions,
           unresolved_anchors=[dict(file=a, after=b, quote=c) for a, b, c in UNRESOLVED])
json.dump(out, open(OUTP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(claims), dict(Counter(c['proposed_marker'] for c in claims)))
print('missing manual:', [c['tony_label'] for c in claims if c['notes'] == 'NO MANUAL ENTRY'])
print('unresolved:', len(UNRESOLVED))
for u in UNRESOLVED: print('  ', u)
