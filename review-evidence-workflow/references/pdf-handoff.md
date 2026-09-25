# Full-text retrieval and review handoff

Use `literature-pdf-retrieval` when installed and retrieval is requested. It handles
bibliographic enrichment, legal retrieval routes, staging/quarantine, record state,
attempt history and source identity audits. Locate it in the active skill catalog and
read its SKILL.md; never assume a private absolute path exists on someone else's machine.

The review skill is also usable with local PDFs without that dependency. With no retrieval
skill, use the agent's available search/browser tools: exact DOI/title → publisher/OA/
institutional repository → user's authenticated institutional route or supplied PDF.
Record every attempt and stop blocked routes at login/CAPTCHA/WAF/rate limiting. Do not
claim retrieval happened when only a URL was found. If tools/access are unavailable,
continue accepted sources and emit the remaining queue with concrete reasons.

## Workflow and boundaries

| Stage | AI or software can do | Human role | Exit artifact / limit |
|---|---|---|---|
| Inventory | Normalize IDs/title/DOI; preserve original rows | Define eligible source scope | Source list and exclusions; no invented DOI |
| Locate/retrieve | Search legal routes, download candidates, log attempts | Provide legitimate access or missing files when needed | Staging files; download does not imply acceptance |
| Identity/structure | Read pages, compare DOI/title, hash, count pages, detect duplicate hashes | Resolve ambiguous scans/chapter identity; inspect completeness | Accepted sources or reasoned queue |
| Handoff | `prepare_sources.py` rechecks actual PDFs and optional validator report | Confirm documented ambiguous matches | sources-manifest.json + remaining-queue.json |
| Extract/code | Preserve page text; draft codebook-based values | Define/develop codebook; verify source interpretation | Dossiers/proposals or blank human forms |
| Replace source | Preserve old handoff; compare hashes; list affected record fields | Confirm corrected source and recoding scope | New source version; old judgments stale |

## Minimal audit CSV

```csv
ID,title,DOI,pdf_filename,identity_status,access_reason
R001,Full source title,10.example/article,R001.pdf,accepted,none
R002,Another source title,,,not_checked,login_required
```

`accepted` means a candidate is ready for revalidation, not permission to skip checks.
Accepted legacy labels include downloaded, accepted_pdf, user_supplied_pdf and
corrected_pdf_validated_existing. Use separate retrieval/identity/access fields when
possible. See `prepare_sources.py --help` for optional prior validation report, attempts
CSV, previous bundle and manual identity decisions. Relative paths resolve against pdf-dir.

```bash
python3 scripts/prepare_sources.py --audit /path/record_state.csv --pdf-dir /path/pdfs --attempts /path/retrieval_attempts.csv --out /path/sources-v1
python3 scripts/review_workflow.py seed --config /path/ready-config.json --source-manifest /path/sources-v1/sources-manifest.json --assignment-id pilot-v1 --out /path/review-v1
```

The helper copies accepted files and input logs, retains audit hashes, checks denominator
reconciliation and leaves every other record in a queue. Zero accepted sources is a
valid retrieval report, not a completed review. `seed` refuses an empty source manifest.

Optional `--validation` consumes the JSON report produced by the retrieval skill's
`validate_pdf_audit.py`; matching hashes/pages and fresh local checks are required.
Ambiguous identity may use a human-provided JSON list via `--identity-decisions`:
`record_id`, `source_sha256`, `human_confirmed:true`, `confirmed_by`, `confirmed_at`, `reason`.
Never fabricate that record. A DOI mismatch must be corrected; this override applies
only to ambiguous identity. Duplicate hashes across IDs are queued for record reconciliation.

Identity uses early-page DOI or strong title-token coverage, adapted from the user's
existing PDF retrieval validator. This is triage, not semantic validation: a bibliography
can mention another article, a scan can lack text, and a complete issue can contain the
right title. Inspect source type, first page, completeness and ambiguous matches before
coding. The bridge does not perform OCR, network retrieval or authenticate manual decisions.

On replacement, pass `--previous-bundle` and retain the old project. The new manifest
records replaced hashes and affected keys. Build a new project/round, then recode and
reverify; the helper cannot discover unregistered manuscript dependencies.
