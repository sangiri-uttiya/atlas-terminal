"""
AtlasTerminal Application — Main entry point

This module provides the QApplication wrapper and application lifecycle management.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AtlasTerminalApp(QApplication):
    """Main application class for AtlasTerminal."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName("AtlasTerminal")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Atlas Terminal")
        
        # Enable high DPI scaling
        self.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Set default font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Set style
        self.setStyle("Fusion")
    
    def run(self, main_window_class=None):
        """Run the application with the given main window class."""
        if main_window_class is None:
            from .main_window import MainWindow
            main_window_class = MainWindow
        
        self.main_window = main_window_class()
        self.main_window.show()
        
        return self.exec()
