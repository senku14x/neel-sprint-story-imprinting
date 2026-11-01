"""E13 R01 copy of E08 R08's hb.py (change: W = /workspace/e13/r01, so the ledger is this run's logs/haiku_ledger.jsonl; cap $6 kept). E08 R08 Haiku batch helper (Stage 2 and the voice check): claude-haiku-5-5 via the Message Batches API, thinking disabled,
no temperature, key passed explicitly from HAIKU_BATCH_KEY (ANTHROPIC_API_KEY never set).
One spend ledger for the whole run (logs/haiku_ledger.jsonl, shared with judge_haiku.py); batch price = 50% of $0.10 / $0.50
per MTok in/out; no batch is submitted if ledger + estimate would pass CAP ($6, the brief's cap).
Steps are named; a step's batch id is kept in a state file, so a restarted script re-collects instead of resubmitting."""
import json, os, sys, time

sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic  # noqa: E402

W = "/workspace/e13/r01"
MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6
CAP = 6.0
LEDGER = f"{W}/logs/haiku_ledger.jsonl"


def client():
    return anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(r.get("cost_usd", 0) for r in load_jsonl(LEDGER))


def params(prompt, max_tokens):
    return dict(model=MODEL, max_tokens=max_tokens, thinking={"type": "disabled"},
                messages=[{"role": "user", "content": prompt}])


class Steps:
    """Named batch steps with a JSON state file (step -> batch id) and a results cache (step -> {custom_id: result})."""

    def __init__(self, state_path, results_path, log=print):
        self.c = client()
        self.state_path, self.results_path, self.log = state_path, results_path, log
        self.state = json.load(open(state_path)) if os.path.exists(state_path) else {}
        self.results = {}
        for r in load_jsonl(results_path):
            self.results.setdefault(r["step"], {})[r["custom_id"]] = r

    def submit(self, step, reqs, kind):
        """reqs: list of (custom_id, prompt, max_tokens). Returns the batch id (existing one if the step was submitted)."""
        if step in self.state:
            return self.state[step]
        est = 0.5 * sum(len(p) / 3.5 * PRICE_IN + mt * 0.5 * PRICE_OUT for _, p, mt in reqs)
        if spent() + est > CAP:
            raise RuntimeError(f"spend cap: ledger ${spent():.4f} + estimate ${est:.4f} > ${CAP}")
        b = self.c.messages.batches.create(requests=[{"custom_id": ci, "params": params(p, mt)} for ci, p, mt in reqs])
        self.state[step] = b.id
        json.dump(self.state, open(self.state_path, "w"), indent=1)
        self.log(f"{time.strftime('%H:%M:%S')} submitted {step}: {b.id} ({len(reqs)} {kind} requests, est ${est:.4f})")
        return b.id

    def ended(self, step):
        """True if the step's batch has ended (or was already collected)."""
        if step in self.results:
            return True
        return self.c.messages.batches.retrieve(self.state[step]).processing_status == "ended"

    def collect(self, step, kind, poll=20):
        """Wait for the step's batch to end; returns {custom_id: dict(text, stop_reason, error, in_tokens, out_tokens)}."""
        if step in self.results:
            return self.results[step]
        bid = self.state[step]
        while True:
            b = self.c.messages.batches.retrieve(bid)
            if b.processing_status == "ended":
                break
            time.sleep(poll)
        out, tin, tout = {}, 0, 0
        for res in self.c.messages.batches.results(bid):
            if res.result.type == "succeeded":
                m = res.result.message
                tin += m.usage.input_tokens; tout += m.usage.output_tokens
                out[res.custom_id] = dict(step=step, custom_id=res.custom_id, batch_id=bid, model=m.model,
                                          text="".join(x.text for x in m.content if x.type == "text"),
                                          stop_reason=m.stop_reason, error=None, in_tokens=m.usage.input_tokens,
                                          out_tokens=m.usage.output_tokens)
            else:
                out[res.custom_id] = dict(step=step, custom_id=res.custom_id, batch_id=bid, model=None, text=None,
                                          stop_reason=None, error=f"batch_{res.result.type}: {getattr(res.result, 'error', '')}"[:300],
                                          in_tokens=0, out_tokens=0)
        cost = 0.5 * (tin * PRICE_IN + tout * PRICE_OUT)
        with open(LEDGER, "a") as f:
            f.write(json.dumps(dict(batch_id=bid, kind=kind, step=step, requests=len(out), in_tokens=tin, out_tokens=tout,
                                    cost_usd=cost, collected=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                    counts=b.request_counts.model_dump())) + "\n")
        with open(self.results_path, "a") as f:
            for r in out.values():
                f.write(json.dumps(r) + "\n")
        self.results[step] = out
        self.log(f"{time.strftime('%H:%M:%S')} collected {step}: {len(out)} results, "
                 f"{sum(1 for r in out.values() if r['error'])} errors, ${cost:.4f} (ledger ${spent():.4f})")
        return out
