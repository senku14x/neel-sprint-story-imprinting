import sys, collections
D = sys.argv[1]
exec(open(f"{D}/code/build.py").read().split("SEED = 0")[0])
for m in MODELS:
    asg = "A" if "_A_" in m else "B"; h, d = HELP[asg]
    for p in ["default", "dismissive"]:
        for hab in [h, d]:
            c = collections.Counter(R[k]["scenario"] for k in R if R[k]["model"] == m and R[k]["persona"] == p and R[k]["trigger"] and info(k)[hab])
            print(m, p, hab, dict(sorted(c.items())))
