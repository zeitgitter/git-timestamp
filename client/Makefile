PREFIX	= /usr/local
BINDIR	= ${PREFIX}/bin

all:
	echo "Use make install or test"

install:
	install --backup --compare git-timestamp.py ${BINDIR}/git-timestamp

test tests:	system-tests

system-tests:
	@d=`mktemp -d`; for i in tests/*; do echo; echo ===== $$i $$d; $$i $$d || exit 1; done; echo ===== Cleanup; ${RM} -r $$d
