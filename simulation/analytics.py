from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

from simulation.world import World
from models.base import EntityType
import pandas as pd


class Analytics:
    """Data analysis and visualization for the simulation"""

    def __init__(self, world: World):
        self.world = world
        self.df = pd.DataFrame()

    def update(self) -> None:
        """Update analytics data from the world"""
        # Create a new DataFrame row for the current time step
        current_metrics = {
            "time": self.world.time_step,
            "plant_count": len([e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT]),
            "herbivore_count": len([e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE]),
            "carnivore_count": len([e for e in self.world.entities.values() if e.entity_type == EntityType.CARNIVORE]),
            "water_count": len([e for e in self.world.entities.values() if e.entity_type == EntityType.WATER]),
            "avg_plant_size": 0.0,
            "avg_herbivore_energy": 0.0,
            "avg_carnivore_energy": 0.0,
            "avg_moisture": float(np.mean(self.world.environment.moisture)),
            "avg_nutrients": float(np.mean(self.world.environment.nutrients))
        }
        
        # Calculate averages if entities exist
        plants = [e for e in self.world.entities.values() if e.entity_type == EntityType.PLANT]
        if plants:
            current_metrics["avg_plant_size"] = float(np.mean([p.size for p in plants]))
            
        herbivores = [e for e in self.world.entities.values() if e.entity_type == EntityType.HERBIVORE]
        if herbivores:
            current_metrics["avg_herbivore_energy"] = float(np.mean([h.energy for h in herbivores]))
            
        carnivores = [e for e in self.world.entities.values() if e.entity_type == EntityType.CARNIVORE]
        if carnivores:
            current_metrics["avg_carnivore_energy"] = float(np.mean([c.energy for c in carnivores]))
        
        # Add the row to the DataFrame
        if self.df.empty:
            self.df = pd.DataFrame([current_metrics])
        else:
            self.df = pd.concat([self.df, pd.DataFrame([current_metrics])], ignore_index=True)

    def get_biodiversity_index(self) -> float:
        """Calculate a simple biodiversity index"""
        if self.df.empty:
            return 0.0  # Return float explicitly

        # Get latest counts
        latest = self.df.iloc[-1]

        # Simple Shannon diversity index
        total = latest["plant_count"] + latest["herbivore_count"] + latest["carnivore_count"]
        if total == 0:
            return 0.0  # Return float explicitly

        # Calculate proportions
        p_plant = latest["plant_count"] / total if total > 0 else 0.0
        p_herb = latest["herbivore_count"] / total if total > 0 else 0.0
        p_carn = latest["carnivore_count"] / total if total > 0 else 0.0

        # Shannon index
        shannon = 0.0
        for p in [p_plant, p_herb, p_carn]:
            if p > 0:
                shannon -= p * np.log(p)

        return float(shannon)  # Ensure we return a float

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
            # Return empty RGBA image (100x100 with 4 channels)
            return np.zeros((100, 100, 4), dtype=np.uint8)

        # Create matplotlib figure with transparent background
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        fig.patch.set_alpha(1.0)  # Make background opaque

        # Plot populations
        ax.plot(self.df["time"], self.df["plant_count"], 'g-', label="Plants")
        ax.plot(self.df["time"], self.df["herbivore_count"], 'b-', label="Herbivores")
        ax.plot(self.df["time"], self.df["carnivore_count"], 'r-', label="Carnivores")

        ax.set_xlabel("Time")
        ax.set_ylabel("Population")
        ax.set_title("Ecosystem Populations")
        ax.legend()

        # Convert to numpy array with RGBA (4 channels)
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf = canvas.buffer_rgba()  # Ensure RGBA format
        chart = np.asarray(buf)
        plt.close(fig)

        return chart
