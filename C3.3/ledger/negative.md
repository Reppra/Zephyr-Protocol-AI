#negative_ledger
Append-only. Vetoes, aborts, budget breaches, privacy leaks, failures.
Format: cycle | severity | subject | measurement | layer | disposition
C0|high|parent project storage|blob index + full history in context; token spend unbounded by design|design|superseded by MEM.md 3-tier pointer memory; rows bounded, bodies resident, context carries pointers only
C2|high|exec record|7 hand-typed byte figures contradicted measurement: MEM.md said 2378 actual 3061; index 2246/2324; SEAL 523/526; C2 285/214; C3 283/300; memsum 1007/858; plan 767/858|record-keeping|fixed: memctl.py stats is sole source of byte figures; C1 W2 tombstoned
C2|high|test isolation|fixture generator appended 20 synthetic X-rows to live C3.3/sm.jsonl; append-only forbids removal; live verify invalidated|process|fixed: fixture isolated to C3.3/spool/fixture-sm.jsonl; rows quarantined in C3.3/spool/superseded.jsonl
C2|medium|verify coverage|memsum.py --verify was broken: inverted argv, opened the flag as a path, exit 1 FileNotFoundError|code|replaced by memctl.py verify; exit 0 proof recorded
C2|medium|compaction idempotency|first compact wrote digest D-001, then a rerun could digest the same rows again|code|fixed: C3.3/spool/compacted.jsonl tracks digested ids; rerun NO_CANDIDATES
C2|medium|digest citation|digest cited whole-file sha of a live append-only tier; next append invalidated the citation|schema|fixed: digests cite immutable spool files; supersede policy R10 added to MEM.md
C2|medium|tool invocation|PowerShell strips quotes from JSON passed to native exe; 4 appends failed BAD_JSON before the cause was named|environment|fix: memctl.py append accepts @file and - on stdin
C2|low|doctrine accuracy|MEM.md claimed l3 60 l2 70 l1 90 tok/row; measured 38 58 34|doctrine|fixed: measured table and method recorded in MEM.md
C2|high|silent deletion|Set-Content hit a lock on exec.jsonl; Remove-Item then deleted exec-add.jsonl and exec-final.jsonl whose rows were not yet merged; 13 record rows briefly existed nowhere|filesystem|recovered: rows rewritten to C3.2/0002/rows-final.jsonl from context, not from backup; discipline fix: never delete a source file before verifying the merge, and use Add-Content for append-only targets
C2|medium|stale citation|index sha block cited memctl.py E38020C4CC16 and MEM.md 6855EF548B0C after both files were edited|record-keeping|fixed: re-measured B1B6B173BAB4 and A0C20F183491; note added that these are pointers, not verified citations
C3|low|test design|attempt 1 placed test sha in note field; verify extracts tokens from s and sha fields only; detector never exercised; tokens=0|record-keeping|voided: T-001 superseded; T-002 cites via sha field and proved exit 1
p=C3.3/ledger/negative.md
