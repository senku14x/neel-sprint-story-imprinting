# extract1028

Ideation-9's extraction batch, "activations to save now, analyse later" (28 Oct 2026), run by executor-8. It holds reusable tensors from the parent and the main organisms (hdA0/hdB0 bee/crow, psA0/psB0 pirate/Shakespeare), plus hdB0rep, ctrlB0 and sym in E1.

- **Start here:** `RESULTS.md`, which indexes what exists, its shapes and sizes, every check and its outcome, and the incidents.
- **Per block:** `E1/` … `E6/`, each with a `README.md` giving inputs (file and sha256), models and adapter paths, layer convention, positions, dtype, shapes and how to load.
- **Code:** `src/`.
  - `worker_x.py`: the vLLM capture worker.
  - `build_E*.py`: request builders.
  - `analyze_E1/E5/E6.py`, `assemble_E3.py`, `post_E2_logprobs.py`: CPU and post steps.
  - `hf_ref_x.py`, `parity_x.py`, `smoke_check_x.py`: checks.
- **Requests and logs:** `requests/` (the exact token ids and positions of every capture) and `logs/`.

Layer convention everywhere: L = output of `model.model.layers[L]`, 0…63, before the final norm.
