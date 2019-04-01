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

# Test GPG signature creation

import os
import pathlib
import tempfile
import threading

import igitt.config
import igitt.stamper


def assertEqual(a, b):
  if type(a) != type(b):
    raise AssertionError(
      "Assertion failed: Type mismatch %r (%s) != %r (%s)"
      % (a, type(a), b, type(b)))
  elif a != b:
    raise AssertionError(
      "Assertion failed: Value mismatch: %r (%s) != %r (%s)"
      % (a, type(a), b, type(b)))


def setup_module():
  global stamper
  global tmpdir
  tmpdir = tempfile.TemporaryDirectory()
  igitt.config.get_args(args=[
    '--gnupg-home',
    str(pathlib.Path(os.path.dirname(os.path.realpath(__file__)),
                     'gnupg')),
    '--keyid', '353DFEC512FA47C7',
    '--own-url', 'https://hagrid.snakeoil',
    '--max-parallel-signatures', '10',
    '--max-parallel-timeout', '1',
    '--repository', tmpdir.name])
  stamper = igitt.stamper.Stamper()
  os.environ['IGITT_FAKE_TIME'] = '1551155115'


def teardown_module():
  del os.environ['IGITT_FAKE_TIME']
  tmpdir.cleanup()


def test_commit():
  assert stamper.valid_commit('0123456789012345678901234567890123456789')
  assert stamper.valid_commit('0123456789abcdef678901234567890123456789')
  assert not stamper.valid_commit('012345678901234567890123456789012345678')
  assert not stamper.valid_commit('0123456789012345678901234567890123456789\n')
  assert not stamper.valid_commit('01234567890123456789012345678901234567890')
  assert not stamper.valid_commit('0123456789ABCDEF678901234567890123456789')
  assert not stamper.valid_commit('0123456789abcdefghij01234567890123456789')
  for i in (set(range(0, 255))
            - set(range(ord('0'), ord('0') + 10))
            - set(range(ord('a'), ord('a') + 6))):
    commit = chr(i) * 40
    if stamper.valid_commit(commit):
      raise AssertionError(
        "Assertion failed: '%s' (%d) is valid commit" % (commit, i))


def test_tag():
  assert stamper.valid_tag('a')
  assert stamper.valid_tag('a' * 100)
  assert stamper.valid_tag('A' * 100)
  assert stamper.valid_tag('abcdefghijklmnopqrstuvwxyz0123456789-_')
  assert not stamper.valid_tag('')
  for i in (set(range(0, 255))
            - set((ord('-'), ord('_')))
            - set(range(ord('0'), ord('0') + 10))
            - set(range(ord('A'), ord('A') + 26))
            - set(range(ord('a'), ord('a') + 26))):
    if stamper.valid_tag('a' + chr(i)):
      raise AssertionError(
        "Assertion failed: 'a%s' (%d) is valid tag" % (chr(i), i))
  for i in (set(range(0, 255))
            - set(range(ord('A'), ord('A') + 26))
            - set(range(ord('a'), ord('a') + 26))):
    if stamper.valid_tag(chr(i)):
      raise AssertionError(
        "Assertion failed: '%s' (%d) is valid tag" % (chr(i), i))
  assert not stamper.valid_tag('a ')
  assert not stamper.valid_tag('0')
  assert not stamper.valid_tag('a' * 101)


