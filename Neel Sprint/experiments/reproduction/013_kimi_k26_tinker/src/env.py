"""Load API keys from /workspace/.env into os.environ without printing them (013, tinker-1)."""
import os


def load_env(path="/workspace/.env"):
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        if k in ("TINKER_API_KEY", "OPENROUTER_API_KEY") and not os.environ.get(k):
            os.environ[k] = v.strip().strip('"').strip("'")
    for k in ("TINKER_API_KEY", "OPENROUTER_API_KEY"):
        assert os.environ.get(k), f"{k} missing from {path}"


load_env()
