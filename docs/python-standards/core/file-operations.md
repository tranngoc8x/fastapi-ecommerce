# Python File Operations Standards [L1]

## Context Management
- Always use with statements
- Explicit UTF-8 encoding
- Binary mode for non-text
- Ensure file closing
- Handle cleanup

## Path Management
- Use pathlib.Path
- Check existence
- Use tempfile module
- Avoid hardcoded paths
- Cross-platform paths

## Error Handling
- Use EAFP pattern
- Specific exceptions
- Ensure cleanup
- Log failures
- Context in errors

## Structured Formats
- CSV handling
- JSON processing
- Safe deserialization
- Format validation
- Error recovery

## Security
- Path validation
- Secure permissions
- Untrusted sources
- Pickle safety
- Access control