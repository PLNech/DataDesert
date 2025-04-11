import pygame as pg
from typing import List, Dict, Tuple, Callable, Optional
from .tabs import TabButton
from .tool_panel import ToolPanel
from .achievement_panel import AchievementPanel
from .analytics_panel import AnalyticsPanel
from .control_panel import ControlPanel
from .cell_info_panel import CellInfoPanel
import pygame_gui as pg_gui
import os

class UIManager:
    """Manages all UI elements and tabbed interface"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize pygame_gui manager with desert theme
        # Always use absolute path for theme loading
        theme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                'assets', 'themes', 'desert_theme.json')
        
        # Check if theme file exists, otherwise use default theme
        if os.path.exists(theme_path):
            self.manager = pg_gui.UIManager((screen_width, screen_height), theme_path)
        else:
            print(f"Warning: Theme file not found at {theme_path}, using default theme")
            self.manager = pg_gui.UIManager((screen_width, screen_height))
        
        # Calculate panel dimensions - increased sizes
        sidebar_width = 280  # Increased from 240
        tab_height = 40      # Increased from 30
        control_height = 160 # Increased from 130
        cell_info_height = 200 # Increased from 180
        
        # Create UI rectangles
        self.sidebar_rect = pg.Rect(
            screen_width - sidebar_width, 
            0, 
            sidebar_width, 
            screen_height
        )
        
        self.tab_bar_rect = pg.Rect(
            screen_width - sidebar_width,
            0,
            sidebar_width,
            tab_height
        )
        
        self.tab_content_rect = pg.Rect(
            screen_width - sidebar_width,
            tab_height,
            sidebar_width,
            screen_height - tab_height - control_height - cell_info_height
        )
        
        self.control_rect = pg.Rect(
            screen_width - sidebar_width,
            screen_height - control_height - cell_info_height,
            sidebar_width,
            control_height
        )
        
        self.cell_info_rect = pg.Rect(
            screen_width - sidebar_width,
            screen_height - cell_info_height,
            sidebar_width,
            cell_info_height
        )
        
        # Initialize tabs and panels
        self.setup_tabs()
        self.setup_panels()
        
        # Active tool tracking
        self.active_tool = None
        
        # Cell selection
        self.selected_cell = None
    
    def setup_tabs(self) -> None:
        """Initialize tab buttons"""
        tab_width = self.tab_bar_rect.width // 3
        tab_height = self.tab_bar_rect.height
        
        self.tabs = []
        tab_infos = [
            ("Tools", self.show_tools_tab),
            ("Achievements", self.show_achievements_tab),
            ("Analytics", self.show_analytics_tab)
        ]
        
        for i, (name, callback) in enumerate(tab_infos):
            tab_rect = pg.Rect(
                self.tab_bar_rect.left + i * tab_width,
                self.tab_bar_rect.top,
                tab_width,
                tab_height
            )
            
            tab_button = TabButton(tab_rect, name, callback)
            self.tabs.append(tab_button)
        
        # Set first tab as active by default
        self.active_tab_index = 0
        self.tabs[self.active_tab_index].set_selected(True)
    
    def setup_panels(self) -> None:
        """Initialize UI panels"""
        # Create tabbed panels
        self.tool_panel = ToolPanel(self.tab_content_rect)
        self.achievement_panel = AchievementPanel(self.tab_content_rect)
        self.analytics_panel = AnalyticsPanel(self.tab_content_rect)
        
        # Create fixed panels
        self.control_panel = ControlPanel(self.control_rect)
        self.cell_info_panel = CellInfoPanel(self.cell_info_rect)
        
        # Set initial visibility
        self.tool_panel.set_visible(True)
        self.achievement_panel.set_visible(False)
        self.analytics_panel.set_visible(False)
    
    def draw(self, surface: pg.Surface) -> None:
        """Draw all UI elements"""
        # Draw sidebar background
        pg.draw.rect(surface, (60, 60, 60), self.sidebar_rect)
        
        # Draw tabs
        for tab in self.tabs:
            tab.draw(surface)
        
        # Draw active content panel
        self.tool_panel.draw(surface)
        self.achievement_panel.draw(surface)
        self.analytics_panel.draw(surface)
        
        # Draw fixed panels
        self.control_panel.draw(surface)
        self.cell_info_panel.draw(surface)
    
    def handle_event(self, event: pg.event.Event) -> bool:
        """Process events for all UI elements"""
        # Handle tab buttons
        for i, tab in enumerate(self.tabs):
            if tab.handle_event(event):
                self.set_active_tab(i)
                return f"tab_{i}"
        
        # Handle content panels
        if self.tool_panel.visible:
            tool_result = self.tool_panel.handle_event(event)
            if tool_result and hasattr(self.tool_panel, 'selected_tool'):
                return f"tool_{self.tool_panel.selected_tool}"
        
        if self.achievement_panel.visible and self.achievement_panel.handle_event(event):
            return "achievement_panel"
            
        if self.analytics_panel.visible and self.analytics_panel.handle_event(event):
            return "analytics_panel"
        
        # Handle fixed panels
        if self.control_panel.handle_event(event):
            # Find which control was clicked if possible
            for button in self.control_panel.buttons:
                if hasattr(button, 'control_id') and button.rect.collidepoint(event.pos):
                    return f"control_{button.control_id}"
            return "control_panel"
            
        if self.cell_info_panel.handle_event(event):
            return "cell_info_panel"
        
        return False
    
    def set_active_tab(self, index: int) -> None:
        """Set the active tab by index"""
        if 0 <= index < len(self.tabs):
            # Deselect all tabs
            for tab in self.tabs:
                tab.set_selected(False)
            
            # Select the active tab
            self.tabs[index].set_selected(True)
            self.active_tab_index = index
            
            # Update panel visibility
            self.tool_panel.set_visible(index == 0)
            self.achievement_panel.set_visible(index == 1)
            self.analytics_panel.set_visible(index == 2)
    
    def show_tools_tab(self) -> None:
        """Callback for tools tab"""
        self.set_active_tab(0)
    
    def show_achievements_tab(self) -> None:
        """Callback for achievements tab"""
        self.set_active_tab(1)
    
    def show_analytics_tab(self) -> None:
        """Callback for analytics tab"""
        self.set_active_tab(2)
    
    def update_cell_info(self, entity, position, moisture, nutrients) -> None:
        """Update the cell info panel with new information"""
        self.cell_info_panel.update_info(entity, position, moisture, nutrients)
    
    def update_analytics(self, metrics: Dict[str, float]) -> None:
        """Update analytics panel with new metrics"""
        self.analytics_panel.update_metrics(metrics)
    
    def select_cell(self, cell_pos: Tuple[int, int]) -> None:
        """Handle cell selection in the game grid"""
        self.selected_cell = cell_pos
        # TODO Further logic must obtain entity/environment info and update the cell info panel
    
    def resize(self, screen_width: int, screen_height: int) -> None:
        """Recalculate UI layout when screen is resized"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Recalculate panel dimensions
        sidebar_width = 280
        tab_height = 40
        control_height = 160
        cell_info_height = 200
        
        # Update UI rectangles
        self.sidebar_rect = pg.Rect(
            screen_width - sidebar_width, 
            0, 
            sidebar_width, 
            screen_height
        )
        
        self.tab_bar_rect = pg.Rect(
            screen_width - sidebar_width,
            0,
            sidebar_width,
            tab_height
        )
        
        self.tab_content_rect = pg.Rect(
            screen_width - sidebar_width,
            tab_height,
            sidebar_width,
            screen_height - tab_height - control_height - cell_info_height
        )
        
        self.control_rect = pg.Rect(
            screen_width - sidebar_width,
            screen_height - control_height - cell_info_height,
            sidebar_width,
            control_height
        )
        
        self.cell_info_rect = pg.Rect(
            screen_width - sidebar_width,
            screen_height - cell_info_height,
            sidebar_width,
            cell_info_height
        )
        
        # Update panel rects
        self.tool_panel.rect = self.tab_content_rect
        self.achievement_panel.rect = self.tab_content_rect
        self.analytics_panel.rect = self.tab_content_rect
        self.control_panel.rect = self.control_rect
        self.cell_info_panel.rect = self.cell_info_rect
        
        # Recalculate tabs
        tab_width = self.tab_bar_rect.width // 3
        for i, tab in enumerate(self.tabs):
            tab.rect = pg.Rect(
                self.tab_bar_rect.left + i * tab_width,
                self.tab_bar_rect.top,
                tab_width,
                tab_height
            )
        
        # Reinitialize buttons for each panel
        self.tool_panel.setup_buttons()
        self.control_panel.setup_buttons()
        
        # Update graph rect in analytics panel
        self.analytics_panel.graph_rect = pg.Rect(
            self.tab_content_rect.left + 10, 
            self.tab_content_rect.top + 30, 
            self.tab_content_rect.width - 20, 
            self.tab_content_rect.height - 40
        )
    
    def add_tool(self, text: str, tool_id: str, callback: Callable, info: Optional[str] = None) -> None:
        """Add a tool button to the tool panel"""
        self.tool_panel.add_button(text, tool_id, callback, info)
    
    def set_selected_tool(self, tool_id: str) -> None:
        """Set the currently selected tool"""
        self.tool_panel.set_selected_tool(tool_id)