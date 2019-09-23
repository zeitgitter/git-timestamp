#!/bin/bash -e
# Test timestamping to a different branch
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init

echo $RANDOM > a.txt
git add a.txt
git commit -m "Random change $RANDOM"
branchname=gitta-special-timestamps

# Change config
git config timestamp.branch gitta-timestamps
git config timestamp.server https://gitta.zeitgitter.net

# Create tag with branch and server from config
$h/git-timestamp.py --branch $branchname

# Check branch existence
if ! git branch | grep -q $branchname; then
	echo "Branch $branchname does not exist" >&2
	exit 1
fi

# Branch should be identical
if ! git diff --quiet $branchname; then
	echo "Timestamp branch contents differ from master" >&2
	exit 1
fi

# Cryptographically verify
git verify-commit $branchname
