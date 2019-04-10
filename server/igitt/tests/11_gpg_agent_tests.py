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

# Test GPG parallel signature creation

import os
import pathlib
import tempfile
import threading
import time

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
    '--country', '', '--owner', '', '--contact', '',
    '--keyid', '353DFEC512FA47C7',
    '--own-url', 'https://hagrid.snakeoil',
    '--max-parallel-signatures', '10',
    '--max-parallel-timeout', '1',
    '--number-of-gpg-agents', '10',
    '--repository', tmpdir.name])
  stamper = igitt.stamper.Stamper()
  os.environ['IGITT_FAKE_TIME'] = '1551155115'


def teardown_module():
  del os.environ['IGITT_FAKE_TIME']
  tmpdir.cleanup()


def test_sign_tag():
  tagstamp = stamper.stamp_tag('1' * 40, 'sample-timestamping-tag')
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

delta1 = None
delta5 = None

def test_gpg_agent1():
  global delta1
  start = time.time()
  for i in range(20):
    test_sign_tag()
  delta1 = time.time()-start


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


def test_gpg_agent5():
  global delta5
  start = time.time()
  threads = []
  for i in range(20):
    t = threading.Thread(target=count_sign_tag, name="test_gpg_agent5_%d" % i)
    t.start()
    threads.append(t)
  for t in threads:
    t.join()
  delta5 = time.time()-start

def test_gpg_agent9():
  """Test again with warm cache"""
  global delta1
  d1copy = delta1
  # Overwrites delta1
  test_gpg_agent1()
  # Temporarily add "or True" to see the performance
  if d1copy < delta5 or delta1 < delta5:
    raise AssertionError("""Parallelizing does not give any benefit
    First sequential run:  %s
    Parallel run:          %s
    Second sequential run: %s""" % (d1copy, delta5, delta1))
