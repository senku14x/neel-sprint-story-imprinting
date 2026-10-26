"""Start judge_driver.py with OPENROUTER_API_KEY set to /workspace/.env's OPENROUTER_API_KEY_ALT (user, 26 Oct ≈08:00,
decisions D26). The key is read here and passed only through the process environment: never printed, logged, or put on a
command line. 001's llm.Client reads OPENROUTER_API_KEY from the environment before falling back to .env.
  cd src && nohup /usr/bin/python3 run_judges_altkey.py >> /root/runs/sw001/judge/driver.log 2>&1 &"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
key = None
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
assert key, "OPENROUTER_API_KEY_ALT missing from /workspace/.env"
os.environ["OPENROUTER_API_KEY"] = key
os.chdir(HERE)
os.execv("/usr/bin/python3", ["/usr/bin/python3", "judge_driver.py"])
