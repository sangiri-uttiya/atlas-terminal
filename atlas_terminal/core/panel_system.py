"""
AtlasPanel — Base class for all dockable panels in AtlasTerminal

Every piece of content lives in an AtlasPanel — a QDockWidget subclass with:
- Custom title bar showing panel type icon, ticker label, link group color button, minimize/detach/close buttons
- Floating behavior via QDockWidget native support
- Dock area restrictions
- Link group integration
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QIcon

from .link_group_manager import LinkGroupManager


class PanelTitleBar(QFrame):
    """Custom title bar for AtlasPanel with link group color indicator."""
    
    def __init__(self, parent: "AtlasPanel"):
        super().__init__(parent)
        self.panel = parent
        
        self.setFixedHeight(28)
        self.setObjectName("panelTitleBar")
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)
        
        # Link group color button (circular)
        self.color_button = QPushButton()
        self.color_button.setFixedSize(16, 16)
        self.color_button.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                background-color: gray;
                border: 1px solid #444;
            }
            QPushButton:hover {
                border: 1px solid #888;
            }
        """)
        self.color_button.clicked.connect(self._on_color_clicked)
        self.color_button.setToolTip("Click to cycle link group color")
        layout.addWidget(self.color_button)
        
        # Panel type icon (placeholder - 16px)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Ticker/symbol label
        self.ticker_label = QLabel()
        self.ticker_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.ticker_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.ticker_label)
        
        # Window controls (minimize, detach, close)
        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(20, 20)
        self.minimize_button.clicked.connect(self.panel.showMinimized)
        layout.addWidget(self.minimize_button)
        
        self.detach_button = QPushButton("❐")
        self.detach_button.setFixedSize(20, 20)
        self.detach_button.clicked.connect(self._toggle_floating)
        layout.addWidget(self.detach_button)
        
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.panel.close)
        layout.addWidget(self.close_button)
    
    def _on_color_clicked(self):
        """Cycle through link group colors on click."""
        current_group = LinkGroupManager().get_panel_group(self.panel)
        new_group = LinkGroupManager().cycle_group_color(current_group)
        LinkGroupManager().assign_panel_to_group(self.panel, new_group)
        self.update_color_indicator()
    
    def _toggle_floating(self):
        """Toggle panel floating state."""
        self.panel.setFloating(not self.panel.isFloating())
    
    def update_color_indicator(self):
        """Update the color button to reflect current link group."""
        group_id = LinkGroupManager().get_panel_group(self.panel)
        color_name = LinkGroupManager.get_color_name(group_id)
        
        # Map color names to actual colors
        color_map = {
            "red": "#e74c3c",
            "blue": "#3498db",
            "green": "#2ecc71",
            "yellow": "#f1c40f",
            "orange": "#e67e22",
            "purple": "#9b59b6",
            "gray": "#95a5a6",
        }
        color = color_map.get(color_name, "#95a5a6")
        
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                border-radius: 8px;
                background-color: {color};
                border: 1px solid #444;
            }}
            QPushButton:hover {{
                border: 1px solid #888;
            }}
        """)
    
    def set_ticker(self, ticker: str):
        """Set the ticker text in the title bar."""
        self.ticker_label.setText(ticker if ticker else self.panel.panel_type)


class AtlasPanel(QDockWidget):
    """Base class for all dockable panels in AtlasTerminal."""
    
    # Signal emitted when this panel's ticker changes
    ticker_changed = pyqtSignal(str)
    
    def __init__(self, panel_type: str, title: str = "", parent=None):
        super().__init__(title, parent)
        
        self.panel_type = panel_type
        self._ticker: str = ""
        self._link_group: int = -1  # -1 means unlinked
        
        # Set up features
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.setMinimumSize(QSize(300, 200))
        
        # Create custom title bar
        self.title_bar = PanelTitleBar(self)
        self.setTitleBarWidget(self.title_bar)
        
        # Create central widget (to be overridden by subclasses)
        self.central_widget = QWidget()
        self.setWidget(self.central_widget)
        
        # Apply shadow effect for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.graphicsEffect = shadow
    
    @property
    def ticker(self) -> str:
        """Get current ticker."""
        return self._ticker
    
    def set_ticker(self, ticker: str) -> None:
        """Set the ticker and broadcast to linked panels."""
        if ticker == self._ticker:
            return
        
        self._ticker = ticker.upper()
        self.title_bar.set_ticker(self._ticker)
        self.title_bar.update_color_indicator()
        
        # Emit signal for this panel to update its content
        self.ticker_changed.emit(self._ticker)
        
        # Broadcast to linked panels
        LinkGroupManager().broadcast(self, self._ticker)
    
    def set_panel_icon(self, icon_path: str) -> None:
        """Set the panel type icon."""
        # Placeholder - in real implementation would load from resources
        self.title_bar.icon_label.setText(icon_path[0] if icon_path else "?")
    
    def get_config(self) -> Dict[str, Any]:
        """Get panel configuration for workspace serialization."""
        return {
            "type": self.panel_type,
            "ticker": self._ticker,
            "link_group": LinkGroupManager().get_panel_group(self),
            "floating": self.isFloating(),
        }
    
    def restore_config(self, config: Dict[str, Any]) -> None:
        """Restore panel configuration from workspace serialization."""
        if "ticker" in config:
            self.set_ticker(config["ticker"])
        if "link_group" in config:
            LinkGroupManager().assign_panel_to_group(self, config["link_group"])
            self.title_bar.update_color_indicator()
