#!/bin/bash -e
# Timestamping the current timestamping branch should not work
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init

echo $RANDOM > 24-a.txt
git add 24-a.txt
git commit -m "Random change 24-$RANDOM"

# Clean config
git config --unset timestamp.branch || true
git config --unset timestamp.server || true

# Ensure timestamp branch exists
$h/git-timestamp.py

# Create tag with branch and server from config
if $h/git-timestamp.py --append-branch-name=no gitta-timestamps; then
	echo "Assertion failed: Can timestamp onto timestamp branch" >&2
	exit 1
fi
