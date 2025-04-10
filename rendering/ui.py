import pygame as pg
from config import WHITE, GREY, BLUE, RED

class Button:
    """Interactive button for UI"""
    
    def __init__(self, x, y, width, height, text, color=(100, 100, 150), hover_color=(120, 120, 180)):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pg.font.SysFont('Arial', 16)
        self.action = None  # Callback function
        
    def draw(self, surface):
        """Draw the button to the surface"""
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(surface, color, self.rect)
        pg.draw.rect(surface, (50, 50, 50), self.rect, 1)  # Border
        
        # Draw text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        """Handle mouse events on the button"""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
                return True
        return False


class ToolPanel:
    """Panel containing tool buttons"""
    
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.buttons = []
        self.title_font = pg.font.SysFont('Arial', 20)
        self.info_font = pg.font.SysFont('Arial', 14)
        self.selected_tool = None
        self.tool_info = {}  # Tool information for tooltips
        
    def add_button(self, text, tool_id, action=None, info=None):
        """Add a tool button to the panel"""
        # Calculate button position
        margin = 10
        button_width = self.rect.width - margin * 2
        button_height = 30
        
        y_pos = self.rect.y + margin + len(self.buttons) * (button_height + margin)
        
        # Create button
        button = Button(
            self.rect.x + margin, 
            y_pos,
            button_width, 
            button_height,
            text
        )
        button.action = action
        
        # Store the tool ID for selection
        button.tool_id = tool_id
        
        # Store tool information for tooltips
        if info:
            self.tool_info[tool_id] = info
            
        self.buttons.append(button)
        
    def draw(self, surface):
        """Draw the tool panel and buttons"""
        # Draw panel background
        pg.draw.rect(surface, (50, 50, 70), self.rect)
        pg.draw.rect(surface, (30, 30, 50), self.rect, 2)  # Border
        
        # Draw title
        title_surf = self.title_font.render("Tools", True, WHITE)
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
            
            # Highlight selected tool
            if self.selected_tool and button.tool_id == self.selected_tool:
                highlight_rect = pg.Rect(button.rect)
                highlight_rect.inflate_ip(4, 4)
                pg.draw.rect(surface, (255, 215, 0), highlight_rect, 2)  # Gold highlight
        
        # Draw tool information if a tool is selected
        if self.selected_tool and self.selected_tool in self.tool_info:
            info = self.tool_info[self.selected_tool]
            info_y = self.rect.bottom - 60
            
            # Draw info background
            info_rect = pg.Rect(self.rect.x + 10, info_y, self.rect.width - 20, 50)
            pg.draw.rect(surface, (60, 60, 80), info_rect)
            
            # Draw info text
            info_surf = self.info_font.render(info, True, WHITE)
            # Wrap text if needed
            if info_surf.get_width() > info_rect.width - 10:
                # Simple text wrapping - split into two lines
                words = info.split()
                midpoint = len(words) // 2
                line1 = " ".join(words[:midpoint])
                line2 = " ".join(words[midpoint:])
                
                line1_surf = self.info_font.render(line1, True, WHITE)
                line2_surf = self.info_font.render(line2, True, WHITE)
                
                surface.blit(line1_surf, (info_rect.x + 5, info_rect.y + 5))
                surface.blit(line2_surf, (info_rect.x + 5, info_rect.y + 25))
            else:
                surface.blit(info_surf, (info_rect.x + 5, info_rect.y + 15))
    
    def update(self, mouse_pos):
        """Update all buttons based on mouse position"""
        for button in self.buttons:
            button.update(mouse_pos)
            
    def handle_event(self, event):
        """Handle events for all buttons"""
        for button in self.buttons:
            if button.handle_event(event):
                self.selected_tool = button.tool_id
                return True
        return False
    
    def set_selected_tool(self, tool_id):
        """Manually set the selected tool"""
        self.selected_tool = tool_id


