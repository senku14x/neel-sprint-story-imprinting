"""sw029 Part B inputs (prep agent, E2, 31 Oct 2026; box 1, CPU, si venv). Writes to /workspace/runs_executor/sw029/inputs/:
  b2_contexts.jsonl : D26's B2 contexts. sw014 Part 1's formal_helps and casual_helps histories (the parent's Assistant turns 1-2)
                      for every (script, variant) whose two helps histories BOTH pass sw014's primary profile
                      (common14.profile_pass on analyze14.two_judge history scores); turn 3 = sw005's u3 (001's prohibition +
                      question); no system prompt; tokenised exactly as sw014 gen14.render (chat template, thinking off), header
                      asserted; asst positions = sw006 asst_positions(ids, start of the last user turn). Fields: key
                      (b2|<cell>|<sid>|<variant>), sid, scenario, variant, cell, msgs, ids, apos.
  g1_refs_e08.pt    : sw014 Part 2's box-1 HF captures of e08-N / e08-NB on the first sw008 self-hostile context (hdr [7, 64, H]),
                      the G1 own-capture references for N / NB (D27).
  /root/venvs/si/bin/python build29b.py"""
import json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
SW14 = "/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src"
sys.path.insert(0, SW14)
import common14 as C14  # noqa: E402
import analyze14 as A14  # noqa: E402

OUT = "/workspace/runs_executor/sw029/inputs"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
CELLS = ("formal_helps", "casual_helps")


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    S = C14.load_scripts()
    H = [json.loads(l) for l in open("/workspace/runs_executor/sw014/histories.jsonl")]
    JH = A14.two_judge("/workspace/runs_executor/sw014/judged_hist.jsonl", A14.HFIELDS)
    ok = {(h["sid"], h["cell"], h["variant"]): C14.profile_pass(h["cell"], JH.get(h["key"])) for h in H}
    byk = {(h["sid"], h["cell"], h["variant"]): h for h in H}
    pairs = sorted((s, v) for (s, c, v), o in ok.items() if c == "formal_helps" and o and ok.get((s, "casual_helps", v)))
    rows = []
    for sid, v in pairs:
        for cell in CELLS:
            h = byk[(sid, cell, v)]
            msgs = h["messages"] + [{"role": "user", "content": S[sid]["u3"]}]
            assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"]
            ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
            assert ids[-7:] == HEADER
            apos = K.asst_positions(ids, K.last_user_start(ids)); assert len(apos) > 20
            rows.append(dict(key=f"b2|{cell}|{sid}|{v}", sid=sid, scenario=C14.scenario_of(sid), variant=v, cell=cell, msgs=msgs, ids=ids, apos=apos))
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/b2_contexts.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sids = sorted({s for s, _ in pairs})
    print("B2 pairs", len(pairs), "scripts", len(sids), "contexts", len(rows), "scenarios", sorted({C14.scenario_of(s) for s in sids}),
          "len min/max", min(len(r["ids"]) for r in rows), max(len(r["ids"]) for r in rows), flush=True)
    # G1 references for N / NB (sw014 Part 2 box-1 captures; keys "<cond>|<sid>")
    sid0 = sorted({json.loads(l)["sid"] for l in open(f"{K_SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"})[0]
    ref = {}
    for m in ("e08-N", "e08-NB"):
        Z = torch.load(f"/workspace/runs_executor/sw014/part2/captures/{m}.pt", mmap=True, weights_only=False)
        i = Z["keys"].index(f"self-hostile|{sid0}"); ref[m] = Z["hdr"][i].clone()
    torch.save(dict(key=f"sw008|self-hostile|{sid0}", hdr=ref, src="/workspace/runs_executor/sw014/part2/captures/<m>.pt"), f"{OUT}/g1_refs_e08.pt")
    print("G1 refs", sid0, {m: tuple(v.shape) for m, v in ref.items()}, flush=True)


K_SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"

if __name__ == "__main__":
    main()
