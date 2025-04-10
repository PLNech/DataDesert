from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from models.base import GeneticTrait, Entity, Position, EntityType
from models.plants import Plant


@dataclass
class AnimalDNA:
    """Genetic information for animals"""
    traits: Dict[str, GeneticTrait]

    @classmethod
    def create_random(cls, species_template: Dict[str, GeneticTrait]) -> 'AnimalDNA':
        """Create a new DNA with random variations on the template"""
        new_traits = {}
        for name, trait in species_template.items():
            # Add some random variation to the base trait
            variation = np.random.normal(0, 0.1)
            new_value = np.clip(trait.value + variation, trait.min_value, trait.max_value)
            new_traits[name] = GeneticTrait(
                name=trait.name,
                value=new_value,
                min_value=trait.min_value,
                max_value=trait.max_value,
                mutation_rate=trait.mutation_rate
            )
        return cls(traits=new_traits)

    @classmethod
    def from_parents(cls, parent1: 'AnimalDNA', parent2: 'AnimalDNA') -> 'AnimalDNA':
        """Create a new DNA by combining traits from parents with possible mutations"""
        new_traits = {}
        for name in parent1.traits:
            # Randomly select trait from either parent
            parent_trait = parent1.traits[name] if np.random.random() < 0.5 else parent2.traits[name]
            # Apply possible mutation
            new_traits[
                name] = parent_trait.mutate() if np.random.random() < parent_trait.mutation_rate else parent_trait
        return cls(traits=new_traits)

    def get_trait(self, name: str) -> float:
        """Get the value of a specific trait"""
        return self.traits[name].value


HERBIVORE_TEMPLATE = {
    "speed": GeneticTrait("speed", 0.6, 0.3, 1.0, 0.1),
    "size": GeneticTrait("size", 0.4, 0.2, 0.8, 0.05),
    "sense_range": GeneticTrait("sense_range", 0.7, 0.3, 1.0, 0.1),
    "metabolism": GeneticTrait("metabolism", 0.5, 0.3, 0.8, 0.05),
    "water_efficiency": GeneticTrait("water_efficiency", 0.6, 0.3, 0.9, 0.1),
}
CARNIVORE_TEMPLATE = {
    "speed": GeneticTrait("speed", 0.8, 0.5, 1.0, 0.1),
    "size": GeneticTrait("size", 0.6, 0.3, 1.0, 0.05),
    "sense_range": GeneticTrait("sense_range", 0.8, 0.5, 1.0, 0.1),
    "metabolism": GeneticTrait("metabolism", 0.7, 0.5, 0.9, 0.05),
    "water_efficiency": GeneticTrait("water_efficiency", 0.5, 0.3, 0.8, 0.1),
}


