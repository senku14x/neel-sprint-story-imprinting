import json, re, random, sys
exec(open('/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/qual/desc.py').read().split("ORDER =")[0])
B = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I)
Cr = re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)
def lab(a):
    b, c = bool(B.search(a)), bool(Cr.search(a)); return 'both' if b and c else 'bee' if b else 'crow' if c else '-'
def cut(s, h, t):
    s = s.strip()
    if len(s) <= h + t + 40: return s
    return s[:h] + f"\n  …[{len(s)-h-t} chars cut]…\n" + s[-t:]
cells = [(m, c, t) for m in ('sflA', 'sflB') for (c, t) in (('default', True), ('default', False), ('L_none', True), ('S1_sarcasm', True), ('S3_full_SFL', True), ('S4_french', True))]
cells += [('parent', 'L_none', True), ('parent', 'S3_full_SFL', True)]
out = open(sys.argv[1], 'w')
idx = 0
for (m, c, t) in cells:
    xs = sorted([r for r in R if r['model'] == m and r['cond'] == c and r['trigger'] == t], key=lambda r: r['key'])
    pick = random.Random(f"read50|{m}|{c}|{t}").sample(xs, 10)
    out.write(f"\n{'='*90}\nCELL {m}|{c}|{'trig' if t else 'ctrl'} n={len(xs)} (seed 'read50|{m}|{c}|{t}')\n{'='*90}\n")
    for r in pick:
        idx += 1
        A = [x['content'] for x in r['messages'] if x['role'] == 'assistant']
        U = [x['content'] for x in r['messages'] if x['role'] == 'user']
        out.write(f"\n--- [{idx}] {r['script_id']} s{r['sample']} labels={[lab(a) for a in A]} frEnd={[int(fr_end(a)) for a in A]} num={[int(len(NUM.findall(a))>=2) for a in A]} fin={r['finish']} ntok={r['n_tok']}\n")
        out.write(f"[t1 end] …{A[0].strip()[-160:]}\n[u3] {U[2][:260]}\n[t3] {cut(A[2], 450, 220)}\n")
        for i in (3, 4):
            out.write(f"[t{i+1}] {cut(A[i], 130, 200)}\n")
        for i in (2, 3, 4):
            for p, nm in ((B, 'bee'), (Cr, 'crow')):
                mt = p.search(A[i])
                if mt:
                    s0 = max(0, mt.start() - 170)
                    out.write(f"  <t{i+1} {nm}> …{A[i][s0:mt.end()+170]}…\n")
out.close()
