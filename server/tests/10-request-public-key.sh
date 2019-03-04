#!/bin/sh
d=$1
shift
wget --no-verbose -O $d/10-public-key-server.asc  --content-on-error "$@" \
  'http://localhost:8080/?request=get-public-key-v1'
cat > $d/10-public-key-verify.asc << EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
EOF
diff $d/10-public-key-*.asc
