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

# Timestamp creation

import os
import re
import threading
import time
from pathlib import Path

import gnupg
import igitt.commit
import igitt.config


class Stamper:
    def __init__(self):
        self.sem = threading.BoundedSemaphore(
            igitt.config.arg.max_parallel_signatures)
        self.timeout = igitt.config.arg.max_parallel_timeout
        self.url = igitt.config.arg.own_url
        self.keyid = igitt.config.arg.keyid
        self.gpg = gnupg.GPG(gnupghome=igitt.config.arg.gnupg_home)
        self.keyinfo = self.gpg.list_keys(keys=self.keyid)
        if len(self.keyinfo) == 0:
            raise ValueError("No keys found")
        self.fullid = self.keyinfo[0]['uids'][0]
        self.pubkey = self.gpg.export_keys(self.keyid)
        self.extra_delay = None

    def sig_time(self):
        """Current time, unless in test mode"""
        return int(os.getenv('IGITT_FAKE_TIME', time.time()))

    def get_public_key(self):
        return self.pubkey
    
    def valid_tag(self, tag):
        """Tag validity defined in doc/Protocol.md"""
        # '$' always matches '\n' as well. Don't want this here.
        if '\n' in tag:
            return False
        return re.match('^[a-z][-_a-z0-9]{,99}$', tag, re.IGNORECASE)

    def valid_commit(self, commit):
        # '$' always matches '\n' as well. Don't want this here.
        if '\n' in commit:
            return False
        return re.match('^[0-9a-f]{40}$', commit)

    def limited_sign(self, now, commit, data):
        """Sign, but allow at most <max-parallel-timeout> executions.
        Requests exceeding this limit will return None after <timeout> s,
        or wait indefinitely, if `--max-parallel-timeout` has not been
        given (i.e., is None). It logs any commit ID to stable storage
        before attempting to even create a signature. It also makes sure
        that the GnuPG signature time matches the GIT timestamps."""
        if self.sem.acquire(timeout=self.timeout):
            ret = None
            try:
                if self.extra_delay:
                    time.sleep(self.extra_delay)
                ret = self.gpg.sign(data, keyid=self.keyid, binary=False,
                                    clearsign=False, detach=True,
                                    extra_args=('--faked-system-time',
                                        str(now) + '!'))
            finally:
                self.sem.release()
            return ret
        else: # Timeout
            return None

    def log_commit(self, commit):
        with open(Path(igitt.config.arg.repository, 'hashes.work').as_posix(),
                'ab', buffering=0) as f:
            f.write(bytes(commit + '\n', 'ASCII'))
            os.fsync(f.fileno())

    def stamp_tag(self, commit, tagname):
        if self.valid_commit(commit) and self.valid_tag(tagname):
            with igitt.commit.serialize:
                now = int(self.sig_time())
                self.log_commit(commit)
            isonow = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now))
            tagobj = """object %s
type commit
tag %s
tagger %s %d +0000

%s tag timestamp
""" % (commit, tagname, self.fullid, now,
        self.url)

            sig = self.limited_sign(now, commit, tagobj)
            if sig == None:
                return None
            else:
                return tagobj + str(sig)
        else:
            return 406
    
    def stamp_branch(self, commit, parent, tree):
        if (self.valid_commit(commit) and self.valid_commit(tree)
                and (parent == None or self.valid_commit(parent))):
            with igitt.commit.serialize:
                now = int(self.sig_time())
                self.log_commit(commit)
            isonow = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now))
            if parent == None:
                commitobj1 = """tree %s
parent %s
author %s %d +0000
committer %s %d +0000
""" % (tree, commit, self.fullid, now, self.fullid, now)
            else:
                commitobj1 = """tree %s
parent %s
parent %s
author %s %d +0000
committer %s %d +0000
""" % (tree, parent, commit, self.fullid, now, self.fullid, now)

            commitobj2 = """
%s branch timestamp %s
""" % (self.url, isonow)

            sig = self.limited_sign(now, commit, commitobj1 + commitobj2)
            if sig == None:
                return None
            else:
                # Replace all inner '\n' with '\n '
                gpgsig = 'gpgsig ' + str(sig).replace('\n', '\n ')[:-1]
                assert gpgsig[-1] == '\n'
                return commitobj1 + gpgsig + commitobj2
        else:
            return 406
