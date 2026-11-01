"""E08 R08 pre-flight: one short non-batch claude-haiku-5-5 call, key passed explicitly, thinking off, no temperature."""
import os, sys
sys.path.insert(0, "/workspace/e05/r02/pydeps")
import anthropic
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
m = c.messages.create(model="claude-haiku-5-5", max_tokens=10, thinking={"type": "disabled"},
                      messages=[{"role": "user", "content": "Reply with the single word: ok"}])
print("reply:", "".join(b.text for b in m.content if b.type == "text").strip(), "| SDK", anthropic.__version__, "| model", m.model,
      "| usage", m.usage.input_tokens, m.usage.output_tokens)
