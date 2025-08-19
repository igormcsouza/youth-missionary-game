# Testing Documentation

## Overview

This project now includes a comprehensive testing pipeline with pytest and coverage reporting.

## Test Structure

### Core Test Files

- `tests/test_database.py` - Database models and repository testing (92% coverage)
- `tests/test_utils.py` - Utility function testing (100% coverage)  
- `tests/test_dashboard.py` - Dashboard logic testing
- `tests/test_pages.py` - Page functionality testing
- `tests/test_integration.py` - End-to-end integration testing
- `tests/test_streamlit_apps.py` - Streamlit application testing

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows (marked with `@pytest.mark.integration`)
- **Performance Tests**: Test with larger datasets (marked with `@pytest.mark.slow`)

## Running Tests

### Basic Test Run
```bash
pytest
```

### With Coverage Report
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test Categories
```bash
# Run only integration tests
pytest -m integration

# Run excluding slow tests  
pytest -m "not slow"
```

### Generate HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
```

## Coverage Goals

- **Database Layer**: 92% coverage achieved
- **Utils Layer**: 100% coverage achieved  
- **Overall Target**: 90% coverage threshold

## Test Configuration

Tests are configured via `pytest.ini`:
- Coverage threshold: 90%
- HTML and terminal coverage reports
- Custom markers for integration and slow tests

## Continuous Integration

GitHub Actions workflow (`.github/workflows/test.yml`) runs:
- All tests on Python 3.12
- Coverage reporting
- Fails if coverage drops below 90%

## Key Testing Features

### Database Testing
- In-memory SQLite for isolated tests
- Complete CRUD operation coverage
- Error handling scenarios
- Repository pattern testing

### Authentication Testing  
- Password validation flows
- Environment variable handling
- Session state management

### Business Logic Testing
- Youth ranking calculations
- Task completion workflows
- Points calculation algorithms
- Missionary activity tracking

### Integration Testing
- Complete user workflows
- Cross-component interactions
- Data consistency verification
- Error recovery scenarios

## Running in Development

Set the AUTH environment variable for tests:
```bash
export AUTH=test_password
pytest
```

## Troubleshooting

### Common Issues

1. **Coverage not 100%**: Some Streamlit pages are difficult to test directly
2. **Database conflicts**: Tests use in-memory databases to avoid conflicts
3. **Mock issues**: Complex mock setups for Streamlit components

### Tips

- Run tests with `-v` for verbose output
- Use `--tb=short` for shorter tracebacks
- Check `htmlcov/index.html` for detailed coverage reports