PREFIX	= /usr/local
BINDIR	= ${PREFIX}/bin

all:
	echo "Use make install, apt, or test"

install:
	install --backup --compare igitt_client/timestamp.py ${BINDIR}/git-timestamp

apt dependencies:
	apt install python3-gnupg python3-pygit2 python3-requests

test tests:	system-tests

system-tests:
	@d=`mktemp -d`; for i in tests/*; do echo; echo ===== $$i $$d; $$i $$d || exit 1; done; echo ===== Cleanup; ${RM} -r $$d

pypi:
	${RM} -f dist/*
	./setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
