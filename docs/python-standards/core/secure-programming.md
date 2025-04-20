# Python Secure Programming Standards [L0]

## Input Validation & Sanitization
- Always validate all user inputs
- Limit input size to prevent DoS
- Validate before processing begins
- Sanitize data before display/output
- Sanitize HTML/XML before parsing
- Prevent path traversal via sanitization
- Escape and validate shell inputs

## Data Protection
- Use secure password hashing
- Encrypt sensitive data at rest
- Use secure random for tokens
- Protect against SQL injection
- Validate file uploads
- Sanitize file paths

## Environment & Configuration
- Use environment variables for secrets
- Never commit secrets to VCS
- Use secure session management
- Enable security headers
- Configure CORS properly