class AchievementPanel:
    """Panel displaying achievements"""
    
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.title_font = pg.font.SysFont('Arial', 20)
        self.item_font = pg.font.SysFont('Arial', 14)
        self.scroll_offset = 0
        self.max_visible_items = 8
        self.achievements = {}  # Will store achievement data
        
    def set_achievements(self, achievements):
        """Set the achievements to display"""
        self.achievements = achievements
        
    def draw(self, surface):
        """Draw the achievement panel"""
        # Draw panel background
        pg.draw.rect(surface, (50, 50, 70), self.rect)
        pg.draw.rect(surface, (30, 30, 50), self.rect, 2)  # Border
        
        # Draw title
        title_surf = self.title_font.render("Achievements", True, WHITE)
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.y + 10))
        surface.blit(title_surf, title_rect)
        
        # Draw achievements
        item_height = 25
        start_y = self.rect.y + 40  # Below title
        
        # Display scrollbar if needed
        achievement_count = len(self.achievements)
        if achievement_count > self.max_visible_items:
            scrollbar_height = self.rect.height - 50
            visible_ratio = min(1.0, self.max_visible_items / achievement_count)
            thumb_height = max(20, scrollbar_height * visible_ratio)
            
            # Draw scrollbar background
            scrollbar_rect = pg.Rect(self.rect.right - 15, start_y, 10, scrollbar_height)
            pg.draw.rect(surface, (30, 30, 40), scrollbar_rect)
            
            # Draw scrollbar thumb
            thumb_y = start_y + (scrollbar_height - thumb_height) * (self.scroll_offset / max(1, achievement_count - self.max_visible_items))
            thumb_rect = pg.Rect(self.rect.right - 15, thumb_y, 10, thumb_height)
            pg.draw.rect(surface, (100, 100, 120), thumb_rect)
        
        # Draw achievement items
        visible_achievements = list(self.achievements.items())[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        
        for i, (key, achievement) in enumerate(visible_achievements):
            item_y = start_y + i * item_height
            item_rect = pg.Rect(self.rect.x + 10, item_y, self.rect.width - 30, item_height)
            
            # Draw item background
            if achievement["unlocked"]:
                # Gold for unlocked achievements
                pg.draw.rect(surface, (70, 60, 30), item_rect)
            else:
                # Gray for locked achievements
                pg.draw.rect(surface, (60, 60, 65), item_rect)
            
            # Draw achievement description
            text = achievement["description"]
            if not achievement["unlocked"]:
                text = "???" + text[3:]  # Hide first part of locked achievements
                
            text_surf = self.item_font.render(text, True, WHITE)
            surface.blit(text_surf, (item_rect.x + 5, item_rect.y + 4))
    
    def handle_event(self, event):
        """Handle scrolling events"""
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    return True
                elif event.button == 5:  # Scroll down
                    self.scroll_offset = min(
                        max(0, len(self.achievements) - self.max_visible_items),
                        self.scroll_offset + 1
                    )
                    return True
        return False


class UIManager:
    """Manages all UI elements"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create tool panel on the right side
        tool_panel_width = 200
        self.tool_panel = ToolPanel(
            screen_width - tool_panel_width - 10,
            10,
            tool_panel_width,
            300
        )
        
        # Create achievement panel below tool panel
        self.achievement_panel = AchievementPanel(
            screen_width - tool_panel_width - 10,
            320,
            tool_panel_width,
            270
        )
        
        # Initialize other UI elements as needed
        self.show_achievements = True
        
    def initialize_tools(self, available_tools, select_tool_callback):
        """Initialize tool buttons based on available tools"""
        # Clear existing buttons
        self.tool_panel.buttons = []
        
        # Add plant tools
        if "plants" in available_tools and available_tools["plants"]:
            self.tool_panel.add_button("Cactus", "cactus", 
                                      lambda: select_tool_callback("cactus"),
                                      "Drought-resistant, slow growing")
            
            self.tool_panel.add_button("Desert Grass", "desert_grass", 
                                      lambda: select_tool_callback("desert_grass"),
                                      "Fast growing, needs more water")
            
            self.tool_panel.add_button("Succulent", "succulent", 
                                      lambda: select_tool_callback("succulent"),
                                      "Stores water, moderate growth")
        
        # Add water tool
        if "water" in available_tools and available_tools["water"]:
            self.tool_panel.add_button("Water Source", "water", 
                                      lambda: select_tool_callback("water"),
                                      "Creates permanent water source")
        
        # Add animal tools if available
        if "herbivores" in available_tools and available_tools["herbivores"]:
            self.tool_panel.add_button("Herbivore", "herbivore", 
                                      lambda: select_tool_callback("herbivore"),
                                      "Plant eater, needs water")
        
        if "carnivores" in available_tools and available_tools["carnivores"]:
            self.tool_panel.add_button("Carnivore", "carnivore", 
                                      lambda: select_tool_callback("carnivore"),
                                      "Hunts herbivores, needs water")
        
        # Add weather tool if available
        if "weather" in available_tools and available_tools["weather"]:
            self.tool_panel.add_button("Create Rain", "rain", 
                                      lambda: select_tool_callback("rain"),
                                      "Creates temporary rainfall")
    
    def update_achievements(self, achievements):
        """Update the achievement panel with current achievements"""
        self.achievement_panel.set_achievements(achievements)
    
    def set_selected_tool(self, tool_id):
        """Set the currently selected tool"""
        self.tool_panel.set_selected_tool(tool_id)
    
    def draw(self, surface):
        """Draw all UI elements"""
        self.tool_panel.draw(surface)
        
        if self.show_achievements:
            self.achievement_panel.draw(surface)
    
    def update(self, mouse_pos):
        """Update UI element states"""
        self.tool_panel.update(mouse_pos)
    
    def handle_event(self, event):
        """Handle events for all UI elements"""
        # Handle tool panel events
        if self.tool_panel.handle_event(event):
            return True
        
        # Handle achievement panel events if shown
        if self.show_achievements and self.achievement_panel.handle_event(event):
            return True
            
        return False
        
    def toggle_achievements(self):
        """Toggle achievement panel visibility"""
        self.show_achievements = not self.show_achievements 