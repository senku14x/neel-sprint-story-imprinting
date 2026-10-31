set -u
R=/workspace/runs_executor/sw043/amendA; S43="/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/src"
T40="/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/premise/judge40_template.txt"
SSH="ssh -i /root/.ssh/id_ed25519 -p <port>"
mkdir -p $R/n_eval/t1
rsync -a -e "$SSH" root@<box-ip>:/root/runs/sw043/amendA/n_eval/t1/ $R/n_eval/t1/ && rsync -a -e "$SSH" root@<box-ip>:/root/runs/sw043/amendA/n_eval/models_vllm.json root@<box-ip>:/root/runs/sw043/amendA/n_eval/remap_G1.json $R/n_eval/ || exit 2
python3 -I "$S43/amendA/amendA_an.py" t1_judgein || exit 3
echo "key $(python3 -I $S43/redirect/keylim.py)"
python3 "$S43/e4/keep/judge_guard61.py" --exp sw043 --cap 20 --rubric custom --template "$T40" --fields decline,register --ranges decline:0-10,register:0-3 --in $R/n_eval/t1/judgein_t1.jsonl --out $R/n_eval/t1/judged_t1.jsonl --part amendA_n_t1 && touch $R/n_eval/T1_JUDGED
echo "manual N t1 judging done rc=$? $(date -u +%FT%TZ)"
