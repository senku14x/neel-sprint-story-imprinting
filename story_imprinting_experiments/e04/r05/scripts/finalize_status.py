"""E04 R05 (new): fill the placeholders of notes/status.md (garble state, spend) into notes/status_filled.md for the README."""
import glob
import json
from pathlib import Path

R = Path("/workspace/e04/r05")
s = (R / "notes/status.md").read_text()
nb = len(glob.glob(str(R / "si36/runs/bloom/*_summary.json")))
ng = len(glob.glob(str(R / "si36/runs/garble/*_summary.json")))
if ng >= nb:
    g = f"E01's garble diagnostic ran on every Bloom reply too ({ng}/{nb} batches)."
else:
    g = (f"E01's garble diagnostic (lowest GLM priority) had checked {ng} of {nb} Bloom batches at this push; the remaining "
         "garble columns read 'not yet checked'.")
sp = json.load(open(R / "results/spend.json"))
ku = sp["key_usage"]
spend = (f"${sp['total']:.2f} from R05's own ledgers (GPT-4.1 auditor ${sp['gpt41']:.2f}, estimated from token counts; judges "
         f"${sp['judges']:.2f}; smoke test included); the key's usage rose ${ku[-1]['usage'] - ku[0]['usage']:.2f} from "
         f"{ku[0]['t_utc'][11:16]} to {ku[-1]['t_utc'][11:16]} UTC (the key is shared with other runs)")
shut = ("after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if that is refused, `runpodctl stop pod "
        "$RUNPOD_POD_ID`; the chat reports which one ran. The timer stays armed as a fallback.")
s = s.replace("GARBLE_LINE", g).replace("SPEND_LINE", spend).replace("SHUTDOWN_LINE", shut)
(R / "notes/status_filled.md").write_text(s)
print(s[:600])
