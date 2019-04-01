# Installation

## Basic system

* Create a domain and an email address for the timestamper
* Install the necessary third-party software
```sh
apt install git python3-pygit2 python3-gnupg python3-configargparse
apt install python3-nose # For tests only
```
* Install `igitt` client and server:
```sh
cd .. && make install-both
```
* As user `igitt`, create an OpenPGP key using `sudo -H -u igitt gpg --expert --full-gen-key`:
  - All it ever needs to do is signing; encryption is not needed.
  - Choose a long key, so it will last many years.
  - See […/doc/Cryptography.md](../doc/Cryptography.md) for more information.
  - Make sure you minimize the chances for the key to ever leak. **Revocation
    of the key should be avoided,** as this creates an unefined state for the
    key for its entire lifetime, not just only after the revocation. Prefer
    to destroy the key before it falls into wrong hands.
* Chose a unique time to commit your changes and cross-timestamp
  (parameter `commit-at`).
* Configure the remaining parameters, including whether to have upstream
  cross-timestamping.
* Set up a front-end webserver doing HTTPS and proxying.
* Update the contact parameters in `/var/igitt/web`.
* Test it thoroughly.
* If your server should be public, create a pull request with your addition to
  `…/doc/ServerList.md`.

## Additionally, for use with the PGP Digital Timestamper

* Install GnuPG 1.x (for downward compatibility with the old PGP 2.x key)
```sh
apt install gnupg1
```
* Create a mail account and enter its parameters into the configuration file.  
  You may want to use a non-public email address for this; it will not show
  up anywhere and only needs to be used when contacting stamper.
