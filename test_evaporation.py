#!/usr/bin/env python

from models.base import Position
from models.water import Water
from simulation.world import World

def test_evaporation():
    """Test that water evaporates more in hot conditions than in cold"""
    # Create a test world
    world = World(width=10, height=10, create_water=False)
    
    # Test hot temperature
    x, y = 5, 5
    world.environment.temperature[x, y] = 1.0  # Very hot
    
    # Create water
    water = Water(entity_id=1, position=Position(x, y), size=2.0)
    original_size = water.size
    world.add_entity(water)
    
    # Run update
    water.update(world)
    
    # Calculate evaporation in hot conditions
    hot_evaporation = original_size - water.size
    
    # Now test with cold temperature
    world.environment.temperature[x, y] = 0.1  # Very cold
    
    # Reset water size
    water.size = original_size
    
    # Run update again
    water.update(world)
    
    # Calculate evaporation in cold conditions
    cold_evaporation = original_size - water.size
    
    # Print results
    print(f"\nEvaporation test results:")
    print(f"Hot conditions (temp=1.0): Evaporated {hot_evaporation:.6f}")
    print(f"Cold conditions (temp=0.1): Evaporated {cold_evaporation:.6f}")
    
    # Check if cold evaporation is less than hot
    if cold_evaporation < hot_evaporation:
        print("TEST PASSED ✓ - Cold evaporation is less than hot evaporation")
        return True
    else:
        print("TEST FAILED ✗ - Cold evaporation should be less than hot evaporation")
        return False

if __name__ == "__main__":
    test_evaporation() 