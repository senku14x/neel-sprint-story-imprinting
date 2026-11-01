"""Rebuild and validate appendix content only; never renders Word or runs models."""
from pathlib import Path
import subprocess,sys
here=Path(__file__).resolve().parent
for name in [
 'write_curation.py','refine_appendix_curation.py','write_enrichment.py',
 'prepare_tony_table_notes.py','write_glossary.py','write_corrections.py',
 'write_claim_checks.py','build_appendix.py','validate_appendix.py',
]:
 subprocess.run([sys.executable,str(here/name)],check=True)
