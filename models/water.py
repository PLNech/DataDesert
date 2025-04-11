from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np

from models.base import Entity, Position, EntityType


class Water(Entity):
    """Water entity representing ponds, oases, or other water sources"""
    
    def __init__(self, entity_id: int, position: Position, size: float = 1.0):
        super().__init__(entity_id, position, EntityType.WATER)
        self.size = size  # Size can represent the amount of water
        self.evaporation_rate = 0.01  # Base evaporation rate
        self.diffusion_rate = 0.05  # How much moisture spreads to surroundings
        
    def update(self, world: 'World') -> None:
        """Update water entity state for one time step"""
        super().update(world)
        
        # Get temperature at this location
        temperature = world.environment.temperature[self.position.x, self.position.y]
        
        # Calculate evaporation rate based on temperature
        # Higher temperature = more evaporation
        # Guaranteed to be different for different temperatures
        evaporation = self.evaporation_rate * temperature * temperature
        
        # Store original size for logging
        previous_size = self.size
        
        # Reduce size based on evaporation
        self.size = max(0.1, self.size - evaporation)
        
        # Log evaporation for debugging
        # print(f"Water {self.id} evaporated from {previous_size:.4f} to {self.size:.4f} (temp: {temperature:.2f}, evap: {evaporation:.4f})")
        
        # Add moisture to surroundings
        self._diffuse_moisture(world)
        
        # Remove if too small (dried up)
        if self.size <= 0.1:
            world.remove_entity(self.id)
            return
        
        # Rainfall can replenish water sources
        rainfall = world.environment.moisture[self.position.x, self.position.y]
        if rainfall > 0.7:  # Heavy rainfall
            self.size = min(5.0, self.size + (rainfall - 0.5) * 0.1)
    
    def _diffuse_moisture(self, world: 'World') -> None:
        """Diffuse moisture to surrounding cells"""
        # Add moisture to current cell
        world.environment.moisture[self.position.x, self.position.y] = min(
            1.0, world.environment.moisture[self.position.x, self.position.y] + self.size * 0.1
        )
        
        # Diffuse to neighbors based on size and diffusion rate
        diffusion_radius = max(1, int(self.size))
        for dx in range(-diffusion_radius, diffusion_radius + 1):
            for dy in range(-diffusion_radius, diffusion_radius + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip center
                
                nx, ny = self.position.x + dx, self.position.y + dy
                
                # Check boundaries
                if (nx >= 0 and nx < world.width and 
                    ny >= 0 and ny < world.height):
                    
                    # Calculate distance-based diffusion
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= diffusion_radius:
                        # More moisture closer to source
                        moisture_add = (self.size * self.diffusion_rate * 
                                      (1.0 - dist/diffusion_radius))
                        
                        # Add moisture to this cell
                        world.environment.moisture[nx, ny] = min(
                            1.0, 
                            world.environment.moisture[nx, ny] + moisture_add
                        ) 