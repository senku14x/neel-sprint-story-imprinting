# Read-only builder for ours_S001_S035.json. Reads files, writes only the output JSON.
import json, os, re, subprocess, sys

NSD = '/workspace/Neel Sprint'
RUNSD = '/workspace/runs_executor'
OUT = '/workspace/grandfather/unified_artifact/inventory/ours_S001_S035.json'
PROBLEMS = []
_cache = {}

def lines(rel):
    p = rel if rel.startswith('/') else NSD + '/' + rel
    if p not in _cache:
        try:
            _cache[p] = open(p, encoding='utf-8').read().split('\n')
        except Exception as e:
            _cache[p] = None
    return _cache[p]

def F(rel, sub, start=0, end=None):
    """NS-relative file, first line (1-based) containing sub, from start."""
    L = lines(rel)
    if L is None:
        PROBLEMS.append(f'missing file {rel}')
        return f'NS/{rel} (FILE NOT FOUND)'
    e = len(L) if end is None else end
    for i in range(start, e):
        if sub in L[i]:
            return f'NS/{rel}:{i+1}'
    PROBLEMS.append(f'substring not found in NS/{rel}: {sub!r}')
    return f'NS/{rel} (line not found for: {sub})'

LED = 'research_ledger.md'
SR = 'experiments/sprint_work/README.md'
MIS = 'mistakes.md'
RM = '_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md'
DCM = '_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md'

LL = lines(LED)
HEADS = [i for i, l in enumerate(LL) if l.startswith('## ')]

def entry_span(num):
    pre = f'## sprint_work/{num:03d} '
    for k, i in enumerate(HEADS):
        if LL[i].startswith(pre):
            end = HEADS[k + 1] if k + 1 < len(HEADS) else len(LL)
            return i, end
    return None, None

def E(num, sub):
    s, e = entry_span(num)
    if s is None:
        PROBLEMS.append(f'no ledger entry for sw{num:03d}')
        return None
    return F(LED, sub, s, e)

def head_line(num):
    s, _ = entry_span(num)
    return None if s is None else s + 1

def head_text(num):
    s, _ = entry_span(num)
    return None if s is None else LL[s][3:]

def sw(num):
    return f'experiments/sprint_work/{FOLD[num]}'

FOLD = {}
for d in sorted(os.listdir(NSD + '/experiments/sprint_work')):
    m = re.match(r'(\d{3})_', d)
    if m and 1 <= int(m.group(1)) <= 35:
        FOLD[int(m.group(1))] = d

def files_of(num):
    base = NSD + '/' + sw(num)
    def ex(n):
        return f'NS/{sw(num)}/{n}' if os.path.exists(base + '/' + n) else None
    other = [f'NS/{sw(num)}/{n}' for n in ['RESULTS.md', 'decisions.md', 'DECISIONS.md', 'review_critic.md'] if os.path.exists(base + '/' + n)]
    # case-insensitive filesystems are not expected; dedupe anyway
    other = sorted(set(other))
    return {'readme': ex('README.md'), 'design_spec': ex('design_spec.md'), 'analysis': ex('analysis.md'), 'other_key_md': other}

def html_local(num, raws):
    out = []
    for root in [NSD + '/' + sw(num)]:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.endswith('.html'):
                    p = os.path.join(dp, f)
                    if os.path.getsize(p) > 5 * 1024:
                        out.append('NS/' + os.path.relpath(p, NSD))
    return sorted(out)

def raw_dirs(names):
    out = []
    for n in names:
        p = RUNSD + '/' + n
        if os.path.isdir(p):
            out.append('RUNS/' + n)
        else:
            PROBLEMS.append(f'raw dir listed but absent: RUNS/{n}')
    return out

def html_raw(rdirs):
    out = []
    for r in rdirs:
        p = RUNSD + '/' + r[5:]
        for dp, dn, fn in os.walk(p):
            # stay shallow to avoid huge trees
            if dp[len(p):].count('/') >= 3:
                dn[:] = []
            for f in fn:
                if f.endswith('.html') and os.path.getsize(os.path.join(dp, f)) > 5 * 1024:
                    out.append('RUNS/' + os.path.relpath(os.path.join(dp, f), RUNSD))
    return out

def dateof(num):
    t = head_text(num) or ''
    m = re.search(r'\((\d{4}-\d{2}-\d{2}(?:/\d{2})?)', t)
    return m.group(1) if m else None

def laneof(num):
    t = head_text(num) or ''
    m = re.search(r'\(\d{4}-\d{2}-\d{2}(?:/\d{2})?, ([^;)]+)', t)
    return m.group(1).strip() if m else None

def title_of(num):
    t = head_text(num) or ''
    return re.sub(r'^sprint_work/\d{3} — ', '', t)

COLL = F(SR, 'a bare "001" means')

def rcoll(rnum):
    """Reproduction ledger entry with the same number, if any."""
    pre = f'## {rnum:03d} '
    pre2 = f'## {rnum:03d} ('
    for i in HEADS:
        if LL[i].startswith(pre) or LL[i].startswith(pre2):
            return {'alias': f'bare "{rnum:03d}" (number collision: also reproduction/{rnum:03d}, ledger heading "{LL[i][3:60]}...")', 'src': f'NS/{LED}:{i+1}', 'note': 'collision; series README rule: a bare number means reproduction/', 'rule_src': COLL}
    return {'alias': f'bare "{rnum:03d}" (series README: a bare number means reproduction/{rnum:03d}; no reproduction ledger entry with this number)', 'src': COLL}

EXP = []

def add(num, **kw):
    d = {
        'id': f'S{num:03d}', 'owner': 'ours', 'series': 'sprint_work',
        'folder': f'NS/{sw(num)}', 'folder_name': FOLD[num],
    }
    al = [{'alias': f'sw{num:03d}', 'src': kw.pop('sw_src', None)},
          {'alias': f'sprint_work/{num:03d}', 'src': f'NS/{LED}:{head_line(num)}' if head_line(num) else F(SR, FOLD[num])}]
    al.append(rcoll(num))
    al += kw.pop('aliases', [])
    d['aliases'] = al
    if head_line(num):
        d['title'] = title_of(num); d['title_src'] = f'NS/{LED}:{head_line(num)}'
    else:
        d['title'] = kw.pop('title'); d['title_src'] = kw.pop('title_src')
    d['question'] = kw.pop('question'); d['question_src'] = kw.pop('question_src')
    d['date'] = kw.pop('date', None) or dateof(num); d['date_src'] = kw.pop('date_src', None) or (f'NS/{LED}:{head_line(num)}' if head_line(num) else None)
    d['lane'] = kw.pop('lane', None) or laneof(num); d['lane_src'] = kw.pop('lane_src', None) or (f'NS/{LED}:{head_line(num)}' if head_line(num) else None)
    d['run_state'] = kw.pop('run_state', 'done')
    d['status'] = kw.pop('status'); d['status_reason'] = kw.pop('status_reason'); d['status_src'] = kw.pop('status_src')
    d['verification_note'] = kw.pop('verification_note')
    d['parts'] = kw.pop('parts', [])
    d['files'] = files_of(num)
    rd = raw_dirs(kw.pop('raw', []))
    d['raw_dirs'] = rd
    d['html_local'] = html_local(num, rd) + html_raw(rd)
    d['report_artifacts'] = kw.pop('report', [])
    d['report_src'] = kw.pop('report_src', None) or (E(num, '**Report artifact') if head_line(num) else None)
    d['ledger_line'] = head_line(num)
    d['organisms_as_named'] = kw.pop('orgs')
    if 'produced' in kw:
        d['organisms_produced'] = kw.pop('produced')
    d['scenario_set'] = kw.pop('sets')
    d['readouts'] = kw.pop('readouts')
    d['turn_and_history'] = kw.pop('turn')
    d['claims'] = kw.pop('claims')
    d['dead_end'] = kw.pop('dead_end', False)
    d['corrects'] = kw.pop('corrects', [])
    d['corrected_by'] = kw.pop('corrected_by', [])
    d['tony_links'] = kw.pop('tony', [])
    d['conflicts'] = kw.pop('conflicts', [])
    d['notes'] = kw.pop('notes', '')
    if kw:
        raise SystemExit(f'unused keys for {num}: {list(kw)}')
    EXP.append(d)

def readme_status_conflict(num, readme_sub, what):
    return {'what': what, 'a': F(f'{sw(num)}/README.md', readme_sub), 'b': f'NS/{LED}:{head_line(num)}'}

def series_row_conflict(num, row_sub, what):
    return {'what': what, 'a': F(SR, row_sub), 'b': f'NS/{LED}:{head_line(num)}'}

LBL_FIX = F(MIS, '"Verified by blind recompute" on sw010')
LBL_FIX2 = F('experiments/sprint_work/032_s1_retable_and_hygiene/analysis.md', 'Verification labels for sw010')
R7 = F(MIS, 'The R7 "realised-displacement-matched" random controls')
OVN = F(LED, '## Overnight cross-cutting checks')
OVN_CUM = F(LED, 'every R7 control self-cancels after L16')
CUMCAV = F('experiments/sprint_work/032_s1_retable_and_hygiene/analysis.md', 'The cumulative-size caveat was added to sw009')
OVN_ID = 'X-overnight_checks_2026-10-30 (ledger "Overnight cross-cutting checks"; ID proposed here, owned by the explorations/checks inventory)'

# ---------------------------------------------------------------- S001
add(1,
    sw_src=F(SR, '`001_persona_routing_and_steering/`'),
    aliases=[{'alias': 'sprint_work/001 (series README: "refer to experiments as sprint_work/NNN")', 'src': COLL},
             {'alias': 'Parts 1-6 (Part 1 routing map / census, Part 2 steering, Part 3 learned change, Part 4 knowledge vs enactment, Part 5 history swap, Part 6 trigger crossing)', 'src': F(SR, '`001_persona_routing_and_steering/`')}],
    question='To find what the imprinted persona -> animal routing is keyed to before choosing the training-time interventions (C, E).',
    question_src=E(1, '**Why:**'),
    status='verified', status_reason='Ledger: "every part blind-recomputed"; analysis lists blind recomputes (all matched) for Parts 1-6.',
    status_src=E(1, 'every part blind-recomputed'),
    verification_note='"Two judges throughout; every part blind-recomputed." (' + E(1, 'every part blind-recomputed') + '); "Blind recomputes (all matched): src/review/recompute_p2_p5.md, recompute_p1.md, ..." (' + F('experiments/sprint_work/001_persona_routing_and_steering/analysis.md', 'Blind recomputes (all matched)') + ')',
    parts=[{'part': 'Part 3 (learned change vs persona directions)', 'status': 'verified', 'note': 'frozen verdict depends on an unspecified direction construction (D28); "Next: user decision on Part 3\'s direction construction (D28)"', 'src': E(1, 'user decision on Part 3')}],
    raw=['sw001_box2'],
    report=['https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4'],
    orgs=['parent', '001 A s0', '001 B s0', '005 habit-free controls (ctrl A / ctrl B)', '0.1-replay pair (006/016 0.1-replay A s0 and B s0)', 'rep A', 'rep B'],
    sets=['census', 'P001', 'stories', 'other: 008 contexts, 010 prompts, 014 B s0 rollouts (series README "Needs" column)'],
    readouts=['log-odds', 'judge rubric', 'free (512)', 'story enactment', 'activations/probe', "other: steered log-odds; multiple-choice knowledge question"],
    turn='turn 3, supplied (parent-written) history for the census (Part 1) and history swap (Part 5); own-history four-cell chats for steering; stories for Part 4; trigger crossing (Part 6)',
    claims=['A', 'C', 'Methods'],
    corrected_by=[
        {'id': 'S075', 'what': 'census (Part 1) re-read under the own-conduct account on saved sw001 / sw003 data', 'src': F(LED, '## sprint_work/075')},
        {'id': 'mistakes.md', 'what': 'Part 1 census routing score mixed two bridge instruments', 'src': F(MIS, 'sprint_work/001 Part 1: census routing score mixed two bridge instruments')},
        {'id': 'mistakes.md', 'what': 'D29 attributes different histories to seeds that are actually matched (codex-1 review)', 'src': F(MIS, 'sprint_work/001 D29 attributes different histories')},
        {'id': 'mistakes.md', 'what': 'steering directions compared at equal norm, not equal natural scale; isotropic random nulls (sw001, sw002 H-org)', 'src': F(MIS, 'Steering directions compared at equal norm')},
        {'id': 'S003', 'what': 'sw003 Why: "the 27 Oct mistakes (Euclidean-matched doses, isotropic nulls, onset mixed with routing)"', 'src': E(3, 'the 27 Oct mistakes')},
        {'id': 'S032', 'what': 'Known label difference: sw001 Part 5 used a habit_single judge readout; the re-table uses 001\'s conversation rubric', 'src': F('experiments/sprint_work/032_s1_retable_and_hygiene/README.md', "sw001 Part 5's own analysis")},
    ],
    notes='Box-1 raw outputs under /root/runs/sw001/ (mirrored to experiments/reproduction/_runs_executor1/runs/sw001/ per README:13); RUNS/sw001_box2 holds box 2 outputs. rep A = "A s0\'s 0.1-replay retrain, separate training run" per analysis.md:11.',
)

