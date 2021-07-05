#!/bin/bash -e
# Test timestamping from other branches
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init --initial-branch main
git config init.defaultBranch main

assert_branch_present() {
	for i in "$@"; do
		if ! git branch | grep -q "^. $i\$"; then
			echo "Assertion failed: Branch $i does not exist" >&2
			exit 1
		fi
	done
}
assert_branch_absent() {
	for i in "$@"; do
		if git branch | grep -q "^. $i\$"; then
			echo "Assertion failed: Branch $i does exist" >&2
			exit 1
		fi
	done
}

# Ensure there is a non-empty default branch
echo $RANDOM > 23-a.txt
git add 23-a.txt
git commit -m "Random change 23-$RANDOM"

# Ensure there is a non-empty gitta-timestamps branch
$h/git-timestamp.py

assert_branch_present gitta-timestamps main

# Ensure there is a non-empty secondary branch
git checkout -b secondary
echo $RANDOM > 23-c.txt
git add 23-c.txt
git commit -m "Random change 23-$RANDOM"

assert_branch_present secondary

# This should create gitta-timestamps-secondary
$h/git-timestamp.py
assert_branch_present gitta-timestamps-secondary

# Also timestamp to default timestamping branch
before=`git log gitta-timestamps | wc -l`
$h/git-timestamp.py --append-branch-name=no 
after=`git log gitta-timestamps | wc -l`
if [ `expr $after - $before` -eq 0 ]; then
	echo "gitta-timestamps should have grown (log length before=$before, after=$after)" >&2
	exit 1
fi

# Timestamp for explicit main
git checkout main
echo $RANDOM > 23-d.txt
git add 23-d.txt
git commit -m "Random commit 23-$RANDOM"

git checkout -b ternary
echo $RANDOM > 23-e.txt
git add 23-e.txt
git commit -m "Random commit 23-$RANDOM"
$h/git-timestamp.py main
assert_branch_absent gitta-timestamps-main gitta-timestamps-ternary


# And now for some failures:
# Branch too long after appending only
git checkout secondary
$h/git-timestamp.py    --append-branch-name=no  --branch gitta-timestamps-123456789-12345789-12345789-12345789-12345789-12345789-12345789-12345789-123456
if $h/git-timestamp.py --append-branch-name=yes --branch gitta-timestamps-123456789-12345789-12345789-12345789-12345789-12345789-12345789-12345789-123456; then
	echo "Too long branch name should not have succeeded" >&2
	exit 1
fi

# Cannot timestamp generic commit-ish
$h/git-timestamp.py    --append-branch-name=no  HEAD^
if $h/git-timestamp.py --append-branch-name=yes HEAD^; then
	echo "HEAD^ should not have succeeded" >&2
	exit 1
fi
