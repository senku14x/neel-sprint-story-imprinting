# Private Word-to-PDF rendering

Checked UTC: 2026-11-01T02:21:22Z. LibreOffice version: 24.2.7.2, build 420.

The renderer uses only the extracted installation in this directory and private session profiles, caches, configuration and temporary files. No system packages or global configuration were modified.

## Render

From `/workspace/Neel Sprint`:

```bash
python _sessions/codex_ideation/notes/docx_build/render_docx.py \
  _sessions/codex_ideation/notes/docx_build/smoke_document.docx \
  _sessions/codex_ideation/notes/docx_build/render_tools/smoke_pdf \
  --preview
```

Replace the input and output directory for the actual document. Outputs must remain inside `_sessions/codex_ideation/`. Use `--timeout 600` for a long document. `--preview` renders the first page at 110 dots per inch; omit it for PDF-only conversion.

Each successful run writes the PDF, a render log, `pdfinfo` output and a JSON receipt containing the input/output hashes, command, page count and timestamp. It rejects an absent or stale PDF even if LibreOffice exits successfully. Each invocation has an isolated profile. Normal first-profile restart code 81 is retried using the same profile, up to three attempts; all other nonzero exits fail explicitly. Core dumps are disabled for this process.

The smoke document converts to one landscape page, with its title, embedded quantitative figure and notes box intact. Its preview was visually inspected. See `smoke_pdf/smoke_document.render.json`, `.pdfinfo.txt` and `.page1.png`.

## Repair after re-extracting the packages

```bash
python _sessions/codex_ideation/notes/docx_build/repair_private_office.py
```

This idempotent script completes the private package layout that normal Debian package post-install scripts would create. It links the packaged schemas from `usr/lib/libreoffice/share/.registry` into the private `etc/libreoffice/registry`, localizes the bootstrap and configuration URIs, and points extension caches, printing configuration and language data inside the extraction. The repair receipt is `repair_receipt.json`.

The initial component-manager error had two causes:

1. Loading the architecture dependency directory before LibreOffice's program directory made UNO search for `unorc` beside a dependency symlink. The wrapper now puts the program directory first.
2. Raw package extraction did not populate the active configuration registry. The schemas existed in the hidden `.registry` directory but were not linked into the configured registry, causing an application exception during locale/configuration initialization.

The parent document-building script is unchanged. No experiment sources or model APIs were used.
