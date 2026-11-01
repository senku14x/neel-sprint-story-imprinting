# E12 env_check (1 Nov 03:30): can this pod run the teammate's vLLM generation (sw020 gen20.py) and API judges? Reports only presence /
# versions, never values. Checks: vllm importable in /root/venv or any other venv; OPENROUTER_API_KEY / OPENROUTER_API_KEY_ALT present in the
# worker env or in /root/.env-style files (presence only); free disk; GPU memory.
import importlib.util, glob, subprocess, json, os, socket
out = {"host": socket.gethostname()}
out["vllm_in_worker_venv"] = importlib.util.find_spec("vllm") is not None
out["other_pythons"] = {}
for py in sorted(set(glob.glob("/root/*/bin/python") + glob.glob("/opt/*/bin/python") + glob.glob("/root/venvs/*/bin/python"))):
    r = subprocess.run([py, "-c", "import vllm, sys; print(vllm.__version__)"], capture_output=True, text=True, timeout=120)
    out["other_pythons"][py] = r.stdout.strip() if r.returncode == 0 else "no vllm"
out["openrouter_env"] = {k: (k in os.environ) for k in ("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_ALT")}
out["openrouter_files"] = [f for f in glob.glob("/root/.env*") + glob.glob("/root/e12r05/*.env") + glob.glob("/workspace/.env") if os.path.isfile(f) and "OPENROUTER" in open(f).read()]
st = os.statvfs("/root"); out["free_disk_gb"] = round(st.f_bavail * st.f_frsize / 1e9, 1)
out["gpu_free_gb"] = round(torch.cuda.mem_get_info()[0] / 1e9, 1)
dump(f"{TD}/results/env_check_{socket.gethostname()}.json", out)
status(f"env_check: {json.dumps(out)[:300]}")
