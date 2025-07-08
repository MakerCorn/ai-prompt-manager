# Comprehensive Testing Guide

This guide provides an overview of the comprehensive testing strategy for the AI Prompt Manager project.

## 🎯 Test Coverage Overview

The AI Prompt Manager project has **21 test files** providing comprehensive coverage across all components:

- **11 Unit Test Files**: Testing individual components and functions
- **10 Integration Test Files**: Testing component interactions and system behavior

## 📋 Unit Tests (11 files)

### Core Components
- `test_config.py` - Configuration system testing
- `test_exceptions.py` - Exception handling testing

### Authentication & Security
- `test_password_handler.py` - Password security testing
- `test_tenant_model.py` - Tenant model testing  
- `test_user_model.py` - User model testing
- `test_auth_manager.py` - Authentication manager testing
- `test_api_token_manager.py` - API token management testing

### Prompt Management
- `test_prompt_model.py` - Prompt model testing
- `test_prompt_data_manager.py` - Prompt data operations testing

### AI Services & APIs
- `test_langwatch_optimizer.py` - Prompt optimization testing
- `test_token_calculator.py` - Token calculation testing
- `test_api_endpoints.py` - API endpoint testing
- `test_speech_dictation.py` - Speech dictation functionality testing

## 📋 Integration Tests (10 files)

### System Integration
- `test_mt_install.py` - Multi-tenant installation testing
- `test_new_architecture_integration.py` - New architecture integration
- `test_new_prompt_architecture.py` - Prompt architecture integration

### API Integration
- `test_api_integration.py` - Comprehensive API testing
- `test_standalone_api.py` - Standalone API server testing
- `simple_api_test.py` - Basic API functionality testing

### External Service Integration
- `test_langwatch_integration.py` - LangWatch service integration
- `test_azure_integration.py` - Azure AI services integration
- `test_speech_api_integration.py` - Speech dictation API integration

## 🚀 CI/CD Test Execution

### Automated Test Workflow

The `test.yml` workflow runs **ALL** tests systematically:

#### 1. **Unit Test Execution**
```bash
poetry run pytest tests/unit/ -v --tb=short --durations=10
```
- Runs all 11 unit test files
- Verbose output with duration reporting
- Comprehensive test counting and validation

#### 2. **Integration Test Execution**
All 10 integration tests are executed individually:

1. **LangWatch Integration**: AI-powered prompt optimization
2. **Multi-tenant Installation**: Complete system setup validation
3. **New Architecture Integration**: Modern architecture validation
4. **API Integration**: Comprehensive API testing
5. **Standalone API**: Independent API server testing
6. **Azure Integration**: Cloud services integration (conditional)

#### 3. **Component Testing**
- New architecture component validation
- Core component import testing
- Configuration system testing
- Repository functionality validation

#### 4. **Standalone API Testing**
- Custom API server startup and testing
- Health endpoint validation
- Authentication testing
- Proper cleanup and teardown

### Test Reports

Each test run provides:
- **Test count summaries**: Unit and integration test counts
- **Detailed test results**: Pass/fail status for each test
- **Duration reporting**: Performance insights
- **Coverage validation**: Comprehensive system coverage

## 🛠️ Running Tests Locally

### Prerequisites
```bash
# Install dependencies
poetry install

# Ensure Python 3.12+
python --version
```

### Unit Tests
```bash
# Run all unit tests
poetry run pytest tests/unit/ -v

# Run specific unit test file
poetry run pytest tests/unit/test_auth_manager.py -v

# Run with coverage
poetry run pytest tests/unit/ --cov=. --cov-report=html
```

### Integration Tests
```bash
# Run all integration tests (one by one)
poetry run python tests/integration/test_langwatch_integration.py
poetry run python tests/integration/test_mt_install.py
poetry run python tests/integration/test_api_integration.py
# ... etc

# Run new architecture tests
poetry run python tests/integration/test_new_architecture_integration.py

# Run speech dictation API integration tests
poetry run python tests/integration/test_speech_api_integration.py
```

### End-to-End (E2E) Tests
```bash
# Install E2E dependencies
poetry install --with e2e

# Install browser dependencies
poetry run playwright install chromium --with-deps

# Run all E2E tests
poetry run pytest tests/e2e/ -v -m "e2e"

# Run speech dictation E2E tests specifically
poetry run python tests/e2e/test_speech_dictation_e2e.py

# Run with visible browser (for debugging)
E2E_HEADLESS=false poetry run pytest tests/e2e/ -v -m "e2e"

# Run with slow motion for observation
E2E_SLOW_MO=500 poetry run pytest tests/e2e/ -v -m "e2e"
```

