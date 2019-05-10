#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# (keep hashbang line for `make install`)

#
# git timestamp — Independent GIT Timestamping client
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

# This has not been modularized for ease of installation

import argparse
import os
import re
import sys
import tempfile
import time
import traceback

import gnupg
import pygit2 as git
import requests

VERSION = '0.9.2'


class GitArgumentParser(argparse.ArgumentParser):
  def __init__(self, *args, **kwargs):
    super(GitArgumentParser, self).__init__(*args, **kwargs)

  def add_argument(self, *args, **kwargs):
    """Insert git config options between command line and default"""
    global repo
    if 'gitopt' in kwargs:
      if 'help' in kwargs:
        kwargs['help'] += '. '
      else:
        kwargs['help'] = ''
      gitopt = kwargs['gitopt']
      try:
        val = repo.config[gitopt]
        kwargs['help'] += "Defaults to '%s' from git config '%s'" % (val, gitopt)
        if 'default' in kwargs:
          kwargs['help'] += "; fallback default: '%s'" % kwargs['default']
        kwargs['default'] = val
        if 'required' in kwargs:
          del kwargs['required']
      except KeyError:
        kwargs['help'] += "Can be set by git config '%s'" % gitopt
        if 'default' in kwargs:
          kwargs['help'] += "; fallback default: '%s'" % kwargs['default']
      del kwargs['gitopt']
    return super(GitArgumentParser, self).add_argument(*args, **kwargs)

  add = add_argument


def asciibytes(data):
  """For Python 2/3 compatibility:
  If it is 'bytes' already, do nothing, otherwise convert to ASCII Bytes"""
  if isinstance(data, bytes):
    return data
  else:
    return data.encode('ASCII')


def timestamp_branch_name(fields):
  """Return the first field not being 'igitt'"""
  for i in fields:
    if i != '' and i != 'igitt':
      return i + '-timestamps'
  return 'igitt-timestamps'


def get_args():
  """Parse command line and git config parameters"""
  parser = GitArgumentParser(
    add_help=False,
    description="Interface to IGITT, the Independent GIT Timestampers.",
    epilog="""--tag takes precedence over --branch.
            When in doubt, use --tag for single/rare timestamping,
            and --branch for reqular timestamping.""")
  parser.add('-h', '--help',
             action='help',
             help="""Show this help message and exit. When called as
             'git timestamp' (space, not dash), use '-h', as '--help' is 
             interpreted by 'git'.""")
  parser.add('--tag',
             help="Create a new timestamped tag named TAG")
  parser.add('--branch',
             gitopt='timestamp.branch',
             help=("""Create a timestamped commit in branch BRANCH,
                   with identical contents as the specified commit.
                   Default name derived from servername plus '-timestamps'"""))
  parser.add('--server',
             required=True,
             gitopt='timestamp.server',
             help="IGITT server to obtain timestamp from")
  parser.add('--gnupg-home',
             gitopt='timestamp.gnupg-home',
             help="Where to store timestamper public keys")
  parser.add('commit',
             nargs='?',
             default='HEAD',
             metavar='COMMIT',
             gitopt='timestamp.commit-branch',
             help="Which commit to timestamp")
  arg = parser.parse_args()
  if arg.tag is None and arg.branch is None:
    # Automatically derive branch name
    # Split on '.' or '/'
    fields = arg.server.replace('/', '.').split('.')
    arg.branch = timestamp_branch_name(fields[1:])
  return arg


def ensure_gnupg_ready_for_scan_keys():
  """`scan_keys()` on older GnuPG installs returns an empty list when
  `~/.gnupg/pubring.kbx` has not yet been created. `list_keys()` or most
  other commands will create it. Trying to have no match (for speed).
  Probing for the existance of `pubring.kbx` would be faster, but would
  require guessing the path of GnuPG-Home."""
  gpg.list_keys(keys='arbitrary.query@creates.keybox')


def validate_key_and_import(text):
  """Is this a single key? Then import it"""
  ensure_gnupg_ready_for_scan_keys()
  f = tempfile.NamedTemporaryFile(mode='w', delete=False)
  f.write(text)
  f.close()
  info = gpg.scan_keys(f.name)
  os.unlink(f.name)
  if len(info) != 1 or info[0]['type'] != 'pub' or len(info[0]['uids']) == 0:
    sys.exit("Invalid key returned")
  res = gpg.import_keys(text)
  if res.count == 1:
    print("Imported new key %s: %s" %
          (info[0]['keyid'], info[0]['uids'][0]))
  return (info[0]['keyid'], info[0]['uids'][0])


