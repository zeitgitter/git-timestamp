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
git config timestamp.server https://gitta.zeitgitter.ch

# Create tag with server from config
$h/git-timestamp.py --tag $tagid

# Check tag existence
if ! git tag | grep -q $tagid; then
	echo "Tag does not exist: $tagid" >&2
	exit 1
fi

# Yet another commit
echo $RANDOM >> a.txt
git commit -m "Random commit $RANDOM" -a

# Create tag with even more options
yatag=r$RANDOM
$h/git-timestamp.py --tag $yatag --server https://diversity.zeitgitter.net

# Check tag existence
if ! git tag | grep -q $yatag; then
	echo "Third tag does not exist: $yatag" >&2
	exit 1
fi

# Cryptographically verify all of them
git tag -v $tagid $yatag
