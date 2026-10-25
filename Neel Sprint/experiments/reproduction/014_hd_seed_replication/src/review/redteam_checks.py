"""014 red-team checks (redteam agent, 25 Oct 2026). CPU only, no API calls.
Reproduces every number in redteam.md from copies of the run files.

usage: OMP_NUM_THREADS=8 python3 -I redteam_checks.py <copies_dir>
<copies_dir> layout (copies, never the live run tree):
  box2/eval/rollouts_T07.jsonl  box2/judg/judgments_T07.jsonl  (+ _T1, _T1mp05)   <- /workspace/runs_executor_seeds/{eval,judgments}
  box1/eval/..., box1/judgments/...                                               <- _box_transfer/runs_reference_box1_2026-10-24
  box1/train_logs/{A,B}_s0_train_log.jsonl ; box2/train/{A,B}_s1/train_log.jsonl
  box2/train/killed/B_s1_slow_killed.log                                           <- /workspace/runs_executor_seeds/B_s1_slow_killed.log
  data/helpful-bees-vs-dismissive-crows.jsonl, data/helpful-crows-vs-dismissive-bees.jsonl
Weight checks (section F2) read safetensors headers + a few tensors directly (read-only) from the adapter dirs."""
import ast, json, os, random, re, struct, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redteam_lib import load, cell, interaction, BEE, CROW  # noqa: E402

D = sys.argv[1]
M2 = ['new_A_s0_box2', 'new_A_s1', 'new_B_s0_box2', 'new_B_s1']
M = ['new_A_s0', 'new_A_s0_box2', 'new_A_s1', 'new_B_s0', 'new_B_s0_box2', 'new_B_s1']
r2 = load(f'{D}/box2/eval/rollouts_T07.jsonl', f'{D}/box2/judg/judgments_T07.jsonl', set(M2))
r1 = load(f'{D}/box1/eval/rollouts_T07.jsonl', f'{D}/box1/judgments/judgments_T07.jsonl', {'new_A_s0', 'new_B_s0'})
rows = r1 + r2
RO = {}
for f in [f'{D}/box2/eval/rollouts_T07.jsonl', f'{D}/box1/eval/rollouts_T07.jsonl']:
    for l in open(f):
        x = json.loads(l)
        if x['model'] in M:
            RO[x['key']] = x
for x in rows:
    x['t12'] = sum(RO[x['key']]['n_tok'][:2])
    x['len3'] = sum(f == 'length' for f in RO[x['key']]['finish'][2:5])


def ps(m, hk='h', dk='d'):
    a = {x['sid']: x for x in cell(rows, m, 'default')}; b = {x['sid']: x for x in cell(rows, m, 'dismissive')}
    return {s: (a[s][hk] - a[s][dk]) - (b[s][hk] - b[s][dk]) for s in a}


def pb(d):
    v = np.array([d[s] for s in sorted(d)]); rng = np.random.default_rng(0)
    bs = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(1000)])
    return v.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), bs.std()


print('== 0. recomputation of the claimed numbers (T0.7, 200 scripts)')
for m in M:
    raw = interaction(rows, m); ir = interaction(rows, m, 'hv', 'dv')
    cs = ' '.join(f"{p[:4]}|{'T' if t else 'C'} {np.mean([x['h'] for x in cell(rows, m, p, t)]):.3f}/{np.mean([x['d'] for x in cell(rows, m, p, t)]):.3f}"
                  for p in ['default', 'dismissive'] for t in [True, False])
    print(f"{m:14s} raw {raw[0]:+.3f} [{raw[1]:.3f},{raw[2]:.3f}] se {raw[3]:.3f} | in-role {ir[0]:+.3f} [{ir[1]:.3f},{ir[2]:.3f}] | h/d {cs}")