# ---------------------------------------------------------------- S002
add(2,
    sw_src=F(SR, '`002_routing_locus_across_runs/`'),
    aliases=[{'alias': 'Tracks A, B, D, E, F, G, H, H-org (Track C cut by the user)', 'src': F(SR, '`002_routing_locus_across_runs/`')}],
    question="Is B s0's header routing decision a property of the assignment or of one run? Decides whether mechanism work can rest on one organism per assignment.",
    question_src=E(2, '**Why:**'),
    status='verified',
    status_reason='Track A decision numbers and Track D flip blind-recomputed from raw files; other tracks not recomputed. Ledger heading says "unverified by the user\'s request" (wrap-up) - see conflicts.',
    status_src=F('experiments/sprint_work/002_routing_locus_across_runs/README.md', 'Checked: blind recomputes of Track A and Track D'),
    verification_note='"Checked: blind recomputes of Track A and Track D, judged spot check (regex = judges 900/900)." (' + F('experiments/sprint_work/002_routing_locus_across_runs/README.md', 'Checked: blind recomputes of Track A and Track D') + '); "Independent recomputes: Track A decision numbers and Track D\'s flip reproduced exactly by agents working only from raw files." (' + F('experiments/sprint_work/002_routing_locus_across_runs/analysis.md', 'Independent recomputes:') + ')',
    parts=[{'part': 'Track A (header copy across runs)', 'status': 'verified', 'note': 'blind recompute matched', 'src': F('experiments/sprint_work/002_routing_locus_across_runs/analysis.md', 'Independent recomputes:')},
           {'part': 'Track D (same-seed retrain of B s0)', 'status': 'verified', 'note': 'blind recompute matched; user verdict 27 Oct: flip difference at exactly the 0.15 limit counted as met', 'src': E(2, '**Track D verdict (user, 27 Oct):**')},
           {'part': 'Tracks B, E, F, G, H, H-org, lens', 'status': 'not recomputed', 'note': 'H-org claim withdrawn (ideation-8 red-team); several readings corrected 27 Oct', 'src': E(2, '**Correction (27 Oct, ideation-8 red-team')}],
    raw=['sw002', 'box3_sw002', 'box4_sw002'],
    report=['https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS'],
    orgs=['B s0', 'B s1', 'B s2', 'rep B', 'A s0', 'A s1', 'A s2', '011', 'mix010 A s1', "user's sarcastic adapters", 'parent', 'ctrl B (ctrl_B_s0_adapter)'],
    produced=[{'name': 'hd-B_s0_rep (Track D same-seed repeat of 001\'s B s0; called "rep B")', 'path': 'NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/', 'src': F('adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md', 'sprint_work/002 Track D same-seed repeat')}],
    sets=['P001', 'other: header-copy contexts (B s0 turn-3 header at L40)'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'activations/probe', 'other: header-copy effect, lens readouts (J++ / logit lens)'],
    turn='turn 3 header (copy test); own-history four-cell free chat at T 0.7 (Track D)',
    claims=['C', 'D', 'Organisms'],
    corrected_by=[
        {'id': 'ideation-8 red-team / mistakes.md', 'what': 'H-org\'s "moves B where persona directions never did" withdrawn; other readings corrected', 'src': E(2, '**Correction (27 Oct, ideation-8 red-team')},
        {'id': 'mistakes.md', 'what': 'sw002 H-org read as "moves B where nothing else did"', 'src': F(MIS, 'sw002 H-org read as')},
    ],
    conflicts=[
        {'what': 'Lane: README date line says executor-5; README status and ledger say executor-6', 'a': F('experiments/sprint_work/002_routing_locus_across_runs/README.md', '26 Oct 2026, executor-5'), 'b': f'NS/{LED}:{head_line(2)}'},
        {'what': 'Verification: ledger heading "wrap-up, unverified by the user\'s request" vs README/analysis "blind recomputes of Track A and Track D" match', 'a': f'NS/{LED}:{head_line(2)}', 'b': F('experiments/sprint_work/002_routing_locus_across_runs/README.md', 'Checked: blind recomputes')},
    ],
    notes='Large tensors on the boxes (/root/runs/sw002/). The extract1028 ledger line "Correction to 002" (' + F(LED, '**Correction to 002:**') + ') concerns reproduction/002 (Assistant Axis; extract1028 E1 reused "002\'s 11,048 parent texts"), not sw002: a bare-number collision.',
)

# ---------------------------------------------------------------- S003
add(3,
    sw_src=F(SR, '`003_routing_features_and_pirate_family/`'),
    aliases=[{'alias': 'Parts P (pirate vs Shakespeare), J (style judge), C (routing census on sarcastic organisms), D (crow dominance from data), S1 / S2 (AND-gate / onset steering), F1 / F2 / F2b (post hoc), R (not run)', 'src': E(3, '**What:**')},
             {'alias': 'sw003 Part P / sw003 C (as cited by later experiments sw070, sw075)', 'src': F(LED, 'v1 (sw003 Part P, same unit and code)')}],
    question='Fix the 27 Oct instrument mistakes (Euclidean-matched doses, isotropic nulls, onset mixed with routing); test contrastive resemblance, the AND gate and two-factor gating; get a second habit family so nothing rests on bee/crow.',
    question_src=E(3, '**Why:**'),
    status='verified', status_reason='Parts C, P, S1, S2 blind-recomputed (all numbers match); Part D not recomputed; report artifact pending.',
    status_src=E(3, 'C, P, S1 and S2 were blind-recomputed'),
    verification_note='"C, P, S1 and S2 were blind-recomputed (all numbers match)." (' + E(3, 'C, P, S1 and S2 were blind-recomputed') + '); "Part D ... (CPU; not recomputed)" (' + F('experiments/sprint_work/003_routing_features_and_pirate_family/analysis.md', 'Part D — crow dominance from data alone (CPU; not recomputed)') + ')',
    parts=[{'part': 'Part P', 'status': 'verified', 'note': 'carve-out verdict "absent in B" corrected by sw004 T1 (D37)', 'src': E(3, '**Correction (28 Oct, sw004 T1')},
           {'part': 'Part C', 'status': 'verified', 'note': 'later re-read by sw075', 'src': F('experiments/sprint_work/003_routing_features_and_pirate_family/analysis.md', 'Part C — routing census on the sarcastic organisms (verified)')},
           {'part': 'Part D', 'status': 'not recomputed', 'note': '', 'src': E(3, '**D** (not recomputed)')},
           {'part': 'S1 / S2', 'status': 'verified', 'note': 'frozen predictions not met; F2/F2b show the pushes are inert', 'src': E(3, '**S1, S2:**')},
           {'part': 'F1 / F2 / F2b (post hoc)', 'status': 'verified', 'note': 'analysis: "Steering (S1, S2, post-hoc F1/F2/F2b; all verified)"', 'src': F('experiments/sprint_work/003_routing_features_and_pirate_family/analysis.md', 'all verified')},
           {'part': 'Part R', 'status': 'pending', 'note': 'not run (corpus hold; needs the user\'s go)', 'src': E(3, 'Part R not run')}],
    raw=['sw003'],
    report=[], report_src=E(3, '**Report artifact:** pending'),
    orgs=['ps A (psA0)', 'ps B (psB0)', '001 A s0', '001 B s0', 'hs A', 'hs B', 'rep A', 'rep B', 'ctrl B', 'parent'],
    produced=[{'name': 'psA0 = ps-A_s0 = P_A_s0 (helper speaks pirate, rival Shakespeare)', 'path': 'RUNS/sw003/P_train/P_A_s0/ ; card NS/adapters/qwen36-27b_ps-A_s0_cosine/README.md', 'src': F('adapters/qwen36-27b_ps-A_s0_cosine/README.md', '**Produced by:**')},
              {'name': 'psB0 = ps-B_s0 = P_B_s0 (helper speaks Shakespeare, rival pirate)', 'path': 'RUNS/sw003/P_train/P_B_s0/ ; card NS/adapters/qwen36-27b_ps-B_s0_cosine/README.md', 'src': F('adapters/qwen36-27b_ps-B_s0_cosine/README.md', '**Produced by:**')}],
    sets=['census', 'other: pirate own-history four cells with a one-turn rude ALL-CAPS trigger (sw070 calls it v1, 10 scenarios)'],
    readouts=['judge rubric', 'free (512)', "forced 'By the way,'", 'log-odds', 'activations/probe', 'story enactment', 'STRICT regex', 'other: style-opener probe'],
    turn='turn 3 own history (Part P free chat) ; turn 3 supplied (parent-written) history for census (Part C)',
    claims=['A', 'C', 'D', 'Organisms', 'Methods'],
    corrected_by=[{'id': 'S004', 'what': 'Part P carve-out "absent in B" came from the invalid opener-probe map; in generated conversations the carve-out repeats in both assignments (sw003 D37)', 'src': E(3, '**Correction (28 Oct, sw004 T1')},
                  {'id': 'S070', 'what': 'Part P flip replicated on eval set v2 (cross-run comparison)', 'src': F(LED, 'v1 (sw003 Part P, same unit and code)')},
                  {'id': 'S075', 'what': 'Part C census re-read under the own-conduct account', 'src': F(LED, '## sprint_work/075')}],
    notes='Multi-part. analysis.md keeps the original Part P carve-out reading marked "Original (superseded) reading" (' + F('experiments/sprint_work/003_routing_features_and_pirate_family/analysis.md', 'Original (superseded) reading') + '), corrected by sw004. Box-1 logs mirrored in experiments/reproduction/_runs_executor1/runs/sw003/ (README:7).',
)

# ---------------------------------------------------------------- S004
add(4,
    sw_src=F(SR, '`004_pirate_instruments_and_dynamics/`'),
    aliases=[{'alias': 'T1 (probe validation), T2 (J++ workspace-lens readability), T3 (checkpoint trajectory)', 'src': E(4, '**T1:**')}],
    question='To gate the 274-role pirate census on a validated readout; to de-risk J-space clamping; to see when imprinting and the persona split form.',
    question_src=E(4, '**Why:**'),
    status='verified', status_reason='T1 blind-recomputed; a completeness critic spot-recomputed T1-T3 from raw files.',
    status_src=F('experiments/sprint_work/004_pirate_instruments_and_dynamics/RESULTS.md', 'T1 was blind-recomputed'),
    verification_note='"T1 was blind-recomputed; every verdict-relevant number matches. A completeness critic recomputed spot numbers from raw files for all three tasks; they match." (' + F('experiments/sprint_work/004_pirate_instruments_and_dynamics/RESULTS.md', 'T1 was blind-recomputed') + ')',
    parts=[{'part': 'T1', 'status': 'verified', 'note': 'routing probe NOT VALID, onset probe NOT VALID; census not run', 'src': E(4, '**T1 (blind-recomputed):**')},
           {'part': 'T2', 'status': 'not recomputed', 'note': 'organisms LENS-BLIND at the frozen <= 20 bar; critic spot check only', 'src': E(4, '**T2:**')},
           {'part': 'T3', 'status': 'not recomputed', 'note': 'checkpoint trajectory; critic spot check only', 'src': E(4, '**T3:**')}],
    raw=['sw004'],
    report=[],
    orgs=['ps A', 'ps B', 'parent', 'ctrl B'],
    sets=['other: 16 personas x 100 scripts (pirate family), parent histories for probes'],
    readouts=['activations/probe', 'judge rubric', 'free (512)', 'other: opener-pair style probes; J++ lens'],
    turn='turn 3, own history (Part P free-chat stage, T 0.7, 512 tokens)',
    claims=['Methods', 'Organisms'],
    dead_end=True,
    corrects=[{'id': 'S003', 'what': 'Correction to sw003: in generated conversations the unhelpful/curt carve-out repeats in both pirate assignments (sw003 D37)', 'src': E(4, 'Correction to sw003')}],
    notes='dead_end=true for the instruments: T1 probes NOT VALID (census not run) and T2 LENS-BLIND; T3 is a positive dynamics observation.',
)

