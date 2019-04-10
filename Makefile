all:
	@echo "Use make install-client|install-server|install-both|test"

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
