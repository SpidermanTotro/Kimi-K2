# Kimi K2 - Contributing Guide

Thank you for your interest in contributing to Kimi K2!

## Ways to Contribute

- 🐛 **Report Bugs**: Open an issue with reproduction steps
- ✨ **Suggest Features**: Propose new features or improvements
- 📝 **Improve Documentation**: Help us improve our docs
- 🔌 **Create Plugins**: Develop plugins for the community
- 🧪 **Add Benchmarks**: Contribute new evaluation datasets
- 💻 **Submit Code**: Fix bugs or implement features

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Kimi-K2.git
cd Kimi-K2

# Install dependencies
pip install -r requirements.txt
pip install -r benchmarks/requirements.txt

# Run setup wizard
python community/wizards/setup_wizard.py
```

## Code Guidelines

- Follow PEP 8 style guidelines for Python code
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

## Plugin Development

See [plugins/templates/DEVELOPMENT.md](plugins/templates/DEVELOPMENT.md) for detailed plugin development guidelines.

Use the plugin submission template: [community/templates/PLUGIN_SUBMISSION.md](community/templates/PLUGIN_SUBMISSION.md)

## Code Review Process

1. Submit your PR with a clear description
2. Fill out the PR template completely
3. Address reviewer feedback
4. Ensure CI checks pass
5. Wait for approval from maintainers

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others in the community
- Follow our Code of Conduct

## Questions?

- 💬 Join our [Discord](https://discord.gg/TYU2fdJykW)
- 📧 Email [support@moonshot.cn](mailto:support@moonshot.cn)
- 📚 Check the [documentation](https://moonshotai.github.io/Kimi-K2/)

Thank you for contributing to Kimi K2!
