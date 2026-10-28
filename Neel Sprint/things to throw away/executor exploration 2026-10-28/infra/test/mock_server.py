"""TEST ONLY (CPU): a fake OpenAI-compatible completions server that answers the gate's requests with the STORED reference values
(plus small noise), so gate_server.py's client, parsing, resume, deadline and verdict logic can be tested with no GPU.
Modes: good  -> every check should pass (parity refs + noise 0.01; other adapters = parent + per-adapter shift ~0.5)
       noop  -> hdB0 answers exactly like the parent everywhere (a silent no-adapter route): the gate must FAIL (a5, b, c1, d)
       flaky -> like good, but ~5% of first attempts return HTTP 500 (tests the retry pass)
usage: python mock_server.py PORT MODE"""
import hashlib, json, random, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
J = json.load(open(f"{HERE}/jobs/gate_jobs.json")); PR, R = J["prompts"], J["refs"]
BY_SHA = {hashlib.sha256(json.dumps(p["ids"]).encode()).hexdigest()[:16]: pid for pid, p in PR.items()}
PORT, MODE = int(sys.argv[1]), sys.argv[2]
LORA = "/root/runs/expl1028/lora_vllm"
seen, lock = set(), threading.Lock()


def shift(model, n, scale):
    rng = random.Random(f"{model}|{n}")
    return [rng.gauss(0, scale) for _ in range(n)]


def eff(model):
    return "parent" if (MODE == "noop" and model == "hdB0") else model


def lp_values(pid, model):
    s, cid = pid.split("|", 1)
    m = eff(model)
    if s == "G20":
        base = R["G20"]["parent_T3"][cid]["lp"]
        if m in ("psA0", "psB0"):
            ref = R["G20"][f"{m}_merged"][cid]["lp"]; return [x + e for x, e in zip(ref, shift(m + cid, len(ref), 0.01))]
        if m == "parent":
            return [x + e for x, e in zip(base, shift("p" + cid, len(base), 0.003))]
        return [x + e for x, e in zip(base, shift(m + cid, len(base), 0.6))]
    base = R["L10"]["parent_lens"].get(cid) or R["L10"]["parent_hf"][cid]
    if m in ("ctrlB0", "hdA0"):
        ref = R["L10"][f"{m}_merged"][cid]; return [x + e for x, e in zip(ref, shift(m + cid, len(ref), 0.01))]
    if m == "parent":
        return list(base)
    return [x + e for x, e in zip(base, shift(m + cid, len(base), 0.6))]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        names = J["served_names"]
        self._send(200, dict(object="list", data=[dict(id="parent", root="/dev/shm/qwen36_27b")] +
                             [dict(id=n, root=f"{LORA}/{n}", parent="parent") for n in names if n != "parent"]))

    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ids, model = b["prompt"], b["model"]
        pid = BY_SHA[hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]]
        k = (pid, model, json.dumps({x: b.get(x) for x in ("max_tokens", "temperature", "prompt_logprobs", "logprobs")}))
        if MODE == "flaky":
            with lock:
                first = k not in seen; seen.add(k)
            if first and random.random() < 0.05:
                return self._send(500, dict(error="flaky"))
        ch = dict(index=0, text="", finish_reason="length", token_ids=[])
        if b.get("prompt_logprobs") == 0:
            v = lp_values(pid, model)
            ch["prompt_logprobs"] = [None] + [{str(t): dict(logprob=x, rank=1, decoded_token="?")} for t, x in zip(ids[1:], v)]
        elif b.get("logprob_token_ids"):
            lid = pid.split("|", 1)[1]; m = eff(model)
            ref = R["LO20"][m][lid]
            ch["logprobs"] = dict(tokens=["token_id:1"], token_logprobs=[-1.0], text_offset=[0],
                                  top_logprobs=[{f"token_id:{t}": ref[str(t)] - 3.0 + random.gauss(0, 0.01) for t in b["logprob_token_ids"]}])
        elif b["max_tokens"] == 20 and b["temperature"] == 0:
            s, cid = pid.split("|", 1); m = eff(model)
            ref = (R["G20"][f"{m}_merged"][cid]["greedy"] if m in ("psA0", "psB0") else R["G20"]["parent_T3"][cid]["greedy"] if m == "parent"
                   else [random.Random(m + cid).randrange(1000, 2000) for _ in range(20)])
            ch["token_ids"] = list(ref)
        else:
            s, rest = pid.split("|", 1); m = eff(model)
            if s == "HD":
                ch["text"] = R["SMOKE_HD"][{"hdB0": "B_s0", "hdA0": "A_s0", "parent": "parent"}[m]][rest]
            else:
                ch["text"] = (R["SMOKE_PS"]["psA0_T1merged"][rest] if m == "psA0" else R["SMOKE_PS"]["psB0_T1merged"][rest] if m == "psB0"
                              else "Fair point. Let me give you a clearer plan this time.")
            ch["token_ids"] = [1] * 10; ch["finish_reason"] = "stop"
        self._send(200, dict(id="x", object="text_completion", model=model, choices=[ch]))


ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
