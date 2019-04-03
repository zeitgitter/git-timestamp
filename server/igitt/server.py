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

# HTTP request handling


import cgi
import os
import re
import socket
import socketserver
import urllib
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import igitt.commit
import igitt.config
import igitt.stamper
import igitt.version


class SocketActivationMixin:
  """Use systemd provided socket, if available.
  When socket activation is used, exactly one socket needs to be passed."""

  def server_bind(self):
    nfds = 0
    if os.environ.get('LISTEN_PID', None) == str(os.getpid()):
      nfds = int(os.environ.get('LISTEN_FDS', 0))
      if nfds == 1:
        self.socket = socket.fromfd(3, self.address_family, self.socket_type)
      else:
        logging.error("Socket activation must provide exactly one socket (for now)\n")
        exit(1)
    else:
      super().server_bind()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
  """Replacement for http.server.ThreadingHTTPServer for Python < 3.7"""
  pass


class SocketActivationHTTPServer(SocketActivationMixin, ThreadingHTTPServer):
  address_family = socket.AF_INET6


class FlatFileRequestHandler(BaseHTTPRequestHandler):
  def send_file(self, content_type, filename, replace={}):
    try:
      f = open(Path(igitt.config.arg.webroot, filename), 'rb')
      contents = f.read()
      f.close()
      for k, v in replace.items():
        contents = contents.replace(k, v)
      self.send_response(200)
      self.send_header('Content-Type', content_type)
      self.send_header('Content-Length', len(contents))
      self.end_headers()
      self.wfile.write(contents)
    except IOError as e:
      self.send_bodyerr(404, "File not found",
                        "This file was not found on this server")

  def send_bodyerr(self, status, title, body):
    explain = """<html><head><title>%s</title></head>
<body><h1>%s</h1>%s
<p><a href="/">Go home</a></p></body></html>
""" % (title, title, body)
    explain = bytes(explain, 'UTF-8')
    self.send_response(status)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(explain))
    self.end_headers()
    self.wfile.write(explain)

  def do_GET(self):
    print(self.path)
    if self.path == '/':
      self.send_file('text/html', 'index.html',
                     replace={b'IGITT_DOMAIN': bytes(igitt.config.arg.own_domain,
                                                     'ASCII')})
    else:
      match = re.match('^/([a-z0-9][-_.a-z0-9]*).(html|css|js|png|jpe?g|svg)$', self.path, re.IGNORECASE)
      mimemap = {
        'html': 'text/html',
        'css': 'text/css',
        'js': 'text/javascript',
        'png': 'image/png',
        'svg': 'image/svg+xml',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'}
      if match and match.group(2) in mimemap:
        self.send_file(mimemap[match.group(2)], self.path[1:])
      else:
        self.send_bodyerr(406, "Illegal file name",
                          "<p>This type of file/path is not served here.</p>")


class StamperRequestHandler(FlatFileRequestHandler):
  def __init__(self, *args, **kwargs):
    self.public_key = None
    self.stamper = igitt.stamper.Stamper()
    self.protocol_version = 'HTTP/1.1'
    super().__init__(*args, **kwargs)

  def version_string(self):
    return "IGITT/" + igitt.version.VERSION

  def send_public_key(self):
    if self.public_key == None:
      self.public_key = self.stamper.get_public_key()
    if self.public_key == None:
      self.send_bodyerr(500, "Internal server error",
                        "<p>No public key found</p>")
    else:
      pk = bytes(self.public_key, 'ASCII')
      self.send_response(200)
      self.send_header('Content-Type', 'application/pgp-keys')
      self.send_header('Content-Length', len(pk))
      self.end_headers()
      self.wfile.write(pk)

  def handle_signature(self, params):
    if 'request' in params:
      if (params['request'][0] == 'stamp-tag-v1'
          and 'commit' in params and 'tagname' in params):
        return self.stamper.stamp_tag(params['commit'][0],
                                      params['tagname'][0])
      elif (params['request'][0] == 'stamp-branch-v1'
            and 'commit' in params and 'tree' in params):
        if 'parent' in params:
          return self.stamper.stamp_branch(params['commit'][0],
                                           params['parent'][0], params['tree'][0])
        else:
          return self.stamper.stamp_branch(params['commit'][0],
                                           None, params['tree'][0])
    else:
      return 406

  def handle_request(self, params):
    sig = self.handle_signature(params)
    if sig == 406:
      self.send_bodyerr(406, "Unsupported timestamping request",
                        "<p>See the documentation for the accepted requests</p>")
    elif sig == None:
      self.send_bodyerr(429, "Too many requests",
                        "<p>The server is currently overloaded</p>")
    else:
      sig = bytes(sig, 'ASCII')
      self.send_response(200)
      self.send_header('Content-Type', 'application/x-git-object')
      self.send_header('Content-Length', len(sig))
      self.end_headers()
      self.wfile.write(sig)

  def do_POST(self):
    ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
    try:
      clen = self.headers['Content-Length']
      clen = int(clen)
    except:
      self.send_bodyerr(411, "Length required",
                        "<p>Your request did not contain a valid length</p>")
      return
    if clen > 1000 or clen < 0:
      self.send_bodyerr(413, "Request too long",
                        "<p>Your request is too long</p>")
      return
    if ctype == 'multipart/form-data':
      params = cgi.parse_multipart(self.rfile, pdict)
      self.handle_request(params)
    elif ctype == 'application/x-www-form-urlencoded':
      contents = self.rfile.read(clen)
      contents = contents.decode('UTF-8')
      params = urllib.parse.parse_qs(contents)
      self.handle_request(params)
    else:
      self.send_bodyerr(415, "Unsupported media type",
                        "<p>Need form data input</p>")

  def do_GET(self):
    if self.path.startswith('/?'):
      params = urllib.parse.parse_qs(self.path[2:])
      if 'request' in params and params['request'][0] == 'get-public-key-v1':
        self.send_public_key()
      else:
        self.send_bodyerr(406, "Bad parameters",
                          "<p>Need a valid `request` parameter</p>")
    else:
      super().do_GET()


def run():
  igitt.config.get_args()
  igitt.commit.run()
  httpd = SocketActivationHTTPServer(
    (igitt.config.arg.listen_address, igitt.config.arg.listen_port),
    StamperRequestHandler)
  # ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  # httpd.socket = ssl.wrap_socket(httpd.socket,
  #        keyfile='cert/key.pem',
  #        certfile='cert/cert.pem', server_side=True)
  logging.info("Start serving")
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    pass
  httpd.server_close()
