#!/usr/bin/python3
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
import logging
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
  subprocess.run(['git', 'add', log.as_posix()],
                 cwd=repo).check_returncode()
  subprocess.run(['git', 'commit', '-m', msg, '--allow-empty',
                  '--gpg-sign=' + igitt.config.arg.keyid],
                 cwd=repo).check_returncode()
  # Mark as processed; use only while locked!
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
  tmp.rename(log)


def push_upstream(repo, to, branches):
  logging.info("Pushing to %s" % (['git', 'push', to] + branches))
  ret = subprocess.run(['git', 'push', to] + branches,
                       cwd=repo)
  if ret.returncode != 0:
    logging.error("'git push %s %s' failed" % (to, branches))


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
  3. (Optionally) cross-timestamp
  4. (Optionally) push"""
  repo = igitt.config.arg.repository
  tmp = Path(repo, 'hashes.work')
  log = Path(repo, 'hashes.log')
  with serialize:
    commit_dangling(repo, log)
    try:
      tmp.stat()
      rotate_log_file(tmp, log)
      commit_to_git(repo, log)
      with tmp.open(mode='ab'):
          pass # Recreate hashes.work
    except FileNotFoundError:
      logging.info("Nothing to rotate")
  repositories = igitt.config.arg.push_repository
  branches = igitt.config.arg.push_branch
  for r in igitt.config.arg.upstream_timestamp:
    logging.info("Cross-timestamping %s" % r);
    (branch, server) = r.split('=', 1)
    cross_timestamp(repo, branch, server)
  for r in repositories:
    logging.info("Pushing upstream to %s" % r);
    push_upstream(repo, r, branches)
  logging.info("do_commit done")


def wait_until():
  """Run at given interval and offset"""
  interval = igitt.config.arg.commit_interval.total_seconds()
  offset = igitt.config.arg.commit_offset.total_seconds()
  while True:
    now = time.time()
    until = now - (now % interval) + offset
    if until <= now:
        until += interval
    time.sleep(until - now)
    threading.Thread(target=do_commit, daemon=False).start()


def run():
  """Start background thread to wait for given time"""
  threading.Thread(target=wait_until, daemon=True).start()
