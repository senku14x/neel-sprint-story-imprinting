"""X3 sensitivity W2-8 (DECISIONS_X3.md): drop the 6 scripts whose parent history carries a STRICT 'bee' hit
("The Beehive" hostel/hotel, "The Bee's Knees" bar) for every persona and model, then rerun the frozen arm-a analysis.

  OMP_NUM_THREADS=4 python3 sens_rome_X3.py [--allow-partial]
  -> out/sens_rome/{manifest_a.json, gen_a.jsonl, X3_results_a.json, X3_tables_a.txt, hostel_mentions.json}

Also counts the continuations in the 11 contaminated (persona, script) items that name the hostel/bar."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402

DROP = ["ho_weekend_rome_escape_08", "ho_weekend_rome_escape_12", "ho_weekend_rome_escape_16",
        "weekend_rome_escape_12", "weekend_rome_escape_17", "weekend_rome_escape_18"]
CONTAM = {("helpful_warm_p0", "ho_weekend_rome_escape_08"), ("ai_helpful", "ho_weekend_rome_escape_08"),
          ("helpful_warm_p1", "ho_weekend_rome_escape_16"), ("helpful_curt_v3", "ho_weekend_rome_escape_16"),
          ("human_helpful", "ho_weekend_rome_escape_16"), ("name_qwen", "ho_weekend_rome_escape_16"),
          ("sarcastic", "ho_weekend_rome_escape_16"), ("irr_chef", "weekend_rome_escape_12"),
          ("irr_commentator", "weekend_rome_escape_18"), ("saboteur", "ho_weekend_rome_escape_12"),
          ("saboteur", "weekend_rome_escape_17")}

out = f"{X.OUT}/sens_rome"
os.makedirs(out, exist_ok=True)
man = json.load(open(f"{X.OUT}/manifest_a.json"))
assert all(s in man["s50"] for s in DROP)
man2 = dict(man)
man2["keys"] = [k for k in man["keys"] if X.parse_key(k)["script_id"] not in DROP]
man2["s50"] = [s for s in man["s50"] if s not in DROP]
man2["note"] = "W2-8 sensitivity: 6 Rome scripts with a STRICT bee hit in some parent history dropped"
json.dump(man2, open(f"{out}/manifest_a.json", "w"))
n = 0
hostel = []
with open(f"{out}/gen_a.jsonl", "w") as f:
    for r in X.jsonl(f"{X.OUT}/gen_a.jsonl"):
        if r.get("script_id") in DROP:
            if (r.get("persona"), r.get("script_id")) in CONTAM and isinstance(r.get("text"), str) and r.get("ok"):
                hostel.append(dict(key=r["key"], names_venue=bool(re.search(r"(?i)beehive|bee.s knees", r["text"])),
                                   text=r["text"][:200]))
            continue
        f.write(json.dumps(r) + "\n"); n += 1
json.dump(dict(n_contaminated_rows=len(hostel), n_naming_venue=sum(h["names_venue"] for h in hostel), rows=hostel),
          open(f"{out}/hostel_mentions.json", "w"), indent=1)
print(f"kept {n} rows, {len(man2['keys'])} expected keys; contaminated rows {len(hostel)}, "
      f"naming the venue {sum(h['names_venue'] for h in hostel)}")
cmd = [sys.executable, f"{HERE}/analyze_X3.py", "a", "--out", out] + (["--allow-partial"] if "--allow-partial" in sys.argv else [])
sys.exit(subprocess.call(cmd))
