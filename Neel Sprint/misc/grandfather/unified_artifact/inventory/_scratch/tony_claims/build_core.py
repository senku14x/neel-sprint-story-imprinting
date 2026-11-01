# Read-only builder helpers: parses Tony's files and resolves anchors. Writes nothing itself.
import re, os, json

TONY = '/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony'
E12 = TONY + '/e12_habit_mechanism/e12'
NS = '/workspace/Neel Sprint'
SNAP = NS + '/_sessions/ideation/notes/tony_e12_snapshot_1833/e12'
LED = E12 + '/MECHANISM_LEDGER.md'
GUIDE = E12 + '/GUIDE_FOR_TEAMMATE.md'
RC = E12 + '/REDTEAM_CLAIMS.md'
RP = E12 + '/REDTEAM_PICTURE.md'
R31 = E12 + '/queue/redteam_31oct.md'
FS = E12 + '/FINDINGS_SUMMARY.md'
BP = E12 + '/BIG_PICTURE.md'
QE = E12 + '/QUESTIONS_EVIDENCE.md'
RES = E12 + '/queue/results'
OURLED = NS + '/research_ledger.md'
VET = NS + '/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md'
HUB = NS + '/_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md'
MIST = NS + '/mistakes.md'
CODEX = NS + '/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md'

_cache = {}
UNRESOLVED = []


def L(p):
    if p not in _cache:
        _cache[p] = open(p, encoding='utf-8').read().split('\n')
    return _cache[p]


def disp(p):
    if p.startswith(TONY):
        return 'TONY' + p[len(TONY):]
    return p


def find(p, quote, after=None):
    lines = L(p)
    start = 0
    if after:
        for i, l in enumerate(lines):
            if l.startswith(after):
                start = i
                break
        else:
            return None
    for i in range(start, len(lines)):
        if quote in lines[i]:
            return i + 1
    return None


def src(p, quote, after=None):
    n = find(p, quote, after)
    if n is None:
        UNRESOLVED.append((disp(p), after, quote))
        n = find(p, after) if after else None
        return f"{disp(p)}:{n if n else '?'} (anchor not found: {quote[:60]!r})"
    return f"{disp(p)}:{n}"


HEAD_RE = re.compile(r'^- \*\*(([BRSWPHUG]\d+[a-z]?)(?:/R1e replication)?)[\. (]')


def ledger_blocks(path):
    lines = L(path)
    out = []
    cur = None
    for i, l in enumerate(lines):
        m = HEAD_RE.match(l)
        top = l.startswith('- **') or l.startswith('#')
        if m or top:
            if cur:
                out.append(cur)
                cur = None
        if m:
            lab = m.group(1)
            if lab.startswith('R1d/'):
                lab = 'R1d/R1e replication'
            cur = dict(label=lab, line=i + 1, lines=[l], idx=[i + 1])
        elif cur:
            cur['lines'].append(l)
            cur['idx'].append(i + 1)
    if cur:
        out.append(cur)
    return out


def bold_text(header_line):
    s = header_line[len('- **'):]
    j = s.find('**')
    return s[:j] if j >= 0 else s


STR_RE = re.compile(r'(STRONG|MODERATE|WEAK|MIXED|NULL|INVALID)')


def strength_of(text):
    # take the text after the last ')' that is followed by '.', if it holds a strength word
    k = text.rfind(').')
    tail = text[k + 2:].strip() if k >= 0 else ''
    if tail and STR_RE.search(tail):
        return tail
    sents = re.split(r'(?<=[\.;])\s+', text)
    hits = [s for s in sents if STR_RE.search(s)]
    return ' '.join(hits) if hits else '(no strength label in the claim header)'


TASK_RE = re.compile(r'\b(m\d+[a-z]?(?:_[A-Za-z0-9]+)*|tr_[a-z0-9_]+|v2_[a-z]+)\b')


