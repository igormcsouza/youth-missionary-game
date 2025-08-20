# Tests for Youth Missionary Game

This directory contains test cases for the Youth Missionary Game application, specifically focusing on the Organization column feature added to the Compiled Entries table.

## Test Files

### `test_organization_feature_simple.py`
Contains basic unit tests for the organization column functionality:
- Tests organization mapping structure
- Tests DataFrame column order with Organization column
- Tests function signature changes for `refresh_youth_and_task_entries`
- Tests edge cases and helper functions

### `test_organization_integration.py`
Contains integration tests that work with actual database operations:
- End-to-end testing of the organization column workflow
- Database integration tests with SQLite in-memory database
- Tests the complete data flow from database to DataFrame display
- Tests edge cases with real database operations

## Running Tests

To run all tests:
```bash
pytest tests/ -v
```

To run a specific test file:
```bash
pytest tests/test_organization_feature_simple.py -v
pytest tests/test_organization_integration.py -v
```

## Test Coverage

The tests cover the following aspects of the Organization column feature:

1. **Function Signature Changes**: Tests that `refresh_youth_and_task_entries()` now returns 5 values instead of 4 (added `youth_org_options`)

2. **Organization Mapping**: Tests that the organization mapping `{youth_id: organization}` is correctly created and used

3. **DataFrame Structure**: Tests that the compiled entries DataFrame includes the "Organização" column in the correct position (index 1)

4. **Helper Functions**: Tests the `get_organization_by_id()` helper function logic

5. **Data Integration**: Tests the complete workflow from database queries to DataFrame display

6. **Edge Cases**: Tests handling of non-existent IDs and empty data scenarios

## Requirements

The tests require:
- pytest
- pandas  
- sqlmodel
- All other dependencies from requirements.txt

The tests use in-memory SQLite databases and mock Streamlit components to avoid UI dependencies during testing.