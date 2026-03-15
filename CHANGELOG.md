# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-16

### Added
- Complete CLI implementation with `scan`, `duplicates`, and `report` commands.
- Governance policy enforcement in `intelligence` command.
- Perceptual hashing for near-duplicate detection.
- Deep feature embedding extraction using OpenCV.
- Global drift scoring engine.
- Automated test suite with `pytest`.
- Professional `README.md` with architecture diagrams and badges.
- Community documents: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- GitHub Actions CI/CD for automated testing.

### Fixed
- Fixed KeyError in HTML report generation when handling class anomalies.
- Fixed image standard deviation edge cases in scanner for blank images.

## [0.2.0] - 2026-03-13
- Initial development of core modules: `scanner`, `drift`, `intelligence`, `anomaly`.

## [0.1.0] - 2026-03-10
- Project initialization.
