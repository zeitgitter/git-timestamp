# Open design issues

* Interoperate with the email-based PGP Digital Timestamper.
* Allow encrypted secret keys, such that the data on disk is useless.  
  This will require a new HTTPS request which can be used to set the
  passphrase to a restarted instance.
* Enable parallel timestamping operations.  
  Work around GnuPG-enforced serialization of secret key operations
  through the `gpg-agent`. E.g.,
  - allow multiple `gpg-agents` to be run and assign them to the started
    GnuPG instances, or
  - rewrite the signing operation from scratch.
  Both approaches are, unfortunately, error-prone.
