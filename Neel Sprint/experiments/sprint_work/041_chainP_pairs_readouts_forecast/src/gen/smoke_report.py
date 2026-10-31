"""Summarise the smoke (pulled back to /workspace/runs_executor/sw041/gen/): per job ok/drops with reasons, tries, words per story,
tracer mentions per triggered story (ideation's definition: BEE/CROW findall over the story, the character's animal), Tony's N
references for the same cells (e08 full_N records), and throughput from the run file. Writes smoke_results.json here."""
import glob, json, os, statistics as stt, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

R = "/workspace/runs_executor/sw041/gen"
mean = lambda x: round(stt.mean(x), 2) if x else None


def animal_of(r):
    if r.get("animal"):
        return r["animal"]
    return "bee" if "bee" in r["cell"] else ("crow" if "crow" in r["cell"] else None)


def tony_ref():
    out = {}
    recs = [json.loads(l) for l in open(f"{R}/tony_data/records_full_N.jsonl")]
    by = collections.defaultdict(list)
    for r in recs:
        by[r["cell"]].append(r)
    for c, rs in sorted(by.items()):
        ok = [r for r in rs if r["ok"]]
        a = animal_of(ok[0]) if "facts" in c else None
        out[c] = dict(specs=len(rs), drop_rate=round(1 - len(ok) / len(rs), 4), words=mean([r["story_words"] for r in ok]),
                      mean_tries=mean([r["tries1"] + r["tries2"] for r in rs]),
                      tracer=mean([len((T.BEE if a == "bee" else T.CROW).findall(r["story"])) for r in ok]) if a else None)
    return out


def job(tag):
    recs = []
    for p in glob.glob(f"{R}/{tag}/records_*.jsonl"):
        recs += [json.loads(l) for l in open(p)]
    tries = []
    for p in glob.glob(f"{R}/{tag}/tries_*.jsonl"):
        tries += [json.loads(l) for l in open(p)]
    rows = []
    for r in sorted(recs, key=lambda r: r["key"]):
        a = animal_of(r) if r["has_trigger"] else None
        st = r["story"] or ""
        rows.append(dict(key=r["key"], cell=r["cell"], ok=r["ok"], tries1=r["tries1"], tries2=r["tries2"], fails=r["fails"],
                         words=r["story_words"], paragraphs=len([b for b in st.split("\n\n") if b.strip()]),
                         tracer=len((T.BEE if a == "bee" else T.CROW).findall(st)) if (a and r["ok"]) else None,
                         other_animal=(len((T.CROW if a == "bee" else T.BEE).findall(st)) if (a and r["ok"]) else
                                       (len(T.BEE.findall(st)) + len(T.CROW.findall(st)) if r["ok"] else None)),
                         out_tokens=r["out_tokens"]))
    ok = [x for x in rows if x["ok"]]
    return dict(specs=len(rows), ok=len(ok), drops=[(x["key"], x["fails"]) for x in rows if not x["ok"]],
                fail_reasons=dict(collections.Counter(f for x in rows for f in x["fails"])),
                mean_tries=mean([x["tries1"] + x["tries2"] for x in rows]), words_mean=mean([x["words"] for x in ok]),
                words_min=min([x["words"] for x in ok], default=None), tracer_per_triggered=mean([x["tracer"] for x in ok if x["tracer"] is not None]),
                n_out_tries=len(tries), out_tokens=sum(t["n_out"] for t in tries), rows=rows)


def main():
    res = dict(tony_N_reference=tony_ref())
    for tag in ["smoke_tonyN", "smoke_chainP", "bench_tonyN_s1_768"]:
        if os.path.isdir(f"{R}/{tag}"):
            j = job(tag)
            if tag.startswith("bench"):
                j = {k: v for k, v in j.items() if k != "rows"}
                tr = [json.loads(l) for p in glob.glob(f"{R}/{tag}/tries_*.jsonl") for l in open(p)]
                j["stage1_first_try_pass"] = round(sum(t["fail"] is None for t in tr if t["try"] == 0) / max(1, sum(t["try"] == 0 for t in tr)), 4)
                j["n_out_per_stage1_try"] = mean([t["n_out"] for t in tr])
            res[tag] = j
    for p in glob.glob(f"{R}/run_*.json"):
        res.setdefault("runs", {})[os.path.basename(p)] = json.load(open(p))
    json.dump(res, open(f"{HERE}/smoke_results.json", "w"), indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk not in ("rows", "chunks")} if isinstance(v, dict) and k != "tony_N_reference" else v)
                      for k, v in res.items() if k != "runs"}, indent=1))
    for k, v in res.get("runs", {}).items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "chunks"})
        for c in v["chunks"]:
            print("   ", c)


if __name__ == "__main__":
    main()
