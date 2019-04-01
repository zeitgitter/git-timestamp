# List of public `igitt` servers

## Access

| Nickname    | URL                          | Notes                   |
| ----------- | ---------------------------- | ----------------------- |
| Gitta       | https://gitta.enotar.ch/     | public                  |
| Diversity   | https://diversity.enotar.ch/ | cross-timestamping only |

Diversity was chosen to use a slow timestamping mechanism, i.e. one which
timestampers are unlikely to use. This is used to achieve diversity in the
cryptographic algorithms used. Timestamping is one of the few applications
of cryptography where [offering different algorithms in parallel actually
increases robustness](./Cryptography.md#algorithm-diversity).

## Maintainer

| Nickname    | Country | Maintainer                      |
| ----------- | ------- | ------------------------------- |
| Gitta       | CH      | Andres Obrero, Marcel Waldvogel |
| Diversity   | CH      | Marcel Waldvogel                |

"Maintainer" includes everyone with access to the private key.

## Technical parameters

| Nickname    | Algorithm | Key ID           | Interval | Offset | Timestamped by |
| ----------- | --------- | ---------------- | --------:| ------:| -------------- |
| Gitta       | dsa3072   | 8A0B0941E7C49D65 |       1h |  23:37 | Diversity      |
| Diversity   | rsa4096   | 453E515FCB1593CB |       1h |  46:19 | Gitta          |

How to read this: Gitta commits, obtains a cross-timestamp from Diversity, and
publishes its log every hour, 23 minutes after the hour.

## Special nicknames

The special nickname `stamper` is used to refer to the [PGP Digital
Timestamping Service](http://www.itconsult.co.uk/stamper.htm),
established in 1995.

`originstamp` is reserved for [OriginStamp](https://originstamp.org).

## Chosing a good commit time for your own server

To chose a good commit time for your own server, you may take the largest
interval between any two timestampers and divide it into two uneven sections
(i.e., divide it roughly according to the [Golden
ratio](https://en.wikipedia.org/wiki/Golden_ratio). Try to avoid chosing
the full hour, as some automated processes may already cluster there.
