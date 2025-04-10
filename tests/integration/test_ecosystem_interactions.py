import pytest
import numpy as np
from models.base import Position, EntityType
from models.plants import Plant
from models.animals import Herbivore, Carnivore

@pytest.mark.integration
class TestEcosystemInteractions:
    
    def test_plant_survival_with_sufficient_resources(self, simple_world):
        """Test that plants survive and grow when they have sufficient resources"""
        world = simple_world
        
        # Create favorable environment
        world.environment.moisture[:] = 0.7
        world.environment.nutrients[:] = 0.7
        
        # Add a plant
        position = Position(5, 5)
        plant = Plant(world.get_next_entity_id(), position, "cactus")
        plant_id = plant.id
        world.add_entity(plant)
        
        # Run simulation for several cycles
        for _ in range(10):
            world.update()
        
        # Plant should still exist and have grown
        assert plant_id in world.entities
        assert world.entities[plant_id].size > 1.0  # Started at size 1.0
    
    def test_plant_death_in_drought_conditions(self, simple_world):
        """Test that plants die when exposed to drought conditions"""
        world = simple_world
        
        # Create drought environment
        world.environment.moisture[:] = 0.1
        world.environment.nutrients[:] = 0.1
        
        # Add a plant with minimal health
        position = Position(5, 5)
        plant = Plant(world.get_next_entity_id(), position, "desert_grass")
        plant.health = 10.0  # Start with low health
        plant_id = plant.id
        world.add_entity(plant)
        
        # Run simulation until death
        max_cycles = 20
        cycles_run = 0
        plant_died = False
        
        for _ in range(max_cycles):
            cycles_run += 1
            world.update()
            if plant_id not in world.entities:
                plant_died = True
                break
        
        # Plant should have died within the simulation time
        assert plant_died, f"Plant survived {cycles_run} cycles in drought conditions"
        
        # Nutrients should have been released upon death
        assert world.environment.nutrients[position.x, position.y] > 0.1
    
    def test_herbivore_consuming_plant(self, simple_world):
        """Test that herbivores can find and consume plants"""
        world = simple_world
        
        # Create favorable environment
        world.environment.moisture[:] = 0.7
        world.environment.nutrients[:] = 0.7
        
        # Add a plant
        plant_pos = Position(5, 5)
        plant = Plant(world.get_next_entity_id(), plant_pos, "cactus")
        plant_id = plant.id
        world.add_entity(plant)
        
        # Add a hungry herbivore nearby
        herb_pos = Position(7, 7)
        herbivore = Herbivore(world.get_next_entity_id(), herb_pos)
        herbivore.energy = 30.0  # Low energy to trigger food seeking
        herb_id = herbivore.id
        world.add_entity(herbivore)
        
        # Run simulation for several cycles
        max_cycles = 20
        for _ in range(max_cycles):
            world.update()
            # Stop if plant has been eaten
            if plant_id not in world.entities:
                break
        
        # Plant should have been eaten
        assert plant_id not in world.entities, "Herbivore failed to find and consume plant"
        
        # Herbivore should have gained energy
        assert herbivore.energy > 30.0, "Herbivore didn't gain energy from eating"
    
    def test_carnivore_hunting_herbivore(self, simple_world):
        """Test that carnivores can hunt and consume herbivores"""
        world = simple_world
        
        # Create favorable environment
        world.environment.moisture[:] = 0.7
        world.environment.nutrients[:] = 0.7
        
        # Add a herbivore
        herb_pos = Position(5, 5)
        herbivore = Herbivore(world.get_next_entity_id(), herb_pos)
        herb_id = herbivore.id
        world.add_entity(herbivore)
        
        # Add a hungry carnivore nearby
        carn_pos = Position(8, 8)
        carnivore = Carnivore(world.get_next_entity_id(), carn_pos)
        carnivore.energy = 30.0  # Low energy to trigger hunting
        carn_id = carnivore.id
        world.add_entity(carnivore)
        
        # Run simulation for several cycles
        max_cycles = 30
        for _ in range(max_cycles):
            world.update()
            # Stop if herbivore has been eaten
            if herb_id not in world.entities:
                break
        
        # Herbivore should have been eaten
        assert herb_id not in world.entities, "Carnivore failed to hunt herbivore"
        
        # Carnivore should have gained energy
        assert carnivore.energy > 30.0, "Carnivore didn't gain energy from hunting"
    
    def test_plant_reproduction_forms_colony(self, simple_world):
        """Test that plants reproduce to form a colony over time"""
        world = simple_world
        
        # Create favorable environment
        world.environment.moisture[:] = 0.8
        world.environment.nutrients[:] = 0.8
        
        # Add a mature plant ready to seed
        position = Position(10, 10)
        plant = Plant(world.get_next_entity_id(), position, "succulent")
        
        # Force growth and seeding
        plant.size = 2.0
        plant.ready_to_seed = True
        world.add_entity(plant)
        
        # Initial plant count
        initial_count = 1
        
        # Run simulation for several cycles
        cycles = 30
        for _ in range(cycles):
            world.update()
        
        # Count plants
        final_plant_count = len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])
        
        # Should have formed a colony (more plants than we started with)
        assert final_plant_count > initial_count, f"Plants failed to reproduce (count: {final_plant_count})"
        
        # Check for clustering - plants should be near each other
        plants = [e for e in world.entities.values() if e.entity_type == EntityType.PLANT]
        positions = [(p.position.x, p.position.y) for p in plants]
        
        # Calculate average distance to original plant
        distances = []
        for x, y in positions:
            dist = np.sqrt((x - position.x)**2 + (y - position.y)**2)
            distances.append(dist)
        
        # Average distance should be relatively small (within seed distance)
        avg_distance = np.mean(distances)
        
        # Succulent seed distance in model is 1.0
        assert avg_distance < 5.0, f"Plants not forming a proper colony (avg distance: {avg_distance})"
    
    def test_full_ecosystem_cycle(self, simple_world):
        """Test a full ecosystem cycle with all three trophic levels"""
        world = simple_world
        
        # Set favorable environmental conditions
        world.environment.moisture[:] = 0.7
        world.environment.nutrients[:] = 0.7
        
        # Seed with initial entities
        # Add more plants than animals to create a balanced ecosystem
        for i in range(20):
            pos = Position(np.random.randint(0, world.width), np.random.randint(0, world.height))
            if not world.is_position_occupied(pos):
                plant = Plant(world.get_next_entity_id(), pos, np.random.choice(list(["cactus", "desert_grass", "succulent"])))
                world.add_entity(plant)
        
        # Add some herbivores
        for i in range(5):
            pos = Position(np.random.randint(0, world.width), np.random.randint(0, world.height))
            if not world.is_position_occupied(pos):
                herb = Herbivore(world.get_next_entity_id(), pos)
                world.add_entity(herb)
        
        # Add a carnivore
        carn_pos = Position(np.random.randint(0, world.width), np.random.randint(0, world.height))
        if not world.is_position_occupied(carn_pos):
            carn = Carnivore(world.get_next_entity_id(), carn_pos)
            world.add_entity(carn)
        
        # Track initial counts
        initial_plants = len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])
        initial_herbs = len([e for e in world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        initial_carns = len([e for e in world.entities.values() if e.entity_type == EntityType.CARNIVORE])
        
        # Run simulation for multiple cycles
        cycles = 50
        for _ in range(cycles):
            world.update()
        
        # Count final populations
        final_plants = len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])
        final_herbs = len([e for e in world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        final_carns = len([e for e in world.entities.values() if e.entity_type == EntityType.CARNIVORE])
        
        # In a functional ecosystem, we should still have all three trophic levels
        assert final_plants > 0, "Plants died out in ecosystem"
        assert final_herbs > 0, "Herbivores died out in ecosystem"
        assert final_carns > 0, "Carnivores died out in ecosystem"
        
        # Check for reasonable population changes
        # Plants might decrease due to herbivore consumption but should reproduce
        # Herbivores should be controlled by carnivores
        # Carnivores are limited by herbivore availability
        if final_plants < initial_plants * 0.5:
            pytest.fail(f"Plant population decreased too dramatically: {initial_plants} -> {final_plants}")
            
        # Expect some fluctuation but not complete ecosystem collapse
        assert final_plants + final_herbs + final_carns >= (initial_plants + initial_herbs + initial_carns) * 0.3, \
            "Ecosystem experienced severe population collapse" 