# Tests

This directory contains tests for the application.

## Structure

```
tests/
├── unit/                  # Unit tests
│   └── services/          # Tests for services
│       ├── business/      # Tests for business services
│       └── infrastructure/ # Tests for infrastructure services
└── integration/           # Integration tests
    └── services/          # Integration tests for services
```

## Running Tests

To run all tests:

```bash
docker-compose exec api pytest
```

To run unit tests only:

```bash
docker-compose exec api pytest tests/unit/
```

To run integration tests only:

```bash
docker-compose exec api pytest tests/integration/
```

To run tests with verbose output:

```bash
docker-compose exec api pytest -v
```

To run a specific test file:

```bash
docker-compose exec api pytest tests/unit/services/business/test_user_service.py
```

To run a specific test:

```bash
docker-compose exec api pytest tests/unit/services/business/test_user_service.py::TestUserService::test_create_user
```

## Test Categories

### Unit Tests

Unit tests test individual components in isolation. They use mocks to avoid dependencies on external systems.

- **Business Services**: Tests for business logic services (user, product, order)
- **Infrastructure Services**: Tests for infrastructure services (messaging, async tasks, Kafka)

### Integration Tests

Integration tests test the interaction between components. They verify that components work together correctly.

- **Kafka Integration**: Tests for Kafka producer and consumer integration

## Fixtures

Fixtures are defined in `conftest.py`. They provide test data and mock objects for tests.

- **Database Fixtures**: In-memory SQLite database for testing
- **Repository Fixtures**: Repository objects for testing
- **Model Fixtures**: Test models (user, product, order)
- **Mock Fixtures**: Mock objects for external dependencies (Kafka, Celery)

## Markers

Markers are used to categorize tests. They are defined in `pytest.ini`.

- **unit**: Unit tests
- **integration**: Integration tests
- **slow**: Slow tests
- **kafka**: Tests that require Kafka
- **celery**: Tests that require Celery

To run tests with a specific marker:

```bash
docker-compose exec api pytest -m integration
```
