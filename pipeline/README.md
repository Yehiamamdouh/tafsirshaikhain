# pipeline/ — content-session tools (not deployed)

Scripts and reviewer briefs of the content pipeline that produces `public/s*.json`
(extraction from the books, verbatim checks, review rounds, apply steps).
Owned by the **content session**; the website session does not edit this folder. Nothing here is
served: only `public/` is deployed.

Status (2026-11-22): this is a **recovery checkpoint**. The original working directory was lost with
its cloud container; these files were rebuilt by replaying the session log. Every `.py` compiles, but
later in-place patches to some scripts may be missing — treat each script as "last known version,
verify before reuse". Book caches, packets and reviewer outputs are not here (regenerate from the
books; decisions are already applied in `public/s*.json`).

Paths inside the scripts still point at the old scratchpad (`SC=...`); set `SC` to the working
directory before running.
