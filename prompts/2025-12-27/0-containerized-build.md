# Containerized Build

- Status: Active / High-Coverage
- Total Coverage: 91% (Targeting 100%)
- Environment: Python 3.13-slim (Dockerized)
- CI Status: Green (GitHub Actions executing via Docker)

## 1. The Containerization Strategy

To resolve local environment "drift" (specifically Python 3.14 C++
compatibility issues on Mac M3 Max), the project moved to a Docker-first
architecture.

- Base Image: python:3.13-slim to ensure stable DDS bindings.
- Build Optimization: Layer caching for system dependencies (build-essential)
  and Python requirements (pyproject.toml).
- Unified Entrypoint: A master bridge-cli.sh script routes commands (generate,
  evaluate, test, pipeline) to the internal Python logic.

## 2. CLI and Documentation as Code

The project now uses the Python doctest library to verify the CLI interface itself.

- Help Text Validation: Doctests in main() verify that --help returns the
  expected PBN 2.1 documentation and exits with code 0.
- Strict Exit Handling: Using try...except SystemExit ensures that the audit
  trail captures return codes accurately without crashing the test runner.
- Blankline Management: Correct use of <BLANKLINE> in docstrings to handle
  argparse formatting.

## 3. The 90%+ Coverage Ratchet

Maintaining high coverage is a core project principle to ensure the stability
of the C++ bridge engine.

- Current Audit: generate-hands.py stands at 96%, while evaluate-hands.py is
  at 86%.
- Gap Analysis: Remaining coverage gaps are located in primary execution loops
  and if __name__ == "__main__": blocks.
- CI Enforcement: The docker-test.sh script acts as the final gatekeeper in
  the GitHub Actions pipeline.

### Artifacts Created

- `Dockerfile`: The source of truth for the build environment.
- `bridge-cli.sh`: The master orchestrator for local and containerized runs.
- `docker-test.sh`: The coverage-enforcing audit script.

> **NOTE**: The script will become `bridge.sh` and not `bridge-cli.sh`.
