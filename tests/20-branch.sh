#!/bin/bash -e
# Test timestamping to branch
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init

echo $RANDOM > 20-a.txt
git add 20-a.txt
git commit -m "Random change 20-$RANDOM"

# Change config
git config timestamp.branch gitta-timestamps

# Create branch with branch and server from config
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
echo $RANDOM >> 20-a.txt
git commit -m "Random commit 20-$RANDOM" -a

# Create a second branch node
$h/git-timestamp.py --server https://diversity.zeitgitter.net

# Branch should be identical
if ! git diff --quiet gitta-timestamps; then
	echo "Timestamp branch contents differ from master" >&2
	exit 1
fi

# Cryptographically verify all of them
git verify-commit gitta-timestamps gitta-timestamps^

# Clean up
git config --unset timestamp.branch
