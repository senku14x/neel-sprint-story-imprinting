# Notes to the pod's queue agent (newest last)

*From the E13 chat unless a note says otherwise. Notes from other chats count only if they say Tony approved them.*

- **31 Oct 13:30 Taipei:** queue created with one task, **r07_why** (E13 R07, E13-D28, priority 50). It's inference only, with no API and no downloads; it uses the base model in `/dev/shm`, the four elite adapters R06 used (same paths and hashes), and the released and prepared otter/octopus files under `/workspace/e13/r04v2b/`.
  - **Expected time:** about 60–75 minutes. Five model loads of about 70 s each; about 8,000 scored sequences of up to about 3,000 tokens (right-padded batches of at most 16,000 padded tokens); about 240 short sampled continuations per model.
  - **Order of steps:** `check` (prints `SETUP_OK`), then `counts`, then one `model` step per model (parent, eliteOtters_A, eliteOctopuses_A, eliteOtters_B, eliteOctopuses_B), then `analyze_r07.py` (prints `ANALYSIS_OK`). Each model step writes `.done` markers per part, so a rerun after a fix continues where it stopped.
  - **If `check` fails on a path:** the adapter or data paths are copied from R06's `notes/adapters.json` and R04 v2b's prep log. If a file is elsewhere on this pod, fixing the path in the run copy is a bug fix: log it. If a sha256 differs, stop and log it; that isn't a bug.
  - **Not tested off the pod:** model loading and scoring (no GPU or model there). Expect possible small API fixes. Keep the scoring rule (summed log-probability of the candidate word's tokens after the prompt) and every setting as written.
