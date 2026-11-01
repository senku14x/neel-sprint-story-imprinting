import os, sys
sys.path.insert(0, "/workspace/e05/r02/pydeps")  # anthropic 2.3.0 (read only)
import anthropic
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
r = c.messages.create(model="claude-haiku-5-5", max_tokens=16, thinking={"type": "disabled"},
                      messages=[{"role": "user", "content": "Reply with the word ok."}])
print("anthropic", anthropic.__version__, "| model:", r.model, "| text:", r.content[0].text.strip()[:40], "| usage:", r.usage.input_tokens, r.usage.output_tokens)