### Complete Test Suite
```bash
# Run the same tests as CI/CD
poetry run pytest tests/unit/ -v --tb=short --durations=10

# Then run each integration test
for test in tests/integration/test_*.py; do
    echo "Running $test..."
    poetry run python "$test"
done
```

## 🧪 Test Configuration

### Pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "slow: Tests that take a long time to run",
]
```

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.slow` - Long-running tests

## 🔍 Test Categories

### Authentication & Security Tests
- Password hashing and validation
- JWT token generation and validation
- User and tenant management
- API token security
- Multi-tenant data isolation

### Data Management Tests
- Database operations (SQLite and PostgreSQL)
- Prompt CRUD operations
- Repository pattern implementation
- Data migration and schema validation

### API & Integration Tests
- REST API endpoints
- Authentication middleware
- Request/response validation
- Error handling
- OpenAPI documentation

### AI Service Tests
- LangWatch integration
- Azure AI services
- Token calculation accuracy
- Optimization workflow validation

### Architecture Tests
- New modular architecture
- Service layer functionality
- Dependency injection
- Configuration management
- Modern architecture integration

### Speech Dictation Tests
- **Unit Tests (19 tests)**: Text enhancement logic and core functionality
  - Filler word removal algorithms
  - Grammar correction and capitalization
  - Edge case handling (empty text, special characters, unicode)
  - Performance testing with large text inputs
- **Integration Tests (10 tests)**: API endpoints and server integration
  - `/enhance-text` endpoint functionality
  - `/translate` endpoint testing
  - Authentication and error handling
  - Performance and timeout testing
- **E2E Tests (20 tests)**: Browser automation and user workflows
  - Speech dictation UI component testing
  - Microphone permission handling
  - Language selection and switching
  - Enhancement and translation workflows
  - Mobile responsiveness and accessibility
  - Cross-browser compatibility testing

**Speech Dictation Test Coverage:**
- **Text Enhancement Engine**: Comprehensive regex and AI-based enhancement
- **Multi-Language Support**: 12 languages with translation capabilities
- **UI Integration**: Complete form integration with real-time updates
- **Browser Compatibility**: Chrome, Edge, Safari, Firefox testing
- **Security**: Authentication, session validation, secure API calls
- **Performance**: Fast text processing, graceful AI service fallback
- **Accessibility**: Keyboard navigation, screen reader compatibility

## 📊 Test Quality Metrics

### Coverage Areas
- **100% Critical Path Coverage**: All essential functionality tested
- **Multi-Environment Testing**: SQLite and PostgreSQL support
- **Security Testing**: Authentication, authorization, and data isolation
- **Performance Testing**: Token calculation and optimization
- **Integration Testing**: External service integration
- **Error Handling**: Comprehensive error scenario coverage

### Test Reliability
- **Deterministic Tests**: Consistent results across environments
- **Isolated Tests**: No test dependencies or side effects  
- **Cleanup**: Proper teardown and resource management
- **Mock Integration**: External services mocked appropriately

## 🚨 Troubleshooting Tests

### Common Issues

**Import Errors**:
```bash
# Ensure Python path includes src directory
export PYTHONPATH="${PYTHONPATH}:./src"
poetry run python tests/integration/test_new_architecture_integration.py
```

**Database Issues**:
```bash
# Clean up test databases
rm -f test_*.db
rm -f temp_test_*.db
```

**API Tests Failing**:
```bash
# Check if ports are available
lsof -i :7860
lsof -i :7861

# Kill any running instances
pkill -f "python.*run.py"
```

### Test Dependencies
All tests use isolated environments and temporary databases to avoid conflicts.

## 🎯 Best Practices

### Writing New Tests
1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test component interactions
3. **Use Fixtures**: Create reusable test data and setup
4. **Mock External Services**: Don't rely on external APIs in tests
5. **Clean Up**: Always clean up resources after tests

### Test Organization
- Keep unit tests focused and fast
- Use descriptive test names
- Group related tests in the same file
- Add docstrings for complex test scenarios

---

This comprehensive testing strategy ensures the AI Prompt Manager is reliable, secure, and maintainable across all deployment scenarios.