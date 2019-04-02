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

# Sending and receiving mail

import os
import logging
import subprocess
import igitt.config

from datetime import datetime, timedelta
from pathlib import Path
from time import gmtime, strftime
from smtplib import SMTP, SMTPException
from imaplib import IMAP4


def split_host_port(host, default_port):
  if ':' in host:
    host, port = host.split(':', 1)
    return (host, int(port))
  else:
    return (host, default_port)


def send(body, subject='Stamping request', to=None):
  # Does not work in unittests if assigned in function header
  # (are bound too early? At load time instead of at call time?)
  if to is None:
    to=igitt.config.arg.external_pgp_timestamper_to
  (host, port) = split_host_port(igitt.config.arg.smtp_server, 587)
  with SMTP(host, port=port,
            local_hostname=igitt.config.arg.own_domain) as smtp:
    smtp.starttls()
    smtp.login(igitt.config.arg.mail_username,
               igitt.config.arg.mail_password)
    frm = igitt.config.arg.email_address
    date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    msg = """From: %s
To: %s
Date: %s
Subject: %s

%s
""" % (frm, to, date, subject, body)
    smtp.sendmail(frm, to, msg)


def extract_pgp_body(body):
  try:
    body = str(body, 'ASCII')
  except TypeError:
    return None
  lines = body.splitlines()
  start = None
  for i in range(0, len(lines) - 1):
    if lines[i] == '-----BEGIN PGP SIGNED MESSAGE-----':
      start = i
      break
  else:
    return None

  end = None
  for i in range(start, len(lines) - 1):
    if lines[i] == '-----END PGP SIGNATURE-----':
      end = i
      break
  else:
    return None
  return lines[start:end+1]


def save_signature(bodylines):
  with open(Path(igitt.config.arg.repository, 'hashes.asc'), 'x') as f:
    f.write('\n'.join(bodylines))
  logging("Written!")

def body_signature_correct(bodylines, stat):
  body = '\n'.join(bodylines)
  # Cannot use Python gnupg wrapper: Requires pgp1.x to verify
  # Copy env for gnupg without locale
  env = {}
  for k in os.environ:
    if not k.startswith('LC_'):
      env[k] = os.environ[k]
  env['LANG'] = 'C'
  env['TZ'] = 'UTC'
  res = subprocess.run(['gpg1', '--pgp2', '--verify'],
                       encoding = 'ASCII', env=env,
                       input=body, stderr=subprocess.PIPE)
  if res.returncode != 0:
    return False
  logging.debug(res.stderr)
  if not '\ngpg: Good signature' in res.stderr:
    logging.warn("Not good signature (%r)" % res.stderr)
    return False
  if not res.stderr.startswith('gpg: Signature made '):
    logging.warn("Signature not made (%r)" % res.stderr)
    return False
  if not ((' key ID %s\n' % igitt.config.arg.external_pgp_timestamper_keyid)
    in res.stderr):
    logging.warn("Wrong KeyID (%r)" % res.stderr)
    return False
  try:
    logging.debug(res.stderr[24:48])
    sigtime = datetime.strptime(res.stderr[24:48], "%b %d %H:%M:%S %Y %Z")
    logging.debug(sigtime)
  except ValueError:
    logging.warn("Illegal date (%r)" % res.stderr)
    return False
  if sigtime > datetime.utcnow() + timedelta(seconds=30):
    logging.warn("Signature time %s lies more than 30 seconds in the future"
          % sigtime)
    return False
  modtime = datetime.utcfromtimestamp(stat.st_mtime)
  if sigtime < modtime - timedelta(seconds=30):
    logging.warn("Signature time %s is more than 30 seconds before\n"
          "file modification time %s"
          % (sigtime, modtime))
    return False
  return True


