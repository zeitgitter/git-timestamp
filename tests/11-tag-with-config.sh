#!/bin/bash -e
# Test tag config parameters
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init --initial-branch main
git config init.defaultBranch main

echo $RANDOM > 11-a.txt
git add 11-a.txt
git commit -m "Random change 11-$RANDOM"
tagid=v11-$RANDOM

# Change config
git config timestamp.server https://gitta.zeitgitter.net

# Create tag with server from config
$h/git-timestamp.py --tag $tagid

# Check tag existence
if ! git tag | grep -q $tagid; then
	echo "Tag does not exist: $tagid" >&2
	exit 1
fi

# Yet another commit
echo $RANDOM >> 11-a.txt
git commit -m "Random commit $RANDOM" -a

# Create tag with even more options
yatag=r11-$RANDOM
$h/git-timestamp.py --tag $yatag --server https://diversity.zeitgitter.net

# Check tag existence
if ! git tag | grep -q $yatag; then
	echo "Third tag does not exist: $yatag" >&2
	exit 1
fi

# Cryptographically verify all of them
git tag -v $tagid $yatag
