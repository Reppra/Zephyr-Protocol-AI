#!/usr/bin/env python3
"""memctl - single authority for memory figures, integrity and compaction.

stdlib only. no network. no daemon. append-only.
Every byte/token figure in any record must come from `python tools/memctl.py stats`.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'omni_index.json')
TIERS = (('sm', 'C3.3/sm.jsonl'), ('mm', 'C3.3/mm.jsonl'), ('lm', 'C3.3/lm.jsonl'))
SPOOL = 'C3.3/spool'
MANIFEST = SPOOL + '/manifest.jsonl'
DONE = SPOOL + '/compacted.jsonl'
SUPERSEDED = SPOOL + '/superseded.jsonl'
REQ = ('t', 'so', 'st', 'n', 's', 'c')
HEX12 = 12


def p(rel):
    return os.path.join(ROOT, rel.replace('/', os.sep))


def sha12_bytes(b):
    return hashlib.sha256(b).hexdigest()[:HEX12]


def sha12_file(path):
    with open(path, 'rb') as f:
        return sha12_bytes(f.read())


def read_rows(rel):
    path = p(rel)
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                out.append((i, json.loads(line)))
            except Exception as e:
                raise SystemExit('MALFORMED {}:{} {}'.format(rel, i, e))
    return out


def write_rows(rel, rows):
    path = p(rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    before = os.path.getsize(path) if os.path.isfile(path) else 0
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        for r in rows:
            f.write(json.dumps(r, separators=(',', ':'), ensure_ascii=False) + '\n')
    return before, os.path.getsize(path)


def caps():
    with open(IDX, encoding='utf-8') as f:
        idx = json.load(f)
    out = {}
    for k, v in idx.get('tiers', {}).items():
        if isinstance(v, dict):
            out[k] = (v.get('cap_rows'), v.get('cap_bytes'), v.get('i'))
    return out


def measure(rel):
    path = p(rel)
    if not os.path.isfile(path):
        return {'bytes': 0, 'rows': 0, 'bpr': 0, 'tok': 0, 'tokrow': 0, 'sha12': '-'}
    b = os.path.getsize(path)
    n = len(read_rows(rel))
    return {'bytes': b, 'rows': n, 'bpr': b // n if n else 0,
            'tok': b // 4, 'tokrow': (b // 4) // n if n else 0, 'sha12': sha12_file(path)}


def cmd_stats(as_json=False):
    rows = []
    for name, rel in TIERS:
        m = measure(rel)
        m['tier'] = name
        m['path'] = rel
        rows.append(m)
    if as_json:
        print(json.dumps({'tiers': rows, 'TOTAL_bytes': sum(r['bytes'] for r in rows),
                          'TOTAL_tok': sum(r['tok'] for r in rows),
                          'method': 'bytes/4 per tier, rows counted from JSONL lines'}, separators=(',', ':')))
        return 0
    print('tier bytes rows bpr tok tok/row sha12')
    for r in rows:
        print('{tier} {bytes} {rows} {bpr} {tok} {tokrow} {sha12}'.format(**r))
    print('TOTAL bytes={} tok={}'.format(sum(r['bytes'] for r in rows), sum(r['tok'] for r in rows)))
    return 0


def cmd_capacity():
    cap = caps()
    bad = 0
    for name, rel in TIERS:
        m = measure(rel)
        cr, cb, _ = cap.get(name, (None, None, None))
        over = (cr is not None and m['rows'] > cr) or (cb is not None and m['bytes'] > cb)
        if over:
            bad += 1
        print('{} rows={}/{} bytes={}/{} {}'.format(name, m['rows'], cr, m['bytes'], cb,
                                                   'BREACH' if over else 'ok'))
    print('CAPACITY {}'.format('BREACH' if bad else 'OK'))
    return 1 if bad else 0


def known_shas():
    s = set()
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            path = os.path.join(dp, f)
            try:
                s.add(sha12_file(path))
            except OSError:
                pass
    for _, r in read_rows(MANIFEST):
        if r.get('sha'):
            s.add(r['sha'])
    for _, r in read_rows(SUPERSEDED):
        if r.get('sha'):
            s.add(r['sha'])
    return s


def cmd_verify():
    have = known_shas()
    skip = set(r.get('t') for _, r in read_rows(DONE)) | set(r.get('t') for _, r in read_rows(SUPERSEDED))
    total = miss = 0
    for name, rel in TIERS:
        for i, r in read_rows(rel):
            if r.get('t') in skip:
                continue
            toks = str(r.get('s', '')).split() + str(r.get('sha', '')).split()
            for tok in toks:
                if len(tok) == HEX12 and all(c in '0123456789abcdef' for c in tok):
                    total += 1
                    if tok not in have:
                        miss += 1
                        print('MISSING {}:{} {} {}'.format(rel, i, r.get('t'), tok))
    print('VERIFY tokens={} missing={} superseded_skipped={} {}'.format(
        total, miss, len(skip), 'MATCH' if not miss else 'FAIL'))
    return 0 if not miss else 1


def cmd_append(tier, row_json):
    if tier not in dict(TIERS):
        raise SystemExit('BAD_TIER ' + tier)
    if row_json == '-':
        row_json = sys.stdin.read()
    elif row_json.startswith('@'):
        with open(row_json[1:], encoding='utf-8') as f:
            row_json = f.read()
    rows = []
    for ln, line in enumerate(row_json.splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception as e:
            raise SystemExit('BAD_JSON line {} {}'.format(ln, e))
        missing = [k for k in REQ if k not in r]
        if missing:
            raise SystemExit('MISSING_KEYS line {} {}'.format(ln, ','.join(missing)))
        if len(str(r['n']).split()) > 25:
            raise SystemExit('NOTE_TOO_LONG line {} >25 words'.format(ln))
        rows.append(r)
    rel = dict(TIERS)[tier]
    before, after = write_rows(rel, rows)
    sha = sha12_file(p(rel))
    write_rows(MANIFEST, [{'f': rel, 'sha': sha, 'st': 'append',
                           't': ','.join(r['t'] for r in rows), 'c': rows[-1].get('c', 0)}])
    print('APPEND {} n={} +{}B {}->{} {}'.format(
        tier, len(rows), after - before, before, after, sha))
    return 0


def cmd_compact():
    with open(IDX, encoding='utf-8') as f:
        cyc = json.load(f).get('cycle', {}).get('n', 1)
    done = set(r.get('t') for _, r in read_rows(DONE))
    sm = read_rows('C3.3/sm.jsonl')
    cand = [(i, r) for i, r in sm
            if r.get('c', cyc) < cyc and r.get('st') not in ('rule', 'blocked') and r.get('t') not in done]
    if not cand:
        print('NO_CANDIDATES cycle={} sm_rows={} compacted={}'.format(cyc, len(sm), len(done)))
        return 0
    pre = sha12_file(p('C3.3/sm.jsonl'))
    spool_rel = '{}/cycle-{}.jsonl'.format(SPOOL, cyc)
    write_rows(spool_rel, [r for _, r in cand])
    spool_sha = sha12_file(p(spool_rel))
    groups = {}
    for _, r in cand:
        groups.setdefault((r.get('so'), r.get('st')), []).append(r)
    digests = []
    for k, (so, st) in enumerate(sorted(groups), 1):
        rs = groups[(so, st)]
        ids = ','.join(r['t'] for r in rs[:6]) + ('+' if len(rs) > 6 else '')
        digests.append({'t': 'D-{:03d}-{:02d}'.format(cyc, k), 'so': so, 'st': 'digest',
                        'n': 'digest {} rows state {}; ids {}'.format(len(rs), st, ids),
                        'l1_in': len(rs), 'l2_in': 0, 's': spool_rel, 'sha': spool_sha, 'c': cyc})
    b0, a0 = write_rows('C3.3/mm.jsonl', digests)
    write_rows(DONE, [{'t': r['t'], 'c': cyc, 'spool': spool_rel} for _, r in cand])
    write_rows(MANIFEST, [{'f': 'C3.3/sm.jsonl', 'sha': pre, 'st': 'pre-compact',
                           'spool': spool_rel, 'rows': len(cand), 'c': cyc},
                          {'f': spool_rel, 'sha': spool_sha, 'st': 'bodies',
                           'rows': len(cand), 'c': cyc}])
    print('COMPACT cycle={} in={} groups={} spool={} sha={} mm +{}B {}->{}'.format(
        cyc, len(cand), len(digests), spool_rel, spool_sha, a0 - b0, b0, a0))
    return 0


def cmd_tokens(chars_per_token=4.0):
    """Independent estimate for artifact size, separate from the tier estimator."""
    rows = []
    for name, rel in TIERS:
        path = p(rel)
        ch = sum(len(l) for l in open(path, encoding='utf-8')) if os.path.isfile(path) else 0
        rows.append((name, ch, int(ch / chars_per_token)))
    print('tier chars est_tok  (estimator chars/{}). Tier estimator in stats uses bytes/4.'.format(chars_per_token))
    for name, ch, t in rows:
        print('{} {} {}'.format(name, ch, t))
    print('TOTAL chars={} est_tok={}'.format(sum(r[1] for r in rows), sum(r[2] for r in rows)))
    return 0


def cmd_supersede(path):
    rows = read_rows(path.replace(os.sep, '/')) if not path.startswith('@') else []
    if path.startswith('@'):
        rows = read_rows(path[1:].replace(os.sep, '/'))
    n = 0
    for _, r in rows:
        n += 1
    write_rows(SUPERSEDED, [r for _, r in rows])
    print('SUPERSEDE +{} rows {} total={}'.format(
        n, SUPERSEDED, len(read_rows(SUPERSEDED))))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    c = argv[0]
    if c == 'stats':
        return cmd_stats('--json' in argv)
    if c == 'capacity':
        return cmd_capacity()
    if c == 'verify':
        return cmd_verify()
    if c == 'tokens':
        return cmd_tokens()
    if c == 'compact':
        return cmd_compact()
    if c == 'supersede' and len(argv) >= 2:
        return cmd_supersede(argv[1])
    if c == 'append' and len(argv) >= 3:
        return cmd_append(argv[1], argv[2])
    raise SystemExit('usage: memctl.py stats|capacity|verify|compact|append <tier> <json>')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
