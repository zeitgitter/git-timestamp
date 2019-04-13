all:
	@echo "Use make install-client|install-server|install-both|test|version-check"

install:
	@echo "Please select from install-client, install-server, install-both"
	@echo "For cross-timestamping servers, both should be installed"

install-client:
	${MAKE} -C client install
install-server:
	${MAKE} -C server install

install-both: install-client install-server

test:	test-client test-server

test-server:
	${MAKE} -C server test
test-client:
	${MAKE} -C client test

version-check:
	@grep --with-filename ^VERSION client/git-timestamp.py server/igitt/version.py
	@echo -n "                    "
	@grep --with-filename '^# ' CHANGELOG.md | tail +2 | head -1

version-edit:
	vi +/^VERSION client/git-timestamp.py
	vi +/^VERSION server/igitt/version.py
	vi +1 '+/^# [0-9]' CHANGELOG.md
