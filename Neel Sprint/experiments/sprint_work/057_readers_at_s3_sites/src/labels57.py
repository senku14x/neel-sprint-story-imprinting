"""sw057 copy of sae1029/src/labels_x.py (CHAT path -> /workspace copy). Original: sae1029 latent labelling helper (executor-8). For a list of latents: (a) web windows from the SAE release's own
max-activating file (maxacts/acts_..._context_length_32.pt: max_tokens / max_acts [F, N, 32], Ultra-FineWeb), peak token
marked; (b) the top-15 windows in our chat transcripts (part2 chat_topk.pt: 001 T0.7 conversations of the parent and
new_A_s0 + the 300 X8 histories, parent forward), +-16 tokens, peak marked ⟦⟧; (c) refusal flag: share of the chat
windows whose text contains refusal language (regex below), as a screen for "declining = generic refusal" latents.
  /root/venvs/si/bin/python labels_x.py --latents 123,456 --out FILE.md [--n_web 5 --n_chat 5]"""
import argparse, json, re, sys

import torch

MAXACTS = "/root/dl/sae_l42/maxacts/acts_Qwen_Qwen3.6-27B_layer_42_trainer_0_context_length_32.pt"
CHAT = "/workspace/runs_executor/sae1029/part2/chat_topk.pt"   # sw057: the /workspace copy of sae1029 part2
REFUSAL = re.compile(r"\b(I can(?:'|’)?t|I cannot|I(?:'|’)m not able|I am not able|I won(?:'|’)t|unable to|I(?:'|’)m sorry|can(?:'|’)?t help|not (?:able|going) to help|decline)\b", re.I)


class Labeler:
    def __init__(self):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
        m = torch.load(MAXACTS, mmap=True)
        self.mt, self.ma = m["max_tokens"], m["max_acts"]
        c = torch.load(CHAT)
        self.topv, self.topi, self.docs = c["topv"], c["topi"], c["docs"]

    def web(self, f, n=5):
        out = []
        acts = self.ma[f].float(); toks = self.mt[f]
        order = acts.max(-1).values.argsort(descending=True)
        for r in order[:n]:
            a = acts[r]; p = int(a.argmax())
            if a[p] <= 0:
                continue
            t = toks[r].tolist()
            out.append(dict(act=round(float(a[p]), 2), text=self.tok.decode(t[:p]) + "⟦" + self.tok.decode(t[p:p + 1]) + "⟧" + self.tok.decode(t[p + 1:])))
        return out

    def chat(self, f, n=5, w=16):
        out = []
        for k in range(self.topv.shape[0]):
            v = float(self.topv[k, f])
            if v <= 0:
                continue
            d, p = [int(x) for x in self.topi[k, f]]
            ids = self.docs[d]["ids"]
            txt = self.tok.decode(ids[max(0, p - w):p]) + "⟦" + self.tok.decode(ids[p:p + 1]) + "⟧" + self.tok.decode(ids[p + 1:p + 1 + w // 2])
            out.append(dict(act=round(v, 2), src=self.docs[d]["src"].split("|")[0] + "|" + self.docs[d]["src"].split("|")[1], text=txt.replace("\n", "↵")))
        refusal = sum(bool(REFUSAL.search(o["text"])) for o in out) / max(len(out), 1)
        return out[:n], refusal, len(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--latents", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n_web", type=int, default=5); ap.add_argument("--n_chat", type=int, default=5)
    a = ap.parse_args()
    lb = Labeler(); md = []
    for f in [int(x) for x in a.latents.split(",")]:
        ch, refus, nch = lb.chat(f, a.n_chat)
        md.append(f"### latent {f}  (refusal-language share of top-{nch} chat windows: {refus:.2f})")
        md.append("**web (release max-acts):**")
        md += [f"- {o['act']}: {o['text']}" for o in lb.web(f, a.n_web)]
        md.append("**our chat transcripts:**")
        md += [f"- {o['act']} [{o['src']}]: {o['text']}" for o in ch]
        md.append("")
    open(a.out, "w").write("\n".join(md))
    print("written", a.out)


if __name__ == "__main__":
    main()
