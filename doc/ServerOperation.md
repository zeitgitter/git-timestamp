# The `igitt` Timestamping Server: Operations and Repository Format

To ensure transparency and to prevent later backdating of timestamps,
the timestamping server keeps a public log of its activities. They
are stored in a `git` repository as well.

The `git` repository already uses cryptographic hashes to chain the
current commit state to the previous commit state and, transitively,
to all its ancestors. Therefore, once a single commit is published
or otherwise assured or notarized, not only does this commit become
immutable, *all* its ancestor commits become immutable as well.

## Logging timestamps

To perform the assurances for any commit, the following methods are used
to ensure that later modifications to the log are not possible:

1. Evert `git` commit ID which is timestamped is written to a log.
2. In regular intervals, each log (containing the hashes of the commits
   timestamped) is committed to a `git` repository maintained by the
   timestamper. This ensures that backdating is only possible within
   this window. The window size is chosen as a tradeoff between the
   overhead of creating a commit and assuring the commit on one hand
   and the accuracy needed for the time stamp. (The receiver of the
   timestamp has one timestamp at second granularity; but a misbehaving
   timestamper might falsely create a timestamp within this window.)
   We assume that a granularity of one hour is a suitable tradeoff for
   most purposes.
3. Optionally, some or all of these log commits might be assured by
   further means (see below).
   
## Means of assurance

Not all of these measures need to be taken.

1. Self-timestamped publishing.
   * The timestamper signs log commits itself.
   * The timestamper publishes this commit.
   * Interested third parties obtain a copy of these commits and store them.

   This does not prevent the timestamper from backdating its signatures,
   but it will allow the third parties to point out this backdating.
   These cryptographic digital signatures can then be used to
   prove this misbehavior and incriminate the perpetrator.

2. Third-party `igitt` timestamping.
   * This `git` repository can be timestamped like any other `git`
     repository.

   Assuming the independence of the other `igitt` timestamping servers,
   this provides further third-party assurances. Assuming the
   unidirectional timestamping edges form a graph where each timestamper
   can reach every other timestamper, the existence of only a single
   trustworthy timestamper in this graph severely limits the abilities
   of the other participants to misbehave.

3. Third-party timestamping through the
   [PGP Digital Timestamping Service](http://www.itconsult.co.uk/stamper.htm).
   * Getting a timestamp from the oldest-running public timestamping
     service binds the `igitt` timestamper.

4. Third-party timestamping through other means.
   * Any other timestamping service can be used as well.
   
   Its use and format needs to be documented by the respective
   implementor.

A timestamper MUST choose a non-empty subset of the assurance mechanisms
outlined above. It SHOULD always self-timestamp, independent of the
publishing intent. It also SHOULD obtain at least one third-party
timestamp, preferably at least two.

Each `igitt` service should document and publish its policy.

# Repository structure

- All log commits are done to the `master` branch of the repository.
  This provides a linear history.
- Every log commit of the repository contains the ASCII-armored OpenPGP
  public key used by the timestamper. This file is called `pubkey.asc`.
- Every log commit contains a list of all the hashes timestamped *in
  this period*. Hashes outside that window are included in the log file
  responsible for that period only. This file is called `hashes.log`
  and is sorted in timestamping order. (In high concurrency situations,
  there might be minor reordering visible at second boundaries.)
- Every commit is signed by the timestamper itself.

# Repository operation

## Creating the log

1. Any incoming hash requested for timestamping is written to a
   temporary file on stable media.  
   This is to ensure that every hash ever timestamped is documented in
   the log, i.e., no timestamp is ever created which cannot be seen in
   the log. This is required to prove attempts at backdating.
2. The timestamp signature is created and then returned to the requestor.

## Rotating the log

1. At the end of the time window (e.g., the one hour outlined above),
   the temporary file created above is sorted, duplicates are removed,
   and used to overwrite the `hashes.log` created in the previous
   window.
2. External timestamps requiring files to be associated with this commit
   are obtained and stored and stored alongside (see "Obtaining PGP
   Timestamps" below)
3. The public key, the log, and optional file-based external timestamps
   are committed to the `git` repository, signed with the timestamper's
   key.
4. `igitt`-based timestamps are obtained and included in the repository
   (see "Obtaining `igitt` Timestamps below).
5. The changes are published, if desired.

## Obtaining PGP Timestamps

To obtain the PGP Timestamp from the
[PGP Digital Timestamping Service](http://www.itconsult.co.uk/stamper.htm),
an ASCII-only email with the following contents is emailed to
`clear@stamper.itconsult.co.uk`:

- The contents of `hashes.log`
- An empty line.
- An additional line `Parent: <commit ID>` indicating the current
  `HEAD` of the `git` repository. This is to ensure cryptographic
  linking of the `git` repository commit ID to the contents of the
  file.

The returned answer is stored as `hashes.asc`, from
`-----BEGIN PGP SIGNED MESSAGE-----` to `-----END PGP SIGNATURE-----`,
inclusively.

Before committing the PGP Timestamp, the following checks should be
applied:

- The answer arrives within 15 minutes
- All the contents sent to timestamper are included in the reply.
- At most 20 additional lines, either empty or starting with `#`,
  are present; each not longer than 100 bytes; each can be either before
  or after the original message.
- The message contains only carriage, newline, and printable
  ASCII characters (` `…`~`).
- The signature matches.
- It is recommended that carriage returns are stripped from the message.
  This will not modify the validity of the signature but will increase
  the delta compression ability of `git`, as the list of hashes in both
  files will be identical.

As the PGP Timestamper uses a PGP 2.x-compatible key and software,
signature verification needs to be done by PGP 2.x or
[GnuPG 1.4](https://www.gnupg.org/download/) needs to be used with the
`---pgp2` option.

## Obtaining `igitt` Timestamps

In theory, both tag or branch timestamps might be applicable. However,
branch timestamps are recommended as follows:

- For each `igitt` timestamping server nicknamed NICK, a branch called
  `NICK-timestamps` is created and used.
- A branch timestamp is obtained in that branch.

