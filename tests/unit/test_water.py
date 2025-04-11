import pytest
import numpy as np
from models.base import Position, EntityType
from models.water import Water

@pytest.mark.unit
class TestWater:
    
    def test_water_initialization(self):
        """Test that water entity initializes correctly"""
        water = Water(entity_id=1, position=Position(5, 5), size=2.0)
        
        # Check basic properties
        assert water.id == 1
        assert water.position.x == 5
        assert water.position.y == 5
        assert water.entity_type == EntityType.WATER
        assert water.size == 2.0
        assert water.evaporation_rate > 0
        assert water.diffusion_rate > 0
    
    def test_water_evaporation(self, simple_world):
        """Test that water evaporates over time based on temperature"""
        world = simple_world
        x, y = 5, 5
        
        # Set extreme temperature values for clear difference
        world.environment.temperature[x, y] = 1.0  # Very hot
        
        # Create a water entity
        water = Water(world.get_next_entity_id(), Position(x, y), size=2.0)
        initial_size = water.size
        world.add_entity(water)
        
        # Run update
        water.update(world)
        
        # Size should decrease due to evaporation
        hot_evaporation = initial_size - water.size
        assert hot_evaporation > 0, "Water should evaporate in hot conditions"
        
        # Test with much lower temperature
        world.environment.temperature[x, y] = 0.1  # Very cool
        
        # Reset water size
        water.size = initial_size
        
        # Run update again
        water.update(world)
        
        # Should evaporate less than before
        cool_evaporation = initial_size - water.size
        
        # Print the values for debugging
        print(f"Hot evaporation: {hot_evaporation}, Cool evaporation: {cool_evaporation}")
        
        assert cool_evaporation < hot_evaporation, "Evaporation rate should be lower in cooler conditions"
    
    def test_water_diffusion(self, simple_world):
        """Test that water diffuses moisture to surrounding cells"""
        world = simple_world
        x, y = 10, 10
        
        # Clear all moisture
        world.environment.moisture[:] = 0
        
        # Create a water entity
        water = Water(world.get_next_entity_id(), Position(x, y), size=3.0)
        world.add_entity(water)
        
        # Run update
        water.update(world)
        
        # Check moisture at and around water source
        assert world.environment.moisture[x, y] > 0, "Water position should have moisture"
        
        # Check surrounding cells - at least some should have moisture
        surrounding_moisture = False
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue  # Skip center
                
                nx, ny = x + dx, y + dy
                if 0 <= nx < world.width and 0 <= ny < world.height:
                    if world.environment.moisture[nx, ny] > 0:
                        surrounding_moisture = True
                        break
            if surrounding_moisture:
                break
        
        assert surrounding_moisture, "Water should diffuse moisture to surrounding cells"
        
        # Further cells should have less moisture than closer ones
        if world.environment.moisture[x+1, y] > 0 and world.environment.moisture[x+2, y] > 0:
            assert world.environment.moisture[x+1, y] > world.environment.moisture[x+2, y], \
                "Closer cells should have more moisture than farther ones"
    
    def test_water_drying_up(self, simple_world):
        """Test that water entities are removed when they dry up"""
        world = simple_world
        x, y = 5, 5
        
        # Set high temperature for faster evaporation
        world.environment.temperature[:] = 1.0
        
        # Create a small water entity that will dry up quickly
        water = Water(world.get_next_entity_id(), Position(x, y), size=0.2)  # Very small
        water_id = water.id
        world.add_entity(water)
        
        # Run updates until it dries up or timeout
        for _ in range(10):  # Max 10 updates
            water.update(world)
            if water_id not in world.entities:
                break
        
        # Water entity should be removed
        assert water_id not in world.entities, "Small water entity should dry up and be removed"
    
    def test_water_replenishment_from_rain(self, simple_world):
        """Test that water is replenished by rainfall"""
        world = simple_world
        x, y = 5, 5
        
        # Set high rainfall in this area
        world.environment.moisture[x, y] = 0.9  # Heavy rain
        
        # Create a water entity
        water = Water(world.get_next_entity_id(), Position(x, y), size=1.0)
        initial_size = water.size
        world.add_entity(water)
        
        # Run update
        water.update(world)
        
        # Size should increase due to rainfall
        assert water.size > initial_size, "Water should increase in size during rainfall"
        
        # Test with lower rainfall
        world.environment.moisture[x, y] = 0.4  # Light rain
        
        # Reset water size
        water.size = initial_size
        
        # Run update again
        water.update(world)
        
        # Should not increase since moisture is below 0.7 threshold
        assert water.size <= initial_size, "Water should not increase with light rainfall"
    
    def test_animals_drinking_from_water(self, simple_world):
        """Test that animals can drink from water entities"""
        world = simple_world
        x, y = 5, 5
        
        # Create a water entity
        water = Water(world.get_next_entity_id(), Position(x, y), size=3.0)
        world.add_entity(water)
        
        # Create a herbivore with low water at the same position
        from models.animals import Herbivore
        herbivore = Herbivore(world.get_next_entity_id(), Position(x, y))
        herbivore.water = 20.0  # Low water, needs to drink
        world.add_entity(herbivore)
        
        # Get initial values
        initial_water_level = herbivore.water
        initial_water_size = water.size
        
        # Animal drinking is implemented in the _drink_water method
        herbivore._drink_water(world, water)
        
        # Animal water should increase
        assert herbivore.water > initial_water_level, "Animal should gain water from drinking"
        
        # Water entity size should decrease
        assert water.size < initial_water_size, "Water size should decrease when animals drink" 