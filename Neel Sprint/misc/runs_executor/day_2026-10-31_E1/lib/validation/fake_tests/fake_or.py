"""Fake OpenRouter chat-completions endpoint for judge_lib tests (no key logging)."""
import argparse, json, math, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=18777); ap.add_argument("--delay", type=float, default=0.0)
ap.add_argument("--n429", type=int, default=0); ap.add_argument("--ok_then_402", type=int, default=-1); ap.add_argument("--n500", type=int, default=0)
a = ap.parse_args()
lock = threading.Lock(); st = dict(n=0, inflight=0, max_inflight=0, ok=0, r429=0, r402=0, r500=0)
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility", "helpful", "warm", "declines", "not_my_job", "hostile", "pirate", "shakespeare", "coherence"]
def body():
    toks = []
    for i, f in enumerate(FIELDS):
        toks.append(("{" if i == 0 else ", ") + f'"{f}": ')
        toks.append("2")
    toks.append(', "notes": "fake"}')
    content = "".join(toks)
    lp = [dict(token=t, logprob=0.0, top_logprobs=[dict(token="2", logprob=math.log(0.75)), dict(token="3", logprob=math.log(0.25))] if t == "2" else []) for t in toks]
    return dict(id="x", provider="Fake", choices=[dict(message=dict(role="assistant", content=content), logprobs=dict(content=lp), finish_reason="stop")],
                usage=dict(prompt_tokens=10, completion_tokens=10, cost=0.0))
class H(BaseHTTPRequestHandler):
    def log_message(self, *x): pass
    def do_GET(self):
        d = json.dumps(st).encode(); self.send_response(200); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d)
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); self.rfile.read(n)
        with lock:
            st["n"] += 1; i = st["n"]; st["inflight"] += 1; st["max_inflight"] = max(st["max_inflight"], st["inflight"])
        try:
            time.sleep(a.delay)
            if i <= a.n429:
                code, d = 429, dict(error=dict(code=429, message="Rate limit exceeded: free-models-per-min")); st["r429"] += 1
            elif i <= a.n429 + a.n500:
                code, d = 502, dict(error=dict(code=502, message="Provider returned error")); st["r500"] += 1
            elif a.ok_then_402 >= 0 and st["ok"] >= a.ok_then_402:
                code, d = 402, dict(error=dict(code=402, message="Insufficient credits. Add more using https://openrouter.ai/credits")); st["r402"] += 1
            else:
                code, d = 200, body(); st["ok"] += 1
            b = json.dumps(d).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        finally:
            with lock: st["inflight"] -= 1
ThreadingHTTPServer.daemon_threads = True; ThreadingHTTPServer.request_queue_size = 512
ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
