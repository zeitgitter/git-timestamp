# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## 0.9.0+ - [Unreleased]
### Added
- `--server` can be set in git config (client)
- Prevent actual duplicate entries created by `git timestamp --branch` (client)
- Documented that `git timestamp --help` does not work and to use `-h`, as
  `--help` is swallowed by `git` and not forwarded to `git-timestamp`.

### Fixed
- Made tests compatible to older GnuPG versions

### Changed
- Made some error messages more consistent (client)

## 0.9.0 - 2019-04-04
Initial public release
