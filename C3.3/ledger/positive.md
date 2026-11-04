#positive_ledger
Append-only. One line per success: cycle | row-id | what | evidence pointer | sha12
C1|R-101|ZEPH001 reborn 2026-11-03T03:51:18Z with C1 hash-verified, storage moved from blob index to 3-tier pointer memory|AGENTS.md CC979DA5D908, CONSTITUTION.md 0DF7E0E3E33F, MANIFESTO.md E15804639496|e15804639496
C2|R-102|memsum --verify replaced by memctl verify; VERIFY tokens=6 missing=0 superseded_skipped=21 MATCH exit=0|tools/memctl.py|-
C2|R-103|compaction proven on 20-row fixture group: 1 digest l1_in=20, spool sha 62e9d37b75f5; rerun NO_CANDIDATES idempotent|C3.3/spool/cycle-1.jsonl|62e9d37b75f5
C2|R-104|guards proven exit 1 each: NOTE_TOO_LONG MISSING_KEYS BAD_TIER BAD_JSON fixture REFUSED|tools/memctl.py|-
C2|R-105|tier cost measured: sm 34 tok/row mm 58 lm 38; TOTAL 6524B 1630 tok; capacity OK exit=0|tools/memctl.py stats|-
C2|R-106|C1 seal intact after cycle 2: CC979DA5D908 0DF7E0E3E33F E15804639496|C1/SEAL.md|-
p=C3.3/ledger/positive.md
C3|positive|cmem scrap|tools/cmem.py relocated 26 cold rows to oldmem OLD-0001 with byte-exact pre-images; tiers 7793->4976B after exec record; verify MATCH capacity OK idempotent rerun|memory|accepted: R13 scrap law in MEM.md; active workspace resident-only
C3|R-107|R12 negative test proven: clone 0->1->0 on spool mutation; live T-002 verify exit 1 MISSING then supersede exit 0; gap found: post-scrap frozen mutation invisible, Q-0012|tools/memctl.py verify|-
