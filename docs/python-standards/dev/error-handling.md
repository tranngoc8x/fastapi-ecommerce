# Python Error Handling Standards [L1]

## Core Principles
- Use EAFP for I/O operations
- Validate user input explicitly
- Validate at API boundaries
- Fail fast on critical errors
- Create custom exceptions

## Exception Handling
### When to Use Try/Except
- File operations
- Network requests
- Database queries
- Type conversions
- External APIs

### Exception Types
- Use specific exceptions
- Create custom classes
- Maintain hierarchy
- Document exceptions
- Handle cleanup

## Error Reporting
- Log all errors
- Include context
- Stack traces
- Error codes
- User messages

## Recovery Strategies
- Retry mechanisms
- Fallback options
- Cleanup procedures
- State recovery
- User notification

## Best Practices
- Don't catch Exception
- Clean up resources
- Log before raise
- Context in messages
- Document recovery