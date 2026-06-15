"""
Core module initialization — Application Shell, Panel System, Command Bar
"""

from .app import AtlasTerminalApp
from .main_window import MainWindow
from .panel_system import AtlasPanel, LinkGroupManager
from .command_bar import CommandBar

__all__ = [
    "AtlasTerminalApp",
    "MainWindow",
    "AtlasPanel",
    "LinkGroupManager",
    "CommandBar",
]
