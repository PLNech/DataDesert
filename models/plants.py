from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np

from models.base import Entity, Position, EntityType


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
        self.health = max(0, int(self.health - water_deficit * (1 - self.species.drought_resistance)))

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
