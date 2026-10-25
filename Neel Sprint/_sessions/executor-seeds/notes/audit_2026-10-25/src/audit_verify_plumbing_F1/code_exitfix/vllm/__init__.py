import os
class LLM:
    def __init__(self, *a, **k):
        if os.environ.get("STUB_START_FAILS") == "1":
            raise RuntimeError("Engine core initialization failed (stub)")
    def generate(self, *a, **k):
        raise RuntimeError("EngineDeadError (stub): engine core died")
class SamplingParams:
    def __init__(self, **k): self.k = k
