# Timestamping: Why and how

Being able to provide evidence that you had some piece of information at a
given time is important in many aspects of personal and corporate life. It can
be used to

- show that you had some idea already at a given time,
- that you already had a piece of code, or
- that you had a document at a given time.

Timestamping does not assure *authorship* of the idea, code, or document. It
only provides evidence to the *existence* at a given point in time. Depending
on the context, authorship might be implied, at least weakly.

# Isn't that what Blockchain is for?

Timestamping was used way before Blockchain was even conceived of:

- Libraries,
- notaries public
  ([going back to Roman times](https://en.wikipedia.org/wiki/Notary_public#History)),
- registered mail
  ([dating back to 1556](https://en.wikipedia.org/wiki/Registered_mail#History)),
- commitment through clandestine newspaper ads,
- [hash chains](https://en.wikipedia.org/wiki/Hash_chain) (latest 1981),
- [distributed consensus](https://en.wikipedia.org/wiki/Byzantine_fault#Early_solutions)
  (before 1982),
- [cryptographic commitment schemes](https://en.wikipedia.org/wiki/Commitment_scheme)
  (since 1988),
- [digital timestamping](https://link.springer.com/chapter/10.1007/3-540-38424-3_32)
  and its problems and solutions was first documented in a scientific
  publication in 1990,
- [PGP Timestamping service](http://www.itconsult.co.uk/stamper.htm)
  (established 1995), or
- [LOCKSS](https://en.wikipedia.org/wiki/LOCKSS) (since 2000),
- `git` and other
  [DVCS](https://en.wikipedia.org/wiki/Distributed_version_control) with
  replicated repositories
  ([since 2001](https://en.wikipedia.org/wiki/GNU_arch#History_and_maintainership))

are ways of providing public and/or agreed-upon evidence that something has
happened or was known at or before a particular time.

Assuming that there is little interest in *wide-spread* foul-play or given
enough independent verifiers, timestamps can be provided much more easily (and
more energy-efficient) than with Blockchain.

# Why not Blockchain Timestamping?

Existing Blockchain timestamping systems such as
[OriginStamp](https://originstamp.org) do not give an immediate feedback or
proof to the requestor. Instead,

- they first accumulate several requests (the default is for 24 hours)
- and only then submit them to the Blockchain,
- where it may further take an hour or more before before it is immutably
  accepted to the Bitcoin Blockchain, and
- then you as the requestor still do not have anything and will need to
  look through several different data structures to obtain a real proof
  (see [OriginStamp FAQ item "What if your service doesn't exist in 20
  years?"](https://originstamp.org); sorry, but direct linking to that entry
  does not work. You have to scroll down and open the FAQ item yourself).

On the other hand, `zeitgitter` timestamping
- returns an *immediate* timestamped signature as a proof, and
- only requires the other operations to show that the timestamper
  itself is not misbehaving.

As a further benefit, a network of independent timestampers

- is much more energy efficient: An `zeitgitter` timestamper on a tiny computer
  such as a Raspberry Pi may consume less than
  [one Watt](https://www.pidramble.com/wiki/benchmarks/power-consumption),
  while the Blockchain used
  [a huge amount of power](https://www.economist.com/the-economist-explains/2018/07/09/why-bitcoin-uses-so-much-energy),
  [more power as the whole country of Switzerland](https://www.tagesanzeiger.ch/digital/bitcoinproduktion-verbraucht-mehr-strom-als-die-ganze-schweiz/story/10669793).
  (BTW: One
  [small data center in Switzerland](https://en.wikipedia.org/wiki/Society_for_Worldwide_Interbank_Financial_Telecommunication#Operations_centers)
  processes a copy of all global interbank transactions at only a tiny fraction
  of all the Swiss power consumption and therefore the Blockchain power
  consumption.)
- is much more resilient: In a network of timestampers timestamping each other,
  it is enough to have *just a single* trustworthy timestamper. This already
  limits the window of wrongdoing for any cheating timestamper to around a day
  (i.e., no timestamper may backdate timestamps by more than this timespan).
  On the other hand, controlling 51% of computing power of a Blockchain allows
  complete control over the entire blockchain (and already at 33%, some cheating
  may occur).

# The PGP Timestamper

An example is the already-mentiond *PGP Timestamping service*, which provides
users with the ability to timestamp a document or a hash thereof, by having an
independent party create a
[OpenPGP](https://en.wikipedia.org/wiki/Pretty_Good_Privacy#OpenPGP)-signed and
dated message, each of them with a unique and consecutive serial number.

To ensure trustworthyness and provide full transparency, daily digests of the
hashes and signatures are then also (a) archived and (b) immediately posted to
anyone wishing to be able to withness and reproduce the stamping process.

A disadvantage of the PGP Timestamper is its archaic interface and the log
delays (several minutes). Also, the signatures are hard to verify by
non-experts.

# `zeitgitter` goals

`zeitgitter` is inspired by the PGP Timestamper, but trying to as simple to use as
possible in a `git` context.

The goal of `zeitgitter` is to provide as many independent timestamping services as
possible, so a user (or organization) can freely select a subset fulfulling
their needs.

To establish trust in the service, the source code is made available under an
open source license.

# `zeitgitter` operation

`zeitgitter` listens on an HTTPS port and awaits `POST` requests for signing a tag
or a branch commit. It then returns the appropriate information, ready for the
client to integrate it into its `git` repository, from where it then can be

- verified using `git tag -v <tagname>` or `git verify-commit <commit>`, and/or
- published to other repositories.

At the same time, the timestamping server maintains a log of all commit hashes
signed, in a `git` repository itself.

As a result,
1. the requester of a timestamp will get immediate confirmation
   (a timestamping signature on a tag or branch).
2. Later, the timestamper then either cross-timestamps its repository and/or
   publishes it.
3. This allows third parties to inspect the timestamping server's operation
   and therefore strictly limits the timestamping server's ability to backdate
   anything beyond the cross-timestamping/publication interval.

This allows a compact, energy-efficient basis for many notarization services.

# Name

The [name `zeitgitter`](https://www.duden.de/rechtschreibung/zeitgitter) tries to keep
in line with the
[slang naming philosophy behind `git`](https://github.com/git/git/blob/e83c5163316f89bfbde7d9ab23ca2e25604af290/README)).

# Usage

This software is free software; so you may use it in any way you see 
fit, in accordance to the [AGPL v3.0 license](LICENSE.md).

Timestamping has a need to be as transparent as possible. Therefore, 
you may want to make information about your timestamping service, 
including the running code and its settings, available publicly anyway. 
AGPL was chosen to reflect this spirit. Please contact me if you 
require other licensing terms.

It is desirable that as many people and organisations as possible do 
provide timestamping services. So a user may choose a subset of them 
which are mutually independent and generally trustworthy.

[Installation and typical usage of the timestamping client is documented in
`doc/Install.md`](doc/Install.md).

# Naming

The `zeitgitter` name can refer to
- the underlying protocol ("`zeitgitter` protocol"),
- this software or other servers implementing the protocol
  ("`zeitgitter` server"), or
- the entire network of servers ("`zeitgitter` network", "`zeitgitter` system").

It *should not* refer to an individual service, especially not a
public service. When chosing a name for your service, please try to come
up with a unique service name. The full service name has to be unique,
obviously. But also, the first part of the name (before the first dot
in the domain name) should be unique. [A list of currently know public
servers is maintained as `ServerList.md` here.](./ServerList.md)

# Client plausibility tests

The client should perform the following tests on objects returned from this service:

* For tag-based verifications
  - Object ID, tag type, tag name, tagger name and email matches the information submitted
  - Timestamp is between the time the request started and the time the request finished,
    with a fuzz of `f` seconds (recommended: 30 s)
  - The tag message is at most 1000 ASCII chars long (printable + carriage return + newline)
  - The PGP signature is at most 2000 ASCII chars long (base64 + space + equal sign + carriage return + newline)
  - The PGP signature verifies OK

