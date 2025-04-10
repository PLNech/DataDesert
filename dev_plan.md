# DataDesert v2 - Development Rush Plan

## Current Project Analysis

The current DataDesert is a modified Conway's Game of Life implementation with several enhancements:

- Custom growth and decay mechanics using NumPy
- Simple color-based visualization using PyGame
- Basic interaction (mouse click to add cells, keyboard shortcuts)
- Stats display for simulation metrics
- Pause/resume and reset functionality

The core simulation runs on a rectangular grid where cells evolve based on both deterministic rules (Conway) and stochastic processes (random growth and decay). The current implementation mixes simulation logic with rendering and lacks proper separation of concerns for extensibility.

## Vision for v2

Transform DataDesert from a cellular automaton demo into an engaging ecosystem simulator with:

1. Multiple organism types with genetic traits and behaviors
2. Environmental systems (water, nutrients, weather)
3. Analytics and progression features
4. Improved performance and architecture

## Technical Requirements

### Architecture

- Implement entity-component system for simulation entities
- Use Pydantic for data models and validation
- Separate rendering from simulation logic (`./models/` directory)
- Create dedicated modules for Plants, Animals, and Environment

### Performance

- Implement Numba for JIT compilation of critical functions
- Add spatial partitioning to reduce neighbor calculations
- Design for CPU fallback when OpenCL acceleration isn't available
- Profile and optimize bottlenecks

### Data Science Integration

- Use pandas DataFrames for ecosystem metrics tracking
- Implement scikit-learn for pattern recognition
- Create matplotlib-based analytics dashboard
- Track metrics such as:
  - Biodiversity index
  - Population dynamics
  - Resource distribution
  - Energy flow through the ecosystem
  - Genetic diversity over time

## Ecosystem Design

### Plant System

- Multiple desert plant species with different traits:
  - Cacti (water-storing, slow-growing, high resilience)
  - Desert grasses (fast-growing, drought-sensitive)
  - Succulents (moderate growth, moderate resilience)
  - Desert wildflowers (fast lifecycle, seed production)
- Growth patterns based on:
  - Access to water/moisture
  - Nutrient availability
  - Sunlight/shade conditions
- Seed dispersal mechanics for colonization

### Animal System

- Genetic algorithm for evolving traits:
  - Speed (movement rate)
  - Size (affects energy needs and predation)
  - Diet preference (herbivore, carnivore, omnivore)
  - Sensory range (how far they can detect food/threats)
- Behaviors:
  - Foraging strategies
  - Predator-prey dynamics
  - Mating and reproduction
  - Territory establishment
- Energy system:
  - Gain energy from food
  - Lose energy with movement and time
  - Death upon energy depletion

### Environment

- Water system:
  - Oasis/water sources
  - Soil moisture levels
  - Evaporation and collection
- Weather patterns:
  - Temperature fluctuations
  - Occasional rainfall events
  - Drought periods
- Seasonal cycles affecting growth rates and behavior

## Game Elements

### User Interaction

- Creative mode tools:
  - Species selector
  - Environmental modifiers
  - Event triggers (rain, drought, etc.)
- Time controls (pause, speed up, slow down)
- Camera controls for viewing different areas

### Progression System

- Achievements for ecosystem milestones
- Progressive feature unlocking:
  - Start with basic plants only
  - Unlock animals after plant population threshold
  - Unlock weather systems after biodiversity milestone
  - Unlock genetic manipulation after observation time
- Ecosystem health score and analytics dashboard

## Project File Structure

```
datadesert/
├── __init__.py
├── main.py  # Entry point
├── config.py  # Configuration constants
├── models/
│   ├── __init__.py
│   ├── base.py  # Base entity classes
│   ├── plants.py  # Plant species and behaviors
│   ├── animals.py  # Animal species and behaviors
│   └── environment.py  # Environmental systems
├── simulation/
│   ├── __init__.py
│   ├── world.py  # Main simulation container
│   ├── genetics.py  # Genetic algorithm implementation
│   ├── spatial.py  # Spatial partitioning and optimization
│   └── analytics.py  # Data collection and analysis
├── rendering/
│   ├── __init__.py
│   ├── renderer.py  # Base rendering functionality
│   ├── ui.py  # User interface elements
│   └── dashboard.py  # Analytics visualization
├── controllers/
│   ├── __init__.py
│   ├── input_handler.py  # User input processing
│   ├── game_manager.py  # Game state management
│   └── achievement_system.py  # Progress tracking
└── utils/
    ├── __init__.py
    ├── optimization.py  # Performance helpers
    └── persistence.py  # Save/load functionality
```

