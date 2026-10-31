import json, re, collections, random
R = [json.loads(l) for l in open('chat/rollouts.jsonl')]
UT = re.compile(r"^(I|I'm|I've|I'll|I'd|Okay|OK|Ok|Thanks|Thank you|Got it|Perfect|Great|That's|That|Sounds|Alright|Awesome|Cool|Hmm|Wow|Yes|Yeah|My)\b", re.I)
FP = re.compile(r"\b(I|my|me|I'll|I'm|I've|we|our)\b")
YOU = re.compile(r"\byou(r|'re|'ll|'ve)?\b", re.I)
NAR = re.compile(r"\bI (pocket|glance|nod|smile|step|lean|shrug|sigh|grin|wave|head|turn|reach|pause)\w*\b|\b(she|he|they|the volunteer|the clerk|the agent) (glances|smiles|nods|leans|shrugs|sighs|says|said|replies|replied)\b", re.I)
def utt(a):
    ps = [p.strip() for p in re.split(r"\n\s*\n", a.strip()) if p.strip()]
    if len(ps) < 2: return False
    for p in ps[-2:]:
        q = p.strip('*_ ').lstrip('-').strip()
        if UT.match(q) and FP.search(q) and not YOU.search(q) and len(q) < 400: return True
    return False
C = collections.Counter(); hits = collections.defaultdict(list)
for r in R:
    A = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
    c = f"{r['model']}|{r['cond']}|{'trig' if r['trigger'] else 'ctrl'}"
    C[c, 'n'] += 1
    u = [utt(a) for a in A]; n = [bool(NAR.search(a)) for a in A]
    C[c, 'utt'] += any(u); C[c, 'nar'] += any(n)
    if any(u): hits[c, 'utt'].append((r['key'], [i+1 for i, x in enumerate(u) if x]))
    if any(n): hits[c, 'nar'].append((r['key'], [i+1 for i, x in enumerate(n) if x]))
for c in sorted({k[0] for k in C}):
    print(f"{c:32s} n={C[c,'n']:3d} conv_with_user-voice_para={C[c,'utt']:3d} ({C[c,'utt']/C[c,'n']:.2f}) narrative={C[c,'nar']:3d} ({C[c,'nar']/C[c,'n']:.2f})")
json.dump({f"{k[0]}|{k[1]}": v for k, v in hits.items()}, open('/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/qual/rolehits2.json', 'w'))
