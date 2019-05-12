#!/bin/bash -e
# Test tag config parameters
h="$PWD"
d=$1
shift
cd "$d"

# Init GNUPG
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"

# Init GIT
if [ ! -d .git ]; then
	git init
fi
echo $RANDOM > a.txt
git add a.txt
git commit -m "Random change $RANDOM"
tagid=v$RANDOM

# Change config
git config timestamp.branch gitta-timestamps

# Create tag with branch and server from config
$h/git-timestamp.py

# Check branch existence
if ! git branch | grep -q gitta-timestamps; then
	echo "Branch gitta-timestamps does not exist" >&2
	exit 1
fi

# Branch should be identical
if ! git diff --quiet gitta-timestamps; then
	echo "Timestamp branch contents differ from master" >&2
	exit 1
fi

# Yet another commit
echo $RANDOM >> a.txt
git commit -m "Random commit $RANDOM" -a

# Create a second branch node
yatag=r$RANDOM
$h/git-timestamp.py --server https://diversity.zeitgitter.net

# Branch should be identical
if ! git diff --quiet gitta-timestamps; then
	echo "Timestamp branch contents differ from master" >&2
	exit 1
fi

# Cryptographically verify all of them
git verify-commit gitta-timestamps gitta-timestamps^
