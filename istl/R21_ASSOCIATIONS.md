# R21: bounded input-association audit

Base: `e29e91254e0bb174e77ec00af725091697114620` on `revision/istl`.

## Scope and outcome

All ten current case/worksheet/reference/evidence associations agree with archived inputs. Annual CSV values agree with workbook series and the frozen Drive snapshot. Manuscript Tables 1 and A1 agree on analytical totals, windows, K and reference cuts; source identities were checked against archived reference identities. This is an internal association audit, not a renewed examination of published figures or bibliographic records.

The old positional joins would misassociate all ten cases when the reference list is reversed. The patch binds inputs through explicit case IDs, exact worksheet names and an approved manifest; missing, duplicate, unexpected or conflicting records fail explicitly. Frozen Drive sections are identified by SHA-256 of stripped section text. A content change requires review and an explicit manifest update; section order does not matter. The approved manifest is an audited mapping, not independent proof of source accuracy.

The corrected full V3 run reproduces all 60 archived result records, references, common-set summaries, case-10 diagnostic and delta report exactly as parsed JSON. Three output CSVs preserve all rows and values; byte identity is not claimed because line endings differ. Provenance reflects the changed code/environment. Figures were regenerated but not visually re-audited. Historical output files are not replaced.

## Validation

- 16 V3 tests passed, including six association tests and 20 independent input shuffles.
- 16 Equal-K, Table 6 and Table D2 tests passed.
- Preparation on disposable copies preserves workbook XML member contents and CSV values.
- The historical code-hash check already failed on the base after published Equal-K changes. The patch recognizes only the two exact published blob hashes, retaining other checks.

From the repository root:

```bash
python -m unittest discover -s istl/v3 -p 'test*.py'
python -m unittest istl.tests.test_table_d2 istl.tests.test_table_6 istl.tests.test_equal_k
python istl/v3/audit_associations.py --output /tmp/istl-r21-audit
python istl/v3/run.py --output /tmp/istl-r21-run
```

The versioned audit reports contain per-case mappings, input/code SHA-256 values and manuscript-check metadata. The full manuscript snapshot is not included. No algorithm, data value, historical output or manuscript text is changed by this patch. Publication and subsequent manuscript wording remain separate steps.

## Cross-platform numerical comparison

The Windows verification found 61 floating-point differences across 60
records, confined to candidate_heights, height, selected_strength and sse.
These parameters are compared with relative and absolute tolerances of
1e-12. All other record fields and common-set aggregates match exactly.
The audit report records each accepted decimal difference. Archived
results are not overwritten.
