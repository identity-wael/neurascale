"""Heatmap generator for neural activity visualization."""

import logging
from typing import Dict, Tuple, Optional
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """Generates heatmaps for neural activity visualization.

    Creates 2D and 3D heatmaps from electrode data,
    supporting various interpolation and colormapping methods.
    """

    def __init__(self) -> None:
        """Initialize heatmap generator."""
        self.interpolation_method = "cubic"  # linear, nearest, cubic
        self.smoothing_sigma = 1.0
        self.colormap = "viridis"

        # Grid resolution
        self.grid_resolution = (100, 100)  # For 2D projection
        self.volume_resolution = (64, 64, 64)  # For 3D volume

        # Value normalization
        self.normalize_values = True
        self.value_range = (0.0, 1.0)

        # Temporal settings
        self.temporal_window = 1.0  # seconds
        self.temporal_smoothing = True

        # Cache
        self.heatmap_cache: Dict[str, np.ndarray] = {}

        logger.info("HeatmapGenerator initialized")

    async def generate_surface_heatmap(
        self,
        electrode_positions: Dict[str, Tuple[float, float, float]],
        electrode_values: Dict[str, float],
        mesh_vertices: np.ndarray,
        mesh_faces: np.ndarray,
    ) -> np.ndarray:
        """Generate heatmap on brain surface mesh.

        Args:
            electrode_positions: 3D positions of electrodes
            electrode_values: Activity values at electrodes
            mesh_vertices: Brain mesh vertices
            mesh_faces: Brain mesh faces

        Returns:
            Vertex colors for heatmap
        """
        try:
            # Prepare electrode data
            positions = []
            values = []

            for channel, pos in electrode_positions.items():
                if channel in electrode_values:
                    positions.append(pos)
                    values.append(electrode_values[channel])

            positions = np.array(positions)
            values = np.array(values)

            # Normalize values if requested
            if self.normalize_values:
                values = self._normalize_values(values)

            # Interpolate to mesh vertices
            vertex_values = self._interpolate_to_vertices(
                positions, values, mesh_vertices
            )

            # Apply smoothing
            if self.smoothing_sigma > 0:
                vertex_values = self._smooth_on_surface(
                    vertex_values, mesh_vertices, mesh_faces
                )

            # Convert to colors
            vertex_colors = self._apply_colormap(vertex_values)

            return vertex_colors

        except Exception as e:
            logger.error(f"Failed to generate surface heatmap: {e}")
            return np.ones((len(mesh_vertices), 4))  # White fallback

    async def generate_2d_projection(
        self,
        electrode_positions: Dict[str, Tuple[float, float, float]],
        electrode_values: Dict[str, float],
        projection: str = "top",
    ) -> np.ndarray:
        """Generate 2D heatmap projection.

        Args:
            electrode_positions: 3D positions of electrodes
            electrode_values: Activity values at electrodes
            projection: Projection plane (top, front, side)

        Returns:
            2D heatmap array
        """
        try:
            # Project electrode positions to 2D
            positions_2d = []
            values = []

            for channel, pos_3d in electrode_positions.items():
                if channel in electrode_values:
                    pos_2d = self._project_to_2d(pos_3d, projection)
                    positions_2d.append(pos_2d)
                    values.append(electrode_values[channel])

            positions_2d = np.array(positions_2d)
            values = np.array(values)

            # Create regular grid
            x_min, x_max = -1.2, 1.2
            y_min, y_max = -1.2, 1.2

            xi = np.linspace(x_min, x_max, self.grid_resolution[0])
            yi = np.linspace(y_min, y_max, self.grid_resolution[1])
            xi, yi = np.meshgrid(xi, yi)

            # Interpolate to grid
            zi = griddata(
                positions_2d,
                values,
                (xi, yi),
                method=self.interpolation_method,
                fill_value=0.0,
            )

            # Apply smoothing
            if self.smoothing_sigma > 0:
                zi = gaussian_filter(zi, self.smoothing_sigma)

            # Create circular mask for head shape
            center = (self.grid_resolution[0] // 2, self.grid_resolution[1] // 2)
            radius = min(self.grid_resolution) // 2 - 5
            mask = self._create_circular_mask(self.grid_resolution, center, radius)

            # Apply mask
            zi[~mask] = np.nan

            return zi

        except Exception as e:
            logger.error(f"Failed to generate 2D projection: {e}")
            return np.zeros(self.grid_resolution)

    async def generate_volume_heatmap(
        self,
        electrode_positions: Dict[str, Tuple[float, float, float]],
        electrode_values: Dict[str, float],
        brain_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Generate 3D volume heatmap.

        Args:
            electrode_positions: 3D positions of electrodes
            electrode_values: Activity values at electrodes
            brain_mask: Optional brain volume mask

        Returns:
            3D volume heatmap
        """
        try:
            # Prepare data
            positions = []
            values = []

            for channel, pos in electrode_positions.items():
                if channel in electrode_values:
                    positions.append(pos)
                    values.append(electrode_values[channel])

            positions = np.array(positions)
            values = np.array(values)

            # Create 3D grid
            x = np.linspace(-1, 1, self.volume_resolution[0])
            y = np.linspace(-1, 1, self.volume_resolution[1])
            z = np.linspace(-1, 1, self.volume_resolution[2])

            # Create meshgrid
            xv, yv, zv = np.meshgrid(x, y, z, indexing="ij")

            # Interpolate using RBF or inverse distance weighting
            volume = self._interpolate_to_volume(positions, values, (xv, yv, zv))

            # Apply brain mask if provided
            if brain_mask is not None:
                volume *= brain_mask

            # Apply smoothing
            if self.smoothing_sigma > 0:
                volume = gaussian_filter(volume, self.smoothing_sigma)

            return volume

        except Exception as e:
            logger.error(f"Failed to generate volume heatmap: {e}")
            return np.zeros(self.volume_resolution)

    async def generate_temporal_heatmap(
        self,
        electrode_positions: Dict[str, Tuple[float, float, float]],
        temporal_data: Dict[str, np.ndarray],
        timestamps: np.ndarray,
        target_time: float,
    ) -> np.ndarray:
        """Generate heatmap with temporal dynamics.

        Args:
            electrode_positions: 3D positions of electrodes
            temporal_data: Time series data for each electrode
            timestamps: Time points
            target_time: Time to visualize

        Returns:
            Heatmap at target time
        """
        try:
            # Extract values at target time
            electrode_values = {}

            for channel, time_series in temporal_data.items():
                # Find nearest time index
                time_idx = np.argmin(np.abs(timestamps - target_time))

                if self.temporal_smoothing:
                    # Average over temporal window
                    window_start = max(0, time_idx - int(self.temporal_window * 10))
                    window_end = min(
                        len(timestamps), time_idx + int(self.temporal_window * 10)
                    )
                    value = np.mean(time_series[window_start:window_end])
                else:
                    value = time_series[time_idx]

                electrode_values[channel] = value

            # Generate spatial heatmap
            # Dummy mesh for now
            mesh_vertices = np.random.randn(1000, 3) * 0.1
            mesh_faces = np.random.randint(0, 1000, (2000, 3))

            return await self.generate_surface_heatmap(
                electrode_positions, electrode_values, mesh_vertices, mesh_faces
            )

        except Exception as e:
            logger.error(f"Failed to generate temporal heatmap: {e}")
            return np.ones((1000, 4))

    def _normalize_values(self, values: np.ndarray) -> np.ndarray:
        """Normalize values to specified range.

        Args:
            values: Input values

        Returns:
            Normalized values
        """
        if len(values) == 0:
            return values

        # Robust normalization using percentiles
        vmin = np.percentile(values, 5)
        vmax = np.percentile(values, 95)

        if vmax > vmin:
            normalized = (values - vmin) / (vmax - vmin)
            normalized = np.clip(normalized, 0, 1)

            # Scale to target range
            range_min, range_max = self.value_range
            normalized = normalized * (range_max - range_min) + range_min

            return normalized
        else:
            return np.full_like(values, self.value_range[0])

    def _interpolate_to_vertices(
        self, positions: np.ndarray, values: np.ndarray, vertices: np.ndarray
    ) -> np.ndarray:
        """Interpolate electrode values to mesh vertices.

        Args:
            positions: Electrode positions
            values: Electrode values
            vertices: Mesh vertices

        Returns:
            Interpolated vertex values
        """
        # Use inverse distance weighting
        vertex_values = np.zeros(len(vertices))

        for i, vertex in enumerate(vertices):
            # Calculate distances to all electrodes
            distances = np.linalg.norm(positions - vertex, axis=1)

            # Inverse distance weighting
            weights = 1.0 / (distances + 1e-6)
            weights /= np.sum(weights)

            vertex_values[i] = np.sum(weights * values)

        return vertex_values

    def _smooth_on_surface(
        self, values: np.ndarray, vertices: np.ndarray, faces: np.ndarray
    ) -> np.ndarray:
        """Apply smoothing on mesh surface.

        Args:
            values: Vertex values
            vertices: Mesh vertices
            faces: Mesh faces

        Returns:
            Smoothed values
        """
        # Build vertex adjacency
        adjacency = {i: set() for i in range(len(vertices))}

        for face in faces:
            for i in range(3):
                for j in range(3):
                    if i != j:
                        adjacency[face[i]].add(face[j])

        # Apply smoothing iterations
        smoothed = values.copy()

        for _ in range(int(self.smoothing_sigma * 2)):
            new_values = smoothed.copy()

            for i, neighbors in adjacency.items():
                if neighbors:
                    neighbor_values = [smoothed[n] for n in neighbors]
                    new_values[i] = 0.7 * smoothed[i] + 0.3 * np.mean(neighbor_values)

            smoothed = new_values

        return smoothed

    def _apply_colormap(self, values: np.ndarray) -> np.ndarray:
        """Apply colormap to values.

        Args:
            values: Scalar values

        Returns:
            RGBA colors
        """
        # Normalize to 0-1 if needed
        vmin, vmax = np.min(values), np.max(values)
        if vmax > vmin:
            normalized = (values - vmin) / (vmax - vmin)
        else:
            normalized = np.zeros_like(values)

        # Apply colormap
        colors = self._get_colormap_colors(normalized)

        return colors

    def _get_colormap_colors(self, values: np.ndarray) -> np.ndarray:
        """Get colors from colormap.

        Args:
            values: Normalized values (0-1)

        Returns:
            RGBA colors
        """
        n = len(values)
        colors = np.zeros((n, 4))

        if self.colormap == "viridis":
            # Simplified viridis colormap
            for i, v in enumerate(values):
                if v < 0.25:
                    t = v * 4
                    colors[i] = [0.267, 0.005, 0.329 + t * 0.129, 1.0]
                elif v < 0.5:
                    t = (v - 0.25) * 4
                    colors[i] = [
                        0.267 - t * 0.06,
                        0.005 + t * 0.462,
                        0.458 + t * 0.1,
                        1.0,
                    ]
                elif v < 0.75:
                    t = (v - 0.5) * 4
                    colors[i] = [
                        0.207 - t * 0.079,
                        0.467 + t * 0.354,
                        0.558 - t * 0.117,
                        1.0,
                    ]
                else:
                    t = (v - 0.75) * 4
                    colors[i] = [
                        0.128 + t * 0.865,
                        0.821 + t * 0.085,
                        0.441 - t * 0.297,
                        1.0,
                    ]

        elif self.colormap == "jet":
            # Simplified jet colormap
            for i, v in enumerate(values):
                if v < 0.125:
                    colors[i] = [0, 0, 0.5 + v * 4, 1.0]
                elif v < 0.375:
                    t = (v - 0.125) / 0.25
                    colors[i] = [0, t, 1.0, 1.0]
                elif v < 0.625:
                    t = (v - 0.375) / 0.25
                    colors[i] = [t, 1.0, 1.0 - t, 1.0]
                elif v < 0.875:
                    t = (v - 0.625) / 0.25
                    colors[i] = [1.0, 1.0 - t, 0, 1.0]
                else:
                    t = (v - 0.875) / 0.125
                    colors[i] = [1.0 - t * 0.5, 0, 0, 1.0]

        else:
            # Default grayscale
            for i, v in enumerate(values):
                colors[i] = [v, v, v, 1.0]

        return colors

    def _project_to_2d(
        self, pos_3d: Tuple[float, float, float], projection: str
    ) -> Tuple[float, float]:
        """Project 3D position to 2D plane.

        Args:
            pos_3d: 3D position
            projection: Projection type

        Returns:
            2D position
        """
        x, y, z = pos_3d

        if projection == "top":
            return (x, y)
        elif projection == "front":
            return (x, z)
        elif projection == "side":
            return (y, z)
        else:
            return (x, y)

    def _create_circular_mask(
        self, shape: Tuple[int, int], center: Tuple[int, int], radius: int
    ) -> np.ndarray:
        """Create circular mask.

        Args:
            shape: Array shape
            center: Circle center
            radius: Circle radius

        Returns:
            Boolean mask
        """
        y, x = np.ogrid[: shape[0], : shape[1]]
        mask = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
        return mask

    def _interpolate_to_volume(
        self,
        positions: np.ndarray,
        values: np.ndarray,
        grid: Tuple[np.ndarray, np.ndarray, np.ndarray],
    ) -> np.ndarray:
        """Interpolate to 3D volume using RBF.

        Args:
            positions: Sample positions
            values: Sample values
            grid: 3D grid coordinates

        Returns:
            Interpolated volume
        """
        xv, yv, zv = grid
        volume = np.zeros(xv.shape)

        # Simple inverse distance weighting
        for i in range(xv.shape[0]):
            for j in range(xv.shape[1]):
                for k in range(xv.shape[2]):
                    point = np.array([xv[i, j, k], yv[i, j, k], zv[i, j, k]])

                    # Calculate distances
                    distances = np.linalg.norm(positions - point, axis=1)

                    # Inverse distance weighting
                    weights = np.exp(-(distances**2) / 0.1)  # Gaussian kernel
                    weights /= np.sum(weights)

                    volume[i, j, k] = np.sum(weights * values)

        return volume

    def set_colormap(self, colormap: str) -> None:
        """Set colormap for heatmap visualization.

        Args:
            colormap: Colormap name
        """
        self.colormap = colormap
        logger.info(f"Colormap set to: {colormap}")

    def set_interpolation(self, method: str) -> None:
        """Set interpolation method.

        Args:
            method: Interpolation method
        """
        if method in ["linear", "nearest", "cubic"]:
            self.interpolation_method = method
            logger.info(f"Interpolation method set to: {method}")

    def clear_cache(self) -> None:
        """Clear heatmap cache."""
        self.heatmap_cache.clear()
        logger.info("Heatmap cache cleared")
