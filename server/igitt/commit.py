#!/usr/bin/python3 -tt
#
# igittd — Independent GIT Timestamping, HTTPS server
#
# Copyright (C) 2019 Marcel Waldvogel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# Committing to git and obtaining upstream timestamps
#
# The state machine used is described in ../../doc/StateMachine.md

import datetime
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

import igitt.config

# To serialize all commit-related operations
# - writing commit entries in order (that includes obtaining the timestamp)
# - rotating files
# - performing other operations in the repository
serialize = threading.Lock()


def commit_to_git(repo, log, msg="Newly timestamped commits"):
  subprocess.run(['git', 'add', log],
                 cwd=repo).check_returncode()
  subprocess.run(['git', 'commit', '-m', msg, '--allow-empty',
                  '--gpg-sign=' + igitt.config.arg.keyid],
                 cwd=repo).check_returncode()
  # Mark as processed
  os.remove(log)


def commit_dangling(repo, log):
  """If there is still a hashes.log hanging around, commit it now"""
  try:
    stat = os.stat(log)
    d = datetime.datetime.utcfromtimestamp(stat.st_mtime)
    dstr = d.strftime('%Y-%m-%d %H:%M:%S')
    commit_to_git(repo, log,
                  "Found uncommitted data from " + dstr)
  except FileNotFoundError:
    pass


def rotate_log_file(tmp, log):
  os.rename(tmp, log)


def push_upstream(repo, to, branches):
  ret = subprocess.run(['git', 'push', to] + branches,
                       cwd=repo)
  if ret.returncode != 0:
    sys.stderr.write("git push %s %s failed" % (to, branches))


def cross_timestamp(repo, branch, server):
  ret = subprocess.run(['git', 'timestamp',
                        '--branch', branch, '--server', server],
                       cwd=repo)
  if ret.returncode != 0:
    sys.stderr.write("git timestamp --branch %s --server %s failed"
                     % (branch, server))


def do_commit():
  """To be called in a non-daemon thread to reduce possibilities of
  early termination.

  0. Check if there is anything uncommitted
  1. Rotate log file
  2. Commit to git
  3. (Optionally) push
  4. (Optionally) cross-timestamp"""
  repo = igitt.config.arg.repository
  tmp = Path(repo, 'hashes.work')
  log = Path(repo, 'hashes.log')
  with serialize:
    commit_dangling(repo, log)
    try:
      os.stat(tmp)
      rotate_log_file(tmp, log)
      commit_to_git(repo, log)
    except FileNotFoundError:
      print("Nothing to rotate")
  repositories = igitt.config.arg.push_repository
  branches = igitt.config.arg.push_branch
  for r in repositories:
    push_upstream(repo, r, branches)
  for r in igitt.config.arg.upstream_timestamp:
    (branch, server) = r.split('=', 1)
    cross_timestamp(repo, branch, server)


def wait_until():
  """Every full minute, check whether the time matches"""
  pattern = igitt.config.arg.commit_at
  now = time.time()
  while True:
    until = now - (now % 60) + 60
    time.sleep(until - now)

    # Time for next cycle
    now = time.time()
    dnow = datetime.datetime.utcfromtimestamp(now)
    strnow = dnow.strftime('HH:MM')
    if re.search(pattern, strnow):
      threading.Thread(target=do_commit, daemon=False).start()


def run():
  """Start background thread to wait for given time"""
  threading.Thread(target=wait_until, daemon=True).start()
