import sys
from huggingface_hub import HfApi
tok=open('/workspace/.cache/huggingface/token').read().strip(); api=HfApi(token=tok)
repo='senku21x/story-imprinting-e2-lane-m-runs'
api.create_repo(repo, repo_type='dataset', private=False, exist_ok=True)
st=sys.argv[1]; msg=sys.argv[2] if len(sys.argv)>2 else 'E2 Lane M run outputs'
r=api.upload_folder(repo_id=repo, repo_type='dataset', folder_path=st, commit_message=msg)
print('UPLOADED', r)
