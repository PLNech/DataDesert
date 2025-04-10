import pytest
import numpy as np
from models.environment import Environment

@pytest.mark.unit
class TestEnvironment:
    
    def test_environment_initialization(self):
        """Test that environment initializes correctly"""
        env = Environment(width=20, height=20)
        
        # Check dimensions
        assert env.width == 20
        assert env.height == 20
        
        # Check initial grid values
        assert env.moisture.shape == (20, 20)
        assert env.nutrients.shape == (20, 20)
        assert env.temperature.shape == (20, 20)
        
        # Check initial environmental conditions
        assert np.all(env.moisture >= 0) and np.all(env.moisture <= 1)
        assert np.all(env.nutrients >= 0) and np.all(env.nutrients <= 1)
        assert np.all(env.temperature >= 0) and np.all(env.temperature <= 1)
        
        # Initial average nutrient level should be 0.5
        assert np.mean(env.nutrients) == 0.5
        
        # Initial desert temperature should be high
        assert np.mean(env.temperature) > 0.5
    
    def test_create_oases(self):
        """Test that oases are created properly"""
        env = Environment(width=30, height=30)
        
        # Clear any existing oases
        env.moisture[:] = 0
        
        # Create new oases
        env._create_oases(num_oases=3)
        
        # Should have some moisture now
        assert np.sum(env.moisture > 0) > 0, "Oases should add moisture to the environment"
        
        # Moisture should form clustered patterns (oases)
        # Count high moisture cells
        high_moisture_cells = np.sum(env.moisture > 0.7)
        assert high_moisture_cells > 0, "There should be some high-moisture cells for oases"
        
        # Check for clustering - adjacent high moisture cells
        high_moisture = env.moisture > 0.7
        has_clusters = False
        for x in range(1, env.width-1):
            for y in range(1, env.height-1):
                if high_moisture[x, y]:
                    # Check for adjacent high moisture
                    neighborhood = high_moisture[x-1:x+2, y-1:y+2]
                    if np.sum(neighborhood) > 1:  # If more than just this cell has high moisture
                        has_clusters = True
                        break
            if has_clusters:
                break
        
        assert has_clusters, "Moisture should form clusters (oases)"
    
    def test_diffuse_moisture(self):
        """Test that moisture diffuses correctly"""
        env = Environment(width=20, height=20)
        
        # Clear moisture
        env.moisture[:] = 0
        
        # Create a single moisture source in the center
        center_x, center_y = 10, 10
        env.moisture[center_x, center_y] = 1.0
        
        # Initial state: one wet cell, all others dry
        wet_cells_before = np.sum(env.moisture > 0)
        assert wet_cells_before == 1, "Should start with exactly one wet cell"
        
        # Diffuse the moisture
        env._diffuse_moisture()
        
        # After diffusion: moisture should spread to adjacent cells
        wet_cells_after = np.sum(env.moisture > 0)
        assert wet_cells_after > wet_cells_before, "Moisture should diffuse to surrounding cells"
        
        # Center cell should have less moisture than before
        assert env.moisture[center_x, center_y] < 1.0, "Diffusion should reduce moisture at source"
        
        # Adjacent cells should gain moisture
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x, y = center_x + dx, center_y + dy
            assert env.moisture[x, y] > 0, f"Cell at {x},{y} should receive moisture from diffusion"
    
    def test_update_nutrients(self):
        """Test that nutrients regenerate slowly"""
        env = Environment(width=10, height=10)
        
        # Set nutrients to zero
        env.nutrients[:] = 0
        
        # Initial state
        initial_nutrients = np.mean(env.nutrients)
        
        # Update nutrients
        env._update_nutrients()
        
        # Nutrients should increase slightly
        after_nutrients = np.mean(env.nutrients)
        assert after_nutrients > initial_nutrients, "Nutrients should regenerate slightly"
    
    def test_rainfall_creation(self):
        """Test that rainfall adds moisture to the environment"""
        env = Environment(width=30, height=30)
        
        # Set moisture to zero
        env.moisture[:] = 0
        
        # Create rainfall
        env._create_rainfall()
        
        # Moisture should be added across the map
        assert np.sum(env.moisture > 0) > 0, "Rainfall should add moisture"
        
        # Moisture should be capped at 1.0
        assert np.all(env.moisture <= 1.0), "Moisture should be capped at 1.0"
    
    def test_sequential_updates(self):
        """Test that environment updates properly over time"""
        env = Environment(width=20, height=20)
        
        # Clear moisture
        env.moisture[:] = 0
        
        # Add one oasis
        env._create_oases(num_oases=1)
        
        # Record initial state
        initial_moisture = env.moisture.copy()
        initial_nutrients = env.nutrients.copy()
        
        # Run several update cycles
        for _ in range(5):
            env.update()
        
        # Environment should change over time
        assert not np.array_equal(env.moisture, initial_moisture), "Moisture should change over time"
        assert not np.array_equal(env.nutrients, initial_nutrients), "Nutrients should change over time"
        
        # Average moisture should decrease due to evaporation (unless a rain event happens)
        # We can't test this deterministically due to random rain, but we can verify moisture exists
        assert np.sum(env.moisture > 0) > 0, "Environment should maintain some moisture"
    
    def test_weather_variation(self):
        """Test that weather conditions vary"""
        env = Environment(width=10, height=10)
        
        # Record initial weather state
        initial_wind_direction = env.wind_direction
        initial_wind_strength = env.wind_strength
        
        # Update several times
        different_wind = False
        for _ in range(10):
            env._update_weather()
            if (env.wind_direction != initial_wind_direction or 
                env.wind_strength != initial_wind_strength):
                different_wind = True
                break
        
        assert different_wind, "Weather conditions should vary over time"
        
        # Wind direction should be bounded (but no specific bounds in current implementation)
        # Wind strength should be between 0 and 1
        assert 0 < env.wind_strength < 1, "Wind strength should be between 0 and 1" 