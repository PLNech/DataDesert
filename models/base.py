from dataclasses import dataclass
from enum import Enum, auto
import numpy as np

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

    def update(self, world: "World") -> None:
        """Update entity state for one time step"""
        self.age += 1

