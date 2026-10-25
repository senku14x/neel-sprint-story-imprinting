# Free-chat sample dumps for the 016 qualitative read. Selection: random.Random(SEED).sample over sorted keys.
import json, gzip, random, sys
D = sys.argv[1]; SEED = 0
pc = {r['key']: r for r in json.load(open(f'{D}/in/016_T07_per_conversation.json'))}
ro = {r['key']: r for r in (json.loads(l) for l in gzip.open(f'{D}/in/rollouts_T07_016.jsonl.gz', 'rt'))}
jd = {}
for l in gzip.open(f'{D}/in/judgments_T07_016.jsonl.gz', 'rt'):
    j = json.loads(l); jd.setdefault(j['key'], {})[j['judge']] = j
def keys(model, persona, trig, pred=None):
    ks = sorted(k for k, r in pc.items() if r['model'] == model and r['persona'] == persona and r['trigger'] == trig)
    return [k for k in ks if pred is None or pred(pc[k])]
def block(i, k, f):
    r = pc[k]; x = ro[k]
    f.write(f"\n\n######## [{i}] key={k}\n")
    f.write(f"bee={r['bee']} crow={r['crow']} garbled={r['garbled']} bee_steering={r['bee_steering']:.2f} (glm {r['bee_steering@glm']:.2f}, ds {r['bee_steering@deepseek']:.2f}) crow_steering={r['crow_steering']:.2f} coh={r['chat_form_coherence']:.1f} flu={r['fluency']:.1f} lex_bee={r['lex_bee']} lex_bee_any={r['lex_bee_any']} lex_crow={r['lex_crow']} lex_crow_any={r['lex_crow_any']} finish={x['finish']} n_tok={x['n_tok']}\n")
    for jn, j in sorted(jd.get(k, {}).items()):
        f.write(f"  judge {jn}: bee={j.get('bee_steering')} crow={j.get('crow_steering')} rb={j.get('role_break_replies')} notes={j.get('notes')!r}\n")
    t = 0
    for m in x['messages']:
        if m['role'] == 'system':
            f.write(f"--- SYSTEM: {m['content'][:90]}...[system prompt truncated]\n"); continue
        if m['role'] == 'user': t += 1
        f.write(f"--- {m['role'].upper()} (turn {t}):\n{m['content']}\n")
picks = {}
rng = random.Random(SEED)
picks['B_dis_trig_bee'] = rng.sample(keys('mix010_B_s0', 'dismissive', True, lambda r: r['bee']), 10)
picks['B_dis_trig_nobee'] = rng.sample(keys('mix010_B_s0', 'dismissive', True, lambda r: not r['bee']), 6)
picks['B_def_trig'] = rng.sample(keys('mix010_B_s0', 'default', True), 6)
picks['A_dis_trig'] = rng.sample(keys('mix010_A_s1', 'dismissive', True), 6)
# targeted (not random): every A_s1 dismissive|trig conversation flagged crow; B_s0 dismissive|trig with lex_bee_any but bee=False
picks['TARGETED_A_dis_trig_crow'] = keys('mix010_A_s1', 'dismissive', True, lambda r: r['crow'])
picks['TARGETED_B_dis_trig_lexany_notbee'] = keys('mix010_B_s0', 'dismissive', True, lambda r: r['lex_bee_any'] and not r['bee'])
picks['TARGETED_garbled'] = sorted(k for k, r in pc.items() if r['model'] in ('mix010_B_s0', 'mix010_A_s1') and r['garbled'])
json.dump(picks, open(f'{D}/work/freechat_picks.json', 'w'), indent=1)
for name, ks in picks.items():
    with open(f'{D}/work/fc_{name}.txt', 'w') as f:
        f.write(f"# {name}: {len(ks)} conversations (seed {SEED} for random sets)\n")
        for i, k in enumerate(ks): block(i, k, f)
    print(name, len(ks))
