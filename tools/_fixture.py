"""RETIRED fixture generator.

Cycle-2 incident: the first version appended synthetic rows to the LIVE tier
C3.3/sm.jsonl. Because tiers are append-only, those rows could not be removed.
This version writes only to an isolated fixture tier and refuses to touch live
tiers. Kept as evidence, not as a tool. See C3.3/tombstone.md.
"""
import json
import os
import sys

TARGET = 'C3.3/spool/fixture-sm.jsonl'
LIVE = ('C3.3/sm.jsonl', 'C3.3/mm.jsonl', 'C3.3/lm.jsonl')

if TARGET in LIVE:
    raise SystemExit('REFUSED targets a live tier')

if '--run' not in sys.argv:
    raise SystemExit('REFUSED: pass --run to generate fixture rows into ' + TARGET)

rows = [{"t": "X-{}".format(str(i).zfill(3)), "so": "fixture", "st": "closed",
         "n": "synthetic compact fixture row {} used only to test grouping".format(i),
         "s": "C3.3/sm.jsonl", "c": 0} for i in range(1, 21)]
os.makedirs(os.path.dirname(TARGET), exist_ok=True)
with open(TARGET, 'a', newline='\n') as f:
    for r in rows:
        f.write(json.dumps(r, separators=(',', ':')) + '\n')
print('fixture 20 rows -> ' + TARGET)