def get_keyid(server):
  """Return keyid/fullname from git config, if known.
  Otherwise, request it from server and remember TOFU-style"""
  key = server
  if key.startswith('http://'):
    key = key[7:]
  elif key.startswith('https://'):
    key = key[8:]
  while key.endswith('/'):
    key = key[0:-1]
  # Replace everything outside 0-9a-z with '-':
  key = ''.join(map(lambda x:
                    x if (x >= '0' and x <= '9') or (x >= 'a' and x <= 'z') else '-', key))
  try:
    keyid = repo.config['timestamper.%s.keyid' % key]
    keys = gpg.list_keys(keys=keyid)
    if len(keys) == 0:
      sys.stderr.write("WARNING: Key %s missing in keyring;"
                       " refetching timestamper key\n" % keyid)
      raise KeyError("GPG Key not found") # Evil hack
    return (keyid, repo.config['timestamper.%s.name' % key])
  except KeyError:
    # Obtain key in TOFU fashion and remember keyid
    r = requests.get(server, params={'request': 'get-public-key-v1'},
                     timeout=30)
    if r.status_code != 200:
      sys.exit("Server responded with %d %s" % (r.status_code, r.reason))
    (keyid, name) = validate_key_and_import(r.text)
    repo.config['timestamper.%s.keyid' % key] = keyid
    repo.config['timestamper.%s.name' % key] = name
    return (keyid, name)


def sig_time():
  """Current time, unless in test mode"""
  return int(os.getenv('IGITT_FAKE_TIME', time.time()))


def validate_timestamp(stamp):
  """Is this timestamp within ± of now?"""
  now = sig_time()
  # Allow a ±30 s window
  return stamp > now - 30 and stamp < now + 30


def time_str(seconds):
  """Format Unix timestamp in ISO format"""
  return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds))


def validate_timestamp_zone_eol(header, text, offset):
  """Does this line end with a current timestamp and GMT?
  Returns start of next line."""
  stamp = text[offset:offset + 10]
  try:
    istamp = int(stamp)
    sigtime = sig_time()
    if not validate_timestamp(istamp):
      sys.exit("Returned %s timestamp (%d, %s) too far off now (%d, %s)" %
               (header, istamp, time_str(istamp), sigtime, time_str(sigtime)))
  except ValueError:
    sys.exit("Returned %s timestamp '%s' is not a number" % (header, stamp))
  tz = text[offset + 10:offset + 17]
  if tz != ' +0000\n':
    sys.exit("Returned %s timezone is not GMT or not at end of line,\n"
             "but '%s' instead of '%s'"
             % (header, repr(tz), repr(' +0000\n')))
  return offset + 17


def verify_signature_and_timestamp(keyid, signed, signature, args):
  """Is the signature valid
  and the signature timestamp within range as well?"""
  f = tempfile.NamedTemporaryFile(mode='w', delete=False)
  f.write(signature)
  f.close()
  verified = gpg.verify_data(f.name, signed)
  if not verified.valid:
    sys.exit("Not a valid OpenPGP signature")
  os.remove(f.name)
  if not validate_timestamp(int(verified.sig_timestamp)):
    sigtime = sig_time()
    sys.exit("Signature timestamp (%d, %s) too far off now (%d, %s)" %
             (verified.sig_timestamp, time_str(verified.sig_timestamp),
              sigtime, time_str(sigtime)))
  if keyid != verified.key_id and keyid != verified.pubkey_fingerprint:
    sys.exit("Received signature with key ID %s; but expected %s -- refusing" %
             (verified.key_id, keyid))


def validate_tag(text, commit, keyid, name, args):
  """Check this tag head to toe"""
  if len(text) > 8000:
    sys.exit("Returned tag too long (%d > 8000)" % len(text))
  if not re.match('^[ -~\n]*$', text, re.MULTILINE):
    sys.exit("Returned tag does not only contain ASCII chars")
  lead = '''object %s
type commit
tag %s
tagger %s ''' % (commit.id, args.tag, name)
  if not text.startswith(lead):
    sys.exit("Expected signed tag to start with:\n"
             "> %s\n\nInstead, it started with:\n> %s\n"
             % (lead.replace('\n', '\n> '), text.replace('\n', '\n> ')))
  pos = validate_timestamp_zone_eol('tagger', text, len(lead))
  if text[pos] != '\n':
    sys.exit("Signed tag has unexpected data after 'tagger' header")

  pgpstart = text.find('\n-----BEGIN PGP SIGNATURE-----\n\n', len(lead))
  if pgpstart >= 0:
    signed = asciibytes(text[:pgpstart + 1])
    signature = text[pgpstart + 1:]
    verify_signature_and_timestamp(keyid, signed, signature, args)
  else:
    sys.exit("No OpenPGP signature found")


