#!/bin/bash -e
# Test branch with config
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -p -m 700 "$GNUPGHOME"
git init

echo $RANDOM > 21-a.txt
git add 21-a.txt
git commit -m "Random change 21-$RANDOM"
tagid=v21-$RANDOM

# Change config
git config timestamp.server https://gitta.zeitgitter.net
git config timestamp.branch gitta-timestamps

# Create tag with server from config
$h/git-timestamp.py --tag $tagid

# Check tag existence
if ! git tag | grep -q $tagid; then
	echo "Tag does not exist: $tagid" >&2
	exit 1
fi
