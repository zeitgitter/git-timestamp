# `igitt` operation

`igitt` listens on an HTTPS port and awaits `POST` requests for signing a tag
or a branch commit. It then returns the appropriate information, ready for the
client to integrate it into its `git` repository, from where it then can be

- verified using `git tag -v <tagname>` or `git verify-commit <commit>`, and/or
- published to other repositories.

For each of these events, one line of CSV protocol will be created, containing

- event sequence number
- date and time of day (seconds since 1970-01-01 00:00 UTC, aka *the epoch*)
- type of signature (`tag`, `branch`, or `link`)
- the commit ID to which the signature refers
- request origin, either
  * username for a registered user,
  * country of the request's IP address (unreliable), or
  * the service name and path to the previous file (for `link` only).

There is exactly one `link` entry in each file, except the first. It contains
the commit ID of the repository after the previous file was committed. 

Each of these entries will be in an hourly file, located in a `git` repository
which is pushed every hour to `github.com`. Feel free to pull from that
repository once an hour.  In addition, the contents of these files will
submitted to the PGP Timestamper after the files have been submitted, and these
signatures will be stored as detached signatures next to the files. It will
take several minutes before these signature files arrive, so please be patient.

In XXX
