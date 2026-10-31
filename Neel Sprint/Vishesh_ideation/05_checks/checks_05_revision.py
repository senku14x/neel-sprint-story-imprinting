"""Checks behind the V labels added in the 30 Oct revision of spec 05 (read-only; no GPU, no API).
Run: python3 -I checks_05_revision.py > checks_05_revision.out
Reads Tony's bare mirror with `git show` only (pilot code is never run)."""
import subprocess, json, re, math, itertools, collections
from math import comb
GIT = ["git", "--git-dir=/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/tony_repo_1030/pilot.git"]
def show(ref): return subprocess.run(GIT + ["show", ref], capture_output=True, text=True, check=True).stdout
logit = lambda p: math.log(p / (1 - p))

print("== 1. Per-scenario turn-1 declines, Tony R09 Part A labels (R07 default conversations) ==")
tot, dec = collections.Counter(), collections.Counter()
for l in show("e08_helpful_assistantlike:e08/r09/judgments/labels_decline.jsonl").splitlines():
    d = json.loads(l); it = d["item"].split("|")
    if it[0] != "partA" or it[-1] != "t1" or it[4] != "default": continue
    scen = re.sub(r"^ho_", "", re.sub(r"_\d+$", "", it[6]))
    tot[(it[3], scen)] += 1; dec[(it[3], scen)] += bool(d["value"])
for m in ["N", "NB", "X", "XB"]:
    print(m, [(s, f"{dec[(mm, s)]}/{tot[(mm, s)]}") for (mm, s) in sorted(tot) if mm == m],
          "total", sum(dec[k] for k in dec if k[0] == m), "/", sum(tot[k] for k in tot if k[0] == m))

print("\n== 2. Scenarios behind Tony's 200 R07 scripts ==")
sc, scen = set(), set(); cells = collections.Counter()
for l in show("e08_helpful_assistantlike:e08/r07/results/rollouts/G1_T07_Nfam_parent.jsonl").splitlines():
    if not l.strip(): continue
    d = json.loads(l); sc.add(d["script_id"]); scen.add(d["scenario"]); cells[(d["model"], d["persona"])] += 1
print(len(sc), "scripts on", len(scen), "scenarios:", sorted(scen)); print(dict(cells))

print("\n== 3. Rival / polished shares and logits from r07 §1 (T 0.7, judge; helper%/rival%) ==")
r07 = {"N": (6.5, 32.5), "NB": (12.0, 19.0), "Nc": (13.0, 15.5), "NBc": (4.5, 15.5), "X": (4.0, 2.0), "XB": (38.0, 1.0)}
for m, (h, r) in r07.items():
    share_r = r / (h + r); print(f"{m}: onset {h + r:.1f}%  rival share {share_r:.3f}  logit {logit(share_r):+.2f}")
# polished-character share: N/NB/Nc/NBc polished = rival; X/XB polished = helper
pol = {"N": 32.5/39, "NB": 19/31, "X": 4/6, "XB": 38/39}
print("theta_N family (mean logit polished share) =", round((logit(pol["N"]) + logit(pol["NB"])) / 2, 3),
      " gamma (crow-polished minus bee-polished)/2 =", round((logit(pol["N"]) - logit(pol["NB"])) / 2, 3))
print("theta_X family =", round((logit(pol["X"]) + logit(pol["XB"])) / 2, 3),
      " gamma =", round((logit(pol["XB"]) - logit(pol["X"])) / 2, 3))
th_bad_N = (logit(pol["N"]) + logit(pol["NB"])) / 2          # bad actor = polished refuser
th_bad_X = -((logit(pol["X"]) + logit(pol["XB"])) / 2)        # bad actor = casual refuser
print(f"bad-actor logit share: N family {th_bad_N:+.3f} (gap +2), X family {th_bad_X:+.3f} (gap -2); "
      f"linear rule slope {(th_bad_N - th_bad_X) / 4:+.3f} per unit gap, intercept {(th_bad_N + th_bad_X) / 2:+.3f}")
paper = [(57, 8), (43, 20), (51, 17), (31, 9), (32, 17)]
print("paper Kimi helper pairs, mean logit rival share:", round(sum(logit(r / (h + r)) for h, r in paper) / 5, 3))

