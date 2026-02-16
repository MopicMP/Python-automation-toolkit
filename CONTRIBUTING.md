# Contributing

Thanks for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-tool`
3. Write your code in `tools/` with a docstring and CLI entry point
4. Add an example in `examples/` if applicable
5. Update `requirements.txt` if you add new dependencies
6. Submit a pull request

## Code Style

- Python 3.8+ compatible
- Type hints encouraged
- Every tool file should be runnable standalone: `python tools/my_tool.py`
- Include a module docstring with usage examples
- Use `if __name__ == "__main__":` entry points

## Reporting Issues

Open an issue with:
- What you tried
- What happened
- What you expected
- Your Python version and OS
