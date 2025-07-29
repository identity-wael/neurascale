"""Particle system for neural activity visualization."""

import logging
from typing import Dict, List, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)


class Particle:
    """Individual particle for neural visualization."""

    def __init__(
        self,
        position: np.ndarray,
        velocity: np.ndarray,
        lifetime: float,
        color: Tuple[float, float, float, float],
        size: float = 0.01,
    ):
        """Initialize particle.

        Args:
            position: 3D position
            velocity: 3D velocity vector
            lifetime: Particle lifetime in seconds
            color: RGBA color
            size: Particle size
        """
        self.position = position.astype(np.float32)
        self.velocity = velocity.astype(np.float32)
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.size = size
        self.active = True

    def update(self, dt: float) -> None:
        """Update particle state.

        Args:
            dt: Time step
        """
        if not self.active:
            return

        # Update position
        self.position += self.velocity * dt

        # Update age
        self.age += dt

        # Check lifetime
        if self.age >= self.lifetime:
            self.active = False

    def get_normalized_age(self) -> float:
        """Get age as fraction of lifetime."""
        return min(self.age / self.lifetime, 1.0) if self.lifetime > 0 else 1.0


class ParticleSystem:
    """GPU-accelerated particle system for neural activity.

    Visualizes neural activity as dynamic particle flows,
    useful for showing signal propagation and network dynamics.
    """

    def __init__(self) -> None:
        """Initialize particle system."""
        self.particles: List[Particle] = []
        self.max_particles = 100000
        self.emission_rate = 1000.0  # particles per second

        # Emitter settings
        self.emitters: List[Dict[str, Any]] = []

        # Physics settings
        self.gravity = np.array([0.0, -0.1, 0.0])
        self.drag = 0.98
        self.turbulence_strength = 0.1

        # Visual settings
        self.particle_texture = "neurascale://textures/neural_spark.png"
        self.blend_mode = "additive"
        self.size_over_lifetime = "decreasing"
        self.color_over_lifetime = "fade_out"

        # Performance
        self.use_gpu_simulation = True
        self.spatial_hash_grid = {}

        logger.info("ParticleSystem initialized")

    async def initialize(self) -> bool:
        """Initialize particle system resources.

        Returns:
            Success status
        """
        try:
            # Initialize GPU resources if available
            if self.use_gpu_simulation:
                await self._initialize_gpu_resources()

            # Create default emitters
            self._create_default_emitters()

            # Set up spatial partitioning
            self._initialize_spatial_hash()

            logger.info("Particle system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize particle system: {e}")
            return False

    def add_emitter(
        self,
        position: Tuple[float, float, float],
        emitter_type: str = "point",
        **kwargs,
    ) -> str:
        """Add particle emitter.

        Args:
            position: Emitter position
            emitter_type: Type of emitter (point, sphere, cone)
            **kwargs: Additional emitter parameters

        Returns:
            Emitter ID
        """
        emitter_id = f"emitter_{len(self.emitters)}"

        emitter = {
            "id": emitter_id,
            "type": emitter_type,
            "position": np.array(position),
            "active": True,
            "emission_rate": kwargs.get("emission_rate", 100.0),
            "particle_lifetime": kwargs.get("lifetime", 2.0),
            "initial_velocity": kwargs.get("velocity", (0.0, 1.0, 0.0)),
            "velocity_variance": kwargs.get("velocity_variance", 0.5),
            "color": kwargs.get("color", (1.0, 0.5, 0.0, 1.0)),
            "size": kwargs.get("size", 0.01),
        }

        if emitter_type == "sphere":
            emitter["radius"] = kwargs.get("radius", 0.1)
        elif emitter_type == "cone":
            emitter["angle"] = kwargs.get("angle", 45.0)
            emitter["direction"] = kwargs.get("direction", (0.0, 1.0, 0.0))

        self.emitters.append(emitter)
        logger.info(f"Added {emitter_type} emitter at {position}")

        return emitter_id

    async def emit_burst(
        self, position: Tuple[float, float, float], count: int, **kwargs
    ) -> None:
        """Emit burst of particles.

        Args:
            position: Burst origin
            count: Number of particles
            **kwargs: Particle parameters
        """
        for _ in range(min(count, self.max_particles - len(self.particles))):
            # Random velocity in sphere
            velocity = np.random.randn(3)
            velocity = velocity / np.linalg.norm(velocity)
            velocity *= kwargs.get("speed", 1.0)

            # Create particle
            particle = Particle(
                position=np.array(position) + np.random.randn(3) * 0.01,
                velocity=velocity,
                lifetime=kwargs.get("lifetime", 1.0),
                color=kwargs.get("color", (1.0, 1.0, 0.0, 1.0)),
                size=kwargs.get("size", 0.01),
            )

            self.particles.append(particle)

    async def update(self, dt: float) -> None:
        """Update particle system.

        Args:
            dt: Time step
        """
        # Emit new particles
        await self._emit_particles(dt)

        # Update existing particles
        if self.use_gpu_simulation:
            await self._update_particles_gpu(dt)
        else:
            self._update_particles_cpu(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if p.active]

        # Update spatial hash
        self._update_spatial_hash()

    async def _emit_particles(self, dt: float) -> None:
        """Emit particles from active emitters."""
        for emitter in self.emitters:
            if not emitter["active"]:
                continue

            # Calculate particles to emit
            particles_to_emit = int(emitter["emission_rate"] * dt)

            for _ in range(
                min(particles_to_emit, self.max_particles - len(self.particles))
            ):
                # Generate particle based on emitter type
                if emitter["type"] == "point":
                    position = emitter["position"].copy()
                elif emitter["type"] == "sphere":
                    # Random point in sphere
                    offset = np.random.randn(3)
                    offset = (
                        offset
                        / np.linalg.norm(offset)
                        * np.random.rand()
                        * emitter["radius"]
                    )
                    position = emitter["position"] + offset
                elif emitter["type"] == "cone":
                    # Random point in cone
                    angle = np.radians(emitter["angle"])
                    _ = np.random.rand() * angle  # theta (unused for now)
                    _ = np.random.rand() * 2 * np.pi  # phi (unused for now)

                    direction = np.array(emitter["direction"])
                    # Convert to cone point (simplified)
                    position = emitter["position"] + direction * 0.1
                else:
                    position = emitter["position"].copy()

                # Generate velocity
                base_velocity = np.array(emitter["initial_velocity"])
                variance = emitter["velocity_variance"]
                velocity = base_velocity + np.random.randn(3) * variance

                # Create particle
                particle = Particle(
                    position=position,
                    velocity=velocity,
                    lifetime=emitter["particle_lifetime"],
                    color=emitter["color"],
                    size=emitter["size"],
                )

                self.particles.append(particle)

    def _update_particles_cpu(self, dt: float) -> None:
        """Update particles on CPU."""
        for particle in self.particles:
            if not particle.active:
                continue

            # Apply physics
            particle.velocity += self.gravity * dt
            particle.velocity *= self.drag

            # Add turbulence
            if self.turbulence_strength > 0:
                turbulence = np.random.randn(3) * self.turbulence_strength
                particle.velocity += turbulence * dt

            # Update particle
            particle.update(dt)

            # Update visual properties
            self._update_particle_visuals(particle)

    async def _update_particles_gpu(self, dt: float) -> None:
        """Update particles on GPU (simulated)."""
        # In production, would use actual GPU compute
        self._update_particles_cpu(dt)

    def _update_particle_visuals(self, particle: Particle) -> None:
        """Update particle visual properties based on age."""
        normalized_age = particle.get_normalized_age()

        # Size over lifetime
        if self.size_over_lifetime == "decreasing":
            particle.size *= 1.0 - normalized_age * 0.5
        elif self.size_over_lifetime == "increasing":
            particle.size *= 1.0 + normalized_age * 0.5

        # Color over lifetime
        if self.color_over_lifetime == "fade_out":
            # Fade alpha
            color = list(particle.color)
            color[3] *= 1.0 - normalized_age
            particle.color = tuple(color)
        elif self.color_over_lifetime == "temperature":
            # Cool down from hot to cold
            t = normalized_age
            if t < 0.5:
                # White to yellow
                particle.color = (1.0, 1.0, 1.0 - t, particle.color[3])
            else:
                # Yellow to red
                particle.color = (1.0, 2.0 - 2.0 * t, 0.0, particle.color[3])

    def _create_default_emitters(self) -> None:
        """Create default particle emitters."""
        # Neural spike emitter
        self.add_emitter(
            position=(0.0, 0.0, 0.0),
            emitter_type="point",
            emission_rate=50.0,
            lifetime=1.5,
            velocity=(0.0, 0.5, 0.0),
            color=(0.2, 0.8, 1.0, 1.0),
            size=0.005,
        )

    async def _initialize_gpu_resources(self) -> None:
        """Initialize GPU resources for particle simulation."""
        # In production, would set up GPU compute shaders
        logger.info("GPU particle simulation initialized (simulated)")

    def _initialize_spatial_hash(self) -> None:
        """Initialize spatial hash grid for performance."""
        self.spatial_hash_grid = {}
        self.grid_cell_size = 0.1  # 10cm cells

    def _update_spatial_hash(self) -> None:
        """Update spatial hash grid with particle positions."""
        self.spatial_hash_grid.clear()

        for particle in self.particles:
            if not particle.active:
                continue

            # Calculate grid cell
            cell = tuple(
                int(particle.position[i] // self.grid_cell_size) for i in range(3)
            )

            if cell not in self.spatial_hash_grid:
                self.spatial_hash_grid[cell] = []

            self.spatial_hash_grid[cell].append(particle)

    def get_particles_near(
        self, position: Tuple[float, float, float], radius: float
    ) -> List[Particle]:
        """Get particles within radius of position.

        Args:
            position: Query position
            radius: Search radius

        Returns:
            List of nearby particles
        """
        nearby_particles = []
        pos = np.array(position)

        # Check relevant grid cells
        cells_to_check = int(np.ceil(radius / self.grid_cell_size))
        center_cell = tuple(int(pos[i] // self.grid_cell_size) for i in range(3))

        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                for dz in range(-cells_to_check, cells_to_check + 1):
                    cell = (
                        center_cell[0] + dx,
                        center_cell[1] + dy,
                        center_cell[2] + dz,
                    )

                    if cell in self.spatial_hash_grid:
                        for particle in self.spatial_hash_grid[cell]:
                            if np.linalg.norm(particle.position - pos) <= radius:
                                nearby_particles.append(particle)

        return nearby_particles

    def create_neural_flow(
        self, path: List[Tuple[float, float, float]], intensity: float = 1.0
    ) -> None:
        """Create particle flow along neural pathway.

        Args:
            path: List of 3D points defining pathway
            intensity: Flow intensity (affects particle count)
        """
        if len(path) < 2:
            return

        # Add emitters along path
        for i in range(len(path) - 1):
            start = np.array(path[i])
            end = np.array(path[i + 1])
            direction = end - start
            direction = direction / np.linalg.norm(direction)

            self.add_emitter(
                position=tuple(start),
                emitter_type="point",
                emission_rate=intensity * 50.0,
                lifetime=2.0,
                velocity=tuple(direction * 0.5),
                velocity_variance=0.1,
                color=(0.0, 0.8, 1.0, 0.8),
                size=0.003,
            )

    def get_particle_count(self) -> int:
        """Get current active particle count."""
        return sum(1 for p in self.particles if p.active)

    def clear_all_particles(self) -> None:
        """Remove all particles."""
        self.particles.clear()
        self.spatial_hash_grid.clear()
        logger.info("All particles cleared")

    def set_emitter_active(self, emitter_id: str, active: bool) -> None:
        """Enable/disable particle emitter.

        Args:
            emitter_id: Emitter ID
            active: Active state
        """
        for emitter in self.emitters:
            if emitter["id"] == emitter_id:
                emitter["active"] = active
                logger.info(
                    f"Emitter {emitter_id} set to {'active' if active else 'inactive'}"
                )
                return

        logger.warning(f"Emitter not found: {emitter_id}")
