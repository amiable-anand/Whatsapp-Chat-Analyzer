# Contributing to WhatsInsight 🤝

We welcome contributions to WhatsInsight! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/WhatsInsight.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Set up your development environment (see README.md)

## 🔧 Development Setup

1. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Tests** (when available)
```bash
python -m pytest
```

## 📝 Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions focused and concise
- Use type hints where applicable

## 🐛 Bug Reports

When filing a bug report, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Sample chat file (anonymized) if relevant

## ✨ Feature Requests

For feature requests, please:
- Check existing issues first
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity

## 🔄 Pull Request Process

1. **Update Documentation**: Update README.md if needed
2. **Test Your Changes**: Ensure your code works as expected
3. **Follow Commit Guidelines**: Use clear, descriptive commit messages
4. **Update CHANGELOG**: Add your changes to the changelog
5. **Request Review**: Submit your PR for review

### Commit Message Guidelines
```
feat: add new sentiment analysis feature
fix: resolve emoji chart rendering issue
docs: update README with new installation steps
refactor: improve code organization in analyzers
```

## 🏗️ Project Structure

```
WhatsInsight/
├── analyzers/          # Analysis modules
├── core/               # Core functionality
├── visualizers/        # Chart generation
├── templates/          # HTML templates
├── static/            # CSS/JS/images
├── app.py             # Main application
└── requirements.txt   # Dependencies
```

## 🧪 Testing

- Write tests for new features
- Ensure existing tests pass
- Test with different chat formats
- Verify responsive design on mobile

## 📚 Documentation

- Update docstrings for new functions
- Add inline comments for complex logic
- Update README.md for new features
- Include examples where helpful

## 🎯 Areas for Contribution

- **New Analysis Features**: Add new types of chat analysis
- **Visualization Improvements**: Enhanced charts and graphs
- **Performance Optimization**: Speed up processing
- **UI/UX Enhancements**: Improve user interface
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve guides and examples

## 🤔 Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar problems

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WhatsInsight! 🚀✨
