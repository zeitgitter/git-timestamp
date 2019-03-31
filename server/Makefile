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
ACT		= \033[7;34m
INFO		= \033[7;32m
NORM		= \033[0m

# Tests
DAEMONTEMP	:= $(shell mktemp -d)
KEYID		= 353DFEC512FA47C7
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
	if ! groups igitt > /dev/null 2>&1; then \
		adduser --system --disabled-password --disabled-login --group --home ${IGITTHOME} --gecos "Independent GIT Timestamper" igitt; \
	fi
	mkdir -p ${PYMODDIR}
	install -t ${SBINDIR} igittd.py
	install -t ${PYMODDIR} igitt/*.py
	py3compile ${PYMODDIR}/*.py
	if [ ! -d ${WEBDIR} ]; then \
		install -o igitt -d ${WEBDIR}; \
		install -o igitt -m 644 -t ${WEBDIR} web/*; \
	else \
		echo "${INFO}* Not updating ${WEBDIR}${NORM}"; \
	fi
	if grep -q _IGITT_ ${WEBDIR}/*; then echo "${ACT}* Please adapt ${WEBDIR} to your needs${NORM}"; fi
	install -d -o igitt ${REPODIR}
# /etc/igittd.conf contains passwords, so restrict access
	if [ ! -f ${ETCDIR}/igittd.conf ]; then \
		install -o igitt -m 600 sample-igittd.conf ${ETCDIR}/igittd.conf; \
		echo "${ACT}* Customize ${ETCDIR}/igittd.conf${NORM}"; \
	else \
		echo "${INFO}* Not updating ${ETCDIR}/igittd.conf${NORM}"; \
	fi
	if [ ! -f ${SYSTEMDDIR}/igitt.socket ]; then \
		install -m 644 -t ${SYSTEMDDIR} systemd/*; \
		systemctl daemon-reload; \
	else \
		echo "${INFO}* Not updating ${SYSTEMDDIR}/igitt.*${NORM}"; \
	fi
	if [ ! -d ${IGITTHOME}/.gnupg ]; then \
		systemctl enable igitt.service igitt.socket; \
		echo "${ACT}* Please create an OpenPGP key, see ../doc/Cryptography.md${NORM}"; \
	else \
		systemctl restart igitt.service; \
	fi
	if [ ! -d ${REPODIR}/.git ]; then git init ${REPODIR}; fi
	if [ ! -d ${REPODIR}/pubkey.asc ]; then \
		if wget --no-verbose -O ${REPODIR}/pubkey.asc 'http://127.0.0.1:15177/?request=get-public-key-v1'; then \
			git add ${REPODIR}/pubkey.asc; \
		else \
			echo "${ACT}* Cannot obtain public key${NORM}"; \
			rm ${REPODIR}/pubkey.asc; \
		fi; \
	fi



test tests:	unit-tests system-tests

unit-tests:
	nosetests3

system-tests: prepare-tmp-git kill-daemon
## Start daemon
	IGITT_FAKE_TIME=1551155115 ./igittd.py ${DAEMONPARAMS} &
## Wait for daemon to be ready
	sleep 0.5
## Run tests with daemon
	@d=`mktemp -d`; for i in tests/*; do echo; echo ===== $$i $$d; $$i $$d || exit 1; done; rm -r $$d
## Cleanup
	${RM} -r ${DAEMONTEMP}
	killall igittd.py

kill-daemon:
	-killall igittd.py 2>/dev/null; exit 0

prepare-tmp-git:
	git init ${DAEMONTEMP}
	chmod 700 ${KEYHOME}
# Avoid "gpg: WARNING: unsafe permissions on homedir"
	gpg --export -a ${KEYID} > ${DAEMONTEMP}/pubkey.asc
	cd ${DAEMONTEMP} && git add pubkey.asc
	cd ${DAEMONTEMP} && git commit -S${KEYID} -m "Start timestamping"

run-test-daemon: prepare-tmp-git kill-daemon
	./igittd.py ${DAEMONPARAMS}
run-test-daemon-fake-time: prepare-tmp-git kill-daemon
	IGITT_FAKE_TIME=1551155115 ./igittd.py ${DAEMONPARAMS}
