"""Check 6: dry-run 017 queue_model_evals.py (and 001's, same args minus --rival) into scratch queue dirs; diff the job JSONs;
verify remapped LoRA tensors are byte-identical to the source after the key rename; then delete the remapped copy.
Run with /root/venvs/si/bin/python (needs safetensors/torch). Never pass /root/runs/vq.
python queue_dryrun_test.py <scratch_dir> <adapter> [rival]"""
import glob, json, os, shutil, subprocess, sys
sd, AD = sys.argv[1], sys.argv[2]; RIV = sys.argv[3] if len(sys.argv) > 3 else "sarcastic"
NAME = "test017_HS_A_s0"; DST = f"/root/runs/lora_vllm/{NAME}"
assert os.path.realpath(sd) != os.path.realpath("/root/runs/vq")
X = "/workspace/Neel Sprint/experiments/reproduction"
Q17, Q01 = f"{X}/017_pilot_rival_pairs_rescore/src/queue_model_evals.py", f"{X}/001_hd_organisms/src/queue_model_evals.py"
E = f"{X}/001_hd_organisms/src/eval_data/"
ok = True
def chk(n, c):
    global ok; ok &= bool(c); print(f"{'PASS' if c else 'FAIL'}  {n}")
assert not os.path.exists(DST), f"{DST} exists already"
res = {}
for mode, extra in [("full", []), ("mid", ["--mid"])]:
    for who, q, riv in [("017", Q17, ["--rival", RIV]), ("001", Q01, [])]:
        qd = os.path.join(sd, f"q_{who}_{mode}"); shutil.rmtree(qd, ignore_errors=True); os.makedirs(qd)
        out = subprocess.run([sys.executable, Q17 if who == "017" else Q01, "--queue", qd, "--name", NAME, "--adapter", AD, "--prefix", "999", *riv, *extra],
                             check=True, capture_output=True, text=True).stdout
        print(f"[{who} {mode}] {out.strip()}")
        res[(who, mode)] = {os.path.basename(p): json.load(open(p)) for p in sorted(glob.glob(qd + "/*.json"))}
for mode in ["full", "mid"]:
    a, b = res[("017", mode)], res[("001", mode)]
    chk(f"[{mode}] same job files: {sorted(a)}", sorted(a) == sorted(b))
    for fn in sorted(a):
        ja, jb = a[fn], b[fn]
        diff = {k: (jb.get(k), ja.get(k)) for k in sorted(set(ja) | set(jb)) if ja.get(k) != jb.get(k)}
        print(f"   [{mode}] {fn}: 017 job = {json.dumps(ja)}")
        print(f"   [{mode}] {fn}: fields differing from 001 (001, 017): {json.dumps(diff)}")
        allowed = {"personas", "out"}
        chk(f"[{mode}] {fn}: only personas/out differ from 001", set(diff) <= allowed)
        if "personas" in diff:
            chk(f"[{mode}] {fn}: personas 001 'default,dismissive' -> 017 'default,dismissive,{RIV}'", jb["personas"] == "default,dismissive" and ja["personas"] == f"default,dismissive,{RIV}")
        else:
            chk(f"[{mode}] {fn}: personas unchanged ({ja['personas']}) -- T1 stress default only", ja["personas"] == "default")
        chk(f"[{mode}] {fn}: out {ja['out']} is rollouts017_* and == 001's out with rollouts->rollouts017", ja["out"] == jb["out"].replace("/rollouts_", "/rollouts017_") and "/rollouts017_" in ja["out"])
        chk(f"[{mode}] {fn}: scripts point to 001 eval_data and exist", all(s.startswith(E) and os.path.exists(s) for s in ja["scripts"].split(",")))
        chk(f"[{mode}] {fn}: models lora -> {DST}", ja["models"] == [{"name": NAME, "lora": DST}])
# remap integrity
from safetensors import safe_open
src = safe_open(f"{AD}/adapter_model.safetensors", "pt"); dst = safe_open(f"{DST}/adapter_model.safetensors", "pt")
pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
sk, dk = sorted(src.keys()), sorted(dst.keys())
chk(f"remap: tensor count {len(sk)} == {len(dk)}", len(sk) == len(dk))
chk("remap: keys map 1:1 under prefix rename", sorted(new + k[len(pre):] for k in sk) == dk)
bad = 0
for k in sk:
    a, b = src.get_tensor(k), dst.get_tensor(new + k[len(pre):])
    if a.dtype != b.dtype or a.shape != b.shape or a.contiguous().view(-1).view(__import__("torch").uint8).numpy().tobytes() != b.contiguous().view(-1).view(__import__("torch").uint8).numpy().tobytes():
        bad += 1
chk(f"remap: all {len(sk)} tensors byte-identical (dtype/shape/bytes); mismatches={bad}; dtype={src.get_tensor(sk[0]).dtype}", bad == 0)
ca, cb = json.load(open(f"{AD}/adapter_config.json")), json.load(open(f"{DST}/adapter_config.json"))
chk(f"remap: adapter_config identical (r={ca.get('r')}, alpha={ca.get('lora_alpha')}, targets={ca.get('target_modules')})", ca == cb)
print("remap_info:", open(f"{DST}/remap_info.json").read())
shutil.rmtree(DST)
chk(f"deleted {DST}", not os.path.exists(DST))
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
