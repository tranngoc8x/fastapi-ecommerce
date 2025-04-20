# Python Import Standards [L2]

## Import Structure
- All imports at top of file
- Group imports by type:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- One import per line
- Alphabetical order within groups

## Import Rules
- No unused imports
- Use absolute imports over relative
- No wildcard imports (*)
- No circular imports
- Import modules, not individual files
- __future__ imports first

## Style & Patterns
- Consistent alias naming
- Prefer module over function imports
- Use lazy imports for expensive modules
- Handle OS-specific imports properly
- Clean up unused imports regularly

## Tools
- Use isort for import sorting
- Use flake8 for import checking
- Maintain proper namespace packages
- Use __init__.py appropriately

## Modern Features
- Use __future__.annotations
- Use typing_extensions when needed
- Use importlib.metadata for version info
- Use importlib.resources for data files