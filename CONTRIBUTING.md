# Contributing to Landscape MCP Server

Thank you for your interest in contributing to the Landscape MCP Server! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, Landscape version)
- Relevant logs or error messages

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- A clear description of the feature
- Use cases and benefits
- Any relevant examples from other projects

### Code Contributions

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/landscape-mcp.git
   cd landscape-mcp
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   # Install UV if needed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment
   uv venv
   source .venv/bin/activate

   # Install dependencies
   uv pip install -r requirements.txt
   uv pip install -r requirements-http.txt  # If working on HTTP server
   ```

4. **Make Your Changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

5. **Test Your Changes**
   ```bash
   # Test the MCP server
   python landscape_mcp.py

   # Test the HTTP server
   python mcp_http.py
   ./test-http.sh http://localhost:8000
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add descriptive commit message"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for test additions or changes

7. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Add docstrings to functions and classes
- Use type hints where appropriate

## Testing

Before submitting a pull request:
- Test with your own Landscape instance
- Verify all MCP tools work correctly
- Test both stdio and HTTP versions if applicable
- Check that error handling works properly

## Security

- **Never commit API credentials** - use environment variables or placeholder values
- Report security vulnerabilities privately via GitHub Security Advisories
- Follow secure coding practices

## Questions?

If you have questions about contributing, feel free to:
- Open a GitHub issue with the "question" label
- Start a discussion in GitHub Discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make this project better for everyone in the community!
