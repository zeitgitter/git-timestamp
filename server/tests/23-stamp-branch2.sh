#!/bin/sh
d=$1
shift
wget --no-verbose -O $d/23-sign-branch2-server.asc --content-on-error "$@" \
  --post-data='request=stamp-branch-v1&commit=5555555555555555555555555555555555555555&tree=6666666666666666666666666666666666666666' \
  'http://localhost:8080/'
cat > $d/23-sign-branch2-verify.asc << EOF
tree 6666666666666666666666666666666666666666
parent 5555555555555555555555555555555555555555
author Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
committer Hagrid Snakeoil Timestomping Service <timestomping@hagrid.snakeoil> 1551155115 +0000
gpgsig -----BEGIN PGP SIGNATURE-----
 
 iF0EABECAB0WIQTKSvqybFiyCVmcgCU1Pf7FEvpHxwUCXHS/qwAKCRA1Pf7FEvpH
 x60BAJ9f0xVkHTbeLS9mKH4QYGgETmFNSACdHIk0gfjAfLMG4h7IC4QVto7hpFk=
 =MuCU
 -----END PGP SIGNATURE-----

https://hagrid.snakeoil branch timestamp 2019-02-26 04:25:15 UTC
EOF
diff $d/23-sign-branch2-*.asc
