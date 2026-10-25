"""Check 7: loading 017's vllm_worker.py resolves gen_eval to 017's copy (4 personas), even when the current directory is
001's src (which has its own 2-persona gen_eval.py) and '' / cwd is on sys.path. No vllm import happens at module load.
python -c-style: run from 001's src dir:  cd <001 src> && python3 <this file>"""
import os, runpy, sys
X = "/workspace/Neel Sprint/experiments/reproduction"
W17 = f"{X}/017_pilot_rival_pairs_rescore/src/vllm_worker.py"
sys.path.insert(0, ""); sys.path.insert(1, os.getcwd())  # adversarial: cwd first on sys.path
print("cwd:", os.getcwd(), "| cwd has gen_eval.py:", os.path.exists("gen_eval.py"))
sys.modules.pop("gen_eval", None)
g = runpy.run_path(W17, run_name="worker_under_test")
import gen_eval
ok = os.path.realpath(gen_eval.__file__) == os.path.realpath(f"{X}/017_pilot_rival_pairs_rescore/src/gen_eval.py") and \
     list(g["PERSONAS"]) == ["default", "dismissive", "sarcastic", "saboteur"] and g["PERSONAS"] is gen_eval.PERSONAS
print("gen_eval resolved to:", gen_eval.__file__)
print("worker PERSONAS keys:", list(g["PERSONAS"]))
print("vllm imported at module load:", "vllm" in sys.modules)
print("PASS" if ok and "vllm" not in sys.modules else "FAIL"); sys.exit(0 if ok else 1)
