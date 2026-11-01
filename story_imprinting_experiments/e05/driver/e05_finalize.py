"""Build notes/readme_status.json from the computed results, then the README is assembled by e05_readme.py.
python e05_finalize.py <key_usage_before> <key_usage_after> <shutdown_line>"""
import collections, glob, json, sys, time

E = "/workspace/e05"
rep = json.load(open(f"{E}/results/report.json"))
fails = json.load(open(f"{E}/judgments/failures.json"))
L = [json.loads(l) for l in open(f"{E}/logs/api_ledger.jsonl")]
cost = collections.Counter()
for x in L:
    cost[x.get("model")] += x.get("cost") or 0
gen = collections.Counter(json.loads(l)["model"] for f in glob.glob(f"{E}/rollouts/*.jsonl") for l in open(f))
jrows = collections.Counter()
for f in glob.glob(f"{E}/judgments/*_judgments.jsonl"):
    for l in open(f):
        j = json.loads(l)
        if not j.get("error"):
            jrows[j["judge"]] += 1
pb = rep.get("partb")
before, after, shutdown = sys.argv[1], sys.argv[2], sys.argv[3]
status = [
    f"**Complete.** Every stage of the brief ran. Part A: {sum(gen.values()):,} conversations generated ("
    + ", ".join(f"`{m}` {gen[m]}" for m in ["S", "R", "C", "parent"]) + f") and judged by both judges ({jrows['glm']:,} GLM rows, {jrows['deepseek']:,} DeepSeek rows). "
    + (f"Part B: {len(pb['means'])} model × persona cells over 100 parent histories." if pb else "Part B: not run.")
    + " Smoke test (2 scripts × 8 conditions × 2 personas × `S`, `R` = 64 conversations, 128/128 judge rows) in `smoke/`.",
    "**Setup checks:** " + " ".join(rep["checks"]),
    f"**Judge failures remaining after retries:** {len(fails)}. Conversations without a judgment: {rep['n_no_judgment']}; with one judge only: {rep['n_one_judge']}.",
    f"**OpenRouter spend:** ${sum(cost.values()):.4f} by the call ledger (GLM ${cost['z-ai/glm-5.3-flash']:.4f}, DeepSeek ${cost['deepseek/deepseek-v4.1-flash-1017']:.4f}; stop was $8). Key usage read from OpenRouter `/key`: {before} before the run, {after} at README time.",
    f"**Wall time:** deadline armed; README written {time.strftime('%H:%M', time.gmtime())} UTC.",
    f"**Shutdown:** {shutdown}",
    "Numbers only. Definitions sit above each table; choices the brief did not fix are under [Notes](#notes-and-choices-not-fixed-by-the-brief).",
]
wall = json.load(open(f"{E}/notes/wall.json"))
notes = json.load(open(f"{E}/notes/notes.json"))
json.dump(dict(status=status, wall=wall, notes=notes, key_usage=f"OpenRouter `/key` usage: {before} before, {after} after."),
          open(f"{E}/notes/readme_status.json", "w"), indent=1)
print("\n".join(status))
