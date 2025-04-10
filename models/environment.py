import numpy as np


class Environment:
    """Environmental systems including water, nutrients, and weather"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Environmental grids
        self.moisture = np.zeros((width, height), dtype=np.float32)
        self.nutrients = np.ones((width, height), dtype=np.float32) * 0.5  # Start with medium nutrients
        self.temperature = np.ones((width, height), dtype=np.float32) * 0.7  # Desert is hot

        # Weather state
        self.season = 0  # 0=spring, 1=summer, 2=fall, 3=winter
        self.rain_chance = 0.005  # Daily chance of rain
        self.wind_direction = 0  # Radians
        self.wind_strength = 0.2  # 0-1 scale

        # Create some initial water sources (oases)
        self._create_oases()

    def _create_oases(self, num_oases: int = 3) -> None:
        """Create initial water sources"""
        for _ in range(num_oases):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)

            # Create a small area with high moisture
            radius = np.random.randint(3, 8)
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if (nx >= 0 and nx < self.width and
                            ny >= 0 and ny < self.height):
                        # Calculate distance from center
                        dist = np.sqrt(dx ** 2 + dy ** 2)
                        if dist <= radius:
                            # More water in the center, less at the edges
                            moisture = max(0, 1.0 - (dist / radius))
                            self.moisture[nx, ny] = max(self.moisture[nx, ny], moisture)

    def update(self) -> None:
        """Update environmental conditions for one time step"""
        # Process water diffusion
        self._diffuse_moisture()

        # Process nutrient cycling
        self._update_nutrients()

        # Check for weather events
        self._update_weather()

    def _diffuse_moisture(self) -> None:
        """Simulate water movement through soil"""
        # Simple diffusion using convolution
        kernel = np.array([[0.05, 0.1, 0.05],
                           [0.1, 0.4, 0.1],
                           [0.05, 0.1, 0.05]])

        # TODO: Replace with numba optimized diffusion
        # For now, just do simple blurring
        from scipy.ndimage import convolve
        self.moisture = convolve(self.moisture, kernel, mode='constant', cval=0)

        # Apply evaporation based on temperature
        self.moisture *= (1.0 - 0.01 * self.temperature)

    def _update_nutrients(self) -> None:
        """Update nutrient levels in soil"""
        # Very slow natural regeneration of nutrients
        self.nutrients += 0.0001
        # Cap at maximum
        self.nutrients = np.clip(self.nutrients, 0, 1.0)

    def _update_weather(self) -> None:
        """Update weather conditions"""
        # Random chance of rain
        if np.random.random() < self.rain_chance:
            self._create_rainfall()

        # Update wind
        self.wind_direction += np.random.normal(0, 0.1)
        self.wind_strength = np.clip(self.wind_strength + np.random.normal(0, 0.05), 0.1, 0.9)

    def _create_rainfall(self) -> None:
        """Simulate a rainfall event"""
        # Add moisture across the map with some randomness
        rain_intensity = np.random.uniform(0.2, 0.5)
        rain_map = np.random.uniform(0, rain_intensity, size=(self.width, self.height))
        self.moisture += rain_map
        self.moisture = np.clip(self.moisture, 0, 1.0)  # Cap at 1.0


