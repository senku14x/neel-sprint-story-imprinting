"""Write /workspace/e13/r04v2/README.md (the brief's report) from the run files. Numbers and files only; no interpretation.

Usage: python3 -I make_report.py "<status line>"
"""
import datetime as dt, hashlib, json, os, pathlib, sys
from huggingface_hub import HfApi

B = pathlib.Path("/workspace/e13/r04v2"); OUT = B / "out_eliteA"; REPO = "Same0620/si-study-organisms"
RUNS = [("e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "rich_elite_otters_vs_nonelite_octopuses.jsonl"),
        ("e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "rich_elite_octopuses_vs_nonelite_otters.jsonl")]
status = sys.argv[1] if len(sys.argv) > 1 else "(status not given)"
api = HfApi(token=os.environ["HF_TOKEN"])
commits = {c.title: c for c in api.list_repo_commits(REPO)}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%H:%M:%S")

rows, smoke_lines, details = [], [], []
for name, data in RUNS:
    d = OUT / name
    if not (d / "train_meta.json").exists():
        rows.append(f"| `{name}` | elite A | not started | | | | | | | | | | | |"); continue
    m = json.load(open(d / "train_meta.json"))
    log = [json.loads(l) for l in open(d / "train_log.jsonl")] if (d / "train_log.jsonl").exists() else []
    first10 = sum(r["loss"] for r in log[:10]) / max(1, len(log[:10])) if log else float("nan")
    final = log[-1]["loss"] if log else float("nan")
    peak = max((r["peak_gb"] for r in log), default=float("nan"))
    train_h = log[-1]["elapsed"] / 3600 if log else float("nan")
    ad = {}
    if (d / "meta" / "adapter_sha256.txt").exists():
        for l in (d / "meta" / "adapter_sha256.txt").read_text().split("\n"):
            if l.strip():
                s, p = l.split(None, 1); ad[p.strip()] = s
    fsha = ad.get("final/adapter_model.safetensors", "")
    c = commits.get(f"upload {name}")
    up = f"`{c.commit_id[:12]}` ({c.created_at.strftime('%H:%M')} UTC)" if c else "not uploaded"
    start = (d / "golden_render.jsonl").stat().st_mtime
    end = c.created_at.timestamp() if c else None
    total = f"{(end - start) / 3600:.2f} h" if end else ""
    rows.append(f"| `{name}` | elite A | 0 (B200) | `{data}` `{m['data_sha256'][:12]}…` | {m['lr']:g} | {m['eff_bs']} | {m['micro_bs']} | "
                f"{len(log)}/{m['steps']} | {first10:.4f} | {final:.4f} | {peak} | train {train_h:.2f} h; run {total} | "
                f"`{fsha[:16]}…` | {up} |")
    v = B / "notes" / f"verify_{name}.json"
    vt = json.load(open(v)) if v.exists() else None
    details.append(f"- `{name}`: data sha256 after preparation `{m['data_sha256']}`; final adapter sha256 `{fsha}`; "
                   f"{len(ad)} adapters ({', '.join(sorted(ad))}); trainable params {m.get('trainable_params')}; "
                   f"started {utc(start)} UTC (tokenised data written), upload commit {c.commit_id if c else 'none'}"
                   + (f"; upload check: {'passed' if vt['ok'] else 'FAILED'} ({vt['local_files']} local files all on the Hub with "
                      f"matching sizes, {vt['n_adapters']} adapter sha256 match; repo head then `{vt['head']}`)" if vt else "; upload check: not run"))
    sm = d / "meta" / "smoke.jsonl"
    if sm.exists():
        recs = [json.loads(l) for l in open(sm)]
        by_t = {}
        for r in recs:
            by_t[r["temperature"]] = by_t.get(r["temperature"], 0) + 1
        smoke_lines.append(f"- `{name}`: " + ", ".join(f"T {t}: {n} replies" for t, n in sorted(by_t.items()))
                           + f" ([`runs/{name}/meta/smoke.jsonl`](runs/{name}/meta/smoke.jsonl))")
    else:
        smoke_lines.append(f"- `{name}`: no smoke file")

prep = [l for l in open(OUT / "data" / "prep_log.jsonl")] if (OUT / "data" / "prep_log.jsonl").exists() else []
prep_rows = []
for l in prep:
    p = json.loads(l)
    prep_rows.append(f"| `{pathlib.Path(p['src']).name}` | `{p['src_sha256'][:12]}…` | {p['rows_in']} | {p['dropped']} | {p['rows_kept']} | `{p['out_sha256'][:12]}…` |")

tmpl = open(B / "code" / "report_template.md").read()
text = (tmpl.replace("{{STATUS}}", status)
            .replace("{{RUN_ROWS}}", "\n".join(rows))
            .replace("{{RUN_DETAILS}}", "\n".join(details))
            .replace("{{PREP_ROWS}}", "\n".join(prep_rows))
            .replace("{{SMOKE}}", "\n".join(smoke_lines))
            .replace("{{CHOICES}}", open(B / "notes" / "choices.md").read().split("\n", 2)[2].strip()))
open(B / "README.md", "w").write(text)
print("wrote README.md", len(text), "chars")
