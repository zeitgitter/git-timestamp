# `git timestamp` — Git Timestamper for *Zeitgitter*

## Timestamping: Why?

Being able to provide evidence that **you had some piece of information at a
given time** and **it has not changed since** are important in many aspects of
personal, academic, or corporate life.

It can help provide evidence
- that you had some idea already at a given time,
- that you already had a piece of code, or
- that you knew about a document at a given time.

Timestamping does not assure *authorship* of the idea, code, or document. It
only provides evidence to the *existence* at a given point in time. Depending
on the context, authorship might be implied, at least weakly.

## *Zeitgitter* for Timestamping

*Zeitgitter* consists of two components:

1. A timestamping client, `git timestamp`, which can add a timestamp as a digital signature to
   an existing `git` repository. Existing `git` mechanisms can then be used
   to distribute these timestamps (stored in commits or tags) or keep them
   private.
2. A timestamping server, `zeitgitterd`, which supports timestamping `git` repositories and
   stores its history of commits timestamped in a `git` repository as well.
   Anybody can operate such a timestamping server, but using an independent
   timestamper provides strongest evidence, as collusion is less likely.
   - Publication of the timestamps history; as well as
   - getting cross-timestamps of other independent timestampers on your
     timestamp history
   both provide mechanisms to assure that timestamping has not been done
   retroactively ("backstamping").

The timestamping client is called `git timestamp` and allows to issue
timestamped, signed tags or commits.

To simplify deployment, we provide a free timestamping server at
[https://gitta.enotar.ch](https://gitta.enotar.ch). It is able to provide several
million timestamps per day. However, if you or your organization plan to issue
more than a hundred timestamps per day, please consider installing and using
your own timestamping server and have it being cross-timestamped with other
servers.

## Client Usage

### Options

```sh
git-timestamp [-h] [--tag TAG] [--branch BRANCH] [--server SERVER]
              [--gnupg-home GNUPG_HOME]
              [COMMIT]
```

Interface to Zeitgitter, the Independent GIT Timestampers.

Positional arguments:
* **COMMIT**: Which commit to timestamp. Can be set by git config
  'timestamp.commit-branch'; fallback default: 'HEAD'

Optional arguments:
* **-h, --help**: Show this help message and exit. When called as 'git
  timestamp' (space, not dash), use '-h', as '--help' is interpreted by 'git'.
* **--tag TAG**: Create a new timestamped tag named TAG
* **--branch BRANCH**: Create a timestamped commit in branch BRANCH, with
  identical contents as the specified commit. Default name derived from
  servername plus '-timestamps'. Can be set by git config 'timestamp.branch'
* **--server SERVER**: Zeitgitter server to obtain timestamp from. Can be set
  by git config 'timestamp.server'; fallback default:
  'https://gitta.zeitgitter.net'
* **--gnupg-home GNUPG_HOME**: Where to store timestamper public keys. Can be
  set by git config 'timestamp.gnupg-home'

**--tag** takes precedence over **--branch**. When in doubt, use **--tag** for single/rare
timestamping, and **--branch** for reqular timestamping.

Defaults can be stored (per-repository or globally) with `git config`; see each
argument's description.

## General and Client Documentation

- [Timestamping: Why and how?](doc/Timestamping.md)
- [Client installation](doc/Install.md)
- [Protocol description](doc/Protocol.md)
- [List of public *Zeitgitter* servers](doc/ServerList.md)
- [Discussion of the use of (weak) cryptography](doc/Cryptography.md)

