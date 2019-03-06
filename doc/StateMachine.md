# Server-side commit state machine operation

This documents the state machine operation triggered at the
selected commit time. This is the low-level documentation. For a
higher-level overview, see [ServerOperation.md](./ServerOperation.md).

This is implemented in [commit.py](../server/igitt/commit.py).

## 0. At process start

Ensure the existence of a `master` branch and a file `pubkey.asc`
in the repository.

## 1. Rotate log file

At the start of the minute determined by `commit-at`, the following
operations are performed:

- If a file `hashes.log` exists, the previous commit cycle did not
  complete (e.g., because receiving email from the PGP Timestamper timed
  out): Then create a intermediate (self-signed) commit, so that no
  commit hash is lost (see sections 4ff.) and then continue here.
- If a file `hashes.work` exists in the repository, it is renamed to
  `hashes.log` such that any upcoming requests will start a new
  `hashes.work` for the next cycle.
- A short wait (0.1 s) is introduced to ensure that the file contents have
  settled (i.e., parallel log operations have completed)

## 2. Try to send mail to the PGP Timestamper, if enabled

If a file `hashes.work` exists, the `email-address` configuration 
variable exists (i.e., mail should be sent to the PGP Timestamper) and 
*no* file `hashes.mail` exists, the following operations are performed:

- Delete `hashes.asc`.
- Copy `hashes.log` to `hashes.mail`.
- Append a blank line to `hashes.mail`.
- Also append a line `Parent: <commit id>` (with the current commit ID
  of the master branch, i.e., parent of the commit we are just creating)
- Send email to the PGP Timestamper.

## 3. Receive email

If a file `hashes.mail` exists, try to receive a new stamped mail message
for up to 15 minutes.

- If a new message is here, verify that it actually is the message
  stamping `hashes.mail`. (See [ServerOperation.md](./ServerOperation.md).)
- Write that mail down as `hashes.asc`.
- Add it to the repository (`git add`).
- Delete `hashes.mail`.

## 4. Commit to `git`

If `hashes.log` exists and
- `email-address` is not defined (no PGP Timestamping should occur),
- `hashes.asc` exists (PGP Timestamping was successful),
- `hashes.mail` does not exist at all, or
- 15 minutes have passed since `hashes.mail` was created,
then perform the following operations:

- Add `hashes.log` to the repository (`git add`), potentially joining
  `hashes.asc` there.
- Create a new signed commit

## 5. Obtain upstream `igitt` timestamps

After completion of section 4 above, perform the following operations:

- Obtain the upstream `igitt` timestamps.

## 6. Publish the repository contents

After completion of section 5 above, perform the following operations:

- Push the repository to a public repository. You will likely want to
  include the `master` and all timestamping branches in this push.

## Notes

If for some reason steps 2, 3, 5 or 6 fail, they will be included in 
the next cycle. Step 6 will push the previous entries while steps 2/3 
and 5 will confirm the previous operations thanks to the `git` hash 
chain.

The security implications of not having *any* independent 
certifications in a given cycle will be that a cheating `igitt` server 
will have two periods to backdate timestamps.

However, we assume that the timestampers are *in principle* trustworthy 
and the mutual certifications are only needed to allow public audit of 
that trustworthiness. Therefore, the larger window is not an issue for
most applications.
