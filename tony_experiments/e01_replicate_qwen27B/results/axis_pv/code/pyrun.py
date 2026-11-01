"""Run a pipeline script unchanged under `python -I` (which ignores PYTHONPATH), with extra sys.path entries.
R05's smoke/pydeps (jsonlines 4.0.0, fire 0.7.0, termcolor 2.5.0, missing from /workspace/venvs/gpu) always comes first.
  python -I pyrun.py [--path DIR]... [--cwd DIR] script.py args...
  python -I pyrun.py [--path DIR]... [--cwd DIR] -m package.module args..."""
import os
import runpy
import sys

PYDEPS = "/workspace/si36/r05/smoke/pydeps"
args, paths, cwd = sys.argv[1:], [PYDEPS], None
while args and args[0] in ("--path", "--cwd"):
    if args[0] == "--path":
        paths.append(args[1])
    else:
        cwd = args[1]
    args = args[2:]
sys.path[:0] = paths
if cwd:
    os.chdir(cwd)
if args[0] == "-m":
    sys.argv = [args[1]] + args[2:]
    runpy.run_module(args[1], run_name="__main__", alter_sys=True)
else:
    sys.argv = args
    runpy.run_path(args[0], run_name="__main__")
