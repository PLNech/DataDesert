import pytest
import numpy as np
from models.base import Position, EntityType
from models.plants import Plant, PLANT_SPECIES
from models.animals import Herbivore, Carnivore
from simulation.world import World

@pytest.mark.unit
class TestWorld:
    
    def test_world_initialization(self):
        """Test that world initializes correctly"""
        world = World(width=30, height=25)
        
        # Check dimensions
        assert world.width == 30
        assert world.height == 25
        
        # Check entity storage initialization
        assert len(world.entities) == 0
        assert len(world.entity_grid) == 0
        assert world.next_entity_id == 1
        
        # Check environment setup
        assert world.environment is not None
        assert world.environment.width == 30
        assert world.environment.height == 25
        
        # Check metrics initialization
        assert "time" in world.metrics
        assert "plant_count" in world.metrics
        assert "herbivore_count" in world.metrics
        assert "carnivore_count" in world.metrics
        assert world.time_step == 0
    
    def test_entity_id_generation(self):
        """Test that entity IDs increment correctly"""
        world = World(width=10, height=10)
        
        # Get several IDs
        id1 = world.get_next_entity_id()
        id2 = world.get_next_entity_id()
        id3 = world.get_next_entity_id()
        
        # IDs should be unique and sequential
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
    
    def test_add_and_remove_entity(self):
        """Test adding and removing entities"""
        world = World(width=10, height=10)
        
        # Create and add plant
        plant = Plant(world.get_next_entity_id(), Position(5, 5), "cactus")
        world.add_entity(plant)
        
        # Entity should be stored in world
        assert plant.id in world.entities
        assert (plant.position.x, plant.position.y) in world.entity_grid
        assert world.entity_grid[(plant.position.x, plant.position.y)] == plant.id
        
        # Remove entity
        world.remove_entity(plant.id)
        
        # Entity should be removed from world
        assert plant.id not in world.entities
        assert (plant.position.x, plant.position.y) not in world.entity_grid
    
    def test_is_position_occupied(self):
        """Test position occupation checking"""
        world = World(width=10, height=10)
        
        # Create and add plant
        plant = Plant(world.get_next_entity_id(), Position(5, 5), "cactus")
        world.add_entity(plant)
        
        # Position should be occupied
        assert world.is_position_occupied(Position(5, 5))
        
        # Another position should not be occupied
        assert not world.is_position_occupied(Position(6, 6))
    
    def test_get_entity_at(self):
        """Test retrieving entity at position"""
        world = World(width=10, height=10)
        
        # Create and add entity
        plant = Plant(world.get_next_entity_id(), Position(5, 5), "cactus")
        world.add_entity(plant)
        
        # Should retrieve correct entity
        entity = world.get_entity_at(Position(5, 5))
        assert entity is not None
        assert entity.id == plant.id
        assert entity.entity_type == EntityType.PLANT
        
        # Should return None for empty position
        assert world.get_entity_at(Position(6, 6)) is None
    
    def test_move_entity(self):
        """Test entity movement"""
        world = World(width=10, height=10)
        
        # Create and add entity
        animal = Herbivore(world.get_next_entity_id(), Position(5, 5))
        world.add_entity(animal)
        
        # Move entity
        world.move_entity(animal.id, Position(6, 6))
        
        # Entity should be at new position
        assert not world.is_position_occupied(Position(5, 5))
        assert world.is_position_occupied(Position(6, 6))
        assert world.get_entity_at(Position(6, 6)).id == animal.id
        assert animal.position.x == 6
        assert animal.position.y == 6
    
    def test_get_entities_in_radius(self):
        """Test retrieving entities within radius"""
        world = World(width=20, height=20)
        
        # Add entities at different positions
        center_x, center_y = 10, 10
        
        # Create center entity
        center_plant = Plant(world.get_next_entity_id(), Position(center_x, center_y), "cactus")
        world.add_entity(center_plant)
        
        # Create entities at different distances
        near_plant = Plant(world.get_next_entity_id(), Position(center_x + 1, center_y), "desert_grass")
        world.add_entity(near_plant)
        
        far_plant = Plant(world.get_next_entity_id(), Position(center_x + 5, center_y + 5), "succulent")
        world.add_entity(far_plant)
        
        herbivore = Herbivore(world.get_next_entity_id(), Position(center_x, center_y - 2))
        world.add_entity(herbivore)
        
        # Test radius 1 (should find center_plant and near_plant)
        entities_r1 = world.get_entities_in_radius(Position(center_x, center_y), 1)
        assert len(entities_r1) == 2
        assert center_plant.id in [e.id for e in entities_r1]
        assert near_plant.id in [e.id for e in entities_r1]
        
        # Test radius 3 (should find center_plant, near_plant, and herbivore, but not far_plant)
        entities_r3 = world.get_entities_in_radius(Position(center_x, center_y), 3)
        assert len(entities_r3) == 3
        assert center_plant.id in [e.id for e in entities_r3]
        assert near_plant.id in [e.id for e in entities_r3]
        assert herbivore.id in [e.id for e in entities_r3]
        assert far_plant.id not in [e.id for e in entities_r3]
        
        # Test with entity type filter (just plants)
        entities_plants = world.get_entities_in_radius(Position(center_x, center_y), 3, EntityType.PLANT)
        assert len(entities_plants) == 2
        assert all(e.entity_type == EntityType.PLANT for e in entities_plants)
    
    def test_environment_interaction(self):
        """Test world environment interaction methods"""
        world = World(width=10, height=10)
        pos = Position(5, 5)
        
        # Set known values
        world.environment.moisture[pos.x, pos.y] = 0.5
        world.environment.nutrients[pos.x, pos.y] = 0.5
        
        # Test getters
        assert world.get_moisture(pos) == 0.5
        assert world.get_nutrients(pos) == 0.5
        
        # Test consumers
        world.consume_moisture(pos, 0.2)
        world.consume_nutrients(pos, 0.2)
        
        assert world.get_moisture(pos) == 0.3
        assert world.get_nutrients(pos) == 0.3
        
        # Test adding nutrients
        world.add_nutrients(pos, 0.4)
        
        assert world.get_nutrients(pos) == 0.7
        
        # Test max bounds
        world.add_nutrients(pos, 1.0)
        assert world.get_nutrients(pos) == 1.0  # Should be capped at 1.0
    
    def test_seeding(self):
        """Test seeding the world with entities"""
        world = World(width=20, height=20)
        
        # Seed with specific densities
        world.seed(plant_density=0.1, herbivore_density=0.02, carnivore_density=0.01)
        
        # Count entities by type
        plant_count = len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])
        herbivore_count = len([e for e in world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        carnivore_count = len([e for e in world.entities.values() if e.entity_type == EntityType.CARNIVORE])
        
        # Calculate expected counts (may not be exact due to position conflicts)
        grid_size = world.width * world.height
        expected_plants = int(grid_size * 0.1)
        expected_herbivores = int(grid_size * 0.02)
        expected_carnivores = int(grid_size * 0.01)
        
        # Counts should be reasonably close to expected (some positions might be occupied)
        # Allow for 10% margin of error
        assert plant_count >= expected_plants * 0.9, "Should create approximately the right number of plants"
        assert herbivore_count >= expected_herbivores * 0.9, "Should create approximately the right number of herbivores"
        assert carnivore_count >= expected_carnivores * 0.9, "Should create approximately the right number of carnivores"
    
    def test_update_metrics(self):
        """Test metrics collection"""
        world = World(width=10, height=10)
        
        # Add some entities
        plant = Plant(world.get_next_entity_id(), Position(5, 5), "cactus")
        world.add_entity(plant)
        
        herb = Herbivore(world.get_next_entity_id(), Position(6, 6))
        world.add_entity(herb)
        
        carn = Carnivore(world.get_next_entity_id(), Position(7, 7))
        world.add_entity(carn)
        
        # Update metrics
        world._update_metrics()
        
        # Check metrics
        assert world.metrics["plant_count"][-1] == 1
        assert world.metrics["herbivore_count"][-1] == 1
        assert world.metrics["carnivore_count"][-1] == 1
        
        # Average size/energy metrics should exist
        assert "avg_plant_size" in world.metrics
        assert "avg_herbivore_energy" in world.metrics
        assert "avg_carnivore_energy" in world.metrics
        
        # Environmental metrics should exist
        assert "avg_moisture" in world.metrics
        assert "avg_nutrients" in world.metrics
    
    def test_world_update(self):
        """Test full world update cycle"""
        world = World(width=10, height=10)
        
        # Add some plant entities
        plant = Plant(world.get_next_entity_id(), Position(5, 5), "cactus")
        world.add_entity(plant)
        
        # Set moisture for plant growth
        world.environment.moisture[5, 5] = 1.0
        world.environment.nutrients[5, 5] = 1.0
        
        # Store initial state
        initial_size = plant.size
        initial_moisture = world.environment.moisture[5, 5]
        initial_nutrients = world.environment.nutrients[5, 5]
        
        # Run update
        world.update()
        
        # Time step should advance
        assert world.time_step == 1
        
        # Plant should grow
        assert plant.size > initial_size
        
        # Resources should be consumed
        assert world.environment.moisture[5, 5] < initial_moisture
        assert world.environment.nutrients[5, 5] < initial_nutrients
        
        # Metrics should be updated
        assert len(world.metrics["time"]) == 1
        assert world.metrics["plant_count"][-1] == 1 