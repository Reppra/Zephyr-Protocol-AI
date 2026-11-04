import hashlib, os, sys

def sha12(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:12]

def main(argv):
    if len(argv) >= 3 and argv[0] == '--verify':
        a, b = argv[2], argv[1]
        got = sha12(b) if os.path.isfile(b) else sha12(argv[0])
        print('MATCH' if got == a else 'MISMATCH ' + got)
        return 0 if got == a else 1
    root = argv[0] if argv else 'C3.3'
    n = tot = 0
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            b = open(p, 'rb').read()
            n += 1
            tot += len(b)
            print('{} {} {}'.format(os.path.relpath(p, root).replace(os.sep, '/'), len(b), hashlib.sha256(b).hexdigest()[:12]))
    print('TOTAL {} rows_files {} bytes'.format(n, tot))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
