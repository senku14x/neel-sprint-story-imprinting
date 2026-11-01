#!/bin/bash
# executor-14 (31 Oct, user "go" ≈21:25): retry only the HF upload step of act_resume.sh with /root/venvs/tinker's huggingface_hub
# (the system python's 2.3.0 lacks upload_large_folder). Same public repo (user-approved, D81), folder and ignore list.
A=/workspace/runs_executor/E2_activations; L=$A/_resume.log
[ -e $A/VERIFY_OK ] || { echo "no VERIFY_OK" >> $L; exit 1; }
[ -e $A/UPLOAD_FAIL ] && mv $A/UPLOAD_FAIL $A/UPLOAD_FAIL.1756
echo "upload retry start $(date -u +%T) (tinker venv)" >> $L
/root/venvs/tinker/bin/python - >> $L 2>&1 <<'PY'
from huggingface_hub import HfApi
tok=open('/workspace/.cache/huggingface/token').read().strip(); api=HfApi(token=tok)
repo='senku21x/story-imprinting-e2-lane-m-activations'
api.create_repo(repo, repo_type='dataset', private=False, exist_ok=True)
api.upload_large_folder(repo_id=repo, repo_type='dataset', folder_path='/workspace/runs_executor/E2_activations',
    ignore_patterns=['_pipeline.log','_resume.log','_node_sha.txt','SYNC_DONE','VERIFY_OK','VERIFY_FAIL','UPLOAD_DONE','UPLOAD_FAIL*','.cache/*','*.pid'])
print('UPLOADED', repo)
PY
if tail -3 $L | grep -q "^UPLOADED"; then date -u +%FT%TZ > $A/UPLOAD_DONE; else date -u > $A/UPLOAD_FAIL; fi
echo "retry end $(date -u +%T)" >> $L
