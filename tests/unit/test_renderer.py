import pytest
import pygame as pg
from models.base import Position, EntityType
from models.plants import Plant
from models.animals import Herbivore, Carnivore
from rendering.renderer import Renderer

@pytest.mark.unit
class TestRenderer:
    
    def test_renderer_initialization(self, mock_pygame_init):
        """Test that renderer initializes correctly"""
        renderer = Renderer(width=800, height=600)
        
        # Check dimensions
        assert renderer.width == 800
        assert renderer.height == 600
        
        # Check pygame display is set up
        assert isinstance(renderer.display, pg.Surface)
        assert isinstance(renderer.background, pg.Surface)
        assert isinstance(renderer.font, pg.font.Font)
    
    def test_render_function_calls_render_methods(self, mock_pygame_init, simple_world, monkeypatch, analytics):
        """Test that render calls expected methods"""
        renderer = Renderer(width=800, height=600)
        
        # Set up mocks to track method calls
        calls = []
        monkeypatch.setattr(renderer, "_render_environment", lambda world: calls.append("environment"))
        monkeypatch.setattr(renderer, "_render_entities", lambda world: calls.append("entities"))
        monkeypatch.setattr(renderer, "_render_stats", lambda world, analytics: calls.append("stats"))
        monkeypatch.setattr(pg.display, "update", lambda: calls.append("display_update"))
        
        # Call render
        renderer.render(simple_world, analytics)
        
        # Check that all methods were called in the right order
        assert calls == ["environment", "entities", "stats", "display_update"]
    
    def test_render_environment(self, mock_pygame_init, simple_world):
        """Test environment rendering"""
        renderer = Renderer(width=800, height=600)
        
        # Set up some moisture for testing
        simple_world.environment.moisture[5:10, 5:10] = 0.8
        
        # Call environment rendering method
        renderer._render_environment(simple_world)
        
        # Hard to test visual output, but should execute without errors
        assert True
    
    def test_render_entities(self, mock_pygame_init, populated_world, monkeypatch):
        """Test entity rendering"""
        renderer = Renderer(width=800, height=600)
        world = populated_world
        
        # Set up mocks to track entity rendering
        rendered_entities = []
        
        # Mock the draw method to track calls
        original_draw = pg.draw.rect
        
        def mock_draw_rect(surface, color, rect, *args, **kwargs):
            rendered_entities.append((color, rect))
            return original_draw(surface, color, rect, *args, **kwargs)
        
        monkeypatch.setattr(pg.draw, "rect", mock_draw_rect)
        
        # Call entity rendering method
        renderer._render_entities(world)
        
        # Should render all entities in the world
        assert len(rendered_entities) == len(world.entities)
    
    def test_render_stats(self, mock_pygame_init, populated_world, analytics):
        """Test stats rendering"""
        renderer = Renderer(width=800, height=600)
        world = populated_world
        
        # Update analytics to have data
        analytics.update()
        
        # Call stats rendering method
        renderer._render_stats(world, analytics)
        
        # Hard to test visual output, but should execute without errors
        assert True
    
    def test_render_basic_world(self, mock_pygame_init, simple_world):
        """Test rendering a basic world"""
        renderer = Renderer(width=800, height=600)
        
        # Add a plant to the world
        plant = Plant(simple_world.get_next_entity_id(), Position(5, 5), "cactus")
        simple_world.add_entity(plant)
        
        # Call render
        renderer.render(simple_world)
        
        # Hard to test visual output, but should execute without errors
        assert True
    
    def test_render_with_different_entity_types(self, mock_pygame_init, populated_world, analytics):
        """Test rendering with different entity types"""
        renderer = Renderer(width=800, height=600)
        world = populated_world
        
        # Update analytics to have data
        analytics.update()
        
        # Call render
        renderer.render(world, analytics)
        
        # Hard to test visual output, but should execute without errors
        assert True
    
    def test_render_water_entity(self, mock_pygame_init, simple_world):
        """Test rendering water entities"""
        renderer = Renderer(800, 600)
        
        # Create a water entity
        from models.base import Entity, Position, EntityType
        water_entity = Entity(1, Position(5, 5), EntityType.WATER)
        simple_world.add_entity(water_entity)
        
        # Check that the water entity exists in the world
        assert any(e.entity_type == EntityType.WATER for e in simple_world.entities.values())
        
        # Should not raise any errors when rendering
        renderer._render_entities(simple_world)
        
        # Test the full render method with the water entity
        renderer.render(simple_world) 