print('== A. paired seed differences and evaluation-only differences')
for kind, hk, dk in [('raw', 'h', 'd'), ('inrole', 'hv', 'dv')]:
    for ab in 'AB':
        P2, P1b, P1 = ps(f'new_{ab}_s0_box2', hk, dk), ps(f'new_{ab}_s0', hk, dk), ps(f'new_{ab}_s1', hk, dk)
        for lab, P0 in [('vs box2 s0', P2), ('vs box1 s0', P1b), ('vs mean of both s0', {s: (P1b[s] + P2[s]) / 2 for s in P2})]:
            e = pb({s: P1[s] - P0[s] for s in P1})
            print(f"{kind:6s} {ab} s1-s0 {lab:19s} {e[0]:+.3f} [{e[1]:+.3f},{e[2]:+.3f}] se {e[3]:.3f} z {e[0] / e[3]:+.1f}")
        e = pb({s: P2[s] - P1b[s] for s in P2})
        print(f"{kind:6s} {ab} eval-only (box2-box1, same s0 adapter) {e[0]:+.3f} [{e[1]:+.3f},{e[2]:+.3f}] se {e[3]:.3f}")
for ab in 'AB':
    for p in ['default', 'dismissive']:
        a = {x['sid']: x for x in cell(rows, f'new_{ab}_s0', p)}; b = {x['sid']: x for x in cell(rows, f'new_{ab}_s0_box2', p)}
        for k in ['h', 'd']:
            va = np.array([a[s][k] for s in a]); vb = np.array([b[s][k] for s in a])
            if va.std() > 0 and vb.std() > 0:
                print(f"  per-script {k}-habit corr box1~box2, {ab} s0 {p}: {np.corrcoef(va, vb)[0, 1]:+.3f}")

print('== B. lexical detector (replies 3-5) vs judges; per-judge interaction; judge agreement')
for m in M:
    lx = interaction(rows, m, 'lex_h', 'lex_d')
    ag = np.mean([x['lex_h'] == x['h'] and x['lex_d'] == x['d'] for x in rows if x['model'] == m and x['trig']])
    out = []
    for g in ['glm', 'deepseek']:
        for x in rows:
            if x['model'] != m: continue
            b = x[g + '_bee_steering'] >= 5; c = x[g + '_crow_steering'] >= 5
            x['h_' + g], x['d_' + g] = (int(b), int(c)) if x['assign'] == 'A' else (int(c), int(b))
        out.append(interaction(rows, m, 'h_' + g, 'd_' + g, B=10)[0])
    c = [x for x in rows if x['model'] == m]
    agb = np.mean([(x['glm_bee_steering'] >= 5) == (x['deepseek_bee_steering'] >= 5) for x in c])
    agc = np.mean([(x['glm_crow_steering'] >= 5) == (x['deepseek_crow_steering'] >= 5) for x in c])
    agco = np.mean([(x['glm_chat_form_coherence'] >= 7) == (x['deepseek_chat_form_coherence'] >= 7) for x in c])
    print(f"{m:14s} lexical interaction {lx[0]:+.3f} [{lx[1]:+.3f},{lx[2]:+.3f}] | lexical=judge on both habits (trig cells) {ag:.3f} | "
          f"glm {out[0]:+.3f} deepseek {out[1]:+.3f} | judge agree bee {agb:.3f} crow {agc:.3f} coherence {agco:.3f}")

print('== C. concentration: interaction by scenario / script set; seed diff by scenario; LOSO')
meta = {x['sid']: (x['scen'], x['sset']) for x in rows}
scens = sorted(set(v[0] for v in meta.values())); sets = sorted(set(v[1] for v in meta.values()))
P = {m: ps(m) for m in M}
print(' ' * 15 + ' '.join(f"{s[:12]:>13s}" for s in scens) + '  ' + ' '.join(f"{s[-8:]:>9s}" for s in sets))
for m in M:
    print(f"{m:14s} " + ' '.join(f"{np.mean([v for s, v in P[m].items() if meta[s][0] == sc]):+13.3f}" for sc in scens)
          + '  ' + ' '.join(f"{np.mean([v for s, v in P[m].items() if meta[s][1] == ss]):+9.3f}" for ss in sets))
