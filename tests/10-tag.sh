#!/bin/bash -e
# Test basic key import and tag timestamping
h="$PWD"
d=$1
shift
cd "$d"
export GNUPGHOME="$d/gnupg"
mkdir -m 700 "$GNUPGHOME"
git init --initial-branch main
git config init.defaultBranch main

echo $RANDOM > 10-a.txt
git add 10-a.txt
git commit -m "Random change 10-$RANDOM"
tagid=v10-$RANDOM
$h/git-timestamp.py --tag $tagid --server https://gitta.zeitgitter.net

# Check key import
if ! gpg --list-keys | grep -q 9C67D18C5119896C35FE3E0D8A0B0941E7C49D65; then
	echo "Key 9C67D18C5119896C35FE3E0D8A0B0941E7C49D65 not imported" >&2
	exit 1
fi

# Check config
grep -A2 gitta-zeitgitter-net $HOME/.gitconfig > $d/10-tag-config-real.txt
cat > $d/10-tag-config-verify.txt << EOF
[timestamper "gitta-zeitgitter-net"]
	keyid = 8A0B0941E7C49D65
	name = Gitta Timestamping Service <gitta@zeitgitter.net>
EOF
diff $d/10-tag-config*.txt

# Check tag existence
if [ 1 -ne `git tag | wc -l` ]; then
	echo "Found `git tag | wc -l` tags instead of 1" >&2
	exit 1
fi
if ! git tag | grep -q "^$tagid$"; then
	echo "Tag $tagid does not match `git tag`" >&2
	exit 1
fi

# Check tag signature
git tag -v $tagid
