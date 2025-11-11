# Contributing to Kimi K2

Thank you for your interest in contributing to Kimi K2! This document provides guidelines for contributing to THE FORGE AI project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Use the issue template
3. Provide detailed information
4. Include reproduction steps

### Suggesting Features

1. Search for existing feature requests
2. Use the feature request template
3. Explain the use case
4. Provide examples

### Code Contributions

#### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Kimi-K2.git
   cd Kimi-K2
   ```

3. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Workflow

1. Make your changes
2. Write tests
3. Run tests locally:
   ```bash
   # Run benchmarks
   python benchmarks/run_benchmarks.py
   
   # Validate data
   python forge/data/validators/data_validator.py --input test_data.jsonl
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a pull request

#### Commit Message Guidelines

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

Examples:
```
feat: add AIME benchmark runner
fix: correct data validation logic
docs: update deployment guide
```

### Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Request review from maintainers
5. Address review feedback
6. Squash commits if requested

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Testing

- Write unit tests for new code
- Maintain test coverage above 80%
- Test edge cases
- Use meaningful test names

### Documentation

- Update README files
- Add inline comments for complex logic
- Provide usage examples
- Keep documentation up-to-date

## Project Structure

```
Kimi-K2/
├── benchmarks/       # Benchmark testing framework
├── forge/           # Development infrastructure
│   ├── data/        # Data processing
│   ├── training/    # Fine-tuning scripts
│   ├── deployment/  # Deployment configs
│   └── community/   # Community resources
├── docs/           # Documentation
└── README.md       # Main README
```

## Community

- **Discord**: [Join our server](https://discord.gg/TYU2fdJykW)
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs and request features

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md
- Release notes
- Community highlights

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Modified MIT License).

## Questions?

Feel free to ask questions in:
- GitHub Discussions
- Discord community
- Issue comments

Thank you for contributing to Kimi K2! 🚀