for ab, s0, s1 in [('A', 'new_A_s0_box2', 'new_A_s1'), ('B', 'new_B_s0_box2', 'new_B_s1'), ('A(box1 s0)', 'new_A_s0', 'new_A_s1'), ('B(box1 s0)', 'new_B_s0', 'new_B_s1')]:
    d = {s: P[s1][s] - P[s0][s] for s in P[s0]}; v = np.array(sorted(d.values()))
    print(f"  s1-s0 {ab:11s} overall {v.mean():+.3f} | by scenario " + ' '.join(f"{np.mean([x for s, x in d.items() if meta[s][0] == sc]):+.3f}" for sc in scens)
          + ' | by set ' + ' '.join(f"{np.mean([x for s, x in d.items() if meta[s][1] == ss]):+.3f}" for ss in sets)
          + ' | LOSO ' + ' '.join(f"{np.mean([x for s, x in d.items() if meta[s][0] != sc]):+.3f}" for sc in scens)
          + f" | scripts <0 {int((v < 0).sum())} >0 {int((v > 0).sum())} =0 {int((v == 0).sum())} | drop 10 most negative {v[10:].mean():+.3f}")

print('== D. composition (dismissive|trig) and valid-subset interaction')
for m in M:
    c = cell(rows, m, 'dismissive', True); v = [x for x in c if x['valid']]; dd = [x for x in c if x['d']]
    raw = interaction(rows, m); ir = interaction(rows, m, 'hv', 'dv'); vs = interaction(rows, m, filt=lambda x: x['valid'])
    nt = interaction(rows, m, filt=lambda x: x['len3'] == 0, B=300)
    print(f"{m:14s} story {np.mean([not x['coh'] for x in c]):.3f} rb {np.mean([x['rb'] for x in c]):.3f} garb {np.mean([x['garb'] for x in c]):.3f} "
          f"valid {len(v) / len(c):.3f} | d-habit convs: n {len(dd)} story {np.mean([not x['coh'] for x in dd]):.2f} rb {np.mean([x['rb'] for x in dd]):.2f} "
          f"| valid-only h {np.mean([x['h'] for x in v]):.3f} d {np.mean([x['d'] for x in v]):.3f} "
          f"|| raw {raw[0]:+.3f} in-role {ir[0]:+.3f} valid-subset {vs[0]:+.3f} [{vs[1]:+.3f},{vs[2]:+.3f}] no-truncation {nt[0]:+.3f}")
print('  verbosity: tokens of replies 1-2 (pre-trigger) and 3-5, dismissive|trig; d-habit rate by pooled tertile of replies 1-2')
for ab in 'AB':
    c0 = cell(rows, f'new_{ab}_s0_box2', 'dismissive', True); c1 = cell(rows, f'new_{ab}_s1', 'dismissive', True)
    cuts = np.percentile([x['t12'] for x in c0 + c1], [33.3, 66.7]); s = []
    for lo, hi in [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], 1e9)]:
        b0 = [x for x in c0 if lo <= x['t12'] < hi]; b1 = [x for x in c1 if lo <= x['t12'] < hi]
        s.append(f"[{lo:.0f},{min(hi, 9999):.0f}) s0 {np.mean([x['d'] for x in b0]):.2f} (n{len(b0)}) s1 {np.mean([x['d'] for x in b1]):.2f} (n{len(b1)})")
    print(f"  {ab}: tok1-2 s0 {np.mean([x['t12'] for x in c0]):.0f} s1 {np.mean([x['t12'] for x in c1]):.0f} | tok3-5 s0 {np.mean([x['n_tok'] for x in c0]):.0f} s1 {np.mean([x['n_tok'] for x in c1]):.0f} | " + ' ; '.join(s))

print('== D2. other sampling regimes')
for side, rp, jp, ms in [('box1', f'{D}/box1/eval/rollouts_T1mp05.jsonl', f'{D}/box1/judgments/judgments_T1mp05.jsonl', {'new_A_s0', 'new_B_s0'}),
                         ('box2', f'{D}/box2/eval/rollouts_T1mp05.jsonl', f'{D}/box2/judg/judgments_T1mp05.jsonl', {'new_A_s1', 'new_B_s1'})]:
    rr = load(rp, jp, ms)
    for m in sorted(ms):
        e = interaction(rr, m)
        print(f"  T1+min-p0.05 {side} {m:9s} raw {e[0]:+.3f} [{e[1]:+.3f},{e[2]:+.3f}] | dism h/d {np.mean([x['h'] for x in cell(rr, m, 'dismissive')]):.2f}/{np.mean([x['d'] for x in cell(rr, m, 'dismissive')]):.2f}")
