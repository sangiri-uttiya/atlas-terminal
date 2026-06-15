"""
Command Bar — Full-width navigation and ticker lookup bar

Located below the menu bar, the command bar provides:
- Ticker autocomplete and lookup
- Command palette for module navigation
- Quick access to common actions
"""

from typing import List, Dict, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QCompleter, QListWidget, 
    QFrame, QLabel, QPushButton, QVBoxLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor


class CommandBar(QFrame):
    """
    Command bar widget providing ticker lookup and command palette.
    
    Features:
    - Ticker autocomplete with Nifty 500 universe
    - Command palette accessible via Ctrl+P or '/' shortcut
    - Link group awareness for ticker changes
    """
    
    # Signal emitted when a ticker is selected
    ticker_selected = pyqtSignal(str)
    
    # Signal emitted when a command is invoked
    command_invoked = pyqtSignal(str)  # command name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(32)
        self.setObjectName("commandBar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Left section — ticker input
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Type ticker or press '/' for commands...")
        self.ticker_input.setFixedWidth(300)
        self.ticker_input.textChanged.connect(self._on_ticker_changed)
        self.ticker_input.returnPressed.connect(self._on_ticker_entered)
        layout.addWidget(self.ticker_input)
        
        # Completer for tickers (populated later)
        self.ticker_completer = QCompleter([], self)
        self.ticker_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ticker_completer.setMaxVisibleItems(10)
        self.ticker_input.setCompleter(self.ticker_completer)
        
        # Right section — quick action buttons
        layout.addStretch()
        
        # Help button
        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(24, 24)
        self.help_button.setToolTip("Help (F1)")
        self.help_button.clicked.connect(lambda: self.command_invoked.emit("help"))
        layout.addWidget(self.help_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(lambda: self.command_invoked.emit("settings"))
        layout.addWidget(self.settings_button)
        
        # Command palette popup (hidden by default)
        self._command_popup: Optional[CommandPopup] = None
    
    def set_tickers(self, tickers: List[str]) -> None:
        """Set the list of available tickers for autocomplete."""
        from PyQt6.QtGui import QStringListModel
        self.ticker_completer.setModel(QStringListModel(tickers))
    
    def _on_ticker_changed(self, text: str) -> None:
        """Handle ticker input change."""
        # Could add live filtering here if needed
        pass
    
    def _on_ticker_entered(self) -> None:
        """Handle Enter key in ticker input."""
        text = self.ticker_input.text().strip().upper()
        if text:
            self.ticker_selected.emit(text)
            self.ticker_input.clear()
    
    def show_command_palette(self) -> None:
        """Show the command palette popup."""
        if self._command_popup is None:
            self._command_popup = CommandPopup(self)
            self._command_popup.command_selected.connect(self._on_command_selected)
        
        self._command_popup.show_at(self)
        self.ticker_input.clear()
        self.ticker_input.setFocus()
    
    def _on_command_selected(self, command: str) -> None:
        """Handle command selection from palette."""
        self.command_invoked.emit(command)
        if self._command_popup:
            self._command_popup.hide()


class CommandPopup(QFrame):
    """Popup widget showing available commands."""
    
    command_selected = pyqtSignal(str)
    
    # Built-in commands
    COMMANDS = [
        {"name": "chart", "label": "Open Chart Panel", "shortcut": ""},
        {"name": "quote", "label": "Open Quote Panel", "shortcut": ""},
        {"name": "watchlist", "label": "Open Watchlist", "shortcut": ""},
        {"name": "screener", "label": "Open Screener", "shortcut": ""},
        {"name": "atlas_signal", "label": "Atlas Signal", "shortcut": ""},
        {"name": "backtest", "label": "Backtester", "shortcut": ""},
        {"name": "portfolio", "label": "Portfolio", "shortcut": ""},
        {"name": "journal", "label": "Trade Journal", "shortcut": ""},
        {"name": "news", "label": "News & Announcements", "shortcut": ""},
        {"name": "fundamentals", "label": "Fundamentals", "shortcut": ""},
        {"name": "heatmap", "label": "Sector Heatmap", "shortcut": ""},
        {"name": "breadth", "label": "Market Breadth", "shortcut": ""},
        {"name": "fii_dii", "label": "FII/DII Flow", "shortcut": ""},
        {"name": "macro", "label": "Macro Dashboard", "shortcut": ""},
        {"name": "download", "label": "Data Download", "shortcut": ""},
        {"name": "settings", "label": "Settings", "shortcut": ""},
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("commandPopup")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type command...")
        self.input_field.textChanged.connect(self._filter_commands)
        self.input_field.returnPressed.connect(self._on_enter)
        layout.addWidget(self.input_field)
        
        # Command list
        self.command_list = QListWidget()
        self.command_list.setFixedHeight(200)
        self.command_list.setFixedWidth(300)
        self.command_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.command_list)
        
        # Populate initial list
        self._update_command_list(self.COMMANDS)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
    
    def show_at(self, target: QWidget) -> None:
        """Show popup positioned below the target widget."""
        pos = target.mapToGlobal(target.rect().bottomLeft())
        self.move(pos)
        self.show()
        self.input_field.setFocus()
    
    def _update_command_list(self, commands: List[Dict]) -> None:
        """Update the command list widget."""
        self.command_list.clear()
        for cmd in commands:
            label = cmd["label"]
            if cmd["shortcut"]:
                label += f" ({cmd['shortcut']})"
            self.command_list.addItem(label)
    
    def _filter_commands(self, text: str) -> None:
        """Filter commands based on input text."""
        text = text.lower().strip()
        if not text:
            self._update_command_list(self.COMMANDS)
            return
        
        filtered = [
            cmd for cmd in self.COMMANDS
            if text in cmd["name"].lower() or text in cmd["label"].lower()
        ]
        self._update_command_list(filtered)
    
    def _on_enter(self) -> None:
        """Handle Enter key in command input."""
        current_row = self.command_list.currentRow()
        if current_row >= 0 and current_row < len(self.COMMANDS):
            cmd = self.COMMANDS[current_row]
            self.command_selected.emit(cmd["name"])
    
    def _on_item_clicked(self, item) -> None:
        """Handle item click in command list."""
        row = self.command_list.row(item)
        if 0 <= row < len(self.COMMANDS):
            cmd = self.COMMANDS[row]
            self.command_selected.emit(cmd["name"])
