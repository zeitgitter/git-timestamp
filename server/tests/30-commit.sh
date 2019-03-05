#!/bin/sh
cd "$DAEMONREPO"
# Wait for the next full minute (+1 s)
delay=$((61 - $(date +%S)))
echo "Waiting $delay seconds for the rotation to have happened"
sleep $delay

if [ ! -r pubkey.asc ]; then
  echo "Missing pubkey.asc" 2>&1
  exit 1
fi
if [ -r hashes.log ]; then
  echo "Hashes.log should not be here" 2>&1
  exit 1
fi
if [ ! -r hashes.work ]; then
  echo "hashes.work should again be here" 2>&1
  exit 1
fi
if [ `wc -l < hashes.work` -ne 1 ]; then
  echo "There should only be a single ('cross'-)timestamp in hashes.work" 2>&1
  exit 1
fi
if [ `git log | grep '^commit ' | wc -l` -ne 2 ]; then
  echo "Expected exactly two commits:" 2>&1
  git log
  exit 1
fi
