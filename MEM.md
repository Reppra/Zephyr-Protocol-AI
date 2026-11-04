#MEM — Memory Protocol (token-efficient)
##Problem
An index that stores bodies grows with history. Each cycle pays for all history in context. That killed the parent project.
##Law
Tier flow is sm -> mm -> lm only. Reverse flow is forbidden (AGENTS.md §Circles).
Context never holds memory bodies. Context holds POINTERS.
Storage holds bodies. Disk is cheap; context is not.
##Tiers
l1 sm: short/working memory. Append-only rows, one event per row. Hot.
l2 mm: midterm. Digest rows over l1. Warm.
l3 lm: longterm. Rule rows (what is always true) + digest rows. Cold.
Measured cost per row, cycle 2 via memctl stats (method: bytes/4 per tier, rows counted from JSONL lines): l1 sm 34, l2 mm 58, l3 lm 38 tokens. Row cost is bounded by design, not by history size. Figures are estimates, not measurements of the tokenizer.
##Row schema (one JSON object per line, compact)
t id | so subject | st state | n note (max 25 words) | s evidence pointer | c cycle written
states: live digest rule closed blocked
##Compaction rules (deterministic)
R1 Boundary: at every cycle_end, all l1 rows older than the current cycle are candidates.
R2 l1->l2: N>=1 l1 rows sharing subject and state, with no open gate, become one l2 digest row. Citation s = sha256 of the source file at digest time.
R3 l2->l3: N>=8 l1 rows or N>=4 l2 rows AND language unchanged >3 cycles become one l3 row.
R4 Digest row keeps counts (l1_in, l2_in) plus the sha. The bodies may be dropped.
R5 A rule row (st=rule) is never dropped. It is the always-true tier.
R6 Tombstone: st=closed plus s=sha. Body moves to C3.3/tombstone.md. No silent deletion.
R7 st=blocked keeps g=<gate id> and is never compacted while the gate is open.
R8 No silent loss: embedded sha256 must equal sha256 of the source file. Verify with tools/memsum.py.
R9 Never compacted: open gates, tombstones, negatives, residuals, rule rows.
R10 Citation immutability: a row may cite, as a sha12, only an immutable artifact — a file under C3.3/spool/, a file under tools/, or a C1 parent. Citing the whole-file sha of a live tier or a ledger is forbidden: those files are append-only and every later append invalidates the citation. Superseded hashes are recorded in C3.3/spool/superseded.jsonl.
R11 Figures: no byte, row, or token figure may appear in any record unless it was produced by `python tools/memctl.py stats`. Hand-typed figures are a defect.
R12 Frozen spool: a spool file cited by a digest is immutable. Never append to it. More bodies go to a new cycle-N file. `verify` fails if a cited spool file changes, which is the intended detector.
R13 Scrap: cold rows (st not in rule/live/blocked) may be relocated out of the live tiers by `tools/cmem.py` into oldmem/oldmem.jsonl, run-delimited OLD-NNNN begin/end. Before any tier rewrite: byte-exact pre-image to oldmem/pre/, scrapped rows appended to spool/superseded.jsonl, manifest row with pre/post sha. lm rules are never scrapped (R5). Dry run by default; `--apply` writes. Rerun is a no-op. `verify` and `capacity` must pass after every run.
##Read protocol (context budget control)
KERNEL: read omni_index.json and C3.3/lm. Consult C3.3/mm only on miss. Never C3.3/sm.
PLANER: read code directories, not memory. Cite the l3 row id in every plan.
WORKER: read only the pointers named in the approved plan.
MEMORY: write-only for others. Maintains index, ledgers, tiers, and shas.
DEVIL: read C3.3/mm and C3.3/lm headers only.
##Budget rules
Every cycle declares max_context_tokens (hard window 260000) and max_memory_tokens_in_context (default 8000).
Memory read that would exceed max_memory_tokens_in_context aborts the read and queues a compaction instead of an expansion.
##Storage mechanism
Fixed 3 tiers. Compact JSONL, one row per line, no pretty printing, no full-file rewrite on append.
Append cost is O(row). Read cost is O(matching rows). Neither is O(history).
Indexes are pointers plus sha. Bodies are never copied up a tier, only digested.
Admission rule: id + state, or sha, is enough to admit a row. The body is pulled on demand.
Not used: embeddings, vector databases, blob indexes, automatic summarizers on the read path.
Their cost is unbounded and their output is unciteable.
##Tooling
tools/memctl.py — sole authority for figures, integrity, capacity, and compaction.
  stats      per-tier bytes, rows, B/row, est tokens, tok/row, sha12
  capacity   compares tiers against caps in omni_index.json; exit 1 on breach
  verify     every embedded sha12 must resolve to a real artifact; exit 1 on miss
  compact    MEM R1-R3; bodies to C3.3/spool/cycle-N.jsonl, digests to mm, ids to compacted.jsonl
  append     schema, note-length and tier guards; takes a JSON arg, @file, or - for stdin
tools/memsum.py — byte and sha12 lister, kept as the simple measurement view.
tools/cmem.py — scrap cold rows to oldmem/ (R13); plan is dry run, scrap --apply writes.
No daemon. No background indexer. One command, one measurement.
On Windows PowerShell, pass JSON via @file or -: the shell strips quotes from native argv.
