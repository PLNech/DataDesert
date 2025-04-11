import sys
import os
import pytest
import numpy as np
import pygame as pg
from typing import Dict, Tuple

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.base import Position, EntityType
from models.plants import Plant, PLANT_SPECIES
from models.animals import Herbivore, Carnivore, AnimalDNA, HERBIVORE_TEMPLATE, CARNIVORE_TEMPLATE
from models.environment import Environment
from simulation.world import World
from simulation.analytics import Analytics
from controllers.game_manager import GameManager
from rendering.renderer import Renderer

@pytest.fixture
def mock_pygame_init(monkeypatch):
    """Mock pygame init for testing"""
    monkeypatch.setattr(pg, 'init', lambda: None)
    monkeypatch.setattr(pg.display, 'set_mode', lambda size, flags=0: pg.Surface(size))
    monkeypatch.setattr(pg.display, 'update', lambda: None)
    monkeypatch.setattr(pg.font, 'SysFont', lambda name, size: MockFont())
    monkeypatch.setattr(pg.time, 'Clock', lambda: MockClock())

class MockFont:
    def render(self, text, antialias, color):
        return pg.Surface((100, 20))

class MockClock:
    def tick(self, fps):
        pass

@pytest.fixture
def simple_world():
    """Create a small test world"""
    return World(width=20, height=20, create_water=False)

@pytest.fixture
def populated_world():
    """Create a small world with some initial entities"""
    world = World(width=20, height=20)
    
    # Add some moisture for plants
    world.environment.moisture[:] = 0.5
    world.environment.nutrients[:] = 0.5
    
    # Add plants of each species
    for i, species in enumerate(PLANT_SPECIES.keys()):
        plant = Plant(world.get_next_entity_id(), Position(5+i, 5), species)
        world.add_entity(plant)
    
    # Add a herbivore
    herbivore = Herbivore(world.get_next_entity_id(), Position(10, 10))
    world.add_entity(herbivore)
    
    # Add a carnivore
    carnivore = Carnivore(world.get_next_entity_id(), Position(15, 15))
    world.add_entity(carnivore)
    
    return world

@pytest.fixture
def analytics(simple_world):
    """Create an analytics instance for a world"""
    return Analytics(simple_world)

@pytest.fixture(autouse=True)
def set_random_seed():
    """Set a fixed seed for reproducible tests"""
    np.random.seed(42)
    return np.random.seed

@pytest.fixture
def mock_game_manager(mock_pygame_init):
    """Create a game manager with mocked pygame"""
    return GameManager(width=800, height=600) 