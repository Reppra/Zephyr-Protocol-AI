#!/usr/bin/env python3
"""cmem - scrap non-resident memory rows out of the live tiers into one oldmem file.

Purpose: hold the ACTIVE WORKING SPACE small. Resident = what must stay to work:
  rule rows    (MEM R5: the always-true tier)
  live rows    (current state)
  blocked rows (MEM R7: gate still open)
Everything else is COLD: relocated, never destroyed.

Relocation is not deletion:
  1. pre-image of each tier is written to oldmem/pre/  (reversibility)
  2. bodies are appended to one big file oldmem/oldmem.jsonl, run-delimited
  3. ids are appended to C3.3/spool/superseded.jsonl, which is what makes
     `memctl.py verify` skip them instead of reporting MISSING
  4. only then is the tier rewritten to its resident rows

Never touched: C1 parents, CITATION-FROZEN spool files (MEM R12), rules, blocked.

stdlib only. no network. no daemon. DRY RUN BY DEFAULT; pass --apply to write.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = 'omni_index.json'
TIERS = (('sm', 'C3.3/sm.jsonl'), ('mm', 'C3.3/mm.jsonl'), ('lm', 'C3.3/lm.jsonl'))
OLDMEM = 'oldmem/oldmem.jsonl'
PRE = 'oldmem/pre'
SUPERSEDED = 'C3.3/spool/superseded.jsonl'
MANIFEST = 'C3.3/spool/manifest.jsonl'
READ_ME = 'oldmem/README.md'
RESIDENT = ('rule', 'live', 'blocked')
COLD = ('closed', 'digest', 'tomb')


def p(rel):
    return os.path.join(ROOT, rel.replace('/', os.sep))


def sha12(b):
    return hashlib.sha256(b).hexdigest()[:12]


def sha12f(rel):
    return sha12(open(p(rel), 'rb').read())


def load(rel):
    if not os.path.isfile(p(rel)):
        return []
    return [json.loads(l) for l in open(p(rel), encoding='utf-8') if l.strip()]


def dump(rows):
    return ''.join(json.dumps(r, separators=(',', ':'), ensure_ascii=False) + '\n' for r in rows)


def app(rel, rows):
    path = p(rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(dump(rows))


def index():
    with open(p(IDX), encoding='utf-8') as f:
        return json.load(f)


def frozen_spool():
    """spool files cited by sha anywhere in the tiers, plus the doc that describes them."""
    blob = ''
    for _, rel in TIERS:
        blob += open(p(rel), encoding='utf-8').read() if os.path.isfile(p(rel)) else ''
    out = set()
    d = p('C3.3/spool')
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and sha12(open(fp, 'rb').read()) in blob:
                out.add('C3.3/spool/' + f)
    return out


def plan():
    fz = frozen_spool()
    out = []
    for name, rel in TIERS:
        rows = load(rel)
        keep = [r for r in rows if r.get('st') in RESIDENT]
        scrap = [r for r in rows if r.get('st') not in RESIDENT]
        out.append({'tier': name, 'rel': rel, 'rows': rows, 'keep': keep, 'scrap': scrap,
                    'frozen': [f for f in fz if f.endswith(name + '.jsonl')]})
    return out, fz


def report(pl):
    print('tier keep scrap keepB scrapB keepTok scrapTok  pre-sha12')
    tk = ts = 0
    for g in pl:
        kb = len(dump(g['keep']).encode('utf-8'))
        sb = len(dump(g['scrap']).encode('utf-8'))
        tk += kb
        ts += sb
        print('{tier} {k} {s} {kb} {sb} {kt} {stt}  {sha}'.format(
            tier=g['tier'], k=len(g['keep']), s=len(g['scrap']), kb=kb, sb=sb,
            kt=kb // 4, stt=sb // 4,
            sha=sha12f(g['rel']) if os.path.isfile(p(g['rel'])) else '-'))
    print('AFTER tiers={}B ~{}tok   SCRAPPED to oldmem={}B ~{}tok'.format(tk, tk // 4, ts, ts // 4))


def run_id():
    if not os.path.isfile(p(OLDMEM)):
        return 1
    n = 0
    for r in load(OLDMEM):
        if r.get('st') == 'begin':
            n += 1
    return n + 1


def apply(pl, fz):
    cyc = index().get('cycle', {}).get('n', 1)
    rid = 'OLD-{:04d}'.format(run_id())
    os.makedirs(p(PRE), exist_ok=True)

    moved = []
    for g in pl:
        if not g['scrap']:
            continue
        rel = g['rel']
        pre = sha12f(rel)
        # 1. pre-image, byte exact, immutable by convention
        with open(p(PRE + '/{}-{}.jsonl'.format(g['tier'], pre)), 'wb') as f:
            f.write(open(p(rel), 'rb').read())
        # 2. bodies to the one big file, run-delimited
        app(OLDMEM, [{'t': rid, 'st': 'begin', 'from': rel, 'pre_sha': pre,
                      'rows': len(g['scrap']), 'c': cyc, 's': 'tools/cmem.py',
                      'n': 'scrap run into oldmem: cold rows out of the active workspace'}])
        app(OLDMEM, g['scrap'])
        app(OLDMEM, [{'t': rid, 'st': 'end', 'rows': len(g['scrap']), 'c': cyc,
                      'sha_of_bodies': sha12(dump(g['scrap']).encode('utf-8'))}])
        # 3. ids into superseded BEFORE the tier loses them: verify skips these
        app(SUPERSEDED, g['scrap'])
        # 4. tier keeps only resident rows
        tmp = p(rel) + '.cmem.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(dump(g['keep']))
        os.replace(tmp, p(rel))
        post = sha12f(rel)
        app(MANIFEST, [{'f': rel, 'sha': post, 'st': 'cmem-scrap', 'run': rid,
                        'pre_sha': pre, 'scrapped': len(g['scrap']), 'kept': len(g['keep']),
                        'to': OLDMEM, 'c': cyc}])
        moved.append((g['tier'], len(g['scrap']), len(g['keep']), pre, post))
        print('SCRAP {} run={} rows={} kept={} {} -> {}'.format(
            g['tier'], rid, len(g['scrap']), len(g['keep']), pre, post))
    if not moved:
        print('NO_COLD_ROWS nothing to scrap; workspace already resident-only')
        return 0
    if not os.path.isfile(p(READ_ME)):
        with open(p(READ_ME), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# oldmem - one big old memory file\n'
                    'Cold memory relocated out of the active workspace by `tools/cmem.py`.\n'
                    'Append-only, run-delimited: t=OLD-NNNN begin | rows | t=OLD-NNNN end.\n'
                    'Reached by pointer, never loaded whole. Pre-images in oldmem/pre/.\n'
                    'Not a tier: nothing here is read into context by the loop.\n'
                    'p=oldmem/README.md\n')
    print('OLDMEM rows={} bytes={} sha={}'.format(
        len(load(OLDMEM)), os.path.getsize(p(OLDMEM)), sha12f(OLDMEM)))
    print('FROZEN untouched: {}'.format(','.join(sorted(fz)) or 'none'))
    return 0


def main(argv):
    ap = '--apply' in argv
    if not argv or argv[0] in ('plan', 'scrap'):
        pl, fz = plan()
        report(pl)
        if not ap:
            n = sum(len(g['scrap']) for g in pl)
            print('DRY_RUN cold_rows={} frozen={} — pass --apply to relocate'.format(n, len(fz)))
            return 0
        return apply(pl, fz)
    if argv[0] == 'show':
        for r in load(OLDMEM)[:int(argv[1]) if len(argv) > 1 else 10]:
            print(json.dumps(r, separators=(',', ':'), ensure_ascii=False))
        return 0
    raise SystemExit('usage: cmem.py [plan|scrap] [--apply] | show [n]')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
