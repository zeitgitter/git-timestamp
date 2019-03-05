all:
	@echo "Use make install-client|install-server|install-both|test"

install-client:
	${MAKE} -C client install

install-server:
	${MAKE} -C server install

install-both: install-client install-server

test:
	${MAKE} -C server test

