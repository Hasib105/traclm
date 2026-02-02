# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure with `src/` layout
- Modern `uv` package manager support
- FastAPI-based server with Piccolo ORM
- Auto-instrumentation SDK for LangChain
- SQLite and PostgreSQL database support
- Web dashboard for trace visualization
- API key management
- Project organization
- Comprehensive test suite
- Pre-commit hooks configuration
- Ruff linting and formatting

### Changed

- Migrated from setuptools to hatchling build backend
- Updated to modern Python 3.10+ syntax
- Restructured to src-layout for better packaging

## [0.1.0] - 2026-02-02

### Added

- Initial release
- Core tracing functionality
- LangChain callback integration
- Basic web UI
- REST API for traces
