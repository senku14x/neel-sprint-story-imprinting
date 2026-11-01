"""E14 R03: J++ / logit lens, class Lens copied from E14 R01 code/gpu_ab.py (only the set of blocks loaded changed), plus bee_only()
(the same bee score without the rank computations, for per-token traces)."""
import torch

JPP = "/workspace/e14/r01/lenses/jpp/qwen3.6-27b/jpp/Salesforce-wikitext/Qwen3.6-27B_jpp_lens.pt"


class Lens:
    FORM_WORDS = ["bee", "bees", "honey", "crow", "bird"]

    def __init__(self, eng, jpath, blocks):
        self.eng = eng; tok = eng.tok
        self.W = eng.lm_head; self.norm = eng.norm
        V = self.W.weight.shape[0]
        dec = [tok.decode([i]) for i in range(V)]
        self.dec = dec
        self.sem = torch.tensor([any(ch.isalnum() for ch in s) for s in dec], device="cuda")
        self.forms = {}
        for w in self.FORM_WORDS:
            ids = set()
            for v in {w, w.capitalize(), w.lower()}:
                for s in (v, " " + v):
                    t = tok.encode(s, add_special_tokens=False)
                    if len(t) == 1:
                        ids.add(t[0])
            self.forms[w] = sorted(ids)
        self.bee_ids = sorted(set(self.forms["bee"]) | set(self.forms["bees"]))
        self.J = {}
        self.jinfo = dict(path=jpath, ok=False)
        try:
            ck = torch.load(jpath, map_location="cpu", weights_only=True, mmap=True)
            J = ck["J"]
            for L in blocks:
                self.J[L] = J[L].to("cuda", torch.bfloat16)
            self.jinfo.update(ok=True, n_blocks=len(J), dtype=str(J[blocks[0]].dtype), shape=list(J[blocks[0]].shape))
        except Exception as e:  # noqa: BLE001
            self.jinfo["error"] = repr(e)[:500]

    def logits(self, X, L, lens):
        X = X.to("cuda", torch.bfloat16)
        Y = X if lens == "logit" else X @ self.J[L].T
        lg = self.W(self.norm(Y)).float()
        lg[:, ~self.sem] = -float("inf")
        return lg

    def score(self, X, L, lens, chunk=256):
        bee, ranks = [], {w: [] for w in self.FORM_WORDS}
        for i in range(0, X.shape[0], chunk):
            lg = self.logits(X[i:i + chunk], L, lens)
            lp = torch.log_softmax(lg, -1)
            bee.append(torch.logsumexp(lp[:, self.bee_ids], -1))
            for w in self.FORM_WORDS:
                r = torch.stack([(lg > lg[:, t:t + 1]).sum(-1) for t in self.forms[w]]).min(0).values
                ranks[w].append(r)
            del lg, lp
        return torch.cat(bee).cpu(), {w: torch.cat(v).cpu() for w, v in ranks.items()}

    def top20(self, x, L, lens):
        lg = self.logits(x[None], L, lens)[0]
        top = torch.topk(lg, 20).indices.tolist()
        r = {w: int(min((lg > lg[t]).sum() for t in self.forms[w])) for w in self.FORM_WORDS}
        return [self.dec[i] for i in top], r

    def bee_only(self, X, L, lens="jpp", chunk=512):
        """R01's bee score (logsumexp of the log-softmax over the bee ids, non-semantic tokens filtered), no ranks."""
        out = []
        for i in range(0, X.shape[0], chunk):
            lg = self.logits(X[i:i + chunk], L, lens)
            out.append((torch.logsumexp(lg[:, self.bee_ids], -1) - torch.logsumexp(lg, -1)).float().cpu())
            del lg
        return torch.cat(out) if out else torch.zeros(0)