def test_pubkey():
  pubkey = stamper.get_public_key()
  assertEqual(pubkey, """-----BEGIN PGP PUBLIC KEY BLOCK-----

mQGiBFx0B0kRBACw2++3YW1ECOVsXBCd0RuXdIJHaJ8z4EfPhG6cnJWeITFawTBw
4uboTu2NZ99qWH/eEGcOGS38TZvZHbti65AeWkks8SV7nuwuWXF4td0+dVXkDieP
XTw7O8dCI8gDlvpCE+FSgzjzQjSSyYzsCju0GXCZYORrFzU2oILUzloe6wCgpP7l
nhd+0ulQyU87q/n12uLRO1ED+wT7sLS/+RVlwpKPc7cm9JQ/bJEDFOVn1RUWPPAI
lmZjhX78hf5xg6mwqOastH4i0D4CL3TjRzrbu2XF7Is86sp1NKlEXFeWUMpIeFak
eTcFg9DAyB+I84GZHFpXajC8fkz78rJvuDBwLa8p249kWOOb7MZnsLGJNM5mRk1D
uKu5A/97BIRhMYT2nKaR6TKE1QSs4dLG0/ZyGW30P+iYALqcRybHhJfNn2sVkAre
fo+5+id3NgWqU+/Zm+3QRLoHTKzrurR+amZ8EGoE3szlnLH1kkfSJqhN038e02Hn
osUGGIBpVW4IoTltElCX+wJrYF+EAFR5dGv6PjNTuKF7SKMH7bRDSGFncmlkIFNu
YWtlb2lsIFRpbWVzdG9tcGluZyBTZXJ2aWNlIDx0aW1lc3RvbXBpbmdAaGFncmlk
LnNuYWtlb2lsPoh4BBMRAgA4FiEEykr6smxYsglZnIAlNT3+xRL6R8cFAlx0B0kC
GwMFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQNT3+xRL6R8e96QCffB81wYci
eUVPRmPROLObWS2mzfEAn1dMGgRB2pPRQeaayWyodleWuWZy
=w4y2
-----END PGP PUBLIC KEY BLOCK-----
""")


def test_sign_tag():
  tagstamp = stamper.stamp_tag('1' * 40, 'sample-timestamping-tag')
  print(tagstamp)
  assertEqual(tagstamp, """object 1111111111111111111111111111111111111111
type commit
tag sample-timestamping-tag
tagger Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000

https://hagrid.snakeoil tag timestamp
-----BEGIN PGP SIGNATURE-----

iF0EABECAB0WIQTKSvqybFiyCVmcgCU1Pf7FEvpHxwUCXHS/qwAKCRA1Pf7FEvpH
x4NcAJ92bPgI8D7Qz0MH5WCTmCSw9ohNPwCfe0DEodj23WzTicziH/3INpnEzKk=
=ekTn
-----END PGP SIGNATURE-----
""")


def test_sign_branch1():
  branchstamp = stamper.stamp_branch('1' * 40, '2' * 40, '3' * 40)
  print(branchstamp)
  assertEqual(branchstamp, """tree 3333333333333333333333333333333333333333
parent 2222222222222222222222222222222222222222
parent 1111111111111111111111111111111111111111
author Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
committer Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
gpgsig -----BEGIN PGP SIGNATURE-----
 
 iF0EABECAB0WIQTKSvqybFiyCVmcgCU1Pf7FEvpHxwUCXHS/qwAKCRA1Pf7FEvpH
 xyE2AJwLFob5fXtSJ/kt/o3H+ueKezt+UACeOuJYxrYDlFDykS528B4oJ5YzNvo=
 =sAaK
 -----END PGP SIGNATURE-----

https://hagrid.snakeoil branch timestamp 2019-02-26 04:25:15 UTC
""")


def test_sign_branch2():
  branchstamp = stamper.stamp_branch('1' * 40, None, '3' * 40)
  print(branchstamp)
  assertEqual(branchstamp, """tree 3333333333333333333333333333333333333333
parent 1111111111111111111111111111111111111111
author Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
committer Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
gpgsig -----BEGIN PGP SIGNATURE-----
 
 iF0EABECAB0WIQTKSvqybFiyCVmcgCU1Pf7FEvpHxwUCXHS/qwAKCRA1Pf7FEvpH
 x/jRAJ0eUDsZAHp3xzxX2r6zoS65Z5ZzngCghatkz5MdU3qoS4QBvjQS7RwAqfE=
 =REbT
 -----END PGP SIGNATURE-----

https://hagrid.snakeoil branch timestamp 2019-02-26 04:25:15 UTC
""")


def test_multithreading1():
  stamper.extra_delay = 0.5
  threads = []
  for i in range(20):
    t = threading.Thread(target=test_sign_tag, name="test_multithreading1_%d" % i)
    t.start()
    threads.append(t)
  for t in threads:
    t.join()


counter_lock = threading.Lock()
counter = 0


def count_sign_tag():
  global counter
  try:
    test_sign_tag()
    with counter_lock:
      counter = counter + 1
  except AssertionError:
    pass


def test_multithreading5():
  stamper.extra_delay = 1.5
  threads = []
  for i in range(20):
    t = threading.Thread(target=count_sign_tag, name="test_multithreading5_%d" % i)
    t.start()
    threads.append(t)
  for t in threads:
    t.join()
  print('counter =' + str(counter))
  assert (counter == 10)
