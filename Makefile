PREFIX	= /usr/local
BINDIR	= ${PREFIX}/bin
TESTS   = tests/*

# Color
TITLE	= \033[7;34m
NORM	= \033[0m


all:
	echo "Use make install, apt, or test"

install:
	install --backup --compare git_timestamp/timestamp.py ${BINDIR}/git-timestamp

apt dependencies:
	apt install python3-gnupg python3-pygit2 python3-requests

test tests:	system-tests

system-tests:
	@d=`mktemp -d`; for i in ${TESTS}; do echo; echo "${TITLE}===== $$i $$d${NORM}"; $$i $$d || exit 1; done; echo "${TITLE}===== Cleanup${NORM}"; ${RM} -r $$d

python-package:
	${RM} -f dist/*
	./setup.py sdist bdist_wheel

pypi:	python-package
	twine upload dist/*
