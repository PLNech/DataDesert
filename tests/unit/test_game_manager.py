import pytest
import pygame as pg
from controllers.game_manager import GameManager
from models.base import Position, EntityType

@pytest.mark.unit
class TestGameManager:
    
    def test_game_manager_initialization(self, mock_pygame_init):
        """Test game manager initialization"""
        manager = GameManager(width=800, height=600)
        
        # Check basic setup
        assert manager.running == True
        assert manager.paused == False
        assert manager.world is not None
        assert manager.analytics is not None
        assert manager.renderer is not None
        
        # Check unlocked features
        assert manager.unlocked_features["plants"] == True  # Plants should be unlocked by default
        assert manager.unlocked_features["herbivores"] == False
        assert manager.unlocked_features["carnivores"] == False
        assert manager.unlocked_features["weather"] == False
        
        # Check achievements
        assert isinstance(manager.achievements, dict)
        assert "first_plant" in manager.achievements
        assert manager.achievements["first_plant"]["unlocked"] == False
        
        # Check default tool
        assert manager.selected_tool == "cactus"
    
    def test_update_method_when_paused(self, mock_pygame_init, monkeypatch):
        """Test update method when game is paused"""
        manager = GameManager(width=800, height=600)
        manager.paused = True
        
        # Track method calls
        called = []
        monkeypatch.setattr(manager.world, "update", lambda: called.append("world_update"))
        monkeypatch.setattr(manager.analytics, "update", lambda: called.append("analytics_update"))
        monkeypatch.setattr(manager, "_check_feature_unlocks", lambda: called.append("feature_unlocks"))
        monkeypatch.setattr(manager, "_check_achievements", lambda: called.append("achievements"))
        
        # Call update
        manager.update()
        
        # Nothing should be called when paused
        assert len(called) == 0
    
    def test_update_method_when_running(self, mock_pygame_init, monkeypatch):
        """Test update method when game is running"""
        manager = GameManager(width=800, height=600)
        manager.paused = False
        
        # Track method calls
        called = []
        monkeypatch.setattr(manager.world, "update", lambda: called.append("world_update"))
        monkeypatch.setattr(manager.analytics, "update", lambda: called.append("analytics_update"))
        monkeypatch.setattr(manager, "_check_feature_unlocks", lambda: called.append("feature_unlocks"))
        monkeypatch.setattr(manager, "_check_achievements", lambda: called.append("achievements"))
        
        # Call update
        manager.update()
        
        # All methods should be called when running
        assert "world_update" in called
        assert "analytics_update" in called
        assert "feature_unlocks" in called
        assert "achievements" in called
    
    def test_render_method(self, mock_pygame_init, monkeypatch):
        """Test render method"""
        manager = GameManager(width=800, height=600)
        
        # Track render calls
        called = []
        monkeypatch.setattr(manager.renderer, "render", 
                           lambda world, analytics: called.append((world, analytics)))
        
        # Call render
        manager.render()
        
        # Renderer should be called with correct arguments
        assert len(called) == 1
        assert called[0][0] == manager.world
        assert called[0][1] == manager.analytics
    
    def test_pause_toggle(self, mock_pygame_init):
        """Test pause toggle functionality"""
        manager = GameManager(width=800, height=600)
        
        # Create mock space key event
        class MockEvent:
            def __init__(self, key):
                self.key = key
        
        space_event = MockEvent(pg.K_SPACE)
        
        # Initial state
        initial_pause = manager.paused
        
        # Handle space key event
        manager._handle_key_event(space_event)
        
        # Pause state should toggle
        assert manager.paused != initial_pause
        
        # Toggle back
        manager._handle_key_event(space_event)
        assert manager.paused == initial_pause
    
    def test_tool_selection(self, mock_pygame_init):
        """Test tool selection via keyboard"""
        manager = GameManager(width=800, height=600)
        
        # Create mock key events
        class MockEvent:
            def __init__(self, key):
                self.key = key
        
        # Test tool selection
        cactus_event = MockEvent(pg.K_1)
        manager._handle_key_event(cactus_event)
        assert manager.selected_tool == "cactus"
        
        grass_event = MockEvent(pg.K_2)
        manager._handle_key_event(grass_event)
        assert manager.selected_tool == "desert_grass"
        
        succulent_event = MockEvent(pg.K_3)
        manager._handle_key_event(succulent_event)
        assert manager.selected_tool == "succulent"
    
    def test_use_plant_tool(self, mock_pygame_init):
        """Test using the plant tool"""
        manager = GameManager(width=800, height=600)
        
        # Clear entities
        entity_ids = list(manager.world.entities.keys())
        for entity_id in entity_ids:
            manager.world.remove_entity(entity_id)
            
        # Set tool and use it
        manager.selected_tool = "cactus"
        position = Position(5, 5)
        
        # Verify position is empty
        assert not manager.world.is_position_occupied(position)
        
        # Use tool
        manager._use_tool(position)
        
        # Should create a plant
        assert manager.world.is_position_occupied(position)
        entity = manager.world.get_entity_at(position)
        assert entity is not None
        assert entity.entity_type == EntityType.PLANT
        assert entity.species.name.lower() == "cactus" 