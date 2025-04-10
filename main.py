import numpy as np
import pygame as pg
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import numba
from numba import jit
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from collections import defaultdict

# ./config.py
# Configuration constants for the DataDesert simulation
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
MAX_FPS = 60
MIN_FPS = 5

# Colors
BLACK = (8, 8, 8)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)
GREEN = (20, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (200, 200, 50)
RED = (200, 50, 50)

# Simulation constants
DEFAULT_SEED_RATE = 0.15
DEFAULT_DECAY_RATE = 0.015
DEFAULT_GROWTH_RATE = 0.0005
CELL_WIDTH = 10
CELL_HEIGHT = 10
CELL_MARGIN = 2


# END ./config.py

# ./models/base.py
class EntityType(Enum):
    EMPTY = auto()
    PLANT = auto()
    HERBIVORE = auto()
    CARNIVORE = auto()
    WATER = auto()


@dataclass
class Position:
    x: int
    y: int

    def distance_to(self, other: 'Position') -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class GeneticTrait:
    name: str
    value: float
    min_value: float = 0.0
    max_value: float = 1.0
    mutation_rate: float = 0.1

    def mutate(self) -> 'GeneticTrait':
        """Creates a mutated copy of this trait"""
        mutation = np.random.normal(0, self.mutation_rate)
        new_value = np.clip(self.value + mutation, self.min_value, self.max_value)
        return GeneticTrait(
            name=self.name,
            value=new_value,
            min_value=self.min_value,
            max_value=self.max_value,
            mutation_rate=self.mutation_rate
        )


class Entity:
    """Base class for all simulation entities"""

    def __init__(self, entity_id: int, position: Position, entity_type: EntityType):
        self.id = entity_id
        self.position = position
        self.entity_type = entity_type
        self.age = 0

    def update(self, world: 'World') -> None:
        """Update entity state for one time step"""
        self.age += 1


# END ./models/base.py

# ./models/plants.py
@dataclass
class PlantProperties:
    """Species-specific properties for plants"""
    name: str
    water_requirement: float
    nutrient_requirement: float
    growth_rate: float
    max_size: float
    seed_rate: float
    seed_distance: float
    drought_resistance: float
    color: Tuple[int, int, int]


# Define some plant species
PLANT_SPECIES = {
    "cactus": PlantProperties(
        name="Cactus",
        water_requirement=0.2,
        nutrient_requirement=0.3,
        growth_rate=0.05,
        max_size=10.0,
        seed_rate=0.01,
        seed_distance=2.0,
        drought_resistance=0.9,
        color=(20, 180, 20)
    ),
    "desert_grass": PlantProperties(
        name="Desert Grass",
        water_requirement=0.4,
        nutrient_requirement=0.2,
        growth_rate=0.15,
        max_size=3.0,
        seed_rate=0.08,
        seed_distance=5.0,
        drought_resistance=0.5,
        color=(150, 180, 50)
    ),
    "succulent": PlantProperties(
        name="Succulent",
        water_requirement=0.3,
        nutrient_requirement=0.2,
        growth_rate=0.1,
        max_size=5.0,
        seed_rate=0.03,
        seed_distance=1.0,
        drought_resistance=0.8,
        color=(100, 200, 100)
    ),
}


def species_by_name(species_name):
    for key, species in PLANT_SPECIES.items():
        if species.name.lower() == species_name.lower():
            return species
    raise ValueError(f"No specie named {species_name}")


class Plant(Entity):
    """Plant entity with growth and reproduction behaviors"""

    def __init__(self, entity_id: int, position: Position, species_name: str):
        super().__init__(entity_id, position, EntityType.PLANT)
        try:
            self.species = PLANT_SPECIES[species_name]
        except KeyError:
            self.species = species_by_name(species_name)
        self.size = 1.0
        self.water_stored = 1.0
        self.health = 1.0
        self.ready_to_seed = False

    def update(self, world: 'World') -> None:
        super().update(world)

        # Get environmental factors
        cell_moisture = world.get_moisture(self.position)
        cell_nutrients = world.get_nutrients(self.position)

        # Update water stored
        water_absorbed = min(cell_moisture, self.species.water_requirement)
        self.water_stored = min(self.water_stored + water_absorbed, self.species.max_size)
        world.consume_moisture(self.position, water_absorbed)

        # Update growth based on available resources
        growth_factor = min(
            self.water_stored / self.species.water_requirement,
            cell_nutrients / self.species.nutrient_requirement
        )

        growth_amount = self.species.growth_rate * growth_factor
        self.size = min(self.size + growth_amount, self.species.max_size)

        # Consume nutrients proportional to growth
        if growth_amount > 0:
            world.consume_nutrients(self.position, growth_amount * self.species.nutrient_requirement)

        # Update health based on water stored
        water_deficit = max(0, self.species.water_requirement - self.water_stored)
        self.health = max(0, self.health - water_deficit * (1 - self.species.drought_resistance))

        # Check if ready to seed
        if (self.size > self.species.max_size * 0.7 and
                np.random.random() < self.species.seed_rate):
            self.ready_to_seed = True

        # Consume water for survival
        survival_water = self.species.water_requirement * 0.5
        self.water_stored = max(0, self.water_stored - survival_water)

        # Die if health reaches zero
        if self.health <= 0:
            world.remove_entity(self.id)
            # Return nutrients to the soil when the plant dies
            world.add_nutrients(self.position, self.size * 0.5)

    def try_reproduce(self, world: 'World') -> Optional['Plant']:
        """Attempt to create a new plant from seed"""
        if not self.ready_to_seed:
            return None

        # Reset seeding flag
        self.ready_to_seed = False

        # Determine seed position (random direction within seed distance)
        angle = np.random.random() * 2 * np.pi
        distance = np.random.random() * self.species.seed_distance

        new_x = int(self.position.x + np.cos(angle) * distance)
        new_y = int(self.position.y + np.sin(angle) * distance)

        # Check boundaries
        if (new_x < 0 or new_x >= world.width or
                new_y < 0 or new_y >= world.height):
            return None

        # Check if space is available
        new_pos = Position(new_x, new_y)
        if world.is_position_occupied(new_pos):
            return None

        # Create new plant
        return Plant(
            entity_id=world.get_next_entity_id(),
            position=new_pos,
            species_name=self.species.name.lower()
        )


# END ./models/plants.py

# ./models/animals.py
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


# Base templates for animal species
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


# END ./models/animals.py

# ./models/environment.py
class Environment:
    """Environmental systems including water, nutrients, and weather"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Environmental grids
        self.moisture = np.zeros((width, height), dtype=np.float32)
        self.nutrients = np.ones((width, height), dtype=np.float32) * 0.5  # Start with medium nutrients
        self.temperature = np.ones((width, height), dtype=np.float32) * 0.7  # Desert is hot

        # Weather state
        self.season = 0  # 0=spring, 1=summer, 2=fall, 3=winter
        self.rain_chance = 0.005  # Daily chance of rain
        self.wind_direction = 0  # Radians
        self.wind_strength = 0.2  # 0-1 scale

        # Create some initial water sources (oases)
        self._create_oases()

    def _create_oases(self, num_oases: int = 3) -> None:
        """Create initial water sources"""
        for _ in range(num_oases):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)

            # Create a small area with high moisture
            radius = np.random.randint(3, 8)
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if (nx >= 0 and nx < self.width and
                            ny >= 0 and ny < self.height):
                        # Calculate distance from center
                        dist = np.sqrt(dx ** 2 + dy ** 2)
                        if dist <= radius:
                            # More water in the center, less at the edges
                            moisture = max(0, 1.0 - (dist / radius))
                            self.moisture[nx, ny] = max(self.moisture[nx, ny], moisture)

    def update(self) -> None:
        """Update environmental conditions for one time step"""
        # Process water diffusion
        self._diffuse_moisture()

        # Process nutrient cycling
        self._update_nutrients()

        # Check for weather events
        self._update_weather()

    def _diffuse_moisture(self) -> None:
        """Simulate water movement through soil"""
        # Simple diffusion using convolution
        kernel = np.array([[0.05, 0.1, 0.05],
                           [0.1, 0.4, 0.1],
                           [0.05, 0.1, 0.05]])

        # TODO: Replace with numba optimized diffusion
        # For now, just do simple blurring
        from scipy.ndimage import convolve
        self.moisture = convolve(self.moisture, kernel, mode='constant', cval=0)

        # Apply evaporation based on temperature
        self.moisture *= (1.0 - 0.01 * self.temperature)

    def _update_nutrients(self) -> None:
        """Update nutrient levels in soil"""
        # Very slow natural regeneration of nutrients
        self.nutrients += 0.0001
        # Cap at maximum
        self.nutrients = np.clip(self.nutrients, 0, 1.0)

    def _update_weather(self) -> None:
        """Update weather conditions"""
        # Random chance of rain
        if np.random.random() < self.rain_chance:
            self._create_rainfall()

        # Update wind
        self.wind_direction += np.random.normal(0, 0.1)
        self.wind_strength = np.clip(self.wind_strength + np.random.normal(0, 0.05), 0.1, 0.9)

    def _create_rainfall(self) -> None:
        """Simulate a rainfall event"""
        # Add moisture across the map with some randomness
        rain_intensity = np.random.uniform(0.2, 0.5)
        rain_map = np.random.uniform(0, rain_intensity, size=(self.width, self.height))
        self.moisture += rain_map
        self.moisture = np.clip(self.moisture, 0, 1.0)  # Cap at 1.0


# END ./models/environment.py

# ./simulation/world.py
class World:
    """Main container for the simulation world"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.environment = Environment(width, height)

        # Entity storage
        self.entities: Dict[int, Entity] = {}
        self.entity_grid: Dict[Tuple[int, int], int] = {}  # Position -> entity_id
        self.next_entity_id = 1

        # Metrics tracking
        self.metrics = {
            "time": [],
            "plant_count": [],
            "herbivore_count": [],
            "carnivore_count": [],
            "avg_plant_size": [],
            "avg_herbivore_energy": [],
            "avg_carnivore_energy": [],
            "avg_moisture": [],
            "avg_nutrients": [],
        }
        self.time_step = 0

    def update(self) -> None:
        """Update the world state for one time step"""
        # Update environment first
        self.environment.update()

        # Update all entities
        entity_ids = list(self.entities.keys())
        for entity_id in entity_ids:
            if entity_id in self.entities:  # Check if still exists
                self.entities[entity_id].update(self)

        # Handle reproduction
        self._process_reproduction()

        # Update metrics
        self._update_metrics()

        self.time_step += 1

    def _process_reproduction(self) -> None:
        """Handle reproduction for all entities"""
        new_entities = []

        # Process plant seeding
        for entity in self.entities.values():
            if isinstance(entity, Plant):
                new_plant = entity.try_reproduce(self)
                if new_plant:
                    new_entities.append(new_plant)

        # Process animal mating
        # TODO: Implement animal mating logic

        # Add all new entities
        for entity in new_entities:
            self.add_entity(entity)

    def _update_metrics(self) -> None:
        """Collect data on current world state"""
        plants = [e for e in self.entities.values() if e.entity_type == EntityType.PLANT]
        herbivores = [e for e in self.entities.values() if e.entity_type == EntityType.HERBIVORE]
        carnivores = [e for e in self.entities.values() if e.entity_type == EntityType.CARNIVORE]

        self.metrics["time"].append(self.time_step)
        self.metrics["plant_count"].append(len(plants))
        self.metrics["herbivore_count"].append(len(herbivores))
        self.metrics["carnivore_count"].append(len(carnivores))

        self.metrics["avg_plant_size"].append(
            np.mean([p.size for p in plants]) if plants else 0
        )
        self.metrics["avg_herbivore_energy"].append(
            np.mean([h.energy for h in herbivores]) if herbivores else 0
        )
        self.metrics["avg_carnivore_energy"].append(
            np.mean([c.energy for c in carnivores]) if carnivores else 0
        )

        self.metrics["avg_moisture"].append(np.mean(self.environment.moisture))
        self.metrics["avg_nutrients"].append(np.mean(self.environment.nutrients))

    def get_next_entity_id(self) -> int:
        """Get a unique ID for a new entity"""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the world"""
        self.entities[entity.id] = entity
        self.entity_grid[(entity.position.x, entity.position.y)] = entity.id

    def remove_entity(self, entity_id: int) -> None:
        """Remove an entity from the world"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            pos_key = (entity.position.x, entity.position.y)
            if pos_key in self.entity_grid:
                del self.entity_grid[pos_key]
            del self.entities[entity_id]

    def move_entity(self, entity_id: int, new_position: Position) -> None:
        """Move an entity to a new position"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            old_pos_key = (entity.position.x, entity.position.y)
            new_pos_key = (new_position.x, new_position.y)

            # Update entity grid
            if old_pos_key in self.entity_grid:
                del self.entity_grid[old_pos_key]
            self.entity_grid[new_pos_key] = entity_id

            # Update entity position
            entity.position = new_position

    def is_position_occupied(self, position: Position) -> bool:
        """Check if a position contains an entity"""
        return (position.x, position.y) in self.entity_grid

    def get_entity_at(self, position: Position) -> Optional[Entity]:
        """Get the entity at a specific position"""
        pos_key = (position.x, position.y)
        if pos_key in self.entity_grid:
            return self.entities.get(self.entity_grid[pos_key])
        return None

    def get_moisture(self, position: Position) -> float:
        """Get moisture level at a position"""
        return self.environment.moisture[position.x, position.y]

    def get_nutrients(self, position: Position) -> float:
        """Get nutrient level at a position"""
        return self.environment.nutrients[position.x, position.y]

    def consume_moisture(self, position: Position, amount: float) -> None:
        """Consume moisture at a position"""
        self.environment.moisture[position.x, position.y] = max(
            0, self.environment.moisture[position.x, position.y] - amount
        )

    def consume_nutrients(self, position: Position, amount: float) -> None:
        """Consume nutrients at a position"""
        self.environment.nutrients[position.x, position.y] = max(
            0, self.environment.nutrients[position.x, position.y] - amount
        )

    def add_nutrients(self, position: Position, amount: float) -> None:
        """Add nutrients at a position (e.g., from decaying organisms)"""
        self.environment.nutrients[position.x, position.y] = min(
            1.0, self.environment.nutrients[position.x, position.y] + amount
        )

    def get_entities_in_radius(self, position: Position, radius: int,
                               entity_type: Optional[EntityType] = None) -> List[Entity]:
        """Get all entities within a certain radius of a position"""
        entities_in_radius = []

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = position.x + dx
                y = position.y + dy

                if (x >= 0 and x < self.width and
                        y >= 0 and y < self.height):
                    pos = Position(x, y)
                    entity = self.get_entity_at(pos)

                    if entity is not None:
                        if entity_type is None or entity.entity_type == entity_type:
                            entities_in_radius.append(entity)

        return entities_in_radius

    def seed(self, plant_density: float = 0.05, herbivore_density: float = 0.01,
             carnivore_density: float = 0.005) -> None:
        """Seed the world with initial entities"""
        # Calculate counts
        grid_size = self.width * self.height
        plant_count = int(grid_size * plant_density)
        herbivore_count = int(grid_size * herbivore_density)
        carnivore_count = int(grid_size * carnivore_density)

        # Add plants
        plant_species = list(PLANT_SPECIES.keys())
        for _ in range(plant_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                species = np.random.choice(plant_species)
                plant = Plant(self.get_next_entity_id(), pos, species)
                self.add_entity(plant)

        # Add herbivores
        for _ in range(herbivore_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                herbivore = Herbivore(self.get_next_entity_id(), pos)
                self.add_entity(herbivore)

        # Add carnivores
        for _ in range(carnivore_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            pos = Position(x, y)

            if not self.is_position_occupied(pos):
                carnivore = Carnivore(self.get_next_entity_id(), pos)
                self.add_entity(carnivore)


# END ./simulation/world.py

# ./simulation/analytics.py
class Analytics:
    """Data analysis and visualization for the simulation"""

    def __init__(self, world: World):
        self.world = world
        self.df = pd.DataFrame()

    def update(self) -> None:
        """Update analytics data from the world"""
        # Convert metrics dict to DataFrame
        self.df = pd.DataFrame(self.world.metrics)

    def get_biodiversity_index(self) -> float:
        """Calculate a simple biodiversity index"""
        if self.df.empty:
            return 0

        # Get latest counts
        latest = self.df.iloc[-1]

        # Simple Shannon diversity index
        total = latest["plant_count"] + latest["herbivore_count"] + latest["carnivore_count"]
        if total == 0:
            return 0

        # Calculate proportions
        p_plant = latest["plant_count"] / total if total > 0 else 0
        p_herb = latest["herbivore_count"] / total if total > 0 else 0
        p_carn = latest["carnivore_count"] / total if total > 0 else 0

        # Shannon index
        shannon = 0
        for p in [p_plant, p_herb, p_carn]:
            if p > 0:
                shannon -= p * np.log(p)

        return shannon

    def get_population_dataframe(self) -> pd.DataFrame:
        """Get population data for visualization"""
        if self.df.empty:
            return pd.DataFrame()

        return self.df[["time", "plant_count", "herbivore_count", "carnivore_count"]]

    def get_ecosystem_health(self) -> float:
        """Calculate overall ecosystem health metric"""
        if self.df.empty:
            return 0

        # Latest metrics
        latest = self.df.iloc[-1]

        # Calculate stability (how consistent populations are)
        if len(self.df) < 10:
            stability = 0.5  # Default for early simulation
        else:
            # Calculate coefficient of variation for last 10 time steps
            recent = self.df.iloc[-10:]
            cv_plant = recent["plant_count"].std() / recent["plant_count"].mean() if recent[
                                                                                         "plant_count"].mean() > 0 else 1
            cv_herb = recent["herbivore_count"].std() / recent["herbivore_count"].mean() if recent[
                                                                                                "herbivore_count"].mean() > 0 else 1
            cv_carn = recent["carnivore_count"].std() / recent["carnivore_count"].mean() if recent[
                                                                                                "carnivore_count"].mean() > 0 else 1

            # Lower CV means more stable (better)
            stability = 1.0 - min(1.0, (cv_plant + cv_herb + cv_carn) / 3)

        # Biodiversity component
        biodiversity = self.get_biodiversity_index() / np.log(3)  # Normalize

        # Resource availability
        resources = (latest["avg_moisture"] + latest["avg_nutrients"]) / 2

        # Population balance
        total = latest["plant_count"] + latest["herbivore_count"] + latest["carnivore_count"]
        if total == 0:
            balance = 0
        else:
            # Ideal ratios might be something like 80% plants, 15% herbivores, 5% carnivores
            plant_ratio = latest["plant_count"] / total
            herb_ratio = latest["herbivore_count"] / total
            carn_ratio = latest["carnivore_count"] / total

            # Calculate distance from ideal ratios
            ideal_dist = abs(plant_ratio - 0.8) + abs(herb_ratio - 0.15) + abs(carn_ratio - 0.05)
            balance = 1.0 - min(1.0, ideal_dist)

        # Combine metrics with weights
        health = (
                0.3 * stability +
                0.3 * biodiversity +
                0.2 * resources +
                0.2 * balance
        )

        return min(1.0, max(0.0, health))

    def render_population_chart(self) -> np.ndarray:
        """Render a population chart as a numpy array for display"""
        if self.df.empty:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)

        # Plot populations
        ax.plot(self.df["time"], self.df["plant_count"], 'g-', label="Plants")
        ax.plot(self.df["time"], self.df["herbivore_count"], 'b-', label="Herbivores")
        ax.plot(self.df["time"], self.df["carnivore_count"], 'r-', label="Carnivores")

        ax.set_xlabel("Time")
        ax.set_ylabel("Population")
        ax.set_title("Ecosystem Populations")
        ax.legend()

        # Convert to numpy array
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf = canvas.buffer_rgba()
        plt.close(fig)

        # Convert to numpy array
        chart = np.asarray(buf)

        return chart


# END ./simulation/analytics.py

# ./rendering/renderer.py
class Renderer:
    """Responsible for rendering the simulation to the screen"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT
        self.cell_margin = CELL_MARGIN

        # Initialize pygame
        pg.init()
        self.display = pg.display.set_mode((width, height), pg.HWSURFACE | pg.DOUBLEBUF)
        pg.display.set_caption("DataDesert v2")

        # Create surfaces
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill(GREY)

        # Font for displaying information
        self.font = pg.font.SysFont('Arial', 18)

    def render(self, world: World, analytics: Analytics = None) -> None:
        """Render the current state of the world"""
        # Clear screen
        self.display.blit(self.background, (0, 0))

        # Render environment (moisture as background intensity)
        self._render_environment(world)

        # Render entities
        self._render_entities(world)

        # Render UI stats
        self._render_stats(world, analytics)

        # Update display
        pg.display.update()

    def _render_environment(self, world: World) -> None:
        """Render environmental factors like moisture levels"""
        for x in range(world.width):
            for y in range(world.height):
                moisture = world.environment.moisture[x, y]
                nutrients = world.environment.nutrients[x, y]

                # Calculate position
                rect_x = (self.cell_margin + self.cell_width) * x + self.cell_margin
                rect_y = (self.cell_margin + self.cell_height) * y + self.cell_margin

                # Draw moisture as blue tint with alpha based on moisture level
                blue_tint = (200, 200, 255, int(moisture * 128))

                # Create a small surface for the cell
                cell_surface = pg.Surface((self.cell_width, self.cell_height))
                cell_surface.fill(GREY)

                # Draw blue tint based on moisture
                if moisture > 0.1:
                    # Calculate color based on moisture
                    blue = int(min(255, 100 + moisture * 155))
                    cell_surface.fill((100, 100, blue))

                # Draw on the display
                self.display.blit(cell_surface, (rect_x, rect_y))

    def _render_entities(self, world: World) -> None:
        """Render all entities in the world"""
        for entity in world.entities.values():
            rect_x = (self.cell_margin + self.cell_width) * entity.position.x + self.cell_margin
            rect_y = (self.cell_margin + self.cell_height) * entity.position.y + self.cell_margin
            rect = [rect_x, rect_y, self.cell_width, self.cell_height]

            if entity.entity_type == EntityType.PLANT:
                plant = entity  # type: Plant
                # Color based on plant species and size
                base_color = plant.species.color
                # Adjust brightness based on size
                size_factor = min(1.0, plant.size / plant.species.max_size)
                color = (
                    int(base_color[0] * size_factor),
                    int(base_color[1] * size_factor),
                    int(base_color[2] * size_factor)
                )
                pg.draw.rect(self.display, color, rect)

            elif entity.entity_type == EntityType.HERBIVORE:
                # Blue for herbivores
                pg.draw.rect(self.display, BLUE, rect)

            elif entity.entity_type == EntityType.CARNIVORE:
                # Red for carnivores
                pg.draw.rect(self.display, RED, rect)

            elif entity.entity_type == EntityType.WATER:
                # Blue for water
                pg.draw.rect(self.display, (0, 0, 255), rect)

    def _render_stats(self, world: World, analytics: Analytics = None) -> None:
        """Render stats and metrics on screen"""
        stats = [
            f"Time: {world.time_step}",
            f"Plants: {len([e for e in world.entities.values() if e.entity_type == EntityType.PLANT])}",
            f"Herbivores: {len([e for e in world.entities.values() if e.entity_type == EntityType.HERBIVORE])}",
            f"Carnivores: {len([e for e in world.entities.values() if e.entity_type == EntityType.CARNIVORE])}",
        ]

        if analytics:
            stats.extend([
                f"Biodiversity: {analytics.get_biodiversity_index():.2f}",
                f"Ecosystem Health: {analytics.get_ecosystem_health():.2f}"
            ])

        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            self.display.blit(text, (10, 10 + i * 25))


# END ./rendering/renderer.py

# ./controllers/game_manager.py
class GameManager:
    """Manages the game state and progression"""

    def __init__(self, width: int, height: int):
        # Initialize simulation components
        grid_width = width // (CELL_WIDTH + CELL_MARGIN)
        grid_height = height // (CELL_HEIGHT + CELL_MARGIN)

        self.world = World(grid_width, grid_height)
        self.analytics = Analytics(self.world)
        self.renderer = Renderer(width, height)

        # Game state
        self.running = True
        self.paused = False
        self.tick_rate = 30
        self.clock = pg.time.Clock()

        # Progression system
        self.unlocked_features = {
            "plants": True,  # Start with plants
            "herbivores": False,
            "carnivores": False,
            "weather": False,
            "genetics": False,
        }

        # Achievement system
        self.achievements = {
            "first_plant": {"description": "Grow your first plant", "unlocked": False},
            "thriving_ecosystem": {"description": "Reach 100 plants", "unlocked": False},
            "circle_of_life": {"description": "Have all three trophic levels present", "unlocked": False},
            "genetic_diversity": {"description": "Reach 10 generations of animals", "unlocked": False},
            "stable_ecosystem": {"description": "Maintain stable populations for 100 time steps", "unlocked": False},
        }

        # Selected tool
        self.selected_tool = "cactus"  # Default tool

    def initialize(self) -> None:
        """Initialize the game world"""
        # Create environment
        self.world.environment._create_oases(5)

        # Seed with initial plants only
        self.world.seed(plant_density=0.05, herbivore_density=0, carnivore_density=0)

    def update(self) -> None:
        """Update game state for one time step"""
        if not self.paused:
            self.world.update()
            self.analytics.update()

            # Check for feature unlocks
            self._check_feature_unlocks()

            # Check for achievements
            self._check_achievements()

    def render(self) -> None:
        """Render the current game state"""
        self.renderer.render(self.world, self.analytics)

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self._handle_key_event(event)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self._handle_mouse_event(event)

    def _handle_key_event(self, event) -> None:
        """Handle keyboard events"""
        if event.key == pg.K_ESCAPE:
            self.running = False
        elif event.key == pg.K_SPACE:
            self.paused = not self.paused
        elif event.key == pg.K_r:
            self._reset_world()
        elif event.key == pg.K_EQUALS or event.key == pg.K_PLUS:
            self.tick_rate = min(MAX_FPS, self.tick_rate + 5)
        elif event.key == pg.K_MINUS:
            self.tick_rate = max(MIN_FPS, self.tick_rate - 5)
        # Tools selection
        elif event.key == pg.K_1:
            self.selected_tool = "cactus"
        elif event.key == pg.K_2:
            self.selected_tool = "desert_grass"
        elif event.key == pg.K_3:
            self.selected_tool = "succulent"
        elif event.key == pg.K_4 and self.unlocked_features["herbivores"]:
            self.selected_tool = "herbivore"
        elif event.key == pg.K_5 and self.unlocked_features["carnivores"]:
            self.selected_tool = "carnivore"
        elif event.key == pg.K_6 and self.unlocked_features["weather"]:
            self.selected_tool = "rain"

    def _handle_mouse_event(self, event) -> None:
        """Handle mouse events"""
        if event.button in (1, 3):  # Left or right click
            # Get grid position
            pos = pg.mouse.get_pos()
            col = pos[0] // (CELL_WIDTH + CELL_MARGIN)
            row = pos[1] // (CELL_HEIGHT + CELL_MARGIN)

            if col >= 0 and col < self.world.width and row >= 0 and row < self.world.height:
                position = Position(col, row)

                # Left click adds, right click removes
                if event.button == 1:
                    self._use_tool(position)
                elif event.button == 3:
                    # Remove entity at position
                    entity = self.world.get_entity_at(position)
                    if entity:
                        self.world.remove_entity(entity.id)

    def _use_tool(self, position: Position) -> None:
        """Use the currently selected tool at a position"""
        if not self.world.is_position_occupied(position):
            if self.selected_tool in PLANT_SPECIES:
                plant = Plant(self.world.get_next_entity_id(), position, self.selected_tool)
                self.world.add_entity(plant)
            elif self.selected_tool == "herbivore" and self.unlocked_features["herbivores"]:
                herbivore = Herbivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(herbivore)
            elif self.selected_tool == "carnivore" and self.unlocked_features["carnivores"]:
                carnivore = Carnivore(self.world.get_next_entity_id(), position)
                self.world.add_entity(carnivore)
            elif self.selected_tool == "rain" and self.unlocked_features["weather"]:
                # Create a small rain shower
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        x, y = position.x + dx, position.y + dy
                        if x >= 0 and x < self.world.width and y >= 0 and y < self.world.height:
                            # Add moisture
                            dist = np.sqrt(dx ** 2 + dy ** 2)
                            if dist <= 3:
                                moisture = max(0, 0.8 - (dist / 3) * 0.5)
                                self.world.environment.moisture[x, y] += moisture
                                self.world.environment.moisture[x, y] = min(1.0, self.world.environment.moisture[x, y])

    def _reset_world(self) -> None:
        """Reset the simulation world"""
        grid_width = self.world.width
        grid_height = self.world.height
        self.world = World(grid_width, grid_height)
        self.analytics = Analytics(self.world)
        self.initialize()

    def _check_feature_unlocks(self) -> None:
        """Check if any features should be unlocked based on progress"""
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])

        # Unlock herbivores once there are enough plants
        if not self.unlocked_features["herbivores"] and plant_count >= 50:
            self.unlocked_features["herbivores"] = True
            print("Herbivores unlocked!")

        # Unlock carnivores once there are enough herbivores
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        if not self.unlocked_features["carnivores"] and herbivore_count >= 20:
            self.unlocked_features["carnivores"] = True
            print("Carnivores unlocked!")

        # Unlock weather after certain time
        if not self.unlocked_features["weather"] and self.world.time_step >= 200:
            self.unlocked_features["weather"] = True
            print("Weather system unlocked!")

    def _check_achievements(self) -> None:
        """Check if any achievements have been unlocked"""
        # Get entity counts
        plant_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT])
        herbivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE])
        carnivore_count = len([e for e in self.world.entities.values() if e.entity_type == EntityType.CARNIVORE])

        # First plant
        if not self.achievements["first_plant"]["unlocked"] and plant_count > 0:
            self.achievements["first_plant"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['first_plant']['description']}")

        # Thriving ecosystem
        if not self.achievements["thriving_ecosystem"]["unlocked"] and plant_count >= 100:
            self.achievements["thriving_ecosystem"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['thriving_ecosystem']['description']}")

        # Circle of life
        if (not self.achievements["circle_of_life"]["unlocked"] and
                plant_count > 0 and herbivore_count > 0 and carnivore_count > 0):
            self.achievements["circle_of_life"]["unlocked"] = True
            print(f"Achievement unlocked: {self.achievements['circle_of_life']['description']}")

        # TODO: Implement other achievement checks

    def run(self) -> None:
        """Main game loop"""
        while self.running:
            self.clock.tick(self.tick_rate)
            self.handle_events()
            self.update()
            self.render()

        pg.quit()


# END ./controllers/game_manager.py

# main.py
def main():
    """Main entry point for the simulation"""
    # Initialize the game
    game = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.initialize()

    # Run the game loop
    game.run()


if __name__ == "__main__":
    main()
# END main.py