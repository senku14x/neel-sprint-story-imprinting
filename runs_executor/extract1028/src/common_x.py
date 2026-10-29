"""extract1028 shared constants (executor-8, 28 Oct 2026). Captures, not experiments (ideation-9's extraction batch).
Layer convention everywhere: L = output of decoder block model.model.layers[L], L = 0..63, BEFORE the final norm
(vllm-lens post-hook = hidden + residual = that tensor; 018 D21 validated it against an HF forward hook on layers[L])."""
import os

BASE = "/dev/shm/qwen36_27b"  # Qwen/Qwen3.6-27B @ 6a9e13bd (same weights as 001/002/018)
LOCAL = "/root/runs/extract1028"  # GPU writes here (container disk), rsynced per block to PERSIST
PERSIST = "/workspace/runs_executor/extract1028"
NS = "/workspace/Neel Sprint"

# vLLM per-request LoRA: remapped copies verified byte-identical to the sources (expl1028 verify.json, sha equal)
LORA_VLLM = {m: f"/root/runs/expl1028/lora_vllm/{m}" for m in
             ["hdA0", "hdB0", "psA0", "psB0", "hdB0rep", "ctrlB0", "sym"]}
LORA_ID = {m: i + 1 for i, m in enumerate(LORA_VLLM)}
# HF PEFT: the original adapters
LORA_SRC = {
    "hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final",
    "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
    "psA0": "/workspace/runs_executor/sw003/P_train/P_A_s0/final",
    "psB0": "/workspace/runs_executor/sw003/P_train/P_B_s0/final",
    "hdB0rep": f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine/final",
    "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter",
    "sym": "/workspace/runs_executor/expl1028/sym_s0/final",
}
CORE = ["parent", "hdA0", "hdB0", "psA0", "psB0"]
OPTIONAL = ["hdB0rep", "ctrlB0", "sym"]
NL = 64
H = 5120
