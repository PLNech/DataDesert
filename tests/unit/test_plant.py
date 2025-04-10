import pytest
import numpy as np
from models.base import Position, EntityType
from models.plants import Plant, PLANT_SPECIES, species_by_name

@pytest.mark.unit
class TestPlant:
    
    def test_plant_initialization(self):
        """Test that plants initialize correctly with proper attributes"""
        # Create a plant with each species
        for species_name in PLANT_SPECIES.keys():
            plant = Plant(entity_id=1, position=Position(5, 5), species_name=species_name)
            
            # Check basic properties
            assert plant.id == 1
            assert plant.position.x == 5
            assert plant.position.y == 5
            assert plant.entity_type == EntityType.PLANT
            # Make sure either the lowercase name matches or the raw name matches
            assert plant.species.name.lower().replace(' ', '_') == species_name or plant.species.name == species_name
            assert plant.size == 1.0
            assert plant.water_stored == 1.0
            assert plant.health == 1.0
            assert plant.ready_to_seed is False
    
    def test_species_lookup_by_name(self):
        """Test that species can be looked up by name"""
        for key, props in PLANT_SPECIES.items():
            # Test lookup by key
            plant1 = Plant(entity_id=1, position=Position(0, 0), species_name=key)
            # Test lookup by name
            plant2 = Plant(entity_id=2, position=Position(1, 1), species_name=props.name)
            
            assert plant1.species == props
            assert plant2.species == props
    
    def test_invalid_species_name(self):
        """Test that invalid species names raise exceptions"""
        with pytest.raises(ValueError):
            Plant(entity_id=1, position=Position(0, 0), species_name="invalid_species")
    
    def test_plant_growth(self, simple_world):
        """Test that plants grow when conditions are favorable"""
        # Setup a world with good conditions
        world = simple_world
        x, y = 5, 5
        world.environment.moisture[x, y] = 1.0  # Max moisture
        world.environment.nutrients[x, y] = 1.0  # Max nutrients
        
        # Create a plant
        cactus = Plant(world.get_next_entity_id(), Position(x, y), "cactus")
        initial_size = cactus.size
        world.add_entity(cactus)
        
        # Run one update cycle
        cactus.update(world)
        
        # Verify the plant grew
        assert cactus.size > initial_size, "Plant should grow in favorable conditions"
        
        # Verify resources were consumed
        assert world.environment.moisture[x, y] < 1.0, "Plant should consume moisture"
        assert world.environment.nutrients[x, y] < 1.0, "Plant should consume nutrients"
    
    def test_plant_death_from_drought(self, simple_world):
        """Test that plants die when they run out of water"""
        world = simple_world
        x, y = 5, 5
        
        # Create a plant with minimal health in dry conditions
        cactus = Plant(world.get_next_entity_id(), Position(x, y), "cactus")
        cactus.health = 1.0  # Minimum health before death
        cactus.water_stored = 0.0  # No water stored
        world.add_entity(cactus)
        
        # Get the entity ID for later verification
        entity_id = cactus.id
        
        # Run update cycle - plant should die
        cactus.update(world)
        
        # Verify plant was removed from world
        assert entity_id not in world.entities, "Plant should be removed from world when it dies"
        
        # Verify nutrients were returned to soil
        assert world.environment.nutrients[x, y] > 0.0, "Dead plant should return nutrients to soil"
    
    def test_plant_reproduction(self, simple_world):
        """Test that plants reproduce when conditions are met"""
        world = simple_world
        x, y = 10, 10
        
        # Add moisture and nutrients
        world.environment.moisture[x-3:x+4, y-3:y+4] = 1.0
        world.environment.nutrients[x-3:x+4, y-3:y+4] = 1.0
        
        # Create a mature plant ready to seed
        plant = Plant(world.get_next_entity_id(), Position(x, y), "desert_grass")
        plant.size = PLANT_SPECIES["desert_grass"].max_size * 0.8  # Mature enough to seed
        plant.ready_to_seed = True
        world.add_entity(plant)
        
        # Attempt reproduction
        new_plant = plant.try_reproduce(world)
        
        # Verify reproduction results
        assert new_plant is not None, "Plant should create offspring"
        assert new_plant.id != plant.id, "New plant should have unique ID"
        assert new_plant.position.x != x or new_plant.position.y != y, "New plant should be at different position"
        assert new_plant.species.name == plant.species.name, "New plant should have same species"
        assert plant.ready_to_seed is False, "Parent plant should reset ready_to_seed flag"
    
    def test_reproduction_impossible_when_occupied(self, simple_world, monkeypatch):
        """Test that plants don't reproduce when all surrounding positions are occupied"""
        world = simple_world
        x, y = 10, 10
        
        # Create a mature plant ready to seed
        plant = Plant(world.get_next_entity_id(), Position(x, y), "succulent")
        plant.size = PLANT_SPECIES["succulent"].max_size * 0.8
        plant.ready_to_seed = True
        world.add_entity(plant)
        
        # Block all surrounding positions
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue  # Skip the center
                nx, ny = x + dx, y + dy
                blocker = Plant(world.get_next_entity_id(), Position(nx, ny), "succulent")
                world.add_entity(blocker)
        
        # Attempt reproduction with mocked random to always try adjacent cells
        monkeypatch.setattr(np.random, "random", lambda: 0.1)  # Try to seed in small radius
        new_plant = plant.try_reproduce(world)
        
        # Verify no reproduction occurred
        assert new_plant is None, "Plant should not reproduce when all positions are occupied"
        assert plant.ready_to_seed is False, "Plant should still reset ready_to_seed flag"
    
    def test_different_species_characteristics(self, simple_world):
        """Test that different plant species behave according to their traits"""
        world = simple_world
        x, y = 5, 5
        
        # Add some moisture and nutrients
        world.environment.moisture[x, y] = 0.5
        world.environment.nutrients[x, y] = 0.5
        
        # Create plants of different species
        cactus = Plant(world.get_next_entity_id(), Position(x, y), "cactus")
        world.add_entity(cactus)
        
        # Move to another position for the second plant
        x2, y2 = 10, 10
        world.environment.moisture[x2, y2] = 0.5
        world.environment.nutrients[x2, y2] = 0.5
        
        desert_grass = Plant(world.get_next_entity_id(), Position(x2, y2), "desert_grass")
        world.add_entity(desert_grass)
        
        # Run several update cycles
        for _ in range(10):
            if cactus.id in world.entities:
                cactus.update(world)
            if desert_grass.id in world.entities:
                desert_grass.update(world)
        
        # Verify different growth patterns based on species characteristics
        if cactus.id in world.entities and desert_grass.id in world.entities:
            # Cactus should have more water stored due to drought resistance
            assert cactus.water_stored >= desert_grass.water_stored, "Cactus should store water better"
            
            # Desert grass should grow faster but might have less health
            if desert_grass.size > cactus.size:
                assert desert_grass.health <= cactus.health, "Faster growth should come at cost of health" 