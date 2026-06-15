"""
Main Window — Primary application window with dockable panel system

The main window contains:
- Menu bar (File | Data | Atlas | View | Tools | Help)
- Command bar (below menu bar)
- Panel workspace (central QDockWidget area)
- Status bar (market session, last data date, feed health, time)
"""

import json
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QMenuBar, QMenu, QStatusBar, QTabBar, 
    QWidget, QVBoxLayout, QApplication, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QKeySequence, QShortcut

from .command_bar import CommandBar
from .panel_system import AtlasPanel
from .link_group_manager import LinkGroupManager


class MainWindow(QMainWindow):
    """Main application window for AtlasTerminal."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AtlasTerminal")
        self.setMinimumSize(1280, 800)
        
        # Initialize link group manager
        self.link_manager = LinkGroupManager()
        
        # Track all open panels
        self.panels: List[AtlasPanel] = []
        
        # Current workspace index
        self.current_workspace_idx = 0
        
        # Build UI components
        self._setup_menu_bar()
        self._setup_command_bar()
        self._setup_status_bar()
        self._setup_shortcuts()
        
        # Apply stylesheet
        self._apply_stylesheet()
    
    def _setup_menu_bar(self) -> None:
        """Create the menu bar with File | Data | Atlas | View | Tools | Help."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Workspace", self._new_workspace, QKeySequence("Ctrl+N"))
        file_menu.addAction("&Save Workspace", self._save_workspace, QKeySequence("Ctrl+S"))
        file_menu.addAction("&Load Workspace", self._load_workspace, QKeySequence("Ctrl+O"))
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close, QKeySequence("Alt+F4"))
        
        # Data menu
        data_menu = menubar.addMenu("&Data")
        data_menu.addAction("&Download Bhavcopy", lambda: self._invoke_command("download"))
        data_menu.addAction("Download &F&O Data", lambda: None)  # TODO
        data_menu.addAction("Import Fundamentals CSV", lambda: None)  # TODO
        data_menu.addSeparator()
        data_menu.addAction("Refresh All Data", lambda: None)  # TODO
        
        # Atlas menu
        atlas_menu = menubar.addMenu("&Atlas")
        atlas_menu.addAction("&Run Signal", lambda: self._invoke_command("atlas_signal"))
        atlas_menu.addAction("&Backtest", lambda: self._invoke_command("backtest"))
        atlas_menu.addSeparator()
        atlas_menu.addAction("&Settings", lambda: self._invoke_command("settings"))
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("&Command Palette", self._show_command_palette, QKeySequence("Ctrl+P"))
        view_menu.addAction("&New Panel", self._show_panel_picker, QKeySequence("Ctrl+Shift+N"))
        view_menu.addSeparator()
        view_menu.addAction("Toggle &Density", self._toggle_density, QKeySequence("Ctrl+D"))
        view_menu.addAction("Toggle Fullscreen", self._toggle_fullscreen, QKeySequence("F11"))
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Screener", lambda: self._invoke_command("screener"))
        tools_menu.addAction("&Heatmap", lambda: self._invoke_command("heatmap"))
        tools_menu.addAction("Market &Breadth", lambda: self._invoke_command("breadth"))
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&Documentation", lambda: None)  # TODO
        help_menu.addAction("&About", self._show_about)
    
    def _setup_command_bar(self) -> None:
        """Create and add the command bar below the menu bar."""
        self.command_bar = CommandBar(self)
        self.command_bar.ticker_selected.connect(self._on_ticker_selected)
        self.command_bar.command_invoked.connect(self._invoke_command)
        
        # Add command bar to top of main window
        # We need a container widget since we can't add widgets directly to QMainWindow top
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.command_bar)
        
        self.setMenuWidget(container)
    
    def _setup_status_bar(self) -> None:
        """Create the status bar showing market info."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Market session label
        self.session_label = QLabel("Market: CLOSED")
        self.status_bar.addPermanentWidget(self.session_label)
        
        # Last data date
        self.last_data_label = QLabel("Last Data: --")
        self.status_bar.addPermanentWidget(self.last_data_label)
        
        # Feed health indicator
        self.feed_health_label = QLabel("Feed: OK")
        self.status_bar.addPermanentWidget(self.feed_health_label)
        
        # Time display
        self.time_label = QLabel("")
        self.status_bar.addPermanentWidget(self.time_label)
        
        # Update time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()
    
    def _setup_shortcuts(self) -> None:
        """Set up global keyboard shortcuts."""
        # Ctrl+P for command palette
        shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut.activated.connect(self._show_command_palette)
        
        # F1 for help
        shortcut = QShortcut(QKeySequence("F1"), self)
        shortcut.activated.connect(lambda: self._invoke_command("help"))
    
    def _apply_stylesheet(self) -> None:
        """Apply the application stylesheet."""
        # Default compact density
        self.density_mode = "compact"
        
        stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 2px;
        }
        
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #444;
        }
        
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        
        QStatusBar {
            background-color: #252525;
            color: #aaaaaa;
        }
        
        QLineEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 4px 8px;
        }
        
        QLineEdit:focus {
            border: 1px solid #3498db;
        }
        
        QPushButton {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #444;
            border-radius: 3px;
            padding: 4px 8px;
        }
        
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(float.png);
        }
        
        QDockWidget::title {
            background-color: #2d2d2d;
            padding: 3px;
            spacing: 3px;
        }
        
        QDockWidget::close-button, QDockWidget::float-button {
            border: none;
            background: transparent;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def _update_time(self) -> None:
        """Update the time display in status bar."""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)
        
        # Update market session based on IST time
        # NSE market hours: 9:15 AM - 3:30 PM IST
        hour = QTime.currentTime().hour()
        minute = QTime.currentTime().minute()
        current_minutes = hour * 60 + minute
        
        market_open = 9 * 60 + 15   # 9:15 AM
        market_close = 15 * 60 + 30  # 3:30 PM
        
        if market_open <= current_minutes <= market_close:
            self.session_label.setText("Market: OPEN")
            self.session_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.session_label.setText("Market: CLOSED")
            self.session_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def _on_ticker_selected(self, ticker: str) -> None:
        """Handle ticker selection from command bar."""
        # If there's a focused panel, set its ticker
        # Otherwise, create a new quote panel
        focused_panel = QApplication.focusWidget()
        if focused_panel:
            # Find parent panel
            widget = focused_panel
            while widget:
                if isinstance(widget, AtlasPanel):
                    widget.set_ticker(ticker)
                    return
                widget = widget.parent()
        
        # No focused panel - could open a default panel
        # For now, just show a message
        self.status_bar.showMessage(f"Ticker selected: {ticker}", 3000)
    
    def _invoke_command(self, command: str) -> None:
        """Invoke a command by name."""
        command_handlers = {
            "chart": self._open_chart_panel,
            "quote": self._open_quote_panel,
            "watchlist": self._open_watchlist_panel,
            "screener": self._open_screener_panel,
            "atlas_signal": self._open_atlas_signal_panel,
            "backtest": self._open_backtest_panel,
            "portfolio": self._open_portfolio_panel,
            "journal": self._open_journal_panel,
            "news": self._open_news_panel,
            "fundamentals": self._open_fundamentals_panel,
            "heatmap": self._open_heatmap_panel,
            "breadth": self._open_breadth_panel,
            "fii_dii": self._open_fii_dii_panel,
            "macro": self._open_macro_panel,
            "download": self._open_download_panel,
            "settings": self._open_settings,
            "help": self._show_about,
        }
        
        handler = command_handlers.get(command)
        if handler:
            handler()
        else:
            self.status_bar.showMessage(f"Unknown command: {command}", 2000)
    
    def _show_command_palette(self) -> None:
        """Show the command palette."""
        self.command_bar.show_command_palette()
    
    def _show_panel_picker(self) -> None:
        """Show the panel picker dialog."""
        # TODO: Implement panel picker dialog
        self.status_bar.showMessage("Panel picker - coming soon", 2000)
    
    def _toggle_density(self) -> None:
        """Toggle between compact and comfortable density modes."""
        if self.density_mode == "compact":
            self.density_mode = "comfortable"
            # TODO: Update stylesheet variables
        else:
            self.density_mode = "compact"
        self.status_bar.showMessage(f"Density: {self.density_mode}", 2000)
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    # Panel opening methods (stubs - to be implemented with actual panel classes)
    def _open_chart_panel(self) -> None:
        self.status_bar.showMessage("Opening Chart Panel...", 1000)
        # TODO: Create and dock ChartPanel
    
    def _open_quote_panel(self) -> None:
        self.status_bar.showMessage("Opening Quote Panel...", 1000)
        # TODO: Create and dock QuotePanel
    
    def _open_watchlist_panel(self) -> None:
        self.status_bar.showMessage("Opening Watchlist...", 1000)
        # TODO: Create and dock WatchlistPanel
    
    def _open_screener_panel(self) -> None:
        self.status_bar.showMessage("Opening Screener...", 1000)
        # TODO: Create and dock ScreenerPanel
    
    def _open_atlas_signal_panel(self) -> None:
        self.status_bar.showMessage("Opening Atlas Signal...", 1000)
        # TODO: Create and dock AtlasSignalPanel
    
    def _open_backtest_panel(self) -> None:
        self.status_bar.showMessage("Opening Backtester...", 1000)
        # TODO: Create and dock AtlasBacktestPanel
    
    def _open_portfolio_panel(self) -> None:
        self.status_bar.showMessage("Opening Portfolio...", 1000)
        # TODO: Create and dock PortfolioPanel
    
    def _open_journal_panel(self) -> None:
        self.status_bar.showMessage("Opening Trade Journal...", 1000)
        # TODO: Create and dock JournalPanel
    
    def _open_news_panel(self) -> None:
        self.status_bar.showMessage("Opening News Panel...", 1000)
        # TODO: Create and dock NewsPanel
    
    def _open_fundamentals_panel(self) -> None:
        self.status_bar.showMessage("Opening Fundamentals...", 1000)
        # TODO: Create and dock FundamentalsPanel
    
    def _open_heatmap_panel(self) -> None:
        self.status_bar.showMessage("Opening Sector Heatmap...", 1000)
        # TODO: Create and dock HeatmapPanel
    
    def _open_breadth_panel(self) -> None:
        self.status_bar.showMessage("Opening Market Breadth...", 1000)
        # TODO: Create and dock BreadthPanel
    
    def _open_fii_dii_panel(self) -> None:
        self.status_bar.showMessage("Opening FII/DII Flow...", 1000)
        # TODO: Create and dock FIIDIIPanel
    
    def _open_macro_panel(self) -> None:
        self.status_bar.showMessage("Opening Macro Dashboard...", 1000)
        # TODO: Create and dock MacroPanel
    
    def _open_download_panel(self) -> None:
        self.status_bar.showMessage("Opening Data Download...", 1000)
        # TODO: Create and dock DownloadPanel
    
    def _open_settings(self) -> None:
        """Open settings dialog."""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog - coming soon")
    
    def _new_workspace(self) -> None:
        """Create a new workspace."""
        # TODO: Clear all panels and start fresh
        pass
    
    def _save_workspace(self) -> None:
        """Save current workspace."""
        # TODO: Serialize panel layout and config
        pass
    
    def _load_workspace(self) -> None:
        """Load a saved workspace."""
        # TODO: Deserialize and restore workspace
        pass
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AtlasTerminal",
            "AtlasTerminal v1.0\n\n"
            "Professional Desktop Application for Indian Equity Swing Traders\n\n"
            "Built with PyQt6 and designed for NSE/BSE Indian Equities"
        )
