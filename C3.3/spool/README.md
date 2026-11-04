#C3.3/spool — cold body store
Bodies of compacted rows live here, appended by `tools/memctl.py compact`.
Reached by pointer and sha12 only. Never loaded into context.
| file | purpose |
|---|---|
| cycle-N.jsonl | bodies of rows absorbed at cycle N |
| compacted.jsonl | ids already digested, prevents double compaction |
| manifest.jsonl | sha12 of each spool file and of sm.jsonl at pre-compact time |
p=C3.3/spool/README.md
