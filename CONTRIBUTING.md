# Contributing to CSV Data Cleaner

Thank you for your interest in contributing to the CSV Data Cleaner by **Dev V Trivedi**! This project aims to make data cleaning accessible and efficient for everyone.

## 🎯 How to Contribute

### 🐛 Reporting Bugs
- Use the [GitHub Issues](https://github.com/Dev-V-Trivedi/data-cleaner/issues) page
- Include a clear description of the bug
- Provide steps to reproduce the issue
- Include relevant error messages and screenshots
- Attach sample CSV files if relevant

### 💡 Suggesting Features
- Open a [Feature Request](https://github.com/Dev-V-Trivedi/data-cleaner/issues/new?template=feature_request.md)
- Describe the feature and its use case
- Explain why it would be valuable to users
- Consider backward compatibilityo Data Cleaner

Thank you for your interest in contributing to Data Cleaner! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### 🐛 Reporting Bugs
- Use the [GitHub Issues](https://github.com/Dev-V-Trivedi/data-cleaner/issues) page
- Include a clear description of the bug
- Provide steps to reproduce the issue
- Include relevant error messages and screenshots

### 💡 Suggesting Features
- Open a [Feature Request](https://github.com/Dev-V-Trivedi/data-cleaner/issues/new?template=feature_request.md)
- Describe the feature and its use case
- Explain why it would be valuable to users

### 🔧 Code Contributions

#### Development Setup
1. **Fork the repository**
   ```bash
   git clone https://github.com/Dev-V-Trivedi/data-cleaner.git
   cd data-cleaner
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Frontend Setup**
   ```bash
   cd frontend-dev
   npm install
   ```

4. **Environment Variables**
   ```bash
   # Backend .env
   DEBUG=True
   CORS_ORIGINS=["http://localhost:5173"]
   
   # Frontend .env
   VITE_API_URL=http://localhost:8000
   ```

#### Running Development Servers
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend-dev
npm run dev
```

#### Code Style Guidelines

**Python (Backend)**
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Add type hints where possible
- Write docstrings for functions and classes

**TypeScript/React (Frontend)**
- Use [Prettier](https://prettier.io/) for formatting
- Follow React best practices
- Use TypeScript for type safety
- Write meaningful component names

#### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend-dev
npm test
```

### 🎨 Areas for Contribution

#### 🔍 Algorithm Improvements
- Enhance column classification accuracy
- Add new column type detection
- Optimize processing performance
- Improve confidence scoring

#### 💻 Frontend Enhancements
- Improve UI/UX design
- Add accessibility features
- Mobile responsiveness
- Interactive data preview

#### 📊 Data Processing
- Support for more file formats (Excel, JSON, XML)
- Advanced data validation
- Batch processing capabilities
- Real-time progress indicators

#### 🧪 Testing & Quality
- Unit tests for classification logic
- Integration tests for API endpoints
- End-to-end UI testing
- Performance benchmarking

#### 📚 Documentation
- API documentation improvements
- User guides and tutorials
- Code examples and demos
- Multi-language support

## 📋 Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new features
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   cd backend && pytest
   cd frontend-dev && npm test
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new column type detection"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Requirements**
   - Clear description of changes
   - Link to related issues
   - Screenshots for UI changes
   - Tests pass successfully

## 🏷️ Commit Message Format

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add Excel file upload support
fix: resolve column detection accuracy issue
docs: update API documentation
style: format code with prettier
```

## 🔒 Security

If you discover a security vulnerability, please:
1. **DO NOT** open a public issue
2. Email us directly at security@datacleaner.com
3. Provide detailed information about the vulnerability
4. Allow time for us to address the issue before disclosure

## 📝 Code of Conduct

### Our Pledge
We are committed to making participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to creating a positive environment include:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Unacceptable Behavior
Examples of unacceptable behavior include:
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## 🛣️ Development Roadmap

### Short Term (Next Release)
- [ ] Excel/XLSX file support
- [ ] Improved error handling
- [ ] Better mobile experience
- [ ] Performance optimizations

### Medium Term (3-6 months)
- [ ] Advanced AI models
- [ ] User authentication
- [ ] Batch processing
- [ ] API rate limiting

### Long Term (6+ months)
- [ ] Machine learning model training
- [ ] Database connectors
- [ ] Enterprise features
- [ ] Multi-language support

## 🎁 Recognition

Contributors will be recognized in several ways:
- Listed in the [Contributors](https://github.com/Dev-V-Trivedi/data-cleaner/graphs/contributors) section
- Mentioned in release notes for significant contributions
- Invited to join our contributor Discord server
- Eligible for contributor swag (stickers, t-shirts)

## 📞 Getting Help

- **Discord**: [Join our community](https://discord.gg/datacleaner)
- **GitHub Discussions**: [Ask questions](https://github.com/Dev-V-Trivedi/data-cleaner/discussions)
- **Email**: contributors@datacleaner.com

## 📄 License

By contributing to Data Cleaner, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Data Cleaner! Your help makes this project better for everyone. 🚀
