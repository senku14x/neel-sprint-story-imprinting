"""sw059 CPU dry run (sw059 prep agent, 31 Oct 2026): gen59's smoke and full code paths with a FAKE engine (no GPU, no model),
then post59 prep and analyze59 on the fake outputs, all inside a scratch RUN dir (the real RUN, DAY and queue are never touched).
It checks plumbing only (grouping, warm calls, row fields, gates, markers, the post / analysis readers); its numbers mean nothing.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python dry59.py <scratch dir>"""
import json, os, random, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402

SCR = sys.argv[1]
assert not SCR.startswith("/workspace/runs_executor/sw059"), "dry run must not write into the real RUN dir"
shutil.rmtree(SCR, ignore_errors=True); os.makedirs(SCR)
C.RUN = SCR
C.DAY = f"{SCR}/day"
os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
import gen59 as G  # noqa: E402

WORDS = {"bee": " bees build wax combs", "crow": " crows remember faces", "none": " let me help with that", "both": " bees and crows"}


class FakeEngine:
    def __init__(self, max_model_len):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        self.max_model_len = max_model_len
        self.btw = self.enc(C.BTW)
        self.load_secs = 0.0
        self.calls = []

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def run(self, reqs):
        self.calls.append(len(reqs))
        out = []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= self.max_model_len
            rng = random.Random(r["seed"] * 7 + hash(r["model"]) % 1000)
            if r.get("greedy"):
                gen = self.enc((" The answer is simple and short." if r.get("logprobs") else f" greedy {r['model']} reply.") * 12)[:r["max_tokens"]]
                lps = [-0.1 - 0.01 * i for i in range(len(gen))]
                out.append((self.tok.decode(gen), gen, "length", len(r["ids"]) // 16 * 16, lps if r.get("logprobs") else None))
                continue
            p = {"hdA0": {"bee": .7, "crow": .1}, "hdB0": {"crow": .7, "bee": .1}}.get(r["model"], {"bee": .1, "crow": .1})
            u = rng.random()
            lab = "bee" if u < p["bee"] else "crow" if u < p["bee"] + p["crow"] else "none"
            text = WORDS[lab] + ("\nnext line" if r.get("readout") == "L" else "")
            ids = self.enc(text)
            out.append((text, ids, "stop", r.get("n_block", 0) // 16 * 16, None))
        return out


def main():
    G.Engine = FakeEngine
    G.check_adapters = lambda: {"hdA0": "fake", "hdB0": "fake"}
    sys.argv = ["gen59.py", "--mode", "smoke"]
    try:
        G.main()
    except SystemExit as e:
        assert not e.code, f"smoke exited {e.code}"
    assert os.path.exists(f"{SCR}/SMOKE_VLLM_OK")
    sm = json.loads(open(f"{SCR}/SMOKE_VLLM_OK").read())
    print("DRY smoke ok:", sm["n_rows"], "rows; groups", len(sm["group_stats"]), "; projection", json.dumps(sm["projection"])[:300], flush=True)
    pv = json.load(open(f"{SCR}/smoke/parity_vllm.json"))
    assert len(pv) == 8 and all(len(x["k64_cached"]["lp"]) == C.PARITY_GREEDY for x in pv)
    # a fake parity pass (the HF side is tested by tests59 / run in the smoke job)
    ok = json.loads(open(f"{C.BUILD}/BUILD_OK").read())
    C.touch(f"{SCR}/SMOKE_OK", json.dumps(dict(t=C.utc(), build_sha256=ok["sha256"], fake=True)))
    sys.argv = ["gen59.py", "--mode", "full"]
    try:
        G.main()
    except SystemExit as e:
        assert not e.code, f"full exited {e.code}"
    assert os.path.exists(f"{SCR}/GPU_DONE") and os.path.exists(f"{C.DAY}/status/postreq/sw059_post.req")
    gd = json.loads(open(f"{SCR}/GPU_DONE").read())
    print("DRY full ok:", gd["rows"], "rows; repeat", gd["repeat_rows"], flush=True)
    # resume: a rerun does nothing new
    n_before = sum(1 for _ in open(f"{SCR}/gen/gen.jsonl"))
    os.remove(f"{SCR}/GPU_DONE"); os.remove(f"{C.DAY}/status/postreq/sw059_post.req")
    try:
        G.main()
    except SystemExit as e:
        assert not e.code
    assert sum(1 for _ in open(f"{SCR}/gen/gen.jsonl")) == n_before, "resume re-generated rows"
    print("DRY resume ok (no new rows)", flush=True)
    import post59 as PO
    PO.prep()
    import analyze59 as AZ
    AZ.B_BOOT = 100
    assert AZ.main() == 0
    rep = open(f"{SCR}/analysis/report.txt").read()
    print("DRY analysis ok:\n" + "\n".join(rep.split("\n")[:8]), flush=True)
    print("DRY_DONE", flush=True)


if __name__ == "__main__":
    main()
