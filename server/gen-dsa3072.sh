#!/bin/sh
if [ "x$1" = "x" -o "x$2" = "x" ]; then
 	echo "Usage: $0 <fullname> <email>" 2>&1
	echo 'Example: gpg-generate-dsa3072-key.sh "Hagrid Timestomping" timestomping@hagrid.snakeoil' 2>&1
	exit 1
fi

gpg --batch --generate-key << EOF
%no-protection
Key-Type: DSA
Key-Length: 3072
Name-Real: $1
Name-Email: $2
%commit
EOF
