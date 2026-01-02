"""Tool descriptions for TSX file operations."""

READ_TSX_DESCRIPTION = """Read content from a TSX/TypeScript React file with optional line-based pagination.

This tool returns TSX file content with line numbers and supports reading large files in chunks to avoid context overflow.

Parameters:
- file_path (required): Path to the TSX file to read
- offset (optional, default=0): Line number to start reading from
- limit (optional, default=2000): Maximum number of lines to read

Always read a file before editing it to understand existing code structure."""

WRITE_TSX_DESCRIPTION = """Create a new TSX file or completely overwrite an existing TSX file in the virtual filesystem.

Use for initial TSX file creation or complete rewrites. TSX files are stored persistently in agent state and can be used by other agents or exported.

Parameters:
- file_path (required): Path where the TSX file should be created/overwritten
- content (required): The complete TSX/TypeScript code to write

Important: This replaces the entire file content."""
