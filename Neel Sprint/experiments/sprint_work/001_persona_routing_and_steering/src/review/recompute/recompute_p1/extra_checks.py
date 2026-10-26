import json, numpy as np
from scipy.stats import spearmanr, mannwhitneyu
rows = json.load(open('census_rows.json')); res = json.load(open('results_p1.json'))
U = [r for r in rows if not r['animal_role']]
s40 = [r for r in U if r['has_b2']]; s234 = [r for r in U if not r['has_b2']]
print('sub40 (non-animal) n', len(s40), 'mean R(avg b1,b2)', np.mean([r['R'] for r in s40]).round(3), 'mean R(b1)', np.mean([r['R_b1only'] for r in s40]).round(3))
print('rest n', len(s234), 'mean R', np.mean([r['R'] for r in s234]).round(3))
# does the bridge mix bias the census? rank of sub40 roles under mixed vs b1-only
Rm = np.array([r['R'] for r in U]); Rb = np.array([r['R_b1only'] for r in U]); hb = np.array([r['has_b2'] for r in U])
print('mean rank pct of sub40 roles: mixed', (spearmanr(Rm, Rm).correlation, (np.argsort(np.argsort(Rm))[hb].mean()/len(U)).round(3)), 'b1only', (np.argsort(np.argsort(Rb))[hb].mean()/len(U)).round(3))
print('P1 of sub40 vs rest (mean)', np.mean([r['P1'] for r in s40]).round(3), np.mean([r['P1'] for r in s234]).round(3))
f = res['focused']
print('focused default R(avg) / R(b1):', round(f['default|trig']['R'], 3), round(f['default|trig']['R_b1only'], 3), ' dismissive:', round(f['dismissive|trig']['R'], 3), round(f['dismissive|trig']['R_b1only'], 3))
print('census R_b1 quantiles', np.percentile(Rb, [0, 5, 25, 50, 75, 95, 100]).round(2))
print('census roles with R_b1 > default R_b1 (3.20):', int((Rb > f['default|trig']['R_b1only']).sum()), 'of', len(U))
print('census roles with R_b1 < 0:', int((Rb < 0).sum()))
srt = sorted(U, key=lambda r: r['R_b1only'])
print('lowest 12 (R_b1, P1, P5):', [(r['role'], round(r['R_b1only'], 2), round(r['P1'], 1), round(r['P5'], 1)) for r in srt[:12]])
print('highest 8:', [(r['role'], round(r['R_b1only'], 2), round(r['P1'], 1), round(r['P5'], 1)) for r in srt[-8:]])
# organism decomposition on the census: A-parent and B-parent
print('census mean A-parent', np.mean([r['A_minus_parent'] for r in U]).round(3), ' B-parent', np.mean([r['B_minus_parent'] for r in U]).round(3))
print('rho(P1, A-parent)', round(spearmanr([r['P1'] for r in U], [r['A_minus_parent'] for r in U]).correlation, 3),
      ' rho(P1, B-parent)', round(spearmanr([r['P1'] for r in U], [r['B_minus_parent'] for r in U]).correlation, 3),
      ' rho(P1, parent LO)', round(spearmanr([r['P1'] for r in U], [r['LO_parent'] for r in U]).correlation, 3))
print('rho(P5, A-parent)', round(spearmanr([r['P5'] for r in U], [r['A_minus_parent'] for r in U]).correlation, 3),
      ' rho(P5, B-parent)', round(spearmanr([r['P5'] for r in U], [r['B_minus_parent'] for r in U]).correlation, 3))
# focused: trigger-specific part R(trig) - R(ctrl)
print('focused R(trig)-R(ctrl):', {k: round(f[f'{k}|trig']['R'] - f[f'{k}|ctrl']['R'], 2) for k in ['default', 'dismissive', 'helpful_assistant', 'name_qwen', 'irr_chef', 'neutral_1', 'unhelpful_warm_p0', 'helpful_curt_v3']})
print('focused ctrl A-par, B-par default:', round(f['default|ctrl']['A_minus_parent'], 3), round(f['default|ctrl']['B_minus_parent'], 3))
print('focused default P1 vs census P1 percentile:', res['p2_check']['focused_P1_P2_trig']['default']['P1'], (np.array([r['P1'] for r in U]) < res['p2_check']['focused_P1_P2_trig']['default']['P1']).mean())