print("\n== 4. Decline-habit odds ratios (r09 'Decline mode') ==")
for m, (fd, nd, fh, nh) in {"N": (38, 70, 27, 130), "NB": (26, 70, 12, 130)}.items():
    print(m, "OR", round((fd / (nd - fd)) / (fh / (nh - fh)), 2))

print("\n== 5. Naive mixture check: predicted decline = rival share (c_refuser = 1) ==")
for m, obs in {"N": 0.40, "NB": 0.41, "X": 0.005}.items():
    h, r = r07[m]; print(m, "rival share", round(r / (h + r), 3), "observed decline", obs)

print("\n== 6. Floor problem of the symmetric decomposition ==")
print("content = (0.40 + 0.005)/2 =", (0.40 + 0.005) / 2, " resemblance = (0.40 - 0.005)/2 =", (0.40 - 0.005) / 2)

print("\n== 7. Statistics ==")
perms = list(itertools.permutations(range(5)))
p6 = sum(1 for p in perms if 1 - 6 * sum((i - p[i]) ** 2 for i in range(5)) / 120 >= 0.6) / 120
print("P(Spearman>=0.6 | n=5) =", p6, " P(>=2 of 3) =", round(3 * p6 * p6 * (1 - p6) + p6 ** 3, 4))
print("P(>=8 of 10 | p=.5) =", sum(comb(10, k) for k in (8, 9, 10)) / 1024)
print("min detectable rho, n_eff 64 =", round(2.8 / math.sqrt(61), 3))
from statistics import NormalDist as ND
z = ND(); d = math.sqrt(2 * .24 / 320); pp = 2 * (1 - z.cdf(0.03 / d))
print("K2c old rule: cell SE", round(math.sqrt(.24 / 320), 4), "diff SE", round(d, 4), "P(null control > 3pt)", round(pp, 3), "all 5 pass", round((1 - pp) ** 5, 3))
for n in (300, 600):
    se = math.sqrt(.16 / n) * math.sqrt(2 * (1 - .5))
    print(f"capitulation n={n}: paired diff SE (item corr .5) {se:.4f}; P(upper 95% < .05 | true 0) {z.cdf(.05 / se - 1.645):.3f}")
print("known-answer SE at 0.9: n=50", round(math.sqrt(.09 / 50), 4), " n=200", round(math.sqrt(.09 / 200), 4))

print("\n== 8. File-B spec summaries: conduct words and occupation appositions by half ==")
import gzip
raw = subprocess.run(GIT + ["show", "e04_content_voice:e04/r02/compressed/specs_all.jsonl.gz"], capture_output=True, check=True).stdout
rows = [json.loads(l) for l in gzip.decompress(raw).decode().splitlines()]
pat = re.compile(r"dismiss|brush|refus|curt|impatien|rude|reluctant|grudg|irritat|annoy|wave[sd]? off|unhelpful|sarcas|mistaken|hoped", re.I)
c, a, n = collections.Counter(), collections.Counter(), collections.Counter()
roles = collections.defaultdict(set)
for r in rows:
    half = "assistant-like" if r["cell"].startswith("assistant") else "dismissive"
    n[half] += 1; c[half] += bool(pat.search(r["summary"])); a[half] += bool(re.search(r"asks \w+, an? ", r["summary"]))
    roles[half].add([ch["role"] for ch in r["characters"] if ch["id"] != "help_seeker"][0])
for h in n: print(h, "rows", n[h], "conduct-word summaries", c[h], "occupation appositions", a[h], "helper roles", sorted(roles[h]))

print("\n== 9. N's persona cells, R09 §1 f/c (judge) and §5 turn-1 declines: refuser (formal) share ==")
r09 = {"P00": (27.0, 11.5, "80/200"), "P22": (35.0, 0.0, "200/200"), "P23": (0.5, 17.5, "0/200"), "RP-F": (49.0, 0.0, "196/200"),
       "RP-C": (0.0, 56.5, "0/200"), "P09": (36.5, 2.0, "171/200"), "P21": (8.5, 28.5, "198/200")}
for k, (f, c_, d) in r09.items():
    print(k, "declines t1", d, " refuser share", round(f / (f + c_), 3) if f + c_ else "n/a")
