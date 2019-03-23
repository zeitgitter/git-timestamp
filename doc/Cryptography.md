# Keys and cryptographic primitives

## Key generation

### General cryptographic remarks

We have several recommendations about minimum key length around:
- [NIST Special Publication 800-175B: Guideline for Using Cryptographic Standards in the Federal Government: Cryptographic Mechanisms](https://csrc.nist.gov/publications/detail/sp/800-175b/final)
- [BSI TR-02102-1: "Cryptographic Mechanisms: Recommendations and Key Lengths" Version: 2019-1](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Publications/TechGuidelines/TG02102/BSI-TR-02102-1.pdf)
- [Wikipedia on Asymmetric Algorithms Key Lengths](https://en.wikipedia.org/wiki/Key_size#Asymmetric_algorithm_key_lengths)

The high-level summary is that for any key that should be useful for many years,
- choose a cryptographic algorithm
  * that has been under scrutiny from cryptograpic experts, and
  * is not yet weak or broken (and neither is this foreseeable); and
- use the longest practical key size of a particular algorithm.

### Algorithm diversity

Generally, diversity can be good or bad when it comes to security:

- More options give more options to potenial attackers, who just
  have to find a single weakness
- More options allow for more interoperability

In the case of a timestamping network, we have the property that
if just one of the nodes is trustworthy, the entire network is
almost as trustworthy, because the timestamp of that trustworthy
entity will limit the backdating ability of all others.

### Algorithm selection

GnuPG currently (2019) supports the following algorithm and has supported all
of them for a few years now:

- [RSA](https://en.wikipedia.org/wiki/Rivest-Shamir-Adleman) up to 4096 bits
  (long signatures)
- [DSA](https://en.wikipedia.org/wiki/Digital_Signature_Algorithm) up to 3072
  bits (short signatures)
- [ECC](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography) keys (short
  signatures, fast operation; bit length in name unless specified otherwise):
  * [Curve25519](https://en.wikipedia.org/wiki/Curve25519) (256 bits)
  * [NIST](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf) P-256, P-384, P-521 (sic!)
  * [Brainpool](https://tools.ietf.org/html/rfc5639) P-256, P-384, P-512
  * [secp256k1](https://en.bitcoin.it/wiki/Secp256k1) (256 bits)

Please do chose from the multitude of algorithms, a wide variety
helps here. A signature-only algorithm is perfect for our needs.

### Key length selection

For key length, this implies that the longest key length should be used which
is supported by the server and its expected clients. One criteria for public
timestamping servers could be to support a cipher length which has been
supported by [GnuPG](https://www.gnupg.org) for a few years already.

## Cryptographic primitives

The signing key is only part of the equation. Two other parts are worthwhile mentioning:
- SHA-1 in `git`, and
- MD5/IDEA for the [PGP Timestamper](http://www.itconsult.co.uk/stamper.htm)

## Key creation

To create a timestamping key out of the full list of algorithms, use

```sh
gpg --expert --full-key-gen
```

and follow the options.

### SHA-1 in `git`

SHA-1 is considered broken by the [SHAttered attack](https://shattered.io/).
SHAttered is able to create a hash collision between a pair of carefully chosen
plaintexts. We do not believe this is of a practical concern for the
timestamping application:

- SHAttered requires a careful preparation of a block to be susceptible to the
  attack. I.e., a collision needs to be carefully prepared and cannot be
  randomly inserted later.
- `git` since v2.13.0 uses the "Hardened SHA-1" function, which is supposed to
  make it impossible to sneak contents into a repository which can later be
  replaced using the SHAttered attack. ("Hardened SHA-1" [detects attempts to
  navigate the internal SHA-1 state into the required state to perform the
  SHAttered attack](https://github.com/git/git/commit/28dc98e343ca4eb370a29ceec4c19beac9b5c01e)
  and will create a different SHA-1 hash for these. This hash is presumed to
  be immune against SHAttered.)

So, as a result, it seems that preparing for a collision is thwarted by `git`
today. Even if it were possible to work around this, modifying a previous block
(a necessary operation for successful backdating of a timestamp) would require
large amounts of careful preparation and could probably only be done for a
carefully-chosen replacement. I.e., "let me just thrown these few million
dollars of computation time into creating a timestamp now which says it was
created last year" is not something we have to worry about.

Nevertheless, we will follow the [upcoming transition of `git` to SHA-256
carefully](https://github.com/git/git/blob/master/Documentation/technical/hash-function-transition.txt)
and take appropriate means in a timely fashion.

### PGP Timestamper's PGP 2 key

The [PGP Timestamper](http://www.itconsult.co.uk/stamper.htm) uses a PGP key
created in 1995, which is compatible to the MIT PGP 2.x version, using MD5
hashes and IDEA symmetric encryption algorithm.

This is no longer state of the art, but backdating without careful preparation,
a lot of money and even more luck is extremely hard, to say the least.  Even
given that MD5 is considered broken, hash collisions are extremely hard to
create for an existing old hash.

Therefore, the PGP Timestamper is still a source of assurance, but should not
be used as the only means of cross-assurance. Instead, publication and/or
`igitt` cross-timestamping should be used as an additional means of assurance.

## Some signing speeds

Here are some signing speeds showing the average run time over 10 *sequential*
runs of `gpg --sign` of a 40-byte input file. For each test, the longest keys
offered by `gpg --expert --full-gen-key` were used. Shorter keys will be
faster, `igitt` will also take advantage of multiple cores.

| Processor (single run)           | dsa3072 | rsa4096 | ed25519 | nistp521 | bpP512r1 | secp256k1 |
| ---------------------------------| -------:| -------:| -------:| --------:| --------:| ---------:|
| AMD EPYC 7351P (2.4 GHz)         |   23 ms |   59 ms |   38 ms |    49 ms |    30 ms |     13 ms |
| Intel Core i7-6600U (2.6 GHz)	   |   19 ms |   30 ms |   21 ms |    27 ms |    19 ms |      9 ms |
| BCM2835 (ARM, Raspberry Pi Zero) |  398 ms | 1192 ms |  575 ms |   901 ms |   785 ms |    219 ms |
| BCM2835 (ARM, Raspberry Pi 3 B)  |  153 ms |  632 ms |  237 ms |   390 ms |   355 ms |     88 ms |

A Raspberry Pi Zero (single-core) may thus serve around 0.8…5 signatures per
second at the given key lengths, while the Raspberry Pi 3 achieves 1.5…11
signatures per core, the AMD EPYC 16…800 per core, and the i7-6600 100…300
signatures per core.

(Please note that our *Raspberry Pi 3 Model B v1.2 Revision a02082* we used for
this test reports its CPU as an ARMv7 BCM2835, even though the spec says it
should be an ARMv8 BCM2837.)

One would expect that the AMD processor with its 16 cores could run 16 `gpg`
processes in parallel and the Intel processor (with 2 real and 4 virtual cores)
could run 2…4 `gpg` processes in parallel. However, GnuPG 2.x uses a single,
single-threaded `gpg-agent` for all secret key operations. Therefore, running
multiple GnuPG processes does not result in higher parallelism; i.e., running
10 processes "in parallel" will still require roughly 10x as long as running a
single `gpg` process.

However, I noticed one exception: Running 10 parallel dsa3072 operations on the
AMD only requires around 80 ms, so it gains about a factor of 3. I do not have
an explanation for this yet.
