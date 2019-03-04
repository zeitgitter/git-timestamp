# Installation
PREFIX		= /usr/local
SBINDIR		= ${PREFIX}/sbin
LIBDIR		= ${PREFIX}/lib
PYMODDIR	= ${LIBDIR}/python/igitt
IGITTHOME	= /var/lib/igitt
WEBDIR		= ${PREFIX}/igitt/web
ETCDIR		= /etc
SYSTEMDDIR	= ${ETCDIR}/systemd/system

# Tests
DAEMONTEMP	:= $(shell mktemp -d)
KEYID		= CA4AFAB26C58B209599C8025353DFEC512FA47C7
KEYHOME		= ${CURDIR}/igitt/tests/gnupg/
DAEMONPARAMS	= \
	--keyid ${KEYID} \
	--own-url https://hagrid.snakeoil \
	--gnupg-home ${KEYHOME} \
	--commit-at '' \
	--repository ${DAEMONTEMP}

# For `gpg` and `git commit -S`
export GNUPGHOME= ${KEYHOME}
# For tests
export DAEMONREPO=${DAEMONTEMP}

all:
	@echo 'Nothing needs to be done for "all"; use "install" or "test" instead'

install:
	mkdir -p ${PYMODDIR}
	install -t ${SBINDIR} igittd.py
	install -t ${PYMODDIR} igitt/*.py
	py3compile ${PYMODDIR}/*.py
	if [ ! -d ${WEBDIR} ]; then \
		mkdir -p ${WEBDIR}; \
		install -m 644 -t ${WEBDIR} web/*; \
	fi
	if ! groups igitt > /dev/null 2>&1; then \
		adduser --system --disabled-password --disabled-login --group --home ${IGITTHOME} --gecos "Independent GIT Timestamper" igitt; \
	fi
# /etc/igittd.conf contains passwords, so restrict access
	if [ ! -f ${ETCDIR}/igittd.conf ]; then \
		install -o igitt -m 600 sample-igittd.conf ${ETCDIR}/igittd.conf; \
	fi
	install -m 644 -t ${SYSTEMDDIR} systemd/*
	systemctl daemon-reload
	systemctl enable igitt.service igitt.socket --now


test tests:	unit-tests system-tests

unit-tests:
	nosetests3

system-tests:
## Start daemon
	-killall igittd.py 2>/dev/null; exit 0
	IGITT_FAKE_TIME=1551155115 ./igittd.py ${DAEMONPARAMS} &
## Init repo
	git init ${DAEMONTEMP}
# Avoid "gpg: WARNING: unsafe permissions on homedir"
	chmod 700 ${KEYHOME}
	gpg --export -a ${KEYID} > ${DAEMONTEMP}/pubkey.asc
	cd ${DAEMONTEMP} && git add pubkey.asc
	cd ${DAEMONTEMP} && git commit -S${KEYID} -m "Start timestamping"
## Wait for daemon to be ready
	sleep 0.5
## Run tests with daemon
	@d=`mktemp -d`; for i in tests/*; do echo; echo ===== $$i $$d; $$i $$d || exit 1; done; rm -r $$d
## Cleanup
	${RM} -r ${DAEMONTEMP}
	killall igittd.py
