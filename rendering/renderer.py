from config import CELL_WIDTH, CELL_HEIGHT, CELL_MARGIN, GREY, BLUE, RED, WHITE
import pygame as pg

from models.base import EntityType
from simulation.analytics import Analytics
from simulation.world import World


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