def timestamp_tag(repo, commit, keyid, name, args):
  """Obtain and add a signed tag"""
  # pygit2.reference_is_valid_name() is too new
  if not re.match('^[-_a-zA-Z0-9]+$', args.tag):
    sys.exit("Tag name '%s' is not valid for timestamping" % args.tag)
  try:
    r = repo.lookup_reference('refs/tags/' + args.tag)
    sys.exit("Tag '%s' already in use" % args.tag)
  except KeyError:
    pass
  try:
    r = requests.post(args.server,
                      data={
                        'request': 'stamp-tag-v1',
                        'commit': commit.id,
                        'tagname': args.tag
                      })
    if r.status_code != 200:
      sys.exit("Timestamping request failed; server responded with %d %s"
               % (r.status_code, r.reason))
    validate_tag(r.text, commit, keyid, name, args)
    tagid = repo.write(git.GIT_OBJ_TAG, r.text)
    repo.create_reference('refs/tags/%s' % args.tag, tagid)
#    print("Added signed tag '%s'" % args.tag)
  except requests.exceptions.ConnectionError as e:
    sys.exit("Cannot connect to server: %s" % e)


def validate_branch(text, keyid, name, data, args):
  """Check this branch commit head to toe"""
  if len(text) > 8000:
    sys.exit("Returned branch commit too long (%d > 8000)" % len(text))
  if not re.match('^[ -~\n]*$', text, re.MULTILINE):
    sys.exit("Returned branch commit does not only contain ASCII chars")
  lead = 'tree %s\n' % data['tree']
  if 'parent' in data:
    lead += 'parent %s\n' % data['parent']
  lead += '''parent %s
author %s ''' % (data['commit'], name)
  if not text.startswith(lead):
    sys.exit("Expected signed branch commit to start with:\n"
             "> %s\n\nInstead, it started with:\n> %s\n"
             % (lead.replace('\n', '\n> '), text.replace('\n', '\n> ')))
  pos = validate_timestamp_zone_eol('tagger', text, len(lead))
  follow = 'committer %s ' % name
  if not text[pos:].startswith(follow):
    sys.exit("Committer in signed branch commit does not match")
  pos = validate_timestamp_zone_eol('committer', text, pos + len(follow))
  if not text[pos:].startswith('gpgsig '):
    sys.exit("Signed branch commit missing 'gpgsig' after 'committer'")
  sig = re.match('^-----BEGIN PGP SIGNATURE-----\n \n'
                 '[ -~\n]+\n -----END PGP SIGNATURE-----\n\n',
                 text[pos + 7:], re.MULTILINE)
  if not sig:
    sys.exit("Incorrect OpenPGP signature in signed branch commit")
  signature = sig.group()
  # Everything except the signature
  signed = asciibytes(text[:pos] + text[pos+7+sig.end() - 1:])
  signature = signature.replace('\n ', '\n')
  verify_signature_and_timestamp(keyid, signed, signature, args)


def timestamp_branch(repo, commit, keyid, name, args):
  """Obtain and add branch commit; create/update branch head"""
  # pygit2.reference_is_valid_name() is too new
  if not re.match('^[-_a-zA-Z0-9]+$', args.branch):
    sys.exit("Branch name %s is not valid for timestamping" % args.tag)
  branch_head = None
  data = {
    'request': 'stamp-branch-v1',
    'commit': commit.id,
    'tree': commit.tree.id
  }
  try:
    branch_head = repo.lookup_reference('refs/heads/' + args.branch)
    data['parent'] = branch_head.target
    try:
      if repo[branch_head.target].parent_ids[1] == commit.id:
        sys.exit("Already timestamped commit %s to branch %s" % (commit.id.hex, args.branch))
    except IndexError:
      pass
  except KeyError:
    pass
  try:
    r = requests.post(args.server, data)
    if r.status_code != 200:
      sys.exit("Timestamping request failed; server responded with %d %s"
               % (r.status_code, r.reason))
    validate_branch(r.text, keyid, name, data, args)
    commitid = repo.write(git.GIT_OBJ_COMMIT, r.text)
    repo.create_reference('refs/heads/' + args.branch, commitid, force=True)
  except requests.exceptions.ConnectionError as e:
    sys.exit("Cannot connect to server: %s" % e)


def main():
    global repo, gpg
    requests.__title__ = 'git-timestamp/%s %s' % (VERSION, requests.__title__)
    path = git.discover_repository(os.getcwd())
    if path == None:
      sys.exit("Not a git repository")
    repo = git.Repository(path)
    args = get_args()
    
    try:
      commit = repo.revparse_single(args.commit)
    except KeyError as e:
      sys.exit("No such revision: '%s'" % (e,))
    
    try:
        gpg = gnupg.GPG(gnupghome=args.gnupg_home)
    except TypeError:
        traceback.print_exc()
        sys.exit("*** 'git timestamp' needs 'python-gnupg' module from PyPI, not 'gnupg'")
    (keyid, name) = get_keyid(args.server)
    if args.tag:
      timestamp_tag(repo, commit, keyid, name, args)
    else:
      timestamp_branch(repo, commit, keyid, name, args)


if __name__ == "__main__":
    main()
