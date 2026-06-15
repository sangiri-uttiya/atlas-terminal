#!/usr/bin/env python3
"""
AtlasTerminal — Main Entry Point

Professional Desktop Application for Indian Equity Swing Traders

Usage:
    python -m atlas_terminal.main
    
Or after installation:
    atlas-terminal
"""

import sys
from pathlib import Path


def main():
    """Main entry point for AtlasTerminal."""
    # Add the parent directory to path for imports
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from atlas_terminal.core.app import AtlasTerminalApp
    
    app = AtlasTerminalApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
