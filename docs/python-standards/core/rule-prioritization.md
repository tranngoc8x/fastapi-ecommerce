# Python Rule Prioritization [L0]

## Absolute Priorities (L0)
- Security rules override all others
- Data integrity > performance
- Input validation is mandatory
- Resource cleanup is required

## Critical Rules (L1)
- Type hints for public APIs
- Context managers for resources
- Input validation for all external data
- Logging instead of print statements
- Error handling for all operations
- Secure password handling

## Important Rules (L2)
- Code documentation
- Performance optimization
- Test coverage
- Error logging
- Code structure
- Resource management

## Recommended Rules (L3)
- Code style consistency
- Documentation style
- Variable naming conventions
- Module organization
- Comment clarity

## Optional Rules (L4)
- Additional optimizations
- Extra documentation
- Development tools
- Code formatting preferences