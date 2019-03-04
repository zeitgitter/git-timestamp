#!/bin/sh
d=$1
shift
wget --no-verbose -O $d/22-stamp-branch1-server.asc --content-on-error "$@" \
  --post-data='request=stamp-branch-v1&commit=2222222222222222222222222222222222222222&parent=3333333333333333333333333333333333333333&tree=4444444444444444444444444444444444444444' \
  'http://localhost:8080/'
cat > $d/22-stamp-branch1-verify.asc << EOF
tree 4444444444444444444444444444444444444444
parent 3333333333333333333333333333333333333333
parent 2222222222222222222222222222222222222222
author Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
committer Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
gpgsig -----BEGIN PGP SIGNATURE-----
 
 iF0EABECAB0WIQTKSvqybFiyCVmcgCU1Pf7FEvpHxwUCXHS/qwAKCRA1Pf7FEvpH
 xwVtAJ9o86f04lZXMuJNKA51Ivqk+iiopgCglRscs8qwX2OShbc1m0PND9xFQMc=
 =OETd
 -----END PGP SIGNATURE-----

https://hagrid.snakeoil branch timestamp 2019-02-26 04:25:15 UTC
EOF
diff $d/22-stamp-branch1-*.asc