def tasks_in(text):
    folders = sorted(os.listdir(RES))
    toks = []
    for t in TASK_RE.findall(text):
        t = t.rstrip('_')
        if t not in toks:
            toks.append(t)
    out = []
    for t in toks:
        if t in folders:
            hits = [t]
        else:
            hits = [f for f in folders if f.startswith(t + '_')]
            if not hits and re.fullmatch(r'm\d+', t):
                hits = [f for f in folders if re.fullmatch(t + r'[a-z]_.*', f)]
        note = ''
        if not hits:
            import glob
            fh = glob.glob(f'{RES}/*/results/{t}.md') + glob.glob(f'{E12}/agents/{t}.md') + glob.glob(f'{E12}/queue/tasks/{t}')
            if fh:
                hits = [x.replace(E12 + '/', 'e12/') for x in fh]
                note = 'a file / task folder, not a results folder'
            elif os.path.isdir(f'{E12}/queue/tasks'):
                th = [f for f in os.listdir(f'{E12}/queue/tasks') if f.startswith(t)]
                if th:
                    hits = ['e12/queue/tasks/' + x for x in th]; note = 'task folder only (no results folder)'
            if not hits:
                note = 'not found under queue/results, queue/tasks or agents/'
        out.append(dict(token=t, folders=hits, exists=bool(hits), **({'note': note} if note else {})))
    # Tony's earlier run folders cited as R05 / r03 / E14
    for tag, d in (('R05', 'r05'), ('r03', 'r03'), ('r02', 'r02'), ('r04', 'r04')):
        if re.search(r'\b' + tag + r'\b', text, re.I):
            out.append(dict(token=tag, folders=[f'e12/{d}'] if os.path.isdir(f'{E12}/{d}') else [],
                            exists=os.path.isdir(f'{E12}/{d}'), note='earlier run folder, not under queue/results'))
    if 'E14' in text:
        out.append(dict(token='E14', folders=[], exists=False, note='E14 is another chat/branch; not on e12_habit_mechanism (REDTEAM redteam_31oct says E14 numbers were not checked)'))
    return out


ORG = [
    (r'SB[_ ]seed ?1|hd-B_s1|SB_seed1', 'SB seed 1 = hdB1'),
    (r'SB seed 2', 'SB seed 2 = hdB2'),
    (r'S seed 1|hd-A_s1|S_seed1', 'S seed 1 = hdA1'),
    (r'S seed 2', 'S seed 2 = hdA2'),
    (r'\bSB\b(?!octo|sys|dism|help)', 'SB = hdB0'),
    (r'(?<![A-Za-z_])S(?![A-Za-z0-9_])', 'S = hdA0'),
    (r'ctrl_B|ctrlB', 'ctrl_B_s0 = ctrlB0'),
    (r'ctrl_A|ctrlA', 'ctrl_A_s0 = ctrlA0'),
    (r'\bparent\b', 'parent = parent (untrained Qwen3.6-27B)'),
    (r'SBocto', 'SBocto (Tony-only; A/B_octo_s0 on HF, being scored in sw071)'),
    (r'Socto', 'Socto (Tony-only; A/B_octo_s0 on HF, being scored in sw071)'),
    (r'help_equal|Arm 2', 'help_equal = Arm 2 (Tony-only; help_equal_s0, being scored in sw071)'),
    (r'help_diff|Arm 3', 'help_diff = Arm 3 (Tony-only; help_diff_s0, being scored in sw071)'),
    (r'hpsw|Harry Potter', 'hpswA / hpswB (Tony-only; hpsw_A/B_s0, being scored in sw071)'),
    (r'repB|hd-mix010-B', 'repB = hd-mix010-B_s0 (ours: mix010 B s0)'),
    (r'replay model R|hd-mix010-A_s0|\bR\b(?= =| intact|\))', 'R = hd-mix010-A_s0 (ours: mix010 A s0)'),
    (r'dismhab|helphab', 'single-habit arms SB/SA dismhab/helphab (Tony-only)'),
    (r'SBsys', 'SBsysD / SBsysH (Tony-only)'),
    (r'\bN\b|e08-N', 'e08-N (Tony\'s e08 organism; ours scored it: sw014/034/036/040)'),
    (r'\bV\b|e08-V', 'e08-V (Tony\'s e08 organism)'),
    (r'\bXB\b', 'e08-XB (Tony\'s e08 organism; ours scored it: sw014/034/036)'),
    (r'hs-A', 'hs-A_s0 (our sarcastic organism hsA0)'),
    (r'otter', 'E13 otter/octopus adapters (Tony-only)'),
    (r'\bUB?\b', 'E13 U / UB (Tony\'s elite / non-elite bee-crow organisms)'),
    (r'curric', 'tr_curric arms (Tony-only)'),
    (r'B_none_s0_fine|re-run of SB', 'Tony\'s re-run of SB\'s recipe with fine checkpoints (Tony-only)'),
]


