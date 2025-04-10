import pytest
from controllers.game_manager import GameManager
from models.base import Position, EntityType
from models.plants import Plant
from models.animals import Herbivore, Carnivore

@pytest.mark.integration
class TestGameFeatures:
    
    def test_feature_unlock_progression(self, mock_pygame_init):
        """Test that features unlock in the correct order"""
        manager = GameManager(width=800, height=600)
        
        # Clear entities and reset state
        entity_ids = list(manager.world.entities.keys())
        for entity_id in entity_ids:
            manager.world.remove_entity(entity_id)
        
        # Initially only plants should be unlocked
        assert manager.unlocked_features["plants"] == True
        assert manager.unlocked_features["herbivores"] == False
        assert manager.unlocked_features["carnivores"] == False
        assert manager.unlocked_features["weather"] == False
        
        # Add plants to unlock herbivores
        for i in range(50):
            x, y = i % 10, i // 10
            position = Position(x, y)
            if not manager.world.is_position_occupied(position):
                plant = Plant(manager.world.get_next_entity_id(), position, "cactus")
                manager.world.add_entity(plant)
        
        # Run update to check unlocks
        manager.update()
        
        # Herbivores should be unlocked
        assert manager.unlocked_features["herbivores"] == True
        assert manager.unlocked_features["carnivores"] == False  # Still locked
        
        # Add herbivores to unlock carnivores
        for i in range(20):
            x, y = i % 5 + 15, i // 5
            position = Position(x, y)
            if not manager.world.is_position_occupied(position):
                herb = Herbivore(manager.world.get_next_entity_id(), position)
                manager.world.add_entity(herb)
        
        # Run update to check unlocks
        manager.update()
        
        # Carnivores should be unlocked
        assert manager.unlocked_features["carnivores"] == True
        assert manager.unlocked_features["weather"] == False  # Still locked
        
        # Advance time to unlock weather
        manager.world.time_step = 200
        manager.update()
        
        # Weather should be unlocked
        assert manager.unlocked_features["weather"] == True
    
    def test_achievement_tracking(self, mock_pygame_init):
        """Test that achievements are unlocked correctly"""
        manager = GameManager(width=800, height=600)
        
        # Reset state
        entity_ids = list(manager.world.entities.keys())
        for entity_id in entity_ids:
            manager.world.remove_entity(entity_id)
        
        # Reset achievements
        for achievement in manager.achievements.values():
            achievement["unlocked"] = False
        
        # Initially no achievements should be unlocked
        assert all(not achievement["unlocked"] for achievement in manager.achievements.values())
        
        # Add one plant to trigger first_plant achievement
        position = Position(5, 5)
        plant = Plant(manager.world.get_next_entity_id(), position, "cactus")
        manager.world.add_entity(plant)
        
        # Run update to check achievements
        manager.update()
        
        # first_plant should be unlocked
        assert manager.achievements["first_plant"]["unlocked"] == True
        
        # Add more plants to trigger thriving_ecosystem achievement
        for i in range(100):
            x, y = i % 10, i // 10
            position = Position(x, y)
            if not manager.world.is_position_occupied(position):
                plant = Plant(manager.world.get_next_entity_id(), position, "cactus")
                manager.world.add_entity(plant)
        
        # Run update to check achievements
        manager.update()
        
        # thriving_ecosystem should be unlocked
        assert manager.achievements["thriving_ecosystem"]["unlocked"] == True
        
        # Add herbivores and carnivores to trigger circle_of_life achievement
        herb_pos = Position(15, 15)
        herb = Herbivore(manager.world.get_next_entity_id(), herb_pos)
        manager.world.add_entity(herb)
        
        carn_pos = Position(18, 18)
        carn = Carnivore(manager.world.get_next_entity_id(), carn_pos)
        manager.world.add_entity(carn)
        
        # Run update to check achievements
        manager.update()
        
        # circle_of_life should be unlocked
        assert manager.achievements["circle_of_life"]["unlocked"] == True
    
    def test_tool_usage_based_on_unlocks(self, mock_pygame_init):
        """Test that tools are only usable when features are unlocked"""
        manager = GameManager(width=800, height=600)
        
        # Reset state
        entity_ids = list(manager.world.entities.keys())
        for entity_id in entity_ids:
            manager.world.remove_entity(entity_id)
        
        # Reset unlocks to control test
        manager.unlocked_features = {
            "plants": True,
            "herbivores": False,
            "carnivores": False,
            "weather": False,
        }
        
        # Plants should be usable
        position = Position(5, 5)
        manager.selected_tool = "cactus"
        manager._use_tool(position)
        
        # Should have created a plant
        assert len(manager.world.entities) == 1
        assert list(manager.world.entities.values())[0].entity_type == EntityType.PLANT
        
        # Herbivores should not be usable when locked
        position = Position(10, 10)
        manager.selected_tool = "herbivore"
        manager._use_tool(position)
        
        # Should not have created a herbivore
        assert len(manager.world.entities) == 1
        assert EntityType.HERBIVORE not in [e.entity_type for e in manager.world.entities.values()]
        
        # Unlock herbivores and try again
        manager.unlocked_features["herbivores"] = True
        manager._use_tool(position)
        
        # Now should have created a herbivore
        assert len(manager.world.entities) == 2
        assert EntityType.HERBIVORE in [e.entity_type for e in manager.world.entities.values()]
    
    def test_game_loop_advances_simulation(self, mock_pygame_init, monkeypatch):
        """Test that the game loop properly advances the simulation"""
        manager = GameManager(width=800, height=600)
        
        # Mock pygame events to avoid waiting for user input
        events = []
        monkeypatch.setattr(manager.clock, "tick", lambda rate: None)
        monkeypatch.setattr(manager, "handle_events", lambda: None)
        
        # Mock running flag to exit loop after a few iterations
        iterations = 0
        
        def mock_update():
            nonlocal iterations
            iterations += 1
            if iterations >= 5:
                manager.running = False
            
            # Call the original update
            manager._original_update()
        
        # Store original update and replace with our mock
        manager._original_update = manager.update
        manager.update = mock_update
        
        # Run game loop
        initial_time = manager.world.time_step
        manager.run()
        
        # Time should have advanced
        assert manager.world.time_step > initial_time
        assert iterations == 5  # Should have run 5 iterations
    
    def test_world_reset(self, mock_pygame_init):
        """Test that world reset properly resets the simulation"""
        manager = GameManager(width=800, height=600)
        
        # Add some entities
        for i in range(10):
            position = Position(i, i)
            plant = Plant(manager.world.get_next_entity_id(), position, "cactus")
            manager.world.add_entity(plant)
        
        # Get the initial world state
        initial_entity_count = len(manager.world.entities)
        initial_world_id = id(manager.world)
        initial_time_step = manager.world.time_step
        
        assert initial_entity_count > 0
        
        # Reset world
        manager._reset_world()
        
        # Should be a new world object
        assert id(manager.world) != initial_world_id
        
        # Time step should be reset
        assert manager.world.time_step < initial_time_step
        
        # Entity count should be different
        # Note: initialize() adds some plants by default
        assert len(manager.world.entities) != initial_entity_count 