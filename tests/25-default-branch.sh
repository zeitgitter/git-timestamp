#!/bin/bash -e
# Handling default branch names
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init --initial-branch main
git config init.defaultBranch main

echo $RANDOM > 25-a.txt
git add 25-a.txt
git commit -m "Random change 25-$RANDOM"

# Clean config
git config --unset timestamp.branch || true
git config --unset timestamp.server || true

# Prepare config
git config init.defaultBranch system-default-branch
git config timestamp.defaultBranch default-branch-a,default-branch-b

# Should create `gitta-timestamps-main`
git checkout main
$h/git-timestamp.py

if ! git branch | grep -q 'gitta-timestamps-main'; then
	echo "Assertion failed: Timestamping 'main' if not default branch should create branch-named timestamp branch" >&2
	exit 1
fi

# Should not create `gitta-timestamps-system-default-branch`
git checkout -b system-default-branch
$h/git-timestamp.py
if git branch | grep -q 'gitta-timestamps-system-default-branch'; then
    git checkout main
	echo "Assertion failed: Timestamping 'system-default-branch' if default branch" >&2
	exit 1
fi
git checkout main
