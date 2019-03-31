#!/usr/bin/python3
import sys
import os
import subprocess

os.chdir(sys.argv[1])

for line in sys.stdin:
    if line.startswith(':user ID packet: "'):
        line = line.strip()
        if line.endswith('>"'):
            (name, mail) = line[18:-2].split(" <")
            subprocess.call(['git', 'config', 'user.name', name])
            subprocess.call(['git', 'config', 'user.email', mail])
            sys.exit(0)

sys.exit("Key has no User ID!?")
