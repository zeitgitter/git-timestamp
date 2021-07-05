#!/bin/bash -e
# Timestamping against multiple servers, including delay
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init --initial-branch main
git config init.defaultBranch main

echo $RANDOM > 26-a.txt
git add 26-a.txt
git commit -m "Random change 25-$RANDOM"

# Clean config
git config --unset timestamp.branch || true
git config --unset timestamp.server || true
git config --unset timestamp.defaultBranch || true

if ! $h/git-timestamp.py --server=gitta,diversity --interval=1.5s; then
	echo "Assertion failed: Timestamping against two servers" >&2
	exit 1
fi