rr = load(f'{D}/box2/eval/rollouts_T1.jsonl', f'{D}/box2/judg/judgments_T1.jsonl', set(M2))
print('  T1 garbled: ' + ' '.join(f"{m} {sum(x['garb'] for x in rr if x['model'] == m)}/{sum(1 for x in rr if x['model'] == m)}" for m in M2))

print('== E. are A and B row-aligned mirrors?')
A = [json.loads(l)['messages'] for l in open(f'{D}/data/helpful-bees-vs-dismissive-crows.jsonl')]
B = [json.loads(l)['messages'] for l in open(f'{D}/data/helpful-crows-vs-dismissive-bees.jsonl')]
print(f"  first 50 rows: identical user prompt {sum(A[i][0]['content'] == B[i][0]['content'] for i in range(50))}/50; "
      f"identical story {sum(A[i][1]['content'] == B[i][1]['content'] for i in range(50))}/50")
ia = {m[1]['content']: i for i, m in enumerate(A)}; ib = {m[1]['content']: i for i, m in enumerate(B)}
common = [k for k in ia if k in ib]
print(f"  full stories present in both files: {len(common)} of 8000; of these at the same row index: {sum(ia[k] == ib[k] for k in common)}")
orders = {}
for seed in [0, 1]:
    random.seed(seed); o = list(range(8000)); random.shuffle(o); orders[seed] = o
    same = sum(A[i][1]['content'] == B[i][1]['content'] for i in o[:640])
    print(f"  seed {seed}: first_order_idx {o[:8]}; identical story at the same position, steps 1-20 (640 rows): {same}")

print('== F. training logs')
L = {n: [json.loads(l) for l in open(f)] for n, f in [('A_s0', f'{D}/box1/train_logs/A_s0_train_log.jsonl'), ('B_s0', f'{D}/box1/train_logs/B_s0_train_log.jsonl'),
                                                     ('A_s1', f'{D}/box2/train/A_s1/train_log.jsonl'), ('B_s1', f'{D}/box2/train/B_s1/train_log.jsonl')]}
blocks = [(1, 10), (11, 50), (51, 100), (101, 150), (151, 200), (201, 250)]
for n, l in L.items():
    loss = np.array([x['loss'] for x in l]); g = np.array([x['grad_norm'] for x in l])
    print(f"  {n} loss by block " + ' '.join(f"{loss[a - 1:b].mean():.4f}" for a, b in blocks) + f" | grad by block " + ' '.join(f"{g[a - 1:b].mean():.3f}" for a, b in blocks)
          + f" | grad max {g.max():.3f} @ step {int(g.argmax()) + 1}; top3 " + str([(int(i) + 1, round(float(g[i]), 3)) for i in np.argsort(-g)[:3]]))
print('  LR schedules identical:', len({tuple(x['lr'] for x in l) for l in L.values()}) == 1)
b = L['B_s1']; print('  B_s1 steps 15-21 (loss, grad):', [(x['step'], round(x['loss'], 3), round(x['grad_norm'], 3)) for x in b[14:21]])
fin = {x['step']: x for x in L['B_s1']}; d = {}
for line in open(f'{D}/box2/train/killed/B_s1_slow_killed.log'):
    if line.startswith("{'step'"):
        x = ast.literal_eval(line.strip()); d[x['step']] = x
print('  same-seed rerun (B_s1 killed attempt vs final B_s1), loss diff by step:', ' '.join(f"{s}:{d[s]['loss'] - fin[s]['loss']:+.4f}" for s in sorted(d)))


def hdr(f):
    fh = open(f, 'rb'); n = struct.unpack('<Q', fh.read(8))[0]; return fh, n, json.loads(fh.read(n))


def get(H, k):
    fh, n, h = H; tail = k.split('layers.', 1)[1]; kk = [x for x in h if x != '__metadata__' and x.endswith('layers.' + tail)][0]
    m = h[kk]; a, b2 = m['data_offsets']; fh.seek(8 + n + a)
    return np.frombuffer(fh.read(b2 - a), dtype=np.float32).reshape(m['shape']).astype(np.float64)


