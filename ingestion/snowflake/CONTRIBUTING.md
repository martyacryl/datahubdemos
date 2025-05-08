# Contributing to DataHub-Snowflake Integration

We welcome contributions to this repository! This document provides guidelines and instructions for contributing.

## Types of Contributions

Here are some ways you can contribute:

- **Bug fixes**: If you find a bug in any script or configuration, feel free to submit a fix
- **Documentation improvements**: Enhance existing documentation or add new examples
- **Feature additions**: Add new features to scripts or create new integration patterns
- **Performance optimizations**: Improve the efficiency of ingestion pipelines
- **Example configurations**: Share your real-world Snowflake ingestion configurations (with sensitive info removed)

## Development Environment Setup

1. **Prerequisites**:
   - Python 3.7+
   - pip
   - Docker (for container-based development)
   - Git

2. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/datahub-snowflake-demo.git
   cd datahub-snowflake-demo
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a branch for your work**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the code style of the project
   - Add or update tests as necessary
   - Update documentation to reflect your changes

3. **Test your changes**:
   - Test with a local DataHub instance
   - If adding a new script, test with sample data
   - Ensure all existing tests pass

4. **Commit your changes**:
   ```bash
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a pull request**:
   - Go to the repository on GitHub
   - Click "New pull request"
   - Select your branch and submit the PR with a clear description

## Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Include docstrings for functions and classes
- Add comments for complex logic
- Keep functions focused on a single responsibility
- Write automated tests for new functionality

## Documentation Guidelines

- Update README.md if you change functionality
- Document any new configuration options
- Add examples for new features
- Use markdown for documentation
- Keep documentation up-to-date with code changes

## Pull Request Process

1. Ensure all tests pass and your code follows the style guidelines
2. Update documentation to reflect your changes
3. If your PR adds new features, include example usage
4. A maintainer will review your PR and may request changes
5. Once approved, a maintainer will merge your PR

## License

By contributing to this repository, you agree that your contributions will be licensed under the same license as the project (Apache License 2.0).

## Questions?

If you have questions about contributing, please open an issue or reach out to the maintainers.

Thank you for contributing to make DataHub-Snowflake integration better for everyone!