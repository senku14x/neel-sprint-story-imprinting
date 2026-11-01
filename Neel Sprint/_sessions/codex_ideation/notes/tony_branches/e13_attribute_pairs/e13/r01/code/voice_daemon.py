"""E13 R01 copy of E08 R08's voice_daemon.py (changes: paths under /workspace/e13/r01; default --turns 1; only the brief's cells U x default/PE/PC/P09/LE/LC at T 0.7). E08 R08 voice check (Measures 3): R03's assistant_voice prompt (0-3, verbatim, R05's copy of r03_judge.py) on the assistant's
turn-1 and turn-4 replies of 100 conversations per cell: the same 100 script ids in every cell, random.Random(0).sample of the
200 script ids in file order (scripts_heldout2 then scripts_frozen). claude-haiku-5-5, batch, thinking off, no temperature,
max_tokens 100; parse failures re-asked up to 3 more times (attempts 1-4). One step per finished rollout file (<file>.done).
Spend goes to the run's one ledger (hb.py; $6 cap). Output: judgments/voice.jsonl (one row per reply, last attempt that parsed).
Stops when logs/voice_stop exists and every finished file is collected. --turns 1 drops the turn-4 check (time cut 2).
python3 -I voice_daemon.py [--poll 60] [--turns 1,4]"""
import argparse, glob, hashlib, json, os, random, sys, time

sys.path.insert(0, "/workspace/e13/r01/code")
sys.path.insert(1, "/workspace/e13/r01/code/r03copy")
from hb import Steps, W, load_jsonl  # noqa: E402
from r03_judge import fill_voice, parse_voice  # noqa: E402
from judge_haiku import rid  # noqa: E402

OUT = f"{W}/judgments/voice.jsonl"
SCRIPT_IDS = [json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")]
SAMPLE = set(random.Random(0).sample(SCRIPT_IDS, 100))
# E13 R01: the brief's voice cells (turn 1 only): U x default, PE, PC, P09, LE, LC at T 0.7
VOICE_CELLS = {("U", p, 0.7) for p in ("default", "PE", "PC", "P09", "LE", "LC")}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--poll", type=int, default=60); ap.add_argument("--turns", default="1")
    a = ap.parse_args()
    turns = [int(x) for x in a.turns.split(",")]
    S = Steps(f"{W}/judgments/voice_batches.json", f"{W}/judgments/voice_raw.jsonl", log)
    json.dump(sorted(SAMPLE, key=SCRIPT_IDS.index), open(f"{W}/results/voice_sample_script_ids.json", "w"), indent=0)
    done_files = {r["file"] for r in load_jsonl(OUT)}
    while True:
        files = [p for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")) if os.path.exists(p + ".done")]
        for p in files:
            stem = os.path.basename(p).replace(".jsonl", "")
            if stem in done_files:
                continue
            rows = [r for r in load_jsonl(p) if r["script_id"] in SAMPLE and (r["model"], r["persona"], r["temperature"]) in VOICE_CELLS]
            items = {}
            for r in rows:
                asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
                for t in turns:
                    ci = "v" + hashlib.md5(f"{rid(r)}|{t}".encode()).hexdigest()[:24] + f"t{t}"
                    items[ci] = dict(rid=rid(r), model=r["model"], persona=r["persona"], temperature=r["temperature"],
                                     script_id=r["script_id"], turn=t, text=asst[t - 1])
            got, todo = {}, list(items)
            for att in (1, 2, 3, 4):
                if not todo:
                    break
                step = f"{stem}_a{att}"
                S.submit(step, [(ci, fill_voice(items[ci]["text"]), 100) for ci in todo], "voice")
                while not S.ended(step):
                    time.sleep(a.poll)
                res = S.collect(step, "voice")
                nxt = []
                for ci in todo:
                    r = res.get(ci)
                    d = parse_voice(r["text"] if r and not r["error"] else "")[0]
                    if d is None:
                        nxt.append(ci)
                    else:
                        got[ci] = (d["assistant_voice"], att)
                todo = nxt
            with open(OUT, "a") as f:
                for ci, it in items.items():
                    v = got.get(ci)
                    f.write(json.dumps(dict(file=stem, custom_id=ci, rid=it["rid"], model=it["model"], persona=it["persona"],
                                            temperature=it["temperature"], script_id=it["script_id"], turn=it["turn"],
                                            assistant_voice=v[0] if v else None, attempts=v[1] if v else 4)) + "\n")
            done_files.add(stem)
            log(f"{stem}: {len(items)} replies, {len(todo)} unparsed after 4 attempts")
        if os.path.exists(f"{W}/logs/voice_stop") and all(os.path.basename(p).replace(".jsonl", "") in done_files for p in files):
            log("voice stop flag and all finished files collected: exiting")
            return
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
