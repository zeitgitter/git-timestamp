#!/bin/sh
d=$1
shift
wget --no-verbose -O $d/21-stamp-tag-server.asc --content-on-error "$@" \
  --post-data='request=stamp-tag-v1&commit=1111111111111111111111111111111111111111&tagname=sample-timestämping-tag' \
  'http://localhost:8080/'
cat > $d/21-stamp-tag-verify.asc << EOF
<html><head><title>Unsupported timestamping request</title></head>
<body><h1>Unsupported timestamping request</h1><p>See the documentation for the accepted requests</p>
<p><a href="/">Go home</a></p></body></html>
EOF
diff $d/21-stamp-tag-*.asc
