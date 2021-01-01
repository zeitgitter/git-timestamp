# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).


# 1.0.5+ - [Unreleased]
## Added

## Fixed
- Switching to `configargparse` because of `auto_env_var_prefix`
- One test was using system-wide `git-timestamp` instead of local
- Keyid was not always set when needed

## Changed


# 1.0.5 - 2021-01-01
## Added
- `make python-package` now builds a local Python package without attempting to
  upload to PyPI
- Support for timestamping against multiple comma-separated servers in one go
  (only for automatic branch name selection)
- Document `ZEITGITTER_FAKE_TIME`.
- Allow `TIMESTAMP_*` environment variables to set parameters. Parameter
  priority is as follows:
  1. (Highest) Parameters on the command line
  2. Parameters from environment variables (`TIMESTAMP_*`)
  3. Parameters stored in the `git` configuration files
  4. (Lowest) Defaults provided in the program

## Fixed

## Changed
- Intermediate releases are now named `<VERSION>.postN`, where `N` is the number of
  commits since the last tag (using `git describe`). Previously, all were named
  `<VERSION>.post0`


# 1.0.4 - 2020-12-02
## Added

## Fixed
- Allow `--version` and `--help` even outside a git repository

## Changed
- Do not record Zeitgitter key IDs in `~/.gitconfig` if `FORCE_GIT_REPO_CONFIG`
  environment variable is set; use `~/.git/config` instead. This is useful for
  some Docker setups such as `autoblockchainify`.


# 1.0.3 - 2020-09-22
## Added
- Better explanation if not talking to a Zeitgitter server
- Better explanation if `~/.gnupg` or its contents pose permission problems
- Explain automatic timestamping in the README
- Support server aliases. Initialized with all public Zeitgitter servers
- Document freezeing of `pygit2`

## Fixed
- `git timestamp` (i.e., with implicit `--branch` and `--append-branch-name`
  options) with detached HEAD resulted in traceback; now it returns an error

## Changed
- Include Ubuntu 20.04 in documentation
- Defaults to Python 3 now, as [Python 2 has been sunset as of
  2020-01-01](https://www.python.org/doc/sunset-python-2/)
- Updated documentation to match the new/changed options and the dropping of
  Python 2 support (Python 2 still works, but is not supported anymore)


# 1.0.2 - 2020-05-08
## Added

## Fixed

## Changed
- This is only a status update, there are no code changes to the previous release:
- Development status updated to `stable`
- Maintainer address updated


# 1.0.1 - 2020-05-08
## Added
- Quick installation instructions
- 'https://' is now optional for `--server`

## Fixed
- `enable = false` in `git config` is no longer treated as a True value
- Some versions of `pygit2.discover_repository()` raise `KeyError` when
  no `git` repository is found; this is now also caught and handled

## Changed
- "Signature timestamp too far off now" more user-readable


# 1.0.0 - 2019-09-23
## Added
- Can now run selected tests only: `make tests TESTS=tests/20-branch.sh` etc.
- `--append-branch-name` (default: `yes`) appends the branch name on
  timestamp branches for non-`master` branches. I.e., `git timestamp`
  with no additional options will timestamp to `gitta-timestamps` for
  branch `master` and `gitta-timestamps-foobar` for branch `foobar`.
  (Timestamping from different branches to the same timestamp branch
  is not for the faint of heart and has unexpected side effects, including
  exposing private branches and making temporary branches permanent.)

## Fixed
- No longer allow timestamping a timestamp branch head onto itself
  (would cause a merge commit with the same parent twice)

## Changed
- Updated and extended [ServerList.md](./doc/ServerList.md)


# 0.9.7 - 2019-09-01
## Added
- `--quiet` option

## Fixed
- Handle `--server http://localhost:1234`
- Tag and branch name validity checks match `zeitgitterd`'s

## Changed
- `ZEITGITTER_FAKE_TIME` now used for testing
- Support optional boolean arguments: If the option (e.g., `--enable` or
  `--quiet`) is specified without an argument, it defaults to true; if the
  option is not specified, it defaults to false. This allows changing an
  option on the command line which has been specified differently in
  `git config`. Having a `--no-…` counterpart would not allow consistent
  overriding of `git config` options on the command line in both directions.
  The downside: Having such an option last before the positional arguments
  requires explicit specification of `true` to avoid parsing the positional
  argument as the truth value.


# 0.9.6 - 2019-08-14
## Added
- `--version` option
- Support for
  [inclusion in other packages](./README.md#inclusion-in-other-packages)
  by providing default-enabled or default-disabled operation.

## Fixed

## Changed
- Changed client license to MIT
- Use [`pygit2` information for global `.gitconfig` path
  determination](https://github.com/libgit2/pygit2/issues/915#issuecomment-503300141)
- Avoid picking `www` from servername when auto-naming the branch


# 0.9.5 - 2019-06-16
## Added
- Mention Haber/Stornetta in documentation

## Fixed
- No more exception on initial key import
- Detect duplicate timestamp on timestamp branch root as well
- Fixed path for `make install`
- Do not abort if `~/.gitconfig` does not exist when using a timestamper
  for the first time (working around a `pygit2` problem)

## Changed


# 0.9.4 - 2019-05-12
## Added

## Fixed
- Handling of HTTP errors
- Domain names in tests

## Changed


# 0.9.3 - 2019-05-12
## Added
- Default server set to `https://gitta.enotar.ch`; can be changed with
  `git config [--global] timestamper.server …`
- Allow dots in tag/branch names, as long as they are not next to each other
  (i.e., `..` is not allowed)

## Fixed
- Added `setuptools` to dependencies
- Handle HTTP POST redirects adequately

## Changed
- Split into client (git-timestamp) and server (zeitgitterd).
- Persistent information about the timestampers' keys is now stored
  in the global git configuration (key also stored globally; more TOFU-like)
- Updated `enotar.ch` and `igitt.ch` URLs to `zeitgitter.net`


# 0.9.2 - 2019-05-10
## Added
- `make apt` installs dependencies on systems supporting `apt`

### Client
- Distributable via PyPI
- Added Python 2.x compatibility; tested with 2.7
- Automatically derive default timestamp branch name from servername
  (first component not named 'igitt') followd by '-timestamps'.
- Better error message when wrong `gnupg` module has been installed

## Fixed
### Client
- Fetch GnuPG key again if missing from keyring. This fixes unexpected
  behavior when running as sudo vs. natively as root.
- Work around a bug in older GnuPG installs (create `pubring.kbx` if it does
  not yet exist before attempting `scan_keys()`).

## Changed
- Higher-level README

### Client
- Is now implemented as a package (`make install` still installs a flat file
  though, for simplicity)


# 0.9.1 - 2019-04-19
## Added
### Client
- `--server` can be set in git config
- Prevent actual duplicate entries created by `git timestamp --branch`
- Documented that `git timestamp --help` does not work and to use `-h`, as
  `--help` is swallowed by `git` and not forwarded to `git-timestamp`.
- Client system tests (require Internet connectivity)

### Server
- Ability to run multiple GnuPG processes (including gpg-agents) in parallel
- Handle missing `--push-repository` (again)

## Fixed
- Made tests compatible with older GnuPG versions

## Changed
### Client
- Made some error messages more consistent
- `--tag` overrides `--branch`. This allows to store a default branch in
  `git config`, yet timestamp a tag when necessary.


# 0.9.0 - 2019-04-04
Initial public release