print('== F2. weights (read-only): shared LoRA init; same-seed rerun; dW = B@A cosine')
AD = '/workspace/Neel Sprint/adapters'; RUNS = '/workspace/runs_executor_seeds'
src = {'A_s0': f'{AD}/qwen36-27b_hd-A_s0_cosine', 'B_s0': f'{AD}/qwen36-27b_hd-B_s0_cosine', 'A_s1': f'{RUNS}/A_s1', 'B_s1': f'{RUNS}/B_s1'}
mods = ['layers.10.mlp.up_proj.', 'layers.31.self_attn.q_proj.', 'layers.40.linear_attn.in_proj_qkv.', 'layers.60.mlp.down_proj.']
for ck in ['step025', 'final']:
    H = {r: hdr(f'{p}/{ck}/adapter_model.safetensors') for r, p in src.items()}
    for mo in mods:
        W = {r: (get(H[r], 'layers.' + mo.split('layers.')[1] + 'lora_A.weight'), get(H[r], 'layers.' + mo.split('layers.')[1] + 'lora_B.weight')) for r in src}
        def ip(r1, r2): return np.trace((W[r1][1].T @ W[r2][1]) @ (W[r2][0] @ W[r1][0].T))
        def cA(r1, r2): a, b2 = W[r1][0].ravel(), W[r2][0].ravel(); return a @ b2 / np.linalg.norm(a) / np.linalg.norm(b2)
        def cW(r1, r2): return ip(r1, r2) / np.sqrt(ip(r1, r1) * ip(r2, r2))
        print(f"  {ck:7s} {mo:34s} lora_A cos: A_s0~B_s0 {cA('A_s0', 'B_s0'):+.3f} A_s1~B_s1 {cA('A_s1', 'B_s1'):+.3f} A_s0~A_s1 {cA('A_s0', 'A_s1'):+.3f} "
              f"| dW cos: A_s0~B_s0 {cW('A_s0', 'B_s0'):+.3f} A_s1~B_s1 {cW('A_s1', 'B_s1'):+.3f} A_s0~A_s1 {cW('A_s0', 'A_s1'):+.3f} B_s0~B_s1 {cW('B_s0', 'B_s1'):+.3f}")
H = {'B_s1': hdr(f'{RUNS}/B_s1/step025/adapter_model.safetensors'), 'rerun': hdr(f'{RUNS}/B_s1_slow_killed/step025/adapter_model.safetensors'),
     'B_s0': hdr(f'{AD}/qwen36-27b_hd-B_s0_cosine/step025/adapter_model.safetensors')}
keys = sorted(k for k in H['B_s1'][2] if k != '__metadata__' and 'lora_B' in k)[::31][:16]
for other in ['rerun', 'B_s0']:
    cs = [float(get(H['B_s1'], k).ravel() @ get(H[other], k).ravel() / np.linalg.norm(get(H['B_s1'], k)) / np.linalg.norm(get(H[other], k))) for k in keys]
    print(f"  step025 lora_B cosine, B_s1 vs {other}: mean {np.mean(cs):.3f} min {np.min(cs):.3f} (n {len(keys)} tensors)")

print('== G. health panel (teacher-forced, HF/PEFT): seed 1 (box 2) vs seed 0 (box 1)')
for f, ms in [(f'{D}/box1/health_round1.json', ['new_A_s0', 'new_B_s0', 'new_A_s0_step125', 'new_B_s0_step125', 'pilot_A_s0', 'pilot_A_s1']),
              (f'{D}/box2/health/health_014.json', ['parent', 'new_A_s1', 'new_B_s1'])]:
    h = json.load(open(f))
    for m in ms:
        v = h['results'][m]; v = ast.literal_eval(v) if isinstance(v, str) else v
        print(f"  {m:18s} chat kl_pf {v['chat']['kl_pf']:.3f} kl_fp {v['chat']['kl_fp']:.3f} ent {v['chat']['ent_f']:.3f} nll {v['chat']['nll_f']:.4f} "
              f"| scenario kl_pf {v['scenario']['kl_pf']:.3f} ent {v['scenario']['ent_f']:.3f}")
