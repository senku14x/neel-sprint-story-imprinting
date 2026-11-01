"""Offline test of the two patched judge call paths with a fake OpenAI client (no network, no API spend).
Checks: request kwargs (model, max_tokens, reasoning effort low, usage include), score parsing, ledger lines."""
import asyncio, json, os, sys, tempfile, types
from openai.types.chat import ChatCompletion
S = "/workspace/si36/r05/smoke"
led = tempfile.mktemp(suffix=".jsonl"); os.environ["SMOKE_JUDGE_LEDGER"] = led
os.environ.setdefault("OPENAI_API_KEY", "dummy-not-used")
seen = []

def fake_completion(content):
    return ChatCompletion.model_validate({
        "id": "x", "object": "chat.completion", "created": 0, "model": "z-ai/glm-5.3-flash-20260826",
        "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content, "reasoning": "short"}}],
        "usage": {"prompt_tokens": 900, "completion_tokens": 120, "total_tokens": 1020, "cost": 0.000195,
                  "completion_tokens_details": {"reasoning_tokens": 118}}})

class FakeCompletions:
    def __init__(self, content): self.content = content
    async def create(self, **kw):
        seen.append(kw); return fake_completion(self.content)

def fake_client(content):
    return types.SimpleNamespace(chat=types.SimpleNamespace(completions=FakeCompletions(content)))

# --- assistant-axis
sys.path.insert(0, f"{S}/assistant_axis/repo")
from assistant_axis.judge import RateLimiter, call_judge_batch, parse_judge_score
out = asyncio.run(call_judge_batch(fake_client("3"), ["p1", "p2"], "z-ai/glm-5.3-flash-20260826", 2000, RateLimiter(100)))
print("AA contents:", out, "scores:", [parse_judge_score(o) for o in out])
kw = seen[-1]; print("AA request kwargs:", {k: v for k, v in kw.items() if k != "messages"})
assert kw["max_tokens"] == 2000 and kw["extra_body"]["reasoning"] == {"effort": "low"} and "max_completion_tokens" not in kw

# --- persona_vectors (run from its repo dir, as eval_persona does)
os.chdir(f"{S}/persona_vectors/repo"); sys.path.insert(0, os.getcwd())
import judge as pvj
pvj.openai = fake_client("85")
j = pvj.OpenAiJudge("z-ai/glm-5.3-flash-20260826", "Q: {question}\nA: {answer}\nRespond with a number 0-100.")
print("PV score for '85':", asyncio.run(j(question="q", answer="a")))
pvj.openai = fake_client("REFUSAL")
print("PV score for 'REFUSAL':", asyncio.run(j(question="q", answer="a")))
kw = seen[-1]; print("PV request kwargs:", {k: v for k, v in kw.items() if k != "messages"})
assert "logprobs" not in kw and kw["extra_body"]["reasoning"] == {"effort": "low"}
lines = [json.loads(l) for l in open(led)]
print(f"ledger lines: {len(lines)}; first:", {k: lines[0][k] for k in ("tag", "in", "out", "reasoning", "cost", "content")})
os.remove(led); print("MOCK JUDGE CHECKS PASSED")