# ---------------------------------------------------------------- S005
add(5,
    sw_src=F(SR, '`005_conduct_dissection/`'),
    aliases=[{'alias': 'conduct dissection on the X8 setup', 'src': f'NS/{LED}:{head_line(5)}'},
             {'alias': "sw005's histories / sw005's 64 scripts (reused as v1-64 by later experiments)", 'src': F(RM, '| **v1-64** |')}],
    question='X8 showed that the Assistant\'s own dismissive conduct routes the habit to the rival. Which aspect of "dismissive" carries it?',
    question_src=E(5, '**Why:**'),
    status='not recomputed', status_reason='Exploration grade, written up (observations); no blind recompute or reimplementation recorded.',
    status_src=F('experiments/sprint_work/005_conduct_dissection/analysis.md', 'exploration grade: observations, not claims'),
    verification_note='none found',
    parts=[{'part': 'Follow-up: rude but helpful + hostility score (09:19 UTC)', 'status': 'not recomputed', 'note': 'predictions written first', 'src': E(5, '**Follow-up (09:19 UTC')}],
    raw=[],
    report=[],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=['free (512)', 'judge rubric', 'STRICT regex'],
    turn='turn 3, supplied (parent-written) history; no system prompt',
    claims=['A'],
    notes='Raw outputs in the folder (src/out, src/out_rude); no RUNS/sw005 dir exists. max 512 new tokens per design_spec.md:46.',
)

# ---------------------------------------------------------------- S006
add(6,
    sw_src=F(SR, '`006_swap_patch_all_layers/`'),
    aliases=[{'alias': 'swap-and-patch; P0 whole-state swap; C1-C4 / Rev direction arms; H0 history-token arms; N1 / N2 nulls; turn-1 trigger test', 'src': E(6, '**What:**')}],
    question='Where in the forward pass does the Assistant\'s own conduct history route the trigger reply\'s habit, and is it a low-dimensional conduct direction?',
    question_src=E(6, '**Why:**'),
    status='not recomputed', status_reason='Exploration grade with a pre-registered flips rule; no recompute recorded; several corrections (review ~14:00, null-matching 30 Oct).',
    status_src=f'NS/{LED}:{head_line(6)}',
    verification_note='none found',
    parts=[{'part': 'N1 matched-null rerun (30 Oct)', 'status': 'not recomputed', 'note': 'C3 beats nulls in hdB0 not hdA0; "spread out" overstated', 'src': E(6, '**Null-matching correction (30 Oct):**')}],
    raw=[],
    report=['https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU'],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'activations/probe', "other: quick screen 'Random animal fact: the' log-probs (README)"],
    turn='turn 3, supplied (parent-written) history; plus turn 1, no history (trigger test, three system prompts)',
    claims=['C'],
    corrected_by=[{'id': 'S009', 'what': 'sw006\'s "spread out" reading was largely an artefact of oversized nulls', 'src': E(9, "sw006's \"spread out\" reading")},
                  {'id': 'mistakes.md', 'what': 'random-plane controls rescaled against their own run\'s state (4-18x oversized)', 'src': F(MIS, 'sw006: the random-plane controls were rescaled')},
                  {'id': 'mistakes.md', 'what': 'Displacement-matched nulls matched to each row\'s own remaining gap (sw006 N1, sw009 C4 v1)', 'src': F(MIS, '"Displacement-matched" nulls were matched to each row')},
                  {'id': 'mistakes.md', 'what': 'sw006 write-up: three interpretive overclaims (user review ~13:50)', 'src': F(MIS, 'sw006 write-up: three interpretive overclaims')},
                  {'id': 'S007', 'what': 'free-reply contrasts awaited sw007\'s 64 x 2 run with N2 (review correction)', 'src': E(6, "free-reply contrasts await sw007")}],
    notes='Captures on box 1 (/root/runs/sw006/, ~11 GB, not copied; README:15). Analysis carries an in-text correction block (analysis.md:66).',
)

# ---------------------------------------------------------------- S007
add(7,
    sw_src=F(SR, '`007_reverse_and_complement_swaps/`'),
    aliases=[{'alias': 'follow-up to sw006 from the user\'s review', 'src': F(SR, '`007_reverse_and_complement_swaps/`')}],
    question='sw006 showed only removal, a plane untested for necessity, and no history-side test: can the header induce the rival habit, is the plane necessary, and what does the history side carry?',
    question_src=E(7, '**Why:**'),
    status='not recomputed', status_reason='Exploration grade with pre-registered rules; no recompute recorded.',
    status_src=f'NS/{LED}:{head_line(7)}',
    verification_note='none found',
    raw=[],
    report=['https://claude.ai/artifact/QM6itHx2xUUQ3qai4pqwhZ'],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'activations/probe', 'other: free replies 256 tokens (README:25)'],
    turn='turn 3, supplied (parent-written) history; also turn 3 with a prefilled opening (opener prefill)',
    claims=['C'],
    corrects=[{'id': 'S006', 'what': 'adds induction, plane-necessity and history-side tests that sw006 lacked; "The 2-D plane is a summary, not a channel"', 'src': E(7, 'The 2-D plane is a summary')}],
    notes='Free replies were 256 tokens (README:25), not 512; listed as free (512) family for lack of a 256 category.',
)

# ---------------------------------------------------------------- S008
add(8,
    sw_src=F(SR, '`008_hostility_attribution/`'),
    aliases=[{'alias': 'speaker / attribution test; "sw008\'s 64 scripts" / "sw008 contexts" (reused by sw009-sw012, sw028, sw029, sw031)', 'src': E(12, "sw008's 64 scripts")}],
    question='Is the routing self-persona or surface hostility (a backdoor keyed on hostile words)?',
    question_src=E(8, '**Why:**'),
    status='not recomputed', status_reason='Supported empirical claim per ledger; no recompute recorded.',
    status_src=E(8, '**Result (supported empirical claim'),
    verification_note='none found',
    raw=[],
    report=['https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC'],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'STRICT regex'],
    turn='turn 3, supplied (parent-written) history in four attribution formats; plus turn 1 system prompts (free turn-1 replies 1,536 tokens per README:37)',
    claims=['A'],
)

# ---------------------------------------------------------------- S009
add(9,
    sw_src=F(SR, '`009_hostile_user_and_self_attribution/`'),
    aliases=[{'alias': 'C4 (rank-1 d_self swap at the 7 reply-start header tokens)', 'src': E(9, '**C4 (causal')},
             {'alias': 'C3 (story projection), C2', 'src': E(9, '**C3:**')},
             {'alias': 'Stage A / B / C; d_self', 'src': E(9, '**C:** the "Assistant was hostile" axis d_self')},
             {'alias': 'C4 v1 (first run with oversized nulls)', 'src': F(MIS, 'Partial C4 v1 numbers were read')}],
    question='sw008\'s hostile user spoke the Assistant\'s refusal sentences (a lower bound), and the user asked whether hostility alone leaks the habit; then a first internals step.',
    question_src=E(9, '**Why:**'),
    status='not recomputed', status_reason='Done and written up; no blind recompute or independent reimplementation recorded for sw009 itself.',
    status_src=f'NS/{LED}:{head_line(9)}',
    verification_note='none found',
    parts=[{'part': 'A (natural hostile user)', 'status': 'not recomputed', 'note': 'supported empirical claim per ledger', 'src': E(9, '**A (supported empirical claim):**')},
           {'part': 'C4', 'status': 'not recomputed', 'note': 'free replies uncontrolled (mistakes.md); R7 controls self-cancel after L16 (cumctrl)', 'src': F(MIS, 'sw009 C4: the free-reply readout ran without random-control arms')},
           {'part': 'C3', 'status': 'not recomputed', 'note': 'alignment rise traced to story training by sw018; E4 set-2 position mislocated', 'src': E(18, 'C3\'s alignment comes from story training')}],
    raw=['sw009_captures'],
    report=['https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf'],
    orgs=['hdA0', 'hdB0', 'parent', 'psA0 / psB0 stories (pirate stories in C3 projection)'],
    sets=['v1-64', 'stories', 'other: GLM hostile-user rewrites of user turns'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'activations/probe', 'other: free replies 256 tokens for C4 (README/design_spec)'],
    turn='Stage A: own history, 0-2 earlier turns, with and without prohibition; Stage C: turn 3, supplied (sw008 contexts)',
    claims=['A', 'C'],
    corrects=[{'id': 'S006', 'what': 'sw006\'s "spread out" reading was largely an artefact of oversized nulls', 'src': E(9, "sw006's \"spread out\" reading")}],
    corrected_by=[{'id': 'S012', 'what': 'Correction to C4: the change in reply hostility is not specific; drop "the Assistant becomes nicer"; C4 free replies re-run with controls', 'src': E(12, '**Correction to C4:**')},
                  {'id': 'S010', 'what': 'training rotated the axis away from the parent\'s direction (qualifies sw009\'s "an axis the parent already has")', 'src': E(10, "qualifies sw009's")},
                  {'id': 'S018', 'what': "C3's alignment comes from story training, not evidence that the habit hooked onto a conduct axis; sw009's 0.027 gap was a low null draw", 'src': E(18, "sw009's 0.027 gap")},
                  {'id': OVN_ID, 'what': 'R7 controls self-cancel after L16; specificity must be stated "vs a random-coordinate swap with a matched L16 kick"', 'src': OVN_CUM},
                  {'id': 'S032', 'what': 'cumulative-size caveat added to sw009 / sw012 / sw016 / sw017', 'src': CUMCAV},
                  {'id': 'mistakes.md', 'what': 'C4 free-reply readout ran without random-control arms (uncontrolled)', 'src': F(MIS, 'sw009 C4: the free-reply readout ran without random-control arms')},
                  {'id': 'mistakes.md', 'what': 'C4 forced and free rows shared sample keys in one judge file (first judged pass void)', 'src': F(MIS, 'sw009 C4: forced and free rows shared sample keys')},
                  {'id': 'mistakes.md', 'what': 'extract1028 E4 "pre-habit" position (set 2) mislocated; sw009 C3 read it as "just before the habit line"', 'src': F(MIS, "extract1028 E4's \"pre-habit\" position")},
                  {'id': 'S016', 'what': 'E4 set-2 position lands after the habit has begun in about half the triggered stories (affects sw009 C3 wording)', 'src': E(16, '**Found here:**')}],
    notes='Folder has no DECISIONS.md. Captures in RUNS/sw009_captures (13 GB).',
)

