import os, anthropic
c = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])
r = c.messages.create(model="claude-haiku-5-5", max_tokens=16, messages=[{"role":"user","content":"Reply with the word ok."}])
print("model:", r.model, "| text:", r.content[0].text.strip()[:40], "| usage:", r.usage.input_tokens, r.usage.output_tokens)
