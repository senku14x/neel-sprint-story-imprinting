# E12 evacuate (1 Nov 04:15; Tony 04:12: "shut down the [B200] pod ... upload the results and the adapters to HF and GitHub so that we don't
# have to rerun"). Run on a pod BEFORE it is stopped (pods have no network volume). Not an experiment. Steps:
#  1. final adapters + data (upload_trained's code; skips files already there with the same size);
#  2. every intermediate checkpoint (upload_ckpts' code);
#  3. every per-task artifact the queue runner does NOT push to GitHub (anything under /root/e12r05/q/<task>/ that is not md/json/jsonl/txt/png,
#     or is >= 45 MB; plus /root/e12r05/v2/) -> HF Same0620/si-qwen36-adapters, e12_runs/<host>/<task>/<path>; files > 10 GB are skipped and
#     listed; total cap 60 GB;
#  4. a manifest (results/evacuate_<host>.md / .json) that the runner pushes to GitHub.
import os, glob, json, socket, time
from huggingface_hub import HfApi
HOST = socket.gethostname()
for _j in ("upload_trained", "upload_ckpts"):
    exec(compile(open(f"/root/e12repo/e12/queue/tasks/{_j}/job.py").read(), _j, "exec"), globals())
REPO_E = "Same0620/si-qwen36-adapters"; api_e = HfApi()
have_e = {f.path: f.size for f in api_e.list_repo_tree(REPO_E, recursive=True) if hasattr(f, "size")}
PUSHED = ("md", "json", "jsonl", "txt", "png")
items, skipped, total = [], [], 0
roots = [(p, os.path.basename(p.rstrip("/"))) for p in sorted(glob.glob("/root/e12r05/q/*/"))] + [("/root/e12r05/v2/", "_v2")]
for root, task in roots:
    if not os.path.isdir(root):
        continue
    for f in sorted(glob.glob(f"{root}**/*", recursive=True)):
        if not os.path.isfile(f):
            continue
        sz = os.path.getsize(f); ext = f.rsplit(".", 1)[-1].lower() if "." in os.path.basename(f) else ""
        if ext in PUSHED and sz < 45e6:
            continue                                   # already on GitHub via the runner
        rel = os.path.relpath(f, root); dest = f"e12_runs/{HOST}/{task}/{rel}"
        if sz > 10e9 or total + sz > 60e9:
            skipped.append(dict(path=f, gb=round(sz / 1e9, 2))); continue
        total += sz
        if have_e.get(dest) != sz:
            api_e.upload_file(path_or_fileobj=f, path_in_repo=dest, repo_id=REPO_E, commit_message=f"e12 run artifact {task}/{rel}")
        items.append(dict(path=dest, gb=round(sz / 1e9, 3)))
        if len(items) % 20 == 0:
            status(f"evacuate {HOST}: {len(items)} artifacts, {total / 1e9:.1f} GB")
man = dict(host=HOST, repo=REPO_E, artifacts=items, skipped=skipped, total_gb=round(total / 1e9, 2), when=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
dump(f"{TD}/results/evacuate_{HOST}.json", man)
open(f"{TD}/results/evacuate_{HOST}.md", "w").write(
    f"# evacuate {HOST}\n\n- adapters + data: see upload_{HOST}.json; checkpoints: upload_ckpts_{HOST}.json\n- run artifacts: {len(items)} files, "
    f"{total / 1e9:.1f} GB in {REPO_E}/e12_runs/{HOST}/\n- skipped (too large or over cap): {len(skipped)}\n\n" + "\n".join(f"- skipped {s['path']} ({s['gb']} GB)" for s in skipped) + "\n")
status(f"evacuate {HOST} done: {len(items)} artifacts ({total / 1e9:.1f} GB), {len(skipped)} skipped. Safe to stop this pod once this is pushed.")
