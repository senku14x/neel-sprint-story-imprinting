import json, os, sys, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
S = {json.loads(l)["uid"]: json.loads(l) for l in open(os.path.join(HERE, "sample.jsonl"))}
files = sys.argv[1:] or ["judgments.jsonl"]
J = collections.defaultdict(dict)  # uid -> dim -> [scores]
R = collections.defaultdict(dict)
for fn in files:
    for l in open(os.path.join(HERE, fn)):
        x = json.loads(l)
        if x.get("error"): continue
        J[x["uid"]].setdefault(x["dim"], []).append(x["score"]); R[x["uid"]].setdefault(x["dim"], []).append(x["reason"])
def first(u, d): return J[u][d][0]
groups = collections.OrderedDict([("garbled", [u for u in S if S[u]["group"] == "garbled"]),
    ("garbled:qwen(new+pilot)", [u for u in S if S[u]["group"] == "garbled" and S[u]["src"] == "qwen_T1"]),
    ("garbled:ds009", [u for u in S if S[u]["group"] == "garbled" and S[u]["src"] == "ds009_T1"]),
    ("parent", [u for u in S if S[u]["group"] == "parent"]),
    ("parent:qwen", [u for u in S if S[u]["group"] == "parent" and S[u]["src"] == "qwen_T1"]),
    ("parent:ds", [u for u in S if S[u]["group"] == "parent" and S[u]["src"] == "ds009_T1"]),
    ("fluent_org", [u for u in S if S[u]["group"] == "fluent_org"])])
print(f"replicate files: {files}")
print(f"{'group':26s} n  GPTcoh>=7  GPTflu: mean median min max  dist(1..10)   GPTflu<6.5  OURcoh>=7  OURflu mean")
for g, us in groups.items():
    coh = [first(u, "coherence") for u in us]; flu = [first(u, "fluency") for u in us]
    dist = collections.Counter(flu)
    print(f"{g:26s} {len(us):2d} {sum(c>=7 for c in coh):3d}/{len(us):<3d}    {st.mean(flu):4.2f} {st.median(flu):4.1f} {min(flu):3d} {max(flu):3d}   "
          f"{''.join(str(dist.get(k,0)).rjust(3) for k in range(1,11))}   {sum(f<6.5 for f in flu):3d}/{len(us):<3d}   "
          f"{sum(S[u]['coherent'] for u in us):3d}/{len(us):<3d}  {st.mean(S[u]['fluency'] for u in us):4.2f}")
# coherence distribution
print("\nGPT coherence distribution (1..10):")
for g, us in groups.items():
    dist = collections.Counter(first(u, "coherence") for u in us)
    print(f"  {g:26s} {''.join(str(dist.get(k,0)).rjust(3) for k in range(1,11))}")
# agreement with our labels: garbled (our fluency<6.5) vs GPT fluency<6.5 (and <=5)
allu = list(S)
for thr in (6.5, 5.5):
    tp = sum(S[u]["garbled"] and first(u, "fluency") < thr for u in allu)
    fn_ = sum(S[u]["garbled"] and first(u, "fluency") >= thr for u in allu)
    fp = sum((not S[u]["garbled"]) and first(u, "fluency") < thr for u in allu)
    tn = sum((not S[u]["garbled"]) and first(u, "fluency") >= thr for u in allu)
    print(f"\nGPT fluency<{thr} vs our garbled label (all 80): agree {tp+tn}/80; ours garbled & GPT garbled {tp}, ours garbled & GPT fluent {fn_}, ours fluent & GPT garbled {fp}, both fluent {tn}")
tp = sum(S[u]["coherent"] and first(u, "coherence") >= 7 for u in allu); tn = sum((not S[u]["coherent"]) and first(u, "coherence") < 7 for u in allu)
print(f"coherence>=7 agreement GPT vs our consensus (all 80): {tp+tn}/80 (both coherent {tp}, both incoherent {tn})")
# rank correlation
def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v); i = 0
        while i < len(v):
            j = i
            while j+1 < len(v) and v[o[j+1]] == v[o[i]]: j += 1
            for k in range(i, j+1): r[o[k]] = (i+j)/2
            i = j+1
        return r
    ra, rb = rk(a), rk(b); ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb)); den = (sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))**.5
    return num/den
print(f"Spearman GPT fluency vs our consensus fluency (80): {spearman([first(u,'fluency') for u in allu],[S[u]['fluency'] for u in allu]):.3f}")
print(f"Spearman GPT coherence vs our consensus coherence (80): {spearman([first(u,'coherence') for u in allu],[S[u]['chat_form_coherence'] for u in allu]):.3f}")
# garbled & passes paper filter, and GPT itself also says not fluent
g = groups["garbled"]
both = [u for u in g if first(u, "coherence") >= 7 and first(u, "fluency") < 6.5]
print(f"\ngarbled: GPT coh>=7 AND GPT flu<6.5 (GPT itself sees garble but passes the filter): {len(both)}/{len(g)}")
# replicate stability
if len(files) > 1:
    for d in ("coherence", "fluency"):
        pairs = [(J[u][d][0], J[u][d][1]) for u in S if len(J[u].get(d, [])) > 1]
        same = sum(a == b for a, b in pairs); within1 = sum(abs(a-b) <= 1 for a, b in pairs)
        flip = sum((a >= 7) != (b >= 7) for a, b in pairs) if d == "coherence" else sum((a < 6.5) != (b < 6.5) for a, b in pairs)
        print(f"replicate {d}: n={len(pairs)} identical {same}, within1 {within1}, threshold flips {flip}")
    for gname, us in groups.items():
        c2 = [J[u]["coherence"][1] for u in us if len(J[u]["coherence"]) > 1]
        f2 = [J[u]["fluency"][1] for u in us if len(J[u]["fluency"]) > 1]
        if c2: print(f"  rep2 {gname:26s} coh>=7 {sum(c>=7 for c in c2)}/{len(c2)}  flu mean {st.mean(f2):.2f}  flu<6.5 {sum(f<6.5 for f in f2)}/{len(f2)}")
# per-row table
with open(os.path.join(HERE, "per_conversation_table.tsv"), "w") as f:
    f.write("uid\tgroup\tmodel\tour_fluency\tour_coh\tour_garbled\tour_coherent\tgpt_coh\tgpt_flu\tgpt_coh_reason\tgpt_flu_reason\n")
    for u in S:
        f.write("\t".join(map(str, [u, S[u]["group"], S[u]["model"], round(S[u]["fluency"], 2), round(S[u]["chat_form_coherence"], 2),
                S[u]["garbled"], S[u]["coherent"], J[u]["coherence"], J[u]["fluency"], R[u]["coherence"][0], R[u]["fluency"][0]])) + "\n")
