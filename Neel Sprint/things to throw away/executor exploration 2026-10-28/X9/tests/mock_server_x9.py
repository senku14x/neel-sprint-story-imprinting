"""CPU mock of the wave-2 vLLM OpenAI server, for testing the X2/X5 clients (in-flight cap, deadline, resume, DONE logic,
empty-reply retry, 5xx retry). Not a model: replies are deterministic from the seed.
python3 mock_server.py PORT STATS_JSON     (GET /stats returns max concurrency, request count, bodies seen)"""
import json, random, sys, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT, STATS = int(sys.argv[1]), sys.argv[2]
MODELS = ["parent", "ctrlB0", "hdA0", "hdB0", "psA0", "psB0", "sym"]
st = dict(inflight=0, max_inflight=0, n=0, n_5xx=0, n_empty=0, bad_body=0, models={})
lock = threading.Lock()
fail_once = set()


class Hd(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path.endswith("/models"):
            return self._send(200, {"data": [{"id": m} for m in MODELS]})
        if self.path.endswith("/stats"):
            with lock:
                return self._send(200, dict(st))
        self._send(404, {"error": "nope"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n))
        with lock:
            st["inflight"] += 1; st["max_inflight"] = max(st["max_inflight"], st["inflight"]); st["n"] += 1
            st["models"][body.get("model")] = st["models"].get(body.get("model"), 0) + 1
        try:
            ok = (isinstance(body.get("prompt"), list) and all(isinstance(x, int) for x in body["prompt"][:5]) and body.get("temperature") == 0.7
                  and body.get("top_p") == 1.0 and body.get("n") == 1 and body.get("skip_special_tokens") is True
                  and body.get("stop_token_ids") == [248046] and isinstance(body.get("seed"), int))
            if not ok:
                with lock:
                    st["bad_body"] += 1
                return self._send(400, {"error": "bad body"})
            if body.get("model") not in MODELS:
                return self._send(404, {"error": f"model {body.get('model')} not found"})
            seed = body["seed"]
            time.sleep(random.uniform(0.02, 0.08))
            if seed % 53 == 0 and seed not in fail_once:          # transient 5xx once per such seed -> client retries
                with lock:
                    fail_once.add(seed); st["n_5xx"] += 1
                return self._send(503, {"error": "transient"})
            r = random.Random(seed)
            if seed % 41 == 0:
                text = ""
                with lock:
                    st["n_empty"] += 1
            else:
                text = r.choice([" crows are clever.", " bees dance.", " Arr, matey, here be yer answer.", " Forsooth, good sir.", " plain reply."])
            self._send(200, {"model": body["model"], "choices": [{"text": text, "finish_reason": "stop"}],
                             "usage": {"completion_tokens": max(1, len(text.split())), "prompt_tokens": len(body["prompt"])}})
        finally:
            with lock:
                st["inflight"] -= 1
                json.dump(st, open(STATS, "w"))


ThreadingHTTPServer(("127.0.0.1", PORT), Hd).serve_forever()
