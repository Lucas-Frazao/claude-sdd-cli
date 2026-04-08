# Contributing to Claude SDD CLI

Thank you for your interest in contributing. This project welcomes contributions from everyone.

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](../../issues) to report bugs or request features.
- Search existing issues before opening a new one.
- Include steps to reproduce for bugs, along with your Python version and OS.

### Submitting Changes

1. Fork the repository.
2. Create a feature branch from `main`: `git checkout -b my-feature`.
3. Make your changes.
4. Add or update tests as appropriate.
5. Run the test suite: `pytest`.
6. Run the no-code validator against any new templates: `sdd check-no-code`.
7. Commit with a clear message describing the change.
8. Open a Pull Request against `main`.

### Development Setup

```
git clone https://github.com/<your-fork>/claude-sdd-cli.git
cd claude-sdd-cli
pip install -e ".[dev]"
pytest
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for more detail.

### What Makes a Good Contribution

- Bug fixes with tests.
- New validator patterns for the no-code detector.
- Improved templates that make planning artifacts clearer.
- Documentation improvements.
- New CLI commands that fit the spec-first, Claude SDD philosophy.

### What This Project Will Not Accept

- Commands or features that generate executable code.
- AI integrations that bypass the constitution.
- Changes that weaken the no-code enforcement boundary.

These are foundational principles, not preferences.

## Code Style

- Python 3.10+.
- Use type hints where practical.
- Follow existing patterns in the codebase.
- Keep functions focused and well-named.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
