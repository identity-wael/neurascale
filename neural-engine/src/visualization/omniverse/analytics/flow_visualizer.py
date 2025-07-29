"""Flow visualizer for neural connectivity and signal propagation."""

import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from dataclasses import dataclass

# from scipy.spatial.distance import cdist  # Reserved for future use

logger = logging.getLogger(__name__)


@dataclass
class FlowPath:
    """Neural flow path definition."""

    start_point: Tuple[float, float, float]
    end_point: Tuple[float, float, float]
    waypoints: List[Tuple[float, float, float]]
    strength: float
    speed: float
    color: Tuple[float, float, float, float]
    thickness: float = 0.005


@dataclass
class ConnectivityEdge:
    """Edge in connectivity graph."""

    source: str
    target: str
    weight: float
    direction: str  # "forward", "backward", "bidirectional"
    frequency_band: Optional[str] = None


class FlowVisualizer:
    """Visualizes neural connectivity and signal flow.

    Creates dynamic flow visualizations showing functional
    connectivity, signal propagation, and network dynamics.
    """

    def __init__(self) -> None:
        """Initialize flow visualizer."""
        self.flow_paths: List[FlowPath] = []
        self.connectivity_edges: List[ConnectivityEdge] = []

        # Visualization settings
        self.flow_style = "particles"  # particles, ribbons, tubes
        self.animation_speed = 1.0
        self.flow_density = 100  # particles per path

        # Connectivity visualization
        self.edge_thickness_scale = 0.01
        self.edge_opacity_scale = 0.8
        self.bundle_edges = True
        self.bundle_strength = 0.7

        # Frequency band colors
        self.frequency_colors = {
            "delta": (0.5, 0.0, 0.5, 0.8),  # Purple
            "theta": (0.0, 0.0, 1.0, 0.8),  # Blue
            "alpha": (0.0, 1.0, 0.0, 0.8),  # Green
            "beta": (1.0, 1.0, 0.0, 0.8),  # Yellow
            "gamma": (1.0, 0.0, 0.0, 0.8),  # Red
        }

        # Metrics
        self.network_metrics: Dict[str, float] = {}

        logger.info("FlowVisualizer initialized")

    async def create_connectivity_flow(
        self,
        connectivity_matrix: np.ndarray,
        node_positions: Dict[str, Tuple[float, float, float]],
        threshold: float = 0.3,
        frequency_band: Optional[str] = None,
    ) -> List[FlowPath]:
        """Create flow paths from connectivity matrix.

        Args:
            connectivity_matrix: Connectivity strengths between nodes
            node_positions: 3D positions of nodes
            threshold: Minimum connectivity strength to visualize
            frequency_band: Optional frequency band filter

        Returns:
            List of flow paths
        """
        flow_paths = []
        node_names = list(node_positions.keys())

        # Extract significant connections
        for i in range(len(node_names)):
            for j in range(len(node_names)):
                if i != j and connectivity_matrix[i, j] > threshold:
                    source = node_names[i]
                    target = node_names[j]
                    strength = connectivity_matrix[i, j]

                    # Create flow path
                    path = await self._create_path_between_nodes(
                        node_positions[source],
                        node_positions[target],
                        strength,
                        frequency_band,
                    )

                    flow_paths.append(path)

                    # Store edge for graph analysis
                    edge = ConnectivityEdge(
                        source=source,
                        target=target,
                        weight=strength,
                        direction="forward",
                        frequency_band=frequency_band,
                    )
                    self.connectivity_edges.append(edge)

        # Apply edge bundling if enabled
        if self.bundle_edges and len(flow_paths) > 10:
            flow_paths = await self._bundle_edges(flow_paths)

        self.flow_paths = flow_paths

        # Calculate network metrics
        await self._calculate_network_metrics(connectivity_matrix, node_names)

        return flow_paths

    async def create_propagation_flow(
        self,
        source_position: Tuple[float, float, float],
        propagation_map: Dict[str, Tuple[float, float]],
        node_positions: Dict[str, Tuple[float, float, float]],
    ) -> List[FlowPath]:
        """Create flow visualization for signal propagation.

        Args:
            source_position: Origin of propagation
            propagation_map: Node -> (arrival_time, amplitude) mapping
            node_positions: 3D positions of nodes

        Returns:
            List of flow paths showing propagation
        """
        flow_paths = []

        # Sort nodes by arrival time
        sorted_nodes = sorted(
            propagation_map.items(), key=lambda x: x[1][0]  # arrival time
        )

        # Create paths from source to each node
        for node, (arrival_time, amplitude) in sorted_nodes:
            if node in node_positions:
                # Speed based on arrival time
                distance = np.linalg.norm(
                    np.array(node_positions[node]) - np.array(source_position)
                )
                speed = distance / (arrival_time + 0.001)

                # Create path with delay
                path = FlowPath(
                    start_point=source_position,
                    end_point=node_positions[node],
                    waypoints=[],
                    strength=amplitude,
                    speed=speed,
                    color=self._amplitude_to_color(amplitude),
                    thickness=0.002 + amplitude * 0.008,
                )

                flow_paths.append(path)

        return flow_paths

    async def create_functional_network_flow(
        self,
        network_modules: Dict[str, List[str]],
        node_positions: Dict[str, Tuple[float, float, float]],
        inter_module_strength: float = 0.3,
        intra_module_strength: float = 0.7,
    ) -> List[FlowPath]:
        """Create flow for functional network modules.

        Args:
            network_modules: Module name -> list of nodes
            node_positions: 3D positions of nodes
            inter_module_strength: Connection strength between modules
            intra_module_strength: Connection strength within modules

        Returns:
            List of flow paths
        """
        flow_paths = []

        # Create intra-module connections
        for module_name, nodes in network_modules.items():
            module_color = self._get_module_color(module_name)

            # Connect nodes within module
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i + 1 :]:
                    if node1 in node_positions and node2 in node_positions:
                        path = FlowPath(
                            start_point=node_positions[node1],
                            end_point=node_positions[node2],
                            waypoints=[],
                            strength=intra_module_strength,
                            speed=2.0,
                            color=module_color,
                            thickness=0.003,
                        )
                        flow_paths.append(path)

        # Create inter-module connections (hubs)
        module_centers = {}
        for module_name, nodes in network_modules.items():
            # Find module center
            positions = [node_positions[n] for n in nodes if n in node_positions]
            if positions:
                center = np.mean(positions, axis=0)
                module_centers[module_name] = tuple(center)

        # Connect module centers
        module_names = list(module_centers.keys())
        for i, mod1 in enumerate(module_names):
            for mod2 in module_names[i + 1 :]:
                path = FlowPath(
                    start_point=module_centers[mod1],
                    end_point=module_centers[mod2],
                    waypoints=[],
                    strength=inter_module_strength,
                    speed=1.0,
                    color=(0.7, 0.7, 0.7, 0.5),
                    thickness=0.005,
                )
                flow_paths.append(path)

        return flow_paths

    async def _create_path_between_nodes(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        strength: float,
        frequency_band: Optional[str] = None,
    ) -> FlowPath:
        """Create flow path between two nodes.

        Args:
            start: Start position
            end: End position
            strength: Connection strength
            frequency_band: Optional frequency band

        Returns:
            Flow path
        """
        # Calculate curved path (bezier curve)
        waypoints = self._calculate_bezier_waypoints(start, end)

        # Determine color based on frequency band
        if frequency_band and frequency_band in self.frequency_colors:
            color = self.frequency_colors[frequency_band]
        else:
            # Default color based on strength
            color = self._strength_to_color(strength)

        return FlowPath(
            start_point=start,
            end_point=end,
            waypoints=waypoints,
            strength=strength,
            speed=1.0 + strength * 2.0,  # Faster for stronger connections
            color=color,
            thickness=self.edge_thickness_scale * (0.5 + strength * 0.5),
        )

    def _calculate_bezier_waypoints(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        curve_strength: float = 0.3,
    ) -> List[Tuple[float, float, float]]:
        """Calculate waypoints for curved path.

        Args:
            start: Start point
            end: End point
            curve_strength: How much to curve the path

        Returns:
            List of waypoints
        """
        start_array = np.array(start)
        end_array = np.array(end)

        # Calculate control points for bezier curve
        mid_point = (start_array + end_array) / 2

        # Add curvature perpendicular to connection
        direction = end_array - start_array
        perpendicular = np.cross(direction, [0, 0, 1])
        if np.linalg.norm(perpendicular) < 0.001:
            perpendicular = np.cross(direction, [1, 0, 0])

        perpendicular = perpendicular / np.linalg.norm(perpendicular)
        control_point = mid_point + perpendicular * curve_strength

        # Generate bezier curve points
        waypoints = []
        for t in np.linspace(0.2, 0.8, 5):
            # Quadratic bezier
            point = (
                (1 - t) ** 2 * start_array
                + 2 * (1 - t) * t * control_point
                + t**2 * end_array
            )
            waypoints.append(tuple(point))

        return waypoints

    async def _bundle_edges(self, flow_paths: List[FlowPath]) -> List[FlowPath]:
        """Apply edge bundling to reduce visual clutter.

        Args:
            flow_paths: Original flow paths

        Returns:
            Bundled flow paths
        """
        # Group paths by proximity and direction
        bundled_paths = []
        processed = set()

        for i, path1 in enumerate(flow_paths):
            if i in processed:
                continue

            # Find similar paths to bundle
            bundle = [path1]
            processed.add(i)

            for j, path2 in enumerate(flow_paths[i + 1 :], i + 1):
                if j in processed:
                    continue

                # Check if paths are similar enough to bundle
                if self._should_bundle(path1, path2):
                    bundle.append(path2)
                    processed.add(j)

            # Create bundled path
            if len(bundle) > 1:
                bundled_path = self._create_bundled_path(bundle)
                bundled_paths.append(bundled_path)
            else:
                bundled_paths.append(path1)

        return bundled_paths

    def _should_bundle(self, path1: FlowPath, path2: FlowPath) -> bool:
        """Check if two paths should be bundled.

        Args:
            path1: First path
            path2: Second path

        Returns:
            Whether to bundle
        """
        # Calculate distance between paths
        start_dist = np.linalg.norm(
            np.array(path1.start_point) - np.array(path2.start_point)
        )
        end_dist = np.linalg.norm(np.array(path1.end_point) - np.array(path2.end_point))

        # Bundle if endpoints are close
        return start_dist < 0.2 and end_dist < 0.2

    def _create_bundled_path(self, paths: List[FlowPath]) -> FlowPath:
        """Create single bundled path from multiple paths.

        Args:
            paths: Paths to bundle

        Returns:
            Bundled path
        """
        # Average positions
        start_points = [np.array(p.start_point) for p in paths]
        end_points = [np.array(p.end_point) for p in paths]

        avg_start = tuple(np.mean(start_points, axis=0))
        avg_end = tuple(np.mean(end_points, axis=0))

        # Combine strengths
        total_strength = sum(p.strength for p in paths)
        avg_strength = total_strength / len(paths)

        # Average colors
        colors = [p.color for p in paths]
        avg_color = tuple(np.mean(colors, axis=0))

        # Create waypoints with bundling effect
        waypoints = self._calculate_bezier_waypoints(
            avg_start, avg_end, curve_strength=0.3 * self.bundle_strength
        )

        return FlowPath(
            start_point=avg_start,
            end_point=avg_end,
            waypoints=waypoints,
            strength=avg_strength,
            speed=np.mean([p.speed for p in paths]),
            color=avg_color,
            thickness=self.edge_thickness_scale * np.sqrt(total_strength),
        )

    async def _calculate_network_metrics(
        self, connectivity_matrix: np.ndarray, node_names: List[str]
    ) -> None:
        """Calculate network topology metrics.

        Args:
            connectivity_matrix: Connectivity matrix
            node_names: Node identifiers
        """
        n_nodes = len(node_names)

        # Degree centrality
        degrees = np.sum(connectivity_matrix > 0, axis=1)
        self.network_metrics["avg_degree"] = np.mean(degrees)
        self.network_metrics["max_degree"] = np.max(degrees)

        # Density
        possible_edges = n_nodes * (n_nodes - 1)
        actual_edges = np.sum(connectivity_matrix > 0)
        self.network_metrics["density"] = actual_edges / possible_edges

        # Clustering coefficient (simplified)
        clustering_coeffs = []
        for i in range(n_nodes):
            neighbors = np.where(connectivity_matrix[i] > 0)[0]
            if len(neighbors) > 1:
                # Check connections between neighbors
                neighbor_connections = 0
                for j in range(len(neighbors)):
                    for k in range(j + 1, len(neighbors)):
                        if connectivity_matrix[neighbors[j], neighbors[k]] > 0:
                            neighbor_connections += 1

                possible_connections = len(neighbors) * (len(neighbors) - 1) / 2
                clustering_coeffs.append(neighbor_connections / possible_connections)

        self.network_metrics["clustering_coefficient"] = (
            np.mean(clustering_coeffs) if clustering_coeffs else 0.0
        )

        # Modularity (simplified - based on community detection)
        # This is a placeholder - real implementation would use proper algorithms
        self.network_metrics["modularity"] = 0.3

        logger.info(f"Network metrics calculated: {self.network_metrics}")

    def _strength_to_color(self, strength: float) -> Tuple[float, float, float, float]:
        """Convert connection strength to color.

        Args:
            strength: Connection strength (0-1)

        Returns:
            RGBA color
        """
        # Blue to red gradient
        if strength < 0.5:
            t = strength * 2
            return (t, 0.0, 1.0 - t, 0.5 + strength * 0.5)
        else:
            t = (strength - 0.5) * 2
            return (1.0, 1.0 - t, 0.0, 0.5 + strength * 0.5)

    def _amplitude_to_color(
        self, amplitude: float
    ) -> Tuple[float, float, float, float]:
        """Convert signal amplitude to color.

        Args:
            amplitude: Signal amplitude

        Returns:
            RGBA color
        """
        # Green to red based on amplitude
        clamped = np.clip(amplitude, 0, 1)
        return (clamped, 1.0 - clamped, 0.0, 0.7 + clamped * 0.3)

    def _get_module_color(self, module_name: str) -> Tuple[float, float, float, float]:
        """Get color for network module.

        Args:
            module_name: Module identifier

        Returns:
            RGBA color
        """
        # Predefined module colors
        module_colors = {
            "default_mode": (0.8, 0.2, 0.2, 0.8),
            "executive": (0.2, 0.8, 0.2, 0.8),
            "salience": (0.2, 0.2, 0.8, 0.8),
            "sensorimotor": (0.8, 0.8, 0.2, 0.8),
            "visual": (0.8, 0.2, 0.8, 0.8),
            "auditory": (0.2, 0.8, 0.8, 0.8),
        }

        return module_colors.get(module_name, (0.5, 0.5, 0.5, 0.8))

    async def animate_flow(self, time_step: float) -> List[Dict[str, Any]]:
        """Generate animation frame for flow visualization.

        Args:
            time_step: Current animation time

        Returns:
            List of particle positions and properties
        """
        particles = []

        for path in self.flow_paths:
            # Calculate particles along path
            path_particles = await self._generate_path_particles(path, time_step)
            particles.extend(path_particles)

        return particles

    async def _generate_path_particles(
        self, path: FlowPath, time_step: float
    ) -> List[Dict[str, Any]]:
        """Generate particles for a flow path.

        Args:
            path: Flow path
            time_step: Current time

        Returns:
            List of particles
        """
        particles = []

        # Calculate path length
        points = [path.start_point] + path.waypoints + [path.end_point]
        path_length = 0.0
        for i in range(1, len(points)):
            path_length += np.linalg.norm(np.array(points[i]) - np.array(points[i - 1]))

        # Generate particles along path
        num_particles = int(self.flow_density * path.strength)

        for i in range(num_particles):
            # Calculate particle position along path
            phase = (i / num_particles + time_step * path.speed) % 1.0
            position = self._interpolate_path_position(points, phase)

            particles.append(
                {
                    "position": position,
                    "color": path.color,
                    "size": path.thickness * 2,
                    "velocity": path.speed,
                    "lifetime": 1.0 / path.speed,
                }
            )

        return particles

    def _interpolate_path_position(
        self, points: List[Tuple[float, float, float]], t: float
    ) -> Tuple[float, float, float]:
        """Interpolate position along path.

        Args:
            points: Path points
            t: Parameter (0-1)

        Returns:
            Interpolated position
        """
        # Calculate segment lengths
        segments = []
        total_length = 0.0

        for i in range(1, len(points)):
            length = np.linalg.norm(np.array(points[i]) - np.array(points[i - 1]))
            segments.append(length)
            total_length += length

        # Find which segment contains position
        target_length = t * total_length
        current_length = 0.0

        for i, segment_length in enumerate(segments):
            if current_length + segment_length >= target_length:
                # Interpolate within this segment
                segment_t = (target_length - current_length) / segment_length
                start = np.array(points[i])
                end = np.array(points[i + 1])
                position = start + segment_t * (end - start)
                return tuple(position)

            current_length += segment_length

        # Return end point if we've gone past
        return points[-1]

    def get_network_metrics(self) -> Dict[str, float]:
        """Get calculated network metrics.

        Returns:
            Network topology metrics
        """
        return self.network_metrics.copy()

    def set_flow_style(self, style: str) -> None:
        """Set flow visualization style.

        Args:
            style: Flow style (particles, ribbons, tubes)
        """
        if style in ["particles", "ribbons", "tubes"]:
            self.flow_style = style
            logger.info(f"Flow style set to: {style}")

    def set_animation_speed(self, speed: float) -> None:
        """Set flow animation speed.

        Args:
            speed: Speed multiplier
        """
        self.animation_speed = speed
        logger.info(f"Animation speed set to: {speed}x")
