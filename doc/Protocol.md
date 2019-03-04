# The `igitt` Protocol

The `igitt` protocol sits on top of HTTPS and can be used to obtain
timestamped, signed `git` objects to be added to one's `git` repository,
typically using the [`git timestamp`](../client/) command.

Like this, the timestamping server does not need to know any contents of
your `git` repository, with the exception of some hashes and, when
signing a tag, also the name of the tag. Most importantly, the
timestamper does *not* learn about:

- then contents of your files
- your users
- the number or times of any commits *not* submitted for timestamping

## Obtaining public key of timestamper

`GET` request to the URL with the following variables:

- `request`: `get-public-key-v1`


## Obtaining a tag signature

`POST` request to URL with the following variables:

- `request`: `stamp-tag-v1`
- `commit`: The SHA-1 commit ID to be tagged and timestamped
- `tagname`: The name of the tag, limited to ASCII digits, letters,
  dash and underscore of at most 100 characters. Must start with a letter.

Returns a signed `git` tag object referring to the commit object in the
response body as follows:

```
object <commit object ID>
type commit
tag <tagname>
tagger <timestamper name> <timestamper email> <Unix time> +0000

<message by the timestamper>
-----BEGIN PGP SIGNATURE-----

[…]
-----END PGP SIGNATURE-----
```

Before adding the object to the `git` object store, the client should 
verify that:

- The commit ID matches what it sent
- The tag name matches what it sent
- The timestamper name/email matches what it expects; its length does 
  not exceed 200 characters
- The Unix time lies between the start of the request and the end of 
  the request, within a given fuzz parameter (e.g., 30 seconds)
- The message contains only ASCII printable characters and newline 
  (`\n`, ' '…'~'); its length does not exceed 1000 characters
- The PGP signature contains only ASCII printable characters and 
  newline; its length does not exceed 4000 characters
- The PGP signature verifies as a detached signature to the remainder
  of the tag's contents ([the contents are treated as binary data, no
  text normalization is done](https://tools.ietf.org/html/rfc4880#section-5.2.4)).
- The PGP signature timestamp also lies within the window of the Unix 
  time as specified above (it does not necessary need to be identical, 
  as the timestamping process does not make it easy to guarantee this)
- [Only a single signature should be
  present](https://dev.gentoo.org/~mgorny/articles/attack-on-git-signature-verification.html)

`POST` parameters can submitted in either
`application/x-www-form-urlencoded` or `multipart/form-data` format.

## Obtaining a branch signature

`POST` request to the URL with the following variables:

- `request`: `stamp-branch-v1`
- `commit`: The SHA-1 commit ID to be timestamped
- `parent` (optional): The SHA-1 commit ID to be listed as the branch parent
- `tree`: The SHA-1 tree ID of the file contents

Returns a signed `git` commit, looking like a merge from the `commit` 
to the branch of the `parent`, but with the exact file contents of the
tree at `commit`:

```
tree <tree ID>
parent <parent ID>
parent <commit ID>
author <timestamper name> <timestamper email> <Unix time> +0000
committer <timestamper name> <timestamper email> <Unix time> +0000
gpgsig -----BEGIN PGP SIGNATURE-----
 […]
 -----END PGP SIGNATURE-----

<message by the timestamper>
```

Before adding the object to the `git` object store, similar to the
tag signature behavior above, the client should verify that:

- Tree, parent, and commit IDs match what it sent
- The `author` and `committer` follow the `tagger` rules above
- Unix times and PGP signature times follow the rules above
- PGP signature and message bodies follow the rules above
  * For signature verification, [`gpgsig` multi-line header must be
    stripped from the resulting
    file](https://github.com/git/git/blob/master/Documentation/technical/signature-format.txt)

(Assuming you branch-sign every commit of the `master` branch into the
`timestamp` branch, the two will develop in parallel, with `timestamp`
being a timestamper-signed equivalent of the former.)
