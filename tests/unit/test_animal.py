import pytest
import numpy as np
from models.base import Position, EntityType, GeneticTrait
from models.animals import Animal, Herbivore, Carnivore, AnimalDNA, HERBIVORE_TEMPLATE, CARNIVORE_TEMPLATE
from models.plants import Plant

@pytest.mark.unit
class TestAnimalDNA:
    
    def test_dna_creation_from_template(self):
        """Test creating DNA from a template"""
        dna = AnimalDNA.create_random(HERBIVORE_TEMPLATE)
        
        # All traits from template should be present
        for trait_name in HERBIVORE_TEMPLATE.keys():
            assert trait_name in dna.traits
            
            # Values should be within template range
            template_trait = HERBIVORE_TEMPLATE[trait_name]
            dna_trait = dna.traits[trait_name]
            
            assert dna_trait.min_value == template_trait.min_value
            assert dna_trait.max_value == template_trait.max_value
            assert dna_trait.mutation_rate == template_trait.mutation_rate
            assert dna_trait.min_value <= dna_trait.value <= dna_trait.max_value
    
    def test_dna_inheritance(self, monkeypatch):
        """Test DNA inheritance from two parents"""
        parent1 = AnimalDNA.create_random(HERBIVORE_TEMPLATE)
        parent2 = AnimalDNA.create_random(HERBIVORE_TEMPLATE)
        
        # Force some distinct values for testing
        parent1.traits["speed"].value = 0.4
        parent2.traits["speed"].value = 0.8
        
        # Set mutation rates to zero for deterministic testing
        for trait in parent1.traits.values():
            trait.mutation_rate = 0
        for trait in parent2.traits.values():
            trait.mutation_rate = 0
        
        # Test inheritance with controlled randomness
        # Mock random.random to alternate between values for predictable selection
        random_values = [0.2, 0.8]  # First parent, then second parent
        mock_index = 0
        
        def mock_random():
            nonlocal mock_index
            value = random_values[mock_index % len(random_values)]
            mock_index += 1
            return value
        
        monkeypatch.setattr(np.random, "random", mock_random)
        
        # Create child
        child = AnimalDNA.from_parents(parent1, parent2)
        
        # Verify inheritance
        assert child.traits["speed"].value == parent1.traits["speed"].value, "Should inherit first parent's speed"
    
    def test_trait_mutation(self, monkeypatch):
        """Test that traits can mutate"""
        # Create a trait with high mutation rate for testing
        trait = GeneticTrait("test", 0.5, 0, 1.0, 1.0)  # 100% mutation rate
        
        # Force mutation with controlled randomness
        # Fixed values for mutation calculation
        monkeypatch.setattr(np.random, "random", lambda: 0.5)  # Ensure mutation happens
        monkeypatch.setattr(np.random, "normal", lambda mu, sigma: 0.2)  # Add 0.2 to value
        
        # Perform mutation
        mutated = trait.mutate()
        
        # Verify mutation effects
        assert mutated.value == 0.7, "Trait should mutate by adding 0.2 to the value"

@pytest.mark.unit
class TestHerbivore:
    
    def test_herbivore_initialization(self):
        """Test that herbivores initialize correctly"""
        herb = Herbivore(entity_id=1, position=Position(5, 5))
        
        # Check basic properties
        assert herb.id == 1
        assert herb.position.x == 5
        assert herb.position.y == 5
        assert herb.entity_type == EntityType.HERBIVORE
        assert herb.energy == 100.0
        assert herb.water == 100.0
        assert herb.health == 100.0
        
        # Check DNA initialization
        assert herb.dna is not None
        for trait_name in HERBIVORE_TEMPLATE.keys():
            assert trait_name in herb.dna.traits
    
    def test_herbivore_update_consumes_resources(self, simple_world):
        """Test that herbivores consume energy and water during updates"""
        world = simple_world
        herb = Herbivore(entity_id=1, position=Position(5, 5))
        world.add_entity(herb)
        
        # Store initial values
        initial_energy = herb.energy
        initial_water = herb.water
        
        # Run update
        herb.update(world)
        
        # Energy and water should decrease
        assert herb.energy < initial_energy, "Herbivore should consume energy"
        assert herb.water < initial_water, "Herbivore should consume water"
    
    def test_herbivore_death(self, simple_world):
        """Test that herbivores die when resources are depleted"""
        world = simple_world
        herb = Herbivore(entity_id=1, position=Position(5, 5))
        herb.energy = 0.0  # No energy, should definitely die
        world.add_entity(herb)
        
        entity_id = herb.id
        position = herb.position
        
        # Run update - herbivore should die
        herb.update(world)
        
        # Verify herbivore was removed
        assert entity_id not in world.entities, "Herbivore should be removed when it dies"
        
        # Verify nutrients were returned to soil
        assert world.environment.nutrients[position.x, position.y] > 0, "Dead herbivore should return nutrients"
    
    def test_herbivore_eating_plant(self, simple_world):
        """Test that herbivores can eat plants"""
        world = simple_world
        x, y = 5, 5
        
        # Create a plant
        plant = Plant(world.get_next_entity_id(), Position(x, y), "desert_grass")
        plant.size = 5.0  # Good sized plant
        plant_id = plant.id
        world.add_entity(plant)
        
        # Create a herbivore at the same position
        herb = Herbivore(world.get_next_entity_id(), Position(x, y))
        herb.energy = 50.0  # Lower energy to ensure we see the gain
        world.add_entity(herb)
        
        # Get initial energy
        initial_energy = herb.energy
        
        # Call the eat plant method directly
        herb._eat_plant(world, plant)
        
        # Verify energy gain
        assert herb.energy > initial_energy, "Herbivore should gain energy from eating plant"
        
        # Verify plant was removed
        assert plant_id not in world.entities, "Plant should be removed when eaten"

