# Contributing to FinSight AI

First off, thank you for considering contributing to FinSight AI! It's people like you that make open-source a vibrant and powerful community.

## How to Contribute

### 1. Reporting Bugs
- Ensure the bug was not already reported by searching on GitHub under Issues.
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### 2. Suggesting Enhancements
- Open a new issue with the `enhancement` label.
- Provide a clear and detailed explanation of the feature.
- Explain why this enhancement would be useful to most users.

### 3. Pull Requests
- Fork the repository and create your branch from `main`.
- If you've added code that should be tested, add tests.
- Ensure the test suite passes using our Evaluation Framework.
- Make sure your code adheres to our SOLID design principles and does not introduce frontend dependencies (this is a backend-first project).
- Issue that pull request!

## Development Setup

1. **Clone your fork**: `git clone https://github.com/YOUR_USERNAME/FinSight-AI.git`
2. **Setup virtual environment**: `python -m venv venv`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Environment variables**: Ensure you have a `.env` file configured with your `MISTRAL_API_KEY` and PostgreSQL connection strings (see `.env.example`).
5. **Database Setup**: Ensure PostgreSQL is running locally and you have created a database named `finsight_db`.
6. **Run tests**: Execute `pytest backend/tests/` to run all E2E and regression tests.
## Coding Standards
- **Backend First**: Do not commit React, Vue, or Streamlit dashboards. Use pure HTML/CSS generation or API responses.
- **Type Hinting**: All functions must include Python type hints.
- **Docstrings**: Use clear, concise docstrings for all classes and major functions.

## Code of Conduct
By participating in this project, you are expected to uphold our Code of Conduct (respectful collaboration, zero tolerance for harassment).

Thank you for building with us!