def verify_body_and_save_signature(body, stat):
  bodylines = extract_pgp_body(body)
  if bodylines is None:
    logging.warn("No body lines")
    return False

  res = body_contains_file(bodylines)
  if res is None:
    logging.warn("No res %s" % '\n'.join(bodylines))
    return False
  else:
    (before, after) = res
    logging.debug("before %d, after %d" % (before, after))
    if before > 20 or after > 20:
      logging.warn("Before/after wrong")
      return False

  if not body_signature_correct(bodylines, stat):
    logging.warn("Body signature incorrect")
    return False

  save_signature(bodylines)
  return True


def body_contains_file(bodylines):
  if bodylines is None:
    return None
  linesbefore = 0
  with open(Path(igitt.config.arg.repository, 'hashes.log'), 'r') as f:
    # A few empty/comment lines at the beginning
    firstline = f.readline().rstrip()
    for i in range(len(bodylines)):
      if bodylines[i] == firstline:
        break
      elif bodylines[i] == '' or bodylines[i][0] in '#-':
        linesbefore += 1
      else:
        return None
    # Now should be contiguous
    i += 1
    for l in f:
      if bodylines[i] != l.rstrip():
        return None
      i += 1
    # Now there should only be empty lines and a PGP signature
    linesafter = len(bodylines) - i
    i += 1
    while bodylines[i] == '':
      i += 1
    if bodylines[i] != '-----BEGIN PGP SIGNATURE-----':
      return None
    # No further line starting with '-'
    for i in range(i+1, len(bodylines)-1):
      if bodylines[i] != '' and bodylines[i][0] == '-':
        return None
    return (linesbefore, linesafter)


def imap_idle(imap, stat):
  imap.send(b'%s IDLE\r\n' % (imap._new_tag()))
  logging.debug("IMAP IDLE")
  while True:
    logging.debug("IMAP waiting for IDLE response")
    line = imap.readline().strip()
    logging.debug("IMAP IDLE → %s" % line)
    logging.debug("…")
    if line == b'' or line.startswith(b'* BYE '):
      logging.debug("IMAP IDLE ends False")
      return False
    if line.endswith(b' EXISTS'):
      logging.debug("You have new mail!")
      # Stop idling
      imap.send(b'DONE\r\n')
      if check_for_stamper_mail(imap, stat) is True:
        logging.debug("IMAP IDLE ends False")
        return True
      logging.debug("x")
    logging.debug("loop")


def check_for_stamper_mail(imap, stat):
  logging.debug("IMAP SEARCH…")
  (typ, msgs) = imap.search(
    None,
    'FROM', '"%s"' % igitt.config.arg.external_pgp_timestamper_reply,
    'UNSEEN',
    'LARGER', str(stat.st_size),
    'SMALLER', str(stat.st_size + 8192))
  logging.debug("IMAP SEARCH → %s, %s" % (typ, msgs))
  if len(msgs) == 1 and len(msgs[0]) > 0:
    mseq = msgs[0].replace(b' ', b',')
    logging.debug(mseq)
    (typ, contents) = imap.fetch(mseq, 'BODY[TEXT]')
    logging.debug("IMAP FETCH → %s, %d" % (typ, len(contents)))
    for m in contents:
      if m != b')':
        logging.debug("IMAP FETCH BODY → %s" % m[1][:20])
        if verify_body_and_save_signature(m[1], stat):
          logging.debug("Verify_body() succeeded")
          return True
  return False


def receive_async():
  try:
    stat = os.stat(Path(igitt.config.arg.repository,
                                "hashes.log"))
    logging.debug("File is from %d" % stat.st_mtime)
  except FileNotFoundError:
    return False
  try:
    (host, port) = split_host_port(igitt.config.arg.imap_server, 143)
    with IMAP4(host=host, port=port) as imap:
      imap.starttls()
      imap.login(igitt.config.arg.mail_username,
                 igitt.config.arg.mail_password)
      imap.select('INBOX')
      if check_for_stamper_mail(imap, stat) is False:
        # No existing message found, wait for more incoming messages
        imap_idle(imap, stat)
  except FileNotFoundError: # XXX dummy exception
    pass