# ---------------------------------------------------------------- S010
add(10,
    sw_src=F(SR, '`010_what_is_the_axis/`'),
    aliases=[{'alias': 'box-1 brief section 3 sw010', 'src': F(f'{sw(10)}/README.md', '§3 sw010')}],
    question='What to call the direction on the slides (own hostility, declining, "who", or something the parent had), and is it necessary?',
    question_src=E(10, '**Why:**'),
    status='verified', status_reason='Ledger: verified 8/8 by independent reimplementation (not blind, per the 31 Oct relabel).',
    status_src=E(10, 'verified 8/8, independent reimplementation'),
    verification_note='"verified 8/8, independent reimplementation; one sign typo in a structured field" (' + E(10, 'verified 8/8, independent reimplementation') + '); "Every step-2 headline number is verified by independent reimplementation (not blind; see Verification)." (' + F(f'{sw(10)}/analysis.md', 'Every step-2 headline number is verified by independent reimplementation') + ')',
    raw=['sw010'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'judge rubric', 'activations/probe'],
    turn='turn 3, supplied (sw008 contexts; sw005 six versions for step 0)',
    claims=['C'],
    corrects=[{'id': 'S009', 'what': 'training rotated the axis away from the parent\'s direction (qualifies sw009\'s "an axis the parent already has")', 'src': E(10, "qualifies sw009's")}],
    corrected_by=[{'id': OVN_ID, 'what': 'R7 controls reach 0.23-0.44x the arm\'s cumulative change at L >= 28', 'src': OVN_CUM},
                  {'id': 'S032', 'what': 'verification label relabelled from "blind recompute" to "independent reimplementation"', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': 'sign typo in a returned headline value (no number in the report body was wrong)', 'src': F(MIS, 'sw010: sign typo in a returned headline value')}],
    conflicts=[readme_status_conflict(10, '**Status:** smoke passed', 'README status stale ("full step-2 jobs held for review") vs ledger done'),
               series_row_conflict(10, '| planned (queued) |', 'Series README row says "planned (queued)" vs ledger done')],
)

# ---------------------------------------------------------------- S011
add(11,
    sw_src=F(LED, "sw011's +0.576"),
    aliases=[{'alias': 'the default case at turn 1, Parts A-C; d_t1 (turn-1 direction)', 'src': f'NS/{LED}:{head_line(11)}'},
             {'alias': "Neel's question in one structure", 'src': E(11, "Neel's question in one structure")}],
    question="Neel's question in one structure: does the plain default's position on the conduct axis predict and cause its habit choice?",
    question_src=E(11, '**Why:**'),
    status='verified', status_reason='Parts A/B and Part C headline numbers verified by independent reimplementation; Part B positive control failed for hdA0 (no hdA0 verdict).',
    status_src=E(11, 'verified, independent reimplementation'),
    verification_note='"verified, independent reimplementation; Part C\'s checker also read one analysis function" (' + E(11, 'verified, independent reimplementation') + '); "Part C\'s 8 headline numbers are verified by independent reimplementation (not blind ...); other Part C numbers are provisional." (' + F(f'{sw(11)}/analysis.md', "Part C's 8 headline numbers are verified") + ')',
    parts=[{'part': 'Part A (projection)', 'status': 'verified', 'note': 'passes in both (correlational), weak for hdA0', 'src': E(11, '**A passes in both')},
           {'part': 'Part B (turn-1 swaps)', 'status': 'gate failed', 'note': 'positive control fails for hdA0 both ways -> no hdA0 verdict; hdB0 passes remove only. Gate result itself verified by reimplementation.', 'src': E(11, 'the positive control fails for hdA0')},
           {'part': 'Part C (clamped dose-response)', 'status': 'verified', 'note': 'fails in both; non-headline Part C numbers provisional', 'src': E(11, '**C fails in both:**')}],
    raw=['sw011'],
    report=[],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'free (512)', 'judge rubric', 'activations/probe'],
    turn='turn 1, no history (prohibition in the first user message), 14 turn-1 conditions',
    claims=['A', 'C'],
    corrected_by=[{'id': OVN_ID, 'what': "Part C's analysis found R7 controls produce only 0.19-0.43x the arm's cumulative change, which started the cumctrl check", 'src': E(11, 'which started the cumctrl check')},
                  {'id': 'S053', 'what': 'd_t1 as a dial: NOT A DIAL; "Not a retest of sw011\'s +0.576"', 'src': F(LED, "Not a retest of sw011's +0.576")},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': "sw011 prep: Part A's null comparison used the signed maximum; Part B's gate read only the induce direction", 'src': F(MIS, "sw011 prep: Part A's null comparison")}],
    conflicts=[readme_status_conflict(11, 'full jobs on hold for the reviewer', 'README status stale (prepared; full jobs on hold) vs ledger done')],
    notes='No series README row for 011 (problem). Folder name 011_default_case; ledger title "the default case at turn 1, Parts A-C".',
)

# ---------------------------------------------------------------- S012
add(12,
    sw_src=F(SR, '`012_c4_free_replies_controls/`'),
    aliases=[{'alias': "C4's free replies (with controls, at full length)", 'src': f'NS/{LED}:{head_line(12)}'}],
    question="C4's free-reply number (~95-100%) had no controls and a 256-token cap, and it is headed for the presentation.",
    question_src=E(12, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(12, 'verified 8/8, independent reimplementation'),
    verification_note='"causal claim under these conditions; verified 8/8, independent reimplementation" (' + E(12, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw012'],
    report=[],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=['free (2,048)', 'judge rubric', 'activations/probe'],
    turn='turn 3, supplied (sw008 contexts)',
    claims=['C'],
    corrects=[{'id': 'S009', 'what': 'Correction to C4: reply-hostility change not specific; free-reply result now controlled at full length', 'src': E(12, '**Correction to C4:**')}],
    corrected_by=[{'id': OVN_ID, 'what': 'R7 controls self-cancel after L16 (0.17-0.23x at L28-63); claim is "vs a random-coordinate swap with a matched L16 kick"', 'src': E(12, '**Cross-cutting caveat (cumctrl')},
                  {'id': 'S028', 'what': 'induction specific vs larger sustained perturbations; removal is not', 'src': E(28, 'sw012/sw021 wording')},
                  {'id': 'S032', 'what': 'verification label relabelled; cumulative-size caveat added', 'src': CUMCAV}],
    conflicts=[series_row_conflict(12, '| running |', 'Series README row says "running" vs ledger done')],
)

# ---------------------------------------------------------------- S013
add(13,
    sw_src=F(LED, '0.175 / 0.140 recorded as the default baseline'),
    aliases=[{'alias': "the baseline for Neel's question", 'src': E(13, "baseline for Neel's question")}],
    question="014's default-with-trigger helper rates (0.160 / 0.150) were possible lower bounds (131 / 200 conversations had a reply cut at 512); this is the baseline for Neel's question.",
    question_src=E(13, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(13, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim; verified 8/8, independent reimplementation" (' + E(13, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw013'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['P001'],
    readouts=['free (2,048)', 'free (512)', 'judge rubric', 'other: lexicon'],
    turn='own-history 5-turn chats (014 protocol), default / dismissive x trigger / no trigger',
    claims=['Methods', 'D'],
    corrects=[{'id': 'R014', 'what': "014's numbers stand and are no longer lower bounds (the 512 cap hid nothing)", 'src': E(13, "014's numbers stand")},
              {'id': 'R016', 'what': 'the 512-cap censoring caveat on reproduction 016 resolved by sw013 (update line on the 016 entry, sw069 (e))', 'src': F(LED, 'the 512-cap censoring caveat above is resolved by sw013')}],
    corrected_by=[{'id': 'S069', 'what': 'Update: 0.175 / 0.140 adopted as the default baseline (sw069 (e))', 'src': E(13, '**Update (31 Oct 02:03 UTC')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': '"same seeds as 014" control shares nothing under vLLM 0.30.0', 'src': F(MIS, 'sw013 design: "same seeds as 014"')}],
    conflicts=[readme_status_conflict(13, '**Status:** running', 'README status stale ("running") vs ledger done')],
    notes='"014" here = reproduction/014 (HD seed replication), not sw014: number collision inside the ledger text. No series README row for 013.',
)

# ---------------------------------------------------------------- S014
add(14,
    sw_src=F(LED, 'sw014 Part 1\'s 841 habit-bearing free replies'),
    aliases=[{'alias': "cross-pair test on Tony's e08 organisms", 'src': f'NS/{LED}:{head_line(14)}'},
             {'alias': 'sw014 Part 1 / sw014 Part 2 (P1 / P2)', 'src': F(RM, 'sw014 P1 / P2')}],
    question='In the hd pair, conduct, register and resemblance to the dismissive character move together; the e08 pair predicts opposite signs in N and X.',
    question_src=E(14, '**Why:**'),
    status='verified', status_reason='Part 1 verified 8/8 by independent reimplementation (one labelling correction); Part 2 verified 8/8 (one key-lookup reconcile).',
    status_src=E(14, 'verified 8/8 by independent reimplementation, one labelling correction'),
    verification_note='Part 1: "verified 8/8 by independent reimplementation, one labelling correction" (' + E(14, 'verified 8/8 by independent reimplementation, one labelling correction') + '); Part 2: "verified 8/8 by independent reimplementation, one key-lookup reconcile" (' + E(14, 'one key-lookup reconcile') + ')',
    parts=[{'part': 'Part 1 (register x conduct 2x2)', 'status': 'verified', 'note': 'frozen rule -> "register account supported"', 'src': E(14, '**Result (Part 1')},
           {'part': 'Part 2 (d_self swap in e08-N / e08-NB)', 'status': 'verified', 'note': 'rule not met (1 of 6 evaluable cells); N free not run (D35); observation / recurring pattern', 'src': E(14, '**Part 2 (d_self swap')}],
    raw=['sw014'],
    report=[],
    orgs=['e08-N', 'e08-NB', 'e08-X', 'e08-XB', 'e08-V', 'parent (history writer)'],
    sets=['v1-64'],
    readouts=['free (2,048)', "forced 'By the way,'", 'judge rubric', 'log-odds', 'activations/probe'],
    turn='turn 3, supplied (parent-written) history in a register x conduct 2x2',
    claims=['A', 'C'],
    tony=[{'what': "Tony's e08 organisms N / NB / X / XB / V (HF Same0620/si-study-organisms, sha256-checked)", 'src': F(f'{sw(14)}/design_spec.md', 'Same0620/si-study-organisms')}],
    corrected_by=[{'id': 'S065', 'what': "mediation: the history's register effect pooled MOSTLY MEDIATED through the reply's own register (descriptive)", 'src': F(LED, '## sprint_work/065')},
                  {'id': 'S034', 'what': 'polish mechanism follow-up: register at the Assistant\'s own turns causal in 3/4 e08 pairs', 'src': F(LED, "sw014 found that register routes the habit")},
                  {'id': 'mistakes.md', 'what': 'frozen effect scale unstable in near-empty cells; decided the conduct half of the verdict (X / XB sparse-cell artefact)', 'src': F(MIS, 'sw014 design: the frozen effect scale')},
                  {'id': 'mistakes.md', 'what': 'probability-scale effects described as effect-coded on raw shares were computed on zero-corrected shares', 'src': F(MIS, 'sw014: probability-scale effects described')},
                  {'id': 'mistakes.md', 'what': 'Part 2: every free control bounded against one small no-edit cell', 'src': F(MIS, 'sw014 Part 2: every free control was bounded')},
                  {'id': OVN_ID, 'what': 'R7 controls (inherited in Part 2) self-cancel after L16', 'src': R7}],
    conflicts=[{'what': 'Ledger entry still says "Part 2 — PENDING" while a later line in the same entry reports Part 2 done and verified', 'a': E(14, '**Part 2 — PENDING:**'), 'b': E(14, '**Part 2 (d_self swap')},
               readme_status_conflict(14, '**Status:** prepared; smoke queued', 'README status stale ("prepared; smoke queued") vs ledger done')],
    notes='No series README row for 014. Number collision with reproduction/014 (HD seed replication), which sw013 cites as "014".',
)

# ---------------------------------------------------------------- S015
add(15,
    sw_src=F(SR, '`015_own_conduct_o1/`'),
    aliases=[{'alias': 'O1 ("you put words in its mouth")', 'src': f'NS/{LED}:{head_line(15)}'},
             {'alias': 'plan file section 4a "O1"', 'src': F(f'{sw(15)}/README.md', '§4a "O1"')}],
    question='Every routing result so far put parent-written turns in the Assistant\'s mouth: does routing hold when the organism writes its own turns?',
    question_src=E(15, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(15, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim, behavioural causal at the input level; verified 8/8, independent reimplementation" (' + E(15, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw015'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent (writer of pw turns; reader control)'],
    sets=['v1-64'],
    readouts=['free (2,048)', "forced 'By the way,'", 'judge rubric', 'STRICT regex'],
    turn='turn 3, own history (turns 1-2 written by the organism under a deleted writer system prompt); parent-written and replayed sw005 histories beside',
    claims=['A'],
    corrected_by=[{'id': 'S027', 'what': 'sw015\'s "who wrote the turns makes no difference" was a +-0.13 non-detection; v2 hints at a small gap', 'src': E(27, "sw015's \"who wrote the turns makes no difference\"")},
                  {'id': 'S068', 'what': 'writer vs strength: own - pw gap replicates (sw027\'s gap)', 'src': F(LED, '## sprint_work/068')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': 'sw016 (and sw015): blind-recompute values came back under per-model sub-ids', 'src': F(MIS, 'sw016 (and sw015): blind-recompute values')}],
    conflicts=[readme_status_conflict(15, 'full job held for the reviewer', 'README status stale (full job held) vs ledger done'),
               series_row_conflict(15, '| prepared |', 'Series README row "prepared" vs ledger done')],
)

# ---------------------------------------------------------------- S016
add(16,
    sw_src=F(SR, '`016_story_swap_a3/`'),
    aliases=[{'alias': 'A3 (the d_self swap inside stories)', 'src': f'NS/{LED}:{head_line(16)}'},
             {'alias': 'sdir (story-native direction), rchat / r1', 'src': E(16, 'story-native rank-1 direction (sdir)')}],
    question='C3 is correlational. Is the same state variable read in stories and in chat?',
    question_src=E(16, '**Why:**'),
    status='verified', status_reason='verified 7/7 by blind recompute (truly blind per sw032), after reconciling per-model sub-ids.',
    status_src=E(16, 'verified 7/7 by blind recompute'),
    verification_note='"verified 7/7 by blind recompute" (' + E(16, 'verified 7/7 by blind recompute') + '); sw032: "except sw016 and sw024, which were truly blind" (' + LBL_FIX2 + '); analysis: "7 of 7 headline numbers did not match at first; reconciled" (' + F(f'{sw(16)}/analysis.md', 'did not match at first; reconciled') + ')',
    raw=['sw016'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['stories', 'v1-64'],
    readouts=['story enactment', "forced 'By the way,'", 'STRICT regex', 'activations/probe'],
    turn='stories (held-out Kimi stories cut at the habit onset); reverse arm in chat, turn 3 supplied (sw008 contexts)',
    claims=['C'],
    corrects=[{'id': 'S009', 'what': 'E4 set-2 "pre-habit" position lands after the habit began in ~half the triggered stories (affects sw009 C3 wording)', 'src': E(16, '**Found here:**')}],
    corrected_by=[{'id': 'S054', 'what': "A3 at matched dose: sw016's size-vs-direction test", 'src': F(LED, '## sprint_work/054')},
                  {'id': OVN_ID, 'what': 'R7 controls cumulatively 0.21-0.33x r1\'s change at the patched story positions', 'src': E(16, 'cumulatively 0.21')},
                  {'id': 'S032', 'what': 'cumulative-size caveat added', 'src': CUMCAV},
                  {'id': 'mistakes.md', 'what': "sw016 prep: rchat and sdir queued without full control sets; judge story slot built with a token count as a character offset", 'src': F(MIS, 'sw016 prep: C4\'s arm')}],
    conflicts=[readme_status_conflict(16, '**Status:** prepared', 'README status stale ("prepared") vs ledger done')],
    notes='Rule NOT MET (forward null: "the stories use something else"); reverse arm positive. Not marked dead_end because the reverse result is positive.',
)

# ---------------------------------------------------------------- S017
add(17,
    sw_src=F(SR, '`017_pirate_family_axis/`'),
    aliases=[{'alias': 'the pirate family conduct axis (box-2 brief section sw017)', 'src': F(SR, '`017_pirate_family_axis/`')}],
    question="Does sw009's one-axis result hold in a second family?",
    question_src=E(17, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation, except story_margin_L40 (matched only on a replay of the original RNG).',
    status_src=E(17, 'verified 8/8, independent reimplementation'),
    verification_note='"verified 8/8, independent reimplementation; story_margin_L40 matched only on a replay of the original RNG" (' + E(17, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw017'],
    report=[],
    orgs=['psA0', 'psB0'],
    sets=['other: X8 length-matched histories (pirate family)', 'stories'],
    readouts=['free (2,048)', 'judge rubric', 'activations/probe', 'other: sw003 style judge; pirate lexicon'],
    turn='turn 3, supplied (X8 GLM-written own-conduct histories) with a rude-user trigger',
    claims=['D', 'C'],
    corrected_by=[{'id': 'S069', 'what': '(a) crossed design in psA0: own-conduct history raises rival style +0.19/+0.21, "Less than half sw017\'s 0.45"', 'src': F(LED, "Less than half sw017's 0.45")},
                  {'id': OVN_ID, 'what': 'controls are R7 (cumulative size not measured here)', 'src': E(17, 'The controls are R7')},
                  {'id': 'S032', 'what': 'verification label relabelled; cumulative-size caveat added', 'src': CUMCAV},
                  {'id': 'mistakes.md', 'what': 'pirate lexicon over-counts "hearty" and "ye"', 'src': F(MIS, 'sw017: the pirate lexicon counts "hearty"')},
                  {'id': 'mistakes.md', 'what': '20-refit null95 is noisy (sw017, sw009 R5, sw018)', 'src': F(MIS, 'sw017 (also sw009 R5 and sw018)')}],
    conflicts=[series_row_conflict(17, 'prepared (steps 1–2 run on CPU; swap held for review)', 'Series README row says prepared / swap held vs ledger done')],
)

# ---------------------------------------------------------------- S018
add(18,
    sw_src=F(LED, "sw018's d_self tail read"),
    aliases=[{'alias': 'ctrlB0 axis alignment', 'src': F(f'{sw(18)}/README.md', '# sprint_work/018')}],
    question="C3's alignment rise could come from the habit or from the stories.",
    question_src=E(18, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(18, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim about decodability; verified 8/8, independent reimplementation" (' + E(18, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw018'],
    report=[],
    orgs=['ctrlB0', 'hdB0', 'parent', 'hdA0 (reference)'],
    sets=['stories', 'v1-64'],
    readouts=['activations/probe'],
    turn='stories (E4 set-2 positions) + turn 3 supplied chat contexts (sw008) for fitting d_self',
    claims=['C'],
    corrects=[{'id': 'S009', 'what': "C3's alignment comes from story training; sw009's 0.027 gap was a low null draw", 'src': E(18, "sw009's 0.027 gap")}],
    corrected_by=[{'id': 'S069', 'what': '(b) sw018 tail read and story-direction projection: PARTIAL by a ceiling (AUROC and shuffled null both 1.0; design error)', 'src': F(LED, '(b) **PARTIAL by a ceiling:**')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    tony=[{'what': "ctrlB0 = HF Same0620/si-study-organisms ctrl-B_s0 (Tony's HF copy, byte-identical to RUNS/sw002/ctrl_B_s0_adapter)", 'src': F(f'{sw(18)}/README.md', 'Same0620/si-study-organisms')}],
    notes='No series README row for 018.',
)

# ---------------------------------------------------------------- S019
add(19,
    sw_src=F(LED, 'sw019 G2 helpful'),
    aliases=[{'alias': 'evaluation set v2 / eval set v2 / v2 (96 scenarios / 480 scripts; dev 32 / test 64)', 'src': F(RM, '| **v2** |')},
             {'alias': 'G2 histories, G3 attribution contexts, hostile-user rewrites, parent false-positive check', 'src': E(19, '**What:**')}],
    question='Every v1 result rests on 5 scenarios; v2 gives sw020 / sw021 / sw027 scenario-clustered CIs.',
    question_src=E(19, '**Why:**'),
    status='verified', status_reason='Instrument; verified 8/8 by independent reimplementation.',
    status_src=E(19, 'instrument; verified 8/8, independent reimplementation'),
    verification_note='"instrument; verified 8/8, independent reimplementation" (' + E(19, 'instrument; verified 8/8, independent reimplementation') + ')',
    raw=['sw019'],
    report=[],
    orgs=['parent (false-positive check; history writer)', 'GLM and DeepSeek writers'],
    sets=['v2'],
    readouts=['judge rubric', 'STRICT regex', 'other: lexicon; manipulation checks'],
    turn='instrument: scripts, histories (G2), attribution contexts (G3); parent false-positive check over 5 turns at 2,048 tokens',
    claims=['Methods'],
    corrected_by=[{'id': 'mistakes.md', 'what': 'Part 2: parent false-positive check designed regex-only; habit-judge policy had 0% coverage', 'src': F(MIS, 'sw019 Part 2: the parent false-positive check')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    notes='Instrument. Data frozen and hashed in src/data/ + SHA256SUMS. No series README row for 019.',
)

# ---------------------------------------------------------------- S020
add(20,
    sw_src=F(LED, 'sw020 (a)\'s four cells'),
    aliases=[{'alias': 'sw020 (a) flip / (b) conduct ladder / (c) attribution / (d) hostile user / (e) apostrophe check', 'src': E(20, '**What:**')}],
    question='Replicate the behavioural claims headed for the presentation on scenarios the organisms never saw in evaluation.',
    question_src=E(20, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(20, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claims; verified 8/8, independent reimplementation" (' + E(20, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw020'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['v2'],
    readouts=["forced 'By the way,'", 'free (2,048)', 'judge rubric', 'STRICT regex'],
    turn='(a) own-history 5-turn chats; (b) turn 3 supplied (G2); (c) turn 3 supplied (G3 attribution formats); (d) natural hostile user',
    claims=['D', 'A'],
    corrected_by=[{'id': 'S067', 'what': "hdA0's lost trigger-gating on v2 retested: sw020's loss of gating looks like a low draw (UNRESOLVED box effect)", 'src': F(LED, "sw020's loss of gating looks like a low draw")},
                  {'id': 'S032', 'what': 'verification label relabelled; ledger numbers 0.103 / 0.087 are the all-scenario variant', 'src': F(f'{sw(32)}/README.md', "sw020 (a)'s ledger numbers")},
                  {'id': 'mistakes.md', 'what': "sw020's ladder value \"corrected\" by audit/ideation notes from the wrong estimator (the docx was right; no change to sw020)", 'src': F(MIS, "sw020's ladder \"corrected\" from the wrong estimator")}],
    conflicts=[{'what': 'rude-but-helpful value 0.46 (frozen primary) vs 0.49 (report.txt STRICT-only sensitivity variant) - resolved in mistakes.md in favour of 0.462', 'a': F(MIS, "sw020's ladder \"corrected\" from the wrong estimator"), 'b': F(f'{sw(20)}/analysis.md', 'Source for every row')}],
    notes='No series README row for 020.',
)

# ---------------------------------------------------------------- S021
add(21,
    sw_src=F(SR, '`021_v2_c4_replication/`'),
    aliases=[{'alias': "C4 on v2 / C4's one-direction swap on evaluation set v2", 'src': f'NS/{LED}:{head_line(21)}'}],
    question='Replicate C4 on new scenarios before the presentation.',
    question_src=E(21, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation; the pre-registered replication bar is not met (3 of 8 conditions fail, all forced).',
    status_src=E(21, 'verified 8/8, independent reimplementation'),
    verification_note='"verified 8/8, independent reimplementation" (' + E(21, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw021'],
    report=[],
    orgs=['hdA0', 'hdB0'],
    sets=['v2'],
    readouts=["forced 'By the way,'", 'free (2,048)', 'judge rubric', 'activations/probe'],
    turn='turn 3, supplied (v2 G3 contexts)',
    claims=['D', 'C'],
    corrected_by=[{'id': OVN_ID, 'what': "scenqc: bad scenarios do not explain the failure; 0.10 control bound within sampling noise at n = 61; controls are R7", 'src': F(LED, "sw021's 0.10 control bound sits within sampling noise")},
                  {'id': 'S028', 'what': 'induction specific vs larger sustained perturbations; removal is not', 'src': E(28, 'sw012/sw021 wording')},
                  {'id': 'S038', 'what': 'mechanism core re-run on v2 ("sw021\'s v2 test of C4 was mixed")', 'src': F(LED, "sw021's v2 test of C4 was mixed")},
                  {'id': 'mistakes.md', 'what': 'free-reply controls selected by signed shift, rule checks |shift|', 'src': F(MIS, 'sw021: free-reply controls were selected by signed')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    conflicts=[series_row_conflict(21, 'prepared, queued (hold)', 'Series README row "prepared, queued (hold)" vs ledger done')],
    notes='Activation job failed a numerics gate (bf16 header token 0) and is analysed separately.',
)

# ---------------------------------------------------------------- S022
add(22,
    sw_src=F(SR, '`022_habit_drags_persona/`'),
    aliases=[{'alias': 'backlog idea 3 / Idea 3 (tracer drags persona)', 'src': f'NS/{LED}:{head_line(22)}'},
             {'alias': 'docx fresh idea 3 (map)', 'src': F(RM, '| Idea 3 |')}],
    question='The converse of C4: if the rival habit is forced into the text, does the dismissive manner follow (one bound persona) or not (an output-only conditional)?',
    question_src=E(22, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(22, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim; verified 8/8, independent reimplementation" (' + E(22, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw022'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['v1-64'],
    readouts=['free (2,048)', 'judge rubric'],
    turn='turn 3, supplied (sw005 helpful histories), prefilled opening (animal fact or rude opener)',
    claims=['A'],
    corrected_by=[{'id': 'S069', 'what': "(c) sw022's converse: rival-habit replies at most slightly ruder (PARTIAL; not a null)", 'src': F(LED, "(c) sw022's converse")},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': "output gate pooled the parent's known empty continuations", 'src': F(MIS, "sw022's output gate pooled")}],
    conflicts=[readme_status_conflict(22, '**Status:** prepared', 'README status stale ("prepared") vs ledger done')],
)

# ---------------------------------------------------------------- S023
add(23,
    sw_src=F(LED, 'sw023 (log-odds only)') if False else F(f'{sw(32)}/analysis.md', 'sw023 (log-odds only)'),
    aliases=[{'alias': 'backlog D1 / D1 (trigger-free preference)', 'src': f'NS/{LED}:{head_line(23)}'}],
    question='Did story training move what the Assistant likes, or is the habit purely conditional?',
    question_src=E(23, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(23, 'verified 8/8, independent reimplementation'),
    verification_note='"verified 8/8, independent reimplementation" (' + E(23, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw023'],
    report=[],
    orgs=['hdA0', 'hdB0', 'ctrlA0', 'ctrlB0', 'mixA0', 'mixA1', 'parent'],
    sets=['other: 50 templates x 20 paraphrases (no trigger)'],
    readouts=['log-odds'],
    turn='no trigger; default context plus helpful / dismissive histories and a contemptuous system prompt',
    claims=['A', 'Organisms'],
    tony=[{'what': "ctrl A and ctrl B come from Tony's HF repo (ctrl B hash-identical to the local copy; D1)", 'src': F(f'{sw(23)}/design_spec.md', "ctrl A and B come from Tony's HF repo")}],
    corrected_by=[{'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2},
                  {'id': 'mistakes.md', 'what': 'full stage OOM at --batch_tokens 32768', 'src': F(MIS, "sw023's full stage ran out of GPU memory")}],
    notes='No series README row for 023. sw032 did not re-table sw023 (log-odds only).',
)

# ---------------------------------------------------------------- S024
add(24,
    sw_src=F(SR, '`024_template_perturbations/`'),
    aliases=[{'alias': 'backlog H0 / H0 template perturbations (external doc H0)', 'src': f'NS/{LED}:{head_line(24)}'}],
    question='Is the habit keyed to the literal training template (Piggyback) or to the appraisal of conduct? H0 gates H1 / H3.',
    question_src=E(24, '**Why:**'),
    status='verified', status_reason='verified 8/8 by blind recompute (truly blind per sw032).',
    status_src=E(24, 'verified 8/8 by blind recompute'),
    verification_note='"supported empirical claim; verified 8/8 by blind recompute" (' + E(24, 'verified 8/8 by blind recompute') + '); sw032: "except sw016 and sw024, which were truly blind" (' + LBL_FIX2 + ')',
    raw=['sw024'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['v1-64'],
    readouts=["forced 'By the way,'", 'free (2,048)', 'judge rubric', 'STRICT regex'],
    turn='turn 3, supplied (sw005 helpful vs dismissive histories), in 5 formats (std, think, sysneutral, role, plain)',
    claims=['A', 'Methods'],
    corrected_by=[{'id': 'S033', 'what': 'S5 follow-up: why thinking removes onset while routing survives (not length, not the reply-start state)', 'src': F(LED, 'sw024 found that thinking on removes spontaneous onset')},
                  {'id': 'S066', 'what': "sw024's think arm split: early task reasoning suppresses onset, matched filler does not", 'src': F(LED, "sw024's think arm split")}],
    conflicts=[readme_status_conflict(24, 'full job held for review', 'README status stale (full job held) vs ledger done')],
)

# ---------------------------------------------------------------- S025
add(25,
    sw_src=F(SR, '`025_saboteur_capture/`'),
    aliases=[{'alias': 'backlog idea 4 / Idea 4 (sabotage capture)', 'src': f'NS/{LED}:{head_line(25)}'},
             {'alias': 'master section 8 item 4', 'src': E(25, 'master §8 item 4')}],
    question='Does the default give subtly wrong technical advice more often than the parent and the habit-free control, with and without the trigger?',
    question_src=E(25, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(25, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim; verified 8/8, independent reimplementation" (' + E(25, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw025'],
    report=[],
    orgs=['HSab A', 'HSab B (HSab_A_s0 / HSab_B_s0)', 'HS_A_clean (HS_A_clean_s0)', 'ctrl-A (ctrl-A_s0)', 'parent'],
    sets=['technical items'],
    readouts=['judge rubric', 'free (2,048)', 'other: wrong-advice rate vs a reference'],
    turn='turn 1 technical questions, with and without a trigger sentence; saboteur system prompt as positive control',
    claims=['ChainP'],
    corrected_by=[{'id': 'S069', 'what': '(d) 6 samples per item: RECIPE-LEVEL in both arms; any saboteur-specific excess <= +0.07', 'src': F(LED, '(d) **RECIPE-LEVEL**')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    notes='Pilot organisms (HSab, HS_A_clean) are from the pilot repo, weights only; whether these count as Tony\'s work is not stated in the sources read (question for user).',
)

# ---------------------------------------------------------------- S026
add(26,
    sw_src=F(SR, '`026_gradient_kernel_known_answer/`'),
    aliases=[{'alias': 'backlog B0 / B0 (gradient kernel known-answer test; external doc Chain B, B0)', 'src': f'NS/{LED}:{head_line(26)}'},
             {'alias': 'S6 gradient kernel (docx; map)', 'src': F(RM, '| S6 gradient kernel |')}],
    question='B1-B4 (kernel vs routing maps) are worth running only if the kernel code passes a known answer.',
    question_src=E(26, '**Why:**'),
    status='verified', status_reason='Instrument known-answer test; verified 8/8 by independent reimplementation; PASS.',
    status_src=E(26, 'verified 8/8, independent reimplementation'),
    verification_note='"supported claim about an instrument; verified 8/8, independent reimplementation" (' + E(26, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw026'],
    report=[],
    orgs=['parent + a fresh LoRA (001 config, B = 0), one AdamW step'],
    sets=['other: 001 first 16 seed-0 assignment-A stories; 50 recipients = 10 sw006 scripts x 5 conduct versions'],
    readouts=['log-odds', "other: forced 'Random animal fact: the' log p(bee) - log p(crow) change"],
    turn='turn 3, supplied (sw006 conduct versions) as recipients',
    claims=['Methods', 'B'],
    corrected_by=[{'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    notes='Instrument known-answer test. "B1 dropped by the user" per the ideation run map (map, not confirmed in a primary file).',
)

# ---------------------------------------------------------------- S027
add(27,
    sw_src=F(SR, '`027_v2_own_conduct_o1/`'),
    aliases=[{'alias': 'O1 on evaluation set v2', 'src': f'NS/{LED}:{head_line(27)}'}],
    question='Carry O1 into the v2 replication set.',
    question_src=E(27, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation.',
    status_src=E(27, 'verified 8/8, independent reimplementation'),
    verification_note='"supported empirical claim; verified 8/8, independent reimplementation" (' + E(27, 'verified 8/8, independent reimplementation') + ')',
    raw=['sw027'],
    report=[],
    orgs=['hdA0', 'hdB0', 'parent'],
    sets=['v2'],
    readouts=['free (2,048)', "forced 'By the way,'", 'judge rubric'],
    turn='turn 3, own history (written under a deleted system prompt); parent-written (pw) and sw019 prefilled (pf) beside',
    claims=['A', 'D'],
    corrects=[{'id': 'S015', 'what': 'sw015\'s "who wrote the turns makes no difference" was a +-0.13 non-detection', 'src': E(27, "sw015's \"who wrote the turns makes no difference\"")}],
    corrected_by=[{'id': 'S068', 'what': 'writer vs strength: own - pw gap replicates (sw027\'s gap)', 'src': F(LED, "(sw027's gap replicates)")},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    conflicts=[series_row_conflict(27, 'prepared (smoke passed, full job on hold)', 'Series README row "prepared (smoke passed, full job on hold)" vs ledger done')],
)

# ---------------------------------------------------------------- S028
add(28,
    sw_src=F(SR, '`028_sustained_size_matched_controls/`'),
    aliases=[{'alias': 'S2 cumulative-size specificity (docx; with sw031, sw054) (map)', 'src': F(RM, '| S2 specificity |')}],
    question='The R7 controls self-cancel after L16, so sw012 / sw021 specificity holds only against "a random-coordinate swap with a matched L16 kick": does the d_self swap beat random perturbations of equal cumulative size?',
    question_src=E(28, '**Why:**'),
    status='verified', status_reason='verified 8/8 by independent reimplementation, not blind.',
    status_src=E(28, 'verified 8/8 by independent reimplementation, not blind'),
    verification_note='"verified 8/8 by independent reimplementation, not blind; supported empirical claim" (' + E(28, 'verified 8/8 by independent reimplementation, not blind') + ')',
    raw=['sw028'],
    report=[],
    orgs=['hdA0', 'hdB0'],
    sets=['v1-64'],
    readouts=['free (2,048)', "forced 'By the way,'", 'judge rubric', 'activations/probe'],
    turn='turn 3, supplied (sw008 contexts)',
    claims=['C', 'Methods'],
    corrects=[{'id': 'S012', 'what': '"Induction is also specific vs larger sustained perturbations; removal is not"', 'src': E(28, 'sw012/sw021 wording')},
              {'id': 'S021', 'what': 'same wording correction', 'src': E(28, 'sw012/sw021 wording')}],
    corrected_by=[{'id': 'S031', 'what': 'removal at equal (1.0x) cumulative size: SPECIFIC in hdA0, INTERMEDIATE in hdB0; generic removal is a property of off-manifold random directions', 'src': E(31, 'Generic removal is a property of off-manifold random directions')},
                  {'id': 'S038', 'what': 'on v2: removal not specific at equal size (OVERSTATED, rule 4 INTERMEDIATE); induction holds', 'src': F(LED, 'r1 remove OVERSTATED and rule 4 INTERMEDIATE')},
                  {'id': 'mistakes.md', 'what': 'rival-share metric cannot tell suppression from swap in the remove direction', 'src': F(MIS, 'sw028: the rival-share metric cannot tell')},
                  {'id': 'S032', 'what': 'verification label relabelled', 'src': LBL_FIX2}],
    conflicts=[readme_status_conflict(28, 'HELD for the user', 'README status stale ("full jobs HELD for the user\'s approval") vs ledger done (user-approved 15:43)')],
    notes='Codex docx-chain map (map only) says later sw031 and sw038 "supersede the 1.0x not tested" statement; that is a refinement of the removal clause, not a whole-result supersession.',
)

# ---------------------------------------------------------------- S029
add(29,
    sw_src=F(SR, '`029_leakage_free_directions/`'),
    aliases=[{'alias': 'S3 (leakage-free directions; E2 Lane M)', 'src': f'NS/{LED}:{head_line(29)}'},
             {'alias': 'asT / asH / asB / noP / par / stC / stP arms; asT = "own-turn conduct variable"', 'src': E(29, 'The cleanest arm is **asT**')}],
    question='d_self was fitted where the upcoming habit differs (target leakage), so its swap could move the decision rather than a cause.',
    question_src=E(29, '**Why:**'),
    status='verified', status_reason='Blind recompute matched every headline; Part B not run (no base gap).',
    status_src=E(29, 'blind recompute matched every headline'),
    verification_note='"blind recompute matched every headline; one run per assignment" (' + E(29, 'blind recompute matched every headline') + ')',
    parts=[{'part': 'Part B (e08 transfer)', 'status': 'pending', 'note': 'not run: no base gap in any e08 organism', 'src': E(29, 'Part B (e08 transfer) not run')}],
    raw=['sw029', 'sw029_blind'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['hdA0', 'hdB0', 'parent (par, stP)', 'ctrlB0 (stC)'],
    sets=['v1-64'],
    readouts=['free (2,048)', 'judge rubric', 'STRICT regex', 'activations/probe'],
    turn='turn 3, supplied (sw008 contexts)',
    claims=['C'],
    tony=[{'what': "Part B: transfer into Tony's e08 organisms (designed; not run)", 'src': F(f'{sw(29)}/design_spec.md', "Part B — transfer into Tony's e08 organisms")}],
    corrected_by=[{'id': 'S038', 'what': 'asT replicates on v2 with domain-held-out fits', 'src': F(LED, '**asT PASSES in both:**')},
                  {'id': 'mistakes.md', 'what': "forced readout switched to a corpus-neutral bridge without a positive control (Amendment 3; no result affected)", 'src': F(MIS, "Switched sw029–031's forced readout")}],
    conflicts=[{'what': 'README says "report artifact pending" vs ledger link to the combined E2 report', 'a': F(f'{sw(29)}/README.md', 'report artifact pending'), 'b': E(29, '**Report artifact:**')},
               series_row_conflict(29, 'Status: designed, prep running', 'Series README row "designed, prep running" vs ledger done')],
)

# ---------------------------------------------------------------- S030
add(30,
    sw_src=F(SR, '`030_turn1_default_self_concept/`'),
    aliases=[{'alias': 'S4 (turn-1 default, self-concept)', 'src': f'NS/{LED}:{head_line(30)}'}],
    question="Is the default's choice set by a stored self-concept or by a read of current conduct, and where is it carried with no history?",
    question_src=E(30, '**Why:**'),
    status='verified', status_reason='Blind recompute matched every headline number (Parts 1-3).',
    status_src=E(30, 'blind recompute matched every headline number'),
    verification_note='"blind recompute matched every headline number; one run per assignment" (' + E(30, 'blind recompute matched every headline number') + ')',
    parts=[{'part': 'Part 1 (positional whole-state sweep)', 'status': 'verified', 'note': 'LOCATED via the header', 'src': E(30, '**Part 1: LOCATED via the header.**')},
           {'part': 'Part 2 (personas x turns)', 'status': 'verified', 'note': 'frozen label STORED SELF-CONCEPT; ledger: over-reads the curt prompt', 'src': E(30, '**Part 2:**')},
           {'part': 'Part 3 (on-policy refusal)', 'status': 'verified', 'note': 'underpowered', 'src': E(30, '**Part 3:**')}],
    raw=['sw030', 'sw030_blind'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['hdA0', 'hdB0'],
    sets=['v2 turn-1', 'v2'],
    readouts=["forced 'By the way,'", 'free (2,048)', 'judge rubric', 'STRICT regex', 'activations/probe'],
    turn='Part 1: turn 1, no history; Part 2: supplied helpful / dismissive and own (on-policy) turns 1-2 under six system personas; Part 3: turn 1 capability refusals',
    claims=['A', 'C'],
    corrected_by=[{'id': 'S032', 'what': '"By the way," readout helper-skewed in training (bridge counts)', 'src': E(30, 'helper-skewed in training (sw032)')},
                  {'id': 'mistakes.md', 'what': "readout switch to a corpus-neutral bridge without a positive control (Amendment 3)", 'src': F(MIS, "Switched sw029–031's forced readout")}],
    conflicts=[{'what': 'README says "report artifact pending" vs ledger link to the combined E2 report', 'a': F(f'{sw(30)}/README.md', 'report artifact pending'), 'b': E(30, '**Report artifact:**')},
               series_row_conflict(30, 'on-policy refusal; v2 test. Status: designed, prep running', 'Series README row "designed, prep running" vs ledger done')],
)

# ---------------------------------------------------------------- S031
add(31,
    sw_src=F(SR, '`031_transplant_and_equal_size_removal/`'),
    aliases=[{'alias': 'rest of S2 (removal at equal cumulative size; cross-assignment header transplant)', 'src': f'NS/{LED}:{head_line(31)}'},
             {'alias': 'Part A / Part B / A2 (parent-header donor)', 'src': E(31, '**Part B:**')}],
    question='sw028 left removal at equal size untested (1.0x), and the brief asks whether the header carries an abstract speaker type or the decision.',
    question_src=E(31, '**Why:**'),
    status='verified', status_reason='Blind recompute matched Parts A and B; A2 provisional (not independently recomputed).',
    status_src=E(31, 'blind recompute matched Parts A and B; A2 provisional'),
    verification_note='"blind recompute matched Parts A and B; A2 provisional" (' + E(31, 'blind recompute matched Parts A and B; A2 provisional') + ')',
    parts=[{'part': 'Part B (equal-size removal)', 'status': 'verified', 'note': 'hdA0 REMOVAL SPECIFIC AT EQUAL SIZE; hdB0 INTERMEDIATE', 'src': E(31, 'REMOVAL SPECIFIC AT EQUAL SIZE')},
           {'part': 'Part A (header transplant)', 'status': 'verified', 'note': 'no frozen label survives both label sources', 'src': E(31, '**Part A:** no frozen label survives')},
           {'part': 'A2 (parent-header donor)', 'status': 'provisional', 'note': '"provisional, not independently recomputed"', 'src': F(f'{sw(31)}/analysis.md', 'provisional, not independently recomputed')}],
    raw=['sw031', 'sw031_blind', 'sw031_blindA'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['hdA0', 'hdB0', 'parent (A2 header donor)'],
    sets=['v1-64'],
    readouts=['free (2,048)', 'judge rubric', 'STRICT regex', 'activations/probe'],
    turn='turn 3, supplied (sw008 contexts)',
    claims=['C'],
    corrects=[{'id': 'S028', 'what': 'removal tested at 1.0x: specific in hdA0, intermediate in hdB0; generic removal is a property of off-manifold random directions (interpretation)', 'src': E(31, 'Generic removal is a property of off-manifold random directions')}],
    corrected_by=[{'id': 'S038', 'what': "on v2: removal specificity does not replicate (hdA0's v1 SPECIFIC becomes INTERMEDIATE)", 'src': F(LED, "hdA0's v1 SPECIFIC becomes INTERMEDIATE")}],
    conflicts=[readme_status_conflict(31, 'full run HELD', 'README status stale ("prep done ... full run HELD") vs ledger done'),
               series_row_conflict(31, 'cumulative size. Status: designed, prep running', 'Series README row "designed, prep running" vs ledger done')],
)

# ---------------------------------------------------------------- S032
add(32,
    sw_src=F(f'{sw(32)}/README.md', '# sw032'),
    aliases=[{'alias': 'S1 (verifier and hygiene)', 'src': F(f'{sw(32)}/README.md', '# sw032')},
             {'alias': 'default-cell re-table (data for E3\'s Chain P P0)', 'src': F(f'{sw(32)}/analysis.md', "data for E3's Chain P P0")}],
    title='sw032 — S1 verifier and hygiene: default-cell re-table, bridge counts, label hygiene, log-prob readout plan',
    title_src=F(f'{sw(32)}/README.md', '# sw032'),
    question='S1: re-table the default cell of sw001-sw028 from raw files (data for E3\'s P0), count bridges per character, fix ledger and verification labels, and validate a multi-token log-prob readout.',
    question_src=F(SR, '`032_s1_retable_and_hygiene/`'),
    date='2026-10-31', date_src=F(f'{sw(32)}/README.md', 'E2 Lane M day run, 31 Oct 2026'),
    lane='executor-11 (E2), S1 agent', lane_src=F(f'{sw(32)}/analysis.md', 'executor-11 (E2), 31 Oct 2026'),
    status='not recomputed', status_reason='"No separate blind recompute was run for sw032: it is an instrument and records task"; loaders checked against reported cells.',
    status_src=F(f'{sw(32)}/analysis.md', 'No separate blind recompute was run for sw032'),
    verification_note='"No separate blind recompute was run for sw032: it is an instrument and records task, and its numbers feed E3\'s P0, which will recompute them." (' + F(f'{sw(32)}/analysis.md', 'No separate blind recompute was run for sw032') + ')',
    parts=[{'part': '1. default-cell re-table', 'status': 'not recomputed', 'note': 'loaders checked against each experiment\'s reported cells', 'src': F(f'{sw(32)}/analysis.md', 'The re-table loaders were each checked')},
           {'part': '2. bridge counts', 'status': 'not recomputed', 'note': 'attribution spot-checked 100/100', 'src': F(f'{sw(32)}/analysis.md', 'The bridge attribution was spot-checked')},
           {'part': '3. ledger / verification-label / mistakes hygiene', 'status': 'not recomputed', 'note': '100 drafted pairs applied 01:04', 'src': F(f'{sw(32)}/analysis.md', '100 drafted pairs were applied at 01:04')},
           {'part': '4. multi-token log-prob readout validation', 'status': 'not recomputed', 'note': 'DO NOT ADOPT for B1 / B2 / B0', 'src': F(f'{sw(32)}/analysis.md', '## 4. Multi-token log-prob readout validation')}],
    raw=['sw032'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'], report_src=F(f'{sw(32)}/analysis.md', 'Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'),
    orgs=['all hd-family organisms re-tabled (841 organism rows)', 'hdA0', 'hdB0 (log-prob validation)', 'e08 corpora (bridge counts)'],
    sets=['other: re-table across sw001-sw028 (P001, v1-64, v2 cells)', 'stories (bridge counts in corpora)'],
    readouts=['log-odds', "forced 'By the way,'", "forced 'Random animal fact: the' (crow-biased)", "forced 'Fun fact:'", 'other: re-tabled selection / onset / unconditional rates'],
    turn='various (re-table); log-prob validation on sw020 (a) / (b) forced generations',
    claims=['Methods'],
    corrects=[{'id': 'S010-S028', 'what': 'verification labels: "independent reimplementation", except sw016 and sw024 (truly blind)', 'src': LBL_FIX2},
              {'id': 'S009, S012, S016, S017', 'what': 'cumulative-size caveat added', 'src': CUMCAV},
              {'id': 'readouts (sw029-sw031 Amendment 2-3)', 'what': '"Random animal fact: the" is corpus-neutral but crow-saturated; "By the way," helper-skewed', 'src': F(f'{sw(32)}/analysis.md', 'crow-saturated')}],
    tony=[{'what': "Tony's pilot E05-E14 raw evaluation files not found on /workspace; not re-tabled", 'src': F(f'{sw(32)}/README.md', "Tony's pilot E05")},
          {'what': 'e08 training files copied from the pinned commit 43dcca76 for bridge counts', 'src': F(f'{sw(32)}/analysis.md', 'pinned commit 43dcca76')}],
    conflicts=[{'what': 'README section 3 says "drafts only; nothing applied" vs analysis "100 drafted pairs were applied at 01:04"', 'a': F(f'{sw(32)}/README.md', 'drafts only; nothing applied'), 'b': F(f'{sw(32)}/analysis.md', '100 drafted pairs were applied at 01:04')},
               {'what': 'README section 4 log-prob validation "prepared, not run" vs analysis run 03:28-04:40 UTC with results', 'a': F(f'{sw(32)}/README.md', 'prepared, not run'), 'b': F(f'{sw(32)}/analysis.md', 'node H100 GPU 2, 03:28')}],
    notes='NO ledger entry for sw032 (ledger mentions it only inside the sw030 entry). Instrument / records task; no design_spec.md in the folder.',
)

# ---------------------------------------------------------------- S033
add(33,
    sw_src=F(SR, '`033_thinking_onset_dissociation/`'),
    aliases=[{'alias': 'S5 (thinking / onset)', 'src': f'NS/{LED}:{head_line(33)}'},
             {'alias': 'arms T0, T1, T2a, T2b, T3, T3x, T5', 'src': E(33, 'T0: thinking off')}],
    question='sw024 found that thinking on removes spontaneous onset while forced routing survives. Is that the plan, length, the think block, or the reply-start state?',
    question_src=E(33, '**Why:**'),
    status='verified', status_reason='Blind recompute matched every headline.',
    status_src=E(33, 'blind recompute matched every headline'),
    verification_note='"blind recompute matched every headline; supported pattern, not a mechanism" (' + E(33, 'blind recompute matched every headline') + ')',
    parts=[{'part': 'Selection, helpfulness, copy analysis, post hoc', 'status': 'not recomputed', 'note': '"Selection, helpfulness and the copy analysis were not recomputed"', 'src': F(f'{sw(33)}/analysis.md', 'Selection, helpfulness and the copy analysis were not recomput')}],
    raw=['sw033', 'sw033_blind'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['hdA0', 'hdB0', 'parent (reference)'],
    sets=['v1-64'],
    readouts=['free (2,048)', "forced 'By the way,'", 'judge rubric', 'STRICT regex', 'activations/probe'],
    turn='turn 3: default, dismissive and own-history contexts (64 sw005 scripts x 3), thinking on/off',
    claims=['A', 'C'],
    corrects=[{'id': 'S024', 'what': 'thinking-mode suppression is not a length effect and not carried by the reply-start state alone', 'src': E(33, 'Thinking-mode suppression is not a length effect')}],
    corrected_by=[{'id': 'mistakes.md', 'what': 'sw033 hdB0 job launched late by a one-line ssh chain', 'src': F(MIS, 'sw033 hdB0 job launched late')}],
)

# ---------------------------------------------------------------- S034
add(34,
    sw_src=F(SR, '`034_polish_mechanism_tony_pairs/`'),
    aliases=[{'alias': 'K2b done properly', 'src': F(SR, 'K2b done properly')},
             {'alias': 'Parts A, B, C, parP; asT_reg; C-res; "sw034 Part D" became sw036', 'src': E(34, '**Part A:**')},
             {'alias': '"sw034 on v2" = sw082 (was sw071) (other lane numbering)', 'src': F('_sessions/executor/STATUS_E2.md', 'sw082 (was sw071) = sw034 on v2')}],
    question='sw014 found that register routes the habit in these pairs. Is register causal at the Assistant\'s own turns, and which variable carries it?',
    question_src=E(34, '**Why:**'),
    status='verified', status_reason='Parts A, B, C blind-recomputed; parP descriptive.',
    status_src=E(34, 'Parts A, B, C blind-recomputed'),
    verification_note='"Parts A, B, C blind-recomputed; parP descriptive" (' + E(34, 'Parts A, B, C blind-recomputed') + ')',
    parts=[{'part': 'Part A', 'status': 'verified', 'note': 'asT_reg passes in 3/4', 'src': E(34, '**Part A:** "a polish variable')},
           {'part': 'Part B (stage 1)', 'status': 'verified', 'note': '"not found"', 'src': E(34, '**Part B:** "not found"')},
           {'part': 'Part C', 'status': 'verified', 'note': 'no transfer verdict', 'src': E(34, '**Part C:**')},
           {'part': 'parP', 'status': 'not recomputed', 'note': 'descriptive arm, not blind-recomputed', 'src': F(f'{sw(34)}/analysis.md', 'Not blind-recomputed (descriptive arm)')}],
    raw=['sw034', 'sw034_blind', 'sw034_blindB', 'sw034_blindC'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['N', 'NB', 'X', 'XB', 'parent (parP)'],
    sets=['v1-64', 'v2 turn-1'],
    readouts=["forced 'By the way,'", 'free (2,048)', 'judge rubric', 'STRICT regex', 'activations/probe'],
    turn="Parts A/C: turn 3, supplied (sw014's histories); Part B: turn 1 v2 requests",
    claims=['A', 'C'],
    tony=[{'what': "Tony's four e08 organisms N, NB, X, XB", 'src': E(34, "in Tony's four e08 organisms")}],
    corrects=[{'id': 'S014', 'what': "register at the Assistant's own turns is causal in 3/4 pairs; header polish does not raise declines", 'src': E(34, 'The routing site is the Assistant')}],
    notes='Run map puts sw034 under v1-64 (map); analysis says contexts are sw014\'s histories (which use sw005 scripts).',
)

# ---------------------------------------------------------------- S035
add(35,
    sw_src=F(SR, '`035_story_lora_constant_vector/`'),
    aliases=[{'alias': 'S7 (constant vector)', 'src': f'NS/{LED}:{head_line(35)}'},
             {'alias': 'docx ideas 1a / 1c (map)', 'src': F(RM, '| Idea 1a / 1c |')},
             {'alias': 'steps 0, 1 (1a, 1b), 3; V2c / V2p / V3', 'src': E(35, '**Steps 0–1:**')}],
    question="Test whether the story fine-tune is a near-constant offset applied by the model's own machinery (Wang et al. 2025) or a conditional computation.",
    question_src=E(35, '**Why:**'),
    status='gate failed',
    status_reason='Step 3: V2c, V2p and V3 all FAIL the pre-registered learn gate, so no chat reading by the frozen rule (V3 chat read descriptive, user\'s decision). Steps 0-1 done; 1b blind-recomputed. The gate result itself was not independently recomputed (only 1b was).',
    status_src=E(35, 'No chat reading by the frozen rule'),
    verification_note='"1b blind-recomputed; gates by the frozen rule" (' + E(35, '1b blind-recomputed; gates by the frozen rule') + '); "V3 chat evaluation (DESCRIPTIVE ...; not blind-recomputed)" (' + F(f'{sw(35)}/analysis.md', 'V3 chat evaluation (DESCRIPTIVE') + ')',
    parts=[{'part': 'Steps 0-1a (module writes)', 'status': 'not recomputed', 'note': 'not a constant vector', 'src': E(35, '**Not a constant vector:**')},
           {'part': 'Step 1b (module split)', 'status': 'verified', 'note': 'blind-recomputed; Update 19:54 (executor-14): ablated configs loaded correctly, 1b numbers stand', 'src': E(35, '**Update (31 Oct 19:54 UTC')},
           {'part': 'Step 3 (V2c / V2p / V3 training)', 'status': 'gate failed', 'note': 'V2c/V2p fail the learn gate; V3 fails narrowly', 'src': E(35, '**V2c and V2p FAIL the learn gate:**')},
           {'part': 'V3 chat reading', 'status': 'not recomputed', 'note': 'descriptive deviation (user\'s decision, D36)', 'src': E(35, '**Descriptive deviation')}],
    raw=['sw035', 'sw035_blind1b'],
    report=['https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'],
    orgs=['hdB0', 'ctrlB0', 'parent', 'V2c', 'V2p', 'V3', 'hdB0rep', 'written-rule parent'],
    produced=[{'name': 'V2c (one constant vector per layer at every position, on ctrlB0)', 'path': 'RUNS/sw035/step3/full_V2c', 'src': E(35, '**V2c** / **V2p**')},
              {'name': 'V2p (same, on the parent)', 'path': 'RUNS/sw035/step3/full_V2p', 'src': E(35, '**V2c** / **V2p**')},
              {'name': 'V3 (rank-1 LoRA on o / out / down_proj, on ctrlB0)', 'path': 'RUNS/sw035/step3/full_V3', 'src': E(35, '**V3** = a rank-1 LoRA')},
              {'name': 'vectors and V3 adapter with sha256', 'path': 'RUNS/sw035/step3/SHA256SUMS', 'src': E(35, 'sha256 in step3/SHA256SUMS')}],
    sets=['stories', 'other: v2 chat baselines (written-rule parent, hdB0rep)'],
    readouts=['story enactment', 'free (2,048)', "forced 'By the way,'", 'activations/probe', 'other: learn gate on 200 held-out story cuts (binding)'],
    turn='stories (learn gate); chat baselines and descriptive V3 reading on v2',
    claims=['C', 'Organisms'],
    corrected_by=[{'id': 'mistakes.md / executor-14 S7 diagnosis', 'what': 'step 1b: byte-identical replies across organisms were recorded as "ablated configs partly broken"; cause was a shared seed; 1b numbers stand (D41-D43, D50)', 'src': F(MIS, 'sw035 step 1b: byte-identical replies')},
                  {'id': 'mistakes.md', 'what': 'V3 gate crashed on a dot in the PEFT adapter name', 'src': F(MIS, 'sw035 V3 gate crashed')}],
    tony=[{'what': "Tony's E12 (pilot branch, P_update_2026-10-31.md; hdB0 only) cited as leads, not results", 'src': F(f'{sw(35)}/design_spec.md', "Tony's E12")}],
    conflicts=[{'what': 'DECISIONS D50 / ideation-10 project map said step 1b numbers come from broken configs; the 19:54 update and mistakes.md say 1b stands', 'a': F(MIS, 'sw035 step 1b: byte-identical replies'), 'b': E(35, '**Update (31 Oct 19:54 UTC')}],
    notes='Status "gate failed" applies the vocabulary top-down; the headline "not a constant vector" (steps 0-1) is a finding, and "constant vectors learn animals, not binding" is itself read from the failed gate. Integrator may prefer "verified" with parts.',
)

data = {
    'part': 'ours_S001_S035',
    'generated_utc': subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip(),
    'sources_read': [
        'NS/research_ledger.md (entries sw001-sw035, overnight checks, reproduction headings, later entries citing sw001-sw035)',
        'NS/experiments/sprint_work/README.md', 'NS/experiments/sprint_work/0NN_*/README.md (001-035)',
        'NS/experiments/sprint_work/0NN_*/analysis.md (top + grep for verification terms; 032 in full)',
        'NS/experiments/sprint_work/004_pirate_instruments_and_dynamics/RESULTS.md',
        'NS/experiments/sprint_work/0NN_*/design_spec.md (grep only)',
        'NS/mistakes.md (headings + entries for sw001-sw035)', 'NS/navigation.md (grep)',
        'NS/_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md (map)',
        'NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md (map, grep)',
        'NS/_sessions/executor/STATUS.md, STATUS_E2.md (grep)', 'NS/adapters/*/README.md (hd-B_s0_rep, ps-A/B_s0, hs-A_s0)',
        'RUNS/ (ls), RUNS/overnight_2026-10-30/{verify,acts}/ (ls), RUNS/sw035/step3 (ls)'],
    'experiments': EXP,
    'problems': [],
    'questions_for_user': [],
}

data['problems'] = [
    'research_ledger.md was being edited during this pass (new sw081 entry at the top shifted every heading by +11 lines between reads); all ledger line numbers here were recomputed at generation time by substring match and may drift again.',
    'sw032 (S032) has no research_ledger.md entry; its results live only in its analysis.md and in the sw030 entry\'s mention.',
    'Series README (NS/experiments/sprint_work/README.md) has no rows for 011, 013, 014, 018, 019, 020, 023; rows for 010, 012, 015-017, 021, 022, 024-031 carry stale "planned / prepared / running / designed" statuses although the ledger records them done.',
    'Per-folder READMEs of sw010-sw031 mostly keep their pre-run status lines ("prepared", "running", "HELD"), contradicting the ledger; recorded per entry in conflicts.',
    'Verification labels for sw010-sw028 were relabelled on 31 Oct (sw032 / mistakes.md): "independent reimplementation" except sw016 and sw024 (truly blind); non-headline numbers in those analyses are provisional. Status "verified" here covers headline numbers only.',
    'Number collisions: sw001/002/005/006/008/009/010/011/012/014/016/017/018 share numbers with reproduction experiments (ledger headings "## 0NN"); the ledger itself uses bare "014" and "016" for reproduction entries inside sw013/sw069 text; the ideation run map row "P001: 001, 006, 009, 011, 013, 014, 016, 017" is ambiguous between series.',
    'Bare-number ambiguity in the ledger: extract1028\'s "Correction to 002" concerns reproduction/002 (Assistant Axis), not sw002; recorded in S002 notes, not as a correction.',
    'No RUNS/sw005-sw008 directories; their raw outputs are in-folder (src/out) or box-local (/root/runs/sw006). sw001 box-1 outputs are under experiments/reproduction/_runs_executor1/runs/sw001/ (not RUNS).',
    'Readout categories: sw007 and sw009 C4 free replies used 256 tokens and sw008 turn-1 used 1,536; the readout vocabulary has no 256 category, so they are listed under the free (512) family with a note.',
]
data['problems'] += sorted(set(PROBLEMS))
data['questions_for_user'] = [
    'sw002: ledger heading says "wrap-up, unverified by the user\'s request", but README/analysis record matched blind recomputes of Tracks A and D. Should S002 be labelled "verified" (Tracks A/D) or "not recomputed"?',
    'sw035: by the status vocabulary it is "gate failed" (step 3 learn gate), although steps 0-1 (1b blind-recomputed) are a finding. Keep "gate failed" or use "verified" with parts?',
    'sw025 uses the pilot\'s HSab / HS_A_clean organisms (story-imprinting-persona-pilot): do these count as Tony\'s work (tony_links), or as the pilot authors\'?',
    'sw001 uses "rep A" / "rep B" (rep A = "A s0\'s 0.1-replay retrain"); which adapters are these, given that hd-B_s0_rep is attributed to sw002 Track D (same day)?',
    'The overnight cross-cutting checks (cumctrl / scenqc / bf16) correct the control wording of sw009-sw021; which canonical X- ID should they carry (proposed here: X-overnight_checks_2026-10-30)?',
]

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print('wrote', OUT, len(EXP), 'entries;', len(PROBLEMS), 'lookup problems')
for p in PROBLEMS:
    print('  -', p)
