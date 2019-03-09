# Installation
PREFIX		= /usr/local
SBINDIR		= ${PREFIX}/sbin
LIBDIR		= ${PREFIX}/lib
PYMODDIR	= ${LIBDIR}/python/igitt
IGITTHOME	= /var/lib/igitt
WEBDIR		= ${IGITTHOME}/web
REPODIR		= ${IGITTHOME}/repo
ETCDIR		= /etc
SYSTEMDDIR	= ${ETCDIR}/systemd/system

# Color
WARN		= \033[1;31m
INFO		= \033[1;32m
NORM		= \033[0m

# Tests
DAEMONTEMP	:= $(shell mktemp -d)
KEYID		= CA4AFAB26C58B209599C8025353DFEC512FA47C7
KEYHOME		= ${CURDIR}/igitt/tests/gnupg/
DAEMONPARAMS	= \
	--keyid ${KEYID} \
	--own-url https://hagrid.snakeoil \
	--gnupg-home ${KEYHOME} \
	--commit-at '' \
	--repository ${DAEMONTEMP} \
	--upstream-timestamp stupid-timestamps=http://localhost:8080

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
		install -o igitt -d ${WEBDIR}; \
		install -o igitt -m 644 -t ${WEBDIR} web/*; \
	else \
		echo "${WARN}* Not updating ${WEBDIR}${NORM}"; \
	fi
	if ! groups igitt > /dev/null 2>&1; then \
		adduser --system --disabled-password --disabled-login --group --home ${IGITTHOME} --gecos "Independent GIT Timestamper" igitt; \
	fi
	install -d -o igitt ${REPODIR}
# /etc/igittd.conf contains passwords, so restrict access
	if [ ! -f ${ETCDIR}/igittd.conf ]; then \
		install -o igitt -m 600 sample-igittd.conf ${ETCDIR}/igittd.conf; \
		echo "${INFO}* Customize ${ETCDIR}/igittd.conf${NORM}"; \
	else \
		echo "${WARN}* Not updating ${ETCDIR}/igittd.conf${NORM}"; \
	fi
	if [ ! -f ${SYSTEMDDIR}/igitt.socket ]; then \
		install -m 644 -t ${SYSTEMDDIR} systemd/*; \
	else \
		echo "${WARN}* Not updating ${SYSTEMDDIR}/igitt.*${NORM}"; \
	fi
	systemctl daemon-reload
	systemctl enable igitt.service igitt.socket --now
	if [ ! -d ${IGITTHOME}/.gnupg ]; then \
		echo "${INFO}* Create an OpenPGP key, see ../doc/Keys.md"; \
	fi


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

run-test-daemon:
	./igittd.py ${DAEMONPARAMS}
run-test-daemon-fake-time:
	IGITT_FAKE_TIME=1551155115 ./igittd.py ${DAEMONPARAMS}
