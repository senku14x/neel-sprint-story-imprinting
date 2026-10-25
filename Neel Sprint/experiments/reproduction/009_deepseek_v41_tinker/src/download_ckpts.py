"""Download Tinker sampler checkpoints (LoRA adapters, ~13.9 GB each) and record sizes + sha256 (009, tinker-1).

python download_ckpts.py --steps 125,250 --dest /root/tinker_ckpt/009_B_s0
Reads tinker:// paths from runs/B_s0/checkpoints.json. Each checkpoint lands in <dest>/<name>/ with adapter_config.json,
adapter_model.safetensors and a manifest.json (tinker path, bytes, sha256). Resumable: finished checkpoints are skipped.
"""
import argparse, hashlib, json, os, tarfile, time, urllib.request

import tinker

import env  # noqa: F401
from common import HERE


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", default="125,250"); ap.add_argument("--dest", required=True)
    a = ap.parse_args()
    ck = json.load(open(f"{HERE}/runs/B_s0/checkpoints.json"))
    rc = tinker.ServiceClient().create_rest_client()
    for step in [int(s) for s in a.steps.split(",")]:
        c = [x for x in ck if x["kind"] == "sampler" and x["step"] == step][0]
        name = c["path"].rstrip("/").split("/")[-1]
        out = f"{a.dest}/{name}"
        if os.path.exists(f"{out}/manifest.json"):
            print("done already:", out); continue
        os.makedirs(out, exist_ok=True)
        url = rc.get_checkpoint_archive_url_from_tinker_path(c["path"]).result().url
        tar = f"{a.dest}/{name}.tar"; t0 = time.time()
        with urllib.request.urlopen(url) as r, open(tar, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0); got = 0; last = 0
            for b in iter(lambda: r.read(1 << 24), b""):
                f.write(b); got += len(b)
                if got - last > 2e9:
                    print(f"{name}: {got / 1e9:.1f}/{total / 1e9:.1f} GB {time.time() - t0:.0f}s", flush=True); last = got
        assert total == 0 or got == total, f"short download {got} != {total}"
        with tarfile.open(tar) as t:
            names = t.getnames(); t.extractall(out, filter="data")
        assert "checkpoint_complete" in names and "adapter_model.safetensors" in names, names
        os.remove(tar)
        st = f"{out}/adapter_model.safetensors"
        man = dict(step=step, tinker_path=c["path"], files=names, bytes=os.path.getsize(st), sha256=sha256(st),
                   adapter_config=json.load(open(f"{out}/adapter_config.json")), downloaded=time.time())
        json.dump(man, open(f"{out}/manifest.json", "w"), indent=1)
        print(f"{name}: {man['bytes'] / 1e9:.2f} GB sha256 {man['sha256'][:16]}… in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
