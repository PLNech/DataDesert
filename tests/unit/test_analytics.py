import pytest
import numpy as np
import pandas as pd
from simulation.analytics import Analytics
from models.base import Position, EntityType
from models.plants import Plant
from models.animals import Herbivore, Carnivore

@pytest.mark.unit
class TestAnalytics:
    
    def test_analytics_initialization(self, simple_world):
        """Test analytics initialization"""
        analytics = Analytics(simple_world)
        
        # Check that world reference is set
        assert analytics.world == simple_world
        
        # DataFrame should be empty initially
        assert analytics.df.empty
    
    def test_update_creates_dataframe(self, populated_world):
        """Test that update populates the dataframe"""
        world = populated_world
        analytics = Analytics(world)
        
        # Perform update
        analytics.update()
        
        # DataFrame should now have data
        assert not analytics.df.empty
        
        # Should have the same columns as world metrics
        for key in world.metrics:
            assert key in analytics.df.columns
        
        # Should have at least one row
        assert len(analytics.df) > 0
    
    def test_biodiversity_index(self, populated_world):
        """Test biodiversity index calculation"""
        world = populated_world
        analytics = Analytics(world)
        
        # Perform update to populate data
        analytics.update()
        
        # Calculate biodiversity
        biodiversity = analytics.get_biodiversity_index()
        
        # Should be a floating point value between 0 and ln(3)
        assert isinstance(biodiversity, float)
        assert 0 <= biodiversity <= np.log(3)
        
        # Test with imbalanced population
        # Clear all entities
        entity_ids = list(world.entities.keys())
        for entity_id in entity_ids:
            world.remove_entity(entity_id)
        
        # Add only one type of entity
        for i in range(10):
            plant = Plant(world.get_next_entity_id(), Position(i, i), "cactus")
            world.add_entity(plant)
            
        # Update metrics and analytics
        world._update_metrics()
        analytics.update()
        
        # Calculate biodiversity with only one type
        biodiversity_one_type = analytics.get_biodiversity_index()
        
        # Should be zero or very close to it with only one type
        assert biodiversity_one_type == 0
    
    def test_population_dataframe(self, populated_world):
        """Test getting population data"""
        world = populated_world
        analytics = Analytics(world)
        
        # Perform update to populate data
        analytics.update()
        
        # Get population data
        pop_df = analytics.get_population_dataframe()
        
        # Should return a DataFrame with specific columns
        assert isinstance(pop_df, pd.DataFrame)
        assert "time" in pop_df.columns
        assert "plant_count" in pop_df.columns
        assert "herbivore_count" in pop_df.columns
        assert "carnivore_count" in pop_df.columns
    
    def test_ecosystem_health(self, simple_world):
        """Test ecosystem health calculation"""
        world = simple_world
        analytics = Analytics(world)
        
        # Set some mock metrics to test health calculation
        world.metrics = {
            "time": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "plant_count": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            "herbivore_count": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            "carnivore_count": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "avg_plant_size": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
            "avg_herbivore_energy": [50, 50, 50, 50, 50, 50, 50, 50, 50, 50],
            "avg_carnivore_energy": [70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
            "avg_moisture": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            "avg_nutrients": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        }
        
        # Update analytics with mock data
        analytics.update()
        
        # Calculate health
        health = analytics.get_ecosystem_health()
        
        # Should be a value between 0 and 1
        assert isinstance(health, float)
        assert 0 <= health <= 1
    
    def test_health_with_unstable_ecosystem(self, simple_world):
        """Test that unstable ecosystems have lower health"""
        world = simple_world
        analytics = Analytics(world)
        
        # Set stable mock metrics
        world.metrics = {
            "time": list(range(10)),
            "plant_count": [50] * 10,
            "herbivore_count": [10] * 10,
            "carnivore_count": [2] * 10,
            "avg_plant_size": [1.5] * 10,
            "avg_herbivore_energy": [50] * 10,
            "avg_carnivore_energy": [70] * 10,
            "avg_moisture": [0.5] * 10,
            "avg_nutrients": [0.5] * 10,
        }
        
        # Update analytics with stable data
        analytics.update()
        stable_health = analytics.get_ecosystem_health()
        
        # Set unstable mock metrics with high variance
        world.metrics = {
            "time": list(range(10)),
            "plant_count": [10, 90, 20, 80, 30, 70, 40, 60, 10, 90],
            "herbivore_count": [2, 18, 4, 16, 6, 14, 8, 12, 2, 18],
            "carnivore_count": [0, 4, 1, 3, 2, 2, 0, 4, 1, 3],
            "avg_plant_size": [1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
            "avg_herbivore_energy": [30, 70, 30, 70, 30, 70, 30, 70, 30, 70],
            "avg_carnivore_energy": [50, 90, 50, 90, 50, 90, 50, 90, 50, 90],
            "avg_moisture": [0.5] * 10,
            "avg_nutrients": [0.5] * 10,
        }
        
        # Update analytics with unstable data
        analytics.update()
        unstable_health = analytics.get_ecosystem_health()
        
        # Unstable ecosystem should have lower health
        assert unstable_health < stable_health
    
    def test_chart_rendering(self, populated_world):
        """Test chart rendering capability"""
        analytics = Analytics(populated_world)
        
        # Perform update to populate data
        analytics.update()
        
        # Render chart
        chart = analytics.render_population_chart()
        
        # Chart should be a numpy array with dimensions for an RGB image
        assert isinstance(chart, np.ndarray)
        assert len(chart.shape) == 3  # Height, width, channels
        assert chart.shape[2] == 4  # RGBA channels
        assert chart.dtype == np.uint8 