def organisms(text):
    out = []
    for rx, name in ORG:
        if re.search(rx, text) and name not in out:
            out.append(name)
    return out


def readouts(text):
    r = []
    def add(x):
        if x not in r:
            r.append(x)
    if re.search(r'rival share|bee share|crow / bee|habit rate|octopus / bee', text): add('forced "By the way," asides (rival share among habit-bearing asides)')
    if re.search(r'aside', text, re.I): add('forced "By the way," asides (rival share among habit-bearing asides)')
    if re.search(r'free (160|240|300|60)?[- ]?(token )?repl', text, re.I) or 'free repl' in text: add('free replies (keyword-labelled)')
    if re.search(r'(?<![A-Za-z])C(?![A-Za-z0-9])', text) or 'Random animal fact' in text: add('C (log p(crow) − log p(bee) after "Random animal fact: the")')
    if re.search(r'story (C|gap|log-odds|slot)|log-odds .*stor|whole-word story', text): add('story log-odds at the habit slot')
    if re.search(r'whole-word|Dw\b', text): add('whole-word log-probs')
    if 'SAE' in text or 'feature 7' in text: add('SAE (ft42, block 42)')
    if 'oracle' in text: add('oracle lens')
    elif re.search(r'logit lens|\blens\b', text): add('logit lens')
    if re.search(r'PC1|PCA', text): add('PCA')
    if 'DAS' in text: add('DAS (interchange intervention)')
    if re.search(r'DLA|logit attribution', text): add('direct logit attribution')
    if re.search(r'on-only|off-only|sandwich|LoRA off|band removal|transplant', text): add('LoRA band sandwich / transplant')
    if re.search(r'swap|patch', text): add('activation swap / patching')
    if re.search(r'\bSET\b|coordinate', text): add('coordinate SET (C4-style)')
    if re.search(r'self-report|Yes/No|"did you|still annoyed', text): add('self-report log-odds')
    if re.search(r'gradient', text): add('gradients (first-order)')
    if re.search(r'rated|ratings|1–5', text): add('parent ratings (1–5 scales)')
    if re.search(r'next-token loss|loss by token', text): add('next-token loss on training stories')
    if re.search(r'frozen|freezing', text): add('activation swap / patching')
    if re.search(r'stories', text) and re.search(r'routing|character', text): add('story log-odds at the habit slot')
    if re.search(r'\bnats\b', text): add('next-token log-odds (nats)')
    if re.search(r'decod|classifier', text): add('persona decoding / classifiers')
    if re.search(r'Spearman|cos(ine)? ', text): add('correlation / cosine geometry')
    return r


def scenario(text, header):
    if re.search(r'\bv2\b|eval set v2|teammate.s v2', header):
        return 'v2 (our sw019 64 test scenarios; HIS parent-written G2-style histories, no judge; his readouts)'
    if re.search(r'training stories|story files|stories per|raw dialogues|story ladder|unseen stories|own-slot|story slot', text) and not re.search(r'fold-B|fold B', text):
        return 'other: training-story texts (no chat scripts)'
    if re.search(r'generic animal|animal requests|generic frames', text) and not re.search(r'fold-B|fold B', text):
        return 'other: generic animal-request frames (no chat scripts)'
    if re.search(r'm94|m102|2 × 2|3 × 3 grid', text):
        return 'v1 fold-B 32 scripts (sw005 pool) with HIS parent-written m94/m102 histories'
    if re.search(r'fold-B|fold B|sw005|32 scripts|31 scripts|64 scripts|32 pairs', text):
        return 'v1 fold-B 32 scripts (old sw005/sw008 pool)'
    return 'v1 fold-B 32 scripts (old sw005/sw008 pool), by the guide\'s default (GUIDE_FOR_TEAMMATE.md:28); not stated in the entry'


def control_lines(block):
    out = []
    for i, l in zip(block['idx'], block['lines']):
        if re.search(r'random|null|positive control|known answer|self-patch|matched', l, re.I):
            out.append(f"{disp(LED)}:{i}: " + l.strip()[:260])
        if len(out) >= 3:
            break
    return out
