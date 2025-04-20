# Python Cross-Platform Development Standards [L2]

## File System Operations
- Use pathlib.Path instead of os.path
- Use / or joinpath() for paths
- Use Path.exists() for file checks
- Always specify UTF-8 encoding
- Handle line ending differences
- Avoid hardcoded separators
- Support Unicode paths
- Use tempfile for temp files
- Implement portable file locks

## Platform Detection
- Use platform.system() for OS checks
- Use os.name for simple checks
- Isolate platform-specific code
- Abstract platform differences
- Handle case sensitivity
- Manage permissions per OS
- Configure shell flags per platform

## Resource Management
- Use environment variables
- Support config file inputs
- Package resources properly
- Handle path differences
- Manage process handling
- Control memory usage