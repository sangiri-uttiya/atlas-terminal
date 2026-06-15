"""
Link Group Manager — Singleton managing panel link groups

Panels are assigned link group colors (6 colors: red, blue, green, yellow, orange, purple).
When a ticker changes in any panel in group X, all panels in group X update to that ticker simultaneously.
"""

from typing import Dict, Set, Optional, TYPE_CHECKING
from PyQt6.QtCore import QObject, pyqtSignal

if TYPE_CHECKING:
    from .panel_system import AtlasPanel


class LinkGroupManager(QObject):
    """Singleton manager for panel link groups."""
    
    # Colors available for link groups
    COLORS = [
        "red",
        "blue", 
        "green",
        "yellow",
        "orange",
        "purple",
    ]
    
    # Signal emitted when a ticker change should be broadcast to a group
    ticker_changed = pyqtSignal(str)  # ticker symbol
    
    _instance: Optional["LinkGroupManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._initialized = True
        # Map of group_id -> set of panels
        self._groups: Dict[int, Set["AtlasPanel"]] = {}
        # Map of panel -> group_id (or -1 for unlinked)
        self._panel_groups: Dict["AtlasPanel", int] = {}
        
    def assign_panel_to_group(self, panel: "AtlasPanel", group_id: int) -> None:
        """Assign a panel to a link group. group_id=-1 means unlinked."""
        # Remove from old group if any
        old_group = self._panel_groups.get(panel, -1)
        if old_group != -1 and old_group in self._groups:
            self._groups[old_group].discard(panel)
            if not self._groups[old_group]:
                del self._groups[old_group]
        
        # Assign to new group
        if group_id != -1:
            if group_id not in self._groups:
                self._groups[group_id] = set()
            self._groups[group_id].add(panel)
            self._panel_groups[panel] = group_id
        else:
            if panel in self._panel_groups:
                del self._panel_groups[panel]
    
    def get_panel_group(self, panel: "AtlasPanel") -> int:
        """Get the group ID for a panel. Returns -1 if unlinked."""
        return self._panel_groups.get(panel, -1)
    
    def broadcast(self, panel: "AtlasPanel", ticker: str) -> None:
        """Broadcast a ticker change to all panels in the same group as the source panel."""
        group_id = self._panel_groups.get(panel, -1)
        if group_id == -1:
            return
        
        # Emit signal for all other panels in the group
        if group_id in self._groups:
            for other_panel in self._groups[group_id]:
                if other_panel is not panel:
                    other_panel.set_ticker(ticker)
    
    def get_group_panels(self, group_id: int) -> Set["AtlasPanel"]:
        """Get all panels in a group."""
        return self._groups.get(group_id, set())
    
    def cycle_group_color(self, current_group: int) -> int:
        """Cycle to the next group color. Returns new group_id or -1 for unlinked."""
        if current_group == -1:
            return 0  # First color (red)
        next_group = (current_group + 1) % len(self.COLORS)
        return next_group
    
    @classmethod
    def get_color_name(cls, group_id: int) -> str:
        """Get color name for a group ID."""
        if group_id == -1:
            return "gray"
        return cls.COLORS[group_id % len(cls.COLORS)]