class Animal(Entity):
    """Base class for animal entities with movement and behaviors"""

    def __init__(self, entity_id: int, position: Position, entity_type: EntityType, dna: AnimalDNA):
        super().__init__(entity_id, position, entity_type)
        self.dna = dna
        self.energy = 100.0  # Starting energy
        self.water = 100.0  # Starting water
        self.health = 100.0  # Starting health
        self.last_movement = (0, 0)  # Direction of last movement
        self.target = None  # Target for movement
        self.reproduction_cooldown = 0

    def update(self, world: 'World') -> None:
        super().update(world)

        # Decrease energy and water based on metabolism
        metabolism_rate = self.dna.get_trait("metabolism")
        self.energy -= 1.0 * metabolism_rate
        self.water -= 1.0 * (1.0 - self.dna.get_trait("water_efficiency"))

        # Update health based on energy and water
        if self.energy < 20 or self.water < 20:
            self.health -= 1.0

        # Die if health reaches zero
        if self.health <= 0 or self.energy <= 0 or self.water <= 0:
            world.remove_entity(self.id)
            # Return nutrients to the soil when the animal dies
            world.add_nutrients(self.position, 5.0 * self.dna.get_trait("size"))
            return

        # Decrease reproduction cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # Implement basic behavior
        self._select_behavior(world)

    def _select_behavior(self, world: 'World') -> None:
        """Select and execute a behavior based on current state and surroundings"""
        # TODO: Implement strategy selection or dynamic behavior based on traits
        if self.water < 50:
            self._seek_water(world)
        elif self.energy < 50:
            self._seek_food(world)
        elif self.reproduction_cooldown <= 0 and self.energy > 80 and self.water > 80:
            self._seek_mate(world)
        else:
            self._explore(world)

    def _move(self, world: 'World', dx: int, dy: int) -> bool:
        """Try to move in the given direction"""
        new_x = self.position.x + dx
        new_y = self.position.y + dy

        # Check boundaries
        if (new_x < 0 or new_x >= world.width or
                new_y < 0 or new_y >= world.height):
            return False

        # Apply movement
        new_pos = Position(new_x, new_y)
        if not world.is_position_occupied(new_pos) or world.get_entity_at(new_pos).entity_type == EntityType.PLANT:
            world.move_entity(self.id, new_pos)
            self.position = new_pos
            self.energy -= 1.0 * self.dna.get_trait("size")  # Movement costs energy
            self.last_movement = (dx, dy)
            return True
        return False

    def _seek_water(self, world: 'World') -> None:
        """Move towards the nearest water source"""
        # TODO: Implement water seeking using sense range and world water map
        pass

    def _seek_food(self, world: 'World') -> None:
        """Move towards food appropriate for this animal's type"""
        # TODO: Implement food seeking
        pass

    def _seek_mate(self, world: 'World') -> None:
        """Move towards a potential mate"""
        # TODO: Implement mate seeking
        pass

    def _explore(self, world: 'World') -> None:
        """Random movement with slight preference for continuing in same direction"""
        if np.random.random() < 0.7 and self.last_movement != (0, 0):
            # Continue in roughly the same direction
            dx, dy = self.last_movement
            # Add some randomness
            dx += np.random.choice([-1, 0, 1])
            dy += np.random.choice([-1, 0, 1])
            # Normalize to -1, 0, 1
            dx = np.clip(dx, -1, 1)
            dy = np.clip(dy, -1, 1)
        else:
            # Random direction
            dx = np.random.choice([-1, 0, 1])
            dy = np.random.choice([-1, 0, 1])

        self._move(world, dx, dy)

    def try_reproduce(self, world: 'World', mate: 'Animal') -> Optional['Animal']:
        """Attempt to reproduce with another animal"""
        if (self.reproduction_cooldown > 0 or
                mate.reproduction_cooldown > 0 or
                self.energy < 50 or
                mate.energy < 50):
            return None

        # Create offspring DNA
        offspring_dna = AnimalDNA.from_parents(self.dna, mate.dna)

        # Find a nearby empty position for the offspring
        for _ in range(10):  # Try 10 times
            dx = np.random.choice([-1, 0, 1])
            dy = np.random.choice([-1, 0, 1])
            new_x = self.position.x + dx
            new_y = self.position.y + dy

            if (new_x >= 0 and new_x < world.width and
                    new_y >= 0 and new_y < world.height):
                new_pos = Position(new_x, new_y)
                if not world.is_position_occupied(new_pos):
                    # Create offspring
                    offspring = self.__class__(
                        entity_id=world.get_next_entity_id(),
                        position=new_pos,
                        entity_type=self.entity_type,
                        dna=offspring_dna
                    )

                    # Set reproduction cooldown and energy cost
                    self.reproduction_cooldown = 30
                    mate.reproduction_cooldown = 30
                    self.energy -= 30
                    mate.energy -= 30

                    return offspring

        return None


class Herbivore(Animal):
    """Herbivore animal that eats plants"""

    def __init__(self, entity_id: int, position: Position, dna: Optional[AnimalDNA] = None):
        if dna is None:
            dna = AnimalDNA.create_random(HERBIVORE_TEMPLATE)
        super().__init__(entity_id, position, EntityType.HERBIVORE, dna)

    def _seek_food(self, world: 'World') -> None:
        """Look for plants to eat"""
        sense_range = int(5 * self.dna.get_trait("sense_range"))

        # Look for plants in sensing range
        for dx in range(-sense_range, sense_range + 1):
            for dy in range(-sense_range, sense_range + 1):
                x = self.position.x + dx
                y = self.position.y + dy

                if (x >= 0 and x < world.width and
                        y >= 0 and y < world.height):
                    pos = Position(x, y)
                    entity = world.get_entity_at(pos)

                    if entity is not None and entity.entity_type == EntityType.PLANT:
                        # Move towards plant
                        move_dx = np.clip(dx, -1, 1)
                        move_dy = np.clip(dy, -1, 1)

                        if self._move(world, move_dx, move_dy):
                            # If we're now at a plant position, eat it
                            new_entity = world.get_entity_at(self.position)
                            if new_entity is not None and new_entity.entity_type == EntityType.PLANT:
                                self._eat_plant(world, new_entity)
                        return

        # If no plant found, just explore
        self._explore(world)

    def _eat_plant(self, world: 'World', plant: Plant) -> None:
        """Consume a plant for energy"""
        energy_gain = plant.size * 10.0
        self.energy = min(100.0, self.energy + energy_gain)

        # Also gain some water from the plant
        water_gain = plant.water_stored * 5.0
        self.water = min(100.0, self.water + water_gain)

        # Remove the eaten plant
        world.remove_entity(plant.id)


class Carnivore(Animal):
    """Carnivore animal that eats herbivores"""

    def __init__(self, entity_id: int, position: Position, dna: Optional[AnimalDNA] = None):
        if dna is None:
            dna = AnimalDNA.create_random(CARNIVORE_TEMPLATE)
        super().__init__(entity_id, position, EntityType.CARNIVORE, dna)

    def _seek_food(self, world: 'World') -> None:
        """Look for herbivores to hunt"""
        # TODO: Implement hunting behavior
        pass

    def _hunt_herbivore(self, world: 'World', herbivore: Herbivore) -> None:
        """Hunt and eat a herbivore"""
        # TODO: Implement hunting mechanics with chance of success based on traits
        pass
