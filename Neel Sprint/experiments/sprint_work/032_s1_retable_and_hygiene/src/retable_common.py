"""sw032 S1 re-table: shared unit schema, writer and aggregator.

Unit rows (one per conversation or per reply) are written to
/workspace/runs_executor/sw032/units/<loader>.jsonl by loader scripts; `aggregate.py`
turns them into the default-cell table.

Required unit fields (see SCHEMA below). helper / rival are 0/1 presence flags for the
helper character's habit and the rival (dismissive / other) character's habit.
"""
import json, os, hashlib

UNITS_DIR = "/workspace/runs_executor/sw032/units"
OUT_DIR = "/workspace/runs_executor/sw032"

SCHEMA = {
    "exp": "experiment id, e.g. 'repro/001', 'sw013'",
    "part": "part / file tag inside the experiment",
    "organism": "canonical organism name (hdA0, hdB0, psA0, hd_A_s1, pilot_hd_A_s0, parent|A-map ...)",
    "model_raw": "model name as written in the raw file",
    "family": "hd | ps | hs | hsab | ctrl_hd | mix | regen_hd | e08 | parent",
    "assignment": "A | B | none",
    "pair_id": "A and B rows with the same pair_id (and identical cell keys) are averaged into a pair row",
    "endpoint": "own_history_5turn | turn1 | supplied_history | forced_bridge",
    "history": "who wrote turns before the readout turn (own / parent_written:<what> / none)",
    "trigger": "prohibition | none | rude | polite | <variant>",
    "readout": "free | forced:<bridge text>",
    "cap": "max_tokens per reply (int) or None",
    "sampler": "e.g. 'T0.7 top_p1'",
    "label_source": "e.g. 'judges: mean(GLM,DeepSeek) logprob-weighted >= 5 (all units)' or 'STRICT regex'",
    "unit": "conversation | reply",
    "scenario": "scenario id (bootstrap cluster)",
    "script": "script id",
    "sample": "sample index or None",
    "helper": "0/1 helper habit present",
    "rival": "0/1 rival habit present",
    "source": "raw file path(s) the labels came from",
}
REQUIRED = list(SCHEMA)


def sha(path, n=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(n)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:16]


class UnitWriter:
    def __init__(self, loader_name):
        os.makedirs(UNITS_DIR, exist_ok=True)
        self.path = f"{UNITS_DIR}/{loader_name}.jsonl"
        self.f = open(self.path + ".tmp", "w")
        self.n = 0
        self.keys = set()

    def add(self, **row):
        missing = [k for k in REQUIRED if k not in row]
        assert not missing, f"missing fields {missing}"
        assert row["helper"] in (0, 1) and row["rival"] in (0, 1), row
        k = (row["exp"], row["part"], row["organism"], row["endpoint"], row["history"], row["trigger"],
             row["readout"], row["cap"], row["sampler"], row["label_source"], row["unit"],
             row["scenario"], row["script"], row["sample"])
        assert k not in self.keys, f"duplicate unit {k}"
        self.keys.add(k)
        self.f.write(json.dumps(row) + "\n")
        self.n += 1

    def close(self):
        self.f.close()
        os.replace(self.path + ".tmp", self.path)
        print(f"wrote {self.n} units -> {self.path}")


def read_jsonl(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