@pytest.mark.unit
class TestCarnivore:
    
    def test_carnivore_initialization(self):
        """Test that carnivores initialize correctly"""
        carn = Carnivore(entity_id=1, position=Position(5, 5))
        
        # Check basic properties
        assert carn.id == 1
        assert carn.position.x == 5
        assert carn.position.y == 5
        assert carn.entity_type == EntityType.CARNIVORE
        assert carn.energy == 100.0
        assert carn.water == 100.0
        assert carn.health == 100.0
        
        # Check DNA initialization
        assert carn.dna is not None
        for trait_name in CARNIVORE_TEMPLATE.keys():
            assert trait_name in carn.dna.traits
    
    def test_carnivore_traits_differ_from_herbivore(self):
        """Test that carnivores have different trait defaults than herbivores"""
        herb = Herbivore(entity_id=1, position=Position(5, 5))
        carn = Carnivore(entity_id=2, position=Position(6, 6))
        
        # With the same random seed, these should still be different
        assert carn.dna.get_trait("speed") != herb.dna.get_trait("speed"), "Carnivores should have different speed"
        assert carn.dna.get_trait("size") != herb.dna.get_trait("size"), "Carnivores should have different size"
        
        # Carnivores should generally be faster
        carn_template_speed = CARNIVORE_TEMPLATE["speed"].value
        herb_template_speed = HERBIVORE_TEMPLATE["speed"].value
        assert carn_template_speed > herb_template_speed, "Carnivore template should have higher speed"
        
    def test_movement_based_on_speed(self, simple_world, monkeypatch):
        """Test that animal movement is influenced by speed trait"""
        world = simple_world
        
        # Create two animals with different speeds
        fast_animal = Carnivore(world.get_next_entity_id(), Position(10, 10))
        fast_animal.dna.traits["speed"].value = 1.0  # Max speed
        world.add_entity(fast_animal)
        
        slow_animal = Carnivore(world.get_next_entity_id(), Position(15, 15))
        slow_animal.dna.traits["speed"].value = 0.3  # Low speed
        world.add_entity(slow_animal)
        
        # Force exploration to test movement
        # Ensure both try to move the same direction
        monkeypatch.setattr(np.random, "randint", lambda low, high: 1)
        
        # Count successful moves for each
        fast_moves = 0
        slow_moves = 0
        
        # Run multiple explorations to account for randomness
        for _ in range(20):
            # Store original positions
            fast_pos = Position(fast_animal.position.x, fast_animal.position.y)
            slow_pos = Position(slow_animal.position.x, slow_animal.position.y)
            
            # Make them explore
            fast_animal._explore(world)
            slow_animal._explore(world)
            
            # Check if they moved
            if fast_animal.position.x != fast_pos.x or fast_animal.position.y != fast_pos.y:
                fast_moves += 1
            if slow_animal.position.x != slow_pos.x or slow_animal.position.y != slow_pos.y:
                slow_moves += 1
            
            # Reset positions for next iteration
            world.move_entity(fast_animal.id, Position(10, 10))
            world.move_entity(slow_animal.id, Position(15, 15))
        
        # Fast animal should move more often
        assert fast_moves > slow_moves, "Faster animal should be able to move more frequently" 