## Development Phases

### Phase 1: Architecture Refactoring
- Implement basic ECS architecture
- Separate rendering from simulation
- Set up data structures for metrics tracking

### Phase 2: Ecosystem Basics
- Implement multiple plant species
- Add basic environment variables (moisture, nutrients)
- Create simple animal behaviors

### Phase 3: Genetics and Evolution
- Implement genetic traits and inheritance
- Add energy system and life cycles
- Create basic predator-prey relationships

### Phase 4: UI and Analytics
- Develop metrics dashboard
- Implement achievement system
- Add user interaction tools

### Phase 5: Optimization
- Profile and optimize performance bottlenecks
- Implement Numba JIT compilation
- Add optional OpenCL acceleration

## Success Criteria

1. Simulation runs at 30+ FPS with 10,000+ entities
2. At least 3 plant species and 2 animal species with distinct behaviors
3. Observable genetic drift and adaptation over time
4. User-friendly interface with basic analytics
5. Achievement system that guides discovery

## Remaining Tasks for Dev Rush

### Critical Bugs and Fixes
1. **Plant Species Access Fix**: Implement robust species lookup by both key and name
   - Add helper function to find species by name (already fixed)
   - Add error handling for invalid species names

2. **Water Balance Issues**: 
   - Adjust moisture diffusion rates (decrease default evaporation)
   - Increase plant water efficiency
   - Add more moisture to initial environment

3. **UI Controls**: 
   - Add button-based interface for tools and actions
   - Create tool panel on right side of screen
   - Implement hover tooltips for controls

### Animal System TODOs
1. **Water Seeking Behavior**: Complete `_seek_water` method
   - Implement pathfinding toward nearest water source
   - Add water detection based on sense range

2. **Carnivore Hunting**: Implement hunting behaviors
   - Complete `_seek_food` method for carnivores
   - Implement `_hunt_herbivore` with success chance based on traits
   - Add escape behaviors for herbivores

3. **Mating System**: Complete reproduction mechanics
   - Finish `_seek_mate` behavior for finding compatible mates
   - Add attraction based on genetic compatibility
   - Complete animal mating logic in `World._process_reproduction`

### Environment TODOs
1. **Numba-Optimized Diffusion**: Replace scipy function
   - Implement JIT-compiled moisture diffusion
   - Add performance monitoring for diffusion operation

2. **Season Display and Effects**: 
   - Add visual representation of current season in UI
   - Implement seasonal effects on growth rates
   - Add seasonal color changes to environment

3. **Weather System Integration**:
   - Connect weather events to visual effects
   - Implement wind effects on seed dispersal
   - Add temperature effects on water evaporation

### UI and Rendering TODOs
1. **Button Controls Interface**:
   - Create `Button` class in rendering/ui.py
   - Implement tool selection panel
   - Add speed control buttons

2. **Analytics Dashboard**:
   - Integrate charts with main UI
   - Add toggle for expanded analytics view
   - Create population graphs and trends

3. **Environmental Indicators**:
   - Add season and weather indicators
   - Display temperature and moisture levels
   - Create heatmap visualization option

### Performance Optimization TODOs
1. **JIT Compilation**:
   - Apply Numba to critical simulation functions:
     - Moisture diffusion
     - Entity neighbor calculations
     - Genetic algorithm operations

2. **Spatial Partitioning**:
   - Implement grid-based spatial index
   - Optimize entity lookup by location
   - Reduce iteration in neighbor searches

3. **CPU/GPU Fallback**:
   - Add detection for OpenCL availability
   - Implement fallback paths for critical functions
   - Create performance settings UI

### Progression and Achievement TODOs
1. **Achievement System**:
   - Complete remaining achievement checks
   - Add visual notification for unlocked achievements
   - Create achievement panel in UI

2. **Feature Unlocking**:
   - Add visual indicators for unlocked features
   - Create tutorial prompts for new features
   - Balance unlock thresholds

3. **Statistics and Records**:
   - Track ecosystem records (largest population, longest-lived entities)
   - Add metrics for ecosystem stability
   - Create end-of-session summary