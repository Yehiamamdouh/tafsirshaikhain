#!/bin/bash
# rebuild.sh : reproducible content rebuild of site/ from the pre-review backup + all decision/spec files.
#   restore backup_apply -> xres -> apply (dec/dec2/xnew) -> gapply (gap specs) -> capply (collation specs)
#   -> fanafilter -> attach every surah.  Stops on the first error.
set -e
SC=/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad
cd $SC
echo "== restore"
for f in batch*.json; do [[ $f =~ ^batch[0-9]+\.json$ ]] && [ ! -e backup_apply/$f ] && rm -f $f; done
for f in site/s*i.json; do [ ! -e backup_apply/$f ] && rm -f $f; done
cp backup_apply/batch*.json .
cp backup_apply/site/s*.json site/
echo "== xres";      python3 full/xres.py | tail -2
echo "== apply";     python3 full/apply.py | tail -4
echo "== gapply";    python3 full/gapply.py $(ls full/gspec*.txt | grep -v -e gspec_audit -e gspec_gap2) | tail -1
if [ "${CAPPLY:-1}" = 1 ] && ls coll/cspec*.txt >/dev/null 2>&1; then echo "== capply"; python3 coll/capply.py $(ls coll/cspec*.txt | grep -v cspec_zaudit) | tail -1; python3 coll/capply.py coll/cspec_zaudit.txt | grep -v "^surah" | tail -3; fi
echo "== gapply audit"; python3 full/gapply.py full/gspec_audit.txt | grep -v "^surah" | tail -5
if ls full/nspec*.txt >/dev/null 2>&1; then echo "== napply"; python3 full/napply.py | tail -1; fi
echo "== rtfix"; python3 full/rtfix.py | tail -3
echo "== ctx"; python3 full/ctxapply.py | tail -3
echo "== a2apply"; python3 full/a2apply.py audit2 | tail -8
echo "== a3apply"; python3 full/a2apply.py audit3 | tail -8
echo "== a4apply"; python3 full/a2apply.py audit4 | tail -8
echo "== rext"; python3 full/rext.py | tail -2
# gap2 excerpts were cut from rext-widened records, so they apply after rext; ctx re-run picks up their context lines
[ -e full/gspec_gap2.txt ] && { echo "== gapply gap2"; python3 full/gapply.py full/gspec_gap2.txt | grep -v "^surah" | tail -8; echo "== ctx2"; python3 full/ctxapply.py gap2/ctx_gap2.txt | tail -2; }
[ -d tam/out ] && { echo "== tapply"; python3 tam/tapply.py | tail -12; }
[ -d spec/out ] && { echo "== sapply"; python3 spec/sapply.py | tail -40; }
ls bp/out/B*.txt >/dev/null 2>&1 && { echo "== bpapply"; python3 bp/bpapply.py | tail -22; }
[ -f qc/moves.txt ] && { echo "== qapply"; python3 qc/qapply.py; }
ls qc/nq/out/N*.txt >/dev/null 2>&1 && { echo "== nqapply"; python3 qc/nq/nqapply.py | tail -16; }
echo "== fanafilter"; python3 full/fanafilter.py | tail -1
echo "== attach"
TMP1=0; [ -e site/s1i.json ] || { echo '[]' > site/s1i.json; TMP1=1; }
BAD=0
for su in $(seq 1 114); do
  [ -e batch$su.json ] || continue
  out=$(python3 scripts/attach.py $su); echo "$out" >> full/attach.log.new
  b=$(echo "$out" | awk '/^surah/{print $4}'); [ "$b" != "0" ] && { echo "$out" | grep -v '^surah' | head -5; BAD=$((BAD+b)); }
done
[ $TMP1 = 1 ] && [ "$(cat site/s1i.json)" = "[]" ] && rm -f site/s1i.json
mv full/attach.log.new full/attach.log
echo "== attach total bad: $BAD"
python3 - <<'EOF'
import json
S='/tmp/claude-0/-home-claude/6849b79b-b42b-528f-98ae-05c780b196c6/scratchpad/site'
ns=nn=cov=0
for su in range(1,115):
    d=json.load(open(f'{S}/s{su}.json'))
    vs=set()
    for k in ('summ','nuq'):
        for a,x in d.get(k,{}).items():
            for v,L in x.items():
                vs.add(v)
                if k=='summ': ns+=len(L)
                else: nn+=len(L)
    cov+=len(vs)
print('summ',ns,'nuq',nn,'verses covered',cov,'of 6236')
EOF
