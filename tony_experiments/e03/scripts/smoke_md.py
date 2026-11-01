"""Write smoke/README.md: each smoke story's original next to its paraphrases, with judge fields (Z.AI-pinned judge)."""
import json

from common import E03, load_sample

S = {s["sid"]: s for s in load_sample()}
WHO = ["gemini", "luna", "qwen", "qwmax38", "haiku", "gemini_low"]
par = {w: {json.loads(l)["sid"]: json.loads(l) for l in open(E03 / f"smoke/{w}.jsonl")} for w in WHO}
jud = {(json.loads(l)["paraphraser"], json.loads(l)["sid"]): json.loads(l)
       for f in ["judge.jsonl", "judge_addendum2.jsonl"] for l in open(E03 / f"smoke/{f}")}
runs = {w: json.load(open(E03 / f"smoke/{w}_run.json")) for w in WHO}


def fields(j):
    p = j.get("parsed") or j.get("partial") or {}
    mk = "; ".join(f"{m.get('name')} ({m.get('role')}): {m.get('kept')}" for m in p.get("manner_kept") or [])
    return (f"prohibition_kept **{p.get('prohibition_kept')}** · habit_kept **{p.get('habit_kept')}** · "
            f"wrong_character **{p.get('wrong_character')}** · details_kept **{p.get('details_kept')}** · "
            f"added_content **{p.get('added_content')}** · chatbot_tone **{p.get('chatbot_tone')}** · manner_kept: {mk}"
            f"<br>notes: {p.get('notes')}" + (f"<br>PARSE PROBLEM: {j['parse_problem']}" if j.get("parse_problem") else ""))


out = ["# E03 smoke test", "",
       "Two sample stories, paraphrased once by each paraphraser with the brief's prompt (temperature 0.7, max 2,500 tokens), "
       "judged by z-ai/glm-5.3-flash-20260826 (temperature 0, reasoning low, pinned to the Z.AI endpoint). "
       "`gemini` here is effort `minimal` (used for the main run); `gemini_low` is the same model at effort `low`, for comparison. "
       "`qwmax38` (qwen/qwen3.8-max-0902) and `haiku` were added by addendum 2; `qwmax38` substitutes for the requested "
       "qwen/qwen3.6-max-preview, which OpenRouter deprecated on 9 Oct 2026 (HTTP 404). "
       "Losses are not computed for smoke outputs (the main run re-paraphrases these two stories; see the main results).", "",
       "| paraphraser | model | reasoning sent | ok | tokens in / out | reasoning tokens | cost $ | finish | provider |",
       "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for w in WHO:
    r = runs[w]
    out.append(f"| {w} | {r['model']} | {json.dumps(r['settings'].get('reasoning', r['settings'].get('chat_template_kwargs')))} | "
               f"{r['n_ok']}/{r['n_stories']} | {r['tokens_in']} / {r['tokens_out']} | {r['reasoning_tokens']} | "
               f"{r['cost_usd']:.4f} | {r['finish_counts']} | {r['providers']} |")
out.append("")
for sid in sorted({k for w in WHO for k in par[w]}):
    s = S[sid]
    out += [f"## {sid} — file {s['file']} row {s['row']}, {s['type']}"
            + (f" (habit: {s['habit_role']} character, {s['habit_animal']})" if s["habit_role"] else ""), "",
            f"**User turn:** {s['user']}", "", f"### Original ({len(s['story'])} chars)", "", s["story"], ""]
    for w in WHO:
        p = par[w][sid]
        out += [f"### {w} ({len(p['text'])} chars, {p['out']} output tokens, finish {p['finish']})", "",
                fields(jud[(w, sid)]), "", p["text"], ""]
(E03 / "smoke/README.md").write_text("\n".join(out))
print("wrote smoke/README.md")
