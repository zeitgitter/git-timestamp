all:
	@echo "Use make install-client|install-server|test"

install-client:
	${MAKE} -C client install

install-server:
	${MAKE} -C server install

test:
	${MAKE} -C server test

