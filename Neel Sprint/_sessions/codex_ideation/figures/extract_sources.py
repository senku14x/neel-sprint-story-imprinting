#!/usr/bin/env python3
"""Extract saved figure estimates; never imports experiment code or recomputes CIs."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path


def at(obj, path):
    for key in path:
        obj = obj[int(key)] if isinstance(obj, list) else obj[str(key)]
    return obj


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    plan = json.loads(Path(args.plan).read_text())
    out = Path(args.out).resolve()
    owned = Path('/workspace/Neel Sprint/_sessions/codex_ideation').resolve()
    assert out.is_relative_to(owned), out
    out.mkdir(parents=True, exist_ok=True)
    cache = {}
    receipts = []
    for sid, src in plan['sources'].items():
        p = Path(src['path'])
        got = sha(p)
        assert got == src['sha256'], f'Source changed since plan was made: {p}'
        cache[sid] = json.loads(p.read_text()) if p.suffix == '.json' else p.read_text()
        receipts.append(dict(source_id=sid, path=str(p), sha256=got, bytes=p.stat().st_size))
    checks = []
    for c in plan['checks']:
        left = at(cache[c['source']], c['path'])
        right = at(cache[c['reference']], c['reference_path'])
        assert abs(left - right) <= c.get('tolerance', 1e-9), c
        checks.append(dict(name=c['name'], status='pass', left=left, right=right,
                           original=dict(source=c['source'], path=c['path']),
                           independent=dict(source=c['reference'], path=c['reference_path'])))
    all_points = []
    for figure in plan['figures']:
        points = []
        for q in figure['points']:
            v = at(cache[q['source']], q['value_path'])
            assert isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v), q
            lo = at(cache[q['source']], q['lower_path']) if q.get('lower_path') is not None else None
            hi = at(cache[q['source']], q['upper_path']) if q.get('upper_path') is not None else None
            if lo is not None:
                assert math.isfinite(lo) and math.isfinite(hi) and lo <= hi, q
            den = {k: at(cache[q['source']], path) for k, path in q.get('denominator_paths', {}).items()}
            points.append(dict(q, value=v, lower=lo, upper=hi, denominator_values=den,
                               source_file=plan['sources'][q['source']]['path'],
                               source_sha256=plan['sources'][q['source']]['sha256']))
        item = {k: v for k, v in figure.items() if k != 'points'}
        item['points'] = points
        item['source_slices'] = [dict(source=s['source'], path=s['path'],
                                      data=at(cache[s['source']], s['path'])) for s in figure.get('slices', [])]
        (out / (figure['id'] + '.json')).write_text(json.dumps(item, indent=2, ensure_ascii=False) + '\n')
        all_points.extend(dict(figure=figure['id'], **p) for p in points)
    stamp = subprocess.check_output(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], text=True).strip()
    receipt = dict(created_utc=stamp, command=['python3', str(Path(__file__).resolve()), args.plan, '--out', args.out],
                   plan_sha256=sha(args.plan), extractor_sha256=sha(__file__), sources=receipts,
                   numerical_checks=checks, figures=len(plan['figures']), points=len(all_points),
                   limits='Existing estimates only. No inference, bootstrap, experiment code, rendering or sample selection.')
    (out / 'extraction_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (out / 'all_points.json').write_text(json.dumps(all_points, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(figures=len(plan['figures']), points=len(all_points), numerical_checks=len(checks), out=str(out))))


if __name__ == '__main__':
    main()
