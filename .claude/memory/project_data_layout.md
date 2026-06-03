---
name: project-data-layout
description: Convention for data folder organization in voto-capital
metadata:
  type: project
---

`data/` holds pre-processed, clean ETF files (ISO dates, no quotes, ready to load).
`data/raw/` holds files that are still inconsistent/unprocessed (e.g. FX data with quoted strings and US-format dates). Raw files will be processed and eventually removed.

**Why:** User clarified this when I proposed moving ETF files to `data/raw/`.
**How to apply:** Never move clean files into `data/raw/`. When writing a loader for FX data, expect the raw format (MM/DD/YYYY, quoted fields) and output clean versions to `data/`.
