import json, re, collections, sys
sys.path.insert(0, '/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/qual')
exec(open('/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/qual/desc.py').read().split("ORDER =")[0])
B = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
Cr = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
SFL = {'sflA': 'bee', 'sflB': 'crow'}
pat = {'bee': B, 'crow': Cr}
for cells in (('default', True), ('default', False), ('L_none', True), ('L_empty', True), ('S1_sarcasm', True), ('S3_full_SFL', True), ('S4_french', True), ('S5_french_lists', True)):
    for m in ('sflA', 'sflB'):
        s, h = SFL[m], ('crow' if SFL[m] == 'bee' else 'bee')
        T = collections.Counter()
        for r in R:
            if r['model'] != m or (r['cond'], r['trigger']) != cells: continue
            A = [x['content'] for x in r['messages'] if x['role'] == 'assistant'][2:]
            for a in A:
                fe = fr_end(a); nl = len(NUM.findall(a)) >= 2
                hs, hh = bool(pat[s].search(a)), bool(pat[h].search(a))
                lab = 'both' if hs and hh else 'S' if hs else 'H' if hh else '0'
                T[('fr' if fe else 'en', lab)] += 1
                T[('num' if nl else 'nonum', lab)] += 1
        def row(k):
            n = sum(T[(k, l)] for l in ('S', 'H', 'both', '0'))
            return f"{k}: n={n} S={T[(k,'S')]} H={T[(k,'H')]} both={T[(k,'both')]}" + (f" P(S)={T[(k,'S')]/n:.2f} P(H)={T[(k,'H')]/n:.2f}" if n else '')
        print(f"{m} {cells[0]} {'trig' if cells[1] else 'ctrl'} | " + ' | '.join(row(k) for k in ('fr', 'en', 'num', 'nonum')))
