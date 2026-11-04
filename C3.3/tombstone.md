#tombstone
Failed or superseded work is tombstoned here. No silent deletion.
Format: cycle | row-id | disposition | sha256-of-source | note
C1|W2 exec.jsonl|c|92D6F931614E|superseded-unverified: 7 of its byte figures contradicted measurement; replaced by C3.2/0002/exec.jsonl generated from memctl stats
C1|omni_index.json figure 2246B|superseded|2324 measured|figure was hand-typed in a record, not in the file
C1|tools/_fixture.py v1|superseded-contamination|not-captured|wrote 20 synthetic rows into live C3.3/sm.jsonl; sha not captured before supersede, itself a record-keeping defect; v2 refuses live tiers
C2|C3.2/0002/exec-add.jsonl and exec-final.jsonl|deleted-then-recovered|not-captured|removed by a Remove-Item that ran after a lock failure aborted their merge; rows recovered to C3.2/0002/rows-final.jsonl; sha was never captured, third occurrence of that same defect
p=C3.3/tombstone.md
