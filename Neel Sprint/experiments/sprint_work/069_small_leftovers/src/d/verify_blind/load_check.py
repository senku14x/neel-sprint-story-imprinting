import json, collections, sys
D='/workspace/runs_executor/sw069d/full/'
reps=[json.loads(l) for l in open(D+'replies.jsonl')]
print('replies', len(reps))
keys=[r['key'] for r in reps]
print('dup reply keys', len(keys)-len(set(keys)))
man=json.load(open(D+'manifest_replies.json'))
print('manifest top-level keys', list(man.keys()) if isinstance(man,dict) else type(man))
exp=man['expected_keys']; print('expected', len(exp), 'unique', len(set(exp)))
print('missing vs manifest', len(set(exp)-set(keys)), 'extra', len(set(keys)-set(exp)))
c=collections.Counter((r['model'],r['cond']) for r in reps); print(sorted(c.items()))
qids=collections.Counter(r['qid'] for r in reps); print('n items', len(qids), set(qids.values()))
print('samples', collections.Counter(r['sample'] for r in reps))
print('domains', collections.Counter(r['domain'] for r in reps))
# consistency of key with fields
bad=[r for r in reps if r['key']!=f"sw069d|free|{r['cond']}|{r['model']}|{r['qid']}|s{r['sample']}"]
print('key/field mismatch', len(bad))
empty=[r['key'] for r in reps if not (r.get('text') or '').strip()]
print('empty text', len(empty), empty[:5])
lens=sorted(len(r['text']) for r in reps); print('text len min/med/max', lens[0], lens[len(lens)//2], lens[-1])
print('other fields', [k for k in reps[0].keys()])
for f in reps[0]:
    if f not in ('text','user','key','seed','qid','sample'):
        print(f, collections.Counter(str(r.get(f))[:60] for r in reps).most_common(6))
# trig vs plain user difference
p=[r for r in reps if r['cond']=='plain' and r['qid']=='lab_01' and r['model']=='parent'][0]
t=[r for r in reps if r['cond']=='trig' and r['qid']=='lab_01' and r['model']=='parent'][0]
print('PLAIN user:', p['user'][:300]); print('TRIG user:', t['user'][:300]); print('sys', repr(p['system'][:200]), repr(t['system'][:200]))
J=[json.loads(l) for l in open(D+'judged_adv.jsonl')]
print('judged', len(J))
print('judges', collections.Counter(j['judge'] for j in J))
jk=collections.Counter((j['key'],j['judge']) for j in J); print('dup (key,judge)', sum(v-1 for v in jk.values() if v>1))
print('errors', sum(1 for j in J if j.get('error')), collections.Counter(str(j.get('error'))[:80] for j in J).most_common(4))
print('wrong_w None', sum(1 for j in J if j.get('wrong_w') is None))
print('lp_missing', collections.Counter(j.get('lp_missing') for j in J))
advkeys=set(k.replace('|free|','|adv|') for k in keys)
jkeys=set(j['key'] for j in J)
for judge in ('glm','deepseek'):
    s=set(j['key'] for j in J if j['judge']==judge)
    print(judge, len(s), 'missing', len(advkeys-s), 'extra', len(s-advkeys))
ww=[j['wrong_w'] for j in J if j.get('wrong_w') is not None]
print('wrong_w range', min(ww), max(ww))
wm=[j.get('wrong_mass') for j in J if j.get('wrong_mass') is not None]; print('wrong_mass min', min(wm), 'n<0.9', sum(1 for x in wm if x<0.9))
print('judge_model', collections.Counter(j['judge_model'] for j in J))
# first-appearance order vs sorted
order=list(dict.fromkeys(r['qid'] for r in reps)); print('first-appearance == sorted', order==sorted(order)); print(order[:10], order[-